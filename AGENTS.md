# Agent guide: chicken-gate

Context for coding agents working on this repo. Read it before you change
anything, and see [README.md](README.md) for setup and usage.

## What this is

An automatic chicken-coop gate. A Raspberry Pi Zero drives a motor through two
relays. The motor winds a rope that pulls the gate closed. By default the
gate opens at sunrise and closes at dusk (both adjustable in Settings), and you
can control it from a small web app on your phone.

Two systemd services run on the Pi, and they share files rather than talking
over a socket:

| Service | Runs | Role |
| --- | --- | --- |
| `chicken-gate.service` | `scripts/chicken-gate-main` as root | Control loop (`src/chicken_gate/gate/main.py`). Ticks about every 0.1 s, drives the GPIO pins, and runs the APScheduler sun schedule. |
| `chicken-gate-web.service` | `chicken-gate-web --port 5000` as `pi` | Flask app (`src/chicken_gate/web/`). Templates extend `templates/base.html`: `index.html` (main page) and `settings.html`. |

How the two services communicate (paths are set in `src/chicken_gate/shared/config.py`):

- **Status:** the gate writes `/dev/shm/chicken-gate-status.json` about once a
  second, plus immediately after a command. The web app reads it.
- **Commands:** the web app writes `gate_cmd.txt` in the repo root atomically.
  The gate claims it by renaming it to `.processing`, then reads it.
- **Settings:** the settings page saves `settings.json` in the repo root
  (git-ignored; validated by `shared/settings.py`). It then sends a
  `RELOAD_SETTINGS` command, so the gate applies the change without a restart.

## Working on the Pi

- **Host:** `pi@192.168.1.192`. Key-based SSH from the dev workstation works
  non-interactively:
  `ssh -o BatchMode=yes pi@192.168.1.192 '<cmd>'`.
  Don't try password auth from an agent shell. If the key doesn't work, ask
  the user.
- **Sudo:** `pi` has passwordless sudo. Use `sudo -n`.
- **Checkout:** the repo on the Pi is at `~/sw/chicken-gate`. It's a plain
  clone of `origin/master` and is installed editable.
- **Web UI:** `http://192.168.1.192` (iptables redirects port 80 to 5000).
  Over Tailscale it's `http://chicken-gate`, but the dev workstation isn't on
  Tailscale.

### Workflow for changes

Don't hand-edit code on the Pi. Instead:

1. Edit in the local repo, then lint and test (commands below).
2. Commit and push to `origin/master`.
3. On the Pi, pull:

   ```bash
   ssh -o BatchMode=yes pi@192.168.1.192 'cd ~/sw/chicken-gate && git pull -q --ff-only'
   ```

4. Restart **only** the service whose code changed:

   - Web app only (`src/chicken_gate/web/`, templates, CSS, JS):

     ```bash
     ssh -o BatchMode=yes pi@192.168.1.192 'sudo -n systemctl restart chicken-gate-web.service'
     ```

   - Gate controller (`src/chicken_gate/gate/`, or `shared/` which both use).
     **First** confirm the gate is idle (see the next section), then restart it:

     ```bash
     curl -s http://192.168.1.192/api/status | grep -o '"is_moving": *[a-z]*'
     # Only if that prints "is_moving":false
     ssh -o BatchMode=yes pi@192.168.1.192 'sudo -n systemctl restart chicken-gate.service'
     ```

     If `shared/` changed, restart the web service too.

   - Docs-only changes need no restart.
   - Code-only changes don't need the `install-*.sh` scripts. Rerun those only
     when the systemd unit files or entry points change.

5. Verify. Check the restarted service with `systemctl is-active ...`, read the
   recent logs with `journalctl -u chicken-gate.service --since -2min`, and fetch
   `curl http://192.168.1.192/api/status`.
6. Make sure local, `origin/master` and the Pi are all on the same commit.

### Restarting the gate service is not free

When the gate service starts, it gets its position from the closed switch:
100 (closed) if the switch is pressed, otherwise 0 (open). It does **not** act
on startup; it waits for the next scheduled event. A restart while the gate is
moving loses the move. Check `/api/status` first, and only restart when
`is_moving` is false.

## Platform constraints (important)

- **Pi Zero, single core, ARMv6.** CPU is scarce. An earlier busy loop that
  recomputed sun times on every tick pegged the CPU and broke the web app. Keep
  the control loop light: cache, throttle, and don't do blocking I/O on the tick
  path. Send email from a background thread, as `gate.py` and `boot_check.py`
  already do.
- **Python 3.7.3 on Raspbian buster.** Don't use 3.8+ features such as the
  walrus operator, `Path.unlink(missing_ok=...)`, `functools.cached_property`,
  `list[int]`-style generics, or `match`. CI tests 3.8 and up, so it won't catch
  these.
- **SD card wear matters.** One card has already failed. Put frequently
  rewritten files in `/dev/shm` (RAM), and don't add per-tick or per-poll disk
  writes or log lines. The web app filters `/api/status` polls out of the access
  log for this reason.
- **No RTC.** The clock is wrong at boot until NTP syncs, so don't trust
  wall-clock time in very early startup code.
- **Time zone:** America/Vancouver. BC moves to permanent UTC-7 from 2026-11-01,
  and the Pi's tzdata had to be patched for it. See the README section
  "Time Zone".
- **Hardware watchdog:** systemd runs it with `RuntimeWatchdogSec=14` (the
  bcm2835 maximum is about 15 s). If the Pi hangs, it reboots.
- **journald is not persistent.** After a reboot, rsyslog keeps history in
  `/var/log/syslog` (rotated by logrotate). Avoid adding a separate file for
  messages already sent there. Long-running processes such as rsyslog keep the
  time zone they started with, so restart them after a time zone change.
- **Logging volume is an SD card wear cost.** Keep the gate's steady-state
  logging to events only (no per-tick prints), and don't duplicate messages in
  multiple files. Unexpected-restart emails include up to 20 recent pre-boot
  lines from the persistent syslog.

## Hardware and gate behaviour

- **GPIO (BCM numbering):**
  - Relays on GPIO4 and GPIO17, active HIGH (LOW means off).
  - Closed limit switch on GPIO2 (HIGH means pressed).
  - **There is no open switch.** Opening is purely timed.
- **Position:** 0 = fully open, 100 = fully closed. With no open switch, the
  position comes from dead reckoning on measured elapsed time (`Gate.tick`).
  Full travel takes about 280 s to open (the "opening run time" setting) and
  420 s to close. Always pass the real
  elapsed time to `tick()`. An earlier fixed 0.1 s/tick assumption made the
  gate open 20–30% too far when the loop ran slow.
- **The extra 10% after the closed switch is intentional.** The rope has a
  spring in line. When the closed switch triggers, the position snaps to at
  least 90, and the motor keeps running to 100. That stretches the spring so the
  gate is held tightly shut. Don't "fix" this overshoot.
- **Safety interlocks in `gate.py`:**
  - If the closed switch is pressed while the position is below 90, it raises
    an error, disables opening and sends an email.
  - It also raises an error when closing finishes without the switch pressed.
- **Clean shutdown:** on SIGTERM, the gate service stops the motor, drives the
  relays LOW and writes `.clean_shutdown`. On the first start after a boot, a
  missing marker means the Pi reset uncleanly (watchdog or power loss), and the
  gate emails the user (`gate/boot_check.py`).
- **Schedule:** `gate/schedule.py` opens at dawn or sunrise and closes at sunset
  or dusk, each plus an offset of ±120 min (defaults: sunrise and dusk, no
  offset). Gate times are kept within their own day. If a settings change moves
  today's event to a time that has already passed while the old time is still
  ahead, the event runs immediately. The main page's Morning/Evening timelines
  slot "Opens"/"Closes" in among the sun events.
- **Email secrets:** stored in `secret.toml`, which is git-ignored. The template
  is `src/chicken_gate/shared/secret.toml.template`. Never commit secrets.

## Lint and test (dev workstation)

```bash
uvx ruff check .
uv run --no-project -q --with pytest --with pytest-mock --with astral \
  --with python-dateutil --with apscheduler --with flask --with toml --with tomli \
  python -m pytest -q
```

- `--no-project` is required: `requires-python = ">=3.7"` conflicts with
  Flask's ≥3.9 floor when uv resolves the project.
- The existing I001 import-order warning in `test_runner.py` is known. Ignore it.
- Tests use `gate_drv_mock.py` instead of real GPIO. `test/conftest.py`
  auto-patches `send_email`, so tests never send real email.
- To check UI changes, render screenshots with Playwright
  (`uv run --no-project --with playwright ...`). Mock `/api/status` with real
  data from the Pi and check both light and dark themes.

## UI conventions

- The page is for a phone. The gate controls are at the top, and the rest is a
  compact 2-column tile grid.
- There is no camera.
- The gear icon in the header opens `/settings`.
- The theme button cycles Auto → Light → Dark. Auto follows the OS setting
  live. Colours are CSS variables in `:root` and `[data-theme="dark"]`.
- The owner prefers a clean, uncluttered look, so keep additions subtle.

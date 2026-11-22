"""
Tests for user settings: validation, persistence, schedule offsets and the web API.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dateutil import tz

from chicken_gate.gate.gate import Gate
from chicken_gate.gate.gate_cmd import Cmd
from chicken_gate.shared import settings as user_settings

TZ = tz.gettz("America/Vancouver")
SUN_TIMES = {
    "dawn": datetime(2026, 11, 22, 7, 5, 40, tzinfo=TZ),
    "sunrise": datetime(2026, 11, 22, 7, 41, 20, tzinfo=TZ),
    "sunset": datetime(2026, 11, 22, 16, 22, 10, tzinfo=TZ),
    "dusk": datetime(2026, 11, 22, 16, 58, 50, tzinfo=TZ),
}


class TestValidation:
    def test_missing_keys_take_defaults_and_unknown_keys_dropped(self):
        result = user_settings.validate({"open_offset_min": "-15", "junk": 1})
        assert result == dict(user_settings.DEFAULTS, open_offset_min=-15)

    @pytest.mark.parametrize(
        "data",
        [
            {"open_travel_s": 29},
            {"open_travel_s": 901},
            {"open_travel_s": 280.5},
            {"open_travel_s": True},
            {"close_travel_s": 901},
            {"close_offset_min": 121},
            {"open_offset_min": "abc"},
            {"open_event": "dusk"},
            {"close_event": "sunrise"},
        ],
    )
    def test_rejects_invalid_values(self, data):
        with pytest.raises(ValueError):
            user_settings.validate(data)

    def test_save_then_load_round_trips(self, tmp_path):
        path = tmp_path / "settings.json"
        saved = user_settings.save(
            {"open_travel_s": 300, "close_event": "sunset"}, path
        )
        assert user_settings.load(path) == saved
        assert saved["open_travel_s"] == 300

    def test_load_falls_back_to_defaults_for_bad_file(self, tmp_path):
        path = tmp_path / "settings.json"
        path.write_text(json.dumps({"open_travel_s": 5}))
        assert user_settings.load(path) == user_settings.DEFAULTS
        assert user_settings.load(tmp_path / "missing.json") == user_settings.DEFAULTS


def test_gate_travel_times_can_be_changed():
    gate = Gate(init_posn=100, open_time=100, close_time=100)
    gate.set_open_time(50)
    gate.set_close_time(200)
    gate.open()
    gate.tick(0)
    gate.tick(25)
    assert gate.get_posn() == pytest.approx(50)
    gate.close()
    gate.tick(0)
    gate.tick(50)
    assert gate.get_posn() == pytest.approx(75)


@pytest.fixture
def make_schedule(mocker):
    from chicken_gate.gate import schedule as schedule_module

    mocker.patch.object(schedule_module, "BackgroundScheduler", MagicMock())
    get_times = mocker.patch.object(schedule_module.SunTimes, "get_times")

    def set_now(hour, minute):
        fake_now = datetime(2026, 11, 22, hour, minute, tzinfo=TZ)
        fake_datetime = mocker.patch.object(schedule_module, "datetime")
        fake_datetime.now.return_value = fake_now

    def make(settings=None, sun_times=SUN_TIMES):
        get_times.return_value = dict(sun_times)
        sched = schedule_module.Schedule(settings)
        sched.get_gate_cmd()  # discard the initial value
        return sched

    make.set_now = set_now
    return make


class TestScheduleOffsets:
    def test_times_use_event_plus_offset_to_the_minute(self, make_schedule):
        sched = make_schedule(
            dict(
                user_settings.DEFAULTS,
                open_event="dawn",
                open_offset_min=10,
                close_event="sunset",
                close_offset_min=-20,
            )
        )
        info = sched.get_schedule_info()
        assert info["gate_open_time"] == "07:15"
        assert info["gate_close_time"] == "16:02"
        assert info["gate_open"].startswith("2026-11-22T07:15:00")

    def test_offset_is_kept_within_the_day(self, make_schedule):
        summer = dict(SUN_TIMES, dusk=datetime(2026, 6, 21, 22, 30, tzinfo=TZ))
        sched = make_schedule(
            dict(user_settings.DEFAULTS, close_offset_min=120), sun_times=summer
        )
        assert sched.get_schedule_info()["gate_close"].startswith("2026-06-21T23:59:00")

    def test_moving_close_earlier_past_now_closes_immediately(self, make_schedule):
        sched = make_schedule()  # closes at dusk, 16:58
        make_schedule.set_now(16, 45)
        sched.apply_settings(dict(user_settings.DEFAULTS, close_offset_min=-30))
        assert sched.get_gate_cmd() == Cmd.CLOSE

    def test_moving_open_earlier_past_now_opens_immediately(self, make_schedule):
        sched = make_schedule()  # opens at sunrise, 07:41
        make_schedule.set_now(7, 30)
        sched.apply_settings(dict(user_settings.DEFAULTS, open_event="dawn"))
        assert sched.get_gate_cmd() == Cmd.OPEN

    def test_no_catch_up_when_event_already_happened_or_disabled(self, make_schedule):
        sched = make_schedule()
        make_schedule.set_now(17, 30)  # past dusk: the gate already closed
        sched.apply_settings(dict(user_settings.DEFAULTS, close_offset_min=-30))
        assert sched.get_gate_cmd() is not Cmd.CLOSE

        make_schedule.set_now(16, 45)
        sched.apply_settings(user_settings.DEFAULTS)
        sched.apply_settings(
            dict(user_settings.DEFAULTS, close_offset_min=-30), catch_up=False
        )
        assert sched.get_gate_cmd() is not Cmd.CLOSE


class TestSettingsApi:
    @pytest.fixture
    def client(self, tmp_path, monkeypatch):
        from chicken_gate.web.app import app

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            user_settings, "get_settings_path", lambda: tmp_path / "settings.json"
        )
        return app.test_client()

    def test_save_persists_and_asks_gate_to_reload(self, client, tmp_path):
        response = client.post("/api/settings", json={"open_travel_s": 320})
        assert response.status_code == 200
        assert response.get_json()["settings"]["open_travel_s"] == 320
        assert client.get("/api/settings").get_json()["open_travel_s"] == 320
        assert (tmp_path / "gate_cmd.txt").read_text() == "RELOAD_SETTINGS"

    def test_invalid_settings_are_rejected_unsaved(self, client, tmp_path):
        response = client.post("/api/settings", json={"open_offset_min": 500})
        assert response.status_code == 400
        assert "between" in response.get_json()["message"]
        assert not (tmp_path / "settings.json").exists()
        assert not (tmp_path / "gate_cmd.txt").exists()

    def test_settings_page_renders(self, client):
        page = client.get("/settings").data
        assert b'id="close_travel_s"' in page
        assert b'name="theme"' in page
        assert b'href="/settings"' in client.get("/").data

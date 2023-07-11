#!/bin/bash

sudo cp ./chicken-gate.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl restart chicken-gate.service
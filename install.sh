#!/bin/bash

# https://www.howtogeek.com/devops/how-to-add-your-own-services-to-systemd-for-easier-management/
cp chicken-gate.service /etc/systemd/system/chicken-gate.service
systemctl daemon-reload
systemctl enable chicken-gate
service chicken-gate start
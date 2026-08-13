#!/usr/bin/env bash
#
# SDV Simulator v2 — systemd user service uninstall script
#
# Stops/disables sdv-simulator.service and removes the installed unit copy.
# Does NOT touch the project files or the linger setting.
#
# Usage:  ./deploy/uninstall.sh
set -euo pipefail

UNIT="sdv-simulator.service"
USER_UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_DEST="$USER_UNIT_DIR/$UNIT"

if systemctl --user list-unit-files "$UNIT" >/dev/null 2>&1; then
  systemctl --user disable --now "$UNIT" 2>/dev/null || true
fi

if [[ -f "$UNIT_DEST" ]]; then
  rm -f "$UNIT_DEST"
  echo "removed $UNIT_DEST"
else
  echo "no installed unit found at $UNIT_DEST — nothing to remove"
fi

systemctl --user daemon-reload
echo "uninstalled: $UNIT"

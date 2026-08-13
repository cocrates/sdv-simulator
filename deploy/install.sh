#!/usr/bin/env bash
#
# SDV Simulator v2 — systemd user service install script
#
# Registers sdv-simulator.service so the dashboard keeps running:
#   1. copies the unit to ~/.config/systemd/user/
#   2. systemctl --user daemon-reload
#   3. systemctl --user enable --now sdv-simulator.service
#   4. enables linger (boot-time start of the user service manager)
#
# Usage:  ./deploy/install.sh
# Uninstall: ./deploy/uninstall.sh
#
# References: ../cocrates-server/deploy/ pattern (systemd user units,
# Restart=always, install copy to ~/.config/systemd/user/).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
UNIT="sdv-simulator.service"
UNIT_SRC="$SCRIPT_DIR/$UNIT"
USER_UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_DEST="$USER_UNIT_DIR/$UNIT"

# ---------------------------------------------------------------- preflight

if [[ ! -f "$UNIT_SRC" ]]; then
  echo "error: unit file not found: $UNIT_SRC" >&2
  exit 1
fi

if [[ ! -x "$PROJECT_DIR/.venv/bin/sdv-sim" ]]; then
  echo "error: venv console script not found: $PROJECT_DIR/.venv/bin/sdv-sim" >&2
  echo "  (set up the venv: python -m venv .venv && .venv/bin/pip install -e .[dev])" >&2
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/sdv_sim/server/static/index.html" ]]; then
  echo "warning: frontend static build missing (sdv_sim/server/static/)" >&2
  echo "  run: cd frontend && npm install && npm run build" >&2
fi

# ---------------------------------------------------------------- install

mkdir -p "$USER_UNIT_DIR"
cp "$UNIT_SRC" "$UNIT_DEST"
systemctl --user daemon-reload
systemctl --user enable --now "$UNIT"

# Boot-time start: the user manager must survive logout/reboot (Linger).
if ! loginctl show-user "$USER" 2>/dev/null | grep -q '^Linger=yes$'; then
  echo "enabling linger so the service starts at boot (loginctl enable-linger $USER)..."
  if ! loginctl enable-linger "$USER" 2>/dev/null; then
    echo "warning: linger enable failed — run as root: sudo loginctl enable-linger $USER" >&2
  fi
fi

# ---------------------------------------------------------------- report

systemctl --user --no-pager status "$UNIT" || true

echo
echo "SDV Simulator v2 dashboard registered as user service: $UNIT"
echo "  local:   http://127.0.0.1:8888"
echo "  external (--host 0.0.0.0): http://<server-ip>:8888"
echo "  NOTE: no authentication — the dashboard is exposed on the network."
echo "        (spec constraint; protect with firewall source-IP rules if needed)"
echo "  logs:    journalctl --user -u $UNIT -f"

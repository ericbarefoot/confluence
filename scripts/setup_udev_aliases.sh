#!/usr/bin/env bash
# Install udev rules that give this node's serial devices memorable
# /dev symlinks (e.g. /dev/teknic_clearcore) instead of raw /dev/ttyUSB*
# names that can shuffle across reboots/re-enumeration.
#
# Unlike a rules file hardcoded to one hub's cable serial numbers, this
# takes the alias->device mapping as command-line arguments, so the same
# script ports to a new confluence node without editing anything — just
# pass that node's own serial numbers (see --list below to find them).
#
# Usage:
#   sudo ./setup_udev_aliases.sh <alias>=<ID_SERIAL_SHORT>[:<IF_NUM>] ...
#
# Examples:
#   # Single-port cable (e.g. a dedicated USB-RS485 adapter):
#   sudo ./setup_udev_aliases.sh massa_ultrasonic=AV0K9L0C
#
#   # Multi-port FTDI hub — same serial number shared across ports,
#   # disambiguated by USB interface number (00/01/02/...):
#   sudo ./setup_udev_aliases.sh \
#     teknic_clearcore=FT9DZBFK:00 \
#     massa_ultrasonic=FT9DZBFK:01 \
#     fuji_vfd=FT9DZBFK:02
#
# Finding the serial numbers/interface numbers on this machine:
#   ./setup_udev_aliases.sh --list
# (no sudo needed for --list; it only reads udev properties)

set -euo pipefail

RULES_FILE=/etc/udev/rules.d/99-confluence-serial.rules

usage() {
    grep '^#' "$0" | sed -n '2,/^set -e/p' | sed '$d' | sed 's/^# \{0,1\}//'
    exit 1
}

list_candidates() {
    echo "Serial devices currently visible on this machine:"
    echo
    shopt -s nullglob
    local found=0
    for dev in /dev/ttyUSB* /dev/ttyACM*; do
        found=1
        local serial ifnum
        serial=$(udevadm info -q property -n "$dev" 2>/dev/null | sed -n 's/^ID_SERIAL_SHORT=//p')
        ifnum=$(udevadm info -q property -n "$dev" 2>/dev/null | sed -n 's/^ID_USB_INTERFACE_NUM=//p')
        if [ -n "$ifnum" ]; then
            echo "  $dev  ID_SERIAL_SHORT=${serial:-<none>}  ID_USB_INTERFACE_NUM=$ifnum"
        else
            echo "  $dev  ID_SERIAL_SHORT=${serial:-<none>}"
        fi
    done
    if [ "$found" -eq 0 ]; then
        echo "  (none found — is anything plugged in?)"
    fi
    echo
    echo "Pass ALIAS=SERIAL or ALIAS=SERIAL:IFNUM pairs to install rules using these."
}

if [ "${1:-}" = "--list" ] || [ "${1:-}" = "-l" ]; then
    list_candidates
    exit 0
fi

if [ "$#" -eq 0 ]; then
    usage
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "Run as root (sudo ./setup_udev_aliases.sh ...) — use --list without sudo to discover devices first." >&2
    exit 1
fi

{
    echo "# Managed by confluence/scripts/setup_udev_aliases.sh — do not edit by hand."
    echo "# Regenerate with the same arguments if a device or cable changes."
} > "$RULES_FILE"

aliases=()
for arg in "$@"; do
    if [[ "$arg" != *=* ]]; then
        echo "Invalid argument '$arg' — expected ALIAS=SERIAL or ALIAS=SERIAL:IFNUM" >&2
        exit 1
    fi
    alias_name="${arg%%=*}"
    spec="${arg#*=}"
    serial="${spec%%:*}"
    if [ -z "$alias_name" ] || [ -z "$serial" ]; then
        echo "Invalid argument '$arg' — expected ALIAS=SERIAL or ALIAS=SERIAL:IFNUM" >&2
        exit 1
    fi
    if [[ "$spec" == *:* ]]; then
        ifnum="${spec#*:}"
        echo "SUBSYSTEM==\"tty\", ENV{ID_SERIAL_SHORT}==\"$serial\", ENV{ID_USB_INTERFACE_NUM}==\"$ifnum\", SYMLINK+=\"$alias_name\"" >> "$RULES_FILE"
    else
        echo "SUBSYSTEM==\"tty\", ENV{ID_SERIAL_SHORT}==\"$serial\", SYMLINK+=\"$alias_name\"" >> "$RULES_FILE"
    fi
    aliases+=("$alias_name")
done

echo "Wrote $RULES_FILE:"
cat "$RULES_FILE"
echo

udevadm control --reload-rules
udevadm trigger --subsystem-match=tty
udevadm settle  # trigger only queues events; wait for udevd to finish processing them

echo "Reloaded udev rules. Resulting aliases:"
for alias_name in "${aliases[@]}"; do
    ls -l "/dev/$alias_name" 2>&1 || echo "  /dev/$alias_name: not present — check the serial/interface number against --list"
done

#!/bin/bash

set -e

WORKING_DIR=$(cd "$1" || exit 1; pwd)
EXEC=$2
DESCRIPTION=$3
SERVICE_FILE=$4

UNIT="\
[Unit]
Description=${DESCRIPTION}

[Service]
User=${USER}
WorkingDirectory=${WORKING_DIR}
ExecStart=${EXEC}

Restart=always

[Install]
WantedBy=multi-user.target
"

echo "$UNIT" | sudo tee "/etc/systemd/system/${SERVICE_FILE}"

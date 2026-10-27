#!/bin/sh
set -eu

DYNAMIC_DIR="/etc/nginx/dynamic"
HOSTS_FILE="${DYNAMIC_DIR}/hosts.conf"
PATHS_FILE="${DYNAMIC_DIR}/paths.conf"

mkdir -p "${DYNAMIC_DIR}"
touch "${HOSTS_FILE}" "${PATHS_FILE}"

LAST_HASH="$(cat "${HOSTS_FILE}" "${PATHS_FILE}" | md5sum | awk '{print $1}')"
echo "[gateway] starting nginx, dynamic config hash=${LAST_HASH}"

(
    while true; do
        sleep 1
        NEW_HASH="$(cat "${HOSTS_FILE}" "${PATHS_FILE}" | md5sum | awk '{print $1}')"
        if [ "${NEW_HASH}" = "${LAST_HASH}" ]; then
            continue
        fi
        if nginx -t >/dev/null 2>&1; then
            nginx -s reload
            LAST_HASH="${NEW_HASH}"
            echo "[gateway] routing table reloaded hash=${LAST_HASH}"
        else
            echo "[gateway] invalid routing table detected, keeping previous config" >&2
        fi
    done
) &

exec nginx -g 'daemon off;'

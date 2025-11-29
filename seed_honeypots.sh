#!/bin/bash
set -e
HOST=127.0.0.1
# Host ports mapped to honeypots container ports
PORTS=(2222 2121 8080 8443 3307 5434 139 445 502 1025)

for p in "${PORTS[@]}"; do
  echo "[*] Seeding port $p"
  for i in {1..15}; do
    timeout 1 bash -lc "echo 'HELLO-$p-$i' > /dev/tcp/${HOST}/${p}" >/dev/null 2>&1 || true
  done
done
# HTTP explicit
curl -m 1 -s http://127.0.0.1:8080/ >/dev/null 2>&1 || true

echo "Done."

#!/bin/bash
set -euo pipefail

echo "Stopping ELK stack..."
docker compose down

echo "Services stopped."
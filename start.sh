#!/bin/bash
set -euo pipefail

# Configuration
SERVICES=("elasticsearch" "kibana")
MAX_RETRIES=30
SLEEP_INTERVAL=5

echo "Starting services..."
docker compose up -d

for SERVICE in "${SERVICES[@]}"; do
    echo "Waiting for $SERVICE to be healthy..."
    RETRY_COUNT=0
    
    while [ "$RETRY_COUNT" -lt "$MAX_RETRIES" ]; do
        HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$SERVICE" 2>/dev/null || echo "starting")
        
        if [ "$HEALTH_STATUS" = "healthy" ]; then
            echo "Service $SERVICE is healthy."
            break
        fi
        
        if [ "$RETRY_COUNT" -eq $((MAX_RETRIES - 1)) ]; then
            echo "Error: Service $SERVICE failed to reach healthy state."
            docker compose logs "$SERVICE"
            exit 1
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep "$SLEEP_INTERVAL"
    done
done

echo "Stack is operational."
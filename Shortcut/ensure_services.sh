#!/bin/bash
# ------------------------------------------------------------
# Script: ensure_services.sh
# Description: Automatically check and start MongoDB & Backend
# ------------------------------------------------------------
# 0. Reset RPLidar hardware
if [ -f /home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/reset_lidar.py ]; then
    python3 /home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/reset_lidar.py
fi


# 1. Check and start MongoDB
if ! systemctl is-active --quiet mongod; then
    echo "⚙️  MongoDB is offline. Starting MongoDB..."
    sudo systemctl start mongod
else
    echo "✅ MongoDB is running."
fi

# 2. Check and start Backend Server on Port 3000
if ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/127.0.0.1/3000" >/dev/null 2>&1; then
    echo "⚙️  Backend Server is offline. Starting Backend Server..."
    cd /home/smr/workspaces/backend
    npm run server > /home/smr/workspaces/mini_amr/amrROS2_ws/backend_server.log 2>&1 &
    cd - >/dev/null
    
    # Wait for the backend to start up
    for i in {1..10}; do
        if timeout 1 bash -c "cat < /dev/null > /dev/tcp/127.0.0.1/3000" >/dev/null 2>&1; then
            echo "✅ Backend Server started successfully on Port 3000."
            break
        fi
        sleep 1
    done
else
    echo "✅ Backend Server is running."
fi

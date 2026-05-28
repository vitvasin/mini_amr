#!/bin/bash

# Extract ROS_DOMAIN_ID from .bashrc
BASHRC_ID=$(grep -oP '^export ROS_DOMAIN_ID=\K[0-9]+' ~/.bashrc | head -n 1)

if [ -z "$BASHRC_ID" ]; then
    echo "Error: Could not find ROS_DOMAIN_ID in ~/.bashrc"
    exit 1
fi

echo "Found ROS_DOMAIN_ID=${BASHRC_ID} in ~/.bashrc"
echo "Updating files in the workspace..."

WORKSPACE_DIR="/home/smr/workspaces/mini_amr"

# Update 'export ROS_DOMAIN_ID=XX' in shell scripts
find "$WORKSPACE_DIR" -type f -name "*.sh" -exec sed -i "s/export ROS_DOMAIN_ID=[0-9][0-9]*/export ROS_DOMAIN_ID=$BASHRC_ID/g" {} +

# Update 'env["ROS_DOMAIN_ID"] = "XX"' or similar in python scripts
find "$WORKSPACE_DIR" -type f -name "*.py" -exec sed -i "s/env\[\"ROS_DOMAIN_ID\"\] = \"[0-9][0-9]*\"/env[\"ROS_DOMAIN_ID\"] = \"$BASHRC_ID\"/g" {} +
find "$WORKSPACE_DIR" -type f -name "*.py" -exec sed -i "s/env\['ROS_DOMAIN_ID'\] = '[0-9][0-9]*'/env['ROS_DOMAIN_ID'] = '$BASHRC_ID'/g" {} +

echo "Successfully updated ROS_DOMAIN_ID to ${BASHRC_ID} across the workspace."

#!/bin/bash

# === Read network interface from robot_config.yaml ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROBOT_CONFIG_PATH="$SCRIPT_DIR/../../robot_config.yaml"

if [ ! -f "$ROBOT_CONFIG_PATH" ]; then
    echo "Error: robot_config.yaml not found at $ROBOT_CONFIG_PATH"
    return 1 2>/dev/null || exit 1
fi

NETWORK_IFACE=$(python3 -c "import yaml; config = yaml.safe_load(open('$ROBOT_CONFIG_PATH')); print(config['robot_configuration']['network_interface'])" 2>/dev/null)
if [ -z "$NETWORK_IFACE" ]; then
    echo "Error: Could not read network_interface from robot_config.yaml"
    return 1 2>/dev/null || exit 1
fi

echo "Network interface from config: $NETWORK_IFACE"

# === ROS Environment Variables ===
unset ROS_DOMAIN_ID
unset RMW_IMPLEMENTATION
unset CYCLONEDDS_URI

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
#export ROS_DOMAIN_ID=42
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Export CYCLONEDDS_URI pointing to the XML file in the same directory
export CYCLONEDDS_URI="file://${SCRIPT_DIR}/../../cyclonedds_config.xml"

# === Network Configuration Check ===
# Unitree B2 ships with the same 192.168.123.0/24 subnet as Go2 / G1.
# Robot interface IP defaults to 192.168.123.161; assign a free host IP here.
if ! command -v nmcli &> /dev/null
then
    echo "Info: nmcli command not found. Skipping network configuration."
else
    IFACE="$NETWORK_IFACE"
    echo "Ethernet interface: $IFACE"
    IP="192.168.123.170"
    NETMASK="255.255.0.0"
    GATEWAY="192.168.123.1"

    echo "Searching for the active connection on interface $IFACE..."
    CONNECTION_NAME=$(nmcli -t -f DEVICE,NAME connection show --active | grep "^$IFACE" | cut -d':' -f2)

    if [ -z "$CONNECTION_NAME" ]; then
        echo "Error: No active connection found on interface $IFACE. Please ensure the interface is connected and has a profile."
    else
        echo "Found active connection: '$CONNECTION_NAME'"

        echo "Modifying connection '$CONNECTION_NAME' with new IP: $IP..."

        sudo nmcli connection modify "$CONNECTION_NAME" ipv4.method manual
        sudo nmcli connection modify "$CONNECTION_NAME" ipv4.addresses "$IP/16"
        sudo nmcli connection modify "$CONNECTION_NAME" ipv4.gateway "$GATEWAY"

        echo "Reapplying connection '$CONNECTION_NAME' to activate the new settings."
        sudo nmcli connection up "$CONNECTION_NAME"

        echo "Interface $IFACE has been reconfigured successfully."
    fi
fi

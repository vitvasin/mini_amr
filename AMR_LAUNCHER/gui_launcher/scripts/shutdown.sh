echo "Shutting Down System..."
# Requires sudo permissions or running as root
if command -v systemctl &> /dev/null; then
    sudo systemctl poweroff
else
    sudo shutdown -h now
fi

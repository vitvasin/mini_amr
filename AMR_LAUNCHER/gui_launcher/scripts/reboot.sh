echo "Rebooting System..."
# Requires sudo permissions or running as root
if command -v systemctl &> /dev/null; then
    sudo systemctl reboot
else
    sudo reboot
fi

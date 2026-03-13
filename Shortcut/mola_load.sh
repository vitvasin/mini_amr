if [ ! -f /home/smr/molamaps/latest_map.txt ]; then
    echo "❌ ไม่พบประวัติการเซฟแมปครับ (คุณยังไม่เคยรันสคริปต์ save_map.sh)"
    exit 1
fi

# 2. อ่านพาทแมปล่าสุดที่ถูกแอบจดไว้
LATEST_MAP=$(cat /home/smr/molamaps/latest_map.txt)

echo "⏳ กำลังโหลดแผนที่ล่าสุดจาก: $LATEST_MAP ..."

# 3. รันคำสั่งโหลดของ MOLA
ros2 service call /map_load mola_msgs/srv/MapLoad "map_path: '$LATEST_MAP'"
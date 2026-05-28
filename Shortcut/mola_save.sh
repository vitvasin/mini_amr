NEW_MAP_NAME="map_$(date +%Y%m%d_%H%M%S)"
FULL_PATH="/home/smr/molamaps/$NEW_MAP_NAME"

echo "⏳ กำลังบันทึกแผนที่ชื่อ: $NEW_MAP_NAME ..."

# 2. รันคำสั่งเซฟของ MOLA
ros2 service call /map_save mola_msgs/srv/MapSave "map_path: '$FULL_PATH'"

# 3. แอบจดจำพาทนี้ไว้ในไฟล์ชื่อ latest_map.txt เพื่อให้ตัวโหลดรู้ว่าเป็น "ไฟล์ล่าสุด"
echo "$FULL_PATH" > /home/smr/molamaps/latest_map.txt

echo "✅ บันทึกเสร็จสิ้น! (จดจำสถิติเป็นแผนที่ล่าสุดแล้ว)"
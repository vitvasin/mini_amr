import sys
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QWidget)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
import math

# Try importing ROS2 libraries
try:
    import rclpy
    from geometry_msgs.msg import Twist
except ImportError:
    print("Warning: rclpy or geometry_msgs not found. Teleop will not work directly.")
    rclpy = None

class VirtualJoystick(QWidget):
    moved = Signal(float, float) # Signal emitting (x, y) values between -1.0 and 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.moving_offset = QPointF(0, 0)
        self.grab_center = False
        self.__max_distance = 100 # Max radius for joystick movement

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bounds = QRectF(self.width()/2 - self.__max_distance, 
                        self.height()/2 - self.__max_distance, 
                        self.__max_distance * 2, 
                        self.__max_distance * 2)

        # Draw Base
        painter.setPen(QPen(Qt.black, 5))
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(bounds)

        # Draw Knob
        center = QPointF(self.rect().center())
        knob_pos = center + self.moving_offset
        
        painter.setPen(QPen(Qt.darkGray, 5))
        painter.setBrush(QBrush(Qt.red))
        painter.drawEllipse(knob_pos, 40, 40)

    def mousePressEvent(self, event):
        self.grab_center = True
        self.moving_offset = self._limit_offset(event.pos() - self.rect().center())
        self.update()
        self._emit_position()

    def mouseMoveEvent(self, event):
        if self.grab_center:
            self.moving_offset = self._limit_offset(event.pos() - self.rect().center())
            self.update()
            self._emit_position()

    def mouseReleaseEvent(self, event):
        self.grab_center = False
        self.moving_offset = QPointF(0, 0)
        self.update()
        self._emit_position()

    def _limit_offset(self, point):
        distance = math.sqrt(point.x()**2 + point.y()**2)
        if distance > self.__max_distance:
            scale = self.__max_distance / distance
            return QPointF(point.x() * scale, point.y() * scale)
        return point

    def _emit_position(self):
        # Normalize to -1.0 to 1.0
        x = self.moving_offset.x() / self.__max_distance
        y = -self.moving_offset.y() / self.__max_distance # Invert Y (up is positive)
        self.moved.emit(x, y)

class TeleopDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Robot Teleoperation")
        self.setModal(True)
        self.resize(500, 500)
        
        self.layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Status: Connecting...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.status_label)
        
        self.joystick = VirtualJoystick()
        self.layout.addWidget(self.joystick, alignment=Qt.AlignCenter)
        
        instruction = QLabel("Drag red circle to move robot.\nUp/Down: Linear Velocity\nLeft/Right: Angular Velocity")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("font-size: 16px; color: #555;")
        self.layout.addWidget(instruction)
        
        close_btn = QPushButton("Close Teleop")
        close_btn.setStyleSheet("background-color: #ffcccc; height: 50px; font-size: 20px; font-weight: bold;")
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)

        # ROS Setup
        if rclpy:
            if not rclpy.ok():
                rclpy.init(args=None)
            
            self.node = rclpy.create_node('gui_teleop_standalone_node')
            self.publisher = self.node.create_publisher(Twist, '/cmd_vel', 10)
            self.joystick.moved.connect(self.on_joystick_move)
            self.status_label.setText("Status: Ready - Publishing to /cmd_vel")
            self.status_label.setStyleSheet("color: green; font-size: 20px; font-weight: bold;")
        else:
            self.status_label.setText("Error: rclpy not available")
            self.status_label.setStyleSheet("color: red; font-size: 20px; font-weight: bold;")

    def on_joystick_move(self, x, y):
        if rclpy and self.publisher:
            msg = Twist()
            # Map x/y to velocities
            MAX_LINEAR = 0.3 # Reduced from 0.5 per user request
            MAX_ANGULAR = 1.0
            
            msg.linear.x = y * MAX_LINEAR
            msg.angular.z = -x * MAX_ANGULAR 
            
            self.publisher.publish(msg)

    def closeEvent(self, event):
        if rclpy and hasattr(self, 'node'):
            self.node.destroy_node()
            rclpy.shutdown()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TeleopDialog()
    window.show()
    sys.exit(app.exec())

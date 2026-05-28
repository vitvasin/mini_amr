# test_pyside.py
import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello, PySide6 on Armbian!")
label.show()
sys.exit(app.exec())

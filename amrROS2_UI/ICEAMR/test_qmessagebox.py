from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox
import sys

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Message Box Example")

        button = QPushButton("Show Message")
        button.clicked.connect(self.show_message)

        layout = QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

    def show_message(self):
        result = QMessageBox.question(
            self,
            "Confirm Action",
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:
            QMessageBox.information(self, "Confirmed", "You clicked Yes.")
        else:
            QMessageBox.warning(self, "Cancelled", "You clicked No.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.resize(300, 100)
    window.show()
    sys.exit(app.exec())
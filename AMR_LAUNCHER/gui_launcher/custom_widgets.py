import os
import signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QProcess
from PySide6.QtGui import QMouseEvent, QMovie

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class IntroWindow(QWidget):
    finished = Signal()

    def __init__(self, gif_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.primaryScreen().availableGeometry())
        self.setStyleSheet("background-color: black;") 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        layout.addWidget(self.label)

        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.label.setMovie(self.movie)
        
        self.movie.frameChanged.connect(self.on_frame_changed)
        self.movie.start()

    def on_frame_changed(self, frame_number):
        if frame_number == self.movie.frameCount() - 1:
            # Last frame reached
            delay = self.movie.nextFrameDelay()
            if delay <= 0: delay = 100
            self.movie.setPaused(True)
            QTimer.singleShot(delay, self.finalize)

    def finalize(self):
        self.close()
        self.finished.emit()

class LogWindow(QWidget):
    def __init__(self, title="Log Output"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: black; color: #00FF00; font-family: Monospace;")
        self.layout.addWidget(self.text_edit)
        
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_finished)

    def start_process(self, command, args):
        self.process.start(command, args)
        self.text_edit.append(f"Starting command: {command} {' '.join(args)}\n")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = data.data().decode().strip()
        if text: self.text_edit.append(text)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = data.data().decode().strip()
        if text: self.text_edit.append(f"<span style='color:red'>{text}</span>")

    def on_finished(self):
        self.text_edit.append("\nProcess Finished.")

    def closeEvent(self, event):
        self.kill_process()
        super().closeEvent(event)
    
    def kill_process(self):
         if self.process.state() != QProcess.NotRunning:
            pid = self.process.processId()
            print(f"Stopping process {pid}...")
            
            # 1. Try SIGINT (Ctrl+C)
            try:
                os.kill(pid, signal.SIGINT)
            except ProcessLookupError:
                pass
            
            # Wait for graceful shutdown (5 seconds)
            if self.process.waitForFinished(5000):
                print("Process stopped gracefully.")
                return

            print("Process did not stop, sending SIGTERM...")
            # 2. Try SIGTERM
            self.process.terminate()
            if self.process.waitForFinished(2000):
                print("Process terminated.")
                return
            
            print("Process stuck, sending SIGKILL...")
            # 3. Force SIGKILL
            self.process.kill()

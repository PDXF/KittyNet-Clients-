import socket
import random
import string
import threading
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import Qt

SERVER_HOST = "locations-class.gl.at.ply.gg"
SERVER_PORT = 11890

def generate_token():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"VKL-{part1}-{part2}-LITE"

class KittyNetLite(QWidget):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.token = generate_token()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.connection_start_time = None  
        self.init_ui()
        self.connect_to_server()

    def init_ui(self):
        self.setWindowTitle("KittyNet Lite - Version 1.0")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("""
            QWidget {
                background: #2E2E2E;
                color: white;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #B0B0B0;
            }
            QPushButton {
                background-color: #9b59b6;  /* Purple color */
                border-radius: 12px;
                padding: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #8e44ad; /* Darker purple on hover */
            }
            QTextEdit {
                background-color: #1E1E2E;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
                color: #E0E0E0;
            }
            QLineEdit {
                background-color: #3A3A3A;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #E0E0E0;
            }
        """)

        layout = QVBoxLayout()

        self.status_label = QLabel(f"Token: {self.token}")
        layout.addWidget(self.status_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            background-color: #232323;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            color: #D1D1D1;
        """)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setStyleSheet("""
            background-color: #3A3A3A;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            color: #E0E0E0;
        """)
        layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            
            request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nToken: {self.token}\r\n\r\n"
            self.client_socket.send(request.encode('utf-8'))

            response = self.client_socket.recv(1024).decode('utf-8')
            if "200 OK" in response:
                self.connected = True
                self.status_label.setText(f"Connected: {self.token}")
                threading.Thread(target=self.receive_messages, daemon=True).start()
                threading.Thread(target=self.update_connection_time, daemon=True).start()  
            else:
                self.connected = False
                self.status_label.setText("Connection failed!")
        except socket.error:
            self.connected = False
            self.status_label.setText("Error: Could not connect!")

    def send_message(self):
        message = self.input_field.text()
        if message and self.connected:
            formatted_message = f"{self.token}: {message}"
            self.display_message(f"[You]: {message}", True)
            self.client_socket.send(formatted_message.encode('utf-8'))
            self.input_field.clear()
        elif not self.connected:
            self.chat_display.append("<p style='color: red;'>Cannot send message: Server is not connected!</p>")

    def display_message(self, message, is_sender):
        color = "#9b59b6" if is_sender else "#FF7F50"
        formatted_message = f"<p style='color: {color}; font-weight: bold;'>{message}</p>"
        self.chat_display.append(formatted_message)
        self.chat_display.moveCursor(QTextCursor.End)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, False)
            except:
                self.chat_display.append("<p style='color: red;'>Disconnected from server!</p>")
                break

    def update_connection_time(self):
        while self.connected:
            if self.connection_start_time:
                elapsed_time = time.time() - self.connection_start_time
                minutes, seconds = divmod(int(elapsed_time), 60)
                time_str = f"{minutes:02}:{seconds:02}"
                self.status_label.setText(f"Connection Time: {time_str}")
            time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    kittynet_window = KittyNetLite(SERVER_HOST, SERVER_PORT)
    kittynet_window.show()
    sys.exit(app.exec_())

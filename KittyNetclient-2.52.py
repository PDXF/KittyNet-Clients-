import socket
import random
import string
import threading
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QListWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QTextCursor

SERVER_HOST = "locations-class.gl.at.ply.gg"
SERVER_PORT = 11890

def generate_token():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"VKL-{part1}-{part2}"

class KittyNet(QWidget):
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
        self.setWindowTitle("KittyNet - Version 2.52")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e2e; color: white;")
        
        main_layout = QHBoxLayout()
        self.user_list = QListWidget()
        self.user_list.setStyleSheet("background-color: #252535; border-radius: 10px; padding: 10px;")
        
        self.user_list.addItem(f"Token: {self.token}")
        self.user_list.addItem(f"Server Host: {self.host}")
        self.user_list.addItem(f"Server Port: {self.port}")
        self.user_list.addItem("Server Status: ❌")
        self.user_list.addItem("Connection Time: 00:00")  
        
        main_layout.addWidget(self.user_list, 2)
        
        chat_layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #2b2b3b; border-radius: 10px; padding: 10px;")
        chat_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setStyleSheet("background-color: #34344a; border-radius: 10px; padding: 10px; color: white;")
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("➤ Send")
        self.send_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #5865F2; color: white; border-radius: 10px;")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(input_layout)
        main_layout.addLayout(chat_layout, 5)
        self.setLayout(main_layout)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            
            request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nToken: {self.token}\r\n\r\n"
            self.client_socket.send(request.encode('utf-8'))

            response = self.client_socket.recv(1024).decode('utf-8')
            if "200 OK" in response:
                self.connected = True
                self.connection_start_time = time.time()  # Record connection start time
                self.user_list.item(3).setText("Server Status: ✅")  # Update server status
                threading.Thread(target=self.receive_messages, daemon=True).start()
                threading.Thread(target=self.update_connection_time, daemon=True).start()  # Start time update thread
            else:
                self.connected = False
                self.user_list.item(3).setText("Server Status: ❌")  # Update server status
                self.chat_display.append("<p style='color: red;'>Server rejected connection.</p>")
        except socket.error:
            self.connected = False
            self.user_list.item(3).setText("Server Status: ❌")  # Update server status
            self.chat_display.append("<p style='color: red;'>Could not connect to server!</p>")

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
        color = "#5865F2" if is_sender else "#FF7F50"
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
                self.user_list.item(4).setText(f"Connection Time: {time_str}")  
            time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    kittynet_window = KittyNet(SERVER_HOST, SERVER_PORT)
    kittynet_window.show()
    sys.exit(app.exec_())

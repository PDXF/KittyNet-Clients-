# -----------------------------------------------------------------------------
# KittyNet Lunar Dev Edition Client - Built to be Hacked (Modifiable)
# 
# This client connects to the closed-source KittyNet Network, offering 
# a custom token-based system for communication and interaction. The client 
# is built with modding and experimentation in mind – feel free to change how 
# it works, but **do not engage in malicious hacking**.
#
# Features:
# - Token-based system (customizable token suffixes)
# - Minimal chat moderation (unless needed)
# - No tolerance for harmful behavior (permanent IP blacklist and bans for violators)
# - Zero tolerance for hate speech, transphobia, homophobia, and similar ideologies
# 
# **Warning:**
# If you engage in harmful activities, your IP will be permanently blacklisted, 
# and you’ll be banned from all KittyNet-related projects, Valk, and any other 
# associated platforms. This includes tracking and banning across any available 
# networks.
#
# **Privacy & Anonymity:**
# Recommended to use an anonymous name or pseudonym instead of your real identity, 
# especially since this is a network for activism and privacy-conscious interactions.
#
# The server is closed-source and will not have its code released in the foreseeable 
# future. This is intentional to protect the network's integrity.
#
#      /\_/\  
#     ( o.o ) 
#      > ^ <
#
# -----------------------------------------------------------------------------


import socket
import random
import string
import threading
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QSplitter, QTextEdit, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

SERVER_HOST = "locations-class.gl.at.ply.gg"
SERVER_PORT = 11890

def generate_token(custom_part=None):
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    if custom_part:
        custom_part = custom_part.upper()  
        return f"VKL-{part1}-{part2}-{custom_part}"
    return f"VKL-{part1}-{part2}-LITE"  

class KittyNetLunarDevClient(QWidget):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.token = generate_token()  
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.connection_start_time = None
        self.last_send_time = 0  
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("KittyNet Lunar Dev Edition - Client Builder")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("""
            QWidget {
                background: #1A1A1A;
                color: white;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #D3D3D3;
            }
            QPushButton {
                background-color: #C0C0C0;
                border-radius: 12px;
                padding: 10px;
                color: #333;
                font-size: 14px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #A9A9A9;
            }
            QTextEdit {
                background-color: #2E2E2E;
                border: 1px solid #4A4A4A;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
                color: #E0E0E0;
            }
            QLineEdit {
                background-color: #333333;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #E0E0E0;
            }
            QComboBox {
                background-color: #333;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        main_layout = QVBoxLayout()

        self.status_label = QLabel(f"Token: {self.token}")
        main_layout.addWidget(self.status_label)

        self.server_response_label = QLabel("Server Response: Waiting for connection...")
        main_layout.addWidget(self.server_response_label)

        self.client_info_label = QLabel("Client Builder Configuration")
        main_layout.addWidget(self.client_info_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        main_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        main_layout.addWidget(self.send_button)

        self.dev_log = QTextEdit()
        self.dev_log.setReadOnly(True)
        main_layout.addWidget(self.dev_log)

        self.token_input_label = QLabel("Custom Token Suffix (e.g., DEV, TEST, HI):")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter custom suffix for token")
        self.token_input.textChanged.connect(self.update_token)
        main_layout.addWidget(self.token_input_label)
        main_layout.addWidget(self.token_input)

        self.config_button = QPushButton("Generate Config File")
        self.config_button.clicked.connect(self.generate_config_file)
        main_layout.addWidget(self.config_button)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        splitter.addWidget(main_widget)

        self.kittycli_panel = QWidget()
        self.kittycli_layout = QVBoxLayout()

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.append("Client Builder Initialized.")
        self.kittycli_layout.addWidget(self.info_display)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command in KittyCLI...")
        self.command_input.returnPressed.connect(self.execute_command)
        self.kittycli_layout.addWidget(self.command_input)

        self.kittycli_panel.setLayout(self.kittycli_layout)
        splitter.addWidget(self.kittycli_panel)

        layout.addWidget(splitter)
        self.setLayout(layout)

        try:
            self.connect_to_server()
        except Exception as e:
            self.display_dev_log(f"Error during connection: {str(e)}")

    def connect_to_server(self):
        """Establish connection with the server"""
        try:
            self.client_socket.connect((self.host, self.port))
            request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nToken: {self.token}\r\n\r\n"
            self.client_socket.send(request.encode('utf-8'))

            self.display_dev_log(f"Sent Request: {request}")

            response = self.client_socket.recv(1024).decode('utf-8')
            self.server_response_label.setText(f"Server Response: {response}")

            if "200 OK" in response:
                self.connected = True
                self.status_label.setText(f"Connected: {self.token}")
                threading.Thread(target=self.receive_messages, daemon=True).start()
                threading.Thread(target=self.update_connection_time, daemon=True).start()
            else:
                self.connected = False
                self.status_label.setText("Connection failed!")
                self.display_dev_log(f"Error: {response}")
        except socket.error as e:
            self.connected = False
            self.status_label.setText("Error: Could not connect!")
            self.display_dev_log(f"Connection failed: {e}")

    def send_message(self):
        """Send message to the server"""
        current_time = time.time()
        if current_time - self.last_send_time < 1:  
            self.display_dev_log("Message sending too quickly, please wait a moment.")
            return

        if self.connected:
            message = self.input_field.text()
            if message:
                formatted_message = f"{self.token}: {message}"
                self.display_message(f"[You]: {message}", True)
                self.client_socket.send(formatted_message.encode('utf-8'))
                self.input_field.clear()

                self.last_send_time = current_time
        else:
            self.chat_display.append("<p style='color: red;'>Cannot send message: Server is not connected!</p>")

    def display_message(self, message, is_sender):
        """Display sent or received message in the chat window"""
        color = "#C0C0C0" if is_sender else "#B0C4DE"
        formatted_message = f"<p style='color: {color}; font-weight: bold;'>{message}</p>"
        self.chat_display.append(formatted_message)
        self.chat_display.moveCursor(QTextCursor.End)

    def receive_messages(self):
        """Receive messages from the server"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, False)

                    self.display_dev_log(f"Received Message: {message}")
            except Exception as e:
                self.chat_display.append("<p style='color: red;'>Error receiving message</p>")
                self.display_dev_log(f"Error: {str(e)}")
                break

    def update_connection_time(self):
        """Keep track of the connection time"""
        self.connection_start_time = time.time()
        while self.connected:
            if self.connection_start_time:
                elapsed_time = int(time.time() - self.connection_start_time)
                self.status_label.setText(f"Connected for: {elapsed_time} seconds")
            time.sleep(1)

    def display_dev_log(self, message):
        """Log information for development purposes"""
        self.dev_log.append(f"[LOG]: {message}")
        self.dev_log.moveCursor(QTextCursor.End)

    def update_token(self):
        """Update the token based on custom input"""
        custom_part = self.token_input.text()
        self.token = generate_token(custom_part)  #
        self.status_label.setText(f"Token: {self.token}")

    def generate_config_file(self):
        """Generate and save the configuration file for the client"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Config File", "", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, "w") as file:
                file.write(f"Client Token: {self.token}\n")
                file.write(f"Server Host: {self.host}\n")
                file.write(f"Server Port: {self.port}\n")
            self.display_dev_log(f"Configuration file saved as {file_name}")

    def execute_command(self):
        """Execute a command entered in KittyCLI"""
        command = self.command_input.text()
        if command:
            self.info_display.append(f"Executing command: {command}")
            self.command_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_builder = KittyNetLunarDevClient(SERVER_HOST, SERVER_PORT)
    client_builder.show()
    sys.exit(app.exec_())

# -----------------------------------------------------------------------------
# KittyNet Lunar Dev Edition - Client Builder:
# This Python application is a client builder for the KittyNet Lunar Dev Edition, 
# which operates over the KittyNet Network. It is designed to connect to a remote 
# server, generate a unique client token, and facilitate communication with the 
# server through a graphical user interface (GUI).
# 
# This client is intentionally built to be "hacked" or modified, allowing developers
# to experiment with the code, adjust the functionality, and learn about networking, 
# token generation, and real-time communication. It's a tool meant for customization 
# and testing, not for malicious hacking.
# 
# The client allows users to send and receive messages, monitor the connection status,
# and generate configuration files for connecting to the server. It also includes
# a custom token generator that supports user-defined suffixes for the token, and logs
# various actions taken by the client, such as connection attempts and message exchanges.
#
# **Token System:**
# The token system is a key component of this client. Each client is issued a unique token
# upon initialization, which is used to identify the client within the KittyNet Network.
# The default token format is `VKL-XXX-YYYY-LITE`, where:
#   - `XXX` and `YYYY` are random alphanumeric parts generated at the start.
#   - The `LITE` suffix is used as a default value indicating the basic version.
#
# Users have the option to provide a **custom suffix** for their token, such as `DEV`, 
# `TEST`, or any other custom string, allowing them to create tokens specific to their 
# needs. This token is used for communication with the server and can be viewed on the
# GUI interface as a status indicator.
# 
# The client verifies the connection using this token when sending requests to the server. 
# It ensures the integrity of the session by sending the token along with every message
# and identifying the client with it. This system helps track and manage clients effectively 
# within the closed network environment.
#
# **Moderation:**
# There is **near to NO moderation** in the chat within the KittyNet Network unless 
# it is absolutely necessary. This means the chat is designed to allow free expression 
# and communication between users with minimal intervention. The aim is to maintain a 
# more open, flexible environment where developers can interact and test the client 
# without constant oversight. However, moderation will step in if any harmful or disruptive 
# activity is detected or reported.
#
# **Severe Consequences for Disruptive Behavior:**
# If any user engages in behavior that is deemed HORRIBLE or deeply disruptive—such as
# spreading harmful content, harassing others, or intentionally damaging the experience 
# of the community—the following actions will be taken:
#
# 1. **Permanent IP Blacklist:** Your IP will be added to a **permanent blacklist**, 
#    preventing you from accessing the KittyNet Network and any associated services.
# 
# 2. **Ban from All Kitty Projects:** You will be banned from all KittyNet-related projects, 
#    including any KittyNet systems, clients, and servers, as well as **Valk** and any other 
#    associated environments or systems.
# 
# 3. **Tracking Across Platforms:** In addition to being banned from KittyNet and Valk,
#    your activities will be tracked, and if possible, you will be banned from any other 
#    platforms or projects associated with these communities. This may include any projects 
#    or networks we can trace your activity to.
#
# **Zero Tolerance for Hate Speech:**
# We do not tolerate hate speech or discriminatory behavior of any kind. This includes,
# but is not limited to, **Nazism**, **transphobia**, **homophobia**, and any other form 
# of harmful ideology or speech directed at marginalized groups. 
#
# Our community is built on inclusivity, respect, and support for all individuals, regardless 
# of gender, race, sexuality, or identity. Hate speech and discrimination will not be allowed 
# and will lead to immediate and permanent removal from the KittyNet Network and related projects.
#
# **Anonymous or Pseudonymous Usage Recommended:**
# While it is not mandatory, we **highly recommend** using an **anonymous or pseudonymous name**
# instead of your real one when interacting on the KittyNet Network. This network serves as a platform
# for **activism** and other sensitive purposes, where privacy and security are key.
#
# By using an anonymous name, you help protect your identity and ensure your safety, especially when 
# discussing or working on topics that may be controversial, sensitive, or politically charged. 
#
# Protecting your anonymity contributes to the overall integrity of the network, enabling everyone to 
# interact freely without fear of being targeted or identified. We encourage users to exercise caution 
# when revealing personal details, and to always prioritize their safety and privacy.
#
# The server this client connects to is **closed-source** and will most likely 
# never have its code released. It is part of the proprietary KittyNet Network, 
# which is intentionally kept private for security and operational reasons.
#
# Features:
# - Connect to a specified server and handle server communication
# - Generate unique tokens for each client session
# - Send and receive messages in real-time through a chat interface
# - Display development logs for debugging purposes
# - Generate and save configuration files for server connection settings
# 
# Note: This client is specifically designed to work with the KittyNet Network and 
# may not function properly with other network setups.
# 
# **Security Notice:**
# To maintain your privacy and security, we recommend using a VPN when accessing the KittyNet 
# Network to protect your connection and location.
# Always be cautious when interacting with unfamiliar tokens or accounts.
#  
# # **Phishing and Scams Warning:**
# Be aware of phishing attempts and scams within the network. Never click on suspicious links 
# or share your account details with others. If you receive messages asking for your credentials, 
# block and report the user immediately. Always verify the authenticity of requests and never share 
# your tokens or personal information with unknown sources.
#
# # **Phishing Scams in Chat:**
# Be cautious when receiving direct messages or links in the chat. Scammers may pose as fellow users or even as KittyNet staff 
# to get you to reveal sensitive information or click on malicious links. Always verify the sender and their request before taking action.
# 
# # **Sensitive or Inappropriate Content:**
# Inappropriate content, whether violent, sexually explicit, or offensive, has no place in the KittyNet chat. 
# If you come across this kind of content, **report it immediately** to ensure the platform remains safe and welcoming for everyone.
#
# **Session-Based Tokens:**
# Your token is unique to each session, meaning once you disconnect and reconnect, you'll receive a different token. 
# This enhances security by limiting the lifetime of a token and preventing misuse from past sessions.
#
# **Visibility of Tokens:**
# Everyone on KittyNet can see your session token. It's part of your user profile, and it helps identify you during your session.
# However, **never rely on the token for security** as it's visible to all members of the network.
#
# # **Never Share Your Token:**
# Even though the token is publicly visible in your profile, **do not share it privately** with others. 
# Sharing your token outside KittyNet increases the risk of impersonation or misuse.
# 
#      /\_/\  
#     ( o.o ) 
#      > ^ <
# =^.^=  Be smart, be kind, and have fun. The internet is your playground — make it a good one!
#
# ------------------------------------------------------------------------------------------------------


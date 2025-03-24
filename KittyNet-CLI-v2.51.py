import socket
import random
import string
import threading
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

SERVER_HOST = "locations-class.gl.at.ply.gg"
SERVER_PORT = 11890

console = Console()

def generate_token():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"VKL-{part1}-{part2}"

class KittyNetClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.token = generate_token()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            request = f"GET / HTTP/1.1\r\nHost: {self.host}\r\nToken: {self.token}\r\n\r\n"
            self.client_socket.send(request.encode('utf-8'))

            response = self.client_socket.recv(1024).decode('utf-8')
            if "200 OK" in response:
                self.connected = True
                console.print(f"[green]Connected to server at {self.host}:{self.port}[/green]")
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                self.connected = False
                console.print("[red]Server rejected connection[/red]")
        except socket.error:
            self.connected = False
            console.print("[red]Could not connect to server![/red]")

    def send_message(self, message):
        if message and self.connected:
            formatted_message = f"{self.token}: {message}"
            console.print(f"[bold blue]You:[/bold blue] {message}")
            self.client_socket.send(formatted_message.encode('utf-8'))
        elif not self.connected:
            console.print("[red]Cannot send message: Server is not connected![/red]")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    console.print(f"[bold orange]Server:[/bold orange] {message}")
            except:
                console.print("[red]Disconnected from server![/red]")
                break

    def display_tui(self):
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
        )

        layout["header"].update(Panel("KittyNet Client", title="Status", subtitle="Connected"))
        message_text = Text("Type your message and hit Enter to send", style="bold blue")
        layout["main"].update(Panel(message_text, title="Message Panel"))
        console.print(layout)

def main():
    client = KittyNetClient(SERVER_HOST, SERVER_PORT)
    client.connect_to_server()

    while True:
        try:
            user_input = input("\nType a message or press Ctrl+C to exit: ")

            if user_input:
                client.send_message(user_input)
        except KeyboardInterrupt:
            console.print("[red]Ctrl+C detected. Exiting...[/red]")
            sys.exit(0)

if __name__ == '__main__':
    main()

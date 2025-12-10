import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 50000))

message = client.recv(1024).decode()

lines_declared = input(message)
client.send(lines_declared.encode())
while True:
    message = client.recv(1024).decode()
    if not message or message == "DONE":
        break
    if message != "\n":
        print(message.strip())
import socket,time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('127.0.0.1',5000))
info = s.recv(1024).decode("ascii")

print(info)
try:
    while 1:
        command = input()
        s.sendall(bytes(command,encoding="ascii"))

        data = s.recv(1024).decode("ascii")
        print(f"{str(data)}")

        if command == "--EXIT":
            break

        time.sleep(1)
except KeyboardInterrupt:
    print("\nDisconnecting client")
    s.close()


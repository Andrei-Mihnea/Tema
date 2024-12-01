import socket,time
import threading

def recv_msg(sock):
    while 1:
        try:
            data = sock.recv(1024).decode("ascii")

            if not data:
                print("Connection closed from server")
                break

            print(data)

        except Exception as e:
            pass
            break
    sock.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('127.0.0.1',5000))
info = s.recv(1024).decode("ascii")

print(info)

threading.Thread(target=recv_msg,args=(s,),daemon=True).start()

try:
    while 1:
        try:
            command = input()
            s.sendall(bytes(command,encoding="ascii"))

            if command == "--EXIT":
                break
        except OSError:
            print("Connection interrupted")
            break

        time.sleep(1)
except KeyboardInterrupt:
    print("\nDisconnecting client")

s.close()


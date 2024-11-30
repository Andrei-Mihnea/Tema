import socket
import threading
from threading import Lock

clients = {} #dictionary for memorising the nicknames
clients_lock = Lock()


def comm_thread(conn,addr):
    print(f"User connected with port {addr[1]} ")
    conn.sendall(bytes(f"Connection succeeded!\nPlease change your name using the command --NAME=(your name)",encoding="ascii"))

    with clients_lock:
        clients[conn] = f"{addr[1]}"
    try:
        while 1:
            try:
                data = conn.recv(1024).decode("ascii")
                if not data:
                    break
                command = str(data)
                if command.startswith("--EXIT"):
                    print(f"User with name {clients[conn]} has disconnected from the server")
                    conn.sendall(bytes(f"User with name {clients[conn]} has disconnected from the server",encoding="ascii"))
                    break
                    
                elif command.startswith("--NAME"):
                    new_name = command[7:].lower()

                    with clients_lock:
                        if new_name in clients.values():
                            print("Error")
                            conn.sendall(bytes("Operation failed\nName already taken, try something else\nPlease change your name using the command --NAME=(your name)",encoding="ascii"))
                        else:
                            print(f"{clients[conn]} changed its name to {str(new_name)}")
                            conn.sendall(bytes(str(clients[conn]) + 'changed its name to ' + str(new_name), encoding="ascii"))
                            clients[conn] = new_name

                elif command.startswith("--DISP"):
                        print(clients)
                        conn.sendall(bytes("Data printed to server",encoding="ascii"))

                elif command.startswith("--CLOSE"):
                    with clients_lock:
                        username = str(command[8:].lower())
                        if clients[conn] == "admin" and username != "admin":
                            target_conn = None 
                            for connection,name in clients.items():
                                if name == username:
                                    target_conn = connection
                                    break
                            if target_conn:
                                print(f"User {username} disconnected by admin")
                                target_conn.sendall(bytes("You have been disconnected by the admin",encoding="ascii"))
                                conn.sendall(bytes(f"{clients[target_conn]} will be disconnected",encoding="ascii"))
                                target_conn.close()
                                del clients[target_conn] 
                            else:
                                conn.sendall(bytes(f"User not found with username {username}",encoding="ascii"))
                        else:
                            conn.sendall(bytes("You don't have the permission to use such command\nIf you are the admin u cannot kick yourself",encoding="ascii"))

                elif command.startswith("--HELP"):
                    conn.sendall(bytes("Use commands such as:\n --NAME=*new_name*(to change your name\n--EXIT to change your name",encoding="ascii"))

                    
                else:
                    conn.sendall(bytes("Unkown command, try use help to get a list of all commands"))
                    
                print("____________________________________________")
            except ConnectionResetError:
                    print(f"Connection interrupted abruptly from {clients.get(conn,addr[1])}")
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
    except WindowsError:
        with clients_lock:
            if conn in clients:
                print(f"Deleting traces for client {clients[conn]}")
                del clients[conn]
        conn.close()
        print("Connection closed")
            

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('127.0.0.1',5000))

s.listen(10)

print('Waiting for connection...\n(To stop waiting use Ctrl+C)')
try:
    while 1:
        conn,addr = s.accept()
        print("User connected with ip" + str(addr))
        threading.Thread(target = comm_thread, args= (conn,addr)).start()
except KeyboardInterrupt:
    print("Server closed its connection")
finally:
    s.close()
    print("Server stopped")


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

    check = False
    try:
        while 1:
            try:
                data = conn.recv(1024).decode("ascii")
                if not data:
                    break
                command = str(data)

                if not check and not command.upper().startswith("--NAME"):
                        conn.sendall(bytes("Please use --NAME=(username) command to register your name",encoding="ascii"))
                elif command.upper().startswith("--EXIT"):
                    print(f"User with name {clients[conn]} has disconnected from the server")
                    for connection in clients.keys():
                        if connection != conn:
                            connection.sendall(bytes(f"User with name {clients[conn]} has disconnected from the server",encoding="ascii"))
                        conn.sendall(bytes(f"User {clients[conn]} disconnected from server",encoding="ascii"))
                    with clients_lock:
                        del clients[conn]
                    break
                    
                elif command.upper().startswith("--NAME"):
                    new_name = command[7:].lower()
                    check = True
                    with clients_lock:
                        if new_name in clients.values():
                            print("Error")
                            conn.sendall(bytes("Operation failed\nName already taken, try something else\nPlease change your name using the command --NAME=(your name)",encoding="ascii"))
                        else:
                            print(f"{clients[conn]} changed its name to {str(new_name)}")
                            conn.sendall(bytes(str(clients[conn]) + ' changed its name to ' + str(new_name), encoding="ascii"))
                            clients[conn] = new_name

                elif command.startswith("--DISP"):
                        print(clients.values())
                        conn.sendall(bytes("Data printed to server",encoding="ascii"))

                elif command.upper().startswith("--CLOSE"):
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

                                for connection in clients.keys():
                                    if connection != target_conn:
                                        connection.sendall(bytes(f"User {username} got its connection closed by the admin",encoding="ascii"))

                                target_conn.sendall(bytes("You have been disconnected by the admin",encoding="ascii"))
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
            except (ConnectionResetError,OSError,ConnectionAbortedError):
                    with clients_lock:
                        print(f"Connection ended abruptly by {clients[conn]}")
                        break
    except Exception as e:        
            print(f"Unexpected error {e}")

    conn.close()
    
            

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


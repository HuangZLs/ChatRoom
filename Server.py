import socket
import threading


def log_message(message):
    with open("chat_log.txt", "a", encoding="utf-8") as file:
        file.write(message + "\n")


def server():
    host = '0.0.0.0'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    clients = []
    print(f"服务器运行在 {host}:{port}")
    try:
        while True:
            conn, addr = server_socket.accept()
            clients.append(conn)
            threading.Thread(target=client_thread, args=(conn, addr, clients)).start()
    except Exception as e:
        print(f"服务器错误: {e}")
    finally:
        server_socket.close()


def send_history(conn):
    try:
        with open("chat_log.txt", "r", encoding="utf-8") as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                conn.send(chunk.encode('utf-8'))
    except FileNotFoundError:
        conn.send("[Server]没有可用的聊天历史。".encode('utf-8'))


def client_thread(conn, addr, clients):
    conn.send("history_request".encode('utf-8'))  # 提示客户端请求历史记录
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            if message == "request_history":
                send_history(conn)
            else:
                full_message = f"{addr[0]}> {message}"
                print(full_message)
                log_message(full_message)
                for c in clients:
                    c.sendall(full_message.encode('utf-8'))
        except:
            continue


if __name__ == "__main__":
    server()

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter.simpledialog import askstring

def receive():
    history_loaded = False
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == "history_request":
                client_socket.send("request_history".encode('utf-8'))
            elif message:
                chat_box.config(state='normal')
                chat_box.insert(tk.END, message + "\n")
                chat_box.yview(tk.END)
                chat_box.config(state='disabled')
                if not history_loaded:
                    chat_box.insert(tk.END, "\n--- 以下是新消息 ---\n")
                    history_loaded = True
        except OSError:  # 可能客户已离开聊天室。
            break


def send(event=None):
    message = my_msg.get()
    my_msg.set("")  # 清空输入字段。
    client_socket.send(message.encode('utf-8'))
    if message == "{quit}":
        client_socket.close()
        window.quit()

def on_closing(event=None):
    my_msg.set("{quit}")
    send()

def load_initial_chat():
    try:
        with open("chat_log.txt", "r", encoding="utf-8") as file:
            chat_history = file.read()
            chat_box.config(state='normal')
            chat_box.insert(tk.END, chat_history)
            chat_box.yview(tk.END)
            chat_box.config(state='disabled')
    except FileNotFoundError:
        print("没有可用的聊天历史。")

# 创建窗口
window = tk.Tk()
window.title("ChatRoom")

messages_frame = tk.Frame(window)
my_msg = tk.StringVar()  # 发送消息。
my_msg.set("在这里输入消息。")
scrollbar = tk.Scrollbar(messages_frame)  # 滚动查看历史消息。
# 下面将包含消息。
chat_box = scrolledtext.ScrolledText(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_box.pack(side=tk.LEFT, fill=tk.BOTH)
chat_box.pack()
messages_frame.pack()

entry_field = tk.Entry(window, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tk.Button(window, text="发送", command=send)
send_button.pack()

window.protocol("WM_DELETE_WINDOW", on_closing)

# Socket 部分
HOST = askstring('主机', '输入主机IP')
PORT = askstring('端口', '输入端口号')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, int(PORT)))
load_initial_chat()

threading.Thread(target=receive).start()

window.mainloop()

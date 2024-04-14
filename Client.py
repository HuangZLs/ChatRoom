import socket
import threading
from PyQt5 import QtWidgets, QtGui, QtCore


class ChatClient(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatRoom")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.chat_layout = QtWidgets.QVBoxLayout()

        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.chat_layout)

        self.dark_mode_checkbox = QtWidgets.QCheckBox("深色模式", self)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        self.top_layout.addWidget(self.dark_mode_checkbox)

        self.host_label = QtWidgets.QLabel("主机IP:", self)
        self.host_label.setFont(QtGui.QFont("Helvetica", 10))
        self.top_layout.addWidget(self.host_label)

        self.host_input = QtWidgets.QLineEdit(self)
        self.host_input.setFont(QtGui.QFont("Helvetica", 10))
        self.top_layout.addWidget(self.host_input)

        self.port_label = QtWidgets.QLabel("端口号:", self)
        self.port_label.setFont(QtGui.QFont("Helvetica", 10))
        self.top_layout.addWidget(self.port_label)

        self.port_input = QtWidgets.QLineEdit(self)
        self.port_input.setFont(QtGui.QFont("Helvetica", 10))
        self.top_layout.addWidget(self.port_input)

        self.connect_button = QtWidgets.QPushButton("连接", self)
        self.connect_button.setFont(QtGui.QFont("Helvetica", 10))
        self.connect_button.clicked.connect(self.connect_to_server)
        self.top_layout.addWidget(self.connect_button)

        self.chat_box = QtWidgets.QTextEdit(self)
        self.chat_box.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_box)

        self.entry_field = QtWidgets.QLineEdit(self)
        self.entry_field.setFont(QtGui.QFont("Helvetica", 12))
        self.entry_field.returnPressed.connect(self.send_message)
        self.chat_layout.addWidget(self.entry_field)

        self.send_button = QtWidgets.QPushButton("发送", self)
        self.send_button.setFont(QtGui.QFont("Helvetica", 12))
        self.send_button.clicked.connect(self.send_message)
        self.chat_layout.addWidget(self.send_button)

        self.HOST = ""
        self.PORT = 0

        self.client_socket = None

        self.load_initial_chat()

        self.receive_thread = None

        self.set_font()

    def set_font(self):
        font = QtGui.QFont("微软雅黑", 10)
        self.setFont(font)

        self.host_label.setFont(font)
        self.host_input.setFont(font)
        self.port_label.setFont(font)
        self.port_input.setFont(font)
        self.connect_button.setFont(font)
        self.chat_box.setFont(font)
        self.entry_field.setFont(font)
        self.send_button.setFont(font)

    def toggle_dark_mode(self, state):
        if state == QtCore.Qt.Checked:
            self.setStyleSheet("background-color: #1e1e1e; color: #fff;")
        else:
            self.setStyleSheet("background-color: #fff; color: #000;")

    def connect_to_server(self):
        self.HOST = self.host_input.text()
        self.PORT = int(self.port_input.text())

        if not self.HOST or not self.PORT:
            QtWidgets.QMessageBox.warning(self, "警告", "请输入主机IP和端口号")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))

            self.receive_thread = threading.Thread(target=self.receive)
            self.receive_thread.start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"无法连接到服务器：{str(e)}")

    def send_message(self):
        if not self.client_socket:
            QtWidgets.QMessageBox.warning(self, "警告", "请先连接到服务器")
            return

        message = self.entry_field.text()
        self.entry_field.clear()
        self.client_socket.send(message.encode('utf-8'))
        if message == "退出了聊天室":
            self.client_socket.close()
            self.close()

    def load_initial_chat(self):
        try:
            with open("chat_log.txt", "r", encoding="utf-8") as file:
                chat_history = file.read()
                self.chat_box.insertPlainText(chat_history)
        except FileNotFoundError:
            print("没有可用的聊天历史。")

    def receive(self):
        history_loaded = False
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "history_request":
                    self.client_socket.send("request_history".encode('utf-8'))
                elif message:
                    self.chat_box.moveCursor(QtGui.QTextCursor.End)
                    self.chat_box.insertPlainText(message + "\n")
                    if not history_loaded:
                        self.chat_box.insertPlainText("\n--- 以下是新消息 ---\n")
                        history_loaded = True
            except OSError:
                break

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.send("退出了聊天室".encode('utf-8'))
            self.client_socket.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
    app.setPalette(palette)
    font = QtGui.QFont("Helvetica", 12)
    app.setFont(font)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())

# huangZL huangZL magic0610 magic0610

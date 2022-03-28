from socket import *

s = socket(AF_INET,SOCK_STREAM)
s.connect(("127.0.0.1", 19500))


msg = input("Enter your command: ")
msg = msg.encode()
s.send(msg)

txt = s.recv(1024).decode()
print(txt)
from __future__ import print_function
import socket
import getpass
import json
from threading import Timer

HOST = '10.0.0.4'
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def auth():
	username = raw_input("Enter the username [%s]: " % getpass.getuser())
	if not user:
		username = getpass.getuser()

	prompt = lambda: (getpass.getpass(), getpass.getpass('Re-enter the password: '))

	password, conf = prompt()
	while password != conf:
		print('Incorrect Password. Try again.')
		password, conf = prompt()

	return username, password

while 1:
	p, addr = s.recvfrom(1024)
	print(p, end='')
	
	if p == 'done\n':
		break;

	reply = ''
	if 'Password' in p and 'Options' not in p:
		reply = getpass.getpass('')
	else:
		reply = raw_input()

	s.send(reply)

s.close()

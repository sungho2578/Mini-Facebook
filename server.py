import socket
import json
from inspect import cleandoc
from thread import *

HOST = '10.0.0.4'
PORT = 5000

clients = { 
	'user': {
		'password': 'pass',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	}, 
	'user2': {
		'password': 'pass2',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	},
	'user3': {
		'password': 'pass3',
		'isOnline': False,
		'connection': None,
		'newpost': 0,
		'queue': [],
		'fqueue': [],
		'friends': [],
		'timeline': [],
	} 
}

def client_thread(conn):
	try:
		conn.send('\n::: Welcome to Mini-Facebook! :::\nPress Enter to continue.\n')
		conn.send('Enter the username: ')
		usr = conn.recv(1024)
		conn.send('Enter the password: ')
		pswd = conn.recv(1024)

		if usr not in clients or clients[usr]['password'] != pswd:
			conn.send('Invalid username or password.\nClosing connection...\n')
			conn.close()
		
		clients[usr]['isOnline'] = True;
		clients[usr]['connection'] = conn;
		
		options = cleandoc("""
		Choose an action:

		1. Logout
		2. Change Password
		3. View Messages
		""")
	
		conn.send('\n' + options + '\n')


		while 1:
			data = conn.recv(1024)
			if not data:
				conn.send('Invalid input')
				continue
			
			if data == '1':
				clients[usr]['isOnline'] = False
				conn.send('Loggin out...\n')
				conn.close()

			if data == '2':
				conn.send('Enter the old password: ')
				oldPswd = conn.recv(1024)
				conn.send('Enter the new Password: ')
				newPswd = conn.recv(1024)
				
				if oldPswd == clients[usr]['password']:
					clients[usr]['password'] = newPswd
					conn.send('Password successfully changed.\n')
				else:
					conn.send('Old password invalid.')

			if data == '3':
				conn.send('{} unread messages\n'.format(len(clients[usr]['queue'])))
				for message in clients[usr]['queue']:
					conn.send('{}: {}'.format(message['from'], message['message']))
				del clients[usr]['queue'][:]
		
		
			conn.send('\n' + options + '\n')


	except:
		print('Client disconnected')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)
print('Waiting for connection...[{}]'.format(PORT))

while 1:
	conn, addr = s.accept()
	print('Connected with client {}:{}'.format(addr[0], addr[1]))
	start_new_thread(client_thread, (conn,))

s.close()	

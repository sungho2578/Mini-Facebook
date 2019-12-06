import socket
import json
from thread import *
from inspect import cleandoc

HOST = '10.0.0.4'
PORT = 5000

clients = { 
	'user': {
		'password': 'pass',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
	}, 
	'user2': {
		'password': 'pass2',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
	},
	'user3': {
		'password': 'pass3',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
	} 
}

def client_thread(conn):
	try:
		conn.send('\n::: Welcome to Mini-Facebook! :::')
		conn.send('\n')
		conn.send('Enter the username: ')
		username = conn.recv(1024)
		conn.send('Enter the password: ')
		password = conn.recv(1024)

		if username not in clients or clients[username]['password'] != password:
			conn.send('Invalid username or password.\nClosing connection...\n')
			conn.close()
		
		clients[username]['online'] = True;
		clients[username]['connection'] = conn;
		
		menu = cleandoc("""
		::: Choose an action :::
		1. Read Unread Messages
		2. Send Private Message
		3. Send Broadcast Message
		4. Change Password
		5. Logout
		""")
	
		conn.send('\n' + menu + '\n')
		conn.send('You have {} unread messages.\n'.format(len(clients[username]['messages'])))

		while 1:
			data = conn.recv(1024)
			if not data:
				conn.send('Invalid input.\n')
				continue
			
			if data == '1':
				for message in clients[username]['messages']:
					conn.send('{}: {}'.format(message['from'], message['message']))
				del clients[username]['messages'][:]

			if data == '2':
				conn.send('Send to: ')
				receiver = conn.recv(1024)
				conn.send('Message: ')
				mes = conn.recv(1024)
				mes = mes + '\n'

				if clients[receiver]['online']:
					conn.send('Message has been sent.\n')
					clients[receiver]['connection'].send('{}: {}'.format(username, mes))
					#clients[receiver]['connection'].send(menu)
				else:
					conn.send('The receiver is currently offline.\nThe message has been sent to inbox.\n')
					clients[receiver]['messages'].append({'from': username, 'message': mes})


			if data == '3':
				conn.send('Broadcast message: ')
				mes = conn.recv(1024)
				mes = mes + '\n'
				for user in clients:
					if clients[user]['online']:
						clients[user]['connection'].send('{}: {}'.format(user, mes))
						#clients[user]['connection'].send(menu)
				conn.send('Broadcast message has been sent.\n')

			if data == '4':
				conn.send('Enter the old password: ')
				old_pass = conn.recv(1024)
				conn.send('Enter the new password: ')
				new_pass = conn.recv(1024)
				
				if old_pass == clients[username]['password']:
					clients[username]['password'] = new_pass
					conn.send('Password successfully changed.\n')
				else:
					conn.send('Old password invalid.\n')

			if data == '5':
				clients[username]['online'] = False
				conn.send('Logout successful.\n')
				conn.close()
		
			conn.send('\n' + menu + '\n')
			conn.send('You have {} unread messages.\n'.format(len(clients[username]['messages'])))

	except:
		print('Client disconnected.')

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

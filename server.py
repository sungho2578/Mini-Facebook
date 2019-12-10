import socket
import json
from thread import *
from inspect import cleandoc
import datetime

HOST = '10.0.0.4'
PORT = 5000

clients = { 
	'user': {
		'password': 'pass',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
		'friendlist': [],
		'friendrequest': [],
		'timeline': [],
	}, 
	'user2': {
		'password': 'pass2',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
		'friendlist': [],
		'friendrequest': [],
		'timeline': [],
	},
	'user3': {
		'password': 'pass3',
		'online': False,
		'connection': None,
		'count': 0,
		'messages': [],
		'friendlist': [],
		'friendrequest': [],
		'timeline': [],
	} 
}

def posting_time():
	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
	return time[:-4]

def client_thread(conn):
	try:
		conn.send('\n::: Welcome to Mini-Facebook! :::\n')
		conn.send('Enter the username: ')
		username = conn.recv(1024)
		conn.send('Enter the password: ')
		password = conn.recv(1024)

		if username not in clients or clients[username]['password'] != password:
			conn.send('\nInvalid username or password.\nClosing connection...\n')
			conn.close()
		
		clients[username]['online'] = True;
		clients[username]['connection'] = conn;
		
		menu = cleandoc("""

		::: Choose an action :::
		1. Read Unread Messages
		2. Send Private Message
		3. Send Broadcast Message
		4. View Friend Options
		5. View Post Status Options
		6. See Timeline
		7. Change Password
		8. Logout

		""")

		friend_menu = cleandoc("""

		<<< Choose an action >>>
		1. View Friend List
		2. Send Friend Request
		3. Remove Friend
		4. View Friend Requests
		5. Exit the menu

		""")

		friend_request_menu = cleandoc("""

		*** Choose an action ***
		1. Accept Friend Request
		2. Decline Friend Request
		3. Not now

		""")

		post_menu = cleandoc("""

		<<< Choose an action >>>
		1. Post current status
		2. Post different status
		3. Not now

		""")

		conn.send('\n' + menu + '\n')
		conn.send('\nYou have {} unread messages.\n'.format(len(clients[username]['messages'])))
		conn.send('You have {} pending friend requests.\n'.format(len(clients[username]['friendrequest'])))
		conn.send('You have {} new posts on timeline.\n'.format(clients[username]['count']))

		while 1:
			data = conn.recv(1024)
			if not data:
				conn.send('\nInvalid input.\n')
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
					conn.send('\nMessage has been sent.\n')
					clients[receiver]['connection'].send('{}: {}'.format(username, mes))
					#clients[receiver]['connection'].send(menu)
				else:
					conn.send('\nThe receiver is currently offline.\nThe message has been sent to inbox.\n')
					clients[receiver]['messages'].append({'from': username, 'message': mes})

			if data == '3':
				conn.send('Broadcast message: ')
				mes = conn.recv(1024)
				mes = mes + '\n\n'
				for user in clients:
					if clients[user]['online']:
						clients[user]['connection'].send('{}: {}'.format(user, mes))
						clients[user]['connection'].send(menu)
				conn.send('\n\nBroadcast message has been sent.\n')

			if data == '4':
				conn.send('\n' + friend_menu + '\n')

				while 1:
					input = conn.recv(1024)
					if input == '1':
						for friend in clients[username]['friendlist']:
							conn.send(friend + "\n")
		
					if input == '2':
						conn.send("Username to add: ")
						uadd = conn.recv(1024)
						if uadd not in clients:
							conn.send("\nInvalid username.\n")
						elif username in clients[uadd]['friendlist']:
							conn.send("\nThis user is already a friend.\n")
						else:
							clients[uadd]['friendrequest'].append(username)
		
					if input == '3':
						conn.send("=== Friend List ===\n")
						for friend in clients[username]['friendlist']:
							conn.send(friend + "\n")

						conn.send("Friend to remove: ")
						urem = conn.recv(1024)

						if urem not in clients[username]['friendlist']:
							conn.send("\nInvalid username.\n")
						else:
							clients[username]['friendlist'].remove(urem)
							clients[urem]['friendlist'].remove(username)
		
					if input == '4':
						for ureq in clients[username]['friendrequest']:
							conn.send('\nFriend request from ' + ureq + '.\n')
							conn.send(friend_request_menu + '\n')
							req_answer = conn.recv(1024)

							if req_answer == '1':
								if ureq in clients[username]['friendlist']:
									conn.send("\n" + ureq + "is already your friend.\n")
									clients[username]['friendrequest'].remove(ureq)
								else:
									clients[username]['friendlist'].append(ureq)
									clients[ureq]['friendlist'].append(username)
									clients[username]['friendrequest'].remove(ureq)
	
							if  req_answer == '2':
								if ureq in clients[username]['friendlist']:
									clients[username]['friendlist'].remove(ureq)

								clients[username]['friendrequest'].remove(ureq)

							if req_answer == '3':
								pass

					if input == '5':
						conn.send("\nExiting to main menu.\n")
						break

					conn.send("\n" + friend_menu + "\n")

			if data == '5':
				while 1:
					conn.send("Status to post: ")
					status = conn.recv(1024)
					conn.send(post_menu + '\n\n')
					ans = conn.recv(1024)

					if ans == '1':
						time = posting_time()
						clients[username]['timeline'].append({'time': time, 'user': username, 'status': status})
						for friend in clients[username]['friendlist']:
							clients[friend]['timeline'].append({'time': time, 'user': username, 'status': status})
							clients[friend]['count'] += 1
						break

					if ans == '2':
						pass
					if ans == '3':
						pass

			if data == '6':
				for post in clients[username]['timeline']:
					conn.send('{} {}: {}'.format(post['time'], post['user'], post['status']) + '\n')

				clients[username]['count'] = 0

			if data == '7':
				conn.send('Enter the old password: ')
				old_pass = conn.recv(1024)
				conn.send('Enter the new password: ')
				new_pass = conn.recv(1024)
				
				if old_pass == clients[username]['password']:
					clients[username]['password'] = new_pass
					conn.send('\nPassword successfully changed.\n')
				else:
					conn.send('\nOld password invalid.\n')

			if data == '8':
				clients[username]['online'] = False
				conn.send('\nLogout successful.\n')
				conn.close()
		
			conn.send('\n' + menu + '\n')
			conn.send('\nYou have {} unread messages.\n'.format(len(clients[username]['messages'])))
			conn.send('You have {} pending friend requests.\n'.format(len(clients[username]['friendrequest'])))
			conn.send('You have {} new posts on timeline.\n'.format(clients[username]['count']))

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

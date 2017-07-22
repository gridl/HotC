#
# HotC Server
# CTN2 Jackson
#

import socket


def _recv_data(conn):
    data = conn.recv(1024)
    command, _, arguments = data.partition(' ')
    return command, arguments


def game(conn):
    print 'success'


def login_loop(conn):
    while True:
        command, arguments = _recv_data(conn)

        if command == 'login':
            username, password = arguments.split()

            # check if username and password is correct
            with open('login.d', 'r') as f:
                logins = eval(f.read())
                for k, v in logins.items():
                    if (k == username) and (v == password):
                        conn.send('login_success')
                        return

            conn.send('login_failure')

        elif command == 'register':
            username, password = arguments.split()

            # check if username already registered
            with open('login.d', 'r') as f:
                logins = eval(f.read())
                for k, _ in logins.items():
                    if k == username:
                        conn.send('register_failure')
                        continue

            # register new user
            logins[username] = password
            with open('login.d', 'w') as f:
                f.write(str(logins))
            conn.send('register_success')


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 1337))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()

        login_loop(conn)
        game(conn)
        break


if __name__ == '__main__':
    main()

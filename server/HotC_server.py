#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# HotC Server
# https://github.com/vesche/HotC
#

import battle_server
import json
import socket
import sys
import threading
import time

from datetime import datetime


class Server(threading.Thread):
    host = '0.0.0.0'
    port = 1337
    clients = {}
    client_count = 1
    queue = []

    def __init__(self):
        super(Server, self).__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.listen(5)

    def listen(self):
        while True:
            conn, addr = self.s.accept()
            uid = self.client_count
            client = ClientConnection(conn, addr, uid)
            self.clients[uid] = client
            self.client_count += 1
            # spawn thread for each client connected
            threading.Thread(target = client.login).start()

    def get_clients(self):
        return [c for _, c in self.clients.items()]

    def remove_client(self, k):
        return self.clients.pop(k, None)


class ClientConnection():
    def __init__(self, conn, addr, uid):
        self.conn = conn
        self.addr = addr
        self.uid = uid
        self.status = '?'
        self.user = '?'
        self.opp = None
        self.hero_id = False
        self.move = False
        self.hp = 5

    def disconnect(self):
        server.remove_client(self.uid)
        self.log_message('disconnected')
        self.conn.close()

    def load_users(self):
        with open('users.json') as f:
            return json.load(f)

    def log_message(self, msg):
        dt = str(datetime.now())[:19]
        print '{} - {} {}.'.format(dt, self.user, msg)

    def recv_data(self):
        data = self.conn.recv(1024)
        command, _, arguments = data.partition(' ')
        return command, arguments

    def login(self):
        self.log_message('connected')

        logged_in = False
        users = self.load_users()

        while not logged_in:
            command, arguments = self.recv_data()

            if command == 'login':
                try:
                    username, password = arguments.split()
                except ValueError:
                    self.conn.send('login_failure')
                    continue

                # check if username and password are correct
                for u in users:
                    if (u['username'] == username) and (u['password'] == password):
                        logged_in = True
                        self.conn.send('login_success')
                        break
                else:
                    self.conn.send('login_failure')

            elif command == 'register':
                try:
                    username, password = arguments.split()
                except ValueError:
                    self.conn.send('register_failure')
                    continue

                # check if username already exists
                for u in users:
                    if u['username'] == username:
                        self.conn.send('register_failure')
                        break
                else:
                    # register a new user
                    new_user = { "username": username, "password": password,
                                 "wins": 0, "loses": 0 }
                    users.append(new_user)
                    with open('users.json', 'w') as f:
                        json.dump(users, f)
                    logged_in = True
                    self.conn.send('register_success')

            elif command == 'quit':
                self.disconnect()
                return

        # drop logged in user into lobby
        self.user = username
        self.log_message('logged in')
        self.status = 'lobby'
        self.lobby()

    def lobby(self):
        while True:
            command, _ = self.recv_data()

            if command == 'queue':
                self.log_message('entered the queue')

                # add client to the queue
                self.status = 'queue'
                my_client = server.clients[self.uid]
                server.queue.append(my_client)

                # sit in the queue
                while True:
                    try:
                        # ensure clients match up to each other properly
                        queue_index = server.queue.index(my_client)
                        if queue_index % 2 == 0:
                            opp_client = server.queue[queue_index+1]
                        elif queue_index % 2 == 1:
                            opp_client = server.queue[queue_index-1]
                        break
                    except IndexError:
                        # if no opponent found wait a bit and look again
                        time.sleep(.3)

                my_client.status = 'game'
                # wait for both of the clients to leave the queue
                time.sleep(1)

                # remove clients from queue
                try:
                    server.queue.remove(my_client)
                    server.queue.remove(opp_client)
                except ValueError:
                    pass

                # send client opponent info
                self.opp = opp_client.user
                self.conn.send('match {}'.format(self.opp))

                # start game
                players = (my_client, opp_client)
                self.game(players)

            elif command == 'who_online':
                clients_online = [(c.user, c.status) for c in server.get_clients()]
                self.conn.send(str(clients_online))

            elif command == 'highscores':
                users = self.load_users()
                stats = []
                for u in users:
                    stats.append([u['username'], u['wins'], u['loses']])
                self.conn.send(str(stats))

            elif command == 'quit':
                self.disconnect()
                return

    def game(self, players):
        self.log_message('started a game with {}'.format(players[1].user))

        # start battle server
        battle_server.run(players)

        # reset after match
        for p in players:
            p.status = 'lobby'
            p.opp = None

        self.log_message('finished a game with {}'.format(players[1].user))


if __name__ == '__main__':
    server = Server()
    server.setDaemon(True)
    print 'HotC server is listening on port 1337...\n'

    try:
        server.listen()
    except KeyboardInterrupt:
        print 'HotC server shutting down!'
        sys.exit(1)

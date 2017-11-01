# -*- coding: utf-8 -*-

#
# HotC Battle Server
# https://github.com/vesche/HotC
#

import json
import time


def run(players):
    my_client, opp_client = players

    # '1' - attack
    # '2' - defend
    # '3' - throw
    win_states = [ ('1', '3'), ('2', '1'), ('3', '2') ]
    win_status = 'null'

    while True:
        command, argument = my_client.recv_data()

        if command == 'hero':
            my_client.hero_id = argument

            # wait for opponent to select a hero
            while not opp_client.hero_id:
                time.sleep(1)

            # send client opponent hero name
            my_client.conn.send('hero {}'.format(opp_client.hero_id))

        elif command == 'battle':
            my_client.move = argument

            # wait for opponent to move
            while not opp_client.move:
                time.sleep(.3)

            # check if you lost hp in the round
            if (((my_client.move, opp_client.move) not in win_states) and
                (my_client.move != opp_client.move)):
                my_client.hp -= 1

            # wait for both clients to finish
            time.sleep(1)

            # check win state
            if my_client.hp == 0:
                win_status = 'lose'
            if opp_client.hp == 0:
                win_status = 'win'

            # send hp, opponent hp, opponent move, win status
            my_client.conn.send('{} {} {} {} {}'.format('update', my_client.hp,
                opp_client.hp, opp_client.move, win_status))

            # reset move for next turn
            time.sleep(.5) # wait a bit to do this probably
            my_client.move = False

            # break if someone won
            if win_status != 'null':
                break

    # reset data at end of battle
    my_client.hero_id = False
    my_client.hp = 5

    # update win/loss status in highscores
    users = my_client.load_users()
    for u in users:
        if u['username'] == my_client.user:
            if win_status == 'win':
                u['wins'] += 1
            elif win_status == 'lose':
                u['loses'] += 1
    with open('users.json', 'w') as f:
        json.dump(users, f)

    return

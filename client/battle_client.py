#
# HotC Battle Client
# https://github.com/vesche/HotC
#

import time

from HotC_client import clear_screen, recv_data
from hero_data import hero_dict, hero_moves


def run(sock, hero_name, opp_name):
    # get initial hero data
    hero, hero_id = hero_select()
    moves = hero_moves[hero]

    # send user hero selection
    sock.send('hero {}'.format(hero_id))

    # recv opponent hero selection
    _, opp_hero_id = recv_data(sock)
    opp_hero = hero_dict[opp_hero_id]
    opp_moves = hero_moves[opp_hero]

    # a few init vars
    hero_hp = opp_hero_hp = '5'
    hero_move = opp_hero_move = '0'
    win_status = 'null'

    # PLAYER VARIABLES
    # hero_name : 'newuser'
    # hero_id   : '2'
    # hero      : 'santa'
    # hero_hp   : 5
    # hero_move : '0'

    # OPPONENT VARIABLES
    # opp_name      : 'jackson'
    # opp_hero_id   : '1'
    # opp_hero      : 'batman'
    # opp_hero_hp   : 5
    # opp_hero_move : '0'

    ######################
    # main gameplay loop #
    ######################
    while True:
        # draw battle
        clear_screen()
        draw_battle(hero, hero_move, hero_name, hero_hp,
                    opp_hero, opp_hero_move, opp_name, opp_hero_hp)

        # print moves used
        if hero_move != '0':
            print '\n{} used {}! {} used {}!'.format(hero.title(),
                moves[int(hero_move)-1], opp_hero.title(),
                opp_moves[int(opp_hero_move)-1])

        # check for winner
        if win_status != 'null':
            raw_input('You {}! Press ENTER to return to the lobby!'.format(win_status))
            break

        # print possible moves
        print '\nChoose your move!'
        print '1. {} ({})'.format(moves[0], 'Attack')
        print '2. {} ({})'.format(moves[1], 'Block')
        print '3. {} ({})'.format(moves[2], 'Throw')

        # prompt for move to use
        while True:
            game_move = raw_input('> ')

            if game_move in ['1', '2', '3']:
                # send user move to server
                hero_move = game_move
                sock.send('battle {}'.format(game_move))
                print 'Waiting for opponent to move...'

                # recieve battle update and break loop
                command, argument = recv_data(sock)
                break
            else:
                print 'Invalid move!'

        # parse battle update information
        hero_hp, opp_hero_hp, opp_hero_move, win_status = argument.split()


def draw_battle(hero, hero_move, hero_name, hero_hp,
                opp_hero, opp_hero_move, opp_name, opp_hero_hp):
    # hero moves
    # '0' - standing
    # '1' - attack
    # '2' - defend
    # '3' - throw

    # load hero ascii art
    hero_left = get_hero(hero, hero_move)
    hero_right = get_hero(opp_hero, opp_hero_move)

    # flip right image (in a totally non-politically affiliated manner)
    new_right = []
    for line in hero_right:
        new_right.append(_fix_right(line[::-1]))
    hero_right = new_right

    # get max y dim and fix shorter hero to be as tall
    ll = len(hero_left)
    lr = len(hero_right)
    if ll > lr:
        draw_y = ll
        hero_right = ['']*(ll-lr) + hero_right
    elif lr > ll:
        draw_y = lr
        hero_left = ['']*(lr-ll) + hero_left
    else:
        draw_y = ll

    # get max x dim (will change depending on move)
    draw_x = max([len(i) for i in hero_left + hero_right])

    # draw title text and HP bars
    print 'HotC Battle! {} vs. {}'.format(hero_name, opp_name)
    print '{} HP: {:<5} ({}) - {} HP: {:<5} ({})\n'.format(hero.title(),
        int(hero_hp)*'#', hero_hp, opp_hero.title(), int(opp_hero_hp)*'#', opp_hero_hp)

    # draw battle
    for i in range(draw_y):
        print '{:{x}}{}{:>{x}}'.format(hero_left[i], ' '*5, hero_right[i], x=draw_x)


def _fix_right(s):
    cases = [('/','\\'), ('(',')'), ('{','}'), ('[',']'), ('<', '>')]
    for c in cases:
        s = s.replace(c[0], '%temp%').replace(c[1], c[0]).replace('%temp%', c[1])
    return s


def get_hero(hero, move_id):
    with open('heroes/{}-{}.txt'.format(hero, move_id)) as f:
        return f.read().splitlines()


def hero_select():
    print '\nChoose your hero!'

    for k in sorted(hero_dict):
        print '{}. {}'.format(k, hero_dict[k].title())

    while True:
        hero_choice = raw_input('> ')

        try:
            return hero_dict[hero_choice], hero_choice
        except KeyError:
            print 'Invalid choice.'

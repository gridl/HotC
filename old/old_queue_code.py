# sitting in the queue
while self.status != 'game':

    for opp_client in server.get_clients():
        # don't queue up with yourself
        if opp_client.user == self.user:
            continue

        # this is to make sure an opponent doesn't fuck itself
        # if it's checking the queue while a match is found
        if self.status == 'game':
            break

        # if other player in queue status, queue up with them
        if opp_client.status == 'queue':
            print opp_client.user, self.user
            # set both clients to game status, and set each other as opponents
            opp_client.status = 'game'
            opp_client.opp = self.user
            self.status = 'game'
            self.opp = opp_client.user

            # send message to clients about match
            opp_client.conn.send('match {}'.format(self.user))
            self.conn.send('match {}'.format(opp_client.user))
            break

    # wait 3 seconds to check for opponents again
    time.sleep(3)

# start up game after leaving queue (keep it to one)
match = sorted((self.user, self.opp))
players = (server.clients[self.uid], opp_client)

if match not in server.matches:
    server.matches.append(match)
    self.log_message("has started a game with {}".format(self.opp))
    self.game(players, match)

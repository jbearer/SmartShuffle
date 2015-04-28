from shared import *
from Account import Account
from SongPlayer import SongPlayer
import pyglet

if __name__ == '__main__':
	clearLog()

	user = raw_input('Username:')
	pword = raw_input('Password:')

	log('Logging in', console = True)
	account = Account(user, pword)
	assert(account.isAuthenticated())
	log('Login successful', console = True)
	log()

	player = SongPlayer(account)
	pyglet.app.run()

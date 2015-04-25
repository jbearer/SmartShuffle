from shared import *
from Account import Account
from SongPlayer import SongPlayer
import pyglet

if __name__ == '__main__':
	clearLog()

	log('Logging in', console = True)
	account = Account('jbearer95', 'j09211995')
	assert(account.isAuthenticated())
	log('Login successful', console = True)
	log()

	player = SongPlayer(account)
	pyglet.app.run()

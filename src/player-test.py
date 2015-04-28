from shared import *
from Account import Account
from SongPlayer import SongPlayer
import pyglet

if __name__ == '__main__':
	clearLog()

<<<<<<< HEAD
	user = raw_input('Username:')
	pword = raw_input('Password:')

	log('Logging in', console = True)
	account = Account(user, pword)
=======
	log('Logging in', console = True)
	account = Account('jbearer95', 'j09211995')
>>>>>>> master
	assert(account.isAuthenticated())
	log('Login successful', console = True)
	log()

	player = SongPlayer(account)
	pyglet.app.run()

from shared import *
from SongQueue import SongQueue
from controls import *


class SongPlayer(pyglet.window.Window):
	'''
	Class that manages a queue and other tasks associated
	with playing a list of songs. This will be the implementation
	for the visual interface

	Members:

	* _account: an instance of the api that is logged into the user's 
		Google Play account
	* _queue: the songs queued for playing

	* _curSong: a ManagedSoundPlayer that manages the currently playing song

	Controls (pyglet UI):
	* _btnQuit: a button that closes the window on click
	* _btnPlay: a button to play the current song
	* _btnRestart: a button to start the current song over
	* _btnNext: a button to skip to the start of the next song
	* _btnPrevious: a button to rewind to the start of the previous song
	* _controls: a list of all the controls attached to the window

	'''

	BUTTON_HEIGHT = 40
	BUTTON_WIDTH = 80
	LABEL_HEIGHT = 30
	LABEL_WIDTH = 100
	PADDING = 12

	def __init__(self, account, x = 50, y = 50, width = 500, height = 500):
		'''
		:param account: a valid, authenticated instance of the api
		'''

		assert(account.isAuthenticated())

		#set up the pyglet environment
		#super(SongPlayer, self).__init__(x = x, y = y,
		#								 width = width, height = height, 
		#								 resizable = True, caption = 'SmartShuffle')
		super(SongPlayer, self).__init__()
		
		self._btnRestart = TextButton(self)
		self._btnRestart.x = self.width / 2 - self.BUTTON_WIDTH / 2
		self._btnRestart.y = self.PADDING
		self._btnRestart.width = self.BUTTON_WIDTH
		self._btnRestart.height = self.BUTTON_HEIGHT
		self._btnRestart.text = ('Restart')
		self._btnRestart.on_press = self.restart

		self._btnPlayPause = TextButton(self)
		self._btnPlayPause.x = self.width / 2 - self.BUTTON_WIDTH / 2
		self._btnPlayPause.y = self._btnRestart.y + self._btnRestart.height \
							+ self.PADDING
		self._btnPlayPause.width = self.BUTTON_WIDTH
		self._btnPlayPause.height = self.BUTTON_HEIGHT
		self._btnPlayPause.text = ('Play')
		self._btnPlayPause.on_press = self.togglePlay

		self._btnNext = TextButton(self)
		self._btnNext.x = self._btnPlayPause.x + self.BUTTON_WIDTH + self.PADDING
		self._btnNext.y = self._btnPlayPause.y
		self._btnNext.width = self.BUTTON_WIDTH
		self._btnNext.height = self.BUTTON_HEIGHT
		self._btnNext.text = ('Next Song')
		self._btnNext.on_press = self.next

		self._btnPrevious = TextButton(self)
		self._btnPrevious.x = self._btnPlayPause.x - self.PADDING - self.BUTTON_WIDTH
		self._btnPrevious.y = self._btnPlayPause.y
		self._btnPrevious.width = self.BUTTON_WIDTH
		self._btnPrevious.height = self.BUTTON_HEIGHT
		self._btnPrevious.text = ('Previous Song')
		self._btnPrevious.on_press = self.previous

		self._btnQuit = TextButton(self)
		self._btnQuit.x = self.PADDING
		self._btnQuit.y = self.height - self.BUTTON_HEIGHT - self.PADDING
		self._btnQuit.width = self.BUTTON_WIDTH
		self._btnQuit.height = self.BUTTON_HEIGHT
		self._btnQuit.text = ('Exit')
		self._btnQuit.on_press = self.onQuit

		self._lblSongName = Label(self)
		self._lblSongName.x = self.width / 2 - self.LABEL_WIDTH / 2
		self._lblSongName.y = self.height / 2
		self._lblSongName.width = self.LABEL_WIDTH
		self._lblSongName.height = self.LABEL_HEIGHT
		self._lblSongName.text = ''

		self._lblArtist = Label(self)
		self._lblArtist.x = self._lblSongName.x
		self._lblArtist.y = self._lblSongName.y - self.LABEL_HEIGHT - self.PADDING
		self._lblArtist.width = self.LABEL_WIDTH
		self._lblArtist.height = self.LABEL_HEIGHT
		self._lblArtist.text = ''

		# Next and previous display either the appropriate text or "Buffering"

		self._lblNextSongName = Label(self)
		self._lblNextSongName.x = self._lblSongName.x + 3*self.LABEL_WIDTH + 2*self.PADDING
		self._lblNextSongName.y = self.height / 2
		self._lblNextSongName.width = self.LABEL_WIDTH
		self._lblNextSongName.height = self.LABEL_HEIGHT
		self._lblNextSongName.text = ''

		self._lblNextArtist = Label(self)
		self._lblNextArtist.x = self._lblNextSongName.x
		self._lblNextArtist.y = self._lblNextSongName.y - self.LABEL_HEIGHT - self.PADDING
		self._lblNextArtist.width = self.LABEL_WIDTH
		self._lblNextArtist.height = self.LABEL_HEIGHT
		self._lblNextArtist.text = ''

		self._lblPrevSongName = Label(self)
		self._lblPrevSongName.x = self._lblSongName.x - 2*self.LABEL_WIDTH - 2*self.PADDING
		self._lblPrevSongName.y = self.height / 2
		self._lblPrevSongName.width = self.LABEL_WIDTH
		self._lblPrevSongName.height = self.LABEL_HEIGHT
		self._lblPrevSongName.text = ''

		self._lblPrevArtist = Label(self)
		self._lblPrevArtist.x = self._lblPrevSongName.x
		self._lblPrevArtist.y = self._lblPrevSongName.y - self.LABEL_HEIGHT - self.PADDING
		self._lblPrevArtist.width = self.LABEL_WIDTH
		self._lblPrevArtist.height = self.LABEL_HEIGHT
		self._lblPrevArtist.text = ''


		self._controls = [self._btnQuit,
						  self._btnPlayPause,
						  self._btnNext,
						  self._btnPrevious,
						  self._lblSongName,
						  self._lblArtist,
						  self._btnRestart,
						  self._lblNextArtist,
						  self._lblNextSongName,
						  self._lblPrevArtist,
						  self._lblPrevSongName]

		#set up the google account
		self._account = account

		#For now, automatically load all songs from the library into the queue
		#TODO: options for loading a playlist, loading artists, albums, genres, and radio
		log('Loading library...', console = True)

		allSongs = account.getAllSongs()

		log('Done. ' + str(len(allSongs)) + ' songs detected.', console = True)
		log(console = True)

		self._queue = SongQueue(allSongs)

	def on_draw(self):
		'''
		Update the contents of the window
		'''
		self.clear()

		self.updateInfo()

		if self._queue.isPlaying():
			self._btnPlayPause.text = 'Pause'
		else:
			self._btnPlayPause.text = 'Play'

		for control in self._controls:
			control.draw()

	def updateInfo(self):
		'''
		Update the song information, album photo, etc
		'''
		songInfo = self._queue.getCurrentSongInfo()
		if songInfo:
			if self._lblSongName.text != songInfo['title']:
				self._lblSongName.text = songInfo['title']
			if self._lblSongName.text != songInfo['artist']:
				self._lblArtist.text = songInfo['artist']
		else:
			self._lblSongName.text = ''
			self._lblArtist.text = ''

	def on_close(self):
		
		self.onQuit()

	#########################################################
	#
	# Window control functions
	#
	#########################################################


	def onQuit(self):
		'''
		Do necessary cleanup and exit the window
		'''
		try:
			self._queue.close()
		except WindowsError:
			log('Unable to free queue buffering resources', console=True)

		print 'Logging out'
		if self._account.logout():
			log('Logout successful', console = True)
		else:
			log('Failed to logout!', console = True)

		self.close()

	def togglePlay(self):
		'''
		Play or pause the queue appropriately
		'''

		self._queue.togglePlay()

	def restart(self):
		'''
		Restart the current song from the beginning
		'''
		self._queue.playCurrent()

	def next(self):
		'''
		Play the next song
		'''
		self._queue.playNext()

	def previous(self):
		'''
		Play the previous song
		'''
		self._queue.playPrevious()

	def on_mouse_press(self, x, y, button, modifiers):
		for control in self._controls:
			if control.hit_test(x, y):
				control.on_mouse_press(x, y, button, modifiers)
				break

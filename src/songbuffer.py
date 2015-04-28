import shutil
import os
import pyglet
from shared import *

class SongBuffer:
	'''
	Class to handle the buffering of a song to prepare for playback. On update,
	writes its song to file along with associated files such as album art.

	Members:
		Public:
			* name: the buffer's debug log name

		Private:
			* _song: a song object
			* _filepath: a folder in which to write the buffer's data
			* _needsUpdate: flag to determine when to rewrite the data
			* _source: an avbin source for the song
	'''

	'''
	Filename constants
	'''
	AUDIO_FILE = 'audio.mp3'
	ALBUM_ART_FILE = 'album-art.bmp' #TODO: is this the right extension?

	def __init__(self, path, song = None, debugName = None):

		'''
		:param path: a directory to which the buffe will write its data
		:param song: the song to store. If song is None, nothing happens.
			If song is not None, the buffer will update at the next call to update
		:param debugName: the name of the buffer when it writes debug log
			messages. If debugName is None, the buffer will not write to the log
		'''

		self._song = song
		self._filepath = path
		self.name = debugName
		self._source = None
		if self._filepath[-1] != '/':
			# path must be a directory ending in a slash
			self._filepath += '/'

		# TODO: something seems to be broken here, the directory is not being created
		# causing IOError #2 when the song tries to write to the file
		osPath = os.path.dirname(self._filepath)
		if not os.path.exists(osPath):
			# make a new directory if needed
			os.makedirs(self._filepath)

		if song is None:
			# without a song, the buffer cannot be updated
			self._needsUpdate = False
		else:
			# update at the next call to update
			self._needsUpdate = True

	def close(self):
		'''
		Delete the directory created by the buffer. No need for it to persist,
		so deleting it saves space on the user's hard drive.
		'''

		shutil.rmtree(self._filepath)

	def getSource(self):
		return self._source

	def getFile(self, filename):
		'''
		Return a path to the given filename. Filename should be a valid SongBuffer
		filename constant
		'''

		return self._filepath + filename

	def setSong(self, song):
		if song != self._song:
			self._needsUpdate = True
			self._song = song

	def update(self):
		'''
		Write the buffer's contents to file. Overwrite existing files
		'''

		if self._needsUpdate:

			if self.name:
				log('Updating buffer ' + self.name)

			self._song.writeAudioToFile(self.getFile(self.AUDIO_FILE))
			self._source = pyglet.media.load(self.getFile(self.AUDIO_FILE), streaming = False)

			# TODO: album art

			self._needsUpdate = False

			if self.name:
				log('Finished updating buffer ' + self.name)

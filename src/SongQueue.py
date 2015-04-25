from shared import *
from songbuffer import SongBuffer
import threading

class SongQueue:
	'''
	Class to handle the playing of a list of songs.
	Warning: writes memory to disc. Must call close on exit to destroy
	memory.

	Members:
		Private:
			*_songsD: a dictionary mapping song titles to Song objects for all
				songs in the queue

			*_songs: a list of the songs in the queue in the order in which they are to be played
				the next song to be played is at the back of songs

			* _history: an ordered list of the songs which have been played(). The current song is 
				at the back of history

			* _currentBuffer: a SongBuffer containing the currently playing song

			* _nextBuffer: a SongBuffer containing the next song in the queue

			* _prevBuffer: a SongBuffer containing the previously played song

			* _curSong: a managed sound player for the currently playing song

			* _curBufThread: a thread object that updates _currentBuffer

			* _nextBufThread: updates _nextBuffer

			* _prevBufThread: updates _prevBuffer

			#TODO: look into using 3.x, in which _songs.keys() would be O(1)
				instead of O(n) in 2.x. This will be useful for shuffling, when
				we lose the benefit of constant time lookup for a known song.
	'''

	FORWARD = True
	BACKWARD = False

	def __init__(self, songs):
		'''
		Create a queue set up to play the given songs

		:param songs: a dictionary of title:Song pairs
		'''	
		self._songsD = songs
		self._songs = songs.keys()

		log(self._songs[-1:10])

		self._history = []
		self._currentBuffer = SongBuffer('buffer1', song=self._songsD[self._songs[-1]], debugName = 'CURRENT')
		self._nextBuffer = SongBuffer('buffer2', song = self._songsD[self._songs[-2]], debugName = 'NEXT')

		# Since no songs have been played yet, prevBuffer's song is undefined
		self._prevBuffer = SongBuffer('buffer3', debugName = 'PREVIOUS')

		self._curBufThread = BufferThread(self._currentBuffer)
		self._nextBufThread = BufferThread(self._nextBuffer)
		self._curBufThread.start()
		self._nextBufThread.start()

		self._prevBufThread = None

		self._curSong = None #Allows us to tell if the queue has been started or not
		self._source = None

	def numSongs(self):
		return len(self._songs)

	def getCurrentSongInfo(self):
		'''
		Return a dictionary with information about the currently playing song
		'''
		if self._history:
			return self._songsD[self._history[-1]].data
		else:
			return None

	def isPlaying(self):
		'''
		Determine whether playback is currently happening
		'''

		if self._curSong:
			return self._curSong.playing
		else:
			return None

	def togglePlay(self):
		'''
		Resume or begin playback if not playing. Pause if playing.
		'''
		if self._curSong is None:
			# begin playback of the queue

			# get the first song from the queue and add it to history
			song = self._songs.pop(-1)
			self._history.append(song)

			self.playCurrent()

		elif not self._curSong.playing:
			#the song is paused
			self._curSong.play()
		else:
			#the song is playing
			self._curSong.pause()

	def playNext(self):
		'''
		Skips to the beginning of the next song in the queue and fixes buffers.
		'''

		if self._songs:

			# get the next song from the queue and add it to history
			song = self._songs.pop(-1)
			self._history.append(song)

			self.exchangeBuffers(self.FORWARD)

			# for a forward step, currentBuffer and prevBuffer will be OK
			# nextBuffer needs to be reloaded
			if self._songs:
				#there is a next song, so write it to the buffer
				self._nextBuffer.setSong(self._songsD[self._songs[-1]])

			self.playCurrent()


	def playPrevious(self):
		'''
		Rewind to the song that was played before the current song and fix buffers.
		if no such song exists in history, do nothing and return False.
		'''
		if len(self._history) >= 2:
			#History must contain the current song and a previous song
			
			#get the currently playing song name from history, and put it back on the queue
			self._songs.append(self._history.pop(-1))

			self.exchangeBuffers(self.BACKWARD)

			# for a backward step, currentBuffer and nextBuffer will be OK
			# prevBuffer needs to be reloaded
			if len(self._history) > 1:
				# there is a previous song, write it to the buffer
				self._prevBuffer.setSong(self._songsD[self._history[-2]])

			self.playCurrent()

	def playCurrent(self):
		'''
		Start the current song from the beginning. Buffers do not change.
		:pre All three buffers are correct
		'''

		# stop playback
		if self._curSong and self._curSong.playing:
			self._curSong.pause()

		# if currentBuffer is still updating, wait for it to finish
		# unlike prevBuffer and nextBuffer, currentBuffer MUST be
		# up-to-date for a song to be played
		log('waiting for thread: CURRENT')
		self._curBufThread.join()
		log('proceeding')

		# start the new song
		log('playing song: ' + self._songs[-1])
		self._curSong = self._currentBuffer.getSource().play()
		self._curSong.on_eos = self.playNext

		# while the song is playing, update the other buffers
		self.updateBuffers()

	def playSong(self, songName):
		###############################################################
		# This method can be implemented several ways:
		# 1. Search through the list for the song. Play it and refresh
		#	buffers. Theta(n). Preserves order of queue. Also, if 
		#	searching through queue, no need to have a dictionary.
		#
		# 2. Reshuffle. Append song to beginning of shuffled queue and
		#	start the queue from the beginning. Complexity depends on
		#	shuffling algorithm
		#
		# 3. Pause playback of the queue. Play song. Resume playback.
		#	Theta(1). Preserves order of queue. However, since buffers
		#	are not changed, the user cannot "jump ahead" in the queue
		###############################################################
		'''
		Play the given song. Returns True if the song was able to be played,
		false otherwise.

		:param songName: the title of the song to be played
		

		# DEBUG
		self._songsD[songName].writeAudioToFile('test.txt')
		self._songsD[songName].writeAudioToFile('test.mp3')
		# END DEBUG


		if self._curSong is not None and self._curSong.playing:
			self._curSong.pause()

		if songName in self._songsD:
			song = self._songsD[songName]
			self._curSong = song.play()
			return True
		else:
			return False

		'''

	def exchangeBuffers(self, forward):
		'''
		Executed when stepping to another song. Exchanges the
		buffer files so that the current song is ready to be played,
		either the prev or next buffer corresponds to the proper song,
		and the other is ready to be filled.

		:param forward: A boolean value that is true if stepping to the
			next song, False if stepping to the previous song
		'''

		if forward:
			# step forward:
			# currentBuffer becomes prevBuffer
			# nextBuffer becomes currentBuffer
			# prevBuffer becomes nextBuffer, and is ready to be loaded
			oldPrev = self._prevBuffer
			self._prevBuffer = self._currentBuffer
			self._currentBuffer = self._nextBuffer
			self._nextBuffer = oldPrev

		else:
			# step backward:
			# currentBuffer becomes nextBuffer
			# prevBuffer becomes currentBuffer
			# nextBuffer becomes prevBuffer, and is ready to be loaded
			oldNext = self._nextBuffer
			self._nextBuffer = self._currentBuffer
			self._currentBuffer = self._prevBuffer
			self._prevBuffer = oldNext

		self._nextBuffer.name = 'NEXT'
		self._currentBuffer.name = 'CURRENT'
		self._prevBuffer.name = 'PREVIOUS'

	def updateBuffers(self):
		self._curBufThread = BufferThread(self._currentBuffer)
		self._nextBufThread = BufferThread(self._nextBuffer)
		self._prevBufThread = BufferThread(self._prevBuffer)

		self._curBufThread.start()
		self._nextBufThread.start()
		self._prevBufThread.start()

	def close(self):
		'''
		Clean up resources
		'''

		# delete the buffers
		self._prevBuffer.close()
		self._currentBuffer.close()
		self._nextBuffer.close()


class BufferThread(threading.Thread):
	'''
	Updates a songbuffer 
	TODO: can be interrupted (eg when the user skips several songs quickly)
	'''

	def __init__(self, buffer):
		'''
		:param buffer: the buffer to update
		'''
		super(BufferThread, self).__init__()
		self._buffer = buffer

	def run(self):
		log('Starting buffer thread: ' + self._buffer.name)
		self._buffer.update()
		log('Returning from buffer thread: ' + self._buffer.name)

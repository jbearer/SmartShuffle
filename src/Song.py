from shared import *
import urllib3
import certifi

class Song:
	'''
	A class representing a song

	TODO: implement function to write album art to file

	Members:
		Public:
			* data: the dictionary representing the song


			*play(): begin playback of the song
			*pause(): pause playback
			*duration(): the length of the song in milliseconds
			*title()
			*artist()
			*album()
			*rating(): the rating(thumbs up, thumbs down, or none)
			*lastPlayed()
			*bpm()

		Private:
			*streamUrl(): returns a playableURL for the song

			*id(): returns the Google id code for the song

			*_account: the account which owns the song
	'''

	def __init__(self, data, account):
		'''
		Constructor for a song with the given information
		:param data: a dictionary representing the song
		:param account: the account to which the song belongs
		'''
		self.data = data
		self._account = account
		self._song = None
		self._exitFlag = False

	def title(self):
		return self.data['title']

	def id(self):
		'''
		Returns the song id, which can be used to get URLs for the song
		'''

		#try to find the id in the song dictionary
		if 'id' in self.data:
			return self.data['id'].encode('utf-8')
		elif 'nid' in self.data:
			# all access ids are stored as 'nid'
			return self.data['nid'].encode('utf-8')

		#the lengths of each segment separated by a '-' in a song id
		#IDFORMAT = [8,4,4,4,12]

		#the actual key for the id data varies, sometimes it is something like
		#nid or storeid, so we search for anything containing 'id' with the
		#proper format
		#for key in self.data:
		#	if 'id' in key:
		#		format = string.split(self.data[key], '-')
		#		if [len(subString) for subString in format] == IDFORMAT:
		#			return self.data[key].encode('utf-8')

		#assert(False) #fail if we don't find an id
		#return

	def streamUrl(self):
		'''
		Returns a playable URL for the song

		:param urlL: a list of URLs
		'''
		return self._account.getStreamUrl(self.id())

	def abortThreads(self):
		'''
		Stop any operations currently being processed
		'''
		self._exitFlag = True

	def writeAudioToFile(self, filename):
		'''
		Write the audio to the given file. Should overwrite if the file
		exists
		'''
		http = urllib3.PoolManager(
		    cert_reqs='CERT_REQUIRED', # Force certificate check.
		    ca_certs=certifi.where()  # Path to the Certifi bundle.
		)

		response = None
		try:
			log('getting stream url: song ' + self.data['title'])
			url = self.streamUrl()
			log('obtained stream url: song ' + self.data['title'])
			log('getting audio data: song ' + self.data['title'])

			# TODO: this is where the call spends the vast majority of its time
			# get the data in chunks and have the song check a flag each time so
			# that the streaming can be interrupted when necessary
			response = http.request('GET', url)
			log('obtained audio data: song ' + self.data['title'])

		except urllib3.exceptions.SSLError as e:
			log('SSL Error:', console=True)
			log(e, console=True)

		try:
			f = open(filename, 'wb')
			log('writing audio data: song ' + self.data['title'])
			f.write(response.data)
			log('wrote audio data: song ' + self.data['title'])
			f.close()
		except IOError as e:
			log('IOERROR: Unable to open file in Song ' + self.data['title'], console = True)
			log('\tFile: ' + filename, console = True)
			log('\t' + str(e), console = True)
			log('\tTraceback: song.Song.writeAudioToFile(' + filename + ')')

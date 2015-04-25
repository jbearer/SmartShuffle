from gmusicapi import Mobileclient
from gmusicapi import Webclient
import re
from Song import Song

class Account:
	'''
	As of 4/13/2015, the gmusicapi is missing key functionality in its Webclient
	and Mobileclient. Performing many basic operations requires a logged-in
	instance of eac. To simplify the interface with the rest of the program,
	I wrap the functionality of both interfaces in this Account class.

	Members:
		Private:
			*_mobile: an instance of Mobileclient that is logged into the user's 
				Google Play account
			*_web: an instance of Webclient that is logged into the user's 
				Google Play account	
			*_authenticated: a boolean for whether or not the account is
				succesfully logged in
	'''

	def __init__(self):
		'''
		Default constructor. Initializes _mobile and _web but does not log in.
		'''

		self._mobile = Mobileclient()
		self._web = Webclient()
		self._authenticated = False

	def __init__(self, username, password):
		'''
		Initializes _mobile and _web and attempts to log in with the given
		credentials. If login fails, isAuthenticated() will return False

		:param username: The username of the account
		:param password: The password corresponding to the username
		'''

		self._mobile = Mobileclient()
		self._web = Webclient()
		self._authenticated = False
		self.login(username, password)

	def login(self, username, password):
		'''
		Attempts to log in with the given credentials. If login fails,
		_authenticated is set to False, either _mobile or _web, or both,
		will be None, depending on which login attempts fail, and the function
		will return False. If login succeeds, _authenticated will be set to True
		and the funtion will return True.

		:param username: The username of the account
		:param password: The password corresponding to the username
		'''

		webSuccess = self._web.login(username, password)
		if not webSuccess:
			self._web = None

		mobileSuccess = self._mobile.login(username, password)
		if not mobileSuccess:
			self._mobile = None

		self._authenticated = webSuccess and mobileSuccess
		return self._authenticated

	def isAuthenticated(self):
		'''
		Returns true if the account is properly logged in. Else returns false.
		'''

		return self._authenticated

	def logout(self):
		'''
		Logs out both _web and _mobile and sets _authenticated to False.
		Returns True for success and False for failure.
		'''

		webSuccess = self._web.logout()
		mobileSuccess = self._mobile.logout()

		#if either of the interfacs is logged out, we are not authenticated
		self._authenticated = not(webSuccess or mobileSuccess)

		#the operation was not successful unless both are logged out
		return webSuccess and mobileSuccess

	def registeredDevices(self):
		'''
		Returns a list of devices registered to the account.
		'''
		return self._web.get_registered_devices()

	def validMobileDeviceID(self):
		'''
		Trying to get a stream URL from a desktop or laptop causes a 403 error.
		This function returns a mobile device from which it is possible to
		obtain a URL. If no such devices is regesterd to the account, returns
		None.
		'''

		#Each element should be a RegEx to match a particular valid format.
		#Each element should have one subgroup, corresponding to the part of the
		#format to use as the device ID. For example, Android IDs drop the '0x'
		#at the beginning, so the rest of the format is subgrouped.
		DEVICE_FORMATS = [re.compile(r"0x(.{16})")] #TODO: add more formats

		devices = self.registeredDevices()
		for device in devices:
			for format in DEVICE_FORMATS:
				match = re.match(format, device['id'])
				if match:
					return match.group(1)

		return None

	def getAllSongs(self):
		'''
		Return a dictionary of title:Song pairs for each song in the library.
		'''

		ret = {}
		allSongs = self._mobile.get_all_songs()
		for song in allSongs:
			if song['title'] not in ret:
				ret[song['title']] = Song(song, self)

		return ret

	def getStreamUrl(self, songID, deviceID = None):
		'''
		Return a  playable URL corresponding to the given song

		Note: Due to the current (4/22/15) implementation of the
		gmusic api, makes an unverified https request causing a
		urllib3 InsecureRequestWarning. This is a known issue with
		the API (issues #28 and #313) and does not pose a security
		risk.
		'''

		if deviceID is None:
			deviceID = self.validMobileDeviceID()
		try:
			#the unverified request happens here
			import urllib3
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
			url = self._mobile.get_stream_url(songID, deviceID)

			return url

		except RuntimeError as e:
			log('Exception in getStreamUrl: ')
			log( e)
			return None

	def __del__(self):
		'''
		Logout of the connection before closing the account
		'''

		self.logout()

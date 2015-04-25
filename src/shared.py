import time

OUTPUT_FILE = 'output.txt'

def log(message = None, console = False):
	'''
	print a message with a timestamp to output.txt

	:param message: the message to write. If absent, a newline is printed

	:param console: indicates whether the message should be written to the
	console in addition to the file. This allows output.txt to accumulate a
	complete record of the run, while only information directed to the user
	is printed to the console.
	'''

	f = open(OUTPUT_FILE, 'a')
	if message:
		timeStamp = time.ctime(time.time())	
		f.write(timeStamp + ' ' + str(message) + '\n')

		if console:
			print message
	else:
		f.write('\n')
		print

	f.close()

def clearLog():
	'''
	Erase the contents of the log
	'''
	f = open(OUTPUT_FILE, 'w')
	f.write('')
	f.close()


VERB = 0

def setVerbosity(verbose):
	global VERB
	VERB = int(verbose)
	printV(2, "Verbosity = ", VERB)

def printV(level, *args):
	if VERB >= level:
		for i in args:
			print i
		print ''


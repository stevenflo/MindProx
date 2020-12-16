#!/usr/bin/python

# Copyright (c) 2019 The University of Texas at Austin. 
#     All rights reserved.
 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
 
#       http://www.apache.org/licenses/LICENSE-2.0
 
#   Unless required by applicable law or agreed to in writing,
#   software distributed under the License is distributed on an "AS
#   IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied.  See the License for the specific language
#   governing permissions and limitations under the License.
 
#  For more about this software visit:
 
#       http://lca.ece.utexas.edu
import argparse		# actively maintained successor to optparse
import json
import copy
import sys
import os
import subprocess




###Helper Functions###
VERB = 0

def printv(level, *args):
	if VERB >= level:
		for i in args:
			print i,
		print ''


def setVerbosity(verbose):
	global VERB
	VERB = int(verbose)
	printv(2, "Verbosity = ", VERB)


def parseCommandLine():
	"""We parse the command line to fill in the options and set the verbosity
	
	    Args:
	No arguments are needed, automatically parses the command line
	
	    Returns:
	options: a collection of command line parameters, mainly JSON config file,
	desired output file, and level of verbosity
	
	"""

	parser = argparse.ArgumentParser(description="Generate a collection of JSONS based on PinBalls")
	parser.add_argument("-i", "--Pinballs", dest="Pinballs", metavar="FILE", required=True, help="Directory containing the pinballs to be profiled")
	parser.add_argument("-o", "--OutDir", dest="outDir", metavar="FILE", required=True, help="Output Directory for profiles, multiple subdirectories will be created for each Pinballs")
	parser.add_argument("-v", "--verbose", metavar="N", type=int, dest="Verb", default=0, help="level of debug information printed out (0-3)")
	args = parser.parse_args()
        setVerbosity(args.Verb)
	return args


##File parsing functions
def getBaseNames(loc):
        """"This function returns all pinball basenames present in a directory

        Args: 
            loc--directory containing pinballs
        Returns:
            base_names--a list of files present in the directory
        """
        files = os.listdir(loc)
        printv(3, files)
        base_names = []
        for f in files:
                while f[-1:] != '0' and len(f) > 10:
                        printv(3,"Last Character",f[-1:])
                        f = os.path.splitext(f)[0]
                        printv(3, f)
                if f not in base_names:
                        printv(2, "Basename found", f)
                        base_names.append(f)
        printv(2, "Pinball Basenames to be profiled")
        for b in base_names:
                printv(2, b)
        return base_names

def makeOutputDirs(loc, names):
        """
        This function creates a bunch of directories in loc based on the names
        ARG:
            loc: path to directory to output results into
            names: a collection of pinball names that will be parsed to create directory names
        Returns:
            idents: dictionary mapping base names to associated output directory
        """
        idents = {}
        for n in names:
                ident = n.split('_')
                for e in ident:
                        printv(3, e)
                if len(ident) > 3:
                        printv(3, "identity for basename is",ident[2])
                        if os.path.exists(loc+ident[2]):
                                printv(3, "Output Directory for", ident[2], "already exists")
                        else:
                                printv(2, "Creating output directory", ident[2])
                                os.makedirs(loc+ident[2])
                        idents[n] = ident[2]

                else:
                        printv(1, "Ignoring invalid basename:",n)
        return idents
        

def profilePinballs(Pinballs_dir, idents, outDir):
        """
        Runs profiling on all pinballs present in idents and outputs profiles into associated output directory
        """
        base_command="./mkJSON_both_pinballs.sh "
        for Basename in idents:
                command = base_command + Pinballs_dir + Basename + " " + outDir + idents[Basename] + " " + idents[Basename]
                command = command + " > " + outDir + idents[Basename] + "/profiling.out"
                printv(2, "Running Command:",command)
                os.system(command)
                #status = subprocess.Popen([command],shell=True, close_fds=True) attempt at parralel 
        status.wait()
        printv(1, "profiling of at least one pinball finished") 
        printv(2, "Consider waiting and double checking that all runs have finished")
                


if __name__== "__main__":
	options = parseCommandLine()
        printv(3, "Hello World")
        printv(3, "Input Directory:", options.Pinballs)
        printv(3, "Output Directory:", options.outDir)
        if os.path.exists(options.outDir):
                printv(2, "Output Directory already exists")
        else:
                printv(2, "Creating output directory")
                os.makedirs(options.outDir)
        ##Reading in the pinballs
        base_names = getBaseNames(options.Pinballs)
        ##Making the directories
        idents = makeOutputDirs(options.outDir, base_names)
        ##Profiling all pinballs
        profilePinballs(options.Pinballs, idents, options.outDir)

#!/usr/bin/python3

import os
import re
import sys

###########
# LOGGERS #
###########

# Date formatting will be the same for all loggers
import logging
dateformatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s')

# Make formatNotesLogger logger object.
formatNotesLogger = logging.getLogger("FORMATNOTES")
formatNotesLogger.setLevel(logging.DEBUG)
formatNotesFileH = logging.FileHandler('/tmp/formatNotes.log')
formatNotesFileH.setLevel(logging.DEBUG)
formatNotesConsoleH = logging.StreamHandler()
formatNotesConsoleH.setLevel(logging.WARNING)
formatNotesFileH.setFormatter(dateformatter)
formatNotesConsoleH.setFormatter(dateformatter)
formatNotesLogger.addHandler(formatNotesFileH)  # File Handler add
formatNotesLogger.addHandler(formatNotesConsoleH)  # Console Handler add

def getSetNumber(setName):
    """
    Remember this returns a string, not an integer
    """
    formatNotesLogger.info("getSetNumber: Retrieving Set Number")
    try:
        setNumSearch = re.search(".*([\d]+)$", setName)
        if setNumSearch is not None:
            setNum = str(setNumSearch.group(1))
            formatNotesLogger.debug("getSetNumber: Set Number is '%s'", setNum)
            return setNum
        else:
            formatNotesLogger.warning("getSetNumber: Set Name is not in correct format")
            return "0"
    except:
        formatNotesLogger.warning("getSetNumber: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                  str(sys.exc_info()[1])))

#####################
# CLASS DEFINITIONS #
#####################

class FormatNotes():
    """
    This class is used to put together a set of notes for one batch set
    into a single post, inserting the stepartist name for each judge.

    * CLASS ATTRIBUTES *
    - path: Full file path to the set.
    - setName: Name of the set folder.
    - setNumber: The Set Number of the Batch Group. Note this is a string.
    - setPostFile: Output file of formatted forum post.
    """

    def __init__(self, notesDir):
        """
        Constructor
        """
        self.path = notesDir
        self.setDirs = os.listdir(self.path) # Gives a list of the set folders containing notes
        self.setPostFile = "forum_post.txt"
        self.setNums = [] # List storing numbers of the sets as strings, not integers.
        self.setInfo = {} # Dictionary storing set numbers and judge lists for each set

    def getJudgeName(self, notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Format.txt
        File must be in format of <JudgeName>_Format -- anything else can come after
        """
        formatNotesLogger.info("getJudgeName: Retrieving Judge Name from Notes File '%s'", notesFileName)
        try:
            judgeParse = re.search("^(.*)_Format", notesFileName)
            if judgeParse is not None:
                judgeName = str(judgeParse.group(1))
                formatNotesLogger.info("getJudgeName: Judge is '%s'", judgeName)
                return judgeName     
            else:
                formatNotesLogger.warning("getJudgeName: Judge Notes File is not in correct format")
                return "Judge"
        except:
            formatNotesLogger.warning("getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def getSetJudgeInfo(self):
        """
        Goes through the set folders, parses set number from folder name,
        and then gets the judge name for each notes text file in those folders.
        So basically for each set directory get set number and judges for those sets.
        Set folders should be in the form of set<number>, so e.g. set1 set2
        """
        formatNotesLogger.info("getSetJudgeInfo: Getting Set and Judge Info")
        try:
            for setDir in self.setDirs:

                # Retrieve set number from the set folder directory.
                setNumber = getSetNumber(setDir) # Retrieve set number from folder name
                self.setNums.append(setNumber) # Add the set number to the list of set numbers.

                # Change working directory to this set folder.
                fullSetDir = os.path.join(self.path, setDir)
                os.chdir(fullSetDir) # Go into the set folder

                # List all the judge notes file in the set directory, then get judges from text files.
                notesFiles = os.listdir(fullSetDir)
                setJudgeList = []
                for notesFile in notesFiles:
                    judge = self.getJudgeName(notesFile)
                    setJudgeList.append(judge) # Add judge to the set's judge list
                self.setInfo[setNumber] = setJudgeList # Make the set number entry to this judge list
        except:
            formatNotesLogger.warning("getSetJudgeInfo: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    def makeFormattedPost(self):
        """
        Puts the outline at the top of the post of the set numbers and judges, then
        appends the judge notes for each set. The Batch (e.g. July/August) will be put
        manually after the .txt file from this script is generated to prevent convoluted code.
        """
        formatNotesLogger.info("makeFormattedPost: Attempting to create formatted post.")
        try:
            os.chdir(self.path)
            with open(self.setPostFile, 'w') as post:

                # Write the top outline of the post. This also includes the order of the judges.
                alphabet = "abcdefghijklmnopqrstuvwxyz"
                setCounter = 1 # Sets will be listed with numbers
                for setNum in self.setNums:
                    judgeCounter = 0 # Judges will be listed with alphabet indices
                    judgesInSet = self.setInfo[setNum]
                    post.write("[b][size=4]{0}.) SET {1}[/size][/b]\n".format(setCounter,setNum))
                    for judge in judgesInSet:
                        letterForList = alphabet[judgeCounter]
                        post.write("[b]{0}.) {1}[/b]\n".format(letterForList,judge))
                        judgeCounter += 1
                    setCounter += 1
                post.write("\n") # This deals with spacing in the first Set posted.

                # Now time to write the sets and the notes for them.
                setDirCounter = 0 # For use in determining set directory to change to.
                for setNum in self.setNums:

                    # Change working directory to this set folder.
                    fullSetDir = os.path.join(self.path, self.setDirs[setDirCounter])
                    os.chdir(fullSetDir) # Go into the set folder
                    notesFiles = os.listdir(fullSetDir) # List all judge notes files in set.

                    # Write judge notes info
                    post.write("[b][size=7]SET {0}[/size][/b]".format(setNum))
                    judgeList = self.setInfo[setNum] # Retrieve judge list for the set
                    judgeCounter = 0 # For use in determining judge notes file to use
                    for judge in judgeList:
                        post.write("\n\n[b][size=4]=== JUDGE: {0} ===[/size][/b]\n".format(judge))
                        fileToOpen = notesFiles[judgeCounter]
                        with open(fileToOpen) as judgeFile:
                            for line in judgeFile:
                                line = line.strip()
                                songLine = re.search("^\[.*\].*\{.*\}[\s]*\(.*\)$", line)
                                if songLine is not None:
                                    lineToFormat = songLine.group(0)
                                    formattedLine = "[b]" + lineToFormat + "[/b]" 
                                    post.write("\n"+formattedLine)
                                else:
                                    post.write("\n"+line)
                        judgeFile.close()
                        judgeCounter += 1
                    setDirCounter += 1
                        
            post.close()
            formatNotesLogger.info("printFormattedPost: Successfully wrote '%s'", self.setPostFile)
        except:
            formatNotesLogger.warning("makeFormattedPost: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1])))
            formatNotesLogger.warning("Are you sure the directory only has the set folders with "
                                      "the notes files?")


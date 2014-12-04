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
        self.setName = str(os.path.basename(os.path.normpath(self.path)).strip())
        self.setNumber = getSetNumber(self.setName)
        self.setPostFile = "post_set" + self.setNumber + ".txt"
        self.notesFiles = os.listdir(self.path)

    def getJudgeName(self, notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_FormatTest.txt
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

    def makeFormattedPost(self):
        formatNotesLogger.info("printFormattedPost: Attempting to create formatted post.")
        try:
            os.chdir(self.path)
            with open(self.setPostFile, 'w') as post:

                # Write the top of the post. This also includes the order of the judges.
                post.write("[b][size=7]SET {0}[/size][/b]\n".format(self.setNumber))
                counter = 1 # For order of the judges
                for notesFile in self.notesFiles:
                    judge = self.getJudgeName(notesFile)
                    post.write("\n[b]{0}.) {1}[/b]".format(counter,judge))
                    counter += 1
                post.write("\n")

                # Write out notes for each judge in the set.
                for notesFile in self.notesFiles:
                    judge = self.getJudgeName(notesFile)
                    post.write("\n[b][size=4]=== JUDGE: {0} ===[/size][/b]\n".format(judge))
                    with open(notesFile) as judgeFile:
                        for line in judgeFile:
                            line = line.strip()
                            songLine = re.search("^\[.*\].*\{.*\}[\s]*\(.*\)$", line)
                            if songLine is not None:
                                lineToFormat = songLine.group(0)
                                formattedLine = "[b]" + lineToFormat + "[/b]" 
                                post.write("\n"+formattedLine)
                            else:
                                post.write("\n"+line)
                        post.write("\n\n")
                    judgeFile.close()
            post.close()
            formatNotesLogger.info("printFormattedPost: Successfully wrote '%s'", self.setPostFile)
        except:
            formatNotesLogger.warning("makeFormattedPost: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1])))


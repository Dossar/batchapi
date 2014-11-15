#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import re
import sys

# NOTE: I'm able to parse the line info with the song title and rating.

# CLASS DEFINITION
class JudgeNotes(object):
    """
    * CLASS ATTRIBUTES *
    - path: Full file path to the judge notes file.
    - notesFile: Name of the judge notes file itself.
    - fileDir: Directory of the judge notes file.
    - average: Average Rating of the Judge.

    * FUNCTIONS *
    - dumpInfo():
    """

    def __init__(self, judgeNotesFile):
        """
        Constructor
        """
        self.path = judgeNotesFile
        self.notesFile = os.path.basename(os.path.normpath(judgeNotesFile))
        self.fileDir = os.path.abspath(os.path.join(os.path.dirname( self.path ), '.'))
        self.average = 0

    def dumpInfo(self):
        print(logMsg("JUDGENOTES","INFO"),"dumpInfo: Dumping Judge Notes Info")
        print("- JUDGE NOTES FILE PATH:", self.path,
              "\n- JUDGE NOTES FILE:", self.notesFile,
              "\n- JUDGE NOTES FILE DIR:", self.fileDir,
              "\n- JUDGE AVERAGE:", self.average)

    def getJudgeRatings(self):
        """
        Looks through the file user specified for what judge gave.
        """
        print(logMsg("JUDGENOTES","INFO"),"getJudgeRatings: Parsing Judge Notes File")
        try:
            os.chdir(self.fileDir) # Change to batch directory context
            with open(self.notesFile) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        self.saveSongRating(line)
            judgeFile.close()
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def saveSongRating(self,ratingLine):
        """
        ratingLine is the line with the rating and song information in judge notes.
        Format: [Rating] Song Name {Song Artist} (Stepper)
                [Rating] Song Name {Song Artist}
        Example: [7.5/10] Moonearth {DJ Sharpnel} (Tyler)
                 [6/10] valedict {void}
        """

        #ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\((.*)\)$",ratingLine)
        #ratingNoStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)",ratingLine)
        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)
        ratingNoStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}$",ratingLine)
        try:
            if ratingStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating: Found rating with stepartist")
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingStepartist.group(0)) # Full match
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingStepartist.group(1)) # Rating number itself
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingStepartist.group(2).strip()) # Song Title
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingStepartist.group(3).strip()) # Song Artist
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingStepartist.group(4).strip()) # Stepartist
            elif ratingNoStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating: Found rating without stepartist")
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingNoStepartist.group(0)) # Full Match
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingNoStepartist.group(1)) # Rating number itself
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingNoStepartist.group(2).strip()) # Song Title
                print(logMsg("JUDGENOTES","INFO"),"saveSongRating:",ratingNoStepartist.group(3).strip()) # Song Artist
        except:
            print(logMsg("JUDGENOTES","ERROR"), "saveSongRating: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    
        

# use suites\judgenotes\janTest.txt
# 4/10 - 1
# 5/10 - 2
# 6/10 - 2
# 6.5/10 - 1
# 7.5/10 - 1
# 8/10 - 1
# MAIN
if __name__ == "__main__":

    judgeNotesFilePath = input("Input full path of Judge Notes File: ")
    judge = JudgeNotes(judgeNotesFilePath)
    judge.dumpInfo()
    judge.getJudgeRatings()

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
    - judgedSongList: The titles of all the songs judged in notes file.
                      ([TITLE,ARTIST,STEPARTIST],rating)
    - numJudgedFiles: How many files the judge rated.
    - ratingsToSongs: Dictionary storing total ratings a judge has given in the
                      batch file.
                      'rating':[(TITLE,ARTIST,STEPARTIST),...]
    - ratingsRaw: Simpler dictionary just containing counts of ratings.

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
        self.judgeName = ""
        self.average = 0
        self.judgedSongList = []
        self.numJudgedFiles = 0
        self.ratingsToSongs = {}
        self.ratingsRaw = {}

    def dumpInfo(self):
        print(logMsg("JUDGENOTES","INFO"),"dumpInfo: Dumping Judge Notes Info")
        print("- JUDGE NOTES FILE PATH:", self.path,
              "\n- JUDGE NOTES FILE:", self.notesFile,
              "\n- JUDGE NOTES FILE DIR:", self.fileDir,
              "\n- JUDGE AVERAGE:", self.average,
              "\n- JUDGE RATINGS:", self.numJudgedFiles,
              "\n- JUDGE NAME:", self.judgeName)

    def getJudgeRatings(self):
        """
        Looks through the file user specified for what judge gave.
        [TITLE,STEPARTIST] entries are added to judged song list,
        this is used for checks if multiple stepartists submitted
        the same song.
        """
        print(logMsg("JUDGENOTES","INFO"),"getJudgeRatings: Parsing Judge Notes File")
        try:
            os.chdir(self.fileDir) # Change to batch directory context
            with open(self.notesFile) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        ratingTuple = self.getRatingWithInfo(line)
                        # ([TITLE,ARTIST,STEPARTIST],rating) tuple entry added to judged song list.
                        self.judgedSongList.append(ratingTuple)
            judgeFile.close()
            self.numJudgedFiles = len(self.judgedSongList) # Save how many files the judge rated.
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getJudgeName(self):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Notes_MayBatch.txt
        File must be in format of <JudgeName>_Notes -- anything else can come after
        """
        print(logMsg("JUDGENOTES","INFO"),"getJudgeName: Retrieving Judge Name from Notes File '" + self.notesFile + "'")
        try:
            judgeParse = re.search("^(.*)_Notes",self.notesFile)
            if judgeParse != None:
                self.judgeName = str(judgeParse.group(1))
                print(logMsg("JUDGENOTES","INFO"),"getJudgeName: Judge is '" + self.judgeName + "'")
            else:
                print(logMsg("JUDGENOTES","WARNING"),"getJudgeName: Judge Notes File is not in correct format")
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getRatingWithInfo(self,ratingLine):
        """
        ratingLine is the line with the rating and song information in judge notes.
        Format: [Rating] Song Name {Song Artist} (Stepper)
                [Rating] Song Name {Song Artist}
        Example: [7.5/10] Moonearth {DJ Sharpnel} (Tyler)
                 [6/10] valedict {void}

        Returns a tuple in the form of ([TITLE,ARTIST,STEPARTIST],rating)
        Note if there's no stepartist, a null string will be in stepartist field
        Example Return: (["Dysnomia","Reizoko Cj","Nick Skyline"],5.5)
        """

        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)
        ratingNoStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}$",ratingLine)
        songInfo = []
        try:

            # Retrieve song information from line.
            if ratingStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"getRatingWithInfo: Found rating with stepartist")
                # ratingStepartist.group(0) # Full match
                rating = ratingStepartist.group(1) # Rating number itself
                songInfo = [ ratingStepartist.group(2).strip(), # Song Title
                             ratingStepartist.group(3).strip(), # Song Artist
                             ratingStepartist.group(4).strip() ] # Stepartist
            elif ratingNoStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"getRatingWithInfo: Found rating without stepartist")
                # ratingNoStepartist.group(0) # Full Match
                rating = ratingNoStepartist.group(1) # Rating number itself
                songInfo = [ ratingNoStepartist.group(2).strip(), # Song Title
                             ratingNoStepartist.group(3).strip(), # Song Artist
                             "" ]  # Stepartist placeholder, used for compatibility

            return (songInfo,rating)
        
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getRatingWithInfo: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    

    def printJudgeRatings(self):
        """
        Print out parsed judge ratings with song info
        Each tuple is in the form of ([TITLE,ARTIST,STEPARTIST],rating)
        TITLE {STEPARTIST} --> [rating/10]
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "printJudgeRatings: Printing out judge ratings from '" + self.notesFile + "'")
            for ratingTuple in self.judgedSongList:
                if ratingTuple[0][2] != "":
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}", "("+ratingTuple[0][2]+")",
                          "\nRATING:","["+ratingTuple[1]+"/10]")
                else:
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}",
                          "\nRATING:","["+ratingTuple[1]+"/10]")
        except:
            print(logMsg("JUDGENOTES","ERROR"), "printJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getJudgeAverage(self):
        """
        Figures out the average rating a judge gave.
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "getJudgeAverage: Retrieving Judge Average from '" + self.notesFile + "'")
            ratingSum = 0
            for ratingTuple in self.judgedSongList:
                ratingSum += float(ratingTuple[1]) # Get sum of all judge's ratings in the notes file.
            print(logMsg("JUDGENOTES","INFO"), "getJudgeAverage:",ratingSum,"/",self.numJudgedFiles,"=",self.average )
            self.average = ratingSum / self.numJudgedFiles
                
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeAverage: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getRatingsToSongs(self):
        """
        Each tuple in judgedSongList looks like this:
        ([TITLE,ARTIST,STEPARTIST],rating)

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]

        Basically we're reversing the way this is stored.
        Done after ratingsToSongs has been created.
        """
        print(logMsg("JUDGENOTES","INFO"), "getRatingsToSongs: Generating Dictionary for Ratings --> Songs")
        try:
            for ratingTuple in self.judgedSongList:
                keyForDict = ratingTuple[1]
                songInfo = ratingTuple[0]
                if keyForDict not in self.ratingsToSongs:
                    self.ratingsToSongs[keyForDict] = [songInfo]
                else:
                    self.ratingsToSongs[keyForDict].append(songInfo)

        except:
            print(logMsg("JUDGENOTES","ERROR"), "getRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def printRatingsToSongs(self):
        """
        Print out the songs that fell under the parsed ratings.

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]
        """
        print(logMsg("JUDGENOTES","INFO"), "printRatingsToSongs: Printing songs for each rating parsed")
        try:
            sortedRatings = sorted(self.ratingsToSongs.keys(), key=float)
            for rating in sortedRatings:
                print("") # For neater printing. Newline still occurs here
                songsInRating = self.ratingsToSongs[rating]
                print("["+str(rating)+"/10]")
                for song in songsInRating:
                    if song[2] != "":
                        print("-->",song[0],"{"+song[1]+"}","("+song[2]+")")
                    else:
                        print("-->",song[0],"{"+song[1]+"}")
            print("") # For neater printing. Newline still occurs here
        except:
            print(logMsg("JUDGENOTES","ERROR"), "printRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def writeRatingsToSongs(self):
        """
        Write out songs for each rating out to file.
        """
        print(logMsg("JUDGENOTES","INFO"), "writeRatingsToSongs: Writing file containining songs for each rating")
        try:
            os.chdir(self.fileDir)
            sortedRatings = sorted(self.ratingsToSongs.keys(), key=float)
            fileName = "ratingsToSongs.txt"
            with open("ratingsToSongs.txt", 'w') as outFile:
                for rating in sortedRatings:
                    songsInRating = self.ratingsToSongs[rating]
                    outFile.write("["+str(rating)+"/10]")
                    for song in songsInRating:
                        if song[2] != "":
                            outFile.write("\n--> " + str(song[0]) + " {" + str(song[1]) + "} ("+str(song[2]) + ")")
                        else:
                            outFile.write("\n--> " + str(song[0]) + " {" + str(song[1]) + "}")
                    outFile.write("\n\n")
            outFile.close()
            print(logMsg("JUDGENOTES","INFO"),"writeRatingsToSongs: Successfully wrote file '" + fileName + "'")
        except:
            print(logMsg("JUDGENOTES","ERROR"), "writeRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def printJudgeAverage(self):
        """
        Prints out calculated judge average.
        """
        print(logMsg("JUDGENOTES","INFO"), "printJudgeAverage: '" + str(self.average) + "' Judge Average from '" + self.notesFile + "'")

    def printNumOfJudgedFiles(self):
        """
        Prints out number of files the judge rated.
        """
        print(logMsg("JUDGENOTES","INFO"), "printNumOfJudgedFiles:", self.numJudgedFiles, "files judged from '" + self.notesFile + "'")

# use suites\judgenotes\DossarLX ODI_NotesMayBatch.txt
# C:\pythoncode\batchApis\suites\judgenotes\DossarLX ODI_NotesMayBatch.txt
# 9 files
# 4/10 - 1
# 5/10 - 2
# 6/10 - 2
# 6.5/10 - 1
# 7.5/10 - 1
# 8/10 - 1
# 10/10 - 1
# MAIN
if __name__ == "__main__":

    judgeNotesFilePath = input("Input full path of Judge Notes File: ")
    judge = JudgeNotes(judgeNotesFilePath)
    judge.dumpInfo()
    judge.getJudgeName()
##    judge.getJudgeRatings()
##    judge.printJudgeRatings()
##    judge.getJudgeAverage()
##    judge.printJudgeAverage()
##    judge.printNumOfJudgedFiles()
##    judge.getRatingsToSongs()
##    judge.printRatingsToSongs()
##    judge.writeRatingsToSongs()
##    judge.dumpInfo()

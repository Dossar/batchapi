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
    - specialSongList: Same format as judgedSongList but with special ratings.
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
        self.specialSongList = []
        self.numJudgedFiles = 0
        self.numSpecialFiles = 0
        self.numTotalFiles = 0
        self.ratingsToSongs = {}
        self.ratingsRaw = {}
        self.specialRatingsToSongs = {}
        self.specialRatingsRaw = {}

    def dumpInfo(self):
        print(logMsg("JUDGENOTES","INFO"),"dumpInfo: Dumping Judge Notes Info")
        print("- JUDGE NOTES FILE PATH:", self.path,
              "\n- JUDGE NOTES FILE:", self.notesFile,
              "\n- JUDGE NOTES FILE DIR:", self.fileDir,
              "\n- JUDGE NAME:", self.judgeName,
              "\n- JUDGE AVERAGE:", self.average,
              "\n- JUDGED RATINGS:", self.numJudgedFiles,
              "\n- SPECIAL RATINGS:", self.numSpecialFiles,
              "\n- TOTAL RATINGS:", self.numTotalFiles)

    def getJudgeRatings(self):
        """
        Looks through the file user specified for what judge gave.
        This is also used for checks if multiple stepartists submitted
        the same song.
        """
        print(logMsg("JUDGENOTES","INFO"),"getJudgeRatings: Parsing Judge Notes File")
        try:
            os.chdir(self.fileDir) # Change to batch directory context
            with open(self.notesFile) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        self.getRatingWithInfo(line)                       
            judgeFile.close()
            self.numJudgedFiles = len(self.judgedSongList)
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getNumSpecialFiles(self):
        self.numSpecialFiles = len(self.specialSongList)

    def getNumTotalFiles(self):
        self.numTotalFiles = self.numJudgedFiles + self.numSpecialFiles

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

        EXCEPTIONS
        Other 'ratings' to consider are:
        - 'PASS'
        - '++' (this is 10/10, guaranteed)
        - '--' (this is just 0/10, guaranteed)
        - '!' (this is also 0/10, guaranteed)
        - '*' (Conditional Queue Flag)
        - '#' (The Judge made the file)
        - '<' (there's already a better file in queue, this doesn't go as v2)
        - '$' (file is better than queued file)
        """

        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)
        ratingNoStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}$",ratingLine)

        # I wasn't able to do a generalized capture here because weird things happened
        # For instance, !, +, -, and * were captured, but with #, <, and $ things got weird
        passRating = re.search("^\[(PASS).*\]",ratingLine)
        plus = re.search("^\[(\+\+).*\]",ratingLine)
        negative = re.search("^\[(--).*\]",ratingLine)
        bang = re.search("^\[(!).*\]",ratingLine)
        star = re.search("^\[(\*).*\]",ratingLine)
        pound = re.search("^\[(\#).*\]",ratingLine)
        arrow = re.search("^\[(\<)\]",ratingLine)
        dollar = re.search("^\[(\$)\]",ratingLine)
        songInfo = []
        rating = 0
        try:

            # Retrieve song information from line.
            if ratingStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"getRatingWithInfo: Found rating with stepartist")
                # ratingStepartist.group(0) # Full match
                rating = ratingStepartist.group(1) # Rating number itself
                songInfo = [ ratingStepartist.group(2).strip(), # Song Title
                             ratingStepartist.group(3).strip(), # Song Artist
                             ratingStepartist.group(4).strip() ] # Stepartist
                tupleToAdd = (songInfo,rating)
                self.judgedSongList.append(tupleToAdd)
                return
            elif ratingNoStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"getRatingWithInfo: Found rating without stepartist")
                # ratingNoStepartist.group(0) # Full Match
                rating = ratingNoStepartist.group(1) # Rating number itself
                songInfo = [ ratingNoStepartist.group(2).strip(), # Song Title
                             ratingNoStepartist.group(3).strip(), # Song Artist
                             "" ]  # Stepartist placeholder, used for compatibility
                tupleToAdd = (songInfo,rating)
                self.judgedSongList.append(tupleToAdd)
                return
            elif passRating != None:
                specialTuple = self.handleSpecialRating(passRating.group(1).strip(),ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif plus != None:
                specialTuple = self.handleSpecialRating(plus.group(1).strip(),ratingLine)
                self.judgedSongList.append(specialTuple) # A '++' is a 10/10
                return
            elif negative != None:
                specialTuple = self.handleSpecialRating(negative.group(1).strip(),ratingLine)
                self.judgedSongList.append(specialTuple) # A '--' is a 0/10
                return
            elif bang != None:
                specialTuple = self.handleSpecialRating(bang.group(1).strip(),ratingLine)
                self.judgedSongList.append(specialTuple) # A '!' is a 0/10
                return
            elif star != None:
                specialTuple = self.handleSpecialRating(star.group(1).strip(),ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif pound != None:
                specialTuple = self.handleSpecialRating(pound.group(1).strip(),ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif arrow != None:
                specialTuple = self.handleSpecialRating(arrow.group(1).strip(),ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif dollar != None:
                specialTuple = self.handleSpecialRating(dollar.group(1).strip(),ratingLine)
                self.specialSongList.append(specialTuple)
                return            
        
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getRatingWithInfo: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    

    def handleSpecialRating(self,symbol,lineToParse):
        """
        Other 'ratings' to consider are:
        - 'PASS'
        - '++' (this is 10/10, guaranteed)
        - '--' (this is just 0/10, guaranteed)
        - '!' (this is also 0/10, guaranteed)
        - '*' (Conditional Queue Flag)
        - '#' (The Judge made the file)
        - '<' (there's already a better file in queue, this doesn't go as v2)
        - '$' (file is better than queued file)

        symbol is the captured special rating.
        lineToParse is the full line in which the symbol was spotted.
        """
        try:
            songInfo = []
            #ratingStepartist = re.search("^\[.*\](.*)\{(.*)\}[\s]*\((.*)\)$",lineToParse)
            #ratingNoStepartist = re.search("^\[.*\](.*)\{(.*)\}$",lineToParse)
            ratingStepartist = re.search("^\[\\"+symbol+"[10/]*\](.*)\{(.*)\}[\s]*\((.*)\)$",lineToParse)
            ratingNoStepartist = re.search("^\[\\"+symbol+"[10/]*\](.*)\{(.*)\}$",lineToParse)
            if ratingStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"handleSpecialRating: Found rating with stepartist on special rating '" + symbol + "'")
                # ratingStepartist.group(0) # Full match
                songInfo = [ ratingStepartist.group(1).strip(), # Song Title
                             ratingStepartist.group(2).strip(), # Song Artist
                             ratingStepartist.group(3).strip() ] # Stepartist
            elif ratingNoStepartist != None:
                print(logMsg("JUDGENOTES","INFO"),"handleSpecialRating: Found rating without stepartist on special rating '" + symbol + "'")
                # ratingNoStepartist.group(0) # Full Match
                songInfo = [ ratingNoStepartist.group(1).strip(), # Song Title
                             ratingNoStepartist.group(2).strip(), # Song Artist
                             "" ]  # Stepartist placeholder, used for compatibility

            # ++ is a guaranteed 10, and -- and ! are guaranteed 0.
            if symbol == "++":
                rating = '10'
            elif symbol == "--" or symbol == "!":
                rating = '0'
            else:
                rating = symbol

            return (songInfo,rating)
                             
        except:
            print(logMsg("JUDGENOTES","ERROR"), "handleSpecialRating: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    

    def printJudgeRatings(self):
        """
        Print out parsed judge ratings with song info. I wouldn't recommend using this, it's messy
        Each tuple is in the form of ([TITLE,ARTIST,STEPARTIST],rating)
        TITLE {STEPARTIST} --> [rating/10]
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "printJudgeRatings: Printing out judge ratings from '" + self.notesFile + "'\n")

            # Print Normal List First.
            for ratingTuple in self.judgedSongList:
                if ratingTuple[0][2] != "":
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}", "("+ratingTuple[0][2]+")",
                          "\nRATING:","["+str(ratingTuple[1])+"/10]\n")
                else:
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}",
                          "\nRATING:","["+str(ratingTuple[1])+"/10]\n")

            # Print Special List Second.
            for ratingTuple in self.specialSongList:
                if ratingTuple[0][2] != "":
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}", "("+ratingTuple[0][2]+")",
                          "\nRATING:","["+str(ratingTuple[1])+"]\n")
                else:
                    print("SONG:",ratingTuple[0][0], "{"+ratingTuple[0][1]+"}",
                          "\nRATING:","["+str(ratingTuple[1])+"]\n")
            
        except:
            print(logMsg("JUDGENOTES","ERROR"), "printJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getRatingSum(self):
        ratingSum = 0
        for ratingTuple in self.judgedSongList:
            ratingSum += float(ratingTuple[1]) # Get sum of all judge's ratings in the notes file.
        return ratingSum

    def getJudgeAverage(self):
        """
        Figures out the average rating a judge gave.
        Requires judgedSongList to have already been created.
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "getJudgeAverage: Retrieving Judge Average from '" + self.notesFile + "'")
            ratingSum = self.getRatingSum()
            self.average = ratingSum / self.numJudgedFiles
            print(logMsg("JUDGENOTES","INFO"), "getJudgeAverage:",ratingSum,"/",self.numJudgedFiles,"=",self.average )
        except:
            print(logMsg("JUDGENOTES","ERROR"), "getJudgeAverage: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getRawRatings(self):
        """
        Retrieving raw number of songs for each rating.
        This is done after ratingsToSongs has been created.

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]

        Each dictionary entry in ratingsRaw looks like this:
        'rating':<integer/number of files with rating>
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "getRawRatings: Retrieving Raw Ratings from '" + self.notesFile + "'")
            for rating in self.ratingsToSongs.keys():
                numOfSongsWithRating = len(self.ratingsToSongs[rating])
                self.ratingsRaw[rating] = numOfSongsWithRating

        except:
            print(logMsg("JUDGENOTES","ERROR"), "getRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getRawSpecialRatings(self):
        try:
            print(logMsg("JUDGENOTES","INFO"), "getRawSpecialRatings: Retrieving Raw Ratings from '" + self.notesFile + "'")
            for rating in self.specialRatingsToSongs.keys():
                numOfSongsWithRating = len(self.specialRatingsToSongs[rating])
                self.specialRatingsRaw[rating] = numOfSongsWithRating

        except:
            print(logMsg("JUDGENOTES","ERROR"), "getRawSpecialRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        

    def printRawRatings(self):
        """
        Print out just a simple listing of how many songs got a certain rating.

        Each dictionary entry in ratingsRaw looks like this:
        'rating':<integer/number of files with rating>
        """

        try:
            print(logMsg("JUDGENOTES","INFO"), "printRawRatings: Retrieving Raw Ratings from '" + self.notesFile + "'\n")
            sortedRatings = sorted(self.ratingsRaw.keys(), key=float)
            for rating in sortedRatings:
                print("["+str(rating)+"/10]:"+str(self.ratingsRaw[rating]))
            ratingSum = self.getRatingSum()
            sortedRatings = sorted(self.specialRatingsRaw.keys(), key=str.lower)
            for rating in sortedRatings:
                print("["+str(rating)+"]:"+str(self.specialRatingsRaw[rating]))
            print("TOTAL:"+str(round(ratingSum,1)))
            print("JUDGEDFILES:"+str(self.numJudgedFiles))
            print("SPECIALFILES:"+str(self.numSpecialFiles))
            print("TOTALFILES:"+str(self.numTotalFiles))
            print("AVERAGE:"+str(round(self.average,2))+"\n")

        except:
            print(logMsg("JUDGENOTES","ERROR"), "printRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))


    def getRatingsToSongs(self):
        """
        Each tuple in judgedSongList looks like this:
        ([TITLE,ARTIST,STEPARTIST],rating)

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]

        Basically we're reversing the way this is stored.
        Done after judgedSongList has been created.
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

    def getSpecialRatingsToSongs(self):
        print(logMsg("JUDGENOTES","INFO"), "getSpecialRatingsToSongs: Generating Dictionary for Special Ratings --> Songs")
        try:
            for ratingTuple in self.specialSongList:
                keyForDict = ratingTuple[1]
                songInfo = ratingTuple[0]
                if keyForDict not in self.specialRatingsToSongs:
                    self.specialRatingsToSongs[keyForDict] = [songInfo]
                else:
                    self.specialRatingsToSongs[keyForDict].append(songInfo)

        except:
            print(logMsg("JUDGENOTES","ERROR"), "getSpecialRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        
    def printRatingsToSongs(self):
        """
        Print out the songs that fell under the parsed ratings.

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]
        """
        print(logMsg("JUDGENOTES","INFO"), "printRatingsToSongs: Printing songs for each rating parsed")
        try:

            # Print out normal ratings first.
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

            # Print out special ratings after.
            sortedRatings = sorted(self.specialRatingsToSongs.keys(), key=str.lower)
            for rating in sortedRatings:
                print("") # For neater printing. Newline still occurs here
                songsInRating = self.specialRatingsToSongs[rating]
                print("["+str(rating)+"]")
                for song in songsInRating:
                    if song[2] != "":
                        print("-->",song[0],"{"+song[1]+"}","("+song[2]+")")
                    else:
                        print("-->",song[0],"{"+song[1]+"}")
                    
            print("") # For neater printing. Newline still occurs here
        except:
            print(logMsg("JUDGENOTES","ERROR"), "printRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def writeRawRatings(self):
        """
        Write out number of songs that got each rating parsed.
        """
        print(logMsg("JUDGENOTES","INFO"), "writeRawRatings: Writing file containining songs for each rating")
        try:
            os.chdir(self.fileDir)
            sortedRatings = sorted(self.ratingsRaw.keys(), key=float)
            fileName = "ratingsRaw_" + self.judgeName + ".txt"
            with open(fileName, 'w') as outFile:

                # Write out normal raw ratings first.
                for rating in sortedRatings:
                    outFile.write("["+str(rating)+"/10]:"+str(self.ratingsRaw[rating])+"\n")
                ratingSum = self.getRatingSum()

                # Write out special raw ratings second.
                sortedRatings = sorted(self.specialRatingsRaw.keys(), key=str.lower)
                for rating in sortedRatings:
                    outFile.write("["+str(rating)+"]:"+str(self.specialRatingsRaw[rating])+"\n")

                # Write out average as well.
                outFile.write("TOTAL:"+str(round(ratingSum,1))+"\n")
                outFile.write("JUDGEDFILES:"+str(self.numJudgedFiles)+"\n")
                outFile.write("SPECIALFILES:"+str(self.numSpecialFiles)+"\n")
                outFile.write("TOTALFILES:"+str(self.numTotalFiles)+"\n")
                outFile.write("AVERAGE:"+str(round(self.average,2))+"\n")
            outFile.close()
            print(logMsg("JUDGENOTES","INFO"),"writeRawRatings: Successfully wrote file '" + fileName + "'")
        except:
            print(logMsg("JUDGENOTES","ERROR"), "writeRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        

    def writeRatingsToSongs(self):
        """
        Write out songs for each rating out to file.
        """
        print(logMsg("JUDGENOTES","INFO"), "writeRatingsToSongs: Writing file containining songs for each rating")
        try:
            os.chdir(self.fileDir)
            sortedRatings = sorted(self.ratingsToSongs.keys(), key=float)
            fileName = "ratingsToSongs_" + self.judgeName + ".txt"
            with open(fileName, 'w') as outFile:

                # Write out the normal ratings first.
                for rating in sortedRatings:
                    songsInRating = self.ratingsToSongs[rating]
                    outFile.write("["+str(rating)+"/10]")
                    for song in songsInRating:
                        if song[2] != "":
                            outFile.write("\n--> " + str(song[0]) + " {" + str(song[1]) + "} ("+str(song[2]) + ")")
                        else:
                            outFile.write("\n--> " + str(song[0]) + " {" + str(song[1]) + "}")
                    outFile.write("\n\n")

                # Write out the special ratings after.
                sortedRatings = sorted(self.specialRatingsToSongs.keys(), key=str.lower)
                for rating in sortedRatings:
                    songsInRating = self.specialRatingsToSongs[rating]
                    outFile.write("["+str(rating)+"]")
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

# Test files:
# C:\pythoncode\batchApis\suites\judgenotes\DossarLX ODI_NotesMayBatch.txt
# C:\pythoncode\batchApis\suites\judgenotes\Niala_Notes_OtherSymbols.txt

# MAIN
if __name__ == "__main__":

    judgeNotesFilePath = (input("Input full path of Judge Notes File: ")).strip()
    judge = JudgeNotes(judgeNotesFilePath)
    judge.dumpInfo()
    judge.getJudgeName()

    
    judge.getJudgeRatings()
    judge.getNumSpecialFiles()
    judge.getNumTotalFiles()
    judge.printJudgeRatings()
    judge.getJudgeAverage()
    judge.printJudgeAverage()

    
    judge.printNumOfJudgedFiles()
    judge.getRatingsToSongs()
    judge.getSpecialRatingsToSongs()
    judge.printRatingsToSongs()
    judge.writeRatingsToSongs()

    
    judge.getRawRatings()
    judge.getRawSpecialRatings()
    judge.printRawRatings()
    judge.writeRawRatings()
    judge.dumpInfo()

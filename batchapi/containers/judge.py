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

# Make judgeNotesLogger logger object.
judgeNotesLogger = logging.getLogger("JUDGENOTES")
judgeNotesLogger.setLevel(logging.DEBUG)
judgeNotesFileH = logging.FileHandler('/tmp/judgeNotes.log')
judgeNotesFileH.setLevel(logging.DEBUG)
judgeNotesConsoleH = logging.StreamHandler()
judgeNotesConsoleH.setLevel(logging.WARNING)
judgeNotesFileH.setFormatter(dateformatter)
judgeNotesConsoleH.setFormatter(dateformatter)
judgeNotesLogger.addHandler(judgeNotesFileH)  # File Handler add
judgeNotesLogger.addHandler(judgeNotesConsoleH)  # Console Handler add

# Make judgesExcelLogger logger object.
judgesExcelLogger = logging.getLogger("JUDGESFOREXCEL")
judgesExcelLogger.setLevel(logging.DEBUG)
judgesExcelLoggerFileH = logging.FileHandler('/tmp/judgesExcelLogger.log')
judgesExcelLoggerFileH.setLevel(logging.DEBUG)
judgesExcelLoggerConsoleH = logging.StreamHandler()
judgesExcelLoggerConsoleH.setLevel(logging.WARNING)
judgesExcelLoggerFileH.setFormatter(dateformatter)
judgesExcelLoggerConsoleH.setFormatter(dateformatter)
judgesExcelLogger.addHandler(judgesExcelLoggerFileH)  # File Handler add
judgesExcelLogger.addHandler(judgesExcelLoggerConsoleH)  # Console Handler add

#####################
# CLASS DEFINITIONS #
#####################

class JudgeNotes():
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
    - __str__():
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

    def __str__(self):
        return """>>> JUDGE NOTES INFORMATION
- JUDGE NOTES FILE PATH: {}
- JUDGE NOTES FILE: {}
- JUDGE NOTES FILE DIR: {}
- JUDGE NAME: {}
- JUDGE AVERAGE: {}
- JUDGED RATINGS: {}
- SPECIAL RATINGS: {}
- TOTAL RATINGS: {}""" \
        .format(self.path, self.notesFile, self.fileDir, self.judgeName, self.average, self.numJudgedFiles,
                self.numSpecialFiles, self.numTotalFiles)

    def getJudgeRatings(self):
        """
        Looks through the file user specified for what judge gave.
        This is also used for checks if multiple stepartists submitted
        the same song.
        """
        judgeNotesLogger.info("getJudgeRatings: Parsing Judge Notes File")
        try:
            os.chdir(self.fileDir)  # Change to batch directory context
            with open(self.notesFile) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        self.getRatingWithInfo(line)                       
            judgeFile.close()
            self.numJudgedFiles = len(self.judgedSongList)
        except:
            judgeNotesLogger.warning("getJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

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
        judgeNotesLogger.info("getJudgeName: Retrieving Judge Name from Notes File '%s'", self.notesFile)
        try:
            judgeParse = re.search("^(.*)_Notes", self.notesFile)
            if judgeParse is not None:
                self.judgeName = str(judgeParse.group(1))
                judgeNotesLogger.debug("getJudgeName: Judge is '%s'", self.judgeName)
            else:
                judgeNotesLogger.warning("getJudgeName: Judge Notes File is not in correct format")
        except:
            judgeNotesLogger.warning("getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                     str(sys.exc_info()[1])))

    def getRatingWithInfo(self, ratingLine):
        """
        ratingLine is the line with the rating and song information in judge notes.
        Format: [Rating] Song Name {Song Artist} (Stepper)
                [Rating] Song Name {Song Artist}
        Example: [7.5/10] Moonearth {DJ Sharpnel} (Tyler)
                 [6/10] valedict {void}

        Returns a tuple in the form of ([TITLE,ARTIST,STEPARTIST],rating)
        Note if there's no stepartist, a null string will be in stepartist field
        Example Return: (["Dysnomia", "Reizoko Cj", "Nick Skyline"], 5.5)

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

        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$", ratingLine)
        ratingNoStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}$", ratingLine)

        # I wasn't able to do a generalized capture here because weird things happened
        # For instance, !, +, -, and * were captured, but with #, <, and $ things got weird
        passRating = re.search("^\[(PASS).*\]", ratingLine)
        plus = re.search("^\[(\+\+).*\]", ratingLine)
        negative = re.search("^\[(--).*\]", ratingLine)
        bang = re.search("^\[(!).*\]", ratingLine)
        star = re.search("^\[(\*).*\]", ratingLine)
        pound = re.search("^\[(#).*\]", ratingLine)
        arrow = re.search("^\[(<)\]", ratingLine)
        dollar = re.search("^\[(\$)\]", ratingLine)
        songInfo = []
        rating = 0
        try:
            # Retrieve song information from line.
            if ratingStepartist is not None:
                judgeNotesLogger.debug("getRatingWithInfo: Found rating with stepartist")
                # ratingStepartist.group(0) # Full match
                rating = ratingStepartist.group(1)  # Rating number itself
                songInfo = [ratingStepartist.group(2).strip(),  # Song Title
                            ratingStepartist.group(3).strip(),  # Song Artist
                            ratingStepartist.group(4).strip()]  # Stepartist
                tupleToAdd = (songInfo, rating)
                self.judgedSongList.append(tupleToAdd)
                return
            elif ratingNoStepartist is not None:
                judgeNotesLogger.debug("getRatingWithInfo: Found rating without stepartist")
                # ratingNoStepartist.group(0) # Full Match
                rating = ratingNoStepartist.group(1)  # Rating number itself
                songInfo = [ratingNoStepartist.group(2).strip(),  # Song Title
                            ratingNoStepartist.group(3).strip(),  # Song Artist
                            ""]  # Stepartist placeholder, used for compatibility
                tupleToAdd = (songInfo, rating)
                self.judgedSongList.append(tupleToAdd)
                return
            elif passRating is not None:
                specialTuple = self.handleSpecialRating(passRating.group(1).strip(), ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif plus is not None:
                specialTuple = self.handleSpecialRating(plus.group(1).strip(), ratingLine)
                self.judgedSongList.append(specialTuple)  # A '++' is a 10/10
                return
            elif negative is not None:
                specialTuple = self.handleSpecialRating(negative.group(1).strip(), ratingLine)
                self.judgedSongList.append(specialTuple)  # A '--' is a 0/10
                return
            elif bang is not None:
                specialTuple = self.handleSpecialRating(bang.group(1).strip(), ratingLine)
                self.judgedSongList.append(specialTuple)  # A '!' is a 0/10
                return
            elif star is not None:
                specialTuple = self.handleSpecialRating(star.group(1).strip(), ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif pound is not None:
                specialTuple = self.handleSpecialRating(pound.group(1).strip(), ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif arrow is not None:
                specialTuple = self.handleSpecialRating(arrow.group(1).strip(), ratingLine)
                self.specialSongList.append(specialTuple)
                return
            elif dollar is not None:
                specialTuple = self.handleSpecialRating(dollar.group(1).strip(), ratingLine)
                self.specialSongList.append(specialTuple)
                return            
        
        except:
            judgeNotesLogger.warning("getRatingWithInfo: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

    def handleSpecialRating(self, symbol, lineToParse):
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
            ratingStepartist = re.search("^\[\\"+symbol+"[10/]*\](.*)\{(.*)\}[\s]*\((.*)\)$", lineToParse)
            ratingNoStepartist = re.search("^\[\\"+symbol+"[10/]*\](.*)\{(.*)\}$", lineToParse)
            if ratingStepartist is not None:
                judgeNotesLogger.debug("handleSpecialRating: Found rating with stepartist on special "
                                       "rating '%s'", symbol)
                # ratingStepartist.group(0) # Full match
                songInfo = [ratingStepartist.group(1).strip(),  # Song Title
                            ratingStepartist.group(2).strip(),  # Song Artist
                            ratingStepartist.group(3).strip()]  # Stepartist
            elif ratingNoStepartist is not None:
                judgeNotesLogger.debug("handleSpecialRating: Found rating without stepartist on special "
                                       "rating '%s'", symbol)
                # ratingNoStepartist.group(0) # Full Match
                songInfo = [ratingNoStepartist.group(1).strip(),  # Song Title
                            ratingNoStepartist.group(2).strip(),  # Song Artist
                            ""]  # Stepartist placeholder, used for compatibility

            # ++ is a guaranteed 10, and -- and ! are guaranteed 0.
            if symbol == "++":
                rating = '10'
            elif symbol == "--" or symbol == "!":
                rating = '0'
            else:
                rating = symbol

            return songInfo, rating
        except:
            judgeNotesLogger.warning("handleSpecialRating: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                            str(sys.exc_info()[1])))

    def printJudgeRatings(self):
        """
        Print out parsed judge ratings with song info. I wouldn't recommend using this, it's messy
        Each tuple is in the form of ([TITLE,ARTIST,STEPARTIST],rating)
        TITLE {STEPARTIST} --> [rating/10]
        """

        try:
            judgeNotesLogger.info("printJudgeRatings: Printing out judge ratings from '%s'\n", self.notesFile)

            # Print Normal List First.
            for ratingTuple in self.judgedSongList:
                if ratingTuple[0][2] != "":
                    print("SONG:", ratingTuple[0][0], "{"+ratingTuple[0][1]+"}", "("+ratingTuple[0][2]+")",
                          "\nRATING:", "["+str(ratingTuple[1])+"/10]\n")
                else:
                    print("SONG:", ratingTuple[0][0], "{"+ratingTuple[0][1]+"}",
                          "\nRATING:", "["+str(ratingTuple[1])+"/10]\n")

            # Print Special List Second.
            for ratingTuple in self.specialSongList:
                if ratingTuple[0][2] != "":
                    print("SONG:", ratingTuple[0][0], "{"+ratingTuple[0][1]+"}", "("+ratingTuple[0][2]+")",
                          "\nRATING:", "["+str(ratingTuple[1])+"]\n")
                else:
                    print("SONG:", ratingTuple[0][0], "{"+ratingTuple[0][1]+"}",
                          "\nRATING:", "["+str(ratingTuple[1])+"]\n")
            
        except:
            judgeNotesLogger.warning("printJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

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
            judgeNotesLogger.info("getJudgeAverage: Retrieving Judge Average from '%s'", self.notesFile)
            ratingSum = self.getRatingSum()
            self.average = ratingSum / self.numJudgedFiles
            judgeNotesLogger.debug("getJudgeAverage: '%s' / '%s' = '%s'", str(ratingSum),
                                   str(self.numJudgedFiles), str(self.average))
        except:
            judgeNotesLogger.warning("getJudgeAverage: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

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
            judgeNotesLogger.info("getRawRatings: Retrieving Raw Ratings from '%s'", self.notesFile)
            for rating in self.ratingsToSongs.keys():
                numOfSongsWithRating = len(self.ratingsToSongs[rating])
                self.ratingsRaw[rating] = numOfSongsWithRating

        except:
            judgeNotesLogger.warning("getRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def getRawSpecialRatings(self):
        try:
            judgeNotesLogger.info("getRawSpecialRatings: Retrieving Raw Ratings from '%s'", self.notesFile)
            for rating in self.specialRatingsToSongs.keys():
                numOfSongsWithRating = len(self.specialRatingsToSongs[rating])
                self.specialRatingsRaw[rating] = numOfSongsWithRating

        except:
            judgeNotesLogger.warning("getRawSpecialRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))        

    def printRawRatings(self):
        """
        Print out just a simple listing of how many songs got a certain rating.

        Each dictionary entry in ratingsRaw looks like this:
        'rating':<integer/number of files with rating>
        """

        try:
            judgeNotesLogger.info("printRawRatings: Retrieving Raw Ratings from '%s'\n", self.notesFile)
            sortedRatings = sorted(self.ratingsRaw.keys(), key=float)
            for rating in sortedRatings:
                print("["+str(rating)+"/10]:"+str(self.ratingsRaw[rating]))
            ratingSum = self.getRatingSum()
            sortedRatings = sorted(self.specialRatingsRaw.keys(), key=str.lower)
            for rating in sortedRatings:
                print("["+str(rating)+"]:"+str(self.specialRatingsRaw[rating]))
            print("TOTAL:"+str(round(ratingSum, 1)))
            print("JUDGEDFILES:"+str(self.numJudgedFiles))
            print("SPECIALFILES:"+str(self.numSpecialFiles))
            print("TOTALFILES:"+str(self.numTotalFiles))
            print("AVERAGE:"+str(round(self.average, 2))+"\n")

        except:
            judgeNotesLogger.warning("printRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))


    def getRatingsToSongs(self):
        """
        Each tuple in judgedSongList looks like this:
        ([TITLE,ARTIST,STEPARTIST],rating)

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]

        Basically we're reversing the way this is stored.
        Done after judgedSongList has been created.
        """
        judgeNotesLogger.info("getRatingsToSongs: Generating Dictionary for Ratings --> Songs")
        try:
            for ratingTuple in self.judgedSongList:
                keyForDict = ratingTuple[1]
                songInfo = ratingTuple[0]
                if keyForDict not in self.ratingsToSongs:
                    self.ratingsToSongs[keyForDict] = [songInfo]
                else:
                    self.ratingsToSongs[keyForDict].append(songInfo)
        except:
            judgeNotesLogger.warning("getRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

    def getSpecialRatingsToSongs(self):
        judgeNotesLogger.info("getSpecialRatingsToSongs: Generating Dictionary for Special Ratings --> Songs")
        try:
            for ratingTuple in self.specialSongList:
                keyForDict = ratingTuple[1]
                songInfo = ratingTuple[0]
                if keyForDict not in self.specialRatingsToSongs:
                    self.specialRatingsToSongs[keyForDict] = [songInfo]
                else:
                    self.specialRatingsToSongs[keyForDict].append(songInfo)
        except:
            judgeNotesLogger.warning("getSpecialRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                                 str(sys.exc_info()[1])))
        
    def printRatingsToSongs(self):
        """
        Print out the songs that fell under the parsed ratings.

        Each dictionary entry in ratingsToSongs looks like this:
        'rating':[[TITLE,ARTIST,STEPARTIST],[TITLE,ARTIST,STEPARTIST],...]
        """
        judgeNotesLogger.info("printRatingsToSongs: Printing songs for each rating parsed")
        try:

            # Print out normal ratings first.
            sortedRatings = sorted(self.ratingsToSongs.keys(), key=float)
            for rating in sortedRatings:
                print("")  # For neater printing. Newline still occurs here
                songsInRating = self.ratingsToSongs[rating]
                print("["+str(rating)+"/10]")
                for song in songsInRating:
                    if song[2] != "":
                        print("-->", song[0], "{"+song[1]+"}", "("+song[2]+")")
                    else:
                        print("-->", song[0], "{"+song[1]+"}")

            # Print out special ratings after.
            sortedRatings = sorted(self.specialRatingsToSongs.keys(), key=str.lower)
            for rating in sortedRatings:
                print("")  # For neater printing. Newline still occurs here
                songsInRating = self.specialRatingsToSongs[rating]
                print("["+str(rating)+"]")
                for song in songsInRating:
                    if song[2] != "":
                        print("-->", song[0], "{"+song[1]+"}", "("+song[2]+")")
                    else:
                        print("-->", song[0], "{"+song[1]+"}")
                    
            print("")  # For neater printing. Newline still occurs here
        except:
            judgeNotesLogger.warning("printRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                            str(sys.exc_info()[1])))

    def writeRawRatings(self):
        """
        Write out number of songs that got each rating parsed.
        """
        judgeNotesLogger.info("writeRawRatings: Writing file containing songs for each rating")
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
                outFile.write("TOTAL:"+str(round(ratingSum, 1))+"\n")
                outFile.write("JUDGEDFILES:"+str(self.numJudgedFiles)+"\n")
                outFile.write("SPECIALFILES:"+str(self.numSpecialFiles)+"\n")
                outFile.write("TOTALFILES:"+str(self.numTotalFiles)+"\n")
                outFile.write("AVERAGE:"+str(round(self.average, 2))+"\n")
            outFile.close()
            judgeNotesLogger.info("writeRawRatings: Successfully wrote file '%s'", fileName)
        except:
            judgeNotesLogger.warning("writeRawRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

    def writeRatingsToSongs(self):
        """
        Write out songs for each rating out to file.
        """
        judgeNotesLogger.info("writeRatingsToSongs: Writing file containing songs for each rating")
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
            judgeNotesLogger.info("writeRatingsToSongs: Successfully wrote file '%s'", fileName)
        except:
            judgeNotesLogger.warning("writeRatingsToSongs: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                            str(sys.exc_info()[1])))


class JudgesForExcel():
    """
    * CLASS ATTRIBUTES *
    - path: Full file path to the set.
    - setName: Name of the set.
    - setNumber: The Set Number of the Batch Group.
    - notesFiles: List of Judge Notes filenames.
    - judgeNames: List of Judges that did this set.
    - judgeToFileName: Dictionary with <judgeName>:<judgeNotesFile> mappings
    - setSongs: List of tuples in the format (<songTitle>,<stepArtist>)
                This is also an ordered list so it's easy to use with judgeToRating
    - judgeToRating: Dictionary with entries of the format <judgeName>:<listOfRatings>
                    Since setSongs is ordered the same as listOfRatings,
                    nothing complex has to be done here

    * FUNCTIONS *
    - __str__():
    """

    def __init__(self, notesDir):
        """
        Constructor
        """
        self.path = notesDir
        self.setName = str(os.path.basename(os.path.normpath(self.path)).strip())
        self.setNumber = "0"
        self.setCSV = "judgments_" + self.setName + ".csv"
        self.notesFiles = []
        self.judgeNames = []
        self.judgeToFileName = {}
        self.setSongs = []
        self.judgeToRating = {}

        # Rating information stuff

    def __str__(self):
        return """>>> JUDGE TO EXCEL INFORMATION
- NOTES PATH: {}
- NOTES SET NAME: {}
- NOTES FILES: {}
- JUDGE NAMES: {}""" \
        .format(self.path, self.setName, self.notesFiles, self.judgeNames)

    def getSetNumber(self):
        judgesExcelLogger.info("getSetNumber: Retrieving Set Number")
        try:
            setNumSearch = re.search(".*([\d]+)$", self.setName)
            if setNumSearch is not None:
                self.setNumber = setNumSearch.group(1)
                judgesExcelLogger.debug("getSetNumber: Set Number is '%s'", self.setNumber)
            else:
                judgesExcelLogger.warning("getSetNumber: Set Name is not in correct format")
        except:
            judgesExcelLogger.warning("getSetNumber: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def getJudgeName(self, notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Notes_MayBatch.txt
        File must be in format of <JudgeName>_Notes -- anything else can come after
        """
        judgesExcelLogger.info("getJudgeName: Retrieving Judge Name from Notes File '%s'", notesFileName)
        try:
            judgeParse = re.search("^(.*)_Notes", notesFileName)
            if judgeParse is not None:
                judgeName = str(judgeParse.group(1))
                self.judgeNames.append(judgeName)
                self.judgeToFileName[judgeName] = notesFileName # Record judge to file name mapping
                judgesExcelLogger.info("getJudgeName: Judge is '%s'", judgeName)
            else:
                judgesExcelLogger.warning("getJudgeName: Judge Notes File is not in correct format")
        except:
            judgesExcelLogger.warning("getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def getAllJudgesInSet(self):
        """
        Goes through every judge notes file in the set folder specified.
        getJudgeName gets the judge name from each and maps the judge.
        """
        judgesExcelLogger.info("getAllJudgesInSet: Retrieving all judges in Set")
        try:
            os.chdir(self.path)
            for judgeNotesFile in self.notesFiles:
                self.getJudgeName(judgeNotesFile)  # getJudgeName also appends to judge name list
        except:
            judgesExcelLogger.warning("getAllJudgesInSet: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1])))

    def printJudgeNames(self):
        judgesExcelLogger.info("printJudgeNames:\n" + str(self.judgeNames))

    def getSetFileListing(self):
        judgesExcelLogger.info("getSetFileListing: Attempting to get list of judge notes files "
                               "for this set '%s'", self.path)
        try:
            self.notesFiles = os.listdir(self.path)
        except:
            judgesExcelLogger.warning("getSetFileListing: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1])))

    def printSetFileListing(self):
        judgesExcelLogger.info("printSetFileListing:\n" + str(self.notesFiles))

    ########################################################
    # We are just getting order song list from template here
    ########################################################

    def getSongWithStepartist(self,ratingLine):
        """
        Parses Song Title from a rating line in the judge notes file.
        Note song artist will exist in submitted notes for all files,
        so the ratingNoStepartist case does not have to be considered here.
        """
        
        try:
            ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$", ratingLine)
            otherRatingStepartist = re.search("^\[(.*)\](.*)\{(.*)\}[\s]*\((.*)\)$", ratingLine)

            # Retrieve song information from line.
            if ratingStepartist is not None:
                songTitle = ratingStepartist.group(2).strip()
                stepper = ratingStepartist.group(4).strip()
                tupleToAdd = (songTitle, stepper)
                judgesExcelLogger.debug("getSongWithStepartist: Found Song Title '%s'", songTitle)
                self.setSongs.append(tupleToAdd)  # Song Title with Stepartist, Tuple
            elif otherRatingStepartist is not None:
                songTitle = otherRatingStepartist.group(2).strip()
                stepper = otherRatingStepartist.group(4).strip()
                tupleToAdd = (songTitle, stepper)
                judgesExcelLogger.debug("getSongWithStepartist: Found Song Title '%s'", songTitle)
                self.setSongs.append(tupleToAdd)  # Song Title with Stepartist, Tuple
        except:
            judgesExcelLogger.warning("getSongTitle: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def getOrderedSongList(self):
        """
        Since all the judges should be using templates, all the song
        names should be in order honestly. Just go with first one
        """
        judgesExcelLogger.info("getOrderedSongList: Attempting to get ordered song list "
                               "of set '%s'", self.setName)
        try:
            os.chdir(self.path) # Change to set's directory context
            with open(self.notesFiles[0]) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        self.getSongWithStepartist(line)
            judgeFile.close()
        except:
            judgesExcelLogger.warning("getOrderedSongList: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                            str(sys.exc_info()[1])))
        
    def getSimpleRating(self,ratingLine):
        """
        This only returns a parsed rating.
        """

        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$", ratingLine)
        passRating = re.search("^\[(PASS).*\]", ratingLine)
        plus = re.search("^\[(\+\+).*\]", ratingLine)
        negative = re.search("^\[(--).*\]", ratingLine)
        bang = re.search("^\[(!).*\]", ratingLine)
        star = re.search("^\[(\*).*\]", ratingLine)
        pound = re.search("^\[(#).*\]", ratingLine)
        arrow = re.search("^\[(<).*\]", ratingLine)
        dollar = re.search("^\[(\$).*\]", ratingLine)

        try:
            # Retrieve song information from line.
            if ratingStepartist is not None:
                rating = str(ratingStepartist.group(1))  # Rating number itself
                return rating
            elif passRating is not None:
                return passRating.group(1).strip()
            elif plus is not None:
                return "10"  # A '++' is a 10/10
            elif negative is not None:
                return "0"  # A '--' is a 0/10
            elif bang is not None:
                return "0"  # A '!' is a 0/10
            elif star is not None:
                return star.group(1).strip()
            elif pound is not None:
                return pound.group(1).strip()
            elif arrow is not None:
                return arrow.group(1).strip()
            elif dollar is not None:
                return dollar.group(1).strip()
        except:
            judgesExcelLogger.warning("getSimpleRating: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    def getRatingsFromJudge(self, judge):
        """
        judge is the name of the judge in question. This is used
        as a lookup to find the judge's notes file.

        Goes through a judge's file, parses the ratings, and
        saves it into judgeToRating. A list of ratings is saved
        as the value, the judge's name is the key.
        """

        judgesExcelLogger.info("getRatingsFromJudge: Attempting to get ratings from Judge '%s'", judge)
        try:
            fileToUse = self.judgeToFileName[judge]
            os.chdir(self.path)  # Change to set's directory context
            judgeRatings = []
            with open(fileToUse) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        parsedRating = self.getSimpleRating(line)
                        judgeRatings.append(parsedRating)
            judgeFile.close()
            # print(judgeRatings)
            return judgeRatings
        except:
            judgesExcelLogger.warning("getRatingsFromJudge: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))

    def getAllJudgeRatings(self):
        """
        Retrieves the ratings from each judge in the set.
        """

        judgesExcelLogger.info("getAllJudgeRatings: Attempting to get ratings from all judges "
                          "for set '%s'", self.setName)
        try:
            for judgeName in self.judgeNames:
                self.judgeToRating[judgeName] = self.getRatingsFromJudge(judgeName)
        except:
            judgesExcelLogger.warning("getAllJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                            str(sys.exc_info()[1])))

    def createRatingCSV(self):
        """
        Create a CSV file with the judge ratings and song names in order.
        """

        judgesExcelLogger.info("createRatingCSV: Generating CSV file of ratings")
        try:
            os.chdir(self.path)  # Change to set's directory context

            # Set up the header
            header = "Song,Stepartist,Set"
            for judgeName in self.judgeNames:
                header += "," + judgeName
            header += ",supp"
            # print(header)

            with open(self.setCSV, 'w') as setRatings:
                setRatings.write(header+"\n")
                # Set up the judges for printing out. Remember this has tuples
                songcounter = 0
                for song in self.setSongs:
                    lineToWrite = song[0] + "," + song[1] + "," + self.setNumber
                    for judgeName in self.judgeNames:
                        lineToWrite += "," + (self.judgeToRating[judgeName])[songcounter]
                    setRatings.write(lineToWrite+"\n")
                    songcounter += 1
            setRatings.close()
            judgesExcelLogger.info("createRatingCSV: Successfully wrote CSV File '%s'", self.setCSV)
        except:
            judgesExcelLogger.warning("createRatingCSV: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

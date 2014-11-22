#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import re
import sys

# CLASS DEFINITION
class JudgesForExcel(object):
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
    - dumpInfo():
    """

    def __init__(self, notesDir):
        """
        Constructor
        """
        self.path = notesDir
        self.setName = os.path.basename(os.path.normpath(self.path)).strip()
        self.setNumber = "0"
        self.setCSV = "judgments_" + self.setName + ".csv"
        self.notesFiles = []
        self.judgeNames = []
        self.judgeToFileName = {}
        self.setSongs = []
        self.judgeToRating = {}

        # Rating information stuff
        
        
    def dumpInfo(self):
        print(logMsg("JUDGETOEXCEL","INFO"),"dumpInfo: Dumping Judge Notes Info")
        print("- NOTES PATH:", self.path,
              "\n- NOTES SET NAME:", self.setName,
              "\n- NOTES FILES:", self.notesFiles,
              "\n- JUDGE NAMES:", self.judgeNames)

    def getSetNumber(self):
        print(logMsg("JUDGETOEXCEL","INFO"),"getSetNumber: Retrieving Set Number")
        try:
            setNumSearch = re.search(".*([\d]+)$",self.setName)
            if setNumSearch != None:
                self.setNumber = setNumSearch.group(1)
                print(logMsg("JUDGETOEXCEL","INFO"),"getSetNumber: Set Number is '" + self.setNumber + "'")
            else:
                print(logMsg("JUDGETOEXCEL","WARNING"),"getSetNumber: Set Name is not in correct format")
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getSetNumber: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getJudgeName(self,notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Notes_MayBatch.txt
        File must be in format of <JudgeName>_Notes -- anything else can come after
        """
        print(logMsg("JUDGETOEXCEL","INFO"),"getJudgeName: Retrieving Judge Name from Notes File '" + notesFileName + "'")
        try:
            judgeParse = re.search("^(.*)_Notes",notesFileName)
            if judgeParse != None:
                judgeName = str(judgeParse.group(1))
                self.judgeNames.append( judgeName )
                self.judgeToFileName[judgeName] = notesFileName # Record judge to file name mapping
                print(logMsg("JUDGETOEXCEL","INFO"),"getJudgeName: Judge is '" + judgeName + "'")
            else:
                print(logMsg("JUDGETOEXCEL","WARNING"),"getJudgeName: Judge Notes File is not in correct format")
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getAllJudgesInSet(self):
        """
        Goes through every judge notes file in the set folder specified.
        getJudgeName gets the judge name from each and maps the judge.
        """
        print(logMsg("JUDGETOEXCEL","INFO"),"getAllJudgesInSet: Retrieving all judges in Set")
        try:
            os.chdir(self.path)
            for judgeNotesFile in self.notesFiles:
                self.getJudgeName(judgeNotesFile) # getJudgeName also appends to judge name list
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getAllJudgesInSet: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def printJudgeNames(self):
        print(logMsg("JUDGETOEXCEL","INFO"), "printJudgeNames:\n" + str(self.judgeNames))

    def getSetFileListing(self):
        print(logMsg("JUDGETOEXCEL","INFO"),"getSetFileListing: Attempting to get list of judge notes files for this set '" + self.path + "'")
        try:
            self.notesFiles = os.listdir(self.path)
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getSetFileListing: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def printSetFileListing(self):
        print(logMsg("JUDGETOEXCEL","INFO"), "printSetFileListing:\n" + str(self.notesFiles))

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
            ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)
            otherRatingStepartist = re.search("^\[(.*)\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)

            # Retrieve song information from line.
            if ratingStepartist != None:
                songTitle = ratingStepartist.group(2).strip()
                stepper = ratingStepartist.group(4).strip()
                tupleToAdd = (songTitle,stepper)
                print(logMsg("JUDGETOEXCEL","INFO"),"getSongWithStepartist: Found Song Title '" + songTitle + "'")
                self.setSongs.append(tupleToAdd) # Song Title with Stepartist, Tuple
            elif otherRatingStepartist != None:
                songTitle = otherRatingStepartist.group(2).strip()
                stepper = otherRatingStepartist.group(4).strip()
                tupleToAdd = (songTitle,stepper)
                print(logMsg("JUDGETOEXCEL","INFO"),"getSongWithStepartist: Found Song Title '" + songTitle + "'")
                self.setSongs.append(tupleToAdd) # Song Title with Stepartist, Tuple
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getSongTitle: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))


    def getOrderedSongList(self):
        """
        Since all the judges should be using templates, all the song
        names should be in order honestly. Just go with first one
        """
        print(logMsg("JUDGETOEXCEL","INFO"),"getOrderedSongList: Attempting to get ordered song list of set '" + self.setName + "'")
        try:
            os.chdir(self.path) # Change to set's directory context
            with open(self.notesFiles[0]) as judgeFile:
                for line in judgeFile:
                    if line.startswith('['):
                        self.getSongWithStepartist(line)
            judgeFile.close()
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getOrderedSongList: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        
    def getSimpleRating(self,ratingLine):
        """
        This only returns a parsed rating.
        """

        ratingStepartist = re.search("^\[([\d]+\.?[\d]?)/10\](.*)\{(.*)\}[\s]*\((.*)\)$",ratingLine)
        passRating = re.search("^\[(PASS).*\]",ratingLine)
        plus = re.search("^\[(\+\+).*\]",ratingLine)
        negative = re.search("^\[(--).*\]",ratingLine)
        bang = re.search("^\[(!).*\]",ratingLine)
        star = re.search("^\[(\*).*\]",ratingLine)
        pound = re.search("^\[(\#).*\]",ratingLine)
        arrow = re.search("^\[(\<).*\]",ratingLine)
        dollar = re.search("^\[(\$).*\]",ratingLine)
        songInfo = []
        rating = 0

        try:
            # Retrieve song information from line.
            if ratingStepartist != None:
                rating = str(ratingStepartist.group(1)) # Rating number itself
                return rating
            elif passRating != None:
                return passRating.group(1).strip()
            elif plus != None:
                return "10" # A '++' is a 10/10
            elif negative != None:
                return "0" # A '--' is a 0/10
            elif bang != None:
                return "0" # A '!' is a 0/10
            elif star != None:
                return star.group(1).strip()
            elif pound != None:
                return pound.group(1).strip()
            elif arrow != None:
                return arrow.group(1).strip()
            elif dollar != None:
                return dollar.group(1).strip() 

        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getSimpleRating: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    

    def getRatingsFromJudge(self,judge):
        """
        judge is the name of the judge in question. This is used
        as a lookup to find the judge's notes file.

        Goes through a judge's file, parses the ratings, and
        saves it into judgeToRating. A list of ratings is saved
        as the value, the judge's name is the key.
        """

        print(logMsg("JUDGETOEXCEL","INFO"),"getRatingsFromJudge: Attempting to get ratings from Judge '" + judge + "'")
        try:
            fileToUse = self.judgeToFileName[judge]
            os.chdir(self.path) # Change to set's directory context
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
            print(logMsg("JUDGETOEXCEL","ERROR"), "getRatingsFromJudge: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))    

    def getAllJudgeRatings(self):
        """
        Retrieves the ratings from each judge in the set.
        """

        print(logMsg("JUDGETOEXCEL","INFO"),"getAllJudgeRatings: Attempting to get ratings from all judges for set '" + self.setName + "'")
        try:
            for judgeName in self.judgeNames:
                self.judgeToRating[judgeName] = self.getRatingsFromJudge(judgeName)
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "getAllJudgeRatings: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def createRatingCSV(self):
        """
        Create a CSV file with the judge ratings and song names in order.
        """

        print(logMsg("JUDGETOEXCEL","INFO"),"createRatingCSV: Generating CSV file of ratings")
        try:
            os.chdir(self.path) # Change to set's directory context

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
                        lineToWrite += "," + ( self.judgeToRating[judgeName] )[songcounter]
                    setRatings.write(lineToWrite+"\n")
                    songcounter += 1
            setRatings.close()
            print(logMsg("BATCH","INFO"),"createRatingCSV: Successfully wrote CSV File '" + self.setCSV + "'")
        except:
            print(logMsg("JUDGETOEXCEL","ERROR"), "createRatingCSV: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))


# MAIN
# Use C:\pythoncode\batchApis\tests\sets\set1
if __name__ == "__main__":

    print("judgetoexcel.py is used to make a .csv file that contains judge ratings (judgments_<setname>.csv)")
    print("It is assumed you have already ran artistfornotes.py to add in the stepartists (the files had _steppers appended to the file name). If you are specifying a set directory with judge notes that don't have the stepartists in them, you will get unexpected behavior.")
    notesDirPath = (input("Input full path of Set directory with Judge Notes: ")).strip()
    judgeSet = JudgesForExcel(notesDirPath)
    judgeSet.dumpInfo()

    # Get Judge Notes Files First along with Set Number
    judgeSet.getSetFileListing()
    judgeSet.printSetFileListing()
    judgeSet.getSetNumber()

    # Get Judge Names
    judgeSet.getAllJudgesInSet()
    judgeSet.printJudgeNames()

    # Parse ordered song list from judge notes.
    judgeSet.getOrderedSongList()

    # Now get all the judge ratings
    judgeSet.getAllJudgeRatings()

    # Test printing out CSV file
    judgeSet.createRatingCSV()

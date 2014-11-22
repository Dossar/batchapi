#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import re
import sys
from notestemplate import *

class ArtistForNotes(NotesTemplate):
    """
    This class uses the .csv file generated from batch.py as an
    ordered list of stepartists to add to the judge notes files.

    Inherits from NotesTemplate, so no init statement here.
    Noteable attributes for this application:

    - listOfSteppers: Ordered list of stepartists from CSV file.
    - judgeFiles: List of judge files to append stepartist to.
    """

    def setOutputFile(self):
        return 

    def getAllSteppers(self):
        """
        Retrieve ordered list of song artists from CSV file.
        """
        
        print(logMsg("ARTISTFORNOTES","INFO"),"getAllSteppers: Retrieving ordered list of stepartists from CSV File")
        try:
            stepperList = []
            with open(self.csvFile) as fileCSV:
                for line in fileCSV:
                    if line.startswith('[FOLDER]'):
                        continue
                    lineValues = line.split(",") # CSV file separates fields by commas
                    stepArtist = lineValues[self.stepperIndex].strip()
                    stepperList.append(stepArtist)
            fileCSV.close()
            self.listOfSteppers = stepperList
        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "getAllSteppers: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getJudgeFilesForAdd(self):
        """
        Get all judge notes filenames in set directory. This is assuming
        the judge notes files do not have any stepartists added to them
        yet.
        """
        print(logMsg("ARTISTFORNOTES","INFO"),"getJudgeFilesForAdd: Determining Judge Files to add stepartist to")
        try:
            notesFiles = []
            allFiles = os.listdir(self.fileDir) # Retrieve a list of files from the set directory
            for file in allFiles:
                if file.endswith(".txt"):
                    notesFiles.append(file)
            self.judgeFiles = notesFiles

        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "getJudgeFilesForAdd: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        
    def getJudgeName(self,notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Notes_MayBatch.txt
        File must be in format of <JudgeName>_Notes -- anything else can come after
        """
        print(logMsg("ARTISTFORNOTES","INFO"),"getJudgeName: Retrieving Judge Name from Notes File '" + notesFileName + "'")
        try:
            judgeParse = re.search("^(.*)_Notes",notesFileName)
            if judgeParse != None:
                judgeName = str(judgeParse.group(1))
                self.judgeNames.append( judgeName )
                self.judgeToFileName[judgeName] = notesFileName # Record judge to file name mapping
                print(logMsg("ARTISTFORNOTES","INFO"),"getJudgeName: Judge is '" + judgeName + "'")
            else:
                print(logMsg("ARTISTFORNOTES","WARNING"),"getJudgeName: Judge Notes File is not in correct format")
        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def getAllJudgesInSet(self):
        """
        Goes through every judge notes file in the set folder specified.
        getJudgeName gets the judge name from each and maps the judge.
        """
        print(logMsg("ARTISTFORNOTES","INFO"),"getAllJudgesInSet: Retrieving all judges in Set")
        try:
            self.judgeNames = []
            self.judgeToFileName = {}
            os.chdir(self.fileDir)
            for judgeNotesFile in self.judgeFiles:
                self.getJudgeName(judgeNotesFile) # getJudgeName also appends to judge name list
        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "getAllJudgesInSet: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def addStepArtistToLine(self,ratingLine,fileIndex):

        try:
            ratingNoStepartist = re.search(".*\{(.*)\}$",ratingLine)
            if ratingNoStepartist != None:
                ratingLine += " (" + self.listOfSteppers[fileIndex] + ")"
                return ratingLine
            else:
                return ratingLine
        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "addStepArtistToLine: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def addSteppersToFile(self):

        print(logMsg("ARTISTFORNOTES","INFO"),"addSteppersToFile: Writing new files with stepartists added to Notes.")
        try:
            os.chdir(self.fileDir)
            for judgeNotesFile in self.judgeFiles:
                outFile = (judgeNotesFile.split(".txt")[0]) + "_steppers.txt"
                print(logMsg("ARTISTFORNOTES","INFO"),"addSteppersToFile: Writing new file '" + outFile + "'")
                with open(outFile, 'w') as stepperAddedFile:
                    fileCounter = 0 # Needed for ordered list of stepartists
                    with open(judgeNotesFile) as judgeFile:
                        for line in judgeFile:
                            if line.startswith('['):
                                lineToReplace = self.addStepArtistToLine(line.strip(),fileCounter)
                                stepperAddedFile.write(lineToReplace+"\n")
                                fileCounter += 1
                            else:
                                stepperAddedFile.write(line)
        except:
            print(logMsg("ARTISTFORNOTES","ERROR"), "addSteppersToFile: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))


# MAIN
# This is used to simply append the stepartist to the song information lines in a judge notes file.
if __name__ == "__main__":

    # Create Template Object.
    print("artistfornotes.py is used to add stepartists to judge notes files in a set. This is done after judges have passed in their notes.")
    print("It is assumed you have already placed all the judge notes for the set and the .csv file from batch.py in the same directory.")
    inputCSV = (input("Input Full Path to .csv File generated from batch.py: ")).strip()
    searchList = ['STEPARTIST'] # Same song title and same song artist for comparison
    artistAdd = ArtistForNotes(inputCSV,searchList)
    artistAdd.dumpInfo()

    # Get relevant fields from CSV file from batch.py
    artistAdd.getFieldIndices()
    artistAdd.getRelevantFields()

    # Obtain judge file information and set output file
    artistAdd.getJudgeFilesForAdd()
    artistAdd.getAllJudgesInSet()

    # Now add the stepartist to each judge file.
    artistAdd.getAllSteppers()
    artistAdd.addSteppersToFile()

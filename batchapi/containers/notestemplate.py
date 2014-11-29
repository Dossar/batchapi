#!/usr/bin/python3

"""
There are two classes defined here:
- NotesTemplate
- ArtistForNotes

NotesTemplate is used for creating the judge notes file template.
ArtistForNotes is used for adding stepartists to judge notes files.
"""

import re
import os
import sys

###########
# LOGGERS #
###########

# Date formatting will be the same for all loggers
import logging
dateformatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s')

# Make notesTemplateLogger logger object.
notesTemplateLogger = logging.getLogger("NOTESTEMPLATE")
notesTemplateLogger.setLevel(logging.DEBUG)
notesTemplateFileH = logging.FileHandler('/tmp/notesTemplate.log')
notesTemplateFileH.setLevel(logging.DEBUG)
notesTemplateConsoleH = logging.StreamHandler()
notesTemplateConsoleH.setLevel(logging.WARNING)
notesTemplateFileH.setFormatter(dateformatter)
notesTemplateConsoleH.setFormatter(dateformatter)
notesTemplateLogger.addHandler(notesTemplateFileH)  # File Handler add
notesTemplateLogger.addHandler(notesTemplateConsoleH)  # Console Handler add

# Make artistToNotesLogger logger object.
artistToNotesLogger = logging.getLogger("ARTISTFORNOTES")
artistToNotesLogger.setLevel(logging.DEBUG)
artistToNotesFileH = logging.FileHandler('/tmp/artistToNotes.log')
artistToNotesFileH.setLevel(logging.DEBUG)
artistToNotesConsoleH = logging.StreamHandler()
artistToNotesConsoleH.setLevel(logging.WARNING)
artistToNotesFileH.setFormatter(dateformatter)
artistToNotesConsoleH.setFormatter(dateformatter)
artistToNotesLogger.addHandler(artistToNotesFileH)  # File Handler add
artistToNotesLogger.addHandler(artistToNotesConsoleH)  # Console Handler add

#####################
# CLASS DEFINITIONS #
#####################

class NotesTemplate():
    """
    This class is used for creating a template judge notes file.
    It takes a CSV file generated from batch.py and then
    creates the template from there.

    * CLASS ATTRIBUTES *
    - path: Absolute file path to the CSV file.
    - fileDir: Directory of the CSV file.
    - batchName: Name of the batch, extracted from the CSV file.
    - outputFile: Name of template file to write.
    - searchFields: Relevant fields to use to check for multiple submissions on a file.
                    For me this criteria is same song title and song artist.
    - fieldToIndex: Dictionary with a 'field':index mapping
    - relevantFields: List storing integers indicating indices of relevant fields.
    - titleIndex: Column position index of song title in CSV file.
    - stepperIndex: Column position index of stepartist in CSV file.
    - artistIndex: Column position index of song artist in CSV file.

    * FUNCTIONS *
    - dumpInfo(): Prints out information about currently referenced NotesTemplate Object
    """

    def __init__(self, csvPath, searchList):
        """
        Constructor
        """
        self.path = csvPath
        self.fileDir = os.path.abspath(os.path.join(os.path.dirname(self.path), '.'))
        self.csvFile = os.path.basename(os.path.normpath(self.path))
        self.batchName = str((os.path.basename(os.path.normpath(self.path))).split(".csv")[0])
        self.outputFile = "template_" + self.batchName + ".txt"
        self.searchFields = searchList
        self.fieldToIndex = {}
        self.relevantFields = []
        self.titleIndex = 0
        self.stepperIndex = 0
        self.artistIndex = 0

    def __str__(self):
        return """>>> NOTES TEMPLATE INFORMATION
- CSV FILE PATH: {}
- CSV FILE DIR: {}
- CSV FILE NAME: {}
- BATCH NAME: {}
- OUTPUT FILE: {}
- COMPARISON FIELDS: {}
- TITLE INDEX: {}
- STEPARTIST INDEX: {}
- SONG ARTIST INDEX: {}""" \
        .format(self.path, self.fileDir, self.csvFile, self.batchName, self.outputFile, self.searchFields,
                self.titleIndex, self.stepperIndex, self.artistIndex)

    def getFieldIndices(self):
        """
        When looking through the CSV, we went to know what index the field is in.
        Since the CSV file has a consistent row/column format, the index of
        the specified fields will be useful to know. Saves a dictionary with
        'field':index mappings, where index is an integer.

        This is just for the line with the columns in the file. These columns
        might contain some other fields we aren't interested in, so getRelevantFields
        will be used after this to get indices of fields we actually want.
        """

        notesTemplateLogger.info("getFieldIndices: Parsing CSV File's Column Header to get field indices")
        try:
            os.chdir(self.fileDir)  # Change to csv file directory context
            with open(self.csvFile) as fileCSV:
                for line in fileCSV:
                    if line.startswith('[FOLDER]'):
                        break
            fileCSV.close()
            rawFieldList = line.strip().split(",")
            counter = 0  # Fields start at index 0
            for field in rawFieldList:
                rawField = field.strip("[]\s")
                self.fieldToIndex[rawField] = counter
                counter += 1  # Indicate the index for the next field
        except:
            notesTemplateLogger.warning("getFieldIndices: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                           str(sys.exc_info()[1])))

    def getRelevantFields(self):
        """
        Get relevant indices for the fields we're searching for.
        This is done after getFieldIndices builds the dictionary
        with the 'field':index mappings.
        """

        notesTemplateLogger.info("getRelevantFields: Getting Indices of Relevant Comparison Fields")
        try:
            for searchField in self.searchFields:
                index = self.fieldToIndex[searchField]
                self.relevantFields.append(index)
                if searchField == 'TITLE':
                    self.titleIndex = self.fieldToIndex[searchField]
                if searchField == 'STEPARTIST':
                    self.stepperIndex = self.fieldToIndex[searchField]
                if searchField == 'ARTIST':
                    self.artistIndex = self.fieldToIndex[searchField]
        except:
            notesTemplateLogger.warning("getRelevantFields: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))

    def printTemplate(self):
        """
        Test that I can parse through the CSV file correctly
        for making the template notes file.

        Use the list generated from getRelevantFields to retrieve
        what I need for formatting song headers.

        NOTE: Considering that submissions can contain slightly
        different song titles or song artist fields, comparing
        song titles and song artist fields opens a new can of worms.
        So just manually add any stepartists into the template file
        if the song name and song artist look similar enough.
        """

        notesTemplateLogger.info("printTemplate: Testing parsing for writing file")
        try:
            os.chdir(self.fileDir)  # Change to csv file directory context
            with open(self.csvFile) as fileCSV:
                print("")
                for line in fileCSV:
                    if line.startswith('[FOLDER]'):
                        continue
                    lineValues = line.split(",")  # CSV file separates fields by commas
                    songTitle = lineValues[self.titleIndex].strip()
                    songArtist = lineValues[self.artistIndex].strip()
                    stepArtist = lineValues[self.stepperIndex].strip()
                    if songTitle == "":
                        songTitle = lineValues[0].strip()  # First CSV column is ALWAYS folder name
                    if songArtist == "":
                        songArtist = "UNKNOWN"  # this is a way of indicating files where artist names weren't parsed
                    stringToPrint = "[/10] " + songTitle + " {" + songArtist + "}\n-\n-\n"
                    print(stringToPrint)
            fileCSV.close()
        except:
            notesTemplateLogger.warning("printTemplate: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    def writeTemplateFile(self):
        """
        Basically printTemplate except this is used to actually write out
        the judge notes template file. printTemplate is used for testing.
        """

        notesTemplateLogger.info("writeTemplateFile: Writing Template File '%s'", self.outputFile)
        try:
            os.chdir(self.fileDir)  # Change to csv file directory context
            with open(self.outputFile, 'w') as template:
                with open(self.csvFile) as fileCSV:
                    for line in fileCSV:
                        if line.startswith('[FOLDER]'):
                            continue
                        lineValues = line.split(",")  # CSV file separates fields by commas
                        songTitle = lineValues[self.titleIndex].strip()
                        songArtist = lineValues[self.artistIndex].strip()
                        stepArtist = lineValues[self.stepperIndex].strip()
                        if songTitle == "":
                            songTitle = lineValues[0].strip()  # First CSV column is ALWAYS folder name
                        if songArtist == "":
                            songArtist = "UNKNOWN"  # this is a way of indicating files where artist names weren't parsed
                        lineToWrite = "[/10] " + songTitle + " {" + songArtist + "}\n-\n-\n\n"
                        template.write(lineToWrite)
            fileCSV.close()
            template.close()
            notesTemplateLogger.info("writeTemplateFile: Successfully wrote file '%s'", self.outputFile)

        except:
            notesTemplateLogger.warning("writeTemplateFile: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))



class ArtistForNotes(NotesTemplate):
    """
    This class uses the .csv file generated from batch.py as an
    ordered list of stepartists to add to the judge notes files.

    Inherits from NotesTemplate, so no init statement here.
    Notable attributes for this application:

    - listOfSteppers: Ordered list of stepartists from CSV file.
    - judgeFiles: List of judge files to append stepartist to.
    """

    def getAllSteppers(self):
        """
        Retrieve ordered list of song artists from CSV file.
        """

        artistToNotesLogger.info("getAllSteppers: Retrieving ordered list of stepartists from CSV File")
        try:
            stepperList = []
            with open(self.csvFile) as fileCSV:
                for line in fileCSV:
                    if line.startswith('[FOLDER]'):
                        continue
                    lineValues = line.split(",")  # CSV file separates fields by commas
                    stepArtist = lineValues[self.stepperIndex].strip()
                    stepperList.append(stepArtist)
            fileCSV.close()
            self.listOfSteppers = stepperList
        except:
            artistToNotesLogger.warning("getAllSteppers: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                          str(sys.exc_info()[1])))

    def getJudgeFilesForAdd(self):
        """
        Get all judge notes file names in set directory. This is assuming
        the judge notes files do not have any stepartists added to them
        yet.
        """
        artistToNotesLogger.info("getJudgeFilesForAdd: Determining Judge Files to add stepartist to")
        try:
            notesFiles = []
            allFiles = os.listdir(self.fileDir)  # Retrieve a list of files from the set directory
            for file in allFiles:
                if file.endswith(".txt"):
                    notesFiles.append(file)
            self.judgeFiles = notesFiles

        except:
            artistToNotesLogger.warning("getJudgeFilesForAdd: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                               str(sys.exc_info()[1])))
        
    def getJudgeName(self, notesFileName):
        """
        Parses judge name from input judge notes file.
        e.g DossarLX ODI from DossarLX ODI_Notes_MayBatch.txt
        File must be in format of <JudgeName>_Notes -- anything else can come after
        """
        artistToNotesLogger.info("getJudgeName: Retrieving Judge Name from Notes File '%s'",notesFileName)
        try:
            judgeParse = re.search("^(.*)_Notes", notesFileName)
            if judgeParse is not None:
                judgeName = str(judgeParse.group(1))
                self.judgeNames.append(judgeName)
                self.judgeToFileName[judgeName] = notesFileName  # Record judge to file name mapping
                artistToNotesLogger.info("getJudgeName: Judge is '%s'", judgeName)
            else:
                artistToNotesLogger.warning("getJudgeName: Judge Notes File is not in correct format")
        except:
            artistToNotesLogger.warning("getJudgeName: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

    def getAllJudgesInSet(self):
        """
        Goes through every judge notes file in the set folder specified.
        getJudgeName gets the judge name from each and maps the judge.
        """
        artistToNotesLogger.info("getAllJudgesInSet: Retrieving all Judges in Set")
        try:
            self.judgeNames = []
            self.judgeToFileName = {}
            os.chdir(self.fileDir)
            for judgeNotesFile in self.judgeFiles:
                self.getJudgeName(judgeNotesFile) # getJudgeName also appends to judge name list
        except:
            artistToNotesLogger.warning("getAllJudgesInSet: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))

    def addStepArtistToLine(self, ratingLine, fileIndex):

        try:
            ratingNoStepartist = re.search(".*\{(.*)\}$",ratingLine)
            if ratingNoStepartist is not None:
                ratingLine += " (" + self.listOfSteppers[fileIndex] + ")"
                return ratingLine
            else:
                return ratingLine
        except:
            artistToNotesLogger.warning("addStepArtistToLine: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                               str(sys.exc_info()[1])))

    def addSteppersToFile(self):

        artistToNotesLogger.info("addSteppersToFile: Writing new files with stepartists added to Notes.")
        try:
            os.chdir(self.fileDir)
            for judgeNotesFile in self.judgeFiles:
                outFile = (judgeNotesFile.split(".txt")[0]) + "_steppers.txt"
                artistToNotesLogger.info("addSteppersToFile: Writing New Judge File '%s'", outFile)
                with open(outFile, 'w') as stepperAddedFile:
                    fileCounter = 0  # Needed for ordered list of stepartists
                    with open(judgeNotesFile) as judgeFile:
                        for line in judgeFile:
                            if line.startswith('['):
                                lineToReplace = self.addStepArtistToLine(line.strip(), fileCounter)
                                stepperAddedFile.write(lineToReplace+"\n")
                                fileCounter += 1
                            else:
                                stepperAddedFile.write(line)
                judgeFile.close()
                stepperAddedFile.close()
            
        except:
            artistToNotesLogger.warning("addSteppersToFile: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                             str(sys.exc_info()[1])))


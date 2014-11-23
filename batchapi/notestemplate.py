#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import sys


# CLASS DEFINITION
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

    def dumpInfo(self):
        print(logMsg("NOTESTEMPLATE","INFO"),"dumpInfo: Dumping Batch Info")
        print("- CSV FILE PATH:", self.path,
              "\n- CSV FILE DIR:", self.fileDir,
              "\n- CSV FILE NAME:", self.csvFile,
              "\n- BATCH NAME:", self.batchName,
              "\n- OUTPUT FILE:", self.outputFile,
              "\n- COMPARISON FIELDS:", self.searchFields,
              "\n- TITLE INDEX:", self.titleIndex,
              "\n- STEPARTIST INDEX:", self.stepperIndex,
              "\n- SONG ARTIST INDEX:", self.artistIndex)

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

        print(logMsg("NOTESTEMPLATE", "INFO"), "getFieldIndices: Parsing CSV File's Column Header")
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
            print(logMsg("NOTESTEMPLATE", "ERROR"), "getFieldIndices: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                                       str(sys.exc_info()[1])))

    def getRelevantFields(self):
        """
        Get relevant indices for the fields we're searching for.
        This is done after getFieldIndices builds the dictionary
        with the 'field':index mappings.
        """

        print(logMsg("NOTESTEMPLATE", "INFO"), "getRelevantFields: Getting Indices of Relevant Comparison Fields")
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
            print(logMsg("NOTESTEMPLATE", "ERROR"), "getRelevantFields: {0}: {1}".format(sys.exc_info()[0].__name__,
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

        print(logMsg("NOTESTEMPLATE", "INFO"), "printTemplate: Testing parsing for writing file")
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
            print(logMsg("NOTESTEMPLATE", "ERROR"), "printTemplate: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                                     str(sys.exc_info()[1])))

    def writeTemplateFile(self):
        """
        Basically printTemplate except this is used to actually write out
        the judge notes template file. printTemplate is used for testing.
        """

        print(logMsg("NOTESTEMPLATE", "INFO"), "writeTemplateFile: Writing Template File '" + self.outputFile + "'")
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
            print(logMsg("NOTESTEMPLATE", "INFO"), "writeTemplateFile: Successfully wrote file '" + self.outputFile
                  + "'")
        except:
            print(logMsg("NOTESTEMPLATE", "ERROR"), "writeTemplateFile: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                                         str(sys.exc_info()[1])))

# MAIN
# Use C:\pythoncode\batchApis\suites\batch\batch.csv for testing.
if __name__ == "__main__":
    # Create Template Object.
    print("notestemplate.py is used to generate a template judge notes file from the .csv file generated in batch.py")
    print("It is assumed here you already have run batch.py to make this .csv file.")
    inputCSV = (input("Input Full Path to .csv File generated from batch.py: ")).strip()
    templateNotes.dumpInfo()
    searchList = ['ARTIST', 'TITLE', 'STEPARTIST']  # Same song title and same song artist for comparison
    templateNotes = NotesTemplate(inputCSV, searchList)

    templateNotes.getFieldIndices()
    templateNotes.getRelevantFields()
    templateNotes.dumpInfo()


    templateNotes.printTemplate()
    templateNotes.writeTemplateFile()
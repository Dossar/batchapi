#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import re
import sys

# CLASS DEFINITION
class Batch(object):
    """
    * CLASS ATTRIBUTES *
    - path: File path to the batch to search.
    - name: Name of the batch.
    - outputFile: Name of CSV file to write.
    - batchFiles: List of files in the batch directory being searched.
    - smFileFields: Fields to search for in an .sm file
    - dwiFileFields: Fields to search for in a .dwi file
    - songFolderInfo: Dictionary storing info for each song folder in the batch

    * FUNCTIONS *
    - dumpInfo(): Prints out information about the currently reference Batch Object
    - getBatchFileListing(): Get a file listing of the batch directory
    - setSmFileFields(): Sets list of fields to search for in an .sm file
    - setDwiFileFields(): Sets list of fields to search for in a .dwi file
    - parseChartFile(): Tries parsing fields specified for either a dwi or sm file.
    - getStepArtistFromFolder(): Parses stepartist from a passed folder (just name of folder itself). 
    - getSongInfo(): Retrieves song information for a specified folder in the batch directory.
    - parseSongs(): Goes through every folder in the batch directory to find song information.
    - printSongInfo(): Prints out any successfully parsed information.
    - clearBatchFiles(): Empties previous listing of batch directory file contents.
    - clearSongFolderInfo(): Empties any song information that was stored previously.
    - createCsvSongListing(): Writes a Comma-Separated-Values file of the song information.
    """
    
    def __init__(self, batchPath):
        """
        Constructor
        """
        self.path = batchPath
        self.name = os.path.basename(os.path.normpath(batchPath))
        self.outputFile = self.name + ".csv"
        self.batchFiles = []
        self.smFileFields = []
        self.dwiFileFields = []
        self.songFolderInfo = {}

    def dumpInfo(self):
        print(logMsg("BATCH","INFO"),"dumpInfo: Dumping Batch Info")
        print("- BATCH PATH:", self.path,
              "\n- BATCH NAME:", self.name,
              "\n- OUTPUT FILE:", self.outputFile,
              "\n- SM FIELDS:", self.smFileFields,
              "\n- DWI FIELDS:", self.dwiFileFields)

    def getBatchFileListing(self):
        print(logMsg("BATCH","INFO"),"getBatchFileListing: Attempting to get song listing in '" + self.path + "'")
        try:
            self.batchFiles = os.listdir(self.path)
        except:
            print(logMsg("BATCH","ERROR"), "getBatchFileListing: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def setSmFileFields(self,fieldList):
        self.smFileFields = fieldList

    def setDwiFileFields(self,fieldList):
        self.dwiFileFields = fieldList

    def parseChartFile(self,chartFolder,chartFile,chartType):
        """
        chartFolder is the full path to the folder.

        chartType should be one of:
        - sm
        - dwi

        Note that stepartists will be obtained from the folder name. Do not look
        inside the chart file for the stepartist.
        """
        print(logMsg("BATCH","INFO"),"parseChartFile: Attempting to parse chart file '" + chartFile + "'")
        os.chdir(chartFolder) # Change to song folder's context in the batch
        songFieldInfo = {}

        try:

            # group(1) here refers to the captured field.
            if chartType == "sm":
                with open(chartFile) as smFile:
                    for line in smFile:
                        if line.startswith('#'):
                            for field in self.smFileFields:
                                if field == "STEPARTIST":
                                    continue
                                else:
                                    fieldSearch = re.search("^#"+field+":(.*);$",line)
                                    if fieldSearch != None:
                                        songFieldInfo[field] = fieldSearch.group(1)
                        else:
                            break # No more hashtags means we're done with the song info at the top

            # group(1) here refers to the captured field.
            if chartType == "dwi":
                with open(chartFile) as dwiFile:
                    for line in dwiFile:
                        if line.startswith('#'):
                            for field in self.dwiFileFields:
                                if field == "STEPARTIST":
                                    continue
                                else:
                                    fieldSearch = re.search("^#"+field+":(.*);$",line)
                                    if fieldSearch != None:
                                        songFieldInfo[field] = fieldSearch.group(1)
                        else:
                            break # No more hashtags means we're done with the song info at the top
        except:
            print(logMsg("BATCH","ERROR"), "parseChartFile: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
            if 'TITLE' in self.smFileFields:
                # songFieldInfo['TITLE'] = os.path.basename(os.path.normpath(chartFolder))
                folderName = os.path.basename(os.path.normpath(chartFolder))
                songTitle = self.getSongTitleFromFolder(folderName)
                songFieldInfo['TITLE'] = songTitle
            if 'ARTIST' in self.smFileFields:
                songFieldInfo['ARTIST'] = ""
            
        # Get stepartist information after parsing any song information.
        if 'STEPARTIST' in self.smFileFields:
            folderName = os.path.basename(os.path.normpath(chartFolder))
            stepper = self.getStepArtistFromFolder(folderName)
            songFieldInfo['STEPARTIST'] = stepper

        return songFieldInfo # Dictionary of file fields

    def getSongTitleFromFolder(self,folder):
        """
        folder is the name of the folder by itself.
        """
        
        # group(1) here refers to the captured field. Parse stepartist from song folder.
        print(logMsg("BATCH","INFO"),"getSongTitleFromFolder: Retrieving song title from folder '" + folder + "'")
        stepArtist = ""
        try:
            parenthesesArtist = re.search("(.*)\[(.*)\]$",folder)
            bracketArtist = re.search("(.*)\((.*)\)$",folder)
            curlybraceArtist = re.search("(.*)\{(.*)\}$",folder)
            if parenthesesArtist != None:
                song = parenthesesArtist.group(1).strip() # Song Title with parentheses stepartist
            if bracketArtist != None:
                song = bracketArtist.group(1).strip() # Song Title with brackets stepartist
            if curlybraceArtist != None:
                song = curlybraceArtist.group(1).strip() # Song Title with brackets stepartist
        except:
            print(logMsg("BATCH","ERROR"), "getSongTitleFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

        return song
    
    def getStepArtistFromFolder(self,folder):
        """
        folder is the name of the folder by itself.
        """
        
        # group(1) here refers to the captured field. Parse stepartist from song folder.
        print(logMsg("BATCH","INFO"),"getStepArtistFromFolder: Retrieving stepartist from folder '" + folder + "'")
        stepArtist = ""
        try:
            parenthesesArtist = re.search(".*\[(.*)\]$",folder)
            bracketArtist = re.search(".*\((.*)\)$",folder)
            curlybraceArtist = re.search(".*\{(.*)\}$",folder)
            if parenthesesArtist != None:
                stepArtist = parenthesesArtist.group(1) # Stepartist with parentheses
            if bracketArtist != None:
                stepArtist = bracketArtist.group(1) # Stepartist with brackets
            if curlybraceArtist != None:
                stepArtist = curlybraceArtist.group(1) # Stepartist with brackets
        except:
            print(logMsg("BATCH","ERROR"), "getStepArtistFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

        return stepArtist

    def getSongInfo(self,songFolder):
        """
        songFolder is the name of the folder by itself. It will be turned into the full file path
        """
        
        os.chdir(self.path) # Change to batch directory context
        songFolderFiles = os.listdir(songFolder)
        for file in songFolderFiles:

            try:
                
                # smSearch.group(0) is the match that contains .sm file name
                smSearch = re.search("(.*\.sm)$",file)
                if smSearch != None:
                    songFolderPath = os.path.join(self.path, songFolder)
                    songInfo = self.parseChartFile(songFolderPath,file,"sm")
                    self.songFolderInfo[songFolder] = songInfo
                    continue

                # dwiSearch.group(0) is the match that contains .dwi file name
                dwiSearch = re.search("(.*\.dwi)$",file)
                if dwiSearch != None:
                    songFolderPath = os.path.join(self.path, songFolder)
                    songInfo = self.parseChartFile(songFolderPath,file,"dwi")
                    self.songFolderInfo[songFolder] = songInfo

            except:
                print(logMsg("BATCH","ERROR"), "getSongInfo: Something went wrong trying to parse through '" + songFolder + "'")
                print(logMsg("BATCH","ERROR"), "getSongInfo: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def parseSongs(self):
        """
        folder is the name of the folder by itself. It will be turned into the full file path
        However since not every file in the batch could be a folder, keep file cases in mind
        """
        if self.batchFiles != []:
            print(logMsg("BATCH","INFO"),"parseSongs: Looking through batch files")
            for folder in self.batchFiles:
                try:
                    self.getSongInfo(folder)
                except:
                    print(logMsg("BATCH","ERROR"), "parseSongs: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))

    def printSongInfo(self):
        """
        Prints any songs that were parsed.
        """
        print(logMsg("BATCH","INFO"),"printSongInfo: Printing out parsed songs")
        for folder in self.songFolderInfo.keys():
            print(folder,"-->",self.songFolderInfo[folder])

    def clearBatchFiles(self):
        self.batchFiles = []

    def clearSongFolderInfo(self):
        self.songFolderInfo = {}

    def createCsvSongListing(self):
        try:
            print(logMsg("BATCH","INFO"),"createCsvSongListing: Attempting to write CSV File '" + self.outputFile + "'")
            os.chdir(self.path) # Change to batch directory context
            sortedFolders = sorted(self.songFolderInfo.keys(), key=str.lower)
            sortedSongFields = sorted(self.songFolderInfo[sortedFolders[0]].keys(), key=str.lower)
            header = "[FOLDER]"

            # Create first row string in CSV file specifying the fields in the columns.
            for field in sortedSongFields:
                header += ",[" + field + "]"

            # Write header out to file, then write information for all parsed songs.
            with open(self.outputFile, 'w') as batchInfo:
                batchInfo.write(header+"\n")
                for folder in sortedFolders:
                    folderWithoutCommas = folder + ","
                    folderWithoutCommas = re.sub(',', '', folderWithoutCommas)
                    songInfoString = folderWithoutCommas
                    for songField in sortedSongFields:
                        fieldWithoutCommas = self.songFolderInfo[folder][songField] + ","
                        fieldWithoutCommas = re.sub(',', '', fieldWithoutCommas)
                        if fieldWithoutCommas == "":
                            print(logMsg("BATCH","WARNING"),"createCsvSongListing: '" + folder + "' has empty field for '" + songField + "'")
                        songInfoString += "," + fieldWithoutCommas
                    batchInfo.write(songInfoString+"\n")
            batchInfo.close()
            print(logMsg("BATCH","INFO"),"createCsvSongListing: Successfully wrote CSV File '" + self.outputFile + "'")
        except:
            print(logMsg("BATCH","ERROR"), "createCsvSongListing: {0}: {1}".format(sys.exc_info()[0].__name__, str(sys.exc_info()[1])))
        
    
# MAIN
if __name__ == "__main__":

    # Create Batch Object.
    batchPath = input("Input directory to Batch Folder: ")
    batchContainer = Batch(batchPath)
    batchContainer.setSmFileFields(['TITLE','ARTIST','STEPARTIST'])
    batchContainer.setDwiFileFields(['TITLE','ARTIST','STEPARTIST'])
    batchContainer.dumpInfo()
    batchContainer.getBatchFileListing()
    batchContainer.parseSongs()
    # batchContainer.printSongInfo()
    batchContainer.createCsvSongListing()
    

#!/usr/bin/python3

from utilities.logMsg import logMsg
import os
import re

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
    - getSongInfo(): Retrieves song information for a specified folder in the batch directory.
    - parseSongs(): Goes through every folder in the batch directory to find song information.
    - printSongInfo(): Prints out any successfully parsed information.
    - clearBatchFiles(): Empties previous listing of batch directory file contents.
    - clearSongFolderInfo(): Empties any song information that was stored previously.
    - createCsvSongListing(): Writes a Comma-Separated-Values file of the song information.
    """
    
    def __init__(self, batchPath, batchName, batchOutputFile):
        '''
        Constructor
        '''
        self.path = batchPath
        self.name = batchName
        self.outputFile = str(batchOutputFile) + ".csv"
        self.batchFiles = []
        self.smFileFields = []
        self.dwiFileFields = []
        self.songFolderInfo = {}

    def dumpInfo(self):
        print(logMsg("LINEPARSE","INFO"),"dumpInfo: Dumping Batch Info")
        print("BATCH PATH:", self.path,
              "\nBATCH NAME:", self.name,
              "\nSM FIELDS:", self.smFileFields,
              "\nDWI FIELDS:", self.dwiFileFields)

    def getBatchFileListing(self):
        print(logMsg("LINEPARSE","INFO"),"getBatchFileListing: Attempting to get song listing in '" + self.path + "'")
        try:
            self.batchFiles = os.listdir(self.path)
        except:
            print(logMsg("LINEPARSE","ERROR"),"getBatchFileListing: Could not list files, check to see if directory exists")

    def setSmFileFields(self,fieldList):
        self.smFileFields = fieldList

    def setDwiFileFields(self,fieldList):
        self.dwiFileFields = fieldList

    def parseChartFile(self,chartFolder,chartFile,chartType):
        """
        chartType should be one of:
        - sm
        - dwi
        """
        print(logMsg("LINEPARSE","INFO"),"parseChartFile: Attempting to parse chart file '" + chartFile + "'")
        os.chdir(chartFolder) # Change to song folder's context in the batch
        songFieldInfo = {}

        # group(1) here refers to the captured field.
        if chartType == "sm":
            with open(chartFile) as smFile:
                for line in smFile:
                    if line.startswith('#'):
                        for field in self.smFileFields:
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
                            fieldSearch = re.search("^#"+field+":(.*);$",line)
                            if fieldSearch != None:
                                songFieldInfo[field] = fieldSearch.group(1)
                    else:
                        break # No more hashtags means we're done with the song info at the top

        return songFieldInfo # This works

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
                print(logMsg("LINEPARSE","ERROR"),"getSongInfo: Error parsing file information for ", file)
            
    def parseSongs(self):
        """
        songFolder is the name of the folder by itself. It will be turned into the full file path
        However since not every file in the batch could be a folder, keep file cases in mind
        """
        if self.batchFiles != []:
            print(logMsg("LINEPARSE","INFO"),"parseSongs: Looking through batch files")
            for folder in self.batchFiles:
                try:
                    self.getSongInfo(folder)
                except:
                    print(logMsg("LINEPARSE","ERROR"),"parseSongs: Something went wrong with '" + folder + "'")

    def printSongInfo(self):
        """
        Prints any songs that were parsed.
        """
        print(logMsg("LINEPARSE","INFO"),"printSongInfo: Printing out parsed songs")
        for folder in self.songFolderInfo.keys():
            print(folder,"-->",self.songFolderInfo[folder])

    def clearBatchFiles(self):
        self.batchFiles = []

    def clearSongFolderInfo(self):
        self.songFolderInfo = {}

    def createCsvSongListing(self):
        try:
            print(logMsg("LINEPARSE","INFO"),"createCsvSongListing: Attempting to write CSV File '" + self.outputFile + "'")
            os.chdir(self.path) # Change to batch directory context
            header = "[FOLDER]"
            for field in self.smFileFields:
                header += ",[" + field + "]"
            with open(self.outputFile, 'w') as batchInfo:
                batchInfo.write(header+"\n")
                for folder in self.songFolderInfo.keys():
                    folderWithoutCommas = folder + ","
                    folderWithoutCommas = re.sub(',', ' ', folderWithoutCommas)
                    songInfoString = folderWithoutCommas
                    for songField in self.songFolderInfo[folder].keys():
                        fieldWithoutCommas = self.songFolderInfo[folder][songField] + ","
                        fieldWithoutCommas = re.sub(',', ' ', fieldWithoutCommas)
                        songInfoString += "," + fieldWithoutCommas
                    batchInfo.write(songInfoString+"\n")
            batchInfo.close()
        except:
            print(logMsg("LINEPARSE","ERROR"),"createCsvSongListing: Something went wrong writing the file")
        
    
# MAIN
if __name__ == "__main__":

    # Create Batch Object.
    batchPath = input("Input directory to Batch Folder: ")
    batchName = input("Input Name of Batch: ")
    batchOutputFile = input("Input Output CSV File: ")
    batchContainer = Batch(batchPath,batchName,batchOutputFile)
    batchContainer.setSmFileFields(['TITLE','ARTIST'])
    batchContainer.setDwiFileFields(['TITLE','ARTIST'])
    batchContainer.dumpInfo()
    batchContainer.getBatchFileListing()
    batchContainer.parseSongs()
    # batchContainer.printSongInfo()
    batchContainer.createCsvSongListing()
    

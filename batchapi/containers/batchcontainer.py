#!/usr/bin/python3

import os
import re
import sys
from containers.simfile import *

# Create Logger Object with date formatting for output stream
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/tmp/batch_log.log',
                    filemode='w')
batchLogger = logging.getLogger("BATCH")

# CLASS DEFINITION
class BatchContainer():
    """
    * PURPOSE *
    - BatchContainer is a Container that holds Simfile Objects and provides
    a way to contain information about all Simfile Objects in it through a
    dictionary (allSongInfo).

    * CLASS ATTRIBUTES *
    - path: File path to the batch to search.
    - name: Name of the batch.
    - outputFile: Name of CSV file to write.
    - batchFiles: List of files in the batch directory being searched.
    - smFileFields: Fields to search for in an .sm file
    - dwiFileFields: Fields to search for in a .dwi file
    - batchSongFolders: List of files/folders in the batch folder directory.
    - simfile_list: List of simfile objects for each song folder in batch.
    - allSongInfo: Dictionary containing information about all the simfiles
    in simfile_list (information is based on search fields).

    * FUNCTIONS *
    - __str__(): Prints out information about the currently reference Batch Object
    - getBatchFileListing(): Get a file listing of the batch directory
    - setSmFileFields(): Sets list of fields to search for in an .sm file
    - setDwiFileFields(): Sets list of fields to search for in a .dwi file
    - parseSongs(): Goes through every folder in the batch directory to find song information.
    - createCsvSongListing(): Writes a Comma-Separated-Values file of the song information.
    """
    
    def __init__(self, batchPath):
        """
        Constructor. Only requires user to pass full path to batch folder directory.
        """
        self.path = batchPath
        self.name = os.path.basename(os.path.normpath(batchPath))
        self.outputFile = self.name + ".csv"
        self.smFileFields = []
        self.dwiFileFields = []
        self.batchSongFolders = []
        self.simfile_list = []
        self.allSongInfo = {}

    def __str__(self):
        return """>>> BATCH INFORMATION
- BATCH PATH: {}
- BATCH NAME: {}
- OUTPUT FILE: {}
- SM FIELDS: {}
- DWI FIELDS: {}
- SIMFILES: {}""" \
        .format(self.path, self.name, self.outputFile, self.smFileFields, self.dwiFileFields,
                str(len(self.simfile_list)))

    def getFolderList(self):
        batchLogger.info("getFolderList: Retrieving song folder listing in '%s'", self.path)
        try:
            self.batchSongFolders = os.listdir(self.path)
        except:
            batchLogger.warning("getFolderList: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                 str(sys.exc_info()[1])))

    def construct(self):
        # for every folder in the batch folder, instantiate Simfile objects

        batchLogger.info("construct: Attempting to construct simfile objects in '%s'", self.path)
        try:
            for songFolder in self.batchSongFolders:
                try:
                    os.chdir(self.path)
                    songFolderPath = os.path.join(self.path, songFolder)
                    folderFiles = os.listdir(songFolder)
                    batchLogger.debug("construct: Folder Files are '%s'", str(folderFiles))
                    for file in folderFiles:
                        smSearch = re.search("(.*\.[sS][mM])$", file)
                        dwiSearch = re.search("(.*\.[dD][wW][iI])$", file)
                        if smSearch is not None:
                            simfileToAdd = SMFile(songFolderPath, songFolder, file,
                                                  self.smFileFields)
                            batchLogger.debug(simfileToAdd)
                            self.simfile_list.append(simfileToAdd) # Add .sm file simfile
                            break
                        if dwiSearch is not None:
                            simfileToAdd = DWIFile(songFolderPath, songFolder, file,
                                                   self.dwiFileFields)
                            batchLogger.debug(simfileToAdd)
                            self.simfile_list.append(simfileToAdd) # Add .dwi file simfile
                            break
                except:
                    continue # This means we didn't have a directory
            batchLogger.info("construct: Created %s simfile objects", str(len(self.simfile_list)))
        except:
            batchLogger.warning("construct: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                             str(sys.exc_info()[1])))

    def setSmFields(self, fieldList):
        self.smFileFields = fieldList

    def setDwiFields(self, fieldList):
        self.dwiFileFields = fieldList

    def parseSimfiles(self):
        """
        NOTE: Simfile class has its own getSimInfo method. That needs to be changed here.

        folder is the name of the folder by itself. It will be turned into the full file path
        However since not every file in the batch could be a folder, keep file cases in mind
        """
        if self.simfile_list is not []:
            batchLogger.info("parseSongs: Parsing batch simfiles")
            for simfileObj in self.simfile_list:
                try:
                    songFolder = simfileObj.getSongFolderName()
                    batchLogger.debug("parseSongs: Song Folder is '%s'", songFolder)
                    simfileObj.parse()
                    self.allSongInfo[songFolder] = simfileObj.getSimInfo()
                except:
                    batchLogger.warning("parseSongs: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                      str(sys.exc_info()[1])))

    def createCsvSongListing(self):
        try:
            batchLogger.info("createCsvSongListing: Attempting to write CSV File '%s'", self.outputFile)
            os.chdir(self.path)  # Change to batch directory context
            sortedFolders = sorted(self.allSongInfo.keys(), key=str.lower)
            sortedSongFields = sorted(self.allSongInfo[sortedFolders[0]].keys(), key=str.lower)
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
                        fieldWithoutCommas = self.allSongInfo[folder][songField] + ","
                        fieldWithoutCommas = re.sub(',', '', fieldWithoutCommas)
                        if fieldWithoutCommas == "":
                            batchLogger.warning("createCsvSongListing: '%s' has empty field for '%s'",
                                                folder, songField)
                        songInfoString += "," + fieldWithoutCommas
                    batchInfo.write(songInfoString+"\n")
            batchInfo.close()
            batchLogger.info("createCsvSongListing: Successfully wrote CSV File '%s'", self.outputFile)
        except:
            batchLogger.warning("createCsvSongListing: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))


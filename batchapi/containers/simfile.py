#!/usr/bin/python3

import os
import re
import sys
from abc import ABCMeta, abstractmethod

# Create Logger Object with date formatting for output stream
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/tmp/simfile_log.log',
                    filemode='w')
simfileLogger = logging.getLogger("SIMFILE")

def getSongTitleFromFolder(folder):
    """
    folder is the name of the folder by itself.
    """
    
    # group(1) here refers to the captured field. Parse stepartist from song folder.
    simfileLogger.debug("getSongTitleFromFolder: Retrieving song title from folder '%s'", folder)
    try:
        parenthesesArtist = re.search("(.*)\[(.*)\]$", folder)
        bracketArtist = re.search("(.*)\((.*)\)$", folder)
        curlybraceArtist = re.search("(.*)\{(.*)\}$", folder)
        if parenthesesArtist is not None:
            song = parenthesesArtist.group(1).strip()  # Song Title with parentheses stepartist
        if bracketArtist is not None:
            song = bracketArtist.group(1).strip()  # Song Title with brackets stepartist
        if curlybraceArtist is not None:
            song = curlybraceArtist.group(1).strip()  # Song Title with brackets stepartist
    except:
        simfileLogger.warning("getSongTitleFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                        str(sys.exc_info()[1])))

    return song

def getStepArtistFromFolder(folder):
    """
    folder is the name of the folder by itself.
    """
    
    # group(1) here refers to the captured field. Parse stepartist from song folder.
    simfileLogger.debug("getStepArtistFromFolder: Retrieving stepartist from folder '%s'", folder)
    try:
        parenthesesArtist = re.search(".*\[(.*)\]$", folder)
        bracketArtist = re.search(".*\((.*)\)$", folder)
        curlybraceArtist = re.search(".*\{(.*)\}$", folder)
        if parenthesesArtist is not None:
            stepArtist = parenthesesArtist.group(1)  # Stepartist with parentheses
        if bracketArtist is not None:
            stepArtist = bracketArtist.group(1)  # Stepartist with brackets
        if curlybraceArtist is not None:
            stepArtist = curlybraceArtist.group(1)  # Stepartist with brackets
    except:
        simfileLogger.warning("getStepArtistFromFolder: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                         str(sys.exc_info()[1])))

    return stepArtist

class Simfile():
    """
    Simfile is a Container that provides information for a single song
    in the batch folder, including the folder and its path, the chart
    file to parse for information, search fields to look for in the chart
    file. simInfo is a dictionary containing information about these
    fields after parse() is used; note that parse() here is an
    overridden function and we only want to use SMFile and DWIFile.
    """
    
    def __init__(self, pathToSongFolder, songFolderName, chartFile, searchFields=[]):
        self.folderPath = pathToSongFolder
        self.folder = songFolderName
        self.stepfile = chartFile
        self.fields = searchFields
        self.songTitle = getSongTitleFromFolder(self.folder)
        self.stepper = getStepArtistFromFolder(self.folder)
        self.simInfo = {} # Dictionary storing results from search field parsing

    def getSongFolderName(self):
        return self.folder

    def getSimInfo(self):
        return self.simInfo

    def __str__(self):
        return """- FOLDER PATH: {}
- FOLDER: {}
- STEPFILE: {}
- FIELDS: {}
- TITLE: {}
- STEPARTIST: {}
- SONG INFO: {}""" \
        .format(self.folderPath, self.folder, self.stepfile, self.fields, self.songTitle,
                self.stepper, self.simInfo)
 
    @abstractmethod
    def parse(self):
        pass

class SMFile(Simfile):
    def parse(self):

        simfileLogger.debug("parse: Attempting to parse .sm file '%s'", self.stepfile)
        os.chdir(self.folderPath)  # Change to song folder's context in the batch
        songFieldInfo = {}
        try:
            # group(1) here refers to the captured field.
            with open(self.stepfile) as smFile:
                for line in smFile:
                    if line.startswith('#'):
                        for field in self.fields:
                            if field is "TITLE":
                                continue  # We're getting title and stepartist from folder
                            if field is "STEPARTIST":
                                continue
                            else:
                                fieldSearch = re.search("^#"+field+":(.*);$", line)
                                if fieldSearch is not None:
                                    songFieldInfo[field] = fieldSearch.group(1)
                    else:
                        break  # No more hashtags means we're done with the song info at the top
        except:
            simfileLogger.warning("parse: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                              str(sys.exc_info()[1])))
            if 'ARTIST' in self.fields:
                songFieldInfo['ARTIST'] = ""
                
        if 'TITLE' in self.fields:
            songFieldInfo['TITLE'] = self.songTitle
        if 'STEPARTIST' in self.fields:
            songFieldInfo['STEPARTIST'] = self.stepper

        simfileLogger.debug("parse: '%s'", songFieldInfo)
        self.simInfo = songFieldInfo
 
class DWIFile(Simfile):
    def parse(self):
    
        simfileLogger.debug("parse: Attempting to parse .dwi file '%s'", self.stepfile)
        os.chdir(self.folderPath)  # Change to song folder's context in the batch
        songFieldInfo = {}
        try:
            # group(1) here refers to the captured field.
            with open(self.stepfile) as dwiFile:
                for line in dwiFile:
                    if line.startswith('#'):
                        for field in self.fields:
                            if field is "TITLE":
                                continue  # We're getting title and stepartist from folder
                            if field is "STEPARTIST":
                                continue
                            else:
                                fieldSearch = re.search("^#"+field+":(.*);$", line)
                                if fieldSearch is not None:
                                    songFieldInfo[field] = fieldSearch.group(1)
                    else:
                        break  # No more hashtags means we're done with the song info at the top
        except:
            simfileLogger.warning("parse: {0}: {1}".format(sys.exc_info()[0].__name__,
                                                                              str(sys.exc_info()[1])))
            if 'ARTIST' in self.fields:
                songFieldInfo['ARTIST'] = ""

        if 'TITLE' in self.fields:
            songFieldInfo['TITLE'] = self.songTitle
        if 'STEPARTIST' in self.fields:
            songFieldInfo['STEPARTIST'] = self.stepper

        simfileLogger.debug("parse: '%s'", songFieldInfo)
        self.simInfo = songFieldInfo


#!/usr/bin/python3

from containers.batchcontainer import BatchContainer

# MAIN
# C:\pythoncode\batchApis\tests\batch
if __name__ == "__main__":

    # Create Batch Object with user specified directory.
    print(">>> batch.py looks through a batch set song directory and retrieves song "
          "information from it, then generates a .csv file of this information.")
    batchPath = (input(">>> Input full path to directory of Batch Set Folder: ")).strip()
    batch = BatchContainer(batchPath)

    # Initialize search fields and list of folders in batch directory.
    print(">>> Getting list of folders in batch directory.")
    batch.setSmFields(['TITLE', 'ARTIST', 'STEPARTIST'])
    batch.setDwiFields(['TITLE', 'ARTIST', 'STEPARTIST'])
    batch.getFolderList()

    # Make the simfile objects, parse them, then write info out to .csv file.
    print(">>> Constructing Simfile Objects and parsing them.")
    batch.construct()
    batch.parseSimfiles()
    print(batch)
    print(">>> Creating .csv file of song information.")
    batch.createCsvSongListing()
    print(">>> See '/tmp/batchContainer.log' for more output.")

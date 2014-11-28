#!/usr/bin/python3

from containers.notestemplate import ArtistForNotes

# MAIN
# This is used to simply append the stepartist to the song information lines in a judge notes file.
if __name__ == "__main__":

    # Create Template Object.
    print(">>> artistfornotes.py is used to add stepartists to judge notes files in a set. This is done after judges have "
          "passed in their notes.")
    print(">>> It is assumed you have already placed all the judge notes for the set and the .csv file from batch.py in "
          "the same directory.")
    inputCSV = (input(">>> Input Full Path to .csv File generated from batch.py: ")).strip()
    searchList = ['STEPARTIST']  # We're only concerned with getting stepartist index here to add
    artistAdd = ArtistForNotes(inputCSV, searchList)

    # Get relevant fields from CSV file from batch.py
    print(">>> Getting relevant fields to remake judge notes file.")
    artistAdd.getFieldIndices()
    artistAdd.getRelevantFields()
    print(artistAdd)

    # Obtain judge file information and set output file
    print(">>> Getting Judge Files and Judge Name Information.")
    artistAdd.getJudgeFilesForAdd()
    artistAdd.getAllJudgesInSet()

    # Now add the stepartist to each judge file.
    print(">>> Getting stepartist for each song and adding them to judge notes file.")
    artistAdd.getAllSteppers()
    artistAdd.addSteppersToFile()
    print(">>> See '/tmp/notesTemplate_log.log' for more output.")

#!/usr/bin/python3

from containers.format import *

# MAIN
if __name__ == "__main__":

    print(">>> format.py takes a set of judge notes and combines them into a forum post.")
    notesPath = (input(">>> Input full path to directory with sets folders for judge notes: ")).strip()
    notesFormat = FormatNotes(notesPath)

    # Get the judges and all set info.
    notesFormat.getSetJudgeInfo()

    # Print out formatting.
    print(">>> Creating formatted post of the batch set.")
    notesFormat.makeFormattedPost()
    print(">>> See '/tmp/formatNotes.log' for more output.")

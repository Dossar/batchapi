#!/usr/bin/python3

from containers.format import *

# MAIN
if __name__ == "__main__":

    print(">>> format.py takes a set of judge notes and combines them into a forum post.")
    notesPath = (input(">>> Input full path to notes directory for set: ")).strip()
    notesFormat = FormatNotes(notesPath)

    # Print out formatting.
    print(">>> Creating formatted post of the batch set.")
    notesFormat.makeFormattedPost()
    print(">>> See '/tmp/formatNotes.log' for more output.")

#!/usr/bin/python3

from time import strftime

def logMsg( scriptName , level ):
    """
    This function formats the beginning of a print statement for debugging purposes.
    """
    return ("[" + strftime("%Y-%m-%d %H:%M:%S") + "] " + scriptName + ":" + level + ":")

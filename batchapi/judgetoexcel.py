#!/usr/bin/python3

from containers.judge import JudgesForExcel

# MAIN
if __name__ == "__main__":
    print(">>> judgetoexcel.py is used to make a .csv file that contains judge ratings (judgments_<setname>.csv)")
    print(">>> It is assumed you have already ran artistfornotes.py to add in the stepartists (the files had _steppers "
          "appended to the file name). If you are specifying a set directory with judge notes that don't have the "
          "stepartists in them, you will get unexpected behavior.")
    notesDirPath = (input(">>> Input full path of Set directory with Judge Notes: ")).strip()
    judgeSet = JudgesForExcel(notesDirPath)

    # Get Judge Notes Files First along with Set Number
    judgeSet.getSetFileListing()
    judgeSet.printSetFileListing()
    judgeSet.getSetNumber()

    # Get Judge Names
    judgeSet.getAllJudgesInSet()
    judgeSet.printJudgeNames()

    # Parse ordered song list from judge notes.
    judgeSet.getOrderedSongList()

    # Now get all the judge ratings
    judgeSet.getAllJudgeRatings()
    print(judgeSet)

    # Test printing out CSV file
    print(">>> Creating CSV file.")
    judgeSet.createRatingCSV()
    print(">>> See '/tmp/judgesExcelLogger.log' for more output.")

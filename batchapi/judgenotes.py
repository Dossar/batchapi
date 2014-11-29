#!/usr/bin/python3

from containers.judge import JudgeNotes

# MAIN
if __name__ == "__main__":

    print(">>> judgenotes.py is used to get some analytics out of a judge's notes concerning normal ratings and special "
          "ratings.")
    print(">>> This should not be run until after judges have passed in their notes.")
    judgeNotesFilePath = (input(">>> Input full path of Judge Notes File: ")).strip()
    judge = JudgeNotes(judgeNotesFilePath)
    judge.getJudgeName()

    judge.getJudgeRatings()
    judge.getNumSpecialFiles()
    judge.getNumTotalFiles()
    # judge.printJudgeRatings()
    judge.getJudgeAverage()

    judge.getRatingsToSongs()
    judge.getSpecialRatingsToSongs()
    print(judge)
    # judge.printRatingsToSongs()
    print(">>> Writing Ratings To Songs File.")
    judge.writeRatingsToSongs()
    
    judge.getRawRatings()
    judge.getRawSpecialRatings()
    # judge.printRawRatings()
    print(">>> Writing Raw Ratings File.")
    judge.writeRawRatings()
    print(">>> See '/tmp/judgeNotes.log' for more output.")

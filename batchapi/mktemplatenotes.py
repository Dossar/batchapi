#!/usr/bin/python3

from containers.notestemplate import NotesTemplate

# MAIN
if __name__ == "__main__":
    
    # Create Template Object.
    print(">>> notestemplate.py is used to generate a template judge notes file from the .csv file generated in batch.py")
    print(">>> It is assumed here you already have run batch.py to make this .csv file.")
    inputCSV = (input(">>> Input Full Path to .csv File generated from batch.py: ")).strip()
    searchList = ['ARTIST', 'TITLE', 'STEPARTIST']  # Same song title and same song artist for comparison
    templateNotes = NotesTemplate(inputCSV, searchList)

    # Get relevant fields for the template notes file.
    templateNotes.getFieldIndices()
    templateNotes.getRelevantFields()
    print(templateNotes)

    # Write out notes after getting relevant fields information.
    # templateNotes.printTemplate()
    print(">>> Writing out Template Judge Notes File")
    print(">>> See '/tmp/notesTemplate.log' for more output.")
    templateNotes.writeTemplateFile()

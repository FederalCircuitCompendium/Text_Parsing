#This program is a basic text extractor for use on the PDFs collected from the Federal Circuit's website.  It doesn't do anything fancy: all it does is to 
#run through all the PDFs in the named directory and extract the first 2500 characters, then insert it into a list that begins with the filename. 
#Then it outputs the filename and string to a file for future analysis. 
#It is not a speedy program - it took about 5 hours to run on the 17,000 PDFs that are currently in the dataset. That produced a file of 35 MB
#At some point we will need to extract the full text of these opinions - but that will likely need to be done in chunks or to a set of text files rather than one mega file. 

#note that all this program does is to extract the first 2500 characters.  It does not clean up the text at all.  




#This script uses the os toolset
import os

#we're going to export the text to a .csv
import csv

#This script uses the pdfminer package to extract text from PDF files.  You will need to install PDF miner if it is not already installed.  To do this, 
#Open terminal and type "pip3 install pdfminer.six --user"  This should install pdfminer.

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

editFile = csv.writer(open('Appeal_Text_First2500_Characters.csv', 'at')) #This is the file that the text will be output to.  Note that it is in append mode.  

#This section defines a function that will extract the text.  It could probably be tweaked, but for now it does the basic text extract.
#Most of this is straight from the pdfMiner documentation
#The output text is stored in the "text" variable

def pdf_to_text(path):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)

    for page in PDFPage.get_pages(filepath, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    filepath.close()
    device.close()
    retstr.close()
    return text

#The following loop runs through the files in the directory and extracts the key text.
for f in os.listdir("Test Set"): #The directory that this currently runs on is called "Test Set."  It would probably be good to add a prompt for future use. 
    filename = "Test Set/"+str(f)
    try: #I added the try - except clause in order to skip any files that aren't pdfs or that have another error message
        outputText = pdf_to_text(filename) #runs the pdf_to_text function on the file and extracts the text for the entire document
        outputText = str(outputText[:2500])  #limits to the first 2500 characters

    except: 
       outputText="error" #returns an error message if the text miner fails.
    
    appealRow = [outputText] #starts the appeal row list with the first 2500 chars from the PDF
    appealRow.insert(0,f) #inserts the file number at the beginning of the list
    
    print(appealRow) #This is just to that I can see it running.  It's not really necessary otherwise. 
    editFile.writerow(appealRow) #Writes the filename and text string to the .csv file specified at the outset.
    
    
             
print("done") #Yay!


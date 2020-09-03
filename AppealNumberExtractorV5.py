
#This program analyzes a file containing extracted text from court opinons to identify appeal numbers and put them into a CSV. The input is a .csv file with each line having the 
#filename and the text to be scanned.  The output is a .csv file with the filename, number of appeal numbers, and string of appeal numbers separated by a semicolon.

#The purpose of this program is to automate the time-consuming task of manually copying appeal numbers from a set of about 17,000 documents from the Federal Circuit. Results were compared against
#a set of about 4,000 human-coded records and, as of version 5, had a 97% match rate to the human-coded entries. A non-trivial number of the non-matches are errors in the human coding. Another portion of the 
#non-matches are rare anomolies. A substantial portion of the non-matches are because the opinion has two separate captions and the program only captures the appeal numbers in the first caption.

#The current version runs through a couple of different searchstrings to find as many of the numbers as accurately as possible.  This is because there have been
# (and continue to be) multiple different formats used for the appeal numbers.

#Notes: Pay attention to the dates that are hard coded.  These include the yearEnd date as well as the end date for the two-year searches.  
#Look for text "hard coded" if there are these kinds of errors or issues.  Make sure to update the code in 2025. 


#This script makes use of regular expressions
import re    

#This script uses the os toolset
import os

#This script is going to export the text to a .csv so it uses the .csv toolset
import csv
from csv import reader # read csv file as a list of lists



TestText="nonprecedential 2018-2343, 2018-2345, 2014-03243, 03-2425, 03-2426 2010-1243, -3345, 2006-CV-2034 11-2343 " #Test text just to make sure it's working

#The below function uses a regular expression called "findall" to find all the locations of text with this specific
#sequence of characters and generates a list called "substrings" with that text. Basically, what it does is to look through the inputText string until it finds the specified sequence.
#Then it places the four final digits (such as those following "2019-") into the list.  
#It stops when it hits a space.  The numbers that are extracted are placed into a list called "appealNumbers" and the prefix (YYYY-) is added back in. 

def extract_appeal_number(inputText):

    yearStart = 2001 #This is when we'll start running this text analysis.  It is very unlikely that pre-2000 appeal numbers will be searchable using this technique
    yearEnd = 2025 #This is a year five years from now.  The code will need to be updated if we ever get there. 

    appealNumbers = [] #creates empty list for the appeal numbers to go in
    

    for year in range(yearStart, yearEnd): #This for loop runs a search for appeal numbers for each year between 2000 and 2025, adding to the appealNumbers list.  It uses several different search strings.
        appealPrefix  = str(year)+"-" #leading search string that will be used (example: "2012-"
        indexYear = year-2000 #This creates an index year that will be used for two-digit searches
    
        
        searchString = str(year)+'-'+"(\d\d\d\d)" #Searchstring to look for entries in the exact format of YYYY-####
        appealSubstring1 = re.findall(searchString, inputText) #and captures the text until it comes to our example of a number in the exact format YYYY-XXXX.
                
      
        
        if indexYear in range(1, 10):
            searchStringTwoDigitPrefix=(str("0"+str(indexYear))+'-')
            
        else:
            searchStringTwoDigitPrefix=(str((indexYear))+'-')
        
             
        #next the program iterates through some additional searches that use less-specific text.  Because these are less-specific, the text to be searched is also more tightly limited
        #doing this sometimes results in a type II error but that's a trade-off because we really want to avoid Type I errors. The primary search remains the XXXX-YYYY search string used above. 
        
        #The first sequence truncates the text when it hits common text that comes after the appeal numbers.  The disadvantage is that it also prevents the search from finding second-caption
        #appeal numbers, which are a rare occurance. 
        
        inputText = inputText.split("Appeals from")[0]
        inputText = inputText.split("Appeal from") [0]
        inputText = inputText.split("Appeal  from") [0]
        inputText = inputText.split("Appeals  from") [0]
        inputText = inputText.split("Petition for") [0]  
        inputText = inputText.split("Petition  for") [0]
        inputText = inputText.split("Petitions for") [0]        
        
        #Next the code tries to perform various truncations at the beginning and end.  These don't always work - hence the try. If they don't work, then currently the program
        #is set to have no text to be searched.  This could be changed to be the inputText, but it would result in more Type I errors.  
        
        try:
            #Setting the beginning of the search string
            textToBeSearched = inputText.split(searchStringTwoDigitPrefix,1)[1] #The program first extracts just the sequence that it will search, starting with the 2-digit year
            
            textToBeSearched = "-" + textToBeSearched #The split removes the leading hyphen, which we need to run our searches properly. This just adds it back in.
                    
            #We need to make sure that we aren't accidentally picking up the district court docket numbers  
            if textToBeSearched.startswith("-CV"):
                textToBeSearched=""
            elif textToBeSearched.startswith("-cv"):
                textToBeSearched=""
            else:
                pass
            
            #Setting the end of the search string
            textToBeSearched = textToBeSearched.split("\\n",1)[0] #ends the search string when it hits the newline character.
            textToBeSearched = textToBeSearched.split("\n",1)[0] #ends the search string when it hits the newline character               
        
            for yearSuffix in range(yearStart, year):
                appealSuffix=str(yearSuffix)+"-" #trailing search string that can be used to find the end of the search string.  This one looks for the full-year format (YYYY-) before the year 
                #being searched.
                textToBeSearched = textToBeSearched.split(appealSuffix)[0]

            for yearSuffix in range(year+1, yearEnd):
                appealSuffix=str(yearSuffix)+"-" #trailing search string that can be used to find the end of the search string. This one looks for the full-year format (YYYY-) for 
                #years after the year being searched
                textToBeSearched = textToBeSearched.split(appealSuffix)[0]
                
            #The next sequence searches for the two-digit patterns "02-" and truncates the search string when it comes to one of those. 
            for yearSuffixTwoDigit in range(1, indexYear): #This looks for two-digit docket numbers beore the year that was used to start the string
                if yearSuffixTwoDigit in range(1,10): #These two lines create the search string for the 01- to 09- series of dockets
                    searchStringTwoDigit=str("0"+str(yearSuffixTwoDigit)+'-')
                    
                else: #These two lines create the search string for the 10- onward series. 
                    searchStringTwoDigit=str(str(yearSuffixTwoDigit)+'-')
                                
                textToBeSearched = textToBeSearched.split(searchStringTwoDigit,1)[0]
                
            for yearSuffixTwoDigit in range(indexYear+1, 25): #This looks for two-digit docket numbers after the year that was used to start the string. Note that the end year (2025) is hard-coded. 
                if yearSuffixTwoDigit in range(1,10):
                    searchStringTwoDigit=str("0"+str(yearSuffixTwoDigit)+'-')
                    
                else:
                    searchStringTwoDigit=str(str(yearSuffixTwoDigit)+'-')
                                
                textToBeSearched = textToBeSearched.split(searchStringTwoDigit,1)[0] #Performs the split using the two-digit number
                
        #If our truncations fail, then we decide not to search anything.  This could be changed in the future to be the inputText: in other words, to still search the text.  This would result in 
        #fewer type II errors but a lot of type I errors.  
        except:
            textToBeSearched=""
            
        
           
        #The next sequence runs the seach on the textToBeSearched strings that we've extracted. 
        
        searchString='-'+"(\d\d\d\d)" #regular expressions search string.  It looks for text that starts with a "-", followed by a four digit number.  This is a very powerful but non-specific search
        #That can only be used because we restricted the string that's being analyzed. 
        appealSubstring2 = re.findall(searchString, textToBeSearched) #This uses regular expressions to capture the four-digit sequence. It will only return the four-digit sequence.
        appealSubstring = appealSubstring1 + appealSubstring2 #This combines the results of the first search (YYYY-XXXX) with the second search (-XXXX, but only on the specified strings)
        #Remember, we are still doing this function on a per-year basis.
        
        appealSubstringLength=len(appealSubstring) #creates a variable based on the number of items in the Substring list

        for i in range(0,appealSubstringLength): #this for loop will go through all the items in the subtring in order to remove commas
            individualAppealNumber = appealSubstring.pop(i) #This pops out each string in the list
            individualAppealNumber=individualAppealNumber.replace(",", "") #This removes trailing commas (but not other ones)
            appealSubstring.insert(i,individualAppealNumber) #Puts the cleaned value back into the list

        #Next we need to drop anything picked up by the substring search isn't in the right format - (i.e. four characters)  
        appealSubstring = [s for s in appealSubstring if len(s) == 4] #This creates a new version of the appealSubstring list with only items with four characters

        #Next we need to remove duplicates, which might happen because a number is in both substring1 and substring2
        tempList = [] 
        [tempList.append(x) for x in appealSubstring if x not in tempList]
        appealSubstring=tempList

        formattedAppealNumber = [appealPrefix + sub for sub in appealSubstring] #This takes the extracted text (the last four digits of the appeal number) and add the prefix (example: 2012-1012)
        appealNumbers=appealNumbers + formattedAppealNumber #adds the new appeal number to the list of appeal numbers
            
    

    return(appealNumbers) #Returns the final list of appeal numbers


print(extract_appeal_number(TestText)) #Just to make sure everything is working!

###END OF FUNCTION

#The remainder of the program basically just runs the above function on each string of text from the document that's contained in a .csv file

with open("Appeal_Text_First2500_Characters.csv", 'r') as f: #The program will be using this file.  At some point a prompt could be added here, but currently the filename is just hardcoded. 
    # pass the file object to reader() to get the reader object
    reader = csv.reader(f)
    data = list(reader)
    # Pass reader object to list() to get a list of lists.  The first item in the list is the file name and the second is the first 2500 chars
    
    
for s in data: #This loops through the elements in the list of lists to extract the appeal numbers.
    fileName = s[0] #defines the variable fileName as the text in the first column of the .csv 
    inputText = str(s[1]) #defines inputText as the second column of the .csv (which should have the text)the  text of the line
    inputText = inputText.split("Before")[0] #Truncates the inputText string to all text preceding the word "Before" (which usually indicates the judges, which are at the start of the opinion body)
    inputText = inputText.split("Decided:")[0] #Truncates the inputText string to all text preceding the phrase "Decided" (This reduces Type I errors, but may lead to Type II errors. 
    #Specifically, it truncates the string at the point where the opinion date is, which may cause it to miss the second caption in multi-caption opinions.(fairly rare)
    #consider running the code with this split in the function after the specific YYYY-XXXX search.
    
    #Next the program will try to find the first appeal number in the list, using the parsing function defined above.  
    
    try: #I added the try - except clause in order to skip any files that aren't pdfs or that have another error message
        finalAppealNumbers=(extract_appeal_number(inputText))
        appealNumbersString=str(finalAppealNumbers[0]) #starts the string with the FIRST item in the appealNumber list.  Sometimes this will be the only number. 
        
    except: 
        finalAppealNumbers=[] #If there is an exception, this will create a null set for appealNumbers.  The exception could be if the file isn't a PDF or if the
        #appeal number isn't in the first 2500 characters.  The bottom line is that we really want to know which files didn't get parsed properly and this tells us.
        appealNumbersString=""
        
    finalAppealNumberLength=len(finalAppealNumbers) #Knowing the number of appeal dockets is useful information that will be exported at the end. Also we need it for the next step.
    
    if finalAppealNumberLength > 1: # If there is more than one appeal number in the list, this conditional loop will add additional numbers
        for k in range(1,finalAppealNumberLength): #this for-loop adds additional appeal numbers to the string, separated by semicolons
            appealNumbersString=appealNumbersString+"; "+ str(finalAppealNumbers[k]) #May want to improve this by adding an extra "0" to the second half of the number so that it's easier to merge
            #with the PACER data.
    else:
        appealNumbersString=appealNumbersString #If not more than 1 appeal number, this will leave the appealNumberString unchanged (either blank or with only one appeal number).
        
    appealRow = [fileName, finalAppealNumberLength, appealNumbersString] #Exports the information we need.  appealNumbersString can always be split later on if needed. 
    
        
    print(appealRow)
    
#It would probably be better to create a list of lists in order to store the exported data.  Then I can write that entire thing to a file in one go.  But currently
#The program writes each line individually. The program only takes about 20 seconds to run for the 17,000 records so my motivation to do this is small.  

    editFile = csv.writer(open('appealNumbers.csv', 'at')) #Note that this is in append mode - which means that new rows will get written after existing rows.  To run a fresh
    #set, make sure to rename or delete the existing appealNumbers.csv set.
    editFile.writerow(appealRow) #Writes the row of data to our CSV.
    
    
             
print("done") #yay!

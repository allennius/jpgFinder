#!/usr/bin/env python3

from InquirerPy import prompt
from inquirer.themes import GreenPassion
import os
import glob
import sys
import shutil

# headers to find and counter
headers = b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1'
headerCounter = 0
answer = None
f = None

def main():

    # check args
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('usage: imgsearch.py fileORfolder [folder/headerfile]')
        exit()

    global answer
    inFiles = []

    # user choices
    question1 = [
        {
            'type': 'rawlist',
            'name': 'choice',
            'message': 'What to do?',
            'choices': [
                'Search for header',
                'Build from header',
                'Merge files from header',
            ],
            'filter': lambda val: val.lower()
        },
        {
            'type': 'confirm',
            'name': 'sort',
            'message': 'Sort files?',
            'default': False,
            'when': sortOrNo
        }
    ]


    # user choice
    answers = prompt(question1)
    answer = answers['choice'].split(" ",1)[0]

    # file/folder to search
    argPath = sys.argv[1]

    
    isFolder = os.path.isdir(argPath)

    # add all files in folder to list with full path to file
    if isFolder:
        folder = os.listdir(argPath)
        inFiles = glob.glob(os.path.join(argPath, '*'))

        # user sort answer == True -> sort
        if answers['sort']:
            inFiles.sort()      
            
        # if headerfile is given, insert as first element in list
        if len(sys.argv) == 3:
            headerFile = sys.argv[2]
            for file in inFiles:
                if headerFile in file:
                    inFiles.remove(file)
                    inFiles.insert(0, headerFile)
                    print('header applied')

    # if file add file path
    if os.path.isfile(argPath):
        inFiles.append(argPath)


    print('searching...')
    # folder or file
    if isFolder:
        # for filename in inFiles:
        findHeader(inFiles)

    else:
        findHeader(inFiles)
    

    print('Total {} headers found'.format(headerCounter))


# looks through file for header
def findHeader(inFiles):

    global headerCounter
    global answer
    isHeader = False
    fileCreated = False

    for filename in inFiles:
        with open(filename, 'rb') as file:

            if answer == 'build':
                fileCreated = False

            # count buffer for header position calc
            bufferCounter = 0
            buffer = 512 # 512 or 32?

            while True:
                if answer == 'build':
                    isHeader = False

                # read buffer if not EOF
                data = file.read(buffer)
                if not data:
                    break
                
                # search for all headers in buffer
                for header in headers:
                    pointer = 0                
                    while pointer < (buffer - len(header)):
                        try:
                            # split where header is found
                            hdrLocation = data[pointer:].index(header)
                        # if not found
                        except ValueError:
                            break
                        
                        # if user wants to write file
                        if answer == 'build' or answer == 'merge':
                            # if header is already active close previous file
                            if isHeader:
                                f.write(data[:hdrLocation])
                                f.close()

                            # open new file and write from new header
                            f = open('textfile{}'.format(headerCounter), 'wb')
                            fileCreated = True

                            # header of file exists
                            isHeader = True



                        headerCounter += 1

                        # header position in file
                        offset = bufferCounter*buffer + hdrLocation
                        print('Found: #{} in file: {} at: {:,}'.format(headerCounter, filename, offset))

                        # update pointer
                        pointer += (hdrLocation + len(header))

                
                if fileCreated:
                    if isHeader:
                        f.write(data[pointer:])
                    else:
                        f.write(data[:])
                bufferCounter += 1

        if isHeader:
            if answer == 'build':
                f.close()
            isHeader = False

def sortOrNo(answer):

    # return True if file i built else false
    # lets user choose for sorted list or not
    answer = answer['choice'].split(" ",1)[0]
    if answer == 'build': return True
    if answer == 'merge': return True
    return False


if __name__ == "__main__":
    # execute only if run as a script
    main()
#!/usr/bin/python3
from sys import argv


# Open the file in read mode 
start = open(argv[1], "r") 
text = start.readlines()

# Loop through each line of the file 
for line in text[2:]:
    # Create an empty dictionary 
    d = dict() 

    # Remove the leading spaces and newline character 
    line = line.strip() 

    # Convert the characters in line to 
    # lowercase to avoid case mismatch 
    line = line.lower() 
    
    #Extract region id
    portions = line.split(":")
    print("For region ",portions[0],": ")
    # Split the line into words 
    words = portions[1].split(" ") 

    # Iterate over each word in line 
    for word in words: 
    # Check if the word is already in dictionary 
        if word in d: 
            # Increment count of word by 1 
            d[word] = d[word] + 1
        else:
            # Add the word to dictionary with count 1 
            d[word] = 1
  
    # Print the contents of dictionary 
    for int in range(-8,8):
        print(int, end= ", ")
    print("")

    for int in range(-8,8):
        if str(int) in d:
            print(d[str(int)], end= ", ")
        else:
            print(0, end= ", ")
    print("")


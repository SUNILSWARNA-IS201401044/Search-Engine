
from pathlib import Path  
from os import listdir
from os.path import isfile, join


import os

Total_Files =[]

def files_from_folder(mypath):            # extracting file names from folders 
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        return onlyfiles


p = Path('/mnt/c/Users/Sunil/Desktop/sample/')
subdirectories = [x for x in p.iterdir() if x.is_dir()]

for i in subdirectories:
    #print subdirectories
    d= str(i)
    files = files_from_folder(d)
    for j in files:
        name= str(i)+str('/')+str(j)
        Total_Files.append(name)
print len(files),len(Total_Files)

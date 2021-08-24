import os
from os import listdir
from pathlib import Path
import json
import shutil

def createFolderIfNotExists(pathToCheck):
    if not os.path.exists(pathToCheck):
        os.makedirs(pathToCheck)
'''
def getListOfFiles(dirName):
    print("Scanning in "+dirName);
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles
'''

def getAllFilesAsTuple(directoryPath):
    result = list()
    print("Reading: "+directoryPath)
    initialDir = (Path(directoryPath)).parts[-1]
    imagesPath = os.path.join(directoryPath, "images")
    labelsPath = os.path.join(directoryPath, "labels")
    
    fileList = os.listdir(imagesPath)
    print("Reading "+str(len(fileList))+" objects from: "+initialDir)
    for entry in fileList:
        imageFullPath = os.path.join(imagesPath, entry)
        objName = os.path.splitext(os.path.basename(imageFullPath))[0]
        labelFullPath = os.path.join(labelsPath, objName+".txt")
        result.append([objName, "N", initialDir, imageFullPath, labelFullPath])         
    return result




def ScanInternal(dirName):
    result = list()
    pathAL_pos = "positive"
    pathAL_uns = "unsure"
    pathAL_neg = "negative"
    dataset_path_AL_pos = os.path.join(dirName,pathAL_pos)
    dataset_path_AL_uns = os.path.join(dirName,pathAL_uns)
    dataset_path_AL_neg =  os.path.join(dirName,pathAL_neg)
    
    print("Scanning!")
    result += getAllFilesAsTuple(dataset_path_AL_pos)
    result += getAllFilesAsTuple(dataset_path_AL_uns)
    result += getAllFilesAsTuple(dataset_path_AL_neg)
    return result



    
def WriteScanResult(objList, fileName):
    print("Writing report!")
    print("Writing "+str(len(objList))+" objects...")
    
    with open(fileName, 'w') as fp:
        json.dump(objList, fp)
        
    
def Scan():
    #load image
    pathAL_root = "activeLearning"
    cwd = Path.cwd()
    dataset_path_AL_root = str(cwd/pathAL_root)
    print("Paths set")
    
    objList = ScanInternal(dataset_path_AL_root)
    WriteScanResult(objList, 'objReg.json')
    print("Done!")

def LoadRegistries():
    objReg = 'objReg.json'
    print("Loading registries: "+objReg)
    lst1 = []
    lst1Loaded = False
    if Path(objReg).is_file():
        with open(objReg) as f1:
            lst1 = [list(x) for x in json.load(f1)]
            lst1Loaded = True
    return lst1, lst1Loaded

def MoveObjects(listToMove, destination, isReplication):
    print("Moving "+str(len(listToMove))+" objects")
    destImg = os.path.join(destination, "images")
    destLabels = os.path.join(destination, "labels")
    createFolderIfNotExists(destImg)
    createFolderIfNotExists(destLabels)
    print("DestImg: "+destImg)
    print("DestLab: "+destLabels)
    for index, obj in enumerate(listToMove):
        sourceImg = ""
        sourceLabel = ""
        if(isReplication):
            pathAL_root = "activeLearning"
            cwd = Path.cwd()
            dataset_path_AL_root = str(cwd/pathAL_root)             
            sourceImg = os.path.join(dataset_path_AL_root, obj[2], "images", obj[0]+".jpg")
            sourceLabel = os.path.join(dataset_path_AL_root, obj[2], "labels", obj[0]+".txt")
        else:
            sourceImg = obj[3]
            sourceLabel = obj[4]

        #move file
        newImgPath = shutil.move(sourceImg, destImg)
        #move label
        newLabelPath = shutil.move(sourceLabel, destLabels)
        obj[3] = newImgPath
        obj[4] = newLabelPath
        obj[1] = "Y"
        listToMove[index] = obj
    return listToMove
    

def Increment(val):
    print("Increment procedure started...")
    perc = val/100
    objectList, listLoaded = LoadRegistries()
    print("objects loaded? "+str(listLoaded))
    if not(listLoaded):
        Scan()
        objectList, listLoaded = LoadRegistries()
    totalNumObj = len(objectList)
    totObjToIncrement = totalNumObj*perc
    PosPerc = 0.35
    UnsPerc = 0.45
    NegPerc = 0.20
    posIncr = round(PosPerc * totObjToIncrement)
    unsIncr = round(UnsPerc * totObjToIncrement)
    negIncr = round(NegPerc * totObjToIncrement)
    print("Total: "+str(totalNumObj))
    print("To Increment: "+str(totObjToIncrement))
    print("\tPos: "+str(posIncr))
    print("\tUns: "+str(unsIncr))
    print("\tNeg: "+str(negIncr))
    toMove = list(filter(lambda x: x[1] == "N", objectList))
    rest = list(filter(lambda x: x[1] == "Y", objectList))
    posList = list(filter(lambda p: p[2] == "positive", toMove))
    posToMove = posList[:posIncr]
    rest += posList[posIncr:]
    unsList = list(filter(lambda p: p[2] == "unsure", toMove))
    unsToMove = unsList[:unsIncr]
    rest += unsList[unsIncr:]
    negList = list(filter(lambda p: p[2] == "negative", toMove))
    negToMove = negList[:negIncr]
    rest += negList[negIncr:]
    
    pathTrain = "train"
    cwd = Path.cwd()
    dataset_path_train = str(cwd/pathTrain)
    
    rest += MoveObjects(posToMove, dataset_path_train, False)
    rest += MoveObjects(unsToMove, dataset_path_train, False)
    rest += MoveObjects(negToMove, dataset_path_train, False)
    
    WriteScanResult(rest, 'objReg.json')
    print("Done!")
    
        
        

def Replicate():
    print("Replicate procedure started...")
    objectList, listLoaded = LoadRegistries()
    print("objects loaded? "+str(listLoaded))
    toMove = list(filter(lambda x: x[1] == "Y", objectList))
    
    pathTrain = "train"
    cwd = Path.cwd()
    dataset_path_train = str(cwd/pathTrain)
    
    MoveObjects(toMove, dataset_path_train, True)
    print("Done!")
    
    
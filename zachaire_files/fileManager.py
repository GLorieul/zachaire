
import errno
import os
import re
import shutil




def getExtension(filePath):
    _, extension = os.path.splitext(filePath)
    return extension

def substituteExtension(filePath, newExtension):
    pathWithoutExtension, extension = os.path.splitext(filePath)
    return pathWithoutExtension + "." + newExtension

def createParentsIfDoesNotExist(outputPath):
    outputDir = os.path.dirname(outputPath)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)






def mkdir(newDir):
    os.mkdir(newDir)

def mkdirParents(dirPath):
    os.makedirs(dirPath)


def getFileMTime(filePath):
    return os.stat(filePath).st_mtime

def getDirMTime(directory):
    latestMTime = 0
    for entry in os.scandir(directory):
        if entry.is_file():
            fileMTime = entry.stat().st_mtime
            latestMTime = max(latestMTime, fileMTime)
    return latestMTime

def getMTime(path):
    if os.path.isfile(path):
        return getFileMTime(path)
    elif os.path.isdir(path):
        return getDirMTime(path)
    else:
        raise Exception( "'path' must be either file or directory"
                       +f"\tpath = {path}")

def isNewerThan(tested, ref):
#   print(f"mTime {getMTime(tested)} vs {getMTime(ref)}")
    return getMTime(tested) > getMTime(ref)



def cp(src, dst):
    shutil.copy(src, dst)

# Taken from https://stackoverflow.com/a/1994840/3492512
def cpRecursive(src, dst):
    if os.path.isdir(dst): dst += "/" + os.path.basename(src)
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def copyFilesInDirs(srcDir, dstDir):
    for entry in os.scandir(srcDir):
        if entry.is_file():
            cp(entry.path, dstDir)



def rm(filePath):
    os.remove(filePath)

def rmRecursive(path):
    try:
        shutil.rmtree(path)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            os.remove(path)
        else: raise

def rmFilesInDirs(directory):
    for entry in os.scandir(directory):
        if entry.is_file():
            rm(entry.path)

# Taken from https://stackoverflow.com/a/12654798/3492512
def touch(filePath):
    with open(filePath, 'a'):
        os.utime(filePath, None)

def mv(src, dst):
    shutil.move(src, dst)


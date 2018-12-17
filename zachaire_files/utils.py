
import os
import sys
from zachaire_files.fileManager import parseCfgFile

def printInline(msg):
    print(msg, end=" ", flush=True)

def printBuilder(msg, end='\n', file=sys.stdout, flush=False):
    print("\t\t\t" + msg, end=end, file=file, flush=flush)

def raiseError(errMsg):
    print("Error: ", errMsg, file=sys.stderr)
    exit(1)

def getRootUrl():
    buildCfg = parseCfgFile("website.cfg")
    return buildCfg["websiteRoot"]

def getThemeUrl(themeName):
    return getRootUrl() + f"/themes/{themeName}"


def getDepth(path):
    dirPath = os.path.dirname(path)
    dirPath = os.path.normpath(dirPath)
    return _getDepth(dirPath)

def _getDepth(path):
    parentDirs = os.path.dirname(path)
    return _getDepth(parentDirs) + 1 if len(parentDirs) > 0 else 1


def getRelPathToRootUrlFrom(currentFilePath):
    """Outputs a string of the form "../../../" with as many "../" as would be
    necessary to get from the directory of 'currentFilePath' to the root of the
    website (i.e. to "out/" directory)."""
    depthOfFile = getDepth(currentFilePath)
    # Have one "../" less than there are subdirs because we want to go
    # from "./out/alpha/beta/" to "./out/" and not to "./"
    return "../"*(depthOfFile -1)


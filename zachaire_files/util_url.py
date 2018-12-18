
from .cfgParser import WebsiteCfgParser

def getRootUrl():
    buildCfg = WebsiteCfgParser("website.cfg")
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


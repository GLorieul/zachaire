
import errno
import os
import shutil


srcDir       = "content"
outDir       = "out"
templateDir  = "template"
templateHtml = os.path.join(templateDir, "template.html")
templateCss  = os.path.join(templateDir, "style.css")


def getExtension(filePath):
    _, extension = os.path.splitext(filePath)
    return extension

def copyFile(srcPath, output): # Old function : to be removed
    """'output' can be a directory or a file
    """
    outputDir = os.path.dirname(output)
    os.makedirs(outputDir, exist_ok=True)
    shutil.copy(srcPath, outputDir)


def substituteExtension(filePath, newExtension):
    pathWithoutExtension, extension = os.path.splitext(filePath)
    return pathWithoutExtension + "." + newExtension

def substituteContentDirWithOutputDir(filePath):
    isWithinContentDir = (filePath.find(srcDir) == 0)
    if not isWithinContentDir:
        raise Exception(f"File or directory is not within the \"{srcDir}/\" directory"
                        + f"\t filePath=\"{filePath}\"")
    # "max=1" => Only replace the first occurence.
    # If a subdirectory with the same name exists it will be left untouched
    # Note: thanks to the previous line we are 100% certain that
    return filePath.replace(srcDir, outDir, 1)

def copyToOutput(srcFile):
    outFile = substituteContentDirWithOutputDir(srcFile)
    copyFile(srcFile, outFile)

def getDepth(path):
    dirPath = os.path.dirname(path)
    dirPath = os.path.normpath(dirPath)
    return _getDepth(dirPath)

def _getDepth(path):
    parentDirs = os.path.dirname(path)
    return _getDepth(parentDirs) + 1 if len(parentDirs) > 0 else 1

def createParentsIfDoesNotExist(outputPath):
    outputDir = os.path.dirname(outputPath)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)






def rmRecursive():
    shutil.rmtree(directory)

def mkdir(newDir):
    os.mkdir(outDir)

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

def cp(src, dst):
    shutil.copy(src, dst)

# Taken from https://stackoverflow.com/a/1994840/3492512
def cpRecursive(src, dst):
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


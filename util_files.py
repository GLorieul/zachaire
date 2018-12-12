
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

def copyFile(srcPath, output):
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


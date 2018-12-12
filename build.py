
import os
import shutil

import galleryBuilder
import markdownBuilder_build
from util_files import *
from util_other import generateHtmlFromTemplate

srcDir       = "content"
outDir       = "out"
templateDir  = "theme/default"
templateHtml = os.path.join(templateDir, "template.html")
templateCss  = os.path.join(templateDir, "style.css")



def findInputFiles(srcDir):
    return _findSourceFiles(srcDir, [], [])

def _findSourceFiles(srcDir, srcFiles, imgDirs):
    """Explore a directory and its subdirectory in search for source files 'srcFiles' to build the *.html pages from, and image directory to copy in the final """
    for fileName in os.listdir(srcDir):
        path = os.path.join(srcDir, fileName)
        if os.path.isfile(path):
#           print("file = ", path)
            srcFiles.append(path)
        elif os.path.isdir(path):
            isAnImageDirectory = (fileName == "imgs")
            isADocumentDirectory = (fileName == "docs")
            if isAnImageDirectory or isADocumentDirectory:
#               print("img dir = ", path)
                imgDirs.append(path)
            else:
                srcFiles, imgDirs = _findSourceFiles(path, srcFiles, imgDirs)
        else:
#           print("Can't tell: path = ", path)
            exit(1)

    return srcFiles, imgDirs

def cleanOutput(outDir):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)



if __name__ == '__main__':
    srcFiles, imgDirs = findInputFiles(srcDir)
    cleanOutput(outDir)

    shutil.copy(templateCss, outDir)

    for srcFile in srcFiles:
        print(f"Generating \"{srcFile}\"")
        if getExtension(srcFile) == ".md":
            srcFileInOutputDir = srcFile.replace(srcDir, outDir, 1)
            copyFile(srcFile, srcFileInOutputDir)
            markdownBuilder_build.makeHtmlFromMarkdown(srcFileInOutputDir, templateHtml)
            os.remove(srcFileInOutputDir)
        elif getExtension(srcFile) == ".gallery":
            dirPath = os.path.dirname(srcFile) 
            galleryBuilder.build(dirPath, srcFile)
            print("srcFile = ", srcFile)
        elif getExtension(srcFile) == ".html":
            outputPath = srcFile.replace(srcDir, outDir, 1)
            createParentsIfDoesNotExist(outputPath)
            generateHtmlFromTemplate(outputPath, srcFile, templateHtml)
        elif getExtension(srcFile) == ".php":
            outputPath = srcFile.replace(srcDir, outDir, 1)
            createParentsIfDoesNotExist(outputPath)
            generateHtmlFromTemplate(outputPath, srcFile, templateHtml)

    for imgDir in imgDirs:
        outputPath = imgDir.replace(srcDir, outDir, 1)
        shutil.copytree(imgDir, outputPath)



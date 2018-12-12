
import csv
import os
import shutil
from subprocess import call

import galleryBuilder
from util_files import *

srcDir       = "content"
outDir       = "out"
templateDir  = "template"
templateHtml = os.path.join(templateDir, "template.html")
templateCss  = os.path.join(templateDir, "style.css")



def createParentsIfDoesNotExist(outputPath):
    outputDir = os.path.dirname(outputPath)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

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

def getDepth(path):
    dirPath = os.path.dirname(path)
    dirPath = os.path.normpath(dirPath)
    return _getDepth(dirPath)

def _getDepth(path):
    parentDirs = os.path.dirname(path)
    return _getDepth(parentDirs) + 1 if len(parentDirs) > 0 else 1

def cleanOutput(outDir):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)

def makeHtmlFromMarkdown(mdContentPath, htmlTemplatePath):
    # Perform the Markdown -> Html conversion
    htmlContentPath = mdContentPath.replace(".md", ".html.tmp")
    retcode = call(f"pandoc -o {htmlContentPath} {mdContentPath}", shell=True)
    if retcode > 0:
        exit(1) # TO REFACTOR !!!!

    # Include in the template
    outputPath = mdContentPath.replace(".md", ".html", 1)
    generateHtmlFromTemplate(outputPath, htmlContentPath, htmlTemplatePath)

    os.remove( htmlContentPath )

def generateHtmlFromTemplate(outputPath, contentPath, htmlTemplatePath):
    outputFileContent = []

    with open(htmlTemplatePath) as templateFile, open(contentPath) as contentFile:
        for templateLine in templateFile:
            if "<!-- Link to CSS here -->" in templateLine:
                pathToCss = os.path.join(*([".."]*(getDepth(outputPath) -1)), "style.css")
                outputFileContent.append(f"<link rel=\"stylesheet\" href=\"{pathToCss}\" />")
                "../" * getDepth(outputPath)
            elif "<!-- Include content here -->" in templateLine:
                for contentLine in contentFile:
                    outputFileContent.append(contentLine)
            elif "<!-- Include menu here -->" in templateLine:
                    outputFileContent.append("<ul class=\"menuItem\">")
                    with open('content/menu.csv', newline='') as csvfile:
                        for row in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                            linkPath = os.path.join(*([".."]*(getDepth(outputPath) -1)), row['Path'])
                            outputFileContent.append(f"<a href=\"{linkPath}\" class=\"menuItem\"><li class=\"menuItem\">{row['LinkName']}</li></a>")
                    outputFileContent.append("</ul>")
            else:
                outputFileContent.append(templateLine)

    with open(outputPath, 'w') as outputFile:
        for outputLine in outputFileContent:
            outputFile.write(outputLine)



if __name__ == '__main__':
    srcFiles, imgDirs = findInputFiles(srcDir)
    cleanOutput(outDir)

    shutil.copy(templateCss, outDir)

    for srcFile in srcFiles:
        print(f"Generating \"{srcFile}\"")
        if getExtension(srcFile) == ".md":
            srcFileInOutputDir = srcFile.replace(srcDir, outDir, 1)
            copyFile(srcFile, srcFileInOutputDir)
            makeHtmlFromMarkdown(srcFileInOutputDir, templateHtml)
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



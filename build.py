
import csv
import os
import re
import shutil
from subprocess import call

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


def copyFile(srcPath, output):
    """'output' can be a directory or a file
    """
    outputDir = os.path.dirname(output)
    os.makedirs(outputDir, exist_ok=True)
    shutil.copy(srcPath, outputDir)

def getExtension(filePath):
    _, extension = os.path.splitext(filePath)
    return extension

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


def isHeader(line):
    try:
        parseHeaderLine(line)
    except:
        return False
    return True

def isImageLine(line):
    try:
        parseImageLine(line)
    except:
        return False
    return True

def isEmptyLine(line):
    p = re.compile(r'^ *$\n?')
    m = p.match(line)
    return m != None

def parseHeaderLine(line):
    p = re.compile(r'^(##*)(.*)')
    m = p.match(line)

    if not m:
        raise Exception("Invalid syntax for header line:"
                       + f"\tFound:        \"{line}\""
                       + f"\tLegal syntax: \"# Title 1\", \"## Title 2\", etc.")

    headerMark = m.group(1)
    headerText = m.group(2)
    headerClass = len(headerMark)
    return headerClass, headerText.strip()

def translateHeader(line):
    headerClass, titleStr = parseHeaderLine(line)
    startTag = f"<h{headerClass}>"
    endTag = f"</h{headerClass}>"
    return startTag + titleStr + endTag

def extractCurrentImageRow(lines):
    for lineNb,line in enumerate(lines):
        if not isImageLine(line):
            return lines[:lineNb]

def parseImageLine(line):
    p = re.compile(r'^\[(.*)\]\[(.*)\]')
    m = p.match(line)

    if not m:
        raise Exception("Invalid syntax for image line:"
                       + f"\tFound:        \"{line}\""
                       + f"\tLegal syntax: \"[img.jpg][My caption]\"")

    imageLink = m.group(1)
    caption   = m.group(2)
    return imageLink, caption.strip()

def translateImageRow(srcLines):
    # PARSE IMAGE ROW
    imageData = []
    for line in srcLines:
        imageData.append( parseImageLine(line) )
    print(imageData)

    # WRITE THE HTML LINES
    # Write start of table
    htmlLines = "<table>"
    # Write a row for images
    htmlLines += "<tr>\n"
    for (imgLink,_) in imageData:
        imgThumbnailLink = getThumbnailName(imgLink)
        imgTag       = f"<img src=\"{imgThumbnailLink}\">"
        linkTag      = f"<a href=\"{imgLink}\">" + imgTag + "</a>"
        tableCellTag = "\t<td>" + linkTag + "</td>\n"
        htmlLines += tableCellTag
    htmlLines += "</tr>\n"
    # Write a row for captions
    htmlLines += "<tr>\n"
    for (_,caption) in imageData:
        htmlLines += "\t<td>" + caption + "</td>\n"
    htmlLines += "</tr>"
    # Write end of table
    htmlLines += "</table>"

    return htmlLines

def parse(srcLines):
    htmlLines = []
    while srcLines:
        currentLine = srcLines[0]
        print(f"\"{currentLine}\"")
        # Following this line it will be safe to test line[0]
        # because we are sure it exists
        if isEmptyLine(currentLine):
            srcLines = srcLines[1:]
        elif isHeader(currentLine):
            htmlLines.append( translateHeader(currentLine) )
            srcLines = srcLines[1:]
        elif isImageLine(currentLine):
            linesForImageRow = extractCurrentImageRow(srcLines)
            htmlLines.append( translateImageRow(linesForImageRow) )
            srcLines = srcLines[len(linesForImageRow):]
        else:
            raise Exception(  "Illegal syntax on line:\n"
                           + f"\t\"{currentLine}\"")
    return htmlLines


def getThumbnailName(fileName):
    return os.path.splitext(fileName)[0] + '_thumb.jpg'

def generateGallery(dirPath, webPageFile):

    def isImageFile(file):
        return getExtension(file) == ".jpg"

    def isAThumbnail(file):
        return file.endswith('_thumb.jpg')

    def getThumbnailName(file):
        return dirPath + '/' + os.path.splitext(fileName)[0] + '_thumb.jpg'

    def getFileMTime(file):
        return os.stat(file).st_mtime

    # Copy image to destination and generate thumbnail if necessary
    for fileName in os.listdir(dirPath):
#       print(f"Handling {fileName}")
        galleryFile = dirPath + '/' + fileName

        # Copy image to destination and generate thumbnail if necessary
        if isImageFile(galleryFile) and (not isAThumbnail(galleryFile)):
            galFileOutDir = galleryFile.replace(srcDir, outDir, 1)
            print(f"Copied to {galFileOutDir}")
            copyFile(galleryFile, galFileOutDir)

            # Generate associated thumbnail if necessary
            thumbFile = getThumbnailName(galleryFile)
            os.system("convert %s -resize x200 %s" % (galleryFile,thumbFile))
            thbFileOutDir = thumbFile.replace(srcDir, outDir, 1)
            copyFile(thumbFile, thbFileOutDir)
            print(f"Created thumbnail {thbFileOutDir}")

    print(webPageFile)
    htmlPageFile = substituteContentDirWithOutputDir(substituteExtension(webPageFile, "html"))
    print(htmlPageFile)
    with open(webPageFile,'r') as srcFile:
        srcLines = srcFile.readlines()

    htmlLines = parse(srcLines)
    print(htmlLines)

    with open(htmlPageFile,'w') as htmlFile:
        for line in htmlLines:
            htmlFile.write(line)

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
            generateGallery(dirPath, srcFile)
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



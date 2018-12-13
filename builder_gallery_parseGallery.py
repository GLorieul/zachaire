
import re
import os
from builder_gallery_util import getThumbnailName
from util_files import substituteExtension





def __isHeader(line):
    try:
        __parseHeaderLine(line)
    except:
        return False
    return True

def __isImageLine(line):
    try:
        parseImageLine(line)
    except:
        return False
    return True

def __isEmptyLine(line):
    p = re.compile(r'^ *$\n?')
    m = p.match(line)
    return m != None

def __parseHeaderLine(line):
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

def __translateHeader(line):
    headerClass, titleStr = __parseHeaderLine(line)
    startTag = f"<h{headerClass}>"
    endTag = f"</h{headerClass}>"
    return startTag + titleStr + endTag

def extractCurrentImageRow(lines):
    for lineNb,line in enumerate(lines):
        if not __isImageLine(line):
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

def __translateImageRow(srcLines):
    # PARSE IMAGE ROW
    imageData = []
    for line in srcLines:
        imageData.append( parseImageLine(line) )

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

def __parseContents(srcLines):
    htmlLines = []
    while srcLines:
        currentLine = srcLines[0]
        # Following this line it will be safe to test line[0]
        # because we are sure it exists
        if __isEmptyLine(currentLine):
            srcLines = srcLines[1:]
        elif __isHeader(currentLine):
            htmlLines.append( __translateHeader(currentLine) )
            srcLines = srcLines[1:]
        elif __isImageLine(currentLine):
            linesForImageRow = extractCurrentImageRow(srcLines)
            htmlLines.append( __translateImageRow(linesForImageRow) )
            srcLines = srcLines[len(linesForImageRow):]
        else:
            raise Exception(  "Illegal syntax on line:\n"
                           + f"\t\"{currentLine}\"")
    return htmlLines

def makeHtmlFromGalleryFile(galleryFile):
    htmlPath = substituteExtension(galleryFile, "html")
    with open(galleryFile,'r') as srcFile:
        srcLines = srcFile.readlines()

    htmlLines = __parseContents(srcLines)

    with open(htmlPath,'w') as htmlFile:
        for line in htmlLines:
            htmlFile.write(line)
    return htmlPath



import csv
import os
from .fileManager import mv, rm, cp
from .util_url import getRelPathToRootUrlFrom, getThemeUrl, getRootUrl


def injectTheme(rawHtmlFile, themeName):
    themedHtmlPath = rawHtmlFile
    mv(rawHtmlFile, rawHtmlFile + ".tmp")
    rawHtmlFile = rawHtmlFile + ".tmp"
    makeThemedHtml(themedHtmlPath, rawHtmlFile, themeName)
    rm(rawHtmlFile)

def __injectLinkToCss(htmlLines, themeName):
    linkToCss = getThemeUrl(themeName) + "/style.css"
    linkTag = f"<link rel=\"stylesheet\" href=\"{linkToCss}\" />"
    htmlLines.append(linkTag)

def __injectHtmlContent(htmlLines, htmlContentPath):
    with open(htmlContentPath) as htmlContentFile:
        for contentLine in htmlContentFile:
            htmlLines.append(contentLine)

def __injectMenu(htmlLines, themeName):
    htmlLines.append("<ul class=\"menuItem\">")
    menuPath = getThemeUrl(themeName) + "/menu.csv"
    with open(menuPath, newline='') as menuFile:
        csvMenuReader = csv.DictReader(menuFile, delimiter=',', quotechar='"')
        for row in csvMenuReader:
            linkLabel = row['LinkLabel']
            linkTargetFromRoot  = row['PathOfTarget']
            linkTarget = getRootUrl() + "/" + linkTargetFromRoot
            listItemTag = "<li class=\"menuItem\">" + linkLabel + "</li>"
            linkTag = (f"<a href=\"{linkTarget}\" class=\"menuItem\">"
                      + listItemTag + "</a>")
            htmlLines.append(linkTag)
    htmlLines.append("</ul>")

def makeThemedHtml(outFilePath, htmlContentPath, themeName):
    themeHtmlPath = f"themes/{themeName}/template.html"
    workDir = os.path.dirname(htmlContentPath)

    htmlLines = []
    with open(themeHtmlPath, 'r') as themeHtmlFile:
        for templateLine in themeHtmlFile:
            if "<!-- Link to CSS here -->" in templateLine:
                __injectLinkToCss(htmlLines, themeName)
            elif "<!-- Include content here -->" in templateLine:
                __injectHtmlContent(htmlLines, htmlContentPath)
            elif "<!-- Include menu here -->" in templateLine:
                __injectMenu(htmlLines, themeName)
            else:
                htmlLines.append(templateLine)

    with open(outFilePath, 'w') as outputFile:
        for outputLine in htmlLines:
            outputFile.write(outputLine)


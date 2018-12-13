
import csv
import os
from util_files import getDepth, mv, rm, cp


def injectTheme(rawHtmlFile, themeName):
    themedHtmlPath = rawHtmlFile
    mv(rawHtmlFile, rawHtmlFile + ".tmp")
    rawHtmlFile = rawHtmlFile + ".tmp"
    makeThemedHtml(themedHtmlPath, rawHtmlFile, themeName)
    rm(rawHtmlFile)

    # Note that the same css file will be duplicated: one copy in each subdir
    # Not a problem because:
    #  1. There is one parent css file ("theme/[...]/style.css").
    #     Hence adjusting css values implies changing one file only (and not
    #     each copy)
    #  2. Code duplication is usually considered a code smell in soft dev.
    #     However note that there is also duplication of the theme html code:
    #     the content of "theme/[...]/template.html" ends up in every *.html
    #     file. Hence it is not more awful to duplicate the css code as it is
    #     to duplicate the html.
    #  3. Besides, it is simpler to work with one css file in each subdirectory
    #     because it is consistent with the general philosophy of Zachaire:
    #     each subdir is treated (and built) independantly. On the other hand,
    #     a shared *.css file accross all subdirectories would violate this
    #     philosophy.


def __injectLinkToCss(htmlLines):
    linkToCss = f"<link rel=\"stylesheet\" href=\"style.css\" />"
    htmlLines.append( linkToCss )

def __injectHtmlContent(htmlLines, htmlContentPath):
    with open(htmlContentPath) as htmlContentFile:
        for contentLine in htmlContentFile:
            htmlLines.append(contentLine)

def __injectMenu(htmlLines, outFilePath):
    htmlLines.append("<ul class=\"menuItem\">")
    with open('content/menu.csv', newline='') as menuFile:
        csvMenuReader = csv.DictReader(menuFile, delimiter=',', quotechar='"')
        for row in csvMenuReader:
            linkPath = os.path.join(*([".."]*(getDepth(outFilePath) -1)), row['Path'])
            listItemTag = "<li class=\"menuItem\">{row['LinkName']}</li>"
            linkTag = (f"<a href=\"{linkPath}\" class=\"menuItem\">"
                      + listItemTag + "</a>")
            htmlLines.append(linkTag)
    htmlLines.append("</ul>")

def makeThemedHtml(outFilePath, htmlContentPath, themeName):
    themeHtmlPath = f"theme/{themeName}/template.html"
    themeCssPath = f"theme/{themeName}/style.css"
    workDir = os.path.dirname(htmlContentPath)
    cp(themeCssPath, workDir)
    htmlLines = []

    with open(themeHtmlPath) as themeHtmlFile:
        for templateLine in themeHtmlFile:
            if "<!-- Link to CSS here -->" in templateLine:
                __injectLinkToCss(htmlLines)
            elif "<!-- Include content here -->" in templateLine:
                __injectHtmlContent(htmlLines, htmlContentPath)
            elif "<!-- Include menu here -->" in templateLine:
                __injectMenu(htmlLines, outFilePath)
            else:
                htmlLines.append(templateLine)

    with open(outFilePath, 'w') as outputFile:
        for outputLine in htmlLines:
            outputFile.write(outputLine)


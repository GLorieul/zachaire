
import csv
import os
from util_files import getDepth, mv, rm, cp


def injectTheme(rawHtmlFile, themeName):
    workDir = os.path.dirname(rawHtmlFile)
    themeHtml = f"theme/{themeName}/template.html"
    themeCss = f"theme/{themeName}/style.css"
    themedHtmlPath = rawHtmlFile
    mv(rawHtmlFile, rawHtmlFile + ".tmp")
    rawHtmlFile = rawHtmlFile + ".tmp"
    makeThemedHtml(themedHtmlPath, rawHtmlFile, themeHtml)
    rm(rawHtmlFile)

    cp(themeCss, workDir)
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


def makeThemedHtml(outputPath, contentPath, htmlTemplatePath):
    outputFileContent = []

    with open(htmlTemplatePath) as templateFile, open(contentPath) as contentFile:
        for templateLine in templateFile:
            if "<!-- Link to CSS here -->" in templateLine:
                pathToCss = "style.css"
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


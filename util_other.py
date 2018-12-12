
import csv
import os
from util_files import getDepth

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


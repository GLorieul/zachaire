
import os
from subprocess import call
from util_other import generateHtmlFromTemplate

def makeHtmlFromMarkdown(mdContentPath, htmlTemplatePath):
    # Perform the Markdown -> Html conversion
    htmlContentPath = mdContentPath.replace(".md", ".html.tmp")
    retcode = call(f"pandoc -o {htmlContentPath} {mdContentPath}", shell=True)
    if retcode > 0:
        raise Exception("Pandoc returned non-zero return code")

    # Include in the template
    outputPath = mdContentPath.replace(".md", ".html", 1)
    generateHtmlFromTemplate(outputPath, htmlContentPath, htmlTemplatePath)

    os.remove( htmlContentPath )


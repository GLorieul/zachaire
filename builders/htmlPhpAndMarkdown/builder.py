
import os
import subprocess
from zachaire_files.fileManager import getExtension, rm
from zachaire_files.themeHtmlInjector import injectTheme
from zachaire_files.utils import printBuilder


def __makeHtmlFromMarkdown(mdPath):
    # Perform the Markdown -> Html conversion
    htmlPath = mdPath.replace(".md", ".html")
    cmd = f"pandoc -o {htmlPath} {mdPath}"
    returnCode = subprocess.call(cmd, shell=True)
    if returnCode > 0:
        raise Exception( "Pandoc returned non-zero return code:\n"
                       +f"\treturnCode = {returnCode}")
    return htmlPath



def __generateAsMarkdown(mdFile, themeName):
    htmlFile = __makeHtmlFromMarkdown(mdFile)
    injectTheme(htmlFile, themeName)
    rm(mdFile)

def __generateAsHtml(rawHtmlFile, themeName):
    injectTheme(rawHtmlFile, themeName)

def __generateAsPhp(rawPhpFile, themeName):
    injectTheme(rawPhpFile, themeName)

actionForEachExt = {".md" :__generateAsMarkdown, ".html":__generateAsHtml,
                    ".php":__generateAsPhp     }

def build(subdirToBuild, dirBuildCfg):
    themeName = dirBuildCfg["themeToUse"]
    for srcFile in os.scandir(subdirToBuild):
        if srcFile.is_file(): #Filter out subdirs
            fileExt = getExtension(srcFile)
            if fileExt in actionForEachExt: #Filter out images, etc.
                printBuilder(f"Generating from \"{srcFile.path}\"…")
                generator = actionForEachExt[fileExt]
                generator(srcFile.path, themeName)



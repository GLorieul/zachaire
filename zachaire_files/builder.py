
import os
import shutil

from builders.htmlPhpAndMarkdown import builder as htmlPhpAndMarkdownBuilder
from builders.gallery import builder as galleryBuilder
import zachaire_files.fileManager as fm
from .cfgParser import DirBuildingCfgParser
from .fileManager import isNewerThan, mkdirParents, getExtension
from .utils import raiseError, raiseWarning, printInline
from .util_url import getThemeUrl, getRootUrl

contentDir = "content"
outDir     = "out"



def __isSubdirBuildable():
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")

def __isSubdirBuildable(outSubdir):
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")
def __isSubdirToBuild(outSubdir):
    return os.path.isfile(outSubdir + "/.dirNeedsToBeBuilt")

def __getBuilder(builderName):
    builders = {"htmlPhpAndMarkdown":htmlPhpAndMarkdownBuilder,
                "gallery":galleryBuilder}
    try:
        return builders[builderName]
    except:
        raise Exception( "Unknown builder: builderToUse = "
                       +f"\"{buildCfg['builderToUse']}\"")

def __assertContentDirDoesNotContainReservedFile(path):
    if os.path.exists("content/" + path):
        raiseError(f"\"content/\" directory contains reserved file/dir \"{path}\"")

def __assertWebsiteCfgFileExists():
    if not os.path.isfile("website.cfg"):
        raiseError("File \"/website.cfg\" is required but none could be found…")

def __substituteContentDirWithOutputDir(filePath):
    isWithinContentDir = (filePath.find(contentDir) == 0)
    if not isWithinContentDir:
        raise Exception(f"File or directory is not within the \"{contentDir}/\" directory"
                        + f"\t filePath=\"{filePath}\"")
    # "max=1" => Only replace the first occurence.
    # If a subdirectory with the same name exists it will be left untouched
    # Note: thanks to the previous line we are 100% certain that
    return filePath.replace(contentDir, outDir, 1)


def __injectThemeUrlInCss(cssFilePath, themeName):
    """Inject website theme url in *.css file

    Example of theme url: 'http://www.myWebsite.com/themes/myTheme'

    Typical *.css files must contain links to images that are part of the
    page's theme (e.g. "background-images" CSS tags). Those images must be
    refered to using absolute links e.g.
    "url('http://www.myWebsite.com/themes/myTheme/imgs/img.jpg". However the
    theme template files contained "/themes/" do not know what the website's
    root is ("http://www.myWebsite.com/" in that case). Hence they specify
    links in the form "url('<themeUrl>/imgs/img.jpg')", where the <themeUrl>
    tag must be substituted with the website root url + path to "themes/"
    directory (i.e. 'http://www.myWebsite.com/themes/myTheme'). The present
    function performs this substitution.
    """
    # Parse css file
    alteredCssLines = []
    with open(cssFilePath, 'r') as cssFile:
        for line in cssFile:
            alteredLine = line.replace("<themeUrl>", getThemeUrl(themeName))
            alteredCssLines.append(alteredLine)

    # With the following line, the *.css file we just read from is emptied
    # of all its contents and written again with the atoms of alteredCssLines.
    with open(cssFilePath, 'w') as cssFile:
        for line in alteredCssLines:
            cssFile.write(line)

def __isCssFile(fileName):
    return getExtension(fileName) == ".css"



def __buildTheme():
    if not os.path.exists("out"): os.mkdir("out/")
    print("Building themes:")

    # DISPLAY LIST OF THEMES
    printInline("\tAvailable themes in \"/themes/\":")
    allThemes = os.listdir("themes/")
    for themeDir in allThemes:
        printInline(f"\"{themeDir}\"")
        [print() if themeDir==allThemes[-1] else print(", ")]
    if not allThemes:
        print("(None)")
        raiseWarning("No theme could be found in \"/theme/\"\n"
                    +"The \"/theme/\" folder should contain one sub-directory "
                    +"for each theme")

    # BUILD THEME
    # Always build the theme because (i) it's simpler this way and
    # (ii) it's tiny hence barely costs anything
    if os.path.exists("out/themes"): fm.rmRecursive("out/themes")
    fm.mkdir("out/themes")

    for themeDir in os.scandir("themes/"):
        if not themeDir.is_dir(): continue # Skip files, etc.

        srcPath = f"themes/{themeDir.name}/"
        dstPath = f"out/themes/{themeDir.name}/"
        printInline(f"\tBuilding theme \"{themeDir.name}\": "
                   +f"\"/{srcPath}\" -> \"/{dstPath}\"…")

        # Copy theme dir's contents (except "template.html")
        themeName = themeDir.name
        fm.mkdir(dstPath)
        for themeFile in os.scandir(srcPath):
            fileName = themeFile.name
            outThemeFile = dstPath + "/" + fileName
            if fileName == "template.html": continue # Skip
            fm.cpRecursive(themeFile.path, outThemeFile)
            if __isCssFile(fileName): __injectThemeUrlInCss(outThemeFile, themeName)
        print("Done!")
    print()


def __mustSubdirBeIgnored(subdirPath):
    if "/.git/" in subdirPath: return True
    if subdirPath.endswith("/.git"): return True
    return False

def __needsRefreshing(srcSubdir):
    outSubdir = __substituteContentDirWithOutputDir(srcSubdir)
    existsOutSubdir = os.path.isdir(outSubdir)
    isSrcNewer = lambda : isNewerThan(srcSubdir, outSubdir)
    return True if not existsOutSubdir else isSrcNewer()


def __buildContent():
    srcSubdirs = [x[0] for x in os.walk(contentDir)]
    print("Building content:")

    # FIND BUIDLABLE DIRECTORIES
    subDirsToRefresh = []
    buildableSubDirs = []
    for srcSubdir in srcSubdirs:
        if __mustSubdirBeIgnored(srcSubdir): continue
        if __needsRefreshing(srcSubdir): subDirsToRefresh.append(srcSubdir)
        if __isSubdirBuildable(srcSubdir): buildableSubDirs.append(srcSubdir)

    # DISPLAY SUB-DIRECTORIES FOUND

    print("\tBuildable sub-directories:")
    # Up-to-date subDirs
    upToDateSubDirs = set(buildableSubDirs).difference(subDirsToRefresh)
    for subDir in upToDateSubDirs: print(f"\t\t(Up-to-date) \"/{subDir}\"")
    # SubDirs to update
    subDirsToUpdate = set(buildableSubDirs).intersection(subDirsToRefresh)
    for subDir in subDirsToUpdate: print(f"\t\t(To build)   \"/{subDir}\"")
    # No buildable subDirs
    if not buildableSubDirs:
            print("\t\t(None)")
            print("\t\tPlace a \"dirBuilding.cfg\" file in each sub-dir to build.")

    # COPYING CONTENT
    print("\tCopying content:")
    for srcSubdir in subDirsToRefresh:
        outSubdir = __substituteContentDirWithOutputDir(srcSubdir)
        printInline(f"\t\tCopying sub-directory "
                   +f"\"/{srcSubdir}/\" -> \"/{outSubdir}/\"…")
        existsOutSubdir = os.path.isdir(outSubdir)
        if not existsOutSubdir: mkdirParents(outSubdir)
        fm.rmFilesInDirs(outSubdir)
        fm.copyFilesInDirs(srcSubdir, outSubdir)
        print("Done!")
    if not subDirsToRefresh: print("\t\tNo content to copy")

    # BULDING CONTENT
    print("\tBuilding content:")
    for srcSubdir in subDirsToUpdate:
        outSubdir = __substituteContentDirWithOutputDir(srcSubdir)
        dirBuildCfg = DirBuildingCfgParser(outSubdir + "/dirBuilding.cfg")
        print(f"\t\tBuilding \"{outSubdir}/\" with "
             +f"\"{dirBuildCfg['builderToUse']}\" builder…")
        builder = __getBuilder(dirBuildCfg["builderToUse"])
        builder.build(outSubdir, dirBuildCfg)
        print("\t\t\tDone!")
    if not subDirsToUpdate:
        print("\t\tNo content to build")
    print()

def build():
    fm.touch("content/index.html") #For debug: force building of "content/" dir
#   fm.touch("content/photos/2017-09-xx_xianBeijing/photos.gallery")
    print(f"The root of the website is set at the URL: \"{getRootUrl()}\"")
    __assertContentDirDoesNotContainReservedFile("themes")
    __assertWebsiteCfgFileExists()
    __buildTheme()
    __buildContent()



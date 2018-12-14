
import configparser
import os
import shutil

from builders.htmlPhpAndMarkdown import builder as htmlPhpAndMarkdownBuilder
from builders.gallery import builder as galleryBuilder
import util_files as fl
from util_files import isNewerThan, mkdirParents, parseCfgFile, getExtension
from util_misc import getThemeUrl, raiseError

contentDir = "content"
outDir     = "out"



def __isSubdirBuildable():
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")

def __flagAsToBeBuilt(outSubdir):
    fl.touch(outSubdir + "/.dirNeedsToBeBuilt")

def __releaseFlag_toBeBuilt(outSubdir):
    fl.rm(outSubdir + "/.dirNeedsToBeBuilt")

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

    Example of theme url: 'http://www.myWebsite.com/theme/myTheme'

    Typical *.css files must contain links to images that are part of the
    page's theme (e.g. "background-images" CSS tags). Those images must be
    refered to using absolute links e.g.
    "url('http://www.myWebsite.com/theme/myTheme/imgs/img.jpg". However the
    theme template files contained "/theme/" do not know what the website's
    root is ("http://www.myWebsite.com/" in that case). Hence they specify
    links in the form "url('<themeUrl>/imgs/img.jpg')", where the <themeUrl>
    tag must be substituted with the website root url + path to "theme/"
    directory (i.e. 'http://www.myWebsite.com/theme/myTheme'). The present
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


if __name__ == '__main__':
    __assertContentDirDoesNotContainReservedFile("theme")

    # BUILD THEME
    # Always build the theme because (i) it's simpler this way and
    # (ii) it's tiny hence barely costs anything
    print("Copying contents of \"/theme/\" directory in output directory \"/out/theme/\" …")
    if os.path.exists("out/theme"): fl.rmRecursive("out/theme")
    fl.mkdir("out/theme")

    for themeDir in os.scandir("theme/"):
        print(f"\tCopying theme \"{themeDir.name}\"…")
        if not themeDir.is_dir(): # Skip files, etc.
            continue

        # Copy theme dir's contents (except "template.html")
        themeName = themeDir.name
        fl.mkdir("out/theme/" + themeName)
        for themeFile in os.scandir("theme/" + themeName):
            if themeFile.name == "template.html":
                continue # Skip

            outThemeDir = "out/theme/" + themeName
            outFilePath = outThemeDir +"/"+ themeFile.name
            fl.cpRecursive(themeFile.path, outFilePath)

            if getExtension(themeFile.name) == ".css":
                __injectThemeUrlInCss(outFilePath, themeName)

    # BUILD CONTENT
#   fl.touch("content/index.html") #For debug: force building of "content/" dir
#   fl.touch("content/photos/2017-09-xx_xianBeijing/photos.gallery")
    # COPY SRC TO OUTPUT DIRECTORY + FLAG SUBDIRS THAT NEED TO BE BUILT
    print("Copying contents that have changed…", end=" ", flush=True)
    srcSubdirs = [x[0] for x in os.walk(contentDir)]
    for srcSubdir in srcSubdirs:
        outSubdir = __substituteContentDirWithOutputDir(srcSubdir)
        existsOutSubdir = os.path.isdir(outSubdir)
        isSrcNewer = lambda : isNewerThan(srcSubdir, outSubdir)
        needsCopying = True if not existsOutSubdir else isSrcNewer()
        if needsCopying:
            if not existsOutSubdir: mkdirParents(outSubdir)
            fl.rmFilesInDirs(outSubdir)
            fl.copyFilesInDirs(srcSubdir, outSubdir)
            if __isSubdirBuildable(outSubdir):
                __flagAsToBeBuilt(outSubdir)
    print("Done!")

    # BUILD EACH FLAGGED SUBDIR
    outSubdirs = [x[0] for x in os.walk(outDir)]
    for outSubdir in outSubdirs:
        if __isSubdirBuildable(outSubdir) and __isSubdirToBuild(outSubdir):
            dirBuildCfg = parseCfgFile(outSubdir + "/dirBuilding.cfg")
            print(f"Building \"{outSubdir}/\" with "
                 +f"\"{dirBuildCfg['builderToUse']}\" builder…") #, end="", flush=False)
            builder = __getBuilder(dirBuildCfg["builderToUse"])
            builder.build(outSubdir, dirBuildCfg)
            __releaseFlag_toBeBuilt(outSubdir)



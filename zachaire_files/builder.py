
import os
import shutil

from builders.htmlPhpAndMarkdown import builder as htmlPhpAndMarkdownBuilder
from builders.gallery import builder as galleryBuilder
import zachaire_files.fileManager as fm
from .fileManager import isNewerThan, mkdirParents, parseCfgFile, getExtension
from .utils import getThemeUrl, raiseError

contentDir = "content"
outDir     = "out"



def __isSubdirBuildable():
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")

def __flagAsToBeBuilt(outSubdir):
    fm.touch(outSubdir + "/.dirNeedsToBeBuilt")

def __releaseFlag_toBeBuilt(outSubdir):
    fm.rm(outSubdir + "/.dirNeedsToBeBuilt")

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



def __buildTheme():
    # BUILD THEME
    # Always build the theme because (i) it's simpler this way and
    # (ii) it's tiny hence barely costs anything
    print("Copying contents of \"/themes/\" directory in output directory \"/out/themes/\" …")
    if os.path.exists("out/themes"): fm.rmRecursive("out/themes")
    fm.mkdir("out/themes")

    for themeDir in os.scandir("themes/"):
        print(f"\tCopying theme \"{themeDir.name}\"…")
        if not themeDir.is_dir(): # Skip files, etc.
            continue

        # Copy theme dir's contents (except "template.html")
        themeName = themeDir.name
        fm.mkdir("out/themes/" + themeName)
        for themeFile in os.scandir("themes/" + themeName):
            if themeFile.name == "template.html":
                continue # Skip

            outThemeDir = "out/themes/" + themeName
            outFilePath = outThemeDir +"/"+ themeFile.name
            fm.cpRecursive(themeFile.path, outFilePath)

            if getExtension(themeFile.name) == ".css":
                __injectThemeUrlInCss(outFilePath, themeName)


def __buildContent():
    # COPY SRC TO OUTPUT DIRECTORY + FLAG SUBDIRS THAT NEED TO BE BUILT
    print("Copying content sub-directories from \"content/\" "
         +"to output directory \"out/\"…", end=" ", flush=True)
    srcSubdirs = [x[0] for x in os.walk(contentDir)]
    for srcSubdir in srcSubdirs:
        outSubdir = __substituteContentDirWithOutputDir(srcSubdir)
        existsOutSubdir = os.path.isdir(outSubdir)
        isSrcNewer = lambda : isNewerThan(srcSubdir, outSubdir)
        needsCopying = True if not existsOutSubdir else isSrcNewer()
        if needsCopying:
            if not existsOutSubdir: mkdirParents(outSubdir)
            fm.rmFilesInDirs(outSubdir)
            fm.copyFilesInDirs(srcSubdir, outSubdir)
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

def build():
    fm.touch("content/index.html") #For debug: force building of "content/" dir
#   fm.touch("content/photos/2017-09-xx_xianBeijing/photos.gallery")
    __assertContentDirDoesNotContainReservedFile("themes")
    __buildTheme()
    __buildContent()



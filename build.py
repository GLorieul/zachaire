
import configparser
import os
import shutil

import builder_htmlPhpAndMarkdown
import builder_gallery
from util_files import *

srcDir       = "content"
outDir       = "out"
templateDir  = "theme/default"
templateHtml = os.path.join(templateDir, "template.html")
templateCss  = os.path.join(templateDir, "style.css")


def getBuildCfg(cfgPath):
    with open(cfgPath, 'r') as cfgFile:
        cfgFileContent = '[Dummy section]\n' + cfgFile.read()
    buildCfg = configparser.ConfigParser()
    buildCfg.read_string(cfgFileContent)
    return buildCfg["Dummy section"]


def __isSubdirBuildable():
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")

def __flagAsToBeBuilt(outSubdir):
    touch(outSubdir + "/.dirNeedsToBeBuilt")

def __releaseFlag_toBeBuilt(outSubdir):
    rm(outSubdir + "/.dirNeedsToBeBuilt")

def __isSubdirBuildable(outSubdir):
    return os.path.isfile(outSubdir + "/dirBuilding.cfg")
def __isSubdirToBuild(outSubdir):
    return os.path.isfile(outSubdir + "/.dirNeedsToBeBuilt")

def __getBuilder(builderName):
    builders = {"htmlPhpAndMarkdown":builder_htmlPhpAndMarkdown,
                "gallery":builder_gallery}
    try:
        return builders[builderName]
    except:
        raise Exception( "Unknown builder: builderToUse = "
                       +f"\"{buildCfg['builderToUse']}\"")


if __name__ == '__main__':
    # COPY SRC TO OUTPUT DIRECTORY + FLAG SUBDIRS THAT NEED TO BE BUILT
    print("Copying contents that have changed…", end=" ", flush=True)
    srcSubdirs = [x[0] for x in os.walk(srcDir)]
    for srcSubdir in srcSubdirs:
        outSubdir = substituteContentDirWithOutputDir(srcSubdir)
        existsOutSubdir = os.path.isdir(outSubdir)
        isSrcNewer = lambda : isNewerThan(srcSubdir, outSubdir)
        needsCopying = True if not existsOutSubdir else isSrcNewer()
        if needsCopying:
            if not existsOutSubdir: mkdirParents(outSubdir)
            rmFilesInDirs(outSubdir)
            copyFilesInDirs(srcSubdir, outSubdir)
            if __isSubdirBuildable(outSubdir):
                __flagAsToBeBuilt(outSubdir)
    print("Done!")

    # BUILD EACH FLAGGED SUBDIR
    outSubdirs = [x[0] for x in os.walk(outDir)]
    for outSubdir in outSubdirs:
        if __isSubdirBuildable(outSubdir) and __isSubdirToBuild(outSubdir):
            buildCfg = getBuildCfg(outSubdir + "/dirBuilding.cfg")
            print(f"Building \"{outSubdir}/\" with "
                 +f"\"{buildCfg['builderToUse']}\" builder…") #, end="", flush=False)
            builder = __getBuilder(buildCfg["builderToUse"])
            builder.build(outSubdir, buildCfg)
            __releaseFlag_toBeBuilt(outSubdir)



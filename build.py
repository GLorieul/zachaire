
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



def findInputFiles(srcDir):
    return _findSourceFiles(srcDir, [], [])

def _findSourceFiles(srcDir, srcFiles, imgDirs):
    """Explore a directory and its subdirectory in search for source files 'srcFiles' to build the *.html pages from, and image directory to copy in the final """
    for fileName in os.listdir(srcDir):
        path = os.path.join(srcDir, fileName)
        if os.path.isfile(path):
#           print("file = ", path)
            srcFiles.append(path)
        elif os.path.isdir(path):
            isAnImageDirectory = (fileName == "imgs")
            isADocumentDirectory = (fileName == "docs")
            if isAnImageDirectory or isADocumentDirectory:
#               print("img dir = ", path)
                imgDirs.append(path)
            else:
                srcFiles, imgDirs = _findSourceFiles(path, srcFiles, imgDirs)
        else:
#           print("Can't tell: path = ", path)
            exit(1)

    return srcFiles, imgDirs

def cleanOutput(outDir):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)







def getBuildCfg(cfgPath):
    with open(cfgPath, 'r') as cfgFile:
        cfgFileContent = '[Dummy section]\n' + cfgFile.read()
    buildCfg = configparser.ConfigParser()
    buildCfg.read_string(cfgFileContent)
    return buildCfg["Dummy section"]


# NEW MAIN
if __name__ == '__main__':
    # COPY SRC TO OUTPUT DIRECTORY AND FLAG SUBDIRS THAT NEED TO BE BUILT
    print("Copying contents that have changed…", end=" ", flush=True)
    srcSubdirs = [x[0] for x in os.walk(srcDir)]
    for srcSubdir in srcSubdirs:
        outSubdir  = substituteContentDirWithOutputDir(srcSubdir)
        doesOutputSubdirExist = os.path.isdir(outSubdir)
        isSrcNewer = None
        if doesOutputSubdirExist:
            mTimeSrc   = getDirMTime(srcSubdir)
            mTimeOut   = getDirMTime(outSubdir)
            isSrcNewer = (mTimeSrc > mTimeOut)
        if (not doesOutputSubdirExist) or isSrcNewer:
            if doesOutputSubdirExist:
                rmFilesInDirs(outSubdir)
            else:
                mkdirParents(outSubdir)
            copyFilesInDirs(srcSubdir, outSubdir)

            # FLAG SUBDIR IF NEED BE
            # Directories are to be fed to builder have a "dirBuilding.cfg" file
            # whereas directories containing raw data don't have that file
            isSubdirBuildable = os.path.isfile(outSubdir + "/dirBuilding.cfg")
            if isSubdirBuildable:
                touch(outSubdir + "/.dirNeedsToBeBuilt")
    print("Done!")

    # BUILD EACH FLAGGED SUBDIR
    outSubdirs = [x[0] for x in os.walk(outDir)]
    for outSubdir in outSubdirs:
        isSubdirBuildable = os.path.isfile(outSubdir + "/dirBuilding.cfg")
        isSubdirToBuild = os.path.isfile(outSubdir + "/.dirNeedsToBeBuilt")
        if isSubdirBuildable and isSubdirToBuild:
            buildCfg = getBuildCfg(outSubdir + "/dirBuilding.cfg")

            print(f"Building \"{outSubdir}/\" with "
                 +f"\"{buildCfg['builderToUse']}\" builder…") #, end="", flush=False)
            if buildCfg["builderToUse"] == "htmlPhpAndMarkdown":
                builder_htmlPhpAndMarkdown.build(outSubdir, buildCfg)
            elif buildCfg["builderToUse"] == "gallery":
                builder_gallery.build(outSubdir, buildCfg)
            else:
                raise Exception( "Unknown builder: "
                               +f"builderToUse = \"{buildCfg['builderToUse']}\"")

            rm(outSubdir + "/.dirNeedsToBeBuilt")




# OLD MAIN
#if __name__ == '__main__':
#    srcFiles, imgDirs = findInputFiles(srcDir)
#    cleanOutput(outDir)
#
#    shutil.copy(templateCss, outDir)
#
#    for srcFile in srcFiles:
#        print(f"Generating \"{srcFile}\"")
#        if getExtension(srcFile) == ".md":
#            srcFileInOutputDir = srcFile.replace(srcDir, outDir, 1)
#            copyFile(srcFile, srcFileInOutputDir)
#            markdownBuilder_build.makeHtmlFromMarkdown(srcFileInOutputDir, templateHtml)
#            os.remove(srcFileInOutputDir)
#        elif getExtension(srcFile) == ".gallery":
#            dirPath = os.path.dirname(srcFile) 
#            galleryBuilder.build(dirPath, srcFile)
#            print("srcFile = ", srcFile)
#        elif getExtension(srcFile) == ".html":
#            outputPath = srcFile.replace(srcDir, outDir, 1)
#            createParentsIfDoesNotExist(outputPath)
#            generateHtmlFromTemplate(outputPath, srcFile, templateHtml)
#        elif getExtension(srcFile) == ".php":
#            outputPath = srcFile.replace(srcDir, outDir, 1)
#            createParentsIfDoesNotExist(outputPath)
#            generateHtmlFromTemplate(outputPath, srcFile, templateHtml)
#
#    for imgDir in imgDirs:
#        outputPath = imgDir.replace(srcDir, outDir, 1)
#        shutil.copytree(imgDir, outputPath)




import os
from util_files import getExtension, rm
from builders.gallery.util import getThumbnailName
from builders.gallery.parseGallery import makeHtmlFromGalleryFile
from util_theme import injectTheme

def __isImageFile(path):
    return getExtension(path) == ".jpg"
def __isAThumbnail(path):
    return path.endswith('_thumb.jpg')
def __isGalleryFile(path):
    return path.endswith('.gallery')

def __makeThumbnail(rawImg):
    thumbImg = getThumbnailName(rawImg)
    os.system("convert %s -resize x200 %s" % (rawImg, thumbImg))


def build(subdirToBuild, dirBuildCfg):
    themeName = dirBuildCfg.get("themeToUse")
    for srcFile in os.scandir(subdirToBuild):
        print("\t" + srcFile.path)
        if srcFile.is_file(): #Filter out subdirs
            if __isImageFile(srcFile.name):
                rawImg = srcFile.path
                __makeThumbnail(rawImg)
            elif __isGalleryFile(srcFile.name):
                galleryFile = srcFile.path
                htmlFile = makeHtmlFromGalleryFile(galleryFile)
                rm(galleryFile)
                injectTheme(htmlFile, themeName)


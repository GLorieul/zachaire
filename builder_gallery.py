
import os
from util_files import getExtension, rm
from builder_gallery_util import getThumbnailName
from builder_gallery_parseGallery import makeHtmlFromGalleryFile
from util_theme import injectTheme

def isImageFile(path):
    return getExtension(path) == ".jpg"
def isAThumbnail(path):
    return path.endswith('_thumb.jpg')
def isGalleryFile(path):
    return path.endswith('.gallery')

def makeThumbnail(rawImg):
    thumbImg = getThumbnailName(rawImg)
    os.system("convert %s -resize x200 %s" % (rawImg, thumbImg))


def build(subdirToBuild, buildCfg):
    themeName = buildCfg.get("themeToUse", "default")
    for srcFile in os.scandir(subdirToBuild):
        print("\t" + srcFile.path)
        if srcFile.is_file(): #Filter out subdirs
            if isImageFile(srcFile.name):
                rawImg = srcFile.path
                makeThumbnail(rawImg)
            elif isGalleryFile(srcFile.name):
                galleryFile = srcFile.path
                htmlFile = makeHtmlFromGalleryFile(galleryFile)
                rm(galleryFile)
                injectTheme(htmlFile, themeName)


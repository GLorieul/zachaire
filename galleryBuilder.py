
import os
from util_files import getExtension, copyToOutput
import parseGallery


def build(dirPath, webPageFile):

    def isImageFile(file):
        return getExtension(file) == ".jpg"

    def isAThumbnail(file):
        return file.endswith('_thumb.jpg')

    def getThumbnailName(file):
        return dirPath + '/' + os.path.splitext(fileName)[0] + '_thumb.jpg'

    def getFileMTime(file):
        return os.stat(file).st_mtime

    # Copy image to destination and generate thumbnail if necessary
    for fileName in os.listdir(dirPath):
        galleryFile = dirPath + '/' + fileName

        # Copy image to destination and generate thumbnail if necessary
        if isImageFile(galleryFile) and (not isAThumbnail(galleryFile)):
            copyToOutput(galleryFile)

            # Generate associated thumbnail if necessary
            thumbFile = getThumbnailName(galleryFile)
            os.system("convert %s -resize x200 %s" % (galleryFile,thumbFile))
            copyToOutput(thumbFile)

    parseGallery.parseGalleryFile(webPageFile)


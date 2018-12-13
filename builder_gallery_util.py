
import os

def getThumbnailName(fileName):
    return os.path.splitext(fileName)[0] + '_thumb.jpg'


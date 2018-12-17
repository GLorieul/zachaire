
import os
from .fileManager import rmRecursive, mkdir
from .utils import printInline

def clean():
    printInline("Cleaning outputs…")
    if os.path.exists("out/"): rmRecursive("out/")
    mkdir("out/")
    print("Done!")


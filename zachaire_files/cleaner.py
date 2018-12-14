
import os
from zachaire_files.fileManager import rmRecursive, mkdir

def clean():
    print("Cleaning outputs…", end=" ", flush=True)
    if os.path.exists("out/"): rmRecursive("out/")
    mkdir("out/")
    print("Done!")


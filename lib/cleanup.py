import shutil
import os


def cleanup():
    if os.path.isdir("audio-chunks"):
        shutil.rmtree("audio-chunks")
    if os.path.isdir("raw-audio"):
        shutil.rmtree("raw-audio")

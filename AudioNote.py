from utils.speech2text import convert2text
from utils.record import record_audio
from utils.summary import summarize_text
import os
import shutil

# clean directories
if os.path.isdir("recording"):
    shutil.rmtree("recording")
if os.path.isdir("results"):
    shutil.rmtree("results")

# record audio
path = record_audio()

# convert to text
file_path, file_date = convert2text(path)

# create summary file
summarize_text(file_path, file_date)

print("Transcription complete!")
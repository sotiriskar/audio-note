from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, logging
from deepmultilingualpunctuation import PunctuationModel

# from textblob import TextBlob
from threading import Thread
import soundfile as sf

import textwrap
import datetime
import warnings

import librosa
import torch
import nltk
import os

warnings.filterwarnings("ignore", category=UserWarning)
nltk.download("punkt", quiet=True, download_dir="./")
logging.set_verbosity_error()

def load_data(input_file):
    # Load the audio file
    speech, sample_rate = librosa.load(input_file)
    if len(speech.shape) > 1: 
        speech = speech[:,0] + speech[:,1]

    #Resampling the audio
    if sample_rate != 16000:
        speech = librosa.resample(speech, orig_sr=sample_rate, target_sr=16000)
    return speech

def break2chunks(audio_path):
    speech = load_data(audio_path)
    chunk_size = 16000 * 60 # 60 seconds
    chunks = []
    for i in range(0, len(speech), chunk_size):
        chunks.append(speech[i:i+chunk_size])

    if not os.path.isdir("audio-chunks"):
        os.mkdir("audio-chunks")

    # make them wav files
    for i, chunk in enumerate(chunks):
        sf.write(f"audio-chunks/chunk{i}.wav", chunk, 16000)

    chunks = os.listdir("audio-chunks")
    chunks.sort()
    return chunks

def correct_casing(input_sentence):
    model = PunctuationModel(model="kredor/punctuate-all")
    create_sentences = model.restore_punctuation(input_sentence)

    sentences = nltk.sent_tokenize(create_sentences)
    sentences = [sentence.capitalize() for sentence in sentences]

    corr_sentences = " ".join(sentences)
    return '\n'.join(textwrap.wrap(corr_sentences, width=80))

def asr_transcript(input_file):
    model_name = "facebook/wav2vec2-base-960h"
    model = Wav2Vec2ForCTC.from_pretrained(model_name)
    tokenizer = Wav2Vec2Processor.from_pretrained(model_name)
    # Load the audio file
    speech = load_data(input_file)

    #Tokenize, logits and argmax
    input_values = tokenizer(speech, return_tensors="pt", sampling_rate=16000, padding="longest").input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    #Get the words from predicted word ids
    transcription = tokenizer.decode(predicted_ids[0])
    transcription = correct_casing(transcription.lower())
    return str(transcription)

def chunk2text(chunk, transcription):
    chunk_path = f"audio-chunks/{chunk}"
    chunk_transcription = asr_transcript(chunk_path)
    transcription.append(chunk_transcription) 

def convert2text(audio_path):
    if not os.path.isdir("transcripts"):
        os.mkdir("transcripts")

    trans_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    chunks = break2chunks(audio_path)

    transcription = []
    count = 0
    for i, chunk in enumerate(chunks):
        count += 1
        print(f"Processing chunk {i+1} of {len(chunks)}")
        p = Thread(target=chunk2text, args=(chunk, transcription), group=None)
        p.start()

        if count == 2:
            count = 0
            p.join()
    p.join()

    # make a single string
    transcription = " ".join(transcription)

    # # correct spelling
    # transcription = TextBlob(transcription)
    # transcription = str(transcription.correct())

    trans_path = f"transcripts/{trans_date}_transcript.txt"
    with open(trans_path, "w") as f:
        f.write(transcription)
    f.close()

    return trans_path, trans_date

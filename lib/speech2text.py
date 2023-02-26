from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, logging
from deepmultilingualpunctuation import PunctuationModel

from textblob import TextBlob
from threading import Thread
import soundfile as sf

import textwrap
import datetime
import warnings
import librosa

import queue
import torch
import nltk
import os


warnings.filterwarnings("ignore", category=UserWarning)
nltk.download("punkt", quiet=True, download_dir="./")
logging.set_verbosity_error()

def load_data(input_file):
    speech, sample_rate = librosa.load(input_file)
    if len(speech.shape) > 1: 
        speech = speech[:,0] + speech[:,1]

    # Resampling the audio
    if sample_rate != 16000:
        speech = librosa.resample(speech, orig_sr=sample_rate, target_sr=16000)
    return speech

def add_punctuation(input_sentence):
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
    speech = load_data(input_file)

    #Tokenize, logits and argmax
    input_values = tokenizer(speech, return_tensors="pt", sampling_rate=16000, padding="longest").input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    #Get the words from predicted word ids
    transcription = tokenizer.decode(predicted_ids[0])
    transcription = add_punctuation(transcription.lower())
    return str(transcription)

def chunk_to_text(chunk, transcription):
    chunk_path = f"audio-chunks/{chunk}"
    chunk_transcription = asr_transcript(chunk_path)
    transcription.append(chunk_transcription) 

def convert_text(audio_queue, stop_event, trans_date, trans_path):
    if not os.path.isdir("transcripts"):
        os.mkdir("transcripts")

    transcription = []
    last_chunk = None

    while not stop_event.is_set():
        try:
            audio_path = audio_queue.get(timeout=1)
            if not audio_path or not os.path.exists(audio_path):
                continue  # skip if no new audio path available

            if audio_path == last_chunk:
                continue  # skip if already processed
            last_chunk = audio_path

            chunks = os.listdir("audio-chunks")
            chunks.sort()
            for i, chunk in enumerate(chunks):
                if chunk <= last_chunk:
                    continue  # skip if already processed
                chunk_to_text(chunk, transcription)
                os.remove(f"audio-chunks/{chunk}")

            transcription_str = " ".join(transcription)
            
            # correct spelling
            transcription_corr = TextBlob(transcription_str)
            transcription_final = str(transcription_corr.correct())
            
            with open(trans_path, "w") as f:
                f.write("\n" + transcription_final)
        except queue.Empty:
            pass

    return trans_path, trans_date

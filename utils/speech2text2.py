import os
import nltk
import torch
import librosa
import textwrap
import datetime
import warnings
from tqdm import tqdm
import soundfile as sf
from threading import Thread
from textblob import TextBlob
from deepmultilingualpunctuation import PunctuationModel
from happytransformer import HappyTextToText, TTSettings
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, logging

#Loading model
nltk.download("punkt")
logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=UserWarning)
model_name = "facebook/wav2vec2-base-960h"
model = Wav2Vec2ForCTC.from_pretrained(model_name)
tokenizer = Wav2Vec2Processor.from_pretrained(model_name)

def load_data(input_file):
    # Load the audio file
    speech, sample_rate = librosa.load(input_file)
    if len(speech.shape) > 1: 
        speech = speech[:,0] + speech[:,1]

    #Resampling the audio
    if sample_rate != 16000:
        speech = librosa.resample(speech, orig_sr=sample_rate, target_sr=16000)
    return speech

def break2chunks(input_file):
    # if audio is not long enough, just return the whole thing
    if os.path.getsize(input_file) < 16000 * 30:
        return [input_file]

    speech = load_data(input_file)
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
    model = PunctuationModel()
    create_sentences = model.restore_punctuation(input_sentence)

    sentences = nltk.sent_tokenize(create_sentences)
    sentences = [sentence.capitalize() for sentence in sentences]

    corr_sentences = " ".join(sentences)
    return '\n'.join(textwrap.wrap(corr_sentences, width=80))

def asr_transcript(input_file):
    # Load the audio file
    speech = load_data(input_file)

    #Tokenize and take logits and argmax
    input_values = tokenizer(speech, return_tensors="pt", sampling_rate=16000, padding="longest").input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    
    #Get the words from predicted word ids
    transcription = tokenizer.decode(predicted_ids[0])
    transcription = correct_casing(transcription.lower())
    return str(transcription)

def chunk2text(chunk, path, transcription):
    chunk_path = f"audio-chunks/{chunk}"
    chunk_transcription = asr_transcript(chunk_path)
    transcription.append(chunk_transcription)

def convert2text(path):
    if not os.path.isdir("results"):
        os.mkdir("results")
        
    file_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    chunks = break2chunks(path)

    transcription = []
    count = 0
    for i, chunk in enumerate(tqdm(chunks)):
        count += 1
        p = Thread(target=chunk2text, args=(chunk, path, transcription), group=None)
        p.start()
        
        if count == 2:
            count = 0
            p.join()

    # make a single string
    transcription = " ".join(transcription)

    file_path = f"results/{file_date}_transcript.txt"
    with open(file_path, "w") as f:
        f.write(transcription)
    f.close()
    
    return file_path, file_date


if __name__ == "__main__":
    path = "../recording/record.wav"
    file_path, file_date = convert2text(path)
    print(f"Transcription saved in {file_path}")
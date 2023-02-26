import soundfile as sf
import threading
import pyaudio
import wave
import time
import os


def record_audio(audio_queue, stop_event):
    if not os.path.isdir("audio-chunks"):
        os.mkdir("audio-chunks")

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    # Start recording
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    frames = []
    chunk_index = 1
    start_time = time.time()
    while not stop_event.is_set():
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        # Create a chunk every x seconds
        elapsed_time = time.time() - start_time
        if elapsed_time >= 15:
            audio_path = f"audio-chunks/chunk{chunk_index}.wav"
            wf = wave.open(audio_path, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            audio_queue.put(audio_path)

            frames = []
            chunk_index += 1
            start_time = time.time()

    # Save the remaining frames to a chunk
    if frames:
        audio_path = f"audio-chunks/chunk{chunk_index}.wav"
        wf = wave.open(audio_path, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        audio_queue.put(audio_path)

    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()

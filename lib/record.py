import soundfile as sf
import threading
import pyaudio
import wave
import time
import os


def record_audio():
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
    stop_event = threading.Event()
    start_time = time.time()
    def recording():
        nonlocal frames
        nonlocal chunk_index
        nonlocal start_time
        while not stop_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

            # Create a chunk every x seconds
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:
                chunk_path = f"audio-chunks/chunk{chunk_index}.wav"
                wf = wave.open(chunk_path, "wb")
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
                wf.close()

                frames = []
                chunk_index += 1
                start_time = time.time()

    record_thread = threading.Thread(target=recording)
    record_thread.start()

    # Input to stop recording
    input("Press 'Enter' to stop the recording")
    stop_event.set()
    record_thread.join()

    if frames:
        # Save the remaining frames to a chunk
        chunk_path = f"audio-chunks/chunk{chunk_index}.wav"
        wf = wave.open(chunk_path, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()

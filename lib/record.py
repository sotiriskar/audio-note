import threading
import pyaudio
import wave
import os


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS, 
                    rate=RATE, 
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    frames = []
    stop_event = threading.Event()
    def recording():
        while not stop_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

    record_thread = threading.Thread(target=recording)
    record_thread.start()

    # Wait for user to press enter
    input("Press 'enter' to stop the recording")

    stop_event.set()
    record_thread.join()

    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()

    # create temp folder
    if not os.path.isdir("raw-audio"):
        os.mkdir("raw-audio")

    # Save the recording to a file
    audio_path = "raw-audio/record.wav"
    wf = wave.open(audio_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    return audio_path
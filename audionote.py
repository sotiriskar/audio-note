from lib.speech2text import convert_text
from lib.summary import summarize_text
from lib.record import record_audio
from lib.cleanup import cleanup
import threading
import datetime
import queue

def main():
    try:
        stop_event = threading.Event()
        audio_queue = queue.Queue()
        
        trans_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        trans_path = f"transcripts/transcript_{trans_date}.txt"

        audio_thread = threading.Thread(target=record_audio, args=(audio_queue, stop_event))
        audio_thread.start()

        trans_thread = threading.Thread(target=convert_text, args=(audio_queue, stop_event, trans_date, trans_path))
        trans_thread.start()

        input("Press Enter to stop recording...")

        stop_event.set()
        trans_thread.join()

        summarize_text(trans_path, trans_date)
        print("Transcription complete!")
    finally:
        cleanup()

if __name__ == "__main__":
    main()

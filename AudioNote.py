from lib.speech2text import convert_text
from lib.summary import summarize_text
from lib.record import record_audio
from lib.cleanup import cleanup


def main():
    try:
        audio_path = record_audio()
        trans_path, trans_date = convert_text(audio_path)
        summarize_text(trans_path, trans_date)
        print("Transcription complete!")
    finally:
        cleanup()

if __name__ == "__main__":
    main()

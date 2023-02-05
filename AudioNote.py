from utils.speech2text import convert2text
from utils.record import record_audio
from utils.summary import summarize_text
from utils.cleanup import cleanup


def main():
    cleanup()
    audio_path = record_audio()
    trans_path, trans_date = convert2text(audio_path)
    summarize_text(trans_path, trans_date)
    cleanup()
    print("Transcription complete!")
    
if __name__ == "__main__":
    main()

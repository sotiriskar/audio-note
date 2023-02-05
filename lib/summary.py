from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
import textwrap
import os


def summarize_text(trans_path, trans_date):
    with open(trans_path, "r") as f:
        text = f.read()
    f.close()

    parser = PlaintextParser.from_string(text, Tokenizer("english"))

    # Summarize using sumy TextRank
    summarizer = TextRankSummarizer()
    summary =summarizer(parser.document,2)
    text_summary=""
    for sentence in summary:
        text_summary+=str(sentence)

    # Wrap text to 80 characters
    text_summary = '\n'.join(textwrap.wrap(text_summary, width=80))

    # Create summary folder
    if not os.path.isdir("summary"):
        os.mkdir("summary")

    # Create summary file
    with open(f"summary/{trans_date}_summary.txt", "w") as f:
        f.write(text_summary)
    f.close()

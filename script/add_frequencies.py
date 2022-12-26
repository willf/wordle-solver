# Given a file of words and their frequencies, and other file with just words, add the frequencies to the other file.

import argparse
import csv
import os

FREQ_FILE = os.path.join(os.path.dirname(__file__),"..",  "data", "google_5.tsv")
SOLUTION_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "nytimes_2022_12_20.txt")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--freqs", type=str, default=FREQ_FILE)
    parser.add_argument("-l", "--lexicon", type=str, default=SOLUTION_FILE)
    return parser.parse_args()



def main():
    opts = parse_args()
    freqs = {}
    with open(opts.freqs) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            freqs[row[0]] = row[1]
    with open(opts.lexicon) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            word = row[0]
            if word in freqs:
                print(word, freqs[word], sep="\t")
            else:
                print(word, 0, sep="\t")

if __name__ == "__main__":
    main()

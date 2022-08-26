"""
    parser.py - a parser for the daily dialog dataset. Adapted from the original repo https://github.com/Sanghoon94/DailyDialogue-Parser by Sanghoon Kang
"""

__author__ = "Sanghoon Kang"

import argparse
import gzip
import logging
import os
import sys
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_data(in_dir, out_dir):

    # Finding files
    dirname = in_dir.name
    dial_dir = in_dir / f"dialogues_{dirname}.txt"
    emo_dir = in_dir / f"dialogues_emotion_{dirname}.txt"
    act_dir = in_dir / f"dialogues_act_{dirname}.txt"
    assert dial_dir.exists() and emo_dir.exists() and act_dir.exists(), f"{in_dir} does not contain the required files"
    out_dial_path = out_dir / "dial.txt.gz"
    out_emo_path = out_dir / "emo.txt.gz"
    out_act_path = out_dir / "act.txt.gz"

    # Open files
    in_dial = open(dial_dir, "r", encoding="utf-8", errors="ignore")
    in_emo = open(emo_dir, "r", encoding="utf-8", errors="ignore")
    in_act = open(act_dir, "r", encoding="utf-8", errors="ignore")

    out_dial = gzip.open(
        out_dial_path,
        "w",
    )
    out_emo = gzip.open(
        out_emo_path,
        "w",
    )
    out_act = gzip.open(
        out_act_path,
        "w",
    )
    pbar = tqdm(desc="Parsing", )
    for line_count, (line_dial, line_emo, line_act) in enumerate(
        zip(in_dial, in_emo, in_act)
    ):
        seqs = line_dial.split("__eou__")
        seqs = seqs[:-1]

        emos = line_emo.split(" ")
        emos = emos[:-1]

        acts = line_act.split(" ")
        acts = acts[:-1]

        seq_count = 0
        seq_len = len(seqs)
        emo_len = len(emos)
        act_len = len(acts)

        if seq_len != emo_len or seq_len != act_len:
            logging.warning(
                "Different turns btw dialogue & emotion & action! ",
                line_count + 1,
                seq_len,
                emo_len,
                act_len,
            )
            sys.exit()

        for seq, emo, act in zip(seqs, emos, acts):

            # Get rid of the blanks at the start & end of each turns
            if seq[0] == " ":
                seq = seq[1:]
            if seq[-1] == " ":
                seq = seq[:-1]

            out_dial.write(seq.encode("utf-8"))
            out_dial.write("\n".encode("utf-8"))
            out_emo.write(emo.encode("utf-8"))
            out_emo.write("\n".encode("utf-8"))
            out_act.write(act.encode("utf-8"))
            out_act.write("\n".encode("utf-8"))

            if seq_count != 0 and seq_count != seq_len - 1:
                out_dial.write(seq.encode("utf-8"))
                out_dial.write("\n".encode("utf-8"))
                out_emo.write(emo.encode("utf-8"))
                out_emo.write("\n".encode("utf-8"))
                out_act.write(act.encode("utf-8"))
                out_act.write("\n".encode("utf-8"))

            seq_count += 1
        pbar.update(1)
    pbar.close()

    in_dial.close()
    in_emo.close()
    in_act.close()
    out_dial.close()
    out_emo.close()
    out_act.close()

def get_parser():
    """
    get_parser - a helper function for the argparse module
    """

    parser = argparse.ArgumentParser(
        description="parser.py - a parser for the daily dialog dataset"
    )
    parser.add_argument(
        "-i",
        "--in_dir",
        type=Path,
        help="Input directory containing the dialogues",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--out_dir",
        type=Path,
        help="Output directory for the parsed dialogues",
        required=True,
    )
    return parser



if __name__ == "__main__":

    args = get_parser().parse_args()
    logging.info(f"args:\n{args}")
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)

    # check if paths are full paths, if not, assume they are relative to the current working directory
    if not in_dir.is_absolute():
        logging.info("assuming input directory is relative to the current working directory")
        in_dir = Path.cwd() / in_dir
        out_dir = Path.cwd() / out_dir

    logging.info(f"Input directory:\n\t{in_dir}")
    logging.info(f"Output directory:\n\t{out_dir}")

    parse_data(in_dir, out_dir)

    print("Done")

import os
import argparse

def main():
    os.system("rsync -aP" + " " + args["source"] + " " + args["target"])

if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-source", "--source", required=True,
    help="source directory to transfer")
    ap.add_argument("-target", "--target", required=True,
    help="target directory to transfer")
    args = vars(ap.parse_args())
    main()
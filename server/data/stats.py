import sys
import os
import json
import argparse


# List all files in the current directory
def list_files(path):
    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name)
    return files


# For each file in current directory, check if it is a json file and load "label" entry from it.
def load_labels(path):
    labels = []
    files = list_files(path)
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(path, file)) as json_file:
                data = json.load(json_file)
                labels.append(data["label"])
    return labels


# Print counts for each label
def print_counts(labels):
    counts = {}
    for label in labels:
        if label in counts:
            counts[label] += 1
        else:
            counts[label] = 1
    for label in counts:
        print(label + ": " + str(counts[label]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", default=".")
    args = parser.parse_args()

    labels = load_labels(args.dir)
    print_counts(labels)


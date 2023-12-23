"""
PASCAL VOC Data Set Tools

This script converts Dark Label VOC data sets to the correct format and structure for PASCAL VOC
This script also allows for the generation and injection of negatives into the data set to experiment with.

Usage Instructions:
-------------------
Run the script from the command line as follows:
    py prepare_dataset.py --drk_lbl_voc --gen_neg

License:
-------
MIT License
Copyright (c) 2023 @10XTMY, molmez.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
import sys
import traceback
from pathlib import Path
from voc_helpers import generate_negative_data_set, collect_current_data_set, inject_negative_data_set, \
    count_xml_labels, generate_txt_files, prepare_voc


def read_labels(file_path):
    try:
        with open(file_path, 'r') as file:
            return [label.strip() for label in file.readlines()]
    except IOError as e:
        print(f'Error reading labels file: {e}')
        return []


# argument parser
parser = argparse.ArgumentParser(description="VOC data set tools",
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("--drk_lbl_voc", action='store_true', help="Dark Label to VOC data set")
parser.add_argument("--gen_neg", action='store_true', help="Generate and Inject Negatives")

# parse arguments
try:
    args = parser.parse_args()
except Exception as e:
    print(f'Error parsing arguments: {e}')
    traceback.print_exc()
    sys.exit(1)

# paths
CURRENT_DATA_SET = Path('input/')
NEGATIVE_IMAGES = Path('negativesInput/')
NEGATIVE_DATA_SET_OUTPUT = Path('negativeDataSet/')
NEGATIVE_XML_TEMPLATE = Path('negative.xml')
ANNOTATIONS_DIR = Path('output/Annotations/')
JPEG_DIR = Path('output/JPEGImages/')
SETS_DIR = Path('output/ImageSets/')
TXT_DIR = Path('output/ImageSets/Main/')
LABELS_TXT = Path('output/labels.txt')

# read labels
LABELS_FOR_COUNTING = read_labels(LABELS_TXT)

# booleans from arguments
PREPARE_VOC_FROM_DARK_LABEL = args.drk_lbl_voc
INJECT_NEGATIVES = args.gen_neg

if __name__ == "__main__":

    if not PREPARE_VOC_FROM_DARK_LABEL and not INJECT_NEGATIVES:
        print('no action selected, exiting program.')
        sys.exit(0)

    if PREPARE_VOC_FROM_DARK_LABEL:
        try:
            existing_names = collect_current_data_set(CURRENT_DATA_SET,
                                                      JPEG_DIR,
                                                      ANNOTATIONS_DIR)
        except IOError as e:
            print(f'error collecting current data set: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

        try:
            prepare_voc(CURRENT_DATA_SET,
                        JPEG_DIR,
                        ANNOTATIONS_DIR,
                        existing_names)
        except (IOError, Exception) as e:
            print(f'error preparing voc: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

        try:
            generate_txt_files(JPEG_DIR, TXT_DIR, 20)
        except (OSError, ValueError, IOError) as e:
            print(f'error generating txt files: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

    if INJECT_NEGATIVES:
        try:
            existing_names = collect_current_data_set(CURRENT_DATA_SET,
                                                      JPEG_DIR,
                                                      ANNOTATIONS_DIR)
        except IOError as e:
            print(f'error collecting current data set: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

        try:
            generate_negative_data_set(existing_names,
                                       NEGATIVE_IMAGES,
                                       NEGATIVE_DATA_SET_OUTPUT,
                                       NEGATIVE_XML_TEMPLATE)
        except (IOError, Exception) as e:
            print(f'error generating negative data set: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

        try:
            inject_negative_data_set(NEGATIVE_DATA_SET_OUTPUT,
                                     JPEG_DIR,
                                     ANNOTATIONS_DIR,
                                     TXT_DIR,
                                     20)
        except (OSError, ValueError, IOError) as e:
            print(f'error injecting negative data set: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)

    if LABELS_FOR_COUNTING:
        try:
            label_count = count_xml_labels(ANNOTATIONS_DIR,
                                           LABELS_FOR_COUNTING)
        except Exception as e:
            print(f'error counting labels: {e}')
            traceback.print_tb(e.__traceback__)
            sys.exit(1)
        else:
            print(label_count)

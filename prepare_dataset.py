"""
PASCAL VOC Data Tools

This script converts Dark Label VOC data sets to the correct format and structure for PASCAL VOC.

by @0xtommyOfficial, molmez.io
01/Feb/2022
"""
import argparse
import sys
from pathlib import Path
from voc_helpers import generate_negative_data_set, collect_current_data_set, inject_negative_data_set,\
    count_xml_labels, generate_txt_files, prepare_voc


# parse the command line
parser = argparse.ArgumentParser(description="VOC data set tools",
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("--drk_lbl_voc", action='store_true', help="Dark Label to VOC data set")
parser.add_argument("--gen_neg", action='store_true', help="Generate Negatives")

try:
    opt = parser.parse_known_args()[0]
except:
    parser.print_help()
    sys.exit(0)


CURRENT_DATA_SET = Path('input/')
NEGATIVE_IMAGES = Path('negativesInput/')
NEGATIVE_DATA_SET_OUTPUT = Path('negativeDataSet/')
NEGATIVE_XML_TEMPLATE = Path('negative.xml')
ANNOTATIONS_DIR = Path('output/Annotations/')
JPEG_DIR = Path('output/JPEGImages/')
SETS_DIR = Path('output/ImageSets/')
TXT_DIR = Path('output/ImageSets/Main/')
LABELS_TXT = Path('output/labels.txt')
PREPARE_VOC_FROM_DARK_LABEL = opt.drk_lbl_voc
INJECT_NEGATIVES = opt.gen_neg

try:
    LABELS_FILE = open(LABELS_TXT)
except Exception as _err:
    print(f'error: {_err}')
    print('labels will not be counted as a result of missing labels.txt')
    LABELS_FOR_COUNTING = []
else:
    LABELS = LABELS_FILE.readlines()
    LABELS_FOR_COUNTING = []
    for label in LABELS:
        _lbl = label.strip()
        LABELS_FOR_COUNTING.append(_lbl)

if __name__ == "__main__":

    if not PREPARE_VOC_FROM_DARK_LABEL and not INJECT_NEGATIVES:
        print('no action selected, exiting program.')
        sys.exit(0)

    if PREPARE_VOC_FROM_DARK_LABEL:

        existing_names = collect_current_data_set(CURRENT_DATA_SET,
                                                  JPEG_DIR,
                                                  ANNOTATIONS_DIR)

        prepare_voc(CURRENT_DATA_SET,
                    JPEG_DIR,
                    ANNOTATIONS_DIR,
                    existing_names)

        generate_txt_files(JPEG_DIR, TXT_DIR, 20)

    if INJECT_NEGATIVES:

        existing_names = collect_current_data_set(CURRENT_DATA_SET,
                                                  JPEG_DIR,
                                                  ANNOTATIONS_DIR)

        generate_negative_data_set(existing_names,
                                   NEGATIVE_IMAGES,
                                   NEGATIVE_DATA_SET_OUTPUT,
                                   NEGATIVE_XML_TEMPLATE)

        inject_negative_data_set(NEGATIVE_DATA_SET_OUTPUT,
                                 JPEG_DIR,
                                 ANNOTATIONS_DIR,
                                 TXT_DIR,
                                 20)

    if LABELS_FOR_COUNTING:

        label_count = count_xml_labels(ANNOTATIONS_DIR,
                                       LABELS_FOR_COUNTING)
        print(label_count)

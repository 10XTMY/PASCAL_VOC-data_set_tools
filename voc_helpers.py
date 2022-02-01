"""
PASCAL VOC Data Tools
by https://github.com/cyberduderino
01/Feb/2022
"""
import os
import sys
import traceback
import random
import string
import shutil
import tqdm
import datetime
import xml.etree.ElementTree as ElementTree
from PIL import Image


def get_time_date():
    _now = datetime.datetime.now()
    time_stamp = datetime.timedelta(minutes=_now.minute,
                                    seconds=_now.second,
                                    hours=_now.hour)
    date = _now.date()
    return time_stamp, date


def write_to_txt_file(filename, set_to_write, existing):
    """
    appends data to existing txt file or writes data to a new one
    :param filename:name of txt file to write
    :param set_to_write: set of data to write to txt file
    :param existing: does the file already exist?
    """
    if existing:
        mode = 'a'
    else:
        mode = 'w'
    try:
        with open(filename, mode) as f:
            for _line in set_to_write:
                _to_write = _line.rsplit(".", 1)[0]
                f.write(str(_to_write) + '\n')
    except Exception as _err:
        print(f'error writing {filename}: {_err} ')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    else:
        print(f'{filename} saved')


def get_random_alphanum_str(length):
    """
    generates random alphanumerical string
    :param length: desired string length to be returned
    :return: string
    """
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def partition_list(list_to_split, percent, shuffle):
    """
    :param list_to_split: provide a list to be partitioned
    :param percent: desired percentage of partition
    :param shuffle: True to shuffle the list before splitting it
    :return: two lists, the first being the percentage of the original
    """
    if shuffle:
        random.shuffle(list_to_split)
    _split = round(len(list_to_split)*(percent/100))
    return list_to_split[:_split], list_to_split[_split:]


def split_list_in_half(list_to_split):
    """
    :param list_to_split: input list
    :return: two lists, input list split in half
    """
    return list_to_split[::2], list_to_split[1::2]


def get_new_file_name(existing_names):
    """
    :param existing_names: list of existing file names to avoid conflict
    :return: new filename
    """
    _filename = get_random_alphanum_str(15)
    if f'{_filename}' in existing_names:
        while f'{_filename}' in existing_names:
            _filename = get_random_alphanum_str(15)
    return _filename


def count_xml_labels(xml_dir, lbl_list):
    """
    counts the amount of given labels in all xml files within provided directory
    :param xml_dir: xml directory to scan
    :param lbl_list: a list of label names to count
    :return: dictionary of labels and their counts
    """
    # create dictionary from label list and set values to 0
    # count labels
    label_counts = {}
    try:
        label_counts = dict.fromkeys(lbl_list, 0)
    except Exception as _err:
        print(f'error generating dictionary from {lbl_list}: {_err}')
        traceback.print_tb(_err.__traceback__)
    else:
        try:
            for dir_data in os.walk(xml_dir):
                dir_path, folders, files = dir_data
                for _xml in files:
                    try:
                        tree = ElementTree.parse(f'{dir_path}/{_xml}')
                    except Exception as _err:
                        print(f'error parsing {_xml}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                    else:
                        for name in tree.getroot().iter('name'):
                            if name.text in label_counts:
                                _count = label_counts[name.text]
                                _count = _count+1
                                label_counts.update({f'{name.text}': _count})
        except Exception as _err:
            print(f'error walking {xml_dir}: {_err}')
            traceback.print_tb(_err.__traceback__)

    return label_counts


def remove_object_from_xml_files(xml_directory, object_names_set):
    """
    removes objects from xml files within a provided directory
    :param xml_directory: directory path for xml files
    :param object_names_set: a set of object names to be removed
    """
    try:
        for data in os.walk(xml_directory):
            dir_path, folders, files = data
            for xml_file in tqdm.tqdm(files):
                tree = ElementTree.parse(f'{dir_path}\{xml_file}')
                try:
                    tree_root = tree.getroot()
                except Exception as _err:
                    print(f'error getting root from {xml_file}: {_err}')
                    traceback.print_tb(_err.__traceback__)
                    sys.exit(1)
                else:
                    objects = tree.findall("object")
                    for name in object_names_set:
                        for obj in objects:
                            # print(obj.find('name').text)
                            if obj.find('name').text == str(name):
                                try:
                                    tree_root.remove(obj)
                                except Exception as _err:
                                    print(f'error removing {obj} from {tree_root} in {xml_file}: {_err}')
                                    traceback.print_tb(_err.__traceback__)
                                    sys.exit(1)
                    try:
                        tree.write(f'{dir_path}\{xml_file}')
                    except Exception as _err:
                        print(f'error writing {xml_file}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
    except Exception as _err:
        print(f'error parsing {xml_directory}: {_err}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)


def fix_missing_xml_object_name(xml_directory, label_text):
    """
    scans xml file for objects with no name and names them according
    to the label_text
    :param xml_directory: directory of xml files
    :param label_text: label to replace object name with
    """

    for data in os.walk(xml_directory):
        dir_path, folders, files = data
        for xml_file in tqdm.tqdm(files):
            try:
                tree = ElementTree.parse(f'{dir_path}\{xml_file}')
            except Exception as _err:
                print(f'error parsing {xml_file}: {_err}')
                traceback.print_tb(_err.__traceback__)
                sys.exit(1)
            else:
                try:
                    objects = tree.findall("object")
                    for obj in objects:
                        class_name = obj.find('name')
                        if class_name.text is None:
                            class_name.text = label_text
                except Exception as _err:
                    print(f'error editing objects in {xml_file}: {_err}')
                    traceback.print_tb(_err.__traceback__)
                    sys.exit(1)
                else:
                    try:
                        tree.write(f'{dir_path}\{xml_file}')
                    except Exception as _err:
                        print(f'error writing {xml_file}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)


def replace_xml_file_information(xml_file, replace_dict):
    """
    overwrites existing xml file with new values
    :param xml_file: xml file to edit
    :param replace_dict: dictionary of xml tags and the value to place in them
    """
    try:
        tree = ElementTree.parse(xml_file)
    except Exception as _err:
        print(f'error parsing {xml_file}: {_err}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    else:
        for key, value in replace_dict.items():
            for name in tree.getroot().iterfind(key):
                name.text = value
        try:
            tree.write(xml_file)
        except Exception as _err:
            print(f'error writing {xml_file}: {_err}')
            traceback.print_tb(_err.__traceback__)
            sys.exit(1)


def generate_negative_data_set(existing_names, negative_images, negative_output_dir, xml_template):
    """
    generates new filename for both xml and jpg
    copies images to output folder -> copies xml template to output -> edits xml file to match image
    :param existing_names: list of existing file names
    :param negative_images: folder containing negative image files (jpg)
    :param negative_output_dir: folder to output the negative data set (jpg & xml)
    :param xml_template: negative xml template to use
    """
    print('generating negative data set..')
    try:
        for data in os.walk(negative_images):
            dir_path, folders, files = data
            for image_file in tqdm.tqdm(files):
                if image_file.endswith('.jpg'):
                    try:
                        img = Image.open(f'{dir_path}\{image_file}')
                    except Exception as _err:
                        print(f'error opening negative image: {image_file}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
                    else:
                        width, height = img.size
                        filename = get_new_file_name(existing_names)
                        existing_names.add(filename)
                        image_name = f'{filename}.jpg'
                        image_path = f'{dir_path}\{image_file}'
                        image_out_path = f'{negative_output_dir}\{image_name}'
                        xml_file = f'{filename}.xml'
                        xml_path = f'{negative_output_dir}\{xml_file}'
                        replace_dict = {'filename': str(image_name),
                                        'path': str(image_name),
                                        'width': str(width),
                                        'height': str(height),
                                        'xmax': str(width),
                                        'ymax': str(height)}
                        try:
                            shutil.copy(image_path, image_out_path)
                        except Exception as _err:
                            print(f'error copying {image_file} to {negative_output_dir}: {_err}')
                            traceback.print_tb(_err.__traceback__)
                            sys.exit(1)
                        try:
                            shutil.copy(xml_template, xml_path)
                        except Exception as _err:
                            print(f'error copying {xml_template} to {negative_output_dir}: {_err}')
                            traceback.print_tb(_err.__traceback__)
                            sys.exit(1)
                        else:
                            replace_xml_file_information(xml_path, replace_dict)
    except Exception as _err:
        print(f'error walking negatives directory: {_err}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    print(f'..negative data set generated in {negative_output_dir} directory')


def collect_current_data_set(data_set_path, jpg_dir, annotations_dir):
    """
    copies existing data set to appropriate output directories, making a note of file names
    :param data_set_path: directory containing existing data set's jpg and xml files
    :param jpg_dir: output jpg directory
    :param annotations_dir: output annotations directory
    :return: list of unique file names in the data set that has been collected
    """
    print('collecting current data set..')
    existing_names = set({})
    try:
        for data in os.walk(data_set_path):
            dir_path, folders, files = data
            for img in tqdm.tqdm(files):
                if img.endswith('.jpg'):
                    filename = f'{img.rsplit(".", 1)[0]}'
                    xml_filename = f'{filename}.xml'
                    existing_names.add(filename)
                    # copy jpg to JPGImages folder and xml to Annotations folder
                    try:
                        shutil.copy(f'{dir_path}\{img}', jpg_dir)
                    except Exception as _err:
                        print(f'error copying {img} to {jpg_dir}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
                    try:
                        shutil.copy(f'{dir_path}\{xml_filename}', annotations_dir)
                    except Exception as _err:
                        print(f'error copying {xml_filename} to {annotations_dir}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
    except Exception as _err:
        print(f'error walking directory: {data_set_path}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    print('..finished collecting current data set')
    return existing_names


def generate_txt_files(jpg_dir, txt_dir, split_percentage):
    """
    scans image directory and generates text file lists for the data set
    :param jpg_dir: directory containing jpgs to be listed
    :param txt_dir: output txt directory
    :param split_percentage: split percentage for test and validation sets (recommended 20)
    """
    print('generating txt files..')
    try:
        jpeg_names = os.listdir(path=jpg_dir)
    except Exception as _err:
        print(f'error listing {jpg_dir}: {_err}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    else:
        # split the list into a training list and a split_set list
        # by default takes 80 percent for train and  20 percent for test/validation
        split_set, train_set = partition_list(list_to_split=jpeg_names, percent=split_percentage, shuffle=True)
        print(f'split_test count: {len(split_set)}')
        print(f'train_set count: {len(train_set)}')

        # split the split_set list into validation and test lists
        # by default it splits in half
        test_set, val_set = split_list_in_half(list_to_split=split_set)
        print(f'test_set count: {len(test_set)}')
        print(f'val_set count: {len(val_set)}')

        print('writing txt files..')

        train_txt_file = 'train.txt'
        test_txt_file = 'test.txt'
        validation_txt_file = 'val.txt'
        trainval_txt_file = 'trainval.txt'

        write_to_txt_file(filename=f'{txt_dir}\{train_txt_file}', set_to_write=train_set, existing=False)
        write_to_txt_file(filename=f'{txt_dir}\{test_txt_file}', set_to_write=test_set, existing=False)
        write_to_txt_file(filename=f'{txt_dir}\{validation_txt_file}', set_to_write=val_set, existing=False)
        write_to_txt_file(filename=f'{txt_dir}\{trainval_txt_file}', set_to_write=train_set, existing=False)
        write_to_txt_file(filename=f'{txt_dir}\{trainval_txt_file}', set_to_write=val_set, existing=True)

        print(f'..all txt files saved in: {txt_dir}')


def inject_negative_data_set(negatives_dir, jpg_dir, annotations_dir, txt_dir, val_test_percentage):
    """
    takes negative data set, copies to output folders, generates text files for new data set
    :param negatives_dir: directory containing negative jpg and xml files
    :param jpg_dir: output jpg directory
    :param annotations_dir: output annotations directory
    :param txt_dir: output txt directory
    :param val_test_percentage: split percentage for test and validation sets (recommended 20)
    """
    print('injecting negative data set..')
    try:
        for data in os.walk(negatives_dir):
            dir_path, folder, files = data
            for _file in files:
                if _file.endswith('.jpg'):
                    try:
                        shutil.copy(f'{dir_path}\{_file}', jpg_dir)
                    except Exception as _err:
                        print(f'error copying {dir_path}{_file} to {jpg_dir}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
                elif _file.endswith('.xml'):
                    try:
                        shutil.copy(f'{dir_path}\{_file}', annotations_dir)
                    except Exception as _err:
                        print(f'error copying {dir_path}{_file} to {annotations_dir}: {_err}')
                        traceback.print_tb(_err.__traceback__)
                        sys.exit(1)
                else:
                    print(f'file is neither .jpg nor .xml: {_file}')
    except Exception as _err:
        print(f'error walking directory: {negatives_dir}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)
    generate_txt_files(jpg_dir, txt_dir, val_test_percentage)
    print('..finished injecting negative data set into current data set')


def prepare_voc(input_directory, image_directory, annotations_directory, existing_names):
    """
    takes current data set and renames all files unique, converts any pngs into jpgs
    saves new files into VOC output directories
    :param input_directory: current data set
    :param image_directory: output directory for images
    :param annotations_directory: output directory for annotations
    :param existing_names: set containing current filenames
    """
    try:
        for data in os.walk(input_directory):
            dir_path, folders, files = data

            for i in tqdm.tqdm(files):
                # only process .png files
                if i.endswith('.png'):
                    _filename = get_new_file_name(existing_names)
                    if f'{_filename}.xml' not in files:
                        _xml = f'{i.rsplit(".", 1)[0]}.xml'
                        if _xml in files and _xml not in existing_names:
                            try:
                                _img = Image.open(f'{dir_path}\{i}')
                            except Exception as _err:
                                print(f'error opening: {dir_path}\{i}')
                                traceback.print_tb(_err.__traceback__)
                                sys.exit(1)
                            rgb_img = _img.convert('RGB')
                            try:
                                rgb_img.save(f'{image_directory}\{_filename}.jpg')
                            except Exception as _err:
                                print(f'error saving: {image_directory}\{_filename}.jpg')
                                traceback.print_tb(_err.__traceback__)
                                sys.exit(1)
                            _replace_dict = {'filename': f'{_filename}.jpg',
                                             'path': f'{_filename}.jpg'}
                            replace_xml_file_information(xml_file=f'{input_directory}\{_xml}',
                                                         replace_dict=_replace_dict)
                            try:
                                shutil.copy(f'{dir_path}\{_xml}', f'{annotations_directory}\{_filename}.xml')
                            except Exception as _err:
                                print(f'error copying {dir_path}\{_xml} to {annotations_directory}')
                                traceback.print_tb(_err.__traceback__)
                                sys.exit(1)
                            existing_names.add(files.index(_xml))
                            existing_names.add(_filename)
    except Exception as _err:
        print(f'error walking directory: {input_directory}')
        traceback.print_tb(_err.__traceback__)
        sys.exit(1)

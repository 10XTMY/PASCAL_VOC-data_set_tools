"""
PASCAL VOC Data Tools
by @10XTMY, molmez.io
01/Feb/2022
"""
import os
import sys
import traceback
import random
import string
import secrets
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
    Appends data to existing txt file or writes data to a new one
    :param filename:name of txt file to write
    :param set_to_write: set of data to write to txt file
    :param existing: does the file already exist?
    """
    mode = 'a' if existing else 'w'

    try:
        with open(filename, mode) as file:
            for line in set_to_write:
                to_write = line.rsplit(".", 1)[0]
                file.write(f'{to_write}\n')
    except IOError as err:
        raise IOError(f"Error writing to {filename}: {err}") from err
    else:
        print(f'{filename} saved')


def get_random_alphanum(length):
    """
    Generates a random alphanumerical string
    :param length: desired string length to be returned
    :return: a random alphanumerical string of the specified length.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(secrets.choice(letters_and_digits) for _ in range(length))


def partition_list(list_to_split, percent, shuffle):
    """
    :param list_to_split: provide a list to be partitioned
    :param percent: desired percentage of partition
    :param shuffle: True to shuffle the list before splitting it
    :return: two lists, the first being the percentage of the original
    """
    if not 0 <= percent <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    if shuffle:
        random.shuffle(list_to_split)

    split_index = round(len(list_to_split) * (percent / 100))
    return list_to_split[:split_index], list_to_split[split_index:]


def split_list_in_half(list_to_split):
    """
    :param list_to_split: input list
    :return: two lists, input list split in half
    """
    middle = len(list_to_split) // 2
    return list_to_split[:middle], list_to_split[middle:]


def get_new_file_name(existing_names, length=15, max_attempts=100000):
    """
    :param existing_names: list of existing file names to avoid conflict
    :param length: desired length of new file name
    :param max_attempts: maximum number of attempts before giving up
    :return: new filename
    """
    for _ in range(max_attempts):
        filename = get_random_alphanum(length)
        if filename not in existing_names:
            return filename

    raise RuntimeError(f"Failed to generate a unique filename after {max_attempts} attempts.")


def count_xml_labels(xml_dir, lbl_list):
    """
    counts the amount of given labels in all xml files within provided directory
    :param xml_dir: xml directory to scan
    :param lbl_list: a list of label names to count
    :return: dictionary of labels and their counts
    """

    label_counts = dict.fromkeys(lbl_list, 0)

    for dir_path, _, files in os.walk(xml_dir):
        for xml_file in files:
            if not xml_file.lower().endswith('.xml'):
                continue

            xml_path = os.path.join(dir_path, xml_file)
            try:
                tree = ElementTree.parse(xml_path)
            except ElementTree.ParseError as e:
                raise ElementTree.ParseError(f'error parsing {xml_file}: {e}')

            for name in tree.getroot().iter('name'):
                if name.text in label_counts:
                    label_counts[name.text] += 1

    return label_counts


def remove_object_from_xml_files(xml_directory, object_names_set):
    """
    removes objects from xml files within a provided directory
    :param xml_directory: directory path for xml files
    :param object_names_set: a set of object names to be removed
    """
    for dir_path, _, files in os.walk(xml_directory):
        for xml_file in tqdm.tqdm(files):
            xml_path = os.path.join(dir_path, xml_file)
            if not xml_file.lower().endswith('.xml'):
                continue

            try:
                tree = ElementTree.parse(xml_path)
                tree_root = tree.getroot()
                objects = tree_root.findall("object")

                for obj in objects:
                    if obj.find('name').text in object_names_set:
                        tree_root.remove(obj)

                tree.write(xml_path)

            except ElementTree.ParseError as e:
                print(f"Error parsing {xml_file}: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"Error processing {xml_file}: {e}")
                traceback.print_tb(e.__traceback__)
                sys.exit(1)


def fix_missing_xml_object_name(xml_directory, label_text):
    """
    scans xml file for objects with no name and names them according
    to the label_text
    :param xml_directory: directory of xml files
    :param label_text: label to replace object name with
    """
    for dir_path, _, files in os.walk(xml_directory):
        for xml_file in tqdm.tqdm(files):
            if not xml_file.lower().endswith('.xml'):
                continue

            xml_path = os.path.join(dir_path, xml_file)

            try:
                tree = ElementTree.parse(xml_path)
                objects = tree.findall("object")
                updated = False

                for obj in objects:
                    class_name = obj.find('name')
                    if class_name is not None and class_name.text is None:
                        class_name.text = label_text
                        updated = True

                if updated:
                    tree.write(xml_path)

            except ElementTree.ParseError as e:
                raise ElementTree.ParseError(f"Error parsing {xml_file}: {e}")
            except Exception as e:
                raise Exception(f"Error processing {xml_file}: {e}")


def replace_xml_file_information(xml_file, replace_dict):
    """
    overwrites existing xml file with new values
    :param xml_file: xml file to edit
    :param replace_dict: dictionary of xml tags and the value to place in them
    """
    try:
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()

        for key, value in replace_dict.items():
            elements = root.findall(key)
            for elem in elements:
                elem.text = value

        tree.write(xml_file)

    except ElementTree.ParseError as e:
        raise ElementTree.ParseError(f'error parsing {xml_file}: {e}')
    except Exception as e:
        raise Exception(f'error processing {xml_file}: {e}')


def generate_negative_data_set(existing_names, negative_images, negative_output_dir, xml_template):
    """
    generates new filename for both xml and jpg
    copies images to output folder -> copies xml template to output -> edits xml file to match image
    :param existing_names: list of existing file names
    :param negative_images: folder containing negative image files (jpg)
    :param negative_output_dir: folder to output the negative data set (jpg & xml)
    :param xml_template: negative xml template to use
    """
    print('Generating negative data set...')

    for dir_path, _, files in os.walk(negative_images):
        for image_file in tqdm.tqdm(files):
            file_ext = image_file.lower().split('.')[-1]
            if file_ext not in ['jpg', 'jpeg']:
                continue

            try:
                # process image
                img_path = os.path.join(dir_path, image_file)
                img = Image.open(img_path)
                width, height = img.size
            except IOError as e:
                raise IOError(f'error opening {image_file}: {e}')

            try:
                # generate new filename and prepare file paths
                filename = get_new_file_name(existing_names)
                existing_names.add(filename)
                image_name = f'{filename}.{file_ext}'
                image_out_path = os.path.join(negative_output_dir, image_name)
                xml_file = f'{filename}.xml'
                xml_path = os.path.join(negative_output_dir, xml_file)

                # copy image and XML template
                shutil.copy(img_path, image_out_path)
                shutil.copy(xml_template, xml_path)
            except IOError as e:
                raise IOError(f'error copying {image_file} to {negative_output_dir}: {e}')

            try:
                # replace information in XML
                replace_dict = {
                    'filename': image_name,
                    'path': image_name,
                    'width': str(width),
                    'height': str(height),
                    'xmax': str(width),
                    'ymax': str(height)
                }
                try:
                    replace_xml_file_information(xml_path, replace_dict)
                except Exception as e:
                    raise Exception(f'error processing {xml_file}: {e}')
            except ElementTree.ParseError as e:
                raise ElementTree.ParseError(f'error parsing {xml_file}: {e}')

    print(f'..Negative data set generated in {negative_output_dir} directory')


def collect_current_data_set(data_set_path, jpg_dir, annotations_dir):
    """
    copies existing data set to appropriate output directories, making a note of file names
    :param data_set_path: directory containing existing data set's jpg and xml files
    :param jpg_dir: output jpg directory
    :param annotations_dir: output annotations directory
    :return: list of unique file names in the data set that has been collected
    """
    print('Collecting current data set...')
    existing_names = set()

    for dir_path, _, files in os.walk(data_set_path):
        for file in tqdm.tqdm(files):
            file_ext = file.lower().split('.')[-1]  # last element of the split is the file extension
            if file_ext not in ['jpg', 'jpeg']:
                continue

            filename, _ = os.path.splitext(file)
            existing_names.add(filename)

            jpg_path = os.path.join(dir_path, file)
            xml_file = f'{filename}.xml'
            xml_path = os.path.join(dir_path, xml_file)

            try:
                shutil.copy(jpg_path, os.path.join(jpg_dir, file))
                shutil.copy(xml_path, os.path.join(annotations_dir, xml_file))
            except IOError as e:
                raise IOError(f'error copying {file} to {jpg_dir} or {annotations_dir}: {e}')

    print('..Finished collecting current data set')
    return existing_names


def generate_txt_files(jpg_dir, txt_dir, split_percentage):
    """
    scans image directory and generates text file lists for the data set
    :param jpg_dir: directory containing jpgs to be listed
    :param txt_dir: output txt directory
    :param split_percentage: split percentage for test and validation sets (recommended 20)
    """
    print('Generating txt files...')

    try:
        jpeg_names = [file for file in os.listdir(jpg_dir) if file.lower().endswith('.jpg')]
    except OSError as e:
        raise OSError(f"error listing {jpg_dir}: {e}")

    # split the list into training list and split_set list
    try:
        split_set, train_set = partition_list(jpeg_names, split_percentage, shuffle=True)
        print(f'Split test count: {len(split_set)}')
        print(f'Train set count: {len(train_set)}')
    except ValueError as e:
        raise ValueError(f"error partitioning list: {e}")

    # split the split_set list into validation and test lists
    test_set, val_set = split_list_in_half(split_set)
    print(f'Test set count: {len(test_set)}')
    print(f'Validation set count: {len(val_set)}')

    print('Writing txt files...')

    file_mappings = {
        'train.txt': (train_set, False),
        'test.txt': (test_set, False),
        'val.txt': (val_set, False),
        'trainval.txt': (train_set, False),  # first write with train_set
        'trainval.txt': (val_set, True)  # then append with val_set
    }

    for filename, (set_to_write, is_existing) in file_mappings.items():
        try:
            write_to_txt_file(os.path.join(txt_dir, filename), set_to_write, existing=is_existing)
        except IOError as e:
            raise IOError(f"Error writing to {filename}: {e}")

    print(f'..All txt files saved in: {txt_dir}')


def inject_negative_data_set(negatives_dir, jpg_dir, annotations_dir, txt_dir, val_test_percentage):
    """
    takes negative data set, copies to output folders, generates text files for new data set
    :param negatives_dir: directory containing negative jpg and xml files
    :param jpg_dir: output jpg directory
    :param annotations_dir: output annotations directory
    :param txt_dir: output txt directory
    :param val_test_percentage: split percentage for test and validation sets (recommended 20)
    """
    print('Injecting negative data set...')

    for dirpath, _, files in os.walk(negatives_dir):
        for file in files:
            file_ext = file.lower().split('.')[-1]
            if file_ext in ['jpg', 'jpeg']:
                destination = os.path.join(jpg_dir, file)
            elif file_ext == 'xml':
                destination = os.path.join(annotations_dir, file)
            else:
                print(f'File is neither .jpg, .jpeg nor .xml: {file}')
                continue

            source_path = os.path.join(dirpath, file)

            try:
                shutil.copy(source_path, destination)
            except IOError as e:
                raise IOError(f'error copying {file} to {destination}: {e}')
    try:
        generate_txt_files(jpg_dir, txt_dir, val_test_percentage)
    except Exception as e:
        print(f'error generating txt files: {e}')
        traceback.print_tb(e.__traceback__)
        sys.exit(1)

    print('..Finished injecting negative data set into current data set')


def prepare_voc(input_directory, image_directory, annotations_directory, existing_names):
    """
    takes current data set and renames all files unique, converts any pngs into jpgs
    saves new files into VOC output directories
    :param input_directory: current data set
    :param image_directory: output directory for images
    :param annotations_directory: output directory for annotations
    :param existing_names: set containing current filenames
    """
    for dir_path, _, files in os.walk(input_directory):
        for file_name in tqdm.tqdm(files):
            if file_name.lower().endswith('.png'):
                filename_no_ext = file_name.rsplit(".", 1)[0]
                xml_file_name = f'{filename_no_ext}.xml'

                if xml_file_name in files and xml_file_name not in existing_names:
                    new_filename = get_new_file_name(existing_names)

                    # process and save the image
                    img_path = os.path.join(dir_path, file_name)
                    try:
                        img = Image.open(img_path).convert('RGB')
                        img.save(os.path.join(image_directory, f'{new_filename}.jpg'))
                    except IOError as e:
                        raise IOError(f"Error processing image {file_name}: {e}")

                    # update XML file information
                    xml_input_path = os.path.join(input_directory, xml_file_name)
                    replace_dict = {'filename': f'{new_filename}.jpg',
                                    'path': f'{new_filename}.jpg'}
                    try:
                        replace_xml_file_information(xml_input_path, replace_dict)
                    except Exception as e:
                        raise Exception(f"Error processing {xml_file_name}: {e}")

                    # copy XML file
                    try:
                        shutil.copy(xml_input_path, os.path.join(annotations_directory, f'{new_filename}.xml'))
                    except IOError as e:
                        raise IOError(f"Error copying XML file {xml_file_name}: {e}")

                    existing_names.add(new_filename)

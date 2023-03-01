# PASCAL_VOC-data_set_tools

- Correct Dark Label VOC datasets for nvidia jetson inference training.
- Inject new data sets into existing ones.
- Generate and inject negative data sets into an existing VOC set.

Dark Label is a quick and easy tool for labelling video footage for training object detection neural networks. 

However, when exporting to PASCAL VOC, the data set exported is not actually in the format of PASCAL VOC and if you are handling a large amount of data, and adding to your data sets as time goes by, it proves a nightmare.

Yes, you can move on to bigger better solutions, but there is something about Dark Label being so quick to setup and use that made me stick with it, so I wrote some tools to sort out my data sets instead.

### The Problems:

1)
  - Outputs .png and .xml files into one folder
  - No training splits, no text files
  - Occasionally labels can accidently exported as empty if user miss-clicks while labelling
  - Filenames will cause conflicts when adding new data in the future
  - Blank labels will cause fatal crashes when attempting to train the model

2)
  - I wanted a way to inject just negatives into the set, to see if I could eliminate scenes without the objects being in the images

### The Solutions:

1)
  - Gather current data set
  - Generate new file names[^1]
  - Edit XML files to reflect filename changes
  - Place files in ANNOTATIONS | JPEGImages folders
  - Split data set and output text files to ImageSets folder

2)
  - Gather current data set
  - Input negative images folder
  - Generate new file names
  - Generate XML label files
  - Place files in ANNOTATIONS | JPEGImages folder
  - plit data set and output text files to ImageSets/Main folder

[^1]: I read somewhere once that having sequential file names in training neural networks has a risk of the network associating names with results. How true this is I do not know, but I choose to err on the side of caution, hence my files are randomly generated alpahnumerical names.

## Usage:

If you have an existing data set:
  - move xml and jpg files from ANNOTATIONS and JPEGImages folders to the input folder
  - delete current text files in the ImageSets/Main folder
  - images for negatives should be placed in negativesInput


### Creating a valid PASCAL VOC data set from the input directory:

Run: `py prepare_dataset.py --drk_lbl_voc`

### Generating and injecting negatives from the input and negativesInput directory:

Run: `py prepare_dataset.py --gen_neg`

If you have the rotten luck of accidently exporting a load of files with blank labels you can fix them using a function in voc_helpers.py called fix_missing_xml_object_name(xml_directory, label_text). Feed it the xml directory and the label to place in any blank object name spaces.

If you need to remove a label from a data set you can use another function in voc_helpers.py called remove_object_from_xml_files(xml_directory, object_names_set). Feed it the directory and a set of object names to remove.

## Video Demonstration:

[<img src="https://img.youtube.com/vi/rEyfXz5ceAk/maxresdefault.jpg" width="50%">](https://youtu.be/rEyfXz5ceAk)

[ @0xtommyOfficial, molmez.io ]




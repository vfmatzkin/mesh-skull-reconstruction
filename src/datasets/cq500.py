""" Functions to download and process the CQ500 dataset.

Note that you have to have permission to download this dataset, and the URL
of the text file with the images is not provided here.
"""

import os
import shutil
import urllib
import zipfile

import SimpleITK as sitk


def get_data(url, folder_path):
    """ Download the CQ500 dataset.

    Given the url of the text file with the images, and the path to the output
    folder, this function will download the dataset.

    :param url: CQ500 dataset url
    :param folder_path: Output folder path
    :return:
    """
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    # Download the txt file (url) and save it to the folder_path
    print('Downloading the txt file...')
    urllib.request.urlretrieve(url, folder_path + 'cq500_files.txt')
    # Load the lines of the txt file into a list stripping the \n
    with open(folder_path + 'cq500_files.txt') as f:
        lines = [line.rstrip('\n') for line in f]
    # Loop over the lines and download the images
    for url in lines:
        # Split the line into the filename and the url
        filename = url.split('/')[-1]
        print('File %s' % filename)

        # Download the image
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            print('  Zip already downloaded, skipping...')
        else:
            urllib.request.urlretrieve(url, path)

        # Check if the zip file was already extracted
        if path.endswith('.zip'):
            try:
                extracted_path = path.replace('.zip', '')
                if os.path.exists(extracted_path):
                    print('  Zip already extracted, skipping...')
                    continue

                # extract the zip file in path
                print('  Extracting zip file...')
                # Extract the zip file if it is not already extracted
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)
            except zipfile.BadZipfile:
                print(f'Bad zip file {path}')


def convert_nifti(input_folder, out_dir=None):
    """ Converts CQ500 folder and subfolders into NIfTI images

    :param input_folder: Input folder of the downloaded images
    :return:
    """
    out_dir = os.path.join(input_folder, 'converted') if out_dir is None \
        else out_dir
    os.makedirs(out_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_folder):
        # Exclude the converted folder and the folders inside it
        if root == out_dir or root.startswith(out_dir + '/'):
            continue

        root_is_im = len(files) > 0 and len(dirs) == 0
        if root_is_im:
            rel_path = os.path.relpath(root, input_folder)
            print(f'Converting {rel_path}')

            # Create the output folder
            subj = rel_path.split('/')[0]
            subj_folder = os.path.join(out_dir, subj)
            os.makedirs(subj_folder, exist_ok=True)

            # Add the subject name to the filename
            file_name = subj + '_' + os.path.split(root)[1] + '.nii.gz'
            image_path = os.path.join(subj_folder, file_name)

            # Don't overwrite the file if it already exists
            if os.path.exists(image_path):
                print('  File already exists, skipping...')
                continue

            # Convert the image to NIfTI using SimpleITK
            # Load the DICOM image
            sitk.ProcessObject_SetGlobalWarningDisplay(False)
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(root)
            reader.SetFileNames(dicom_names)
            img = reader.Execute()
            sitk.ProcessObject_SetGlobalWarningDisplay(True)

            # Save the image as NIfTI
            sitk.WriteImage(img, image_path)
            print('Converted %s to NIfTI' % image_path)
    return out_dir


def select_imgs(images_folder, output_folder=None):
    """ From the CQ500 dataset, select the biggest images for each subject.

    Note that it might copy images that are not part of the dataset like the
    body without including the head.

    :param images_folder: Folder of the previously converted to NIfTI images.
    :param output_folder: Folder where the selected images will be saved.
    :return: output_folder.
    """
    output_folder = os.path.join(images_folder, 'selected') \
        if output_folder is None else output_folder
    os.makedirs(output_folder, exist_ok=True)

    for subject in os.listdir(images_folder):
        subj_folder = os.path.join(images_folder, subject)
        if not os.path.isdir(subj_folder) or subject == 'selected':
            continue
        print(f'Selecting image for subject {subject}')
        # Get the path of the biggest file in that folder
        imgs = [os.path.join(subj_folder, f) for f in os.listdir(subj_folder)]
        biggest_file = max(imgs, key=os.path.getsize)
        # Save the file to the output folder
        biggest_file_path = os.path.join(subj_folder, biggest_file)
        biggest_file_out_path = os.path.join(output_folder,
                                             os.path.split(biggest_file)[1])
        # Copy the file using shutil
        print(f'Copying {biggest_file_path} to {biggest_file_out_path}')
        shutil.copyfile(biggest_file_path, biggest_file_out_path)

    return output_folder

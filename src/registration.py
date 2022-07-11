""" Registration using Deformetrica """

import os

from deformetrica.api import Deformetrica


def register_imgs(folder, fixed_image, output_dir):
    """ Register images using deformetrica Python API

    :param folder: Input folder containing images to register.
    :param fixed_image: Fixed image to register to.
    :return:
    """
    # instantiate a Deformetrica object
    df = Deformetrica(output_dir, verbosity='INFO')

    # List files, keep .nii.gz excluding fixed img, and create dataset dict.
    def cond(x): return x.endswith('.nii.gz') and x != fixed_image
    file_names = [f for f in os.listdir(folder) if cond(f)]
    file_paths = [os.path.join(folder, f) for f in file_names]
    fns = [[{'skull': i}] for i in file_paths]  # Dataset filenames
    ids = file_names  # noqa Subject IDs TODO Check if it has to be different from file_names

    # Moving images
    dataset_specifications = {'dataset_filenames': fns, 'subject_ids': ids}

    # Fixed image
    template_specifications = {
        'skull': {'deformable_object_type': 'image',
                  'kernel_type': 'torch', 'kernel_width': 20.0,
                  'noise_std': 1.0,
                  'filename': fixed_image,
                  'attachment_type': 'varifold'}
    }

    estimator_options = {'optimization_method_type': 'GradientAscent',
                         'initial_step_size': 1.,
                         'max_iterations': 25,
                         'max_line_search_iterations': 10}

    model = df.estimate_registration(template_specifications,
                                     dataset_specifications,
                                     estimator_options=estimator_options,
                                     model_options={
                                         'deformation_kernel_type': 'torch',
                                         'deformation_kernel_width': 40.0
                                     })

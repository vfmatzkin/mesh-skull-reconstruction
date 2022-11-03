import os
import deformetrica as dfca

iteration_status_dictionaries = []


def estimator_callback(status_dict):
    iteration_status_dictionaries.append(status_dict)
    return True


def estimate_registration(template_path, dataset_paths, output_path=None,
                          template_specifications=None,
                          dataset_specifications=None, model_options=None,
                          estimator_options=None, verbosity='INFO',
                          overwrite=True):
    """ Estimate a registration model from a template and a dataset.

    :param template_path: path to the template file
    :param dataset_paths: list of paths to the dataset files
    :param output_path: path to the output folder
    :param template_specifications: dict of template specifications
    :param dataset_specifications: dict of dataset specifications
    :param model_options: dict of model options
    :param estimator_options: dict of estimator options
    :param verbosity:  'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    :param overwrite: boolean to overwrite existing files
    """
    deform_atlas_reg(template_path, dataset_paths, output_path,
                     template_specifications, dataset_specifications,
                     model_options, estimator_options, verbosity, False,
                     overwrite)


def estimate_atlas(template_path, dataset_paths, output_path=None,
                   template_specifications=None, dataset_specifications=None,
                   model_options=None, estimator_options=None,
                   verbosity='INFO', overwrite=True):
    """ Estimate an atlas model from a template and a dataset.

    :param template_path: path to the template file
    :param dataset_paths: list of paths to the dataset files
    :param output_path: path to the output folder
    :param template_specifications: dict of template specifications
    :param dataset_specifications: dict of dataset specifications
    :param model_options: dict of model options
    :param estimator_options: dict of estimator options
    :param verbosity:  'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    :param overwrite: boolean to overwrite existing files
    """
    deform_atlas_reg(template_path, dataset_paths, output_path,
                     template_specifications, dataset_specifications,
                     model_options, estimator_options, verbosity, True,
                     overwrite)


def deform_atlas_reg(template_path, dataset_paths, output_path=None,
                     template_specifications=None, dataset_specifications=None,
                     model_options=None, estimator_options=None,
                     verbosity='INFO', atlas_creation=False, overwrite=True):
    """ Estimate a registration or atlas model from a template and a dataset.

    :param template_path: path to the template file
    :param dataset_paths: list of paths to the dataset files
    :param output_path: path to the output folder
    :param template_specifications: dict of template specifications
    :param dataset_specifications: dict of dataset specifications
    :param model_options: dict of model options
    :param estimator_options: dict of estimator options
    :param verbosity:  'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    :param atlas_creation: boolean to create an atlas or a registration model
    :param overwrite: boolean to overwrite existing files
    """
    if not output_path:
        out_folder_name = ('atlas_' if atlas_creation else 'reg_') + \
                          os.path.splitext(os.path.split(template_path)[1])[0]
        output_path = os.path.join(
            os.path.dirname(template_path), out_folder_name
        )

    print(f'Output path: {output_path}')
    if os.path.exists(output_path) and not overwrite:
        if len(os.listdir(output_path)) > 5:  # Normally its 18 files min
            print('  Output folder already exists and contains files. Please '
                  'delete the folder or set the overwrite flag.')
            return

    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    deformetrica = dfca.Deformetrica(output_path, verbosity)

    # Load always default params and override with user params if any
    tmpl = {
        'skull': {'deformable_object_type': 'SurfaceMesh',
                  'kernel_type': 'torch', 'kernel_width': 20.0,
                  'noise_std': 10.0,
                  'filename': template_path,
                  'attachment_type': 'current'}
    }
    if template_specifications:
        tmpl.update(template_specifications)

    dtset = {
        'dataset_filenames': [[{'skull': f}] for f in dataset_paths],
        'subject_ids': [
            os.path.splitext(os.path.split(f)[1])[0] for f in dataset_paths
        ],
    }
    if dataset_specifications:
        dtset.update(dataset_specifications)

    mopt = {
        'deformation_kernel_type': 'torch',
        'deformation_kernel_width': 40.0, 'dtype': 'float32'
    }
    if model_options:
        mopt.update(model_options)

    eopt = {
        'optimization_method_type': 'GradientAscent',
        'initial_step_size': 1., 'max_iterations': 25,
        'max_line_search_iterations': 10, 'callback': estimator_callback
    }
    if estimator_options:
        eopt.update(estimator_options)

    if atlas_creation:
        # perform a deterministic atlas estimation
        model = deformetrica.estimate_deterministic_atlas(
            tmpl, dtset, mopt, eopt
        )
    else:
        # perform a registration estimation
        model = deformetrica.estimate_registration(tmpl, dtset, mopt, eopt)

    return model

"""Configuration file for pytest for pynets."""

from pathlib import Path
import pytest
import numpy as np
import nibabel as nib
from dipy.core.gradients import gradient_table
import pickle
import os
from random import randint
from glob import glob


@pytest.fixture(scope='module')
def dmri_estimation_data():
    """Fixture for dmri estimation tests."""

    base_dir = str(Path(__file__).parent/"examples")
    B0_mask = f"{base_dir}/003/anat/mean_B0_bet_mask_tmp.nii.gz"

    dir_path = f"{base_dir}/003/dmri"
    dwi_file = f"{base_dir}/003/test_out/003/dwi/sub-003_dwi_reor-RAS_res-2mm.nii.gz"

    bvals = f"{dir_path}/sub-003_dwi.bval"
    bvecs = f"{base_dir}/003/test_out/003/dwi/bvecs_reor.bvec"

    gtab = gradient_table(np.loadtxt(bvals)[:11], np.loadtxt(bvecs)[:, :11])
    gtab.b0_threshold = 50
    gtab_bvals = gtab.bvals.copy()
    b0_thr_ixs = np.where(gtab_bvals < gtab.b0_threshold)[0]
    gtab_bvals[b0_thr_ixs] = 0
    gtab.b0s_mask = gtab_bvals == 0

    dwi_img = nib.load(dwi_file)
    dwi_data = dwi_img.get_fdata()[48:64, 48:64, 28:37, :11]
    data_img = nib.Nifti1Image(dwi_data, header=dwi_img.header, affine=dwi_img.affine)

    mask_img = nib.load(B0_mask)
    mask_data = mask_img.get_fdata()[48:64, 48:64, 28:37]
    mask_img = nib.Nifti1Image(mask_data, header=mask_img.header, affine=mask_img.affine)

    yield {'gtab': gtab, 'dwi_img': data_img, 'B0_mask_img': mask_img}


@pytest.fixture(scope='function')
def plotting_data():
    """Fixture for plotting tests."""

    base_dir = str(Path(__file__).parent/"examples")
    conn_matrix = np.genfromtxt(f"{base_dir}/miscellaneous/002_rsn-Default_nodetype-parc_model-sps_thrtype-PROP_thr-0.94.txt")

    labels_file_path = f"{base_dir}/miscellaneous/Default_func_labelnames_wb.pkl"
    labels_file = open(labels_file_path, 'rb')
    labels = pickle.load(labels_file)

    coord_file_path = f"{base_dir}/miscellaneous/Default_func_coords_wb.pkl"
    coord_file = open(coord_file_path, 'rb')
    coords = pickle.load(coord_file)

    yield {'conn_matrix': conn_matrix, 'labels': labels, 'coords': coords}

# data-related functions
def _generate_data():
    test_data_dir = str(Path(__file__).parent/"randomized_examples/")
    if os.path.isdir(test_data_dir) is False:
        os.makedirs(test_data_dir, exist_ok=True)
    test_data = [np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(12)]
    test_data = [np.nan_to_num(np.maximum(array, array.T)) for array in test_data]
    for array in range(1, len(test_data) + 1): 
        np.save(test_data_dir + "Randomized_data_" + str(array), test_data[array - 1])
    input_paths = [test_data_dir + "Randomized_data_" +  str(array) + ".npy" for array in range(1, len(test_data) + 1)]

    return input_paths


@pytest.fixture(scope='function') #Returns list for mutability
def random_data():
    return _generate_data()

def pytest_configure(): #Sets constants as tuples for immutability as safeguard against unintended changes
    pytest.constant_random_data = tuple(_generate_data())
    pytest.sub0021001_files = tuple(glob(str(Path(__file__).parent/"examples/miscellaneous/sub-0021001*thrtype-PROP*.npy"))) #All (94, 94) in shape


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 05 12:44:00 2021
@authors: Derek Pisner & Alex Ayala
"""
import pytest
import numpy as np
import networkx as nx
import time
from pathlib import Path
from pynets.stats import netmotifs
import logging
import importlib
from collections import Counter

logger = logging.getLogger(__name__)
logger.setLevel(50)


@pytest.mark.parametrize("N", [3, 4])
def test_countmotifs(N):
    """
    Test for countmotifs() functionality
    """
    start_time = time.time()
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/functional/25659_1_modality-func_rsn-Cont_est-partcorr_nodetype-parc_hpass-0Hz_extract-mean_raw.npy")

    start_time = time.time()
    umotifs = netmotifs.countmotifs(in_mat, N)
    print("%s%s%s" % ('thresh_and_fit (Functional, proportional thresholding) --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    assert isinstance(umotifs, Counter)

@pytest.mark.parametrize("use_gt", [True, False])
@pytest.mark.parametrize("thr", [.1, .2, .3, .4])
@pytest.mark.parametrize("N", [3, 4])
def test_adaptivethresh(use_gt, thr, N):
    """
    Test for adaptivethresh() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    mlib = ["1113", "1122", "1223", "2222", "2233", "3333"]
    in_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/structural/struct_DesikanKlein2012_25659_1_modality-dwi_rsn-Cont_est-csa_nodetype-parc_samples-10000streams_tt-local_dg-clos_ml-0.npy")

    mf = netmotifs.adaptivethresh(in_mat, thr, mlib, N, use_gt)

    assert isinstance(mf, np.ndarray)

def test_compare_motifs():
    """
    Test for compare_motifs() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    struct_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/structural/struct_DesikanKlein2012_25659_1_modality-dwi_rsn-Cont_est-csa_nodetype-parc_samples-10000streams_tt-local_dg-clos_ml-0.npy")
    func_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/functional/25659_1_modality-func_rsn-Cont_est-partcorr_nodetype-parc_hpass-0Hz_extract-mean_raw.npy")

    name = "compare"
    namer_dir = "tests"

    mg_dict, g_dict = netmotifs.compare_motifs(struct_mat, func_mat, name, namer_dir)

    assert isinstance(mg_dict, dict)
    assert isinstance(g_dict, dict)




def test_build_mx_multigraph():
    """
    Test for build_mx_multigraph() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    struct_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/structural/struct_DesikanKlein2012_25659_1_modality-dwi_rsn-Cont_est-csa_nodetype-parc_samples-10000streams_tt-local_dg-clos_ml-0.npy")
    func_mat = np.load(f"{base_dir}/miscellaneous/netmotifs_sample_data/functional/25659_1_modality-func_rsn-Cont_est-partcorr_nodetype-parc_hpass-0Hz_extract-mean_raw.npy")
    name = "MultilayerGraph"
    namer_dir = "tests/examples"

    mg_path = netmotifs.build_mx_multigraph(func_mat, struct_mat, name, namer_dir)

    assert isinstance(mg_path,str)

# def test_build_multigraphs():
#     """
#     Test for build_multigraphs() functionality
#     """
#     base_dir = str(Path(__file__).parent/"examples")
#     est_path_iterlist = ["/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy"]
#
#     netmotifs.build_multigraphs(est_path_iterlist, "test")

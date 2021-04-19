#!/usr/bin/env python

import pytest
from pathlib import Path
import numpy as np
import networkx as nx
import logging
from glob import glob
from pynets.stats import embeddings
import os
from random import randint

logger = logging.getLogger(__name__)
logger.setLevel(50)

to_nparrays = lambda data: [np.load(npfile) for npfile in data]
to_nxgraphs = lambda data: [nx.from_numpy_matrix(nparray) for nparray in to_nparrays(data)]
to_large_nparray = lambda data: np.stack(to_nparrays(data))


#pytest.constant_random_data and pytest.sub0021001_files initialized in conftest.py at runtime
#pylint: disable=no-member
@pytest.mark.parametrize("graph_path_list", [
    pytest.constant_random_data,
    pytest.sub0021001_files, 
    pytest.param(pytest.sub0021001_files[0:1], marks=pytest.mark.xfail), 
    pytest.param([], marks=pytest.mark.xfail),
])
@pytest.mark.parametrize("data_type", [to_nparrays, to_nxgraphs, to_large_nparray])
def test_omni(graph_path_list, data_type, ID="0021001", atlas="Default"):
    pop_array = data_type(graph_path_list)
    output_file = embeddings._omni_embed(pop_array, atlas, graph_path_list, ID)
    assert Path(output_file).is_file() and output_file.endswith(".npy")

    if isinstance(pop_array, np.ndarray) and pop_array.shape == (12, 94, 94):
        assert np.load(output_file).shape[0] == 94

    if isinstance(pop_array[0], nx.Graph) and len(pop_array) == 12 and \
        all([nx.to_numpy_matrix(graph).shape == (94, 94) for graph in pop_array]):
        assert np.load(output_file).shape[0] == 94

    if isinstance(pop_array[0], np.ndarray) and len(pop_array) == 12 and \
        all([graph.shape == (94, 94) for graph in pop_array]):
        assert np.load(output_file).shape[0] == 94


#pylint: disable=no-member
@pytest.mark.parametrize("graph_path_list,graph_path", [
     (pytest.constant_random_data, pytest.constant_random_data[0]),
     (pytest.sub0021001_files, pytest.sub0021001_files[0]),
     pytest.param(pytest.sub0021001_files, str(Path(pytest.sub0021001_files[0]).parent), marks=pytest.mark.xfail(strict=True)),
     #^Strict xfail to ensure file is placed in intended directory
     pytest.param(pytest.sub0021001_files, "", marks=pytest.mark.xfail),
     pytest.param(pytest.sub0021001_files[0:1], pytest.sub0021001_files[0], marks=pytest.mark.xfail), 
     pytest.param([], pytest.sub0021001_files[0], marks=pytest.mark.xfail)
 ])
@pytest.mark.parametrize("data_type", [to_nparrays, to_nxgraphs, to_large_nparray])
def test_mase(graph_path_list, graph_path, data_type, ID="0021001", atlas="Default"):
    pop_array = data_type(graph_path_list)
    output_file = embeddings._mase_embed(pop_array, atlas, graph_path, ID)
    assert Path(output_file).is_file() and output_file.endswith(".npy")
    output_shape = np.load(output_file).shape
    if isinstance(pop_array, np.ndarray) and pop_array.shape == (12, 94, 94):
        assert output_shape[0] == 12
        assert output_shape[1] == output_shape[2]
    if isinstance(pop_array[0], nx.Graph) and len(pop_array) == 12 and \
        all([nx.to_numpy_matrix(graph).shape == (94, 94) for graph in pop_array]):
        assert output_shape[0] == 12
        assert output_shape[1] == output_shape[2]
    if isinstance(pop_array[0], np.ndarray) and len(pop_array) == 12 and \
        all([graph.shape == (94, 94) for graph in pop_array]):
        assert output_shape[0] == 12
        assert output_shape[1] == output_shape[2]


#pylint: disable=no-member
@pytest.mark.parametrize("mat, graph_path, unpack", 
    [tuple([mat] * 2 + [True]) for mat in pytest.constant_random_data] + \
    [tuple([mat] * 2 + [True]) for mat in pytest.sub0021001_files] + [
    pytest.param(pytest.sub0021001_files[0], str(Path(pytest.sub0021001_files[0]).parent), True, marks=pytest.mark.xfail),
    pytest.param(pytest.sub0021001_files[0], "", True, marks=pytest.mark.xfail),
    pytest.param(pytest.sub0021001_files, pytest.sub0021001_files[0], False, marks=pytest.mark.xfail(strict=True)), 
    #^Strict to ensure multiple graphs don't get analyzed as a single graph
    pytest.param([], pytest.sub0021001_files[0], False, marks=pytest.mark.xfail)
    ]) 
@pytest.mark.parametrize("data_type", [to_nparrays, to_nxgraphs])
def test_ase(mat, graph_path, unpack, data_type, ID="0021001", subgraph_name="all_nodes", \
n_components=None, prune=0, norm=1, atlas="Default"):
    if unpack: 
        mat = data_type([mat])[0]
    else:
        mat = data_type(mat)
    output_file = embeddings._ase_embed(mat, atlas, graph_path, ID)
    assert Path(output_file).is_file() and output_file.endswith(".npy")
    print(output_file)

    output_shape = np.load(output_file).shape

    if isinstance(mat, nx.Graph) and nx.to_numpy_matrix(mat).shape == (94, 94):
        assert output_shape[0] == 94

    if isinstance(mat, np.ndarray) and mat.shape == (94, 94):
        assert output_shape[0] == 94


#pylint: disable=no-member
@pytest.mark.parametrize("est_path_iterlist", [
    list(pytest.constant_random_data),
    list(pytest.sub0021001_files),
    [pytest.sub0021001_files[0]],
    pytest.param([], marks=pytest.mark.xfail),
    pytest.param(pytest.sub0021001_files[0], marks=pytest.mark.xfail),
])
def test_build_asetomes(est_path_iterlist, ID="0021001"):
    output_paths = embeddings.build_asetomes(est_path_iterlist,  ID)
    assert all([Path(output_file).is_file() and output_file.endswith(".npy") for output_file in output_paths])

    if all([input_array.shape == (94, 94) for input_array in to_nparrays(est_path_iterlist)]):
        assert all(output_array.shape == (94, 1) for output_array in to_nparrays(output_paths))
    

#pylint: disable=no-member
@pytest.mark.parametrize("est_path_iterlist", [
    [[pytest.constant_random_data[x], pytest.constant_random_data[x + 1]] for x in range(0, len(pytest.constant_random_data), 2)],
    [[pytest.sub0021001_files[x], pytest.sub0021001_files[x + 1]] for x in range(0, len(pytest.sub0021001_files), 2)],
    [[pytest.sub0021001_files[0], pytest.sub0021001_files[1]]],
    pytest.param([pytest.sub0021001_files[0], pytest.sub0021001_files[1]], marks=pytest.mark.xfail),
    pytest.param([], marks=pytest.mark.xfail),
    pytest.param(pytest.sub0021001_files[0], marks=pytest.mark.xfail(strict=True))
]) #^ Strict to ensure a meaningful analysis occurs
def test_build_masetome(est_path_iterlist, ID="0021001"):
    output_paths = embeddings.build_masetome(est_path_iterlist,  ID)
    assert all([Path(output_file).is_file() and output_file.endswith(".npy") for output_file in output_paths])

    if all([input_array.shape == (94, 94) for pair in est_path_iterlist for input_array in to_nparrays(pair)]):
        assert all(output_array.shape == (2, 1, 1) for output_array in to_nparrays(output_paths))


#pylint: disable=no-member
@pytest.mark.parametrize("est_path_iterlist", [
    pytest.constant_random_data,
    pytest.sub0021001_files,
    [pytest.sub0021001_files[0]],
    pytest.param([], marks=pytest.mark.xfail),
    pytest.param(pytest.sub0021001_files[0], marks=pytest.mark.xfail),
])
def test_build_omnetome(est_path_iterlist, ID="0021001"):
    output_paths = embeddings.build_omnetome(est_path_iterlist, ID)
    assert type(output_paths[0]) == list and type(output_paths[1]) == list and len(output_paths) == 2
    output_paths = output_paths[0] + output_paths[1]
    assert all([Path(output_file).is_file() and output_file.endswith(".npy") for output_file in output_paths])
    
    if all([input_array.shape == (94, 94) for input_array in to_nparrays(est_path_iterlist)]):
        assert all([output_array.shape == (94, 1) for output_array in to_nparrays(output_paths)])


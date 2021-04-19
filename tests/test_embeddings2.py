from pynets.stats.embeddings import _omni_embed, _mase_embed, _ase_embed, build_asetomes, build_masetome, build_omnetome
from glob import glob
import numpy as np
from random import randint
from collections import Counter
import os

paths = "/home/landluke11/embeddings2tests/"

def omni_sim():
    output_shapes = []
    for array_series in range(1000):
        tested_pop_array = [np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(12)]
        tested_pop_array = [np.nan_to_num(np.maximum(array, array.T)) for array in tested_pop_array]
        for array in range(1, len(tested_pop_array) + 1): 
            np.save(paths + str(array_series) + "_" + str(array), tested_pop_array[array - 1])
        input_paths = [paths + str(array_series) + "_" +  str(array) + ".npy" for array in range(1, len(tested_pop_array) + 1)]
        output_shapes.append(np.load(_omni_embed(tested_pop_array, "Default", input_paths, "")).shape)

    print(Counter(output_shapes))

def mase_sim():
    output_shapes = []
    for array_series in range(1000):
        tested_pop_array = [np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(12)]
        tested_pop_array = [np.nan_to_num(np.maximum(array, array.T)) for array in tested_pop_array]
        input_path = paths + str(array_series) + ".npy"
        np.save(input_path, tested_pop_array[0])
        output_shapes.append(np.load(_mase_embed(tested_pop_array, "Default", input_path, "")).shape)

    print(Counter(output_shapes))

def ase_sim():
    output_shapes = []
    for array in range(1000):
        mat = np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)])
        mat = np.nan_to_num(np.maximum(mat, mat.T))
        input_path = paths + str(array) + ".npy"
        np.save(input_path, mat)
        output_shapes.append(np.load(_ase_embed(mat, "Default", input_path, "")).shape)

    print(Counter(output_shapes))

def build_asetomes_sim():
    output_shapes = []
    for array_series in range(1000):
        tested_pop_array = [np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(12)]
        tested_pop_array = [np.nan_to_num(np.maximum(array, array.T)) for array in tested_pop_array]
        for array in range(1, len(tested_pop_array) + 1): 
            np.save(paths + str(array_series) + "_" + str(array), tested_pop_array[array - 1])
        input_paths = [paths + str(array_series) + "_" +  str(array) + ".npy" for array in range(1, len(tested_pop_array) + 1)]
        output_paths = build_asetomes(input_paths, str(array_series))
        output_shapes += [np.load(mat).shape for mat in output_paths]
        print("...")

    print(Counter(output_shapes))

def build_masetome_sim():
    output_shapes = []
    for array_series in range(1000):
        print(array_series)
        tested_pop_array = [[np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(2)] for _ in range(6)]
        tested_pop_array = [[np.nan_to_num(np.maximum(array, array.T)) for array in pair] for pair in tested_pop_array]
        for pair_num in range(len(tested_pop_array)): 
            for array_num in range(len(tested_pop_array[pair_num])):
                np.save(paths + str(array_series) + "_" + str(pair_num) + "_" + str(array_num), tested_pop_array[pair_num][array_num])
        input_paths = [[paths + str(array_series) + "_" +  str(pair_num) + "_" + str(array_num) + ".npy" \
            for array_num in range(len(tested_pop_array[pair_num]))] for pair_num in range(len(tested_pop_array))]
        output_paths = build_masetome(input_paths, str(array_series))
        output_shapes += [np.load(mat).shape for mat in output_paths]
        print("...")

    print(Counter(output_shapes))

def build_omnetome_sim():
    output_shapes = []
    for array_series in range(1000):
        print(array_series)
        tested_pop_array = [np.asarray([[np.float64(randint(0, 64)) for _ in range(94)] for _ in range(94)]) for _ in range(12)]
        tested_pop_array = [np.nan_to_num(np.maximum(array, array.T)) for array in tested_pop_array]
        for array in range(1, len(tested_pop_array) + 1): 
            np.save(paths + str(array_series) + "_" + str(array), tested_pop_array[array - 1])
        input_paths = [paths + str(array_series) + "_" +  str(array) + ".npy" for array in range(1, len(tested_pop_array) + 1)]
        output_paths = build_omnetome(input_paths, str(array_series))
        output_shapes += [tuple([tuple([np.load(mat).shape for mat in path_type]) for path_type in output_paths])]
        print("...")
    print(output_shapes)
    print(Counter(output_shapes))

build_omnetome_sim()


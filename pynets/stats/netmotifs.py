#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:40:07 2017
Copyright (C) 2016
@author: Derek Pisner & James Kunert-Graf
"""
import numpy as np
import warnings
import os
import networkx as nx
from copy import copy
from pathlib import Path
from collections import Counter

warnings.filterwarnings("ignore")


def countmotifs(A, N=4):
    """
    Counts number of motifs with size N from A.

    Parameters
    ----------
    A : ndarray
        M x M Connectivity matrix
    N : int
        Size of motif type. Default is N=4, only 3 or 4 supported.

    Returns
    -------
    umotifs : Counter
        Total count of size N motifs for graph A.

    References
    ----------
    .. [1] Sporns, O., & Kötter, R. (2004). Motifs in Brain Networks.
      PLoS Biology. https://doi.org/10.1371/journal.pbio.0020369

    """
    import gc

    assert N in [3, 4], "Only motifs of size N=3,4 currently supported"
    X2 = np.array([[k] for k in range(A.shape[0] - 1)])
    for n in range(N - 1):
        X = copy(X2)
        X2 = []
        for vsub in X:
            # in_matind list of nodes neighboring vsub with a larger index than
            # root v
            idx = np.where(np.any(A[(vsub[0] + 1):, vsub], 1))[0] + vsub[0] + 1
            # Only keep node indices not in vsub
            idx = idx[[k not in vsub for k in idx]]
            if len(idx) > 0:
                # If new neighbors found, add all new vsubs to list
                X2.append([np.append(vsub, ik) for ik in idx])
        if len(X2) > 0:
            X2 = np.vstack(X2)
        else:
            umotifs = Counter([])
            return umotifs

    X2 = np.sort(X2, 1)
    X2 = X2[
        np.unique(
            np.ascontiguousarray(X2).view(
                np.dtype((np.void, X2.dtype.itemsize * X2.shape[1]))
            ),
            return_index=True,
        )[1]
    ]
    umotifs = Counter(
        ["".join(np.sort(np.sum(A[x, :][:, x], 1)).astype(int).astype(str))
         for x in X2]
    )
    del X2
    gc.collect()
    return umotifs


def adaptivethresh(in_mat, thr, mlib, N, use_gt=False):
    """
    Counts number of motifs with a given absolute threshold.

    Parameters
    ----------
    in_mat : ndarray
        M x M Connectivity matrix
    thr : float
        Absolute threshold [0, 1].
    mlib : list
        List of motif classes.

    Returns
    -------
    mf : ndarray
        1D vector listing the total motifs of size N for each
        class of mlib.

    References
    ----------
    .. [1] Battiston, F., Nicosia, V., Chavez, M., & Latora, V. (2017).
      Multilayer motif analysis of brain networks. Chaos.
      https://doi.org/10.1063/1.4979282

    """

    if use_gt is True:
        try:
            import graph_tool.all as gt
            from pynets.stats.netstats import np2gt

            g = np2gt((in_mat > thr).astype(int))
            mlib, mf = gt.motifs(gt.GraphView(g, directed=False), k=N)
        except ImportError as e:
            print(e, "graph_tool not installed!")
    else:
        from pynets.stats.netmotifs import countmotifs
        mf = countmotifs((in_mat > thr).astype(int), N=N)

    try:
        mf = np.array([mf[k] for k in mlib])
    except BaseException:
        print('0 motifs...')
        mf = np.zeros(len(mlib))
    return mf


def compare_motifs(struct_mat, func_mat, name, namer_dir, bins=20, N=4):
    """
    Compare motif structure and population across structural and functional
    graphs to achieve a homeostatic absolute threshold of each that optimizes
    multiplex community detection and analysis.

    Parameters
    ----------
    in_mat : ndarray
        M x M Connectivity matrix
    thr : float
        Absolute threshold [0, 1].
    mlib : list
        List of motif classes.

    Returns
    -------
    mg_dict : dict

    g_dict : dict
        

    References
    ----------
    .. [1] Battiston, F., Nicosia, V., Chavez, M., & Latora, V. (2017).
      Multilayer motif analysis of brain networks. Chaos.
      https://doi.org/10.1063/1.4979282

    """
    from pynets.stats.netmotifs import adaptivethresh
    from pynets.core.thresholding import threshold_absolute
    from pynets.core.thresholding import standardize
    from scipy import spatial
    from nilearn.connectome import sym_matrix_to_vec
    import pandas as pd
    import gc
    import math

    mlib = ["1113", "1122", "1223", "2222", "2233", "3333"]

    # Standardize structural graph
    struct_mat = standardize(struct_mat)
    dims_struct = struct_mat.shape[0]
    struct_mat[range(dims_struct), range(dims_struct)] = 0
    at_struct = adaptivethresh(struct_mat, float(0.0), mlib, N)
    print(
        "%s%s%s" %
        ("Layer 1 (structural) has: ",
         np.sum(at_struct),
         " total motifs"))

    # Functional graph threshold window
    func_mat = standardize(func_mat)
    dims_func = func_mat.shape[0]
    func_mat[range(dims_func), range(dims_func)] = 0
    tmin_func = func_mat.min()
    tmax_func = func_mat.max()
    threshes_func = np.linspace(tmin_func, tmax_func, bins)

    assert np.all(
        struct_mat == struct_mat.T), "Structural Matrix must be symmetric"
    assert np.all(
        func_mat == func_mat.T), "Functional Matrix must be symmetric"

    # Count motifs
    print("%s%s%s%s" % ("Mining ", N, "-node motifs: ", mlib))
    motif_dict = {}
    motif_dict["struct"] = {}
    motif_dict["func"] = {}

    mat_dict = {}
    mat_dict["struct"] = sym_matrix_to_vec(struct_mat, discard_diagonal=True)
    mat_dict["funcs"] = {}
    for thr_func in threshes_func:
        # Count
        at_func = adaptivethresh(func_mat, float(thr_func), mlib, N)
        motif_dict["struct"]["%s%s" % ("thr-", np.round(thr_func, 4))] = \
            at_struct
        motif_dict["func"]["%s%s" % ("thr-", np.round(thr_func, 4))] = at_func
        mat_dict["funcs"]["%s%s" % ("thr-", np.round(thr_func, 4))] = \
            sym_matrix_to_vec(
            threshold_absolute(func_mat, thr_func), discard_diagonal=True)

        print(
            "%s%s%s%s%s"
            % (
                "Layer 2 (functional) with absolute threshold of: ",
                np.round(thr_func, 2),
                " yields ",
                np.sum(at_func),
                " total motifs",
            )
        )
        gc.collect()

        if np.sum(at_struct) == np.sum(at_func):
            break

    df = pd.DataFrame(motif_dict)

    for idx in range(len(df)):
        df.at[
            df.index[idx],
            "motif_dist"] = spatial.distance.cosine(df["struct"][idx],
                                                    df["func"][idx])

    df = df[pd.notnull(df["motif_dist"])]

    for idx in range(len(df)):
        df.at[
            df.index[idx],
            "graph_dist_cosine"] = spatial.distance.cosine(
                mat_dict["struct"].reshape(-1, 1),
                mat_dict["funcs"][df.index[idx]].reshape(-1, 1),
        )
        df.at[
            df.index[idx],
            "graph_dist_correlation"] = spatial.distance.correlation(
                mat_dict["struct"].reshape(-1, 1),
                mat_dict["funcs"][df.index[idx]].reshape(-1, 1),
        )

    df["struct_func_3333"] = np.zeros(len(df))
    df["struct_func_2233"] = np.zeros(len(df))
    df["struct_func_2222"] = np.zeros(len(df))
    df["struct_func_1223"] = np.zeros(len(df))
    df["struct_func_1122"] = np.zeros(len(df))
    df["struct_func_1113"] = np.zeros(len(df))
    df["struct_3333"] = np.zeros(len(df))
    df["func_3333"] = np.zeros(len(df))
    df["struct_2233"] = np.zeros(len(df))
    df["func_2233"] = np.zeros(len(df))
    df["struct_2222"] = np.zeros(len(df))
    df["func_2222"] = np.zeros(len(df))
    df["struct_1223"] = np.zeros(len(df))
    df["func_1223"] = np.zeros(len(df))
    df["struct_1122"] = np.zeros(len(df))
    df["func_1122"] = np.zeros(len(df))
    df["struct_1113"] = np.zeros(len(df))
    df["func_1113"] = np.zeros(len(df))

    # for idx in range(len(df)):
    #     df.at[df.index[idx], "struct_3333"] = df["struct"][idx][-1]
    #     df.at[df.index[idx], "func_3333"] = df["func"][idx][-1]
    #
    #     df.at[df.index[idx], "struct_2233"] = df["struct"][idx][-2]
    #     df.at[df.index[idx], "func_2233"] = df["func"][idx][-2]
    #
    #     df.at[df.index[idx], "struct_2222"] = df["struct"][idx][-3]
    #     df.at[df.index[idx], "func_2222"] = df["func"][idx][-3]
    #
    #     df.at[df.index[idx], "struct_1223"] = df["struct"][idx][-4]
    #     df.at[df.index[idx], "func_1223"] = df["func"][idx][-4]
    #
    #     df.at[df.index[idx], "struct_1122"] = df["struct"][idx][-5]
    #     df.at[df.index[idx], "func_1122"] = df["func"][idx][-5]
    #
    #     df.at[df.index[idx], "struct_1113"] = df["struct"][idx][-6]
    #     df.at[df.index[idx], "func_1113"] = df["func"][idx][-6]

    df["struct_func_3333"] = np.abs(df["struct_3333"] - df["func_3333"])
    df["struct_func_2233"] = np.abs(df["struct_2233"] - df["func_2233"])
    df["struct_func_2222"] = np.abs(df["struct_2222"] - df["func_2222"])
    df["struct_func_1223"] = np.abs(df["struct_1223"] - df["func_1223"])
    df["struct_func_1122"] = np.abs(df["struct_1122"] - df["func_1122"])
    df["struct_func_1113"] = np.abs(df["struct_1113"] - df["func_1113"])

    df = df.drop(columns=["struct", "func"])

    df = df.loc[~(df == 0).all(axis=1)]

    df = df.sort_values(
        by=[
            "motif_dist",
            "graph_dist_cosine",
            "graph_dist_correlation",
            "struct_func_3333",
            "struct_func_2233",
            "struct_func_2222",
            "struct_func_1223",
            "struct_func_1122",
            "struct_func_1113",
            "struct_3333",
            "func_3333",
            "struct_2233",
            "func_2233",
            "struct_2222",
            "func_2222",
            "struct_1223",
            "func_1223",
            "struct_1122",
            "func_1122",
            "struct_1113",
            "func_1113",
        ],
        ascending=[
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
    )

    # Take the top 25th percentile
    df = df.head(int(math.ceil(0.25 * len(df))))
    best_threshes = []
    best_mats = []
    best_multigraphs = []
    for key in list(df.index):
        func_mat_tmp = func_mat.copy()
        struct_mat_tmp = struct_mat.copy()
        struct_thr = float(key.split("-")[-1])
        func_thr = float(key.split("-")[-1])
        best_threshes.append(str(func_thr))

        func_mat_tmp[func_mat_tmp < func_thr] = 0
        struct_mat_tmp[struct_mat_tmp < struct_thr] = 0
        best_mats.append((func_mat_tmp, struct_mat_tmp))

        mG = build_mx_multigraph(
            func_mat,
            struct_mat,
            f"{name}_{key}",
            namer_dir)
        best_multigraphs.append(mG)

    mg_dict = dict(zip(best_threshes, best_multigraphs))
    g_dict = dict(zip(best_threshes, best_mats))

    return mg_dict, g_dict


def build_mx_multigraph(func_mat, struct_mat, name, namer_dir):
    """
    It creates a symmetric (undirected) MultilayerGraph object from
    vertex-aligned structural and functional connectivity matrices.

    Parameters:
    -----------
    func_mat : ndarray
        Functional adjacency matrix of size N x N.
    struct_mat : ndarray
        Structural adjacency matrix of size N x N.
    name : str
        Intended name of the multiplex object.
    namer_dir : str
        Path to output directory.

    Returns:
    --------
    mg_path : str
        A filepath to a gpickled MultilayerGraph object

    References
    ----------
    .. [1] R. Amato, N. E Kouvaris, M. San Miguel and A. Diaz-Guilera,
      Opinion competition dynamics on multiplex networks, New J. Phys.
      DOI: https://doi.org/10.1088/1367-2630/aa936a
    .. [2] N. E. Kouvaris, S. Hata and A. Diaz-Guilera, Pattern formation
      in multiplex networks, Scientific Reports 5, 10840 (2015).
      http://www.nature.com/srep/2015/150604/srep10840/full/srep10840.html
    .. [3] A. Sole-Ribata, M. De Domenico, N. E. Kouvaris, A. Diaz-Guilera, S.
      Gomez and A. Arenas, Spectral properties of the Laplacian of a multiplex
      network, Phys. Rev. E 88, 032807 (2013).
      http://journals.aps.org/pre/abstract/10.1103/PhysRevE.88.032807

    """
    import networkx as nx
    import multinetx as mx

    try:
        import cPickle as pickle
    except ImportError:
        import _pickle as pickle

    mg = mx.MultilayerGraph()
    N = struct_mat.shape[0]
    adj_block = mx.lil_matrix(np.zeros((N * 2, N * 2)))
    adj_block[0:N, N: 2 * N] = np.identity(N)
    adj_block += adj_block.T
    G_struct = nx.from_numpy_matrix(struct_mat)
    G_func = nx.from_numpy_matrix(func_mat)
    mg.add_layer(G_struct)
    mg.add_layer(G_func)
    mg.layers_interconnect(inter_adjacency_matrix=adj_block)
    mg.name = name

    # Save mG to pickle
    graph_dir = f"{namer_dir}/mplx_graphs"
    if not os.path.isdir(graph_dir):
        os.mkdir(graph_dir)
    mG_path = f"{graph_dir}/{name[:200]}_mG.pkl"
    nx.write_gpickle(mg, mG_path, protocol=2)

    return mG_path


def multigraph_matching(paths):
    import networkx as nx
    import numpy as np
    import glob
    from pynets.core import thresholding
    from graspologic.utils import remove_loops, symmetrize, \
        multigraph_lcc_intersection
    from graspologic.match import GraphMatch
    from pynets.core.nodemaker import get_brainnetome_node_attributes

    [struct_graph_path, func_graph_path] = paths
    struct_mat = np.load(struct_graph_path)
    func_mat = np.load(func_graph_path)

    [struct_coords, struct_labels, struct_label_intensities] = \
        get_brainnetome_node_attributes(glob.glob(
            f"{str(Path(struct_graph_path).parent.parent)}/nodes/*.json"),
        struct_mat.shape[0])

    [func_coords, func_labels, func_label_intensities] = \
        get_brainnetome_node_attributes(glob.glob(
            f"{str(Path(func_graph_path).parent.parent)}/nodes/*.json"),
        func_mat.shape[0])

    # Find intersecting nodes across modalities (i.e. assuming the same
    # parcellation, but accomodating for the possibility of dropped nodes)
    diff1 = list(set(struct_label_intensities) - set(func_label_intensities))
    diff2 = list(set(func_label_intensities) - set(struct_label_intensities))
    G_struct = nx.from_numpy_array(struct_mat)
    G_func = nx.from_numpy_array(func_mat)

    bad_idxs = []
    for val in diff1:
        bad_idxs.append(struct_label_intensities.index(val))
        bad_idxs = sorted(list(set(bad_idxs)), reverse=True)
        if type(struct_coords) is np.ndarray:
            struct_coords = list(tuple(x) for x in struct_coords)
    for j in bad_idxs:
        G_struct.remove_node(j)
        print(f"Removing: {(struct_labels[j], struct_coords[j])}...")
        del struct_labels[j], struct_coords[j]

    bad_idxs = []
    for val in diff2:
        bad_idxs.append(func_label_intensities.index(val))
        bad_idxs = sorted(list(set(bad_idxs)), reverse=True)
        if type(func_coords) is np.ndarray:
            func_coords = list(tuple(x) for x in func_coords)
    for j in bad_idxs:
        G_func.remove_node(j)
        print(f"Removing: {(func_labels[j], func_coords[j])}...")
        del func_labels[j], func_coords[j]

    struct_mat = nx.to_numpy_array(G_struct)
    func_mat = nx.to_numpy_array(G_func)

    struct_mat = thresholding.autofix(symmetrize(remove_loops(struct_mat)))
    func_mat = thresholding.autofix(symmetrize(remove_loops(func_mat)))

    metadata = {}
    assert (
        len(struct_coords)
        == len(struct_labels)
        == len(func_coords)
        == len(func_labels)
        == func_mat.shape[0]
    )
    metadata["coords"] = struct_coords
    metadata["labels"] = struct_labels

    gmp = GraphMatch()
    gmp = gmp.fit(struct_mat, func_mat)
    func_mat = func_mat[np.ix_(gmp.perm_inds_, gmp.perm_inds_)]
    print("Number of edge disagreements after matching: ",
         np.sum(abs(struct_mat - func_mat)))

    func_mat[~struct_mat.astype("bool")] = 0
    struct_mat[~func_mat.astype("bool")] = 0
    print(
        "Edge disagreements after masking: ",
        sum(sum(abs(func_mat - struct_mat))),
    )

    metadata = {}
    assert (
        len(struct_coords)
        == len(struct_labels)
        == len(func_coords)
        == len(func_labels)
        == func_mat.shape[0]
    )
    metadata["coords"] = struct_coords
    metadata["labels"] = struct_labels

    return struct_mat, func_mat, metadata


def motif_matching(
    paths,
    ID,
    atlas,
    namer_dir,
    name_list,
    metadata_list,
    multigraph_list_all,
    graph_path_list_all,
    rsn=None,
):
    import numpy as np
    from pynets.stats.netmotifs import compare_motifs

    [struct_graph_path, func_graph_path] = paths

    [struct_mat, func_mat, metadata] = multigraph_matching(paths)

    metadata_list.append(metadata)

    if func_mat.shape == struct_mat.shape:
        struct_name = struct_graph_path.split("/rawgraph_"
                                              )[-1].split(".npy")[0]
        func_name = func_graph_path.split("/rawgraph_")[-1].split(".npy")[0]
        name = f"sub-{ID}_{atlas}_mplx_Layer-1_{struct_name}_" \
               f"Layer-2_{func_name}"
        name_list.append(name)
        try:
            [mldict, g_dict] = compare_motifs(
                struct_mat, func_mat, name, namer_dir)
        except BaseException:
            print(f"Adaptive thresholding by motif comparisons failed "
                  f"for {name}. This usually happens when no motifs are found")
            return [], [], [], []

        multigraph_list_all.append(list(mldict.values())[0])
        graph_path_list = []
        for thr in list(g_dict.keys()):
            multigraph_path_list_dict = {}
            [struct, func] = g_dict[thr]

            struct_out = f"{namer_dir}/struct_{atlas}_{struct_name}.npy"
            func_out = f"{namer_dir}/struct_{atlas}_{func_name}_" \
                       f"motif-{thr}.npy"
            np.save(struct_out, struct)
            np.save(func_out, func)
            multigraph_path_list_dict[f"struct_{atlas}_{thr}"] = struct_out
            multigraph_path_list_dict[f"func_{atlas}_{thr}"] = func_out
            graph_path_list.append(multigraph_path_list_dict)
        graph_path_list_all.append(graph_path_list)
    else:
        print(
            f"Skipping {rsn} rsn, since structural and functional graphs are "
            f"not identical shapes."
        )

    return name_list, metadata_list, multigraph_list_all, graph_path_list_all


def build_multigraphs(est_path_iterlist, ID):
    """
    Constructs a multimodal multigraph for each available resolution of
    vertices.

    Parameters
    ----------
    est_path_iterlist : list
        List of file paths to .npy file containing graph.
    ID : str
        A subject id or other unique identifier.

    Returns
    -------
    multigraph_list_all : list
        List of multiplex graph dictionaries corresponding to
        each unique node resolution.
    graph_path_list_top : list
        List of lists consisting of pairs of most similar
        structural and functional connectomes for each unique node resolution.

    References
    ----------
    .. [1] Bullmore, E., & Sporns, O. (2009). Complex brain networks: Graph
      theoretical analysis of structural and functional systems.
      Nature Reviews Neuroscience. https://doi.org/10.1038/nrn2575
    .. [2] Vaiana, M., & Muldoon, S. F. (2018). Multilayer Brain Networks.
      Journal of Nonlinear Science. https://doi.org/10.1007/s00332-017-9436-8

    """
    import os
    import itertools
    import numpy as np
    from pathlib import Path
    from pynets.core.utils import flatten
    from pynets.stats.netmotifs import motif_matching
    from pynets.core.utils import load_runconfig

    raw_est_path_iterlist = list(
        set(
            [
                os.path.dirname(i) + '/raw' + os.path.basename(i).split(
                    "_thrtype")[0] + ".npy"
                for i in list(flatten(est_path_iterlist))
            ]
        )
    )

    # Available functional and structural connectivity models
    hardcoded_params = load_runconfig()
    try:
        func_models = hardcoded_params["available_models"]["func_models"]
    except KeyError:
        print(
            "ERROR: available functional models not sucessfully extracted"
            " from runconfig.yaml"
        )
    try:
        struct_models = hardcoded_params["available_models"][
            "struct_models"]
    except KeyError:
        print(
            "ERROR: available structural models not sucessfully extracted"
            " from runconfig.yaml"
        )

    atlases = list(set([x.split("/")[-3].split("/")[0]
                        for x in raw_est_path_iterlist]))
    parcel_dict_func = dict.fromkeys(atlases)
    parcel_dict_dwi = dict.fromkeys(atlases)
    est_path_iterlist_dwi = list(
        set(
            [
                i
                for i in raw_est_path_iterlist
                if i.split("model-")[1].split("_")[0] in struct_models
            ]
        )
    )
    est_path_iterlist_func = list(
        set(
            [
                i
                for i in raw_est_path_iterlist
                if i.split("model-")[1].split("_")[0] in func_models
            ]
        )
    )

    if "_rsn" in ";".join(est_path_iterlist_func):
        func_subnets = list(
            set([i.split("_rsn-")[1].split("_")[0] for i in
                 est_path_iterlist_func])
        )
    else:
        func_subnets = []
    if "_rsn" in ";".join(est_path_iterlist_dwi):
        dwi_subnets = list(
            set([i.split("_rsn-")[1].split("_")[0] for i in
                 est_path_iterlist_dwi])
        )
    else:
        dwi_subnets = []

    dir_path = str(
        Path(
            os.path.dirname(
                est_path_iterlist_dwi[0])).parent.parent.parent)
    namer_dir = f"{dir_path}/graphs_multilayer"
    if not os.path.isdir(namer_dir):
        os.mkdir(namer_dir)

    name_list = []
    metadata_list = []
    multigraph_list_all = []
    graph_path_list_all = []
    for atlas in atlases:
        if len(func_subnets) >= 1:
            parcel_dict_func[atlas] = {}
            for sub_net in func_subnets:
                parcel_dict_func[atlas][sub_net] = []
        else:
            parcel_dict_func[atlas] = []

        if len(dwi_subnets) >= 1:
            parcel_dict_dwi[atlas] = {}
            for sub_net in dwi_subnets:
                parcel_dict_dwi[atlas][sub_net] = []
        else:
            parcel_dict_dwi[atlas] = []

        for graph_path in est_path_iterlist_dwi:
            if atlas in graph_path:
                if len(dwi_subnets) >= 1:
                    for sub_net in dwi_subnets:
                        if sub_net in graph_path:
                            parcel_dict_dwi[atlas][sub_net].append(graph_path)
                else:
                    parcel_dict_dwi[atlas].append(graph_path)

        for graph_path in est_path_iterlist_func:
            if atlas in graph_path:
                if len(func_subnets) >= 1:
                    for sub_net in func_subnets:
                        if sub_net in graph_path:
                            parcel_dict_func[atlas][sub_net].append(graph_path)
                else:
                    parcel_dict_func[atlas].append(graph_path)

        parcel_dict = {}
        # Create dictionary of all possible pairs of structural-functional
        # graphs for each unique resolution of vertices
        if len(dwi_subnets) >= 1 and len(func_subnets) >= 1:
            parcel_dict[atlas] = {}
            rsns = np.intersect1d(dwi_subnets, func_subnets).tolist()
            for rsn in rsns:
                parcel_dict[atlas][rsn] = list(set(itertools.product(
                    parcel_dict_dwi[atlas][rsn],
                    parcel_dict_func[atlas][rsn])))
                for paths in list(parcel_dict[atlas][rsn]):
                    [
                        name_list,
                        metadata_list,
                        multigraph_list_all,
                        graph_path_list_all,
                    ] = motif_matching(
                        paths,
                        ID,
                        atlas,
                        namer_dir,
                        name_list,
                        metadata_list,
                        multigraph_list_all,
                        graph_path_list_all,
                        rsn=rsn,
                    )
        else:
            parcel_dict[atlas] = list(set(itertools.product(
                parcel_dict_dwi[atlas], parcel_dict_func[atlas])))
            for paths in list(parcel_dict[atlas]):
                [
                    name_list,
                    metadata_list,
                    multigraph_list_all,
                    graph_path_list_all,
                ] = motif_matching(
                    paths,
                    ID,
                    atlas,
                    namer_dir,
                    name_list,
                    metadata_list,
                    multigraph_list_all,
                    graph_path_list_all,
                )

    graph_path_list_top = [list(i[0].values()) for i in graph_path_list_all]
    assert len(multigraph_list_all) == len(name_list) == len(metadata_list)

    return (
        multigraph_list_all,
        graph_path_list_top,
        len(name_list) * [namer_dir],
        name_list,
        metadata_list,
    )

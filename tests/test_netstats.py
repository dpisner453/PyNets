#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 16:19:14 2017
@authors: Derek Pisner & Ryan Hammonds
"""
import pytest
import numpy as np
import networkx as nx
import time
from pathlib import Path
from pynets.stats import netstats
import logging

logger = logging.getLogger(__name__)
logger.setLevel(50)


@pytest.mark.parametrize("value", [True, 2, 3.14, "word", {}])
def test_get_prop_type(value):
    """
    Test for get_prop_type() functionality
    """
    start_time = time.time()
    tname, value, key = netstats.get_prop_type(value)
    print("%s%s%s" % ('test_get_prop_type --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    if value == 2:
        value = int(value)

    if type(value) == bool:
        assert tname is 'bool'

    elif type(value) == float or type(value) == int:
        assert tname is 'float'

    elif type(value) == dict:
        assert tname is 'object'

    elif type(value) == bytes:
        assert tname is 'string'


def test_nx2gt():
    """
    Test for nx2gt() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    nxG = nx.from_numpy_array(in_mat)

    start_time = time.time()
    gtG = netstats.nx2gt(nxG)
    print("%s%s%s" % ('test_nx2gt --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    try:
        import graph_tool.all as gt
        assert type(gtG) is gt.graph_tool.Graph
    except ImportError as e:
        print(e, "graph_tool not installed!")
        assert gtG is not None


def test_np2gt():
    """
    Test for np2gt() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")

    start_time = time.time()
    Gt = netstats.np2gt(in_mat)
    print("%s%s%s" % ('test_np2gt --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    try:
        import graph_tool.all as gt
        assert type(Gt) is gt.graph_tool.Graph
    except ImportError as e:
        print(e, "graph_tool not installed!")
        assert Gt is not None


def test_average_shortest_path_length_for_all():
    """
    Test for average_shortest_path_length_for_all functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    G = nx.from_numpy_array(in_mat)

    start_time = time.time()
    avgest_path_len = netstats.average_shortest_path_length_for_all(G)
    print("%s%s%s" % ('test_average_shortest_path_length_for_all --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    assert avgest_path_len > 0
    assert type(avgest_path_len) == float


def test_average_local_efficiency():
    """
    Test for average_local_efficiency functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    G = nx.from_numpy_array(in_mat)

    start_time = time.time()
    average_local_efficiency = netstats.average_local_efficiency(G, engine='nx')
    print("%s%s%s" % ('test_average_local_efficiency --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    assert average_local_efficiency > 0
    assert average_local_efficiency.dtype == float


# used random node_comm_aff_mat
def test_create_communities():
    """
    Test for create_communities functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    node_comm_aff_mat = np.random.rand(5,5)
    node_num = 3

    start_time = time.time()
    com_assign = netstats.create_communities(node_comm_aff_mat, node_num)
    print("%s%s%s" % ('test_create_communities --> finished: ',
                      np.round(time.time() - start_time, 1), 's'))
    assert len(com_assign) > 0


@pytest.mark.parametrize("degree", ['undirected', 'in', 'out'])
def test_participation_coef(degree):
    """
    Test for participation_coef functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    ci = np.ones(in_mat.shape[0])
    ci_dim = int(np.shape(ci)[0])
    W = np.random.rand(ci_dim, ci_dim)

    start_time = time.time()
    P = netstats.participation_coef(W, ci, degree=degree)
    print("%s%s%s" % ('test_participation_coef --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))
    assert P.size > 0


def test_modularity():
    """
    Test for modularity functionality
    """
    import community
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    G = nx.from_numpy_matrix(in_mat)

    start_time = time.time()
    ci_dict = community.best_partition(G)
    mod = community.community_louvain.modularity(ci_dict, G)
    print("%s%s%s" % ('test_modularity --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))
    assert type(ci_dict) == dict
    assert type(mod) == float


def test_diversity_coef_sign():
    """
    Test for diversity_coef_sign functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    ci = np.ones(in_mat.shape[0])
    ci_dim = int(np.shape(ci)[0])
    W = np.random.rand(ci_dim, ci_dim)

    start_time = time.time()
    [Hpos, Hneg] = netstats.diversity_coef_sign(W, ci)
    print("%s%s%s" % ('test_diversity_coef_sign() --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert Hpos.size > 0
    assert Hneg.size > 0


@pytest.mark.parametrize("clustering",
    [
        'single',
        pytest.param('complete', marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(None, marks=pytest.mark.xfail(raises=ValueError))
    ]
)
def test_link_communities(clustering):
    """
    Test for link_communities functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy")

    start_time = time.time()
    M = netstats.link_communities(in_mat, type_clustering=clustering)
    print("%s%s%s" % ('test_link_communities --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert type(M) is np.ndarray
    assert np.sum(M) == 24


@pytest.mark.parametrize("connected_case", [True, False])
@pytest.mark.parametrize("fallback_lcc", [True, False])
def test_prune_disconnected(connected_case, fallback_lcc):
    """
    Test pruning functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    if connected_case is True:
        in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
        G = nx.from_numpy_array(in_mat)
    elif connected_case is False:
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_node(3)

    start_time = time.time()
    [G_out, pruned_nodes] = netstats.prune_disconnected(G, fallback_lcc = fallback_lcc)
    print("%s%s%s" % ('test_prune_disconnected --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert type(G_out) is nx.Graph
    assert type(pruned_nodes) is list
    if connected_case is True:
        assert len(pruned_nodes) == 0
    elif connected_case is False:
        assert len(pruned_nodes) > 0
        assert len(list(G_out.nodes())) < len(list(G.nodes()))


@pytest.mark.parametrize("method", ["betweenness", "richclub", "coreness", "eigenvector"])
def test_most_important(method):
    """
    Test pruning for most important nodes functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodetype-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")
    G = nx.from_numpy_array(in_mat)

    start_time = time.time()
    Gt, pruned_nodes = netstats.most_important(G, method=method)
    print("%s%s%s" % ('test_most_important --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert Gt is not None
    assert pruned_nodes is not None


@pytest.mark.parametrize("binary", [True, False])
@pytest.mark.parametrize("prune", [0, 1, 2, 3])
@pytest.mark.parametrize("norm", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("conn_model", ['corr', 'cov', 'sps', 'partcorr'])
def test_extractnetstats(binary, prune, norm, conn_model):
    """
    Test extractnetstats functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    ID = '002'
    network = 'Default'
    thr = 0.95
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"
    roi = None

    start_time = time.time()
    out_path = netstats.extractnetstats(ID=ID, network=network, thr=thr, conn_model=conn_model, est_path=est_path, roi=roi, prune=prune,
                                        norm=norm, binary=binary)
    print("%s%s%s" % ('test_extractnetstats --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert out_path is not None

    # Cover exceptions. This can definiely be improved. It increases coverage, but not as throughly
    # as I hoped.
    from tempfile import NamedTemporaryFile
    f_temp = NamedTemporaryFile(mode='w+', suffix='.npy')

    nan_array = np.empty((5, 5))
    nan_array[:] = np.nan

    np.save(f_temp.name, nan_array)
    est_path = f_temp.name

    try:
        out_path = netstats.extractnetstats(ID, network, thr, conn_model, est_path, roi, prune,
                                            norm, binary)
    except PermissionError:
        pass


def test_raw_mets():
    """
    Test raw_mets extraction functionality
    """
    from pynets.stats.netstats import global_efficiency, average_local_efficiency
    from networkx.algorithms import degree_assortativity_coefficient, average_clustering, average_shortest_path_length, degree_pearson_correlation_coefficient, graph_number_of_cliques, transitivity, sigma
    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"
    in_mat = np.load(est_path)
    G = nx.from_numpy_array(in_mat)
    [G, _] = netstats.prune_disconnected(G)
    metric_list_glob = [global_efficiency, average_local_efficiency,
                        degree_assortativity_coefficient,
                        average_clustering, average_shortest_path_length,
                        degree_pearson_correlation_coefficient,
                        graph_number_of_cliques, transitivity]
    for i in metric_list_glob:
        net_met_val = netstats.raw_mets(G, i, engine='nx')
        assert net_met_val is not np.nan
        assert type(net_met_val) == float


def test_subgraph_number_of_cliques_for_all():
    """
    Test cliques computation
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodety"
                     f"pe-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")

    start_time = time.time()
    G = nx.from_numpy_array(in_mat)
    print("%s%s%s" % ('test_subgraph_number_of_cliques_for_all --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))


    cliques = netstats.subgraph_number_of_cliques_for_all(G)

    assert cliques > 0


@pytest.mark.parametrize("approach",
    [
    'clustering',
    'transitivity',
    pytest.param('impossible', marks=pytest.mark.xfail(raises=ValueError))
    ]
)
@pytest.mark.parametrize("reference",
    [
    'random',
    'lattice',
    #'fast',
    pytest.param('impossible', marks=pytest.mark.xfail(raises=ValueError))
    ]
)
def test_smallworldness(approach, reference):
    """
    Test small-world coefficient (omega) computation
    """
    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"

    in_mat = np.load(est_path)
    G = nx.from_numpy_array(in_mat)

    start_time = time.time()
    sigma = netstats.smallworldness(G, niter=5, nrand=5,
                                    approach=approach,
                                    reference=reference, engine='nx')
    print("%s%s%s" % ('test_smallworldness --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    # A network is smallworld if sigma > 1
    assert sigma < 1


def test_participation_coef_sign():
    """
    Test participation coefficient computation
    """
    base_dir = str(Path(__file__).parent/"examples")
    in_mat = np.load(f"{base_dir}/miscellaneous/graphs/002_modality-func_rsn-Default_model-cov_nodety"
                     f"pe-spheres-2mm_smooth-2fwhm_hpass-0.1Hz_thrtype-PROP_thr-0.95.npy")

    start_time = time.time()
    ci = np.ones(in_mat.shape[0])
    ci_dim = int(np.shape(ci)[0])
    W = np.random.rand(ci_dim, ci_dim)

    Ppos, Pneg = netstats.participation_coef_sign(W, ci)
    print("%s%s%s" % ('test_participation_coef_sign --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert len(Ppos) == ci_dim and len(Pneg) == ci_dim


@pytest.mark.parametrize("binarize", [True, False])
def test_weighted_transitivity(binarize):
    """ Test weighted_transitivity computation
    """
    from pynets.core.thresholding import binarize

    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"

    in_mat = np.load(est_path)
    if binarize:
        in_mat = binarize(in_mat)

    start_time = time.time()
    G = nx.from_numpy_array(in_mat)

    transitivity = netstats.weighted_transitivity(G)
    print("%s%s%s" % ('test_weighted_transitivity --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert transitivity <= 3 and transitivity >= 0


@pytest.mark.parametrize("fmt", ['npy', 'txt'])
@pytest.mark.parametrize("conn_model",
                         ['corr', 'partcorr', 'cov', 'sps'])
@pytest.mark.parametrize("prune",
                         [pytest.param(0,
                                       marks=pytest.mark.xfail(raises=UnboundLocalError)), 1, 2, 3])
@pytest.mark.parametrize("norm", [i for i in range(1, 7)])
def test_clean_graphs(fmt, conn_model, prune, norm):
    #test_CleanGraphs
    """
    Test all combination of parameters for the CleanGraphs class
    """
    base_dir = str(Path(__file__).parent/"examples")

    if fmt == 'npy':
        est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"
        in_mat = np.load(est_path)
    else:
        est_path = f"{base_dir}/miscellaneous/002_rsn-Default_nodetype-parc_model-sps_thrtype-PROP_thr-0.94.txt"
        in_mat = np.genfromtxt(est_path)

    start_time = time.time()
    clean = netstats.CleanGraphs(0.5, conn_model, est_path, prune, norm)
    clean.normalize_graph()
    clean.print_summary()
    clean.create_length_matrix()
    clean.binarize_graph()

    clean.prune_graph()

    G = nx.from_numpy_array(in_mat)
    print("%s%s%s" % ('test_clean_graphs --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert len(clean.G) >= 0
    assert len(clean.G) <= len(G)


def test_save_netmets():
    """
    Test save netmets functionality using dummy metrics
    """
    import tempfile
    dir_path = str(tempfile.TemporaryDirectory().name)

    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"
    metric_list_names = ['metric_a', 'metric_b', 'metric_c']
    net_met_val_list_final = [1, 2, 3]

    start_time = time.time()
    out_path_neat = netstats.save_netmets(dir_path, est_path, metric_list_names, net_met_val_list_final)
    print("%s%s%s" % ('test_save_netmets --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert isinstance(out_path_neat, str)


@pytest.mark.parametrize("true_metric", [True, False])
def test_iterate_nx_global_measures(true_metric):
    """ Test iterating over net metric list
    """
    from networkx.algorithms import average_shortest_path_length

    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"

    in_mat = np.load(est_path)
    G = nx.from_numpy_array(in_mat)

    if true_metric:
        metric_list_glob = [average_shortest_path_length]
    else:
        metric_list_glob = ['<function fake_func at 0x7f8b7129b700>']

    start_time = time.time()
    net_met_val_list, metric_list_names = netstats.iterate_nx_global_measures(G, metric_list_glob)
    print("%s%s%s" % ('test_iterate_nx_global_measures --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert isinstance(net_met_val_list[0], float)
    assert isinstance(metric_list_names[0], str)

@pytest.mark.parametrize("sim_num_comms", [1, 5, 10])
@pytest.mark.parametrize("sim_size", [1, 5, 10])
def test_community_resolution_selection(sim_num_comms, sim_size):
    """ Test community resolution selection
    Note: It is impossible to enter or cover the second while loop in
          netstats.community_resolution_selection.
    """
    G = nx.caveman_graph(sim_num_comms, sim_size)

    start_time = time.time()
    node_ci, ci, resolution, num_comms = netstats.community_resolution_selection(G)
    print("%s%s%s" % ('test_community_resolution_selection --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert len(node_ci) == len(ci)
    assert num_comms == sim_num_comms
    assert resolution is not None


@pytest.mark.parametrize("metric", ['participation', 'diversity', 'local_efficiency',
                                    'comm_centrality', 'rich_club_coeff'])
def test_get_metrics(metric):
    """
    Test various wrappers for getting nx graph metrics
    """
    base_dir = str(Path(__file__).parent/"examples")
    est_path = f"{base_dir}/miscellaneous/sub-0021001_rsn-Default_nodetype-parc_model-sps_template-MNI152_T1_thrtype-DENS_thr-0.19.npy"

    in_mat = np.load(est_path)
    G = nx.from_numpy_array(in_mat)
    ci = np.ones(in_mat.shape[0])
    metric_list_names = []
    net_met_val_list_final = []


    if metric == 'participation':
        metric_list_names, net_met_val_list_final = \
            netstats.get_participation(in_mat, ci, metric_list_names, net_met_val_list_final)
        assert len(metric_list_names) == len(netstats.participation_coef(in_mat, ci))+1
        assert len(net_met_val_list_final) == len(netstats.participation_coef(in_mat, ci))+1
    elif metric == 'diversity':
        metric_list_names, net_met_val_list_final = \
            netstats.get_diversity(in_mat, ci, metric_list_names, net_met_val_list_final)
        assert len(metric_list_names) == np.shape(netstats.diversity_coef_sign(in_mat, ci))[1]+1
        assert len(net_met_val_list_final) == np.shape(netstats.diversity_coef_sign(in_mat, ci))[1]+1
    elif metric == 'local_efficiency':
        metric_list_names, net_met_val_list_final = \
            netstats.get_local_efficiency(G, metric_list_names, net_met_val_list_final)
        assert len(metric_list_names) == len(netstats.local_efficiency(G))+1
        assert len(net_met_val_list_final) == len(netstats.local_efficiency(G))+1
    elif metric == 'comm_centrality':
        metric_list_names, net_met_val_list_final = \
            netstats.get_comm_centrality(G, metric_list_names, net_met_val_list_final)
        assert len(metric_list_names) == len(nx.algorithms.communicability_betweenness_centrality(G))+1
        assert len(net_met_val_list_final) == len(nx.algorithms.communicability_betweenness_centrality(G))+1
    elif metric == 'rich_club_coeff':
        metric_list_names, net_met_val_list_final = \
            netstats.get_rich_club_coeff(G, metric_list_names, net_met_val_list_final)
        assert len(metric_list_names) == len(nx.algorithms.rich_club_coefficient(G))+1
        assert len(net_met_val_list_final) == len(nx.algorithms.rich_club_coefficient(G))+1


@pytest.mark.parametrize("plot_switch", [True, False])
@pytest.mark.parametrize("sql_out", [True, False])
@pytest.mark.parametrize("embed", [True, False])
@pytest.mark.parametrize("create_summary", [True, False])
@pytest.mark.parametrize("graph_num", [pytest.param(-1, marks=pytest.mark.xfail(raises=UserWarning)),
                                       pytest.param(0, marks=pytest.mark.xfail(raises=IndexError)),
                                       1,
                                       2])
def test_collect_pandas_df_make(plot_switch, sql_out, embed, create_summary, graph_num):
    """
    Test for collect_pandas_df_make() functionality
    """
    base_dir = str(Path(__file__).parent/"examples")
    network = None
    ID = '002'

    if graph_num == -1:
        net_mets_csv_list = [f"{base_dir}/miscellaneous/002_parcels_Default.nii.gz"]
    elif graph_num == 0:
        net_mets_csv_list = []
    elif graph_num == 1:
        net_mets_csv_list = [f"{base_dir}/topology/metrics_sub-0021001_modality-dwi_nodetype-parc_model-csa_thrtype-PROP_thr-0.2.csv"]
    else:
        net_mets_csv_list = [f"{base_dir}/topology/metrics_sub-0021001_modality-dwi_nodetype-parc_model-csa_thrtype-PROP_thr-0.2.csv",
                             f"{base_dir}/topology/metrics_sub-0021001_modality-dwi_nodetype-parc_model-csa_thrtype-PROP_thr-0.3.csv"]

    start_time = time.time()
    combination_complete = netstats.collect_pandas_df_make(net_mets_csv_list, ID, network, plot_switch=plot_switch,
                                                           embed=embed, create_summary=create_summary,
                                                           sql_out=sql_out)
    print("%s%s%s" % ('test_collect_pandas_df_make --> finished: ',
                      str(np.round(time.time() - start_time, 1)), 's'))

    assert combination_complete is True

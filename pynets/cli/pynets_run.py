#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:40:07 2017
Copyright (C) 2016
@author: Derek Pisner (dPys)
"""
import warnings

warnings.filterwarnings("ignore")


def get_parser():
    """Parse command-line inputs"""
    import argparse
    from pathlib import Path
    from pynets.__about__ import __version__

    verstr = f"PyNets v{__version__}"

    # Parse args
    parser = argparse.ArgumentParser(
        description="PyNets: A Reproducible Workflow for Structural and "
                    "Functional Connectome Ensemble Learning")
    parser.add_argument(
        "output_dir",
        default=str(Path.home()),
        help="The directory to store pynets derivatives.",
    )
    parser.add_argument(
        "-id",
        metavar="A subject id or other unique identifier",
        default=None,
        nargs="+",
        required=True,
        help="An subject identifier OR list of subject identifiers, separated "
             "by space and of equivalent length to the list of input files "
             "indicated with the -func flag. This parameter must be an "
             "alphanumeric string and can be arbitrarily chosen. If "
             "functional and dmri connectomes are being generated "
             "simultaneously, then space-separated id's need to be repeated "
             "to match the total input file count.\n",
    )
    # Primary file inputs
    parser.add_argument(
        "-func",
        metavar="Path to input functional file (required for functional "
                "connectomes)",
        default=None,
        nargs="+",
        help="Specify either a path to a preprocessed functional Nifti1Image "
             "in MNI152 space OR multiple space-separated paths to multiple "
             "preprocessed functional Nifti1Image files in MNI152 space and in"
             " .nii or .nii.gz format, OR the path to a text file containing "
             "a list of paths to subject files.\n",
    )
    parser.add_argument(
        "-dwi",
        metavar="Path to diffusion-weighted imaging data file (required for "
                "dmri connectomes)",
        default=None,
        nargs="+",
        help="Specify either a path to a preprocessed dmri diffusion "
             "Nifti1Image in native diffusion space and in .nii or "
             ".nii.gz format OR multiple space-separated paths to multiple "
        "preprocessed dmri diffusion Nifti1Image files in native "
             "diffusion space and in .nii or .nii.gz format.\n",
    )
    parser.add_argument(
        "-bval",
        metavar="Path to b-values file (required for dmri connectomes)",
        default=None,
        nargs="+",
        help="Specify either a path to a b-values text file containing "
             "gradient shell values per diffusion direction OR multiple "
             "space-separated paths to multiple b-values text files in "
        "the order of accompanying b-vectors and dwi files.\n",
    )
    parser.add_argument(
        "-bvec",
        metavar="Path to b-vectors file (required for dmri connectomes)",
        default=None,
        nargs="+",
        help="Specify either a path to a b-vectors text file containing "
             "gradient directions (x,y,z) per diffusion direction OR "
             "multiple space-separated paths to multiple b-vectors text files "
             "in the order of accompanying b-values and dwi files.\n",
    )

    # Secondary file inputs
    parser.add_argument(
        "-anat",
        metavar="Path to a skull-stripped anatomical Nifti1Image",
        default=None,
        nargs="+",
        help="Required for dmri and/or functional connectomes. Multiple "
             "paths to multiple anatomical files should be specified by space "
             "in the order of accompanying functional and/or dmri files. "
             "If functional and dmri connectomes are both being generated "
        "simultaneously, then anatomical Nifti1Image file paths "
             "need to be repeated, but separated by comma.\n",
    )
    parser.add_argument(
        "-m",
        metavar="Path to a T1w brain mask image (if available) in native "
                "anatomical space",
        default=None,
        nargs="+",
        help="File path to a T1w brain mask Nifti image (if available) in "
             "native anatomical space OR multiple file paths to multiple T1w "
             "brain mask Nifti images in the case of running multiple "
             "participants, in which case paths should be separated by "
             "a space. If no brain mask is supplied, the template mask will "
             "be used (see runconfig.yaml).\n",
    )
    parser.add_argument(
        "-conf",
        metavar="Confound regressor file (.tsv/.csv format)",
        default=None,
        nargs="+",
        help="Optionally specify a path to a confound regressor file to "
             "reduce noise in the time-series estimation for the graph. "
             "This can also be a list of paths in the case of running multiple"
             "subjects, which requires separation by space and of equivalent"
             " length to the list of input files indicated with "
             "the -func flag.\n",
    )
    parser.add_argument(
        "-g",
        metavar="Path to graph file input.",
        default=None,
        nargs="+",
        help="In either .txt, .npy, .graphml, .csv, .ssv, .tsv, "
             "or .gpickle format. This skips fMRI and dMRI graph estimation "
             "workflows and begins at the thresholding and graph analysis "
             "stage. Multiple graph files corresponding to multiple subject "
             "ID's should be separated by space, and multiple graph files "
             "corresponding to the same subject ID should be separated by "
             "comma. If the `-g` flag is used, then the `-id` flag must also "
             "be used. Consider also including `-thr` flag to activate "
             "thresholding only or the `-p` and `-norm` flags if graph "
             "defragementation or normalization is desired. The `-mod` flag "
             "can be used for additional provenance/file-naming.\n",
    )
    parser.add_argument(
        "-roi",
        metavar="Path to binarized Region-of-Interest (ROI) Nifti1Image in "
                "template MNI space.",
        default=None,
        nargs="+",
        help="Optionally specify a binarized ROI mask and retain only those "
             "nodes of a parcellation contained within that mask for "
             "connectome estimation.\n",
    )
    parser.add_argument(
        "-ref",
        metavar="Atlas reference file path",
        default=None,
        help="Specify the path to the atlas reference .txt file that maps "
             "labels to intensities corresponding to the atlas parcellation "
             "file specified with the -a flag.\n",
    )
    parser.add_argument(
        "-way",
        metavar="Path to binarized Nifti1Image to constrain tractography",
        default=None,
        nargs="+",
        help="Optionally specify a binarized ROI mask in MNI-space to"
             "constrain tractography in the case of dmri connectome "
             "estimation.\n",
    )
    # Modality-pervasive metaparameters
    parser.add_argument(
        "-mod",
        metavar="Connectivity estimation/reconstruction method",
        default="?",
        nargs="+",
        choices=[
            "corr",
            "sps",
            "cov",
            "partcorr",
            "QuicGraphicalLasso",
            "QuicGraphicalLassoCV",
            "QuicGraphicalLassoEBIC",
            "AdaptiveQuicGraphicalLasso",
            "csa",
            "csd",
            "sfm",
        ],
        help="(metaparameter): Specify connectivity estimation model. "
             "For fMRI, possible models include: corr for correlation, "
             "cov for covariance, sps for precision covariance, partcorr for "
             "partial correlation. If skgmm is "
             "installed (https://github.com/skggm/skggm), then "
             "QuicGraphicalLasso, QuicGraphicalLassoCV, "
             "QuicGraphicalLassoEBIC, and AdaptiveQuicGraphicalLasso. For "
             "dMRI, current models include csa, csd, and sfm.\n",
    )
    parser.add_argument(
        "-a",
        metavar="Atlas",
        default=None,
        nargs="+",
        help="(metaparameter): Specify an atlas name from nilearn or "
             "local (pynets) library, and/or specify a path to a custom "
             "parcellation/atlas Nifti1Image file in MNI space. Labels should"
             "be spatially distinct across hemispheres and ordered with "
             "consecutive integers with a value of 0 as the background label."
             "If specifying a list of paths to multiple parcellations, "
             "separate them by space. If you wish to iterate your pynets run "
             "over multiple atlases, separate them by space. "
             "Available nilearn atlases are:"
        "\n\natlas_aal\natlas_talairach_gyrus\natlas_talairach_ba"
             "\natlas_talairach_lobe\n"
        "atlas_harvard_oxford\natlas_destrieux_2009\natlas_msdl"
             "\ncoords_dosenbach_2010\n"
        "coords_power_2011\natlas_pauli_2017.\n\nAvailable local atlases are:"
        "\n\ndestrieux2009_rois\nBrainnetomeAtlasFan2016"
             "\nVoxelwiseParcellationt0515kLeadDBS\n"
        "Juelichgmthr252mmEickhoff2005\n"
        "CorticalAreaParcellationfromRestingStateCorrelationsGordon2014\n"
        "whole_brain_cluster_labels_PCA100\nAICHAreorderedJoliot2015\n"
        "HarvardOxfordThr252mmWholeBrainMakris2006"
             "\nVoxelwiseParcellationt058kLeadDBS\n"
        "MICCAI2012MultiAtlasLabelingWorkshopandChallengeNeuromorphometrics\n"
        "Hammers_mithAtlasn30r83Hammers2003Gousias2008"
             "\nAALTzourioMazoyer2002\nDesikanKlein2012\n"
        "AAL2zourioMazoyer2002\nVoxelwiseParcellationt0435kLeadDBS"
             "\nAICHAJoliot2015\n"
        "whole_brain_cluster_labels_PCA200"
             "\nRandomParcellationsc05meanalll43Craddock2011",
    )
    parser.add_argument(
        "-ns",
        metavar="Spherical centroid node size",
        default=4,
        nargs="+",
        help="(metaparameter): Optionally specify coordinate-based node "
             "radius size(s). Default is 4 "
        "mm for fMRI and 8mm for dMRI. If you wish to iterate the pipeline "
             "across multiple node sizes, separate the list "
             "by space (e.g. 2 4 6).\n",
    )
    parser.add_argument(
        "-thr",
        metavar="Graph threshold",
        default=1.00,
        help="Optionally specify a threshold indicating a proportion of "
             "weights to preserve in the graph. Default is no thresholding. "
             "If `-mst`, `-dt`, or `-df` flags are not included, than "
             "proportional thresholding will be performed\n",
    )
    parser.add_argument(
        "-min_thr",
        metavar="Multi-thresholding minimum threshold",
        default=None,
        help="(metaparameter): Minimum threshold for multi-thresholding.\n",
    )
    parser.add_argument(
        "-max_thr",
        metavar="Multi-thresholding maximum threshold",
        default=None,
        help="(metaparameter): Maximum threshold for multi-thresholding.",
    )
    parser.add_argument(
        "-step_thr",
        metavar="Multi-thresholding step size",
        default=None,
        help="(metaparameter): Threshold step value for multi-thresholding. "
             "Default is 0.01.\n",
    )

    # fMRI metaparameters
    parser.add_argument(
        "-sm",
        metavar="Smoothing value (mm fwhm)",
        default=0,
        nargs="+",
        help="(metaparameter): Optionally specify smoothing width(s). "
             "Default is 0 / no smoothing. If you wish to iterate the pipeline"
             " across multiple smoothing separate the list "
             "by space (e.g. 2 4 6). Safe range: [0-8]\n",
    )
    parser.add_argument(
        "-hp",
        metavar="High-pass filter (Hz)",
        default=None,
        nargs="+",
        help="(metaparameter): Optionally specify high-pass filter values "
             "to apply to node-extracted time-series for fMRI. "
             "Default is None. If you wish to iterate the pipeline across "
             "multiple values, separate the list by space (e.g. 0 0.02 0.1). "
             "Safe range: [0-0.15] for resting-state data.\n",
    )
    parser.add_argument(
        "-es",
        metavar="Node extraction strategy",
        default="mean",
        nargs="+",
        choices=[
            "sum",
            "mean",
            "median",
            "mininum",
            "maximum",
            "variance",
            "standard_deviation",
        ],
        help="Include this flag if you are running functional connectometry "
             "using parcel labels and wish to specify the name of a specific "
             "function (i.e. other than the mean) to reduce the region's "
             "time-series. Options are: `sum`, `mean`, `median`, `mininum`, "
             "`maximum`, `variance`, `standard_deviation`.\n",
    )
    parser.add_argument(
        "-k",
        metavar="Number of k clusters",
        default=None,
        nargs="+",
        help="(metaparameter): Specify a number of clusters to produce. "
             "If you wish to iterate the pipeline across multiple values of k,"
             " separate the list by space (e.g. 200, 400, 600, 800).\n",
    )
    parser.add_argument(
        "-ct",
        metavar="Clustering type",
        default="ward",
        nargs="+",
        choices=["ward", "rena", "kmeans", "complete", "average", "single",
                 "ncut"],
        help="(metaparameter): Specify the types of clustering to use. "
             "Recommended options are: ward, rena, kmeans, or ncut. Note that "
             "imposing spatial constraints with a mask consisting of "
             "disconnected components will leading to clustering instability "
             "in the case of complete, average, or single clustering. If "
             "specifying list of clustering types, separate them by space.\n",
    )
    parser.add_argument(
        "-cm",
        metavar="Cluster mask",
        default=None,
        nargs="+",
        help="(metaparameter): Specify the path to a Nifti1Image mask file"
             " to constrained functional clustering. If specifying a list of "
             "paths to multiple cluster masks, separate them by space.\n",
    )

    # dMRI metaparameters
    parser.add_argument(
        "-ml",
        metavar="Minimum fiber length for tracking",
        default=10,
        nargs="+",
        help="(metaparameter): Include this flag to manually specify a "
             "minimum tract length (mm) for dmri connectome tracking. Default "
             "is 10. If you wish to iterate the pipeline across multiple "
             "minimums, separate the list by space (e.g. 10 30 50). "
             "Safe range: [0-150]. Depending on the tissue classifier used"
             " and the restrictiveness of the parcellation or any way-masking,"
             " values >60mm may fail.\n",
    )
    parser.add_argument(
        "-tol",
        metavar="Error margin",
        default=5,
        nargs="+",
        help="(metaparameter): Distance (in the units of the streamlines, "
             "usually mm). If any coordinate in the streamline is within this "
             "distance from the center of any voxel in the ROI, the filtering "
             "criterion is set to True for this streamline, otherwise False. "
             "Defaults to the distance between the center of each voxel and "
             "the corner of the voxel. Default is 5. Safe range: [0-15].\n",
    )
    parser.add_argument(
        "-dg",
        metavar="Direction getter",
        default="det",
        nargs="+",
        choices=["det", "prob", "clos"],
        help="(metaparameter): Include this flag to manually specify the "
             "statistical approach to tracking for dmri connectome estimation."
             " Options are: det (deterministic), closest (clos), and "
             "prob (probabilistic). Default is det. If you wish to iterate the"
             " pipeline across multiple direction-getting methods, separate "
             "the list by space (e.g. 'det', 'prob', 'clos').\n",
    )
    # General settings
    parser.add_argument(
        "-norm",
        metavar="Normalization strategy for resulting graph(s)",
        default=1,
        nargs=1,
        choices=["0", "1", "2", "3", "4", "5", "6"],
        help="Include this flag to normalize the resulting graph by (1) "
             "maximum edge weight; (2) using log10; (3) using pass-to-ranks "
             "for all non-zero edges; (4) using pass-to-ranks for all non-zero"
             " edges relative to the number of nodes; (5) using pass-to-ranks"
             " with zero-edge boost; and (6) which standardizes the matrix to "
             "values [0, 1]. Default is (6).\n",
    )
    parser.add_argument(
        "-bin",
        default=False,
        action="store_true",
        help="Include this flag to binarize the resulting graph such that "
             "edges are boolean and not weighted.\n",
    )
    parser.add_argument(
        "-dt",
        default=False,
        action="store_true",
        help="Optionally use this flag if you wish to threshold to achieve a "
             "given density or densities indicated by the -thr and -min_thr,"
             " -max_thr, -step_thr flags, respectively.\n",
    )
    parser.add_argument(
        "-mst",
        default=False,
        action="store_true",
        help="Optionally use this flag if you wish to apply local thresholding"
             " via the Minimum Spanning Tree approach. -thr values in this "
             "case correspond to a target density (if the -dt flag is also"
             " included), otherwise a target proportional threshold.\n",
    )
    parser.add_argument(
        "-p",
        metavar="Pruning Strategy",
        default=3,
        nargs=1,
        choices=["0", "1", "2", "3"],
        help="Include this flag to (1) prune the graph of any "
             "isolated + fully disconnected nodes (i.e. anti-fragmentation),"
             " (2) prune the graph of all but hubs as defined by any of a "
             "variety of definitions (see ruconfig.yaml), or (3) retain only "
             "the largest connected component subgraph. Default is no pruning."
             " Include `-p 1` to enable fragmentation-protection.\n",
    )
    parser.add_argument(
        "-df",
        default=False,
        action="store_true",
        help="Optionally use this flag if you wish to apply local thresholding"
             " via the disparity filter approach. -thr values in this case "
             "correspond to α.\n",
    )
    parser.add_argument(
        "-mplx",
        metavar="Perform various levels of multiplex graph analysis (only) if"
                " both structural and diffusion connectometry is run "
                "simultaneously.",
        default=0,
        nargs=1,
        choices=["0", "1", "2"],
        help="Include this flag to perform multiplex graph analysis across "
             "structural-functional connectome modalities. Options include "
             "level (1) Create multiplex graphs using motif-matched adaptive "
             "thresholding; (2) Additionally perform multiplex graph embedding"
             " and analysis. Default is (0) which is no multiplex analysis.\n",
    )
    parser.add_argument(
        "-embed",
        default=False,
        action="store_true",
        help="Optionally use this flag if you wish to embed the ensemble(s) "
             "produced into feature vector(s).\n",
    )
    parser.add_argument(
        "-spheres",
        default=False,
        action="store_true",
        help="Include this flag to use spheres instead of parcels as nodes.\n",
    )
    parser.add_argument(
        "-n",
        metavar="Resting-state network",
        default=None,
        nargs="+",
        choices=[
            "Vis",
            "SomMot",
            "DorsAttn",
            "SalVentAttn",
            "Limbic",
            "Cont",
            "Default",
            "VisCent",
            "VisPeri",
            "SomMotA",
            "SomMotB",
            "DorsAttnA",
            "DorsAttnB",
            "SalVentAttnA",
            "SalVentAttnB",
            "LimbicOFC",
            "LimbicTempPole",
            "ContA",
            "ContB",
            "ContC",
            "DefaultA",
            "DefaultB",
            "DefaultC",
            "TempPar",
        ],
        help="Optionally specify the name of any of the 2017 Yeo-Schaefer RSNs"
             " (7-network or 17-network): Vis, SomMot, DorsAttn, SalVentAttn,"
             " Limbic, Cont, Default, VisCent, VisPeri, SomMotA, SomMotB, "
             "DorsAttnA, DorsAttnB, SalVentAttnA, SalVentAttnB, LimbicOFC, "
             "LimbicTempPole, ContA, ContB, ContC, DefaultA, DefaultB, "
             "DefaultC, TempPar. If listing multiple RSNs, separate them by "
             "space. (e.g. -n 'Default' 'Cont' 'SalVentAttn')'.\n",
    )
    parser.add_argument(
        "-vox",
        default="2mm",
        nargs=1,
        choices=["1mm", "2mm"],
        help="Optionally use this flag if you wish to change the resolution of"
             " the images in the workflow. Default is 2mm.\n",
    )
    parser.add_argument(
        "-plt",
        default=False,
        action="store_true",
        help="Optionally use this flag if you wish to activate plotting of "
             "adjacency matrices, connectomes, and time-series.\n",
    )

    # Debug/Runtime settings
    parser.add_argument(
        "-pm",
        metavar="Cores,memory",
        default="auto",
        help="Number of cores to use, number of GB of memory to use for single"
             " subject run, entered as two integers seperated by comma. "
             "Otherwise, default is `auto`, which uses all resources "
             "detected on the current compute node.\n",
    )
    parser.add_argument(
        "-plug",
        metavar="Scheduler type",
        default="MultiProc",
        nargs=1,
        choices=[
            "Linear",
            "MultiProc",
            "SGE",
            "PBS",
            "SLURM",
            "SGEgraph",
            "SLURMgraph",
            "LegacyMultiProc",
        ],
        help="Include this flag to specify a workflow plugin other than the"
             " default MultiProc.\n",
    )
    parser.add_argument(
        "-v",
        default=False,
        action="store_true",
        help="Verbose print for debugging.\n")
    parser.add_argument(
        "-noclean",
        default=False,
        action="store_true",
        help="Disable post-workflow clean-up of temporary runtime metadata.\n",
    )
    parser.add_argument(
        "-work",
        metavar="Working directory",
        default="/tmp/work",
        help="Specify the path to a working directory for pynets to run. "
             "Default is /tmp/work.\n",
    )
    parser.add_argument("--version", action="version", version=verstr)
    return parser


def build_workflow(args, retval):
    import warnings

    warnings.filterwarnings("ignore")
    import os
    import glob
    import ast
    import os.path as op
    import timeit
    from datetime import timedelta
    from colorama import Fore, Style
    from pathlib import Path
    import datetime
    from os import environ
    from subprocess import check_output
    from pynets.core.utils import load_runconfig

    try:
        import pynets

        print(f"{Fore.RED}\n\nPyNets\nVersion: "
              f"{pynets.__version__}")
    except ImportError:
        print(
            "PyNets not installed! Ensure that you are using the correct "
            "python version."
        )

    if environ.get('FSLDIR') is None:
        print('EnvironmentError: FSLDIR not found! '
              'Be sure that this '
              'environment variable is set and/or that '
              'FSL has been properly installed before '
              'proceeding.')
        retval["return_code"] = 1
        return retval
    else:
        fsl_version = check_output('flirt -version | cut -f3 -d\" \"',
                                   shell=True).strip()
        fsldir = os.environ['FSLDIR']

        if fsl_version and os.path.isdir(fsldir):
            print(f"{Fore.MAGENTA}FSL {fsl_version.decode()} detected: "
                  f"FSLDIR={fsldir}")
        else:
            print('Is your FSL installation corrupted? Check permissions and'
                  ' ensure that you have correctly configured your local '
                  'profile (e.g. ~/.bashrc).')
            retval["return_code"] = 1
            return retval

    # Start timer
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"{Fore.MAGENTA}{timestamp}")
    start_time = timeit.default_timer()
    print(Style.RESET_ALL)

    # Hard-coded:
    hardcoded_params = load_runconfig()

    maxcrossing = hardcoded_params['tracking']["maxcrossing"][0]
    local_corr = hardcoded_params["clustering_local_conn"][0]
    track_type = hardcoded_params['tracking']["tracking_method"][0]
    tiss_class = hardcoded_params['tracking']["tissue_classifier"][0]
    target_samples = hardcoded_params['tracking']["tracking_samples"][0]
    use_parcel_naming = hardcoded_params["parcel_naming"][0]
    step_list = hardcoded_params['tracking']["step_list"]
    curv_thr_list = hardcoded_params['tracking']["curv_thr_list"]
    nilearn_parc_atlases = hardcoded_params["nilearn_parc_atlases"]
    nilearn_coord_atlases = hardcoded_params["nilearn_coord_atlases"]
    nilearn_prob_atlases = hardcoded_params["nilearn_prob_atlases"]
    local_atlases = hardcoded_params["local_atlases"]
    roi_neighborhood_tol = \
        hardcoded_params['tracking']["roi_neighborhood_tol"][0]

    # Set Arguments to global variables
    ID = args.id
    outdir = f"{args.output_dir}/pynets"
    os.makedirs(outdir, exist_ok=True)
    func_file = args.func
    mask = args.m
    dwi_file = args.dwi
    fbval = args.bval
    fbvec = args.bvec
    graph = args.g

    if graph is not None:
        include_str_matches = ['ventral']
        if len(graph) > 1:
            multi_subject_graph = graph
            multi_subject_multigraph = []
            for g in multi_subject_graph:
                if "," in g:
                    multi_graph = g.split(",")
                    multi_subject_multigraph.append(multi_graph)
                else:
                    multi_graph = None
            if len(multi_subject_multigraph) == 0:
                multi_subject_multigraph = None
            else:
                multi_subject_graph = None
            graph = None
            multi_graph = None
        elif graph == ["None"]:
            graph = None
            multi_graph = None
            multi_subject_graph = None
            multi_subject_multigraph = None
        else:
            graph = graph[0]
            if os.path.isdir(graph):
                graph_iter = Path(graph).rglob('rawgraph*.npy')
                if isinstance(ID, list):
                    if len(ID) > 1:
                        multi_graph = None
                        multi_subject_multigraph = []
                        for id in ID:
                            multi_subject_multigraph.append(
                                [str(g) for g in graph_iter if id in str(g)])
                    else:
                        multi_subject_multigraph = None
                        ID = ID[0]
                        multi_graph = [str(g) for g in
                                       graph_iter if
                                       ID in str(g)]
                else:
                    multi_subject_multigraph = None
                    multi_graph = [str(g) for g in
                                   graph_iter if
                                   ID in str(g)]
                graph = None
                multi_subject_graph = None
            else:
                if "," in graph:
                    multi_graph = graph.split(",")
                else:
                    multi_graph = None
                multi_subject_graph = None
                multi_subject_multigraph = None

        if len(include_str_matches) > 0:
            if multi_graph is not None:
                multi_graph = [i for
                               i in multi_graph
                               if any(i for j in include_str_matches if
                                      str(j) in i)]
            if multi_subject_graph is not None:
                multi_subject_graph = [i for
                                       i in multi_subject_graph if
                                       any(i for j in include_str_matches if
                                           str(j) in i)]
            if multi_subject_multigraph is not None:
                multi_subject_multigraph = [i for i in
                                            multi_subject_multigraph if
                                            any(i for j in
                                                include_str_matches if
                                                str(j) in i)]
    else:
        multi_graph = None
        multi_subject_graph = None
        multi_subject_multigraph = None

    if (ID is None) and (
        graph is None
        and multi_graph is None
        and multi_subject_graph is None
        and multi_subject_multigraph is None
    ):
        print("\nERROR: You must include a subject ID in your command "
              "line call.")
        retval["return_code"] = 1
        return retval

    if (
        multi_subject_graph or multi_subject_multigraph or graph or multi_graph
    ) and isinstance(ID, list):
        if multi_subject_graph:
            if len(ID) != len(multi_subject_graph):
                print(
                    "\nERROR: Length of ID list does not correspond to length"
                    " of input graph file list."
                )
                retval["return_code"] = 1
                return retval
        if multi_subject_multigraph:
            if len(ID) != len(multi_subject_multigraph):
                print(
                    "\nERROR: Length of ID list does not correspond to length"
                    " of input graph file list."
                )
                retval["return_code"] = 1
                return retval
        if len(ID) > 1 and not multi_subject_graph and not \
                multi_subject_multigraph:
            print(
                "\nLength of ID list does not correspond to length of"
                " input graph file list."
            )
            retval["return_code"] = 1
            return retval

    resources = args.pm
    if resources == "auto":
        import psutil
        nthreads = psutil.cpu_count()
        vmem = int(list(psutil.virtual_memory())[4]/1000000000) - 1
        procmem = [int(nthreads),
                   [vmem if vmem > 8 else int(8)][0]]
    else:
        procmem = list(eval(str(resources)))
        procmem[1] = procmem[1] - 1
    if args.thr is None:
        thr = float(1.0)
    else:
        thr = float(args.thr)
    node_size = args.ns
    if node_size:
        if (isinstance(node_size, list)) and (len(node_size) > 1):
            node_size_list = node_size
            node_size = None
        elif node_size == ["None"]:
            node_size = None
            node_size_list = None
        elif isinstance(node_size, list):
            node_size = node_size[0]
            node_size_list = None
        else:
            node_size = None
            node_size_list = None
    else:
        node_size_list = None
    smooth = args.sm
    if smooth:
        if (isinstance(smooth, list)) and (len(smooth) > 1):
            smooth_list = smooth
            smooth = 0
        elif smooth == ["None"]:
            smooth = 0
            smooth_list = None
        elif isinstance(smooth, list):
            smooth = smooth[0]
            smooth_list = None
        else:
            smooth = 0
            smooth_list = None
    else:
        smooth_list = None
    hpass = args.hp
    if hpass:
        if (isinstance(hpass, list)) and (len(hpass) > 1):
            hpass_list = hpass
            hpass = None
        elif hpass == ["None"]:
            hpass = None
            hpass_list = None
        elif isinstance(hpass, list):
            hpass = hpass[0]
            hpass_list = None
        else:
            hpass = None
            hpass_list = None
    else:
        hpass_list = None
    extract_strategy = args.es
    if extract_strategy:
        if (isinstance(extract_strategy, list)) and (
                len(extract_strategy) > 1):
            extract_strategy_list = extract_strategy
            extract_strategy = "mean"
        elif extract_strategy == ["None"]:
            extract_strategy = "mean"
            extract_strategy_list = None
        elif isinstance(extract_strategy, list):
            extract_strategy = extract_strategy[0]
            extract_strategy_list = None
        else:
            extract_strategy = "mean"
            extract_strategy_list = None
    else:
        extract_strategy_list = None
    roi = args.roi
    if isinstance(roi, list):
        roi = roi[0]
    conn_model = args.mod
    if conn_model:
        if (isinstance(conn_model, list)) and (len(conn_model) > 1):
            conn_model_list = conn_model
        elif conn_model == ["None"]:
            conn_model_list = None
        elif isinstance(conn_model, list):
            conn_model = conn_model[0]
            conn_model_list = None
        else:
            conn_model_list = None
    else:
        conn_model_list = None
    conf = args.conf
    dens_thresh = args.dt
    min_span_tree = args.mst
    disp_filt = args.df
    clust_type = args.ct
    if clust_type:
        if (isinstance(clust_type, list)) and len(clust_type) > 1:
            clust_type_list = clust_type
            clust_type = None
        elif clust_type == ["None"]:
            clust_type = None
            clust_type_list = None
        elif isinstance(clust_type, list):
            clust_type = clust_type[0]
            clust_type_list = None
        else:
            clust_type = None
            clust_type_list = None
    else:
        clust_type_list = None
    plot_switch = args.plt
    min_thr = args.min_thr
    max_thr = args.max_thr
    step_thr = args.step_thr
    anat_file = args.anat
    spheres = args.spheres
    if spheres is True:
        parc = False
    else:
        parc = True

    if parc is True:
        node_size = None
        node_size_list = None
    else:
        if node_size:
            if node_size is None:
                if (func_file is not None) and (dwi_file is None):
                    node_size = 4
                elif (func_file is None) and (dwi_file is not None):
                    node_size = 8
    ref_txt = args.ref
    k = args.k
    if k:
        if (isinstance(k, list)) and (len(k) > 1):
            k_list = [int(i) for i in k]
            k = None
        elif isinstance(k, list):
            k = k[0]
            k_list = None
        else:
            k_list = None
    else:
        k_list = None
    prune = args.p
    if isinstance(prune, list):
        prune = prune[0]
    norm = args.norm
    if isinstance(norm, list):
        norm = norm[0]
    binary = args.bin
    plugin_type = args.plug
    if isinstance(plugin_type, list):
        plugin_type = plugin_type[0]
    verbose = args.v
    clust_mask = args.cm
    if clust_mask:
        if len(clust_mask) > 1:
            clust_mask_list = clust_mask
            clust_mask = None
        elif clust_mask == ["None"]:
            clust_mask = None
            clust_mask_list = None
        else:
            clust_mask = clust_mask[0]
            clust_mask_list = None
    else:
        clust_mask_list = None
    waymask = args.way
    if isinstance(waymask, list):
        waymask = waymask[0]
    network = args.n
    if network:
        if (isinstance(network, list)) and (len(network) > 1):
            multi_nets = network
            network = None
        elif network == ["None"]:
            network = None
            multi_nets = None
        elif isinstance(network, list):
            network = network[0]
            multi_nets = None
        else:
            network = None
            multi_nets = None
    else:
        multi_nets = None

    atlas_ins = args.a
    if atlas_ins is not None:
        # Parse uatlas files from atlas names
        uatlas = []
        atlas = []

        for atl in atlas_ins:
            if atl in nilearn_parc_atlases or atl in nilearn_coord_atlases or \
                    atl in nilearn_prob_atlases or atl in local_atlases:
                atlas.append(atl)
            elif '/' in atl:
                uatlas.append(atl)
                if not os.path.isfile(atl):
                    print(f"{atl} may not be an existing file path. "
                          f"You can safely ignore this warning if you are "
                          f"using container-mounted directory paths.")
            else:
                raise ValueError(f"{atl} is not in the pynets atlas library "
                                 f"nor is it a file path to a parcellation "
                                 f"file")

        if len(atlas) == 0:
            atlas = None

        if len(uatlas) == 0:
            uatlas = None

        if uatlas:
            if len(uatlas) > 1:
                user_atlas_list = uatlas
                uatlas = None
            elif uatlas == ["None"]:
                uatlas = None
                user_atlas_list = None
            else:
                uatlas = uatlas[0]
                user_atlas_list = None
        else:
            user_atlas_list = None

        if atlas:
            if (isinstance(atlas, list)) and (len(atlas) > 1):
                multi_atlas = atlas
                atlas = None
            elif atlas == ["None"]:
                multi_atlas = None
                atlas = None
            elif isinstance(atlas, list):
                atlas = atlas[0]
                multi_atlas = None
            else:
                atlas = None
                multi_atlas = None
        else:
            multi_atlas = None
    else:
        uatlas = None
        atlas = None
        multi_atlas = None
        user_atlas_list = None

    min_length = args.ml
    if min_length:
        if (isinstance(min_length, list)) and (len(min_length) > 1):
            min_length_list = min_length
            min_length = None
        elif min_length == ["None"]:
            min_length_list = None
        elif isinstance(min_length, list):
            min_length = min_length[0]
            min_length_list = None
        else:
            min_length_list = None
    else:
        min_length_list = None
    error_margin = args.tol
    if error_margin:
        if (isinstance(error_margin, list)) and (len(error_margin) > 1):
            error_margin_list = error_margin
            error_margin = None
        elif error_margin == ["None"]:
            error_margin_list = None
        elif isinstance(error_margin, list):
            error_margin = error_margin[0]
            error_margin_list = None
        else:
            error_margin_list = None
    else:
        error_margin_list = None
    directget = args.dg
    if directget:
        if (isinstance(directget, list)) and (len(directget) > 1):
            multi_directget = directget
            directget = None
        elif directget == ["None"]:
            multi_directget = None
        elif isinstance(directget, list):
            directget = directget[0]
            multi_directget = None
        else:
            multi_directget = None
    else:
        multi_directget = None
    embed = args.embed
    multiplex = args.mplx
    if isinstance(multiplex, list):
        multiplex = multiplex[0]
    vox_size = args.vox
    if isinstance(vox_size, list):
        vox_size = vox_size[0]
    work_dir = args.work
    os.makedirs(work_dir, exist_ok=True)

    print(
        "\n\n\n---------------------------------------------------------------"
        "---------\n"
    )

    if track_type == "particle":
        tiss_class = "cmc"

    # Set paths to templates
    runtime_dict = {}
    execution_dict = {}
    for i in range(len(hardcoded_params["resource_dict"])):
        runtime_dict[
            list(hardcoded_params["resource_dict"][i].keys())[0]
        ] = ast.literal_eval(
            list(hardcoded_params["resource_dict"][i].values())[0][0]
        )
    for i in range(len(hardcoded_params["execution_dict"])):
        execution_dict[
            list(hardcoded_params["execution_dict"][i].keys())[0]
        ] = list(hardcoded_params["execution_dict"][i].values())[0][0]

    if (min_thr is not None) and (
            max_thr is not None) and (step_thr is not None):
        multi_thr = True
    elif (min_thr is not None) or (max_thr is not None) or \
            (step_thr is not None):
        print("ERROR: Missing either min_thr, max_thr, or step_thr flags!")
        retval["return_code"] = 1
        return retval
    else:
        multi_thr = False

    # Check required inputs for existence, and configure run
    if (
        (func_file is None)
        and (dwi_file is None)
        and (graph is None)
        and (multi_graph is None)
        and (multi_subject_graph is None)
        and (multi_subject_multigraph is None)
    ):
        print(
            "\nERROR: You must include a file path to either a 4d BOLD EPI"
            " image in T1w space"
            "in .nii/.nii.gz format using the `-func` flag, or a 4d DWI image"
            " series in native diffusion"
            "space using the `-dwi` flag.")
        retval["return_code"] = 1
        return retval
    if func_file:
        if isinstance(func_file, list) and len(func_file) > 1:
            func_file_list = func_file
            func_file = None
        elif isinstance(func_file, list):
            func_file = func_file[0]
            func_file_list = None
        elif func_file.endswith(".txt"):
            with open(func_file) as f:
                func_file_list = f.read().splitlines()
            func_file = None
        else:
            func_file = None
            func_file_list = None
    else:
        func_file_list = None

    if not anat_file and not graph and not multi_graph:
        print(
            "ERROR: An anatomical image must be specified for fmri and"
            " dmri_connectometry using the `-anat` flag."
        )
        retval["return_code"] = 1
        return retval
    if dwi_file:
        if isinstance(dwi_file, list) and len(dwi_file) > 1:
            dwi_file_list = dwi_file
            dwi_file = None
        elif isinstance(dwi_file, list):
            dwi_file = dwi_file[0]
            dwi_file_list = None
        elif dwi_file.endswith(".txt"):
            with open(dwi_file) as f:
                dwi_file_list = f.read().splitlines()
            dwi_file = None
        else:
            dwi_file = None
            dwi_file_list = None
    else:
        dwi_file_list = None
        track_type = None
        tiss_class = None
        directget = None

    if (ID is None) and (func_file_list is None):
        print("\nERROR: You must include a subject ID in your command line "
              "call.")
        retval["return_code"] = 1
        return retval

    if func_file_list and isinstance(ID, list):
        if len(ID) != len(func_file_list):
            print(
                "ERROR: Length of ID list does not correspond to length of"
                " input func file list."
            )
            retval["return_code"] = 1
            return retval

    if isinstance(ID, list) and len(ID) == 1:
        ID = ID[0]

    if conf:
        if isinstance(conf, list) and func_file_list:
            if len(conf) != len(func_file_list):
                print(
                    "ERROR: Length of confound regressor list does not"
                    " correspond to length of input file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                conf_list = conf
                conf = None
        elif isinstance(conf, list):
            conf = conf[0]
            conf_list = None
        elif conf.endswith(".txt"):
            with open(conf) as f:
                conf_list = f.read().splitlines()
            conf = None
        else:
            conf = None
            conf_list = None
    else:
        conf_list = None

    if dwi_file_list and isinstance(ID, list):
        if len(ID) != len(dwi_file_list):
            print(
                "ERROR: Length of ID list does not correspond to length of"
                " input dwi file list."
            )
            retval["return_code"] = 1
            return retval
    if fbval:
        if isinstance(fbval, list) and dwi_file_list:
            if len(fbval) != len(dwi_file_list):
                print(
                    "ERROR: Length of fbval list does not correspond to"
                    " length of input dwi file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                fbval_list = fbval
                fbval = None
        elif isinstance(fbval, list):
            fbval = fbval[0]
            fbval_list = None
        elif fbval.endswith(".txt"):
            with open(fbval) as f:
                fbval_list = f.read().splitlines()
            fbval = None
        else:
            fbval = None
            fbval_list = None
    else:
        fbval_list = None

    if fbvec:
        if isinstance(fbvec, list) and dwi_file_list:
            if len(fbvec) != len(dwi_file_list):
                print(
                    "ERROR: Length of fbvec list does not correspond to length"
                    " of input dwi file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                fbvec_list = fbvec
                fbvec = None
        elif isinstance(fbvec, list):
            fbvec = fbvec[0]
            fbvec_list = None
        elif fbvec.endswith(".txt"):
            with open(fbvec) as f:
                fbvec_list = f.read().splitlines()
            fbvec = None
        else:
            fbvec = None
            fbvec_list = None
    else:
        fbvec_list = None

    if anat_file:
        if isinstance(anat_file, list) and dwi_file_list and func_file_list:
            if len(anat_file) != len(dwi_file_list) and len(anat_file) != len(
                dwi_file_list
            ):
                print(
                    "ERROR: Length of anat list does not correspond to length"
                    " of input dwi and func file lists."
                )
                retval["return_code"] = 1
                return retval
            else:
                anat_file_list = anat_file
                anat_file = None
        elif isinstance(anat_file, list) and dwi_file_list:
            if len(anat_file) != len(dwi_file_list):
                print(
                    "ERROR: Length of anat list does not correspond to length"
                    " of input dwi file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                anat_file_list = anat_file
                anat_file = None
        elif isinstance(anat_file, list) and func_file_list:
            if len(anat_file) != len(func_file_list):
                print(
                    "ERROR: Length of anat list does not correspond to length"
                    " of input func file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                anat_file_list = anat_file
                anat_file = None
        elif isinstance(anat_file, list):
            anat_file = anat_file[0]
            anat_file_list = None
        else:
            anat_file_list = None
            anat_file = None
    else:
        anat_file_list = None

    if mask:
        if isinstance(mask, list) and func_file_list and dwi_file_list:
            if len(mask) != len(func_file_list) and len(
                    mask) != len(dwi_file_list):
                print(
                    "ERROR: Length of brain mask list does not correspond to"
                    " length of input func "
                    "and dwi file lists.")
                retval["return_code"] = 1
                return retval
            else:
                mask_list = mask
                mask = None
        elif isinstance(mask, list) and func_file_list:
            if len(mask) != len(func_file_list):
                print(
                    "ERROR: Length of brain mask list does not correspond to"
                    " length of input func file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                mask_list = mask
                mask = None
        elif isinstance(mask, list) and dwi_file_list:
            if len(mask) != len(dwi_file_list):
                print(
                    "ERROR: Length of brain mask list does not correspond to"
                    " length of input dwi file list."
                )
                retval["return_code"] = 1
                return retval
            else:
                mask_list = mask
                mask = None
        elif isinstance(mask, list):
            mask = mask[0]
            mask_list = None
        else:
            mask_list = None
            mask = None
    else:
        mask_list = None

    if multi_thr is True:
        thr = None
    else:
        min_thr = None
        max_thr = None
        step_thr = None

    if (
        (k_list is not None)
        and (k is None)
        and (clust_mask_list is not None)
        and (clust_type_list is not None)
    ):
        k_clustering = 8
    elif (
        (k is not None)
        and (k_list is None)
        and (clust_mask_list is not None)
        and (clust_type_list is not None)
    ):
        k_clustering = 7
    elif (
        (k_list is not None)
        and (k is None)
        and (clust_mask_list is None)
        and (clust_type_list is not None)
    ):
        k_clustering = 6
    elif (
        (k is not None)
        and (k_list is None)
        and (clust_mask_list is None)
        and (clust_type_list is not None)
    ):
        k_clustering = 5
    elif (
        (k_list is not None)
        and (k is None)
        and (clust_mask_list is not None)
        and (clust_type_list is None)
    ):
        k_clustering = 4
    elif (
        (k is not None)
        and (k_list is None)
        and (clust_mask_list is not None)
        and (clust_type_list is None)
    ):
        k_clustering = 3
    elif (
        (k_list is not None)
        and (k is None)
        and (clust_mask_list is None)
        and (clust_type_list is None)
    ):
        k_clustering = 2
    elif (
        (k is not None)
        and (k_list is None)
        and (clust_mask_list is None)
        and (clust_type_list is None)
    ):
        k_clustering = 1
    else:
        k_clustering = 0

    if (
        func_file_list
        or dwi_file_list
        or multi_subject_graph
        or multi_subject_multigraph
    ):
        print(
            f"{Fore.YELLOW}Running workflow of workflows across multiple "
            f"subjects:\n")
        for i in ID:
            print(f"{Fore.BLUE}{str(ID)}")
    elif func_file_list is None and dwi_file_list is None:
        print(f"{Fore.YELLOW}Running workflow for single subject: "
              f"{Fore.BLUE}{str(ID)}")

    print(f"{Fore.GREEN}Population template: "
          f"{Fore.BLUE}{hardcoded_params['template'][0]}")
    if (
        graph is None
        and multi_graph is None
        and multi_subject_graph is None
        and multi_subject_multigraph is None
    ):
        if network is not None:
            print(f"{Fore.GREEN}Selecting one RSN subgraph: "
                  f"{Fore.BLUE}{network}")
        elif multi_nets is not None:
            network = None
            print(
                f"{Fore.GREEN}Iterating pipeline across "
                f"{Fore.BLUE}{len(multi_nets)} RSN subgraphs:"
            )
            print(
                f"{Fore.BLUE}{str(', '.join(str(n) for n in multi_nets))}"
            )
        else:
            print(f"{Fore.GREEN}Using whole-brain pipeline...")
        if node_size_list:
            print(
                f"{Fore.GREEN}Growing spherical nodes across multiple radius "
                f"sizes:"
            )
            print(f"{str(', '.join(str(n) for n in node_size_list))}")
            node_size = None
        elif parc is True:
            print(f"{Fore.GREEN}Using parcels as nodes...")
        else:
            if node_size is None:
                node_size = 4
            print(f"{Fore.BLUE}Using node size of {Fore.BLUE}{node_size}mm:")
        if func_file or func_file_list:
            if smooth_list:
                print(
                    f"{Fore.GREEN}Applying smoothing to node signal at "
                    f"multiple FWHM mm values:")
                print(
                    f"{Fore.BLUE}"
                    f"{str(', '.join(str(n) for n in smooth_list))}")
            elif float(smooth) > 0:
                print(
                    f"{Fore.GREEN}Applying smoothing to node signal at: "
                    f"{Fore.BLUE}{smooth}FWHM mm...")
            else:
                smooth = 0

            if hpass_list:
                print(
                    f"{Fore.GREEN}Applying high-pass filter to node signal at"
                    f" multiple Hz values:"
                )
                print(
                    f"{Fore.BLUE}{str(', '.join(str(n) for n in hpass_list))}"
                )
            elif hpass is not None:
                print(
                    f"{Fore.GREEN}Applying high-pass filter to node signal at:"
                    f" {Fore.BLUE}{hpass}Hz...")
            else:
                hpass = None

            if extract_strategy_list:
                print(
                    f"{Fore.GREEN}Extracting node signal using multiple"
                    f" strategies:"
                )
                print(
                    f"{Fore.BLUE}"
                    f"{str(', '.join(str(n) for n in extract_strategy_list))}"
                )
            else:
                print(
                    f"{Fore.GREEN}Extracting node signal using a "
                    f"{Fore.BLUE}{extract_strategy} {Fore.GREEN}strategy..."
                )

        if conn_model_list:
            print(
                f"{Fore.GREEN}Iterating graph estimation across multiple"
                f" connectivity models:"
            )
            print(
                f"{Fore.BLUE}{str(', '.join(str(n) for n in conn_model_list))}"
            )
            conn_model = None
        else:
            print(f"{Fore.GREEN}Using connectivity model: "
                  f"{Fore.BLUE}{conn_model}...")

    elif graph or multi_graph or multi_subject_graph or \
            multi_subject_multigraph:
        from pynets.core.utils import do_dir_path

        network = "custom_graph"
        roi = "None"
        k_clustering = 0
        node_size = "None"
        hpass = "None"
        if not conn_model:
            conn_model = "None"

    if func_file or func_file_list:
        if (uatlas is not None) and (
                k_clustering == 0) and (user_atlas_list is None):
            atlas_par = uatlas.split("/")[-1].split(".")[0]
            print(f"{Fore.GREEN}User atlas: {Fore.BLUE}{atlas_par}")
        elif (uatlas is not None) and (user_atlas_list is None) and \
                (k_clustering == 0):
            atlas_par = uatlas.split("/")[-1].split(".")[0]
            print(f"{Fore.GREEN}User atlas: {Fore.BLUE}{atlas_par}")
        elif user_atlas_list is not None:
            print(f"{Fore.GREEN}Iterating functional connectometry across "
                  f"multiple parcellations:")
            if func_file_list:
                for _uatlas in user_atlas_list:
                    atlas_par = _uatlas.split("/")[-1].split(".")[0]
                    print(f"{Fore.BLUE}{atlas_par}")
            else:
                for _uatlas in user_atlas_list:
                    atlas_par = _uatlas.split("/")[-1].split(".")[0]
                    print(f"{Fore.BLUE}{atlas_par}")
        if k_clustering == 1:
            cl_mask_name = op.basename(clust_mask).split(".nii")[0]
            atlas_clust = f"{cl_mask_name}_{clust_type}_k{k}"
            print(f"{Fore.GREEN}Cluster atlas: {Fore.BLUE}{atlas_clust}")
            print(f"{Fore.GREEN}Clustering within mask at a single"
                  f" resolution...")
        elif k_clustering == 2:
            print(f"{Fore.GREEN}Clustering within mask at multiple"
                  f" resolutions:")
            if func_file_list:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _k in k_list:
                    cl_mask_name = op.basename(clust_mask).split(".nii")[0]
                    atlas_clust = f"{cl_mask_name}_{clust_type}_k{_k}"
                    print(f"{Fore.BLUE}{atlas_clust}")
            else:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _k in k_list:
                    cl_mask_name = op.basename(clust_mask).split(".nii")[0]
                    atlas_clust = f"{cl_mask_name}_{clust_type}_k{_k}"
                    print(f"{Fore.BLUE}{atlas_clust}")
            k = None
        elif k_clustering == 3:
            print(f"{Fore.GREEN}Clustering within multiple masks at a single"
                  f" resolution:")
            if func_file_list:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _clust_mask in clust_mask_list:
                    cl_mask_name = op.basename(_clust_mask).split(".nii")[0]
                    atlas_clust = f"{cl_mask_name}_{clust_type}_k{k}"
                    print(f"{Fore.BLUE}{atlas_clust}")
            else:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _clust_mask in clust_mask_list:
                    cl_mask_name = op.basename(_clust_mask).split(".nii")[0]
                    atlas_clust = f"{cl_mask_name}_{clust_type}_k{k}"
                    print(f"{Fore.BLUE}{atlas_clust}")
            clust_mask = None
        elif k_clustering == 4:
            print("Clustering within multiple masks at multiple resolutions:")
            if func_file_list:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _clust_mask in clust_mask_list:
                    for _k in k_list:
                        cl_mask_name = op.basename(
                            _clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{clust_type}_k{_k}"
                        print(f"Cluster atlas: {atlas_clust}")
            else:
                print(f"{Fore.GREEN}Cluster atlas:")
                for _clust_mask in clust_mask_list:
                    for _k in k_list:
                        cl_mask_name = op.basename(
                            _clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{clust_type}_k{_k}"
                        print(f"{Fore.BLUE}{atlas_clust}")
            clust_mask = None
            k = None
        elif k_clustering == 5:
            print(
                f"{Fore.GREEN}Clustering within mask at a single resolution"
                f" using multiple clustering methods:"
            )
            for _clust_type in clust_type_list:
                cl_mask_name = op.basename(clust_mask).split(".nii")[0]
                atlas_clust = f"{cl_mask_name}_{_clust_type}_k{k}"
                print(f"{Fore.BLUE}{atlas_clust}")
            clust_type = None
        elif k_clustering == 6:
            print(
                f"{Fore.GREEN}Clustering within mask at multiple resolutions"
                f" using multiple clustering methods:"
            )
            if func_file_list:
                for _clust_type in clust_type_list:
                    for _k in k_list:
                        cl_mask_name = op.basename(clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{_clust_type}_k{_k}"
                        print(f"{Fore.BLUE}{atlas_clust}")
            else:
                for _clust_type in clust_type_list:
                    for _k in k_list:
                        cl_mask_name = op.basename(clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{_clust_type}_k{_k}"
                        print(f"{Fore.BLUE}{atlas_clust}")
            clust_type = None
            k = None
        elif k_clustering == 7:
            print(
                f"{Fore.GREEN}Clustering within multiple masks at a single"
                f" resolution using multiple clustering methods:"
            )
            if func_file_list:
                for _clust_type in clust_type_list:
                    for _clust_mask in clust_mask_list:
                        cl_mask_name = op.basename(
                            _clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{_clust_type}_k{k}"
                        print(f"{Fore.BLUE}{atlas_clust}")
            else:
                for _clust_type in clust_type_list:
                    for _clust_mask in clust_mask_list:
                        cl_mask_name = op.basename(
                            _clust_mask).split(".nii")[0]
                        atlas_clust = f"{cl_mask_name}_{_clust_type}_k{k}"
                        print(f"{Fore.BLUE}{atlas_clust}")
            clust_mask = None
            clust_type = None
        elif k_clustering == 8:
            print(
                f"{Fore.GREEN}Clustering within multiple masks at multiple"
                f" resolutions using multiple clustering methods:"
            )
            if func_file_list:
                for _clust_type in clust_type_list:
                    for _clust_mask in clust_mask_list:
                        for _k in k_list:
                            cl_mask_name = op.basename(
                                _clust_mask).split(".nii")[0]
                            atlas_clust = f"{cl_mask_name}_{_clust_type}_k{_k}"
                            print(f"{Fore.BLUE}{atlas_clust}")
            else:
                for _clust_type in clust_type_list:
                    for _clust_mask in clust_mask_list:
                        for _k in k_list:
                            cl_mask_name = op.basename(
                                _clust_mask).split(".nii")[0]
                            atlas_clust = f"{cl_mask_name}_{_clust_type}_k{_k}"
                            print(f"{Fore.BLUE}{atlas_clust}")
            clust_mask = None
            clust_type = None
            k = None
        elif (
            (user_atlas_list is not None or uatlas is not None)
            and (
                k_clustering == 4
                or k_clustering == 3
                or k_clustering == 2
                or k_clustering == 1
            )
            and (atlas is None)
        ):
            print(
                "ERROR: the -a flag cannot be used alone with the clustering"
                " option. Use the `-cm` flag instead."
            )
            retval["return_code"] = 1
            return retval

        if multi_atlas is not None:
            print(
                f"{Fore.GREEN}Iterating functional connectometry across"
                f" multiple predefined atlases:"
            )
            if func_file_list:
                for _func_file in func_file_list:
                    for _atlas in multi_atlas:
                        if (parc is True) and (
                            _atlas in nilearn_coord_atlases
                            or _atlas in nilearn_prob_atlases
                        ):
                            print(
                                f"\nERROR: {_atlas} is a coordinate atlas and"
                                f" must be used with the `-spheres` flag."
                            )
                            retval["return_code"] = 1
                            return retval
                        else:
                            print(f"{Fore.BLUE}{_atlas}")
            else:
                for _atlas in multi_atlas:
                    if (parc is True) and (
                        _atlas in nilearn_coord_atlases
                        or _atlas in nilearn_prob_atlases
                    ):
                        print(
                            f"\nERROR: {_atlas} is a coordinate atlas and must"
                            f" be used with the `-spheres` flag."
                        )
                        retval["return_code"] = 1
                        return retval
                    else:
                        print(f"{Fore.BLUE}{_atlas}")
        elif atlas is not None:
            if (parc is True) and (
                atlas in nilearn_coord_atlases or atlas in nilearn_prob_atlases
            ):
                print(
                    f"\nERROR: {atlas} is a coordinate atlas and must be used"
                    f" with the `-spheres` flag."
                )
                retval["return_code"] = 1
                return retval
            else:
                print(f"{Fore.GREEN}Using curated atlas: {Fore.BLUE}{atlas}")
        else:
            if (
                (uatlas is None)
                and (k == 0)
                and (user_atlas_list is None)
                and (k_list is None)
                and (atlas is None)
                and (multi_atlas is None)
            ):
                print("\nERROR: No atlas specified!")
                retval["return_code"] = 1
                return retval
            else:
                pass

    if dwi_file or dwi_file_list:
        if (conn_model == "ten") and (directget == "prob"):
            print(
                "\nERROR: Cannot perform probabilistic tracking with tensor "
                "model estimation..."
            )
            retval["return_code"] = 1
            return retval

        if (track_type == "particle") and (
            conn_model == "ten" or tiss_class != "cmc"
        ):
            print(
                "Can only perform particle tracking with the `cmc` tissue"
                " classsifier and diffusion models "
                "other than tensor...")
            retval["return_code"] = 1
            return retval

        if user_atlas_list:
            print(f"{Fore.GREEN}Iterating structural connectometry across "
                  f"multiple parcellations:")
            if dwi_file_list:
                for _dwi_file in dwi_file_list:
                    for _uatlas in user_atlas_list:
                        atlas_par = _uatlas.split("/")[-1].split(".")[0]
                        print(f"{Fore.BLUE}{atlas_par}")
            else:
                for _uatlas in user_atlas_list:
                    atlas_par = _uatlas.split("/")[-1].split(".")[0]
                    print(f"{Fore.BLUE}{atlas_par}")
        if multi_atlas:
            print(
                f"{Fore.GREEN}Iterating structural connectometry across"
                f" multiple predefined atlases:"
            )
            if dwi_file_list:
                for _dwi_file in dwi_file_list:
                    for _atlas in multi_atlas:
                        if (parc is True) and (
                                _atlas in nilearn_coord_atlases):
                            print(
                                f"\nERROR: {_atlas} is a coordinate atlas and"
                                f" must be used with the -spheres flag."
                            )
                            retval["return_code"] = 1
                            return retval
                        else:
                            print(f"{Fore.BLUE}{_atlas}")
            else:
                for _atlas in multi_atlas:
                    if (parc is True) and (_atlas in nilearn_coord_atlases):
                        print(
                            f"\nERROR: {_atlas} is a coordinate atlas and must"
                            f" be used with the -spheres flag."
                        )
                        retval["return_code"] = 1
                        return retval
                    else:
                        print(f"{Fore.BLUE}{_atlas}")
        elif atlas:
            if (parc is True) and (atlas in nilearn_coord_atlases):
                print(
                    f"\nERROR: {atlas} is a coordinate atlas and must be used "
                    f"with the -spheres flag."
                )
                retval["return_code"] = 1
                return retval
            else:
                print(f"{Fore.GREEN}Using curated atlas: {Fore.BLUE}{atlas}")

        if directget:
            print(f"{Fore.GREEN}Using {Fore.BLUE}{directget} "
                  f"{Fore.GREEN}direction getting...")
        else:
            print(f"{Fore.GREEN}Iterating direction getting:")
            print(f"{Fore.BLUE}{', '.join(multi_directget)}")
        if min_length:
            print(f"{Fore.GREEN}Using {Fore.BLUE}{min_length}mm{Fore.GREEN} "
                  f"minimum streamline length...")
        else:
            print(f"{Fore.GREEN}Iterating minimum streamline lengths:")
            print(f"{Fore.BLUE}{', '.join(min_length_list)}")
        if error_margin:
            if float(roi_neighborhood_tol) <= float(error_margin):
                print('\nERROR: roi_neighborhood_tol preset cannot be less '
                      'than the value of the structural connectome '
                      'error_margin parameter.')
                retval["return_code"] = 1
                return retval

            print(f"{Fore.GREEN}Using {Fore.BLUE}{error_margin}"
                  f"mm{Fore.GREEN} error margin...")
        else:
            for em in error_margin_list:
                if float(roi_neighborhood_tol) <= float(em):
                    print('\nERROR: roi_neighborhood_tol preset cannot be '
                          'less than the value of the structural connectome '
                          'error_margin parameter.')
                    retval["return_code"] = 1
                    return retval
            print(f"{Fore.GREEN}Iterating ROI-streamline intersection "
                  f"tolerance:")
            print(f"{Fore.BLUE}{', '.join(error_margin_list)}")

        if target_samples:
            print(f"{Fore.GREEN}Using {Fore.BLUE}{target_samples} "
                  f"{Fore.GREEN}streamline samples...")
        print(f"{Fore.GREEN}Using {Fore.BLUE}{track_type} "
              f"{Fore.GREEN}tracking with {Fore.BLUE}{tiss_class} "
              f"{Fore.GREEN}tissue classification...")
        print(f"{Fore.GREEN}Ensemble tractography step sizes: "
              f"{Fore.BLUE}{step_list} {Fore.GREEN}and curvature thresholds: "
              f"{Fore.BLUE}{curv_thr_list}")
    if (dwi_file or dwi_file_list) and not (func_file or func_file_list):
        print(f"\n{Fore.WHITE}Running {Fore.BLUE}dmri{Fore.WHITE} "
              f"connectometry only...")
        if dwi_file_list:
            for (_dwi_file, _fbval, _fbvec, _anat_file) in list(
                zip(dwi_file_list, fbval_list, fbvec_list, anat_file_list)
            ):
                print(f"{Fore.GREEN}Diffusion-Weighted Image:{Fore.BLUE}\n "
                      f"{_dwi_file}")
                if not os.path.isfile(_dwi_file):
                    print(f"\nERROR: {_dwi_file} does not exist. "
                          f"Ensure that you are only specifying absolute "
                          f"paths.")
                    retval["return_code"] = 1
                    return retval

                print(f"{Fore.GREEN}B-Values:\n{Fore.BLUE} {_fbval}")
                print(f"{Fore.GREEN}B-Vectors:\n{Fore.BLUE} {_fbvec}")
                if not os.path.isfile(fbvec):
                    print(f"\nERROR: {_fbvec} does not exist. "
                          f"Ensure that you are only specifying absolute "
                          f"paths.")
                    retval["return_code"] = 1
                    return retval

                if not os.path.isfile(fbval):
                    print(f"\nERROR: {_fbval} does not exist. "
                          f"Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}Diffusion-Weighted Image:\n "
                  f"{Fore.BLUE}{dwi_file}")
            if not os.path.isfile(dwi_file):
                print(f"\nERROR: {dwi_file} does not exist. "
                      f"Ensure that you are"
                      f" only specifying absolute paths.")
                retval["return_code"] = 1
                return retval
            print(f"{Fore.GREEN}B-Values:\n {Fore.BLUE}{fbval}")
            print(f"{Fore.GREEN}B-Vectors:\n {Fore.BLUE}{fbvec}")
            if not os.path.isfile(fbvec):
                print(f"\nERROR: {fbvec} does not exist. Ensure that you are "
                      f"only specifying absolute paths.")
                retval["return_code"] = 1
                return retval
            if not os.path.isfile(fbval):
                print(f"\nERROR: {fbval} does not exist. Ensure that you are "
                      f"only specifying absolute paths.")
                retval["return_code"] = 1
                return retval
        if waymask is not None:
            print(f"{Fore.GREEN}Waymask:\n {Fore.BLUE}{waymask}")
            if not os.path.isfile(waymask):
                print(f"\nERROR: {waymask} does not exist. "
                      f"Ensure that you are "
                      f"only specifying absolute paths.")
                retval["return_code"] = 1
                return retval
        conf = None
        k = None
        clust_mask = None
        k_list = None
        k_clustering = None
        clust_mask_list = None
        hpass = None
        smooth = None
        extract_strategy = None
        clust_type = None
        local_corr = None
        clust_type_list = None
        multimodal = False
    elif (func_file or func_file_list) and not (dwi_file or dwi_file_list):
        print(f"\n{Fore.WHITE}Running {Fore.BLUE}fmri{Fore.WHITE} "
              f"connectometry only...")
        if func_file_list:
            for _func_file in func_file_list:
                print(f"{Fore.GREEN}BOLD Image:\n {Fore.BLUE}{_func_file}")
                if not os.path.isfile(_func_file):
                    print(f"\nERROR: {_func_file} does not exist. Ensure "
                          f"that you are only specifying "
                          f"absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}BOLD Image:\n {Fore.BLUE}{func_file}")
            if not os.path.isfile(func_file):
                print(f"\nERROR: {func_file} does not exist. "
                      f"Ensure that you are only specifying absolute paths.")
                retval["return_code"] = 1
                return retval
        if conf_list:
            for _conf in conf_list:
                print(f"{Fore.GREEN}BOLD Confound Regressors:\n "
                      f"{Fore.BLUE}{_conf}")
                if not os.path.isfile(_conf):
                    print(f"\nERROR: {_conf} does not exist. "
                          f"Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
        elif conf:
            print(f"{Fore.GREEN}BOLD Confound Regressors:\n {Fore.BLUE}{conf}")
            if not os.path.isfile(conf):
                print(f"\nERROR: {conf} does not exist. Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
        multimodal = False
    elif (func_file or func_file_list) and (dwi_file or dwi_file_list):
        multimodal = True
        print(f"\n{Fore.WHITE}Running joint {Fore.BLUE}fMRI-dMRI{Fore.WHITE} "
              f"connectometry...")
        if func_file_list:
            for _func_file in func_file_list:
                print(f"{Fore.GREEN}BOLD Image:\n {Fore.BLUE}{_func_file}")
                if not os.path.isfile(_func_file):
                    print(f"\nERROR: ERROR: {_func_file} does not exist. "
                          f"Ensure that you are only specifying "
                          f"absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}BOLD Image:\n {Fore.BLUE}{func_file}")
            if not os.path.isfile(func_file):
                print(f"\nERROR: {func_file} does not exist. "
                      f"Ensure that you are only "
                      f"specifying absolute paths.")
                retval["return_code"] = 1
                return retval
        if conf_list:
            for _conf in conf_list:
                print(f"{Fore.GREEN}BOLD Confound Regressors:\n "
                      f"{Fore.BLUE}{_conf}")
                if not os.path.isfile(_conf):
                    print(f"\nERROR: {_conf} does not exist. "
                          f"Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
        elif conf:
            print(f"{Fore.GREEN}BOLD Confound Regressors:\n {Fore.BLUE}{conf}")
            if not os.path.isfile(conf):
                print(f"\nERROR: {conf} does not exist. Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
        if dwi_file_list:
            for (_dwi_file, _fbval, _fbvec, _anat_file) in list(
                zip(dwi_file_list, fbval_list, fbvec_list, anat_file_list)
            ):
                print(f"{Fore.GREEN}Diffusion-Weighted Image:\n "
                      f"{Fore.BLUE}{_dwi_file}")
                if not os.path.isfile(_dwi_file):
                    print(f"\nERROR: {_dwi_file} does not exist."
                          f" Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
                print(f"{Fore.GREEN}B-Values:\n {Fore.BLUE}{_fbval}")
                print(f"{Fore.GREEN}B-Vectors:\n {Fore.BLUE}{_fbvec}")
                if not os.path.isfile(_fbvec):
                    print(f"\nERROR: {_fbvec} does not exist. "
                          f"Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
                if not os.path.isfile(_fbval):
                    print(f"\nERROR: {_fbval} does not exist. "
                          f"Ensure that you are only "
                          f"specifying absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}Diffusion-Weighted Image:\n "
                  f"{Fore.BLUE}{dwi_file}")
            if not os.path.isfile(dwi_file):
                print(f"\nERROR: {dwi_file} does not exist. "
                      f"Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
            print(f"{Fore.GREEN}B-Values:\n {Fore.BLUE}{fbval}")
            print(f"{Fore.GREEN}B-Vectors:\n {Fore.BLUE}{fbvec}")
            if not os.path.isfile(fbvec):
                print(f"\nERROR: {fbvec} does not exist. Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
            if not os.path.isfile(fbval):
                print(f"\nERROR: {fbval} does not exist. Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
        if waymask is not None:
            print(f"{Fore.GREEN}Waymask:\n {Fore.BLUE}{waymask}")
            if not os.path.isfile(waymask):
                print(f"\nERROR: {waymask} does not exist. "
                      f"Ensure that you are only "
                      f"specifying absolute paths.")
                retval["return_code"] = 1
                return retval
    else:
        multimodal = False

    if roi is not None and roi is not 'None':
        print(f"{Fore.GREEN}ROI:\n {Fore.BLUE}{roi}")
        if not os.path.isfile(roi):
            print(f"\nERROR: {roi} does not exist. Ensure "
                  f"that you are only specifying "
                  f"absolute paths.")
            retval["return_code"] = 1
            return retval
    if anat_file or anat_file_list:
        if anat_file_list and len(anat_file_list) > 1:
            for anat_file in anat_file_list:
                print(f"{Fore.GREEN}T1-Weighted Image:\n "
                      f"{Fore.BLUE}{anat_file}")
                if not os.path.isfile(anat_file):
                    print(
                        f"\nERROR: {anat_file} does not exist. Ensure "
                        f"that you are only specifying "
                        f"absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}T1-Weighted Image:\n {Fore.BLUE}{anat_file}")
            if not os.path.isfile(anat_file):
                print(f"\nERROR: {anat_file} does not exist. "
                      f"Ensure that you are only "
                      f"specifying absolute paths.")
                retval["return_code"] = 1
                return retval

    if mask or mask_list:
        if mask_list and len(mask_list) > 1:
            for mask in mask_list:
                print(f"{Fore.GREEN}Brain Mask Image:\n {Fore.BLUE}{mask}")
                if not os.path.isfile(mask):
                    print(
                        f"\nERROR: {mask} does not exist. Ensure "
                        f"that you are only specifying "
                        f"absolute paths.")
                    retval["return_code"] = 1
                    return retval
        else:
            print(f"{Fore.GREEN}Brain Mask Image:\n {Fore.BLUE}{mask}")
            if not os.path.isfile(mask):
                print(f"\nERROR: {mask} does not exist. Ensure "
                      f"that you are only specifying "
                      f"absolute paths.")
                retval["return_code"] = 1
                return retval
    print(Style.RESET_ALL)
    print(
        "\n-------------------------------------------------------------------"
        "------\n\n"
    )

    # Variable tracking
    retval["ID"] = ID
    retval["outdir"] = outdir
    retval["atlas"] = atlas
    retval["network"] = network
    retval["node_size"] = node_size
    retval["node_size_list"] = node_size_list
    retval["smooth"] = smooth
    retval["smooth_list"] = smooth_list
    retval["hpass"] = hpass
    retval["hpass_list"] = hpass_list
    retval["extract_strategy"] = extract_strategy
    retval["extract_strategy_list"] = extract_strategy_list
    retval["roi"] = roi
    retval["thr"] = thr
    retval["uatlas"] = uatlas
    retval["conn_model"] = conn_model
    retval["dens_thresh"] = dens_thresh
    retval["conf"] = conf
    retval["plot_switch"] = plot_switch
    retval["multi_thr"] = multi_thr
    retval["multi_atlas"] = multi_atlas
    retval["min_thr"] = min_thr
    retval["max_thr"] = max_thr
    retval["step_thr"] = step_thr
    retval["spheres"] = spheres
    retval["ref_txt"] = ref_txt
    retval["procmem"] = procmem
    retval["waymask"] = waymask
    retval["k"] = k
    retval["clust_mask"] = clust_mask
    retval["k_list"] = k_list
    retval["k_clustering"] = k_clustering
    retval["user_atlas_list"] = user_atlas_list
    retval["clust_mask_list"] = clust_mask_list
    retval["clust_type"] = clust_type
    retval["local_corr"] = local_corr
    retval["clust_type_list"] = clust_type_list
    retval["prune"] = prune
    retval["mask"] = mask
    retval["norm"] = norm
    retval["binary"] = binary
    retval["embed"] = embed
    retval["multiplex"] = multiplex
    retval["track_type"] = track_type
    retval["tiss_class"] = tiss_class
    retval["directget"] = directget
    retval["multi_directget"] = multi_directget
    retval["func_file"] = func_file
    retval["dwi_file"] = dwi_file
    retval["fbval"] = fbval
    retval["fbvec"] = fbvec
    retval["anat_file"] = anat_file
    retval["func_file_list"] = func_file_list
    retval["dwi_file_list"] = dwi_file_list
    retval["mask_list"] = mask_list
    retval["fbvec_list"] = fbvec_list
    retval["fbval_list"] = fbval_list
    retval["conf_list"] = conf_list
    retval["anat_file_list"] = anat_file_list

    # print('\n\n\n\n\n')
    # print("%s%s" % ('ID: ', ID))
    # print("%s%s" % ('outdir: ', outdir))
    # print("%s%s" % ('atlas: ', atlas))
    # print("%s%s" % ('network: ', network))
    # print("%s%s" % ('node_size: ', node_size))
    # print("%s%s" % ('smooth: ', smooth))
    # print("%s%s" % ('hpass: ', hpass))
    # print("%s%s" % ('hpass_list: ', hpass_list))
    # print("%s%s" % ('roi: ', roi))
    # print("%s%s" % ('thr: ', thr))
    # print("%s%s" % ('uatlas: ', uatlas))
    # print("%s%s" % ('conn_model: ', conn_model))
    # print("%s%s" % ('dens_thresh: ', dens_thresh))
    # print("%s%s" % ('conf: ', conf))
    # print("%s%s" % ('plot_switch: ', plot_switch))
    # print("%s%s" % ('multi_thr: ', multi_thr))
    # print("%s%s" % ('multi_atlas: ', multi_atlas))
    # print("%s%s" % ('min_thr: ', min_thr))
    # print("%s%s" % ('max_thr: ', max_thr))
    # print("%s%s" % ('step_thr: ', step_thr))
    # print("%s%s" % ('spheres: ', spheres))
    # print("%s%s" % ('ref_txt: ', ref_txt))
    # print("%s%s" % ('procmem: ', procmem))
    # print("%s%s" % ('waymask: ', waymask))
    # print("%s%s" % ('k: ', k))
    # print("%s%s" % ('clust_mask: ', clust_mask))
    # print("%s%s" % ('k_list: ', k_list))
    # print("%s%s" % ('k_clustering: ', k_clustering))
    # print("%s%s" % ('user_atlas_list: ', user_atlas_list))
    # print("%s%s" % ('clust_mask_list: ', clust_mask_list))
    # print("%s%s" % ('clust_type: ', clust_type))
    # print("%s%s" % ('local_corr: ', local_corr))
    # print("%s%s" % ('clust_type_list: ', clust_type_list))
    # print("%s%s" % ('prune: ', prune))
    # print("%s%s" % ('node_size_list: ', node_size_list))
    # print("%s%s" % ('smooth_list: ', smooth_list))
    # print("%s%s" % ('mask: ', mask))
    # print("%s%s" % ('norm: ', norm))
    # print("%s%s" % ('binary: ', binary))
    # print("%s%s" % ('embed: ', embed))
    # print("%s%s" % ('multiplex: ', multiplex))
    # print("%s%s" % ('track_type: ', track_type))
    # print("%s%s" % ('tiss_class: ', tiss_class))
    # print("%s%s" % ('directget: ', directget))
    # print("%s%s" % ('multi_directget: ', multi_directget))
    # print("%s%s" % ('func_file: ', func_file))
    # print("%s%s" % ('dwi_file: ', dwi_file))
    # print("%s%s" % ('fbval: ', fbval))
    # print("%s%s" % ('fbvec: ', fbvec))
    # print("%s%s" % ('anat_file: ', anat_file))
    # print("%s%s" % ('func_file_list: ', func_file_list))
    # print("%s%s" % ('dwi_file_list: ', dwi_file_list))
    # print("%s%s" % ('mask_list: ', mask_list))
    # print("%s%s" % ('fbvec_list: ', fbvec_list))
    # print("%s%s" % ('fbval_list: ', fbval_list))
    # print("%s%s" % ('conf_list: ', conf_list))
    # print("%s%s" % ('anat_file_list: ', anat_file_list))
    # print("%s%s" % ('extract_strategy: ', extract_strategy))
    # print("%s%s" % ('extract_strategy_list: ', extract_strategy_list))
    # print('\n\n\n\n\n')
    # import sys
    # sys.exit(0)

    # Import wf core and interfaces
    import warnings

    warnings.filterwarnings("ignore")
    from pynets.core.utils import collectpandasjoin
    from pynets.core.interfaces import CombineOutputs, NetworkAnalysis
    from nipype.pipeline import engine as pe
    from nipype.interfaces import utility as niu
    from pynets.core.workflows import workflow_selector

    def init_wf_single_subject(
        ID,
        func_file,
        atlas,
        network,
        node_size,
        roi,
        thr,
        uatlas,
        multi_nets,
        conn_model,
        dens_thresh,
        conf,
        plot_switch,
        dwi_file,
        multi_thr,
        multi_atlas,
        min_thr,
        max_thr,
        step_thr,
        anat_file,
        parc,
        ref_txt,
        procmem,
        k,
        clust_mask,
        k_list,
        k_clustering,
        user_atlas_list,
        clust_mask_list,
        prune,
        node_size_list,
        graph,
        conn_model_list,
        min_span_tree,
        verbose,
        plugin_type,
        use_parcel_naming,
        multi_graph,
        smooth,
        smooth_list,
        disp_filt,
        clust_type,
        clust_type_list,
        mask,
        norm,
        binary,
        fbval,
        fbvec,
        target_samples,
        curv_thr_list,
        step_list,
        track_type,
        min_length,
        maxcrossing,
        error_margin,
        directget,
        tiss_class,
        runtime_dict,
        execution_dict,
        embed,
        multi_directget,
        multimodal,
        hpass,
        hpass_list,
        vox_size,
        multiplex,
        waymask,
        local_corr,
        min_length_list,
        error_margin_list,
        extract_strategy,
        extract_strategy_list,
        outdir,
    ):
        """
        A function interface for generating a single-subject workflow.

        Parameters
        ----------
        ID : str
            A subject ID or other unique identifier
        func_file : str
            File path to a 4D Nifti1Image containing fMRI data
        atlas : str
            name of atlas parcellation used
        network : str
            Resting-state network based on Yeo-7 and Yeo-17 naming
            (e.g. 'Default') used to filter nodes in the study of brain
            subgraphs
        node_size : int
            spherical centroid node size in the case that coordinate-based
            centroids are used as ROI's
        roi : str
            File path to binarized/boolean region-of-interest Nifti1Image file
        thr : float
            A value, between 0 and 1, to threshold the graph using any variety
            of methods triggered through other options.
        multi_nets  list
            List of Yeo RSN's specified in workflow(s)
        conn_model : str
            Connectivity estimation model (e.g. corr for correlation, cov for
            covariance, sps for precision covariance, partcorr for partial
            correlation). sps type is used by default.
        dens_thresh : bool
            Indicates whether a target graph density is to be used as the basis
            for thresholding.
        conf : str
            File path to a confound regressor file for reduce noise in the
            time-series when extracting from ROI's.
        plot_switch : bool
            Activate summary plotting (histograms, ROC curves, etc.)
        dwi_file : str
            File path to diffusion weighted image.
        multi_thr :
        multi_atlas :
        min_thr : int
            If performing multi-thresholding, a minimum threshold
        max_thr : int
            If performing multi-thresholding, a maximum threshold
        step_thr : int
            If performing multi-thresholding, a threshold interval size
        anat_file :
        parc : bool
            Indicates whether to use parcels instead of coordinates as ROI nodes
        ref_txt :
        procmem :
        k : int
            Number of clusters that will be generated
        clust_mask : str
            File path to a 3D NIFTI file containing a mask, which restricts the
            voxels used in the clustering
        k_list :
        k_clustering :
        user_atlas_list :
        clust_mask_list :
        prune : bool
            Indicates whether to prune final graph of disconnected
            nodes/isolates.
        node_size_list :
        graph :
        conn_model_list :
        min_span_tree : bool
             Indicates whether local thresholding from the Minimum Spanning
             Tree should be used.
        verbose :
        plugin_type :
        use_parcel_naming :
        multi_graph :
        smooth : int
            Smoothing width (mm fwhm) to apply to time-series when extracting
            signal from ROI's.
        smooth_list :
        disp_filt : bool
            Indicates whether local thresholding using a disparity filter and
            'backbone network' should be used.
        clust_type : str
            Type of clustering to be performed (e.g. 'ward', 'kmeans',
            'complete', 'average')
        clust_type_list :
        mask : str
             File path to a 3D NIFTI file containing a mask, which restricts
             the voxels used in the analysis.
        norm : int
            Indicates method of normalizing resulting graph.
        binary : bool
            Indicates whether to binarize resulting graph edges to form an
            unweighted graph.
        fbval : number of items in the func_file
        fbvec :
        target_samples : int
            Total number of streamline samples specified to generate streams.
        curv_thr_list : list
            List of integer curvature thresholds used to perform ensemble
            tracking
        step_list : list
            List of float step-sizes used to perform ensemble tracking
        track_type : str
            Tracking algorithm used (e.g. 'local' or 'particle').
        min_length : int
            Minimum fiber length threshold in mm to restrict tracking.
        maxcrossing : int
            Maximum number if diffusion directions that can be assumed per voxel
        error_margin : int
            Euclidean margin of error for classifying a streamline as a
            connection to an ROI. Default is 2 voxels.
        directget : str
            The statistical approach to tracking. Options are:
            det (deterministic), closest (clos), boot (bootstrapped), and
            prob (probabilistic)
        tiss_class : str
            Tissue classification method
        runtime_dict :
        execution_dict :
            Nipype workflow global settings
        embed :
        multi_directget :
        multimodal : bool
            Indicates whether multiple modalities of input data have been
            specified.
        hpass : bool
             High-pass filter values (Hz) to apply to node-extracted time-series
        hpass_list :
        vox_size :
        multiplex :
        waymask :
        local_corr : str
             Type of local connectivity to use as the basis for clustering
             methods. Options are tcorr or scorr. Default is tcorr
        min_length_list :
        error_margin_list :
        extract_strategy : str
            The name of a valid function used to reduce the time-series region
            extraction
        extract_strategy_list :
        outdir : str
            Path to base derivatives directory

        """
        import warnings

        warnings.filterwarnings("ignore")
        from time import strftime

        if (func_file is not None) and (dwi_file is None):
            wf = pe.Workflow(
                name=f"wf_single_sub_{ID}_fmri_{strftime('%Y%m%d_%H%M%S')}"
            )
        elif (dwi_file is not None) and (func_file is None):
            wf = pe.Workflow(
                name=f"wf_single_sub_{ID}_dmri_{strftime('%Y%m%d_%H%M%S')}"
            )
        else:
            wf = pe.Workflow(
                name=f"wf_single_sub_{ID}_{strftime('%Y%m%d_%H%M%S')}")
        import_list = [
            "import sys",
            "import os",
            "import numpy as np",
            "import networkx as nx",
            "import nibabel as nib",
            "import warnings",
            'warnings.filterwarnings("ignore")',
            'np.warnings.filterwarnings("ignore")',
            'warnings.simplefilter("ignore")',
            "from pathlib import Path",
            "import yaml",
        ]
        inputnode = pe.Node(
            niu.IdentityInterface(
                fields=[
                    "ID",
                    "network",
                    "thr",
                    "node_size",
                    "roi",
                    "multi_nets",
                    "conn_model",
                    "plot_switch",
                    "graph",
                    "prune",
                    "norm",
                    "binary",
                    "multimodal",
                    "embed",
                ]
            ),
            name="inputnode",
            imports=import_list,
        )
        if verbose is True:
            from nipype import config, logging

            cfg_v = dict(
                logging={
                    "workflow_level": "INFO",
                    "utils_level": "INFO",
                    "log_to_file": False,
                    "interface_level": "DEBUG",
                    "filemanip_level": "DEBUG",
                }
            )
            logging.update_logging(config)
            config.update_config(cfg_v)
            config.enable_resource_monitor()

        execution_dict["crashdump_dir"] = str(wf.base_dir)
        execution_dict["plugin"] = str(plugin_type)
        cfg = dict(execution=execution_dict)
        for key in cfg.keys():
            for setting, value in cfg[key].items():
                wf.config[key][setting] = value

        inputnode.inputs.ID = ID
        inputnode.inputs.network = network
        inputnode.inputs.thr = thr
        inputnode.inputs.node_size = node_size
        inputnode.inputs.roi = roi
        inputnode.inputs.multi_nets = multi_nets
        inputnode.inputs.conn_model = conn_model
        inputnode.inputs.plot_switch = plot_switch
        inputnode.inputs.graph = graph
        inputnode.inputs.prune = prune
        inputnode.inputs.norm = norm
        inputnode.inputs.binary = binary
        inputnode.inputs.multimodal = multimodal
        inputnode.inputs.embed = embed

        if func_file or dwi_file:
            meta_wf = workflow_selector(
                func_file,
                ID,
                atlas,
                network,
                node_size,
                roi,
                thr,
                uatlas,
                multi_nets,
                conn_model,
                dens_thresh,
                conf,
                plot_switch,
                dwi_file,
                anat_file,
                parc,
                ref_txt,
                procmem,
                multi_thr,
                multi_atlas,
                max_thr,
                min_thr,
                step_thr,
                k,
                clust_mask,
                k_list,
                k_clustering,
                user_atlas_list,
                clust_mask_list,
                prune,
                node_size_list,
                conn_model_list,
                min_span_tree,
                verbose,
                plugin_type,
                use_parcel_naming,
                smooth,
                smooth_list,
                disp_filt,
                clust_type,
                clust_type_list,
                mask,
                norm,
                binary,
                fbval,
                fbvec,
                target_samples,
                curv_thr_list,
                step_list,
                track_type,
                min_length,
                maxcrossing,
                error_margin,
                directget,
                tiss_class,
                runtime_dict,
                execution_dict,
                embed,
                multi_directget,
                multimodal,
                hpass,
                hpass_list,
                vox_size,
                multiplex,
                waymask,
                local_corr,
                min_length_list,
                error_margin_list,
                extract_strategy,
                extract_strategy_list,
                outdir,
            )
            meta_wf._n_procs = procmem[0]
            meta_wf._mem_gb = procmem[1]
            meta_wf.n_procs = procmem[0]
            meta_wf.mem_gb = procmem[1]
            wf.add_nodes([meta_wf])

        # Set resource restrictions at level of the meta-meta wf
        if func_file:
            wf_selected = f"fmri_connectometry_{ID}"
            for node_name in (wf.get_node(meta_wf.name).get_node(
                    wf_selected).list_node_names()):
                if node_name in runtime_dict:
                    wf.get_node(meta_wf.name).get_node(wf_selected).get_node(
                        node_name
                    )._n_procs = runtime_dict[node_name][0]
                    wf.get_node(meta_wf.name).get_node(wf_selected).get_node(
                        node_name
                    )._mem_gb = runtime_dict[node_name][1]

        if dwi_file:
            wf_selected = f"dmri_connectometry_{ID}"
            for node_name in (wf.get_node(meta_wf.name).get_node(
                    wf_selected).list_node_names()):
                if node_name in runtime_dict:
                    wf.get_node(meta_wf.name).get_node(wf_selected).get_node(
                        node_name
                    )._n_procs = runtime_dict[node_name][0]
                    wf.get_node(meta_wf.name).get_node(wf_selected).get_node(
                        node_name
                    )._mem_gb = runtime_dict[node_name][1]

        if func_file or dwi_file:
            wf.get_node(meta_wf.name)._n_procs = procmem[0]
            wf.get_node(meta_wf.name)._mem_gb = procmem[1]
            wf.get_node(meta_wf.name).n_procs = procmem[0]
            wf.get_node(meta_wf.name).mem_gb = procmem[1]
            wf.get_node(meta_wf.name).get_node(
                wf_selected)._n_procs = procmem[0]
            wf.get_node(meta_wf.name).get_node(
                wf_selected)._mem_gb = procmem[1]
            wf.get_node(meta_wf.name).get_node(
                wf_selected).n_procs = procmem[0]
            wf.get_node(meta_wf.name).get_node(wf_selected).mem_gb = procmem[1]

        # Fully-automated graph analysis
        net_mets_node = pe.MapNode(
            interface=NetworkAnalysis(),
            name="NetworkAnalysis",
            iterfield=[
                "ID",
                "network",
                "thr",
                "conn_model",
                "est_path",
                "roi",
                "prune",
                "norm",
                "binary",
            ],
            nested=True,
            imports=import_list,
        )
        net_mets_node.synchronize = True
        net_mets_node._n_procs = runtime_dict["NetworkAnalysis"][0]
        net_mets_node._mem_gb = runtime_dict["NetworkAnalysis"][1]

        collect_pd_list_net_csv_node = pe.Node(
            niu.Function(
                input_names=["net_mets_csv"],
                output_names=["net_mets_csv_out"],
                function=collectpandasjoin,
            ),
            name="AggregateOutputs",
            imports=import_list,
        )
        collect_pd_list_net_csv_node._n_procs = \
            runtime_dict["AggregateOutputs"][0]
        collect_pd_list_net_csv_node._mem_gb = \
            runtime_dict["AggregateOutputs"][1]

        # Combine dataframes across models
        combine_pandas_dfs_node = pe.Node(
            interface=CombineOutputs(),
            name="CombineOutputs",
            imports=import_list)
        combine_pandas_dfs_node._n_procs = runtime_dict["CombineOutputs"][0]
        combine_pandas_dfs_node._mem_gb = runtime_dict["CombineOutputs"][1]

        final_outputnode = pe.Node(
            niu.IdentityInterface(fields=["combination_complete"]),
            name="final_outputnode",
        )

        # Raw graph case
        if graph or multi_graph:
            from pynets.core.workflows import raw_graph_workflow

            if multi_graph:
                print("Using multiple custom input graphs...")
                if op.basename(op.dirname(multi_graph[0])) == 'graphs':
                    if 'func' in op.dirname(multi_graph[0]):
                        outdir = f"{outdir}/func"
                    elif 'dwi' in op.dirname(multi_graph[0]):
                        outdir = f"{outdir}/dwi"
                conn_model_list = []
                i = 1
                for graph in multi_graph:
                    conn_model_list.append(str(i))
                    if op.basename(op.dirname(graph)) == 'graphs':
                        atlas = op.basename(op.dirname(op.dirname(graph)))
                        print(f"Parcellation Resolution detected: {atlas}")
                    else:
                        graph_name = op.basename(graph).split(
                            op.splitext(graph)[1])[0]
                        print(graph_name)
                        atlas = f"{graph_name}_{ID}"
                    do_dir_path(atlas, outdir)
                    i = i + 1
            else:
                if op.basename(op.dirname(graph)) == 'graphs':
                    atlas = op.basename(op.dirname(op.dirname(graph)))
                    print(f"Parcellation Resolution detected: {atlas}")
                    if 'func' in op.dirname(graph):
                        outdir = f"{outdir}/func"
                    elif 'dwi' in op.dirname(graph):
                        outdir = f"{outdir}/dwi"
                else:
                    graph_name = op.basename(graph
                                             ).split(op.splitext(graph)[1])[0]
                    print("Using single custom graph input...")
                    print(graph_name)
                    atlas = f"{graph_name}_{ID}"
                do_dir_path(atlas, outdir)
            wf = raw_graph_workflow(
                multi_thr,
                thr,
                multi_graph,
                graph,
                ID,
                network,
                conn_model,
                roi,
                prune,
                norm,
                binary,
                min_span_tree,
                dens_thresh,
                disp_filt,
                min_thr,
                max_thr,
                step_thr,
                wf,
                net_mets_node,
                runtime_dict
            )
        else:
            wf.connect(
                [
                    (
                        meta_wf.get_node("pass_meta_outs_node"),
                        net_mets_node,
                        [
                            ("est_path_iterlist", "est_path"),
                            ("network_iterlist", "network"),
                            ("thr_iterlist", "thr"),
                            ("ID_iterlist", "ID"),
                            ("conn_model_iterlist", "conn_model"),
                            ("roi_iterlist", "roi"),
                            ("prune_iterlist", "prune"),
                            ("norm_iterlist", "norm"),
                            ("binary_iterlist", "binary"),
                        ],
                    )
                ]
            )

        wf.connect(
            [
                (
                    inputnode,
                    combine_pandas_dfs_node,
                    [
                        ("network", "network"),
                        ("ID", "ID"),
                        ("plot_switch", "plot_switch"),
                        ("multi_nets", "multi_nets"),
                        ("multimodal", "multimodal"),
                        ("embed", "embed"),
                    ],
                ),
                (
                    net_mets_node,
                    collect_pd_list_net_csv_node,
                    [("out_path_neat", "net_mets_csv")],
                ),
                (
                    collect_pd_list_net_csv_node,
                    combine_pandas_dfs_node,
                    [("net_mets_csv_out", "net_mets_csv_list")],
                ),
                (
                    combine_pandas_dfs_node,
                    final_outputnode,
                    [("combination_complete", "combination_complete")],
                ),
            ]
        )
        return wf

    # Multi-subject pipeline
    def wf_multi_subject(
        ID,
        func_file_list,
        dwi_file_list,
        mask_list,
        fbvec_list,
        fbval_list,
        conf_list,
        anat_file_list,
        atlas,
        network,
        node_size,
        roi,
        thr,
        uatlas,
        multi_nets,
        conn_model,
        dens_thresh,
        conf,
        plot_switch,
        dwi_file,
        multi_thr,
        multi_atlas,
        min_thr,
        max_thr,
        step_thr,
        anat_file,
        parc,
        ref_txt,
        procmem,
        k,
        clust_mask,
        k_list,
        k_clustering,
        user_atlas_list,
        clust_mask_list,
        prune,
        node_size_list,
        conn_model_list,
        min_span_tree,
        verbose,
        plugin_type,
        use_parcel_naming,
        multi_subject_graph,
        multi_subject_multigraph,
        smooth,
        smooth_list,
        disp_filt,
        clust_type,
        clust_type_list,
        mask,
        norm,
        binary,
        fbval,
        fbvec,
        target_samples,
        curv_thr_list,
        step_list,
        track_type,
        min_length,
        maxcrossing,
        error_margin,
        directget,
        tiss_class,
        runtime_dict,
        execution_dict,
        embed,
        multi_directget,
        multimodal,
        hpass,
        hpass_list,
        vox_size,
        multiplex,
        waymask,
        local_corr,
        min_length_list,
        error_margin_list,
        extract_strategy,
        extract_strategy_list,
        outdir,
    ):
        """
        A function interface for generating multiple single-subject
        workflows -- i.e. a 'multi-subject' workflow

        Parameters
        ----------

        ID : str
            A subject ID or other unique identifier
        func_file_list : str
            List of file paths to 4D Nifti1Images containing fMRI data
        dwi_file_list,
        mask_list,
        fbvec_list,
        fbval_list,
        conf_list,
        anat_file_list,
        atlas : str
            name of atlas parcellation used
        network : str
            Resting-state network based on Yeo-7 and Yeo-17 naming
            (e.g. 'Default') used to filter nodes in the study of brain subgraphs
        node_size : int
            spherical centroid node size in the case that coordinate-based
            centroids are used as ROI's
        roi : str
            File path to binarized/boolean region-of-interest Nifti1Image file
        thr : float
            A value, between 0 and 1, to threshold the graph using any variety
            of methods triggered through other options
        uatlas,
        multi_nets : list
            List of Yeo RSN's specified in workflow(s)
        conn_model : str
            Connectivity estimation model (e.g. corr for correlation, cov for
            covariance, sps for precision covariance, partcorr for partial
            correlation). sps type is used by default
        dens_thresh : bool
            Indicates whether a target graph density is to be used as the basis
            for thresholding
        conf : str
            File path to a confound regressor file for reduce noise in the
            time-series when extracting from ROI's
        plot_switch : bool
            Activate summary plotting (histograms, ROC curves, etc.)
        dwi_file : str
            File path to diffusion weighted image
        multi_thr,
        multi_atlas,
        min_thr,
        max_thr,
        step_thr,
        anat_file,
        parc : bool
            Indicates whether to use parcels instead of coordinates as ROI nodes
        ref_txt,
        procmem,
        k : int
            Number of clusters that will be generated
        clust_mask : str
            File path to a 3D NIFTI file containing a mask, which restricts the
            voxels used in the clustering
        k_list,
        k_clustering,
        user_atlas_list,
        clust_mask_list,
        prune : bool
            Indicates whether to prune final graph of disconnected
            nodes/isolates
        node_size_list,
        conn_model_list,
        min_span_tree : bool
             Indicates whether local thresholding from the Minimum Spanning
             Tree should be used
        verbose,
        plugin_type,
        use_parcel_naming,
        multi_subject_graph,
        multi_subject_multigraph,
        smooth : int
            Smoothing width (mm fwhm) to apply to time-series when extracting
            signal from ROI's
        smooth_list,
        disp_filt : bool
            Indicates whether local thresholding using a disparity filter and
            'backbone network' should be used
        clust_type : str
            Type of clustering to be performed (e.g. 'ward', 'kmeans',
            'complete', 'average')
        clust_type_list,
        mask : str
             File path to a 3D NIFTI file containing a mask, which restricts
             the voxels used in the analysis
        norm : int
            Indicates method of normalizing resulting graph
        binary : bool
            Indicates whether to binarize resulting graph edges to form an
            unweighted graph
        fbval,
        fbvec,
        target_samples : int
            Total number of streamline samples specified to generate streams
        curv_thr_list : list
            List of integer curvature thresholds used to perform ensemble
            tracking
        step_list : list
            List of float step-sizes used to perform ensemble tracking
        track_type : str
            Tracking algorithm used (e.g. 'local' or 'particle'
        min_length : int
            Minimum fiber length threshold in mm to restrict tracking
        maxcrossing : int
            Maximum number if diffusion directions that can be assumed per voxel
        error_margin : int
            Euclidean margin of error for classifying a streamline as a
            connection to an ROI. Default is 2 voxels
        directget : str
            The statistical approach to tracking. Options are:
            det (deterministic), closest (clos), boot (bootstrapped), and
            prob (probabilistic)
        tiss_class : str
            Tissue classification method
        runtime_dict,
        execution_dict :
            Nipype workflow global settings
        embed,
        multi_directget,
        multimodal : bool
            Indicates whether multiple modalities of input data have been
            specified
        hpass : bool
             High-pass filter values (Hz) to apply to node-extracted time-series
        hpass_list,
        vox_size,
        multiplex,
        waymask,
        local_corr : str
             Type of local connectivity to use as the basis for clustering
             methods. Options are tcorr or scorr. Default is tcorr
        min_length_list,
        error_margin_list,
        extract_strategy : str
            The name of a valid function used to reduce the time-series region
            extraction
        extract_strategy_list,
        outdir : str
            Path to base derivatives directory

        """
        import warnings

        warnings.filterwarnings("ignore")
        from time import strftime

        wf_multi = pe.Workflow(name=f"wf_multisub_{strftime('%Y%m%d_%H%M%S')}")

        if not multi_subject_graph and not multi_subject_multigraph:
            if (func_file_list is None) and dwi_file_list:
                func_file_list = len(dwi_file_list) * [None]
                conf_list = len(dwi_file_list) * [None]

            if (dwi_file_list is None) and func_file_list:
                dwi_file_list = len(func_file_list) * [None]
                fbvec_list = len(func_file_list) * [None]
                fbval_list = len(func_file_list) * [None]

            i = 0
            dir_list = []
            for dwi_file, func_file in zip(dwi_file_list, func_file_list):
                if conf_list and func_file:
                    conf_sub = conf_list[i]
                else:
                    conf_sub = None
                if fbval_list and dwi_file:
                    fbval_sub = fbval_list[i]
                else:
                    fbval_sub = None
                if fbvec_list and dwi_file:
                    fbvec_sub = fbvec_list[i]
                else:
                    fbvec_sub = None
                if mask_list:
                    mask_sub = mask_list[i]
                else:
                    mask_sub = None
                if anat_file_list:
                    anat_file = anat_file_list[i]
                else:
                    anat_file = None

                try:
                    subj_dir = (
                        f"{outdir}/sub-{ID[i].split('_')[0]}/"
                        f"ses-{ID[i].split('_')[1]}"
                    )
                except BaseException:
                    subj_dir = f"{outdir}/{ID[i]}"
                os.makedirs(subj_dir, exist_ok=True)
                dir_list.append(subj_dir)

                wf_single_subject = init_wf_single_subject(
                    ID=ID[i],
                    func_file=func_file,
                    atlas=atlas,
                    network=network,
                    node_size=node_size,
                    roi=roi,
                    thr=thr,
                    uatlas=uatlas,
                    multi_nets=multi_nets,
                    conn_model=conn_model,
                    dens_thresh=dens_thresh,
                    conf=conf_sub,
                    plot_switch=plot_switch,
                    dwi_file=dwi_file,
                    multi_thr=multi_thr,
                    multi_atlas=multi_atlas,
                    min_thr=min_thr,
                    max_thr=max_thr,
                    step_thr=step_thr,
                    anat_file=anat_file,
                    parc=parc,
                    ref_txt=ref_txt,
                    procmem=procmem,
                    k=k,
                    clust_mask=clust_mask,
                    k_list=k_list,
                    k_clustering=k_clustering,
                    user_atlas_list=user_atlas_list,
                    clust_mask_list=clust_mask_list,
                    prune=prune,
                    node_size_list=node_size_list,
                    graph=None,
                    conn_model_list=conn_model_list,
                    min_span_tree=min_span_tree,
                    verbose=verbose,
                    plugin_type=plugin_type,
                    use_parcel_naming=use_parcel_naming,
                    multi_graph=None,
                    smooth=smooth,
                    smooth_list=smooth_list,
                    disp_filt=disp_filt,
                    clust_type=clust_type,
                    clust_type_list=clust_type_list,
                    mask=mask_sub,
                    norm=norm,
                    binary=binary,
                    fbval=fbval_sub,
                    fbvec=fbvec_sub,
                    target_samples=target_samples,
                    curv_thr_list=curv_thr_list,
                    step_list=step_list,
                    track_type=track_type,
                    min_length=min_length,
                    maxcrossing=maxcrossing,
                    error_margin=error_margin,
                    directget=directget,
                    tiss_class=tiss_class,
                    runtime_dict=runtime_dict,
                    execution_dict=execution_dict,
                    embed=embed,
                    multi_directget=multi_directget,
                    multimodal=multimodal,
                    hpass=hpass,
                    hpass_list=hpass_list,
                    vox_size=vox_size,
                    multiplex=multiplex,
                    waymask=waymask,
                    local_corr=local_corr,
                    min_length_list=min_length_list,
                    error_margin_list=error_margin_list,
                    extract_strategy=extract_strategy,
                    extract_strategy_list=extract_strategy_list,
                    outdir=subj_dir,
                )
                wf_single_subject._n_procs = procmem[0]
                wf_single_subject._mem_gb = procmem[1]
                wf_single_subject.n_procs = procmem[0]
                wf_single_subject.mem_gb = procmem[1]
                wf_multi.add_nodes([wf_single_subject])
                wf_multi.get_node(wf_single_subject.name)._n_procs = procmem[0]
                wf_multi.get_node(wf_single_subject.name)._mem_gb = procmem[1]
                wf_multi.get_node(wf_single_subject.name).n_procs = procmem[0]
                wf_multi.get_node(wf_single_subject.name).mem_gb = procmem[1]
                i = i + 1
        else:
            i = 0
            dir_list = []
            if multi_subject_graph:
                multi_subject_graph_iter = multi_subject_graph
            elif multi_subject_multigraph:
                multi_subject_graph_iter = multi_subject_multigraph

            for graph_iter in multi_subject_graph_iter:
                conf_sub = None
                fbval_sub = None
                fbvec_sub = None
                mask_sub = None
                anat_file = None
                dwi_file = None
                func_file = None

                if any(isinstance(i, list) for i in graph_iter):
                    graph = None
                    multi_graph = graph_iter[i]
                else:
                    graph = graph_iter[i]
                    multi_graph = None

                try:
                    subj_dir = (
                        f"{outdir}/sub-{ID[i].split('_')[0]}/"
                        f"ses-{ID[i].split('_')[1]}"
                    )
                except BaseException:
                    subj_dir = f"{outdir}/{ID[i]}"
                os.makedirs(subj_dir, exist_ok=True)
                dir_list.append(subj_dir)

                wf_single_subject = init_wf_single_subject(
                    ID=ID[i],
                    func_file=func_file,
                    atlas=atlas,
                    network=network,
                    node_size=node_size,
                    roi=roi,
                    thr=thr,
                    uatlas=uatlas,
                    multi_nets=multi_nets,
                    conn_model=conn_model,
                    dens_thresh=dens_thresh,
                    conf=conf_sub,
                    plot_switch=plot_switch,
                    dwi_file=dwi_file,
                    multi_thr=multi_thr,
                    multi_atlas=multi_atlas,
                    min_thr=min_thr,
                    max_thr=max_thr,
                    step_thr=step_thr,
                    anat_file=anat_file,
                    parc=parc,
                    ref_txt=ref_txt,
                    procmem=procmem,
                    k=k,
                    clust_mask=clust_mask,
                    k_list=k_list,
                    k_clustering=k_clustering,
                    user_atlas_list=user_atlas_list,
                    clust_mask_list=clust_mask_list,
                    prune=prune,
                    node_size_list=node_size_list,
                    graph=graph,
                    conn_model_list=conn_model_list,
                    min_span_tree=min_span_tree,
                    verbose=verbose,
                    plugin_type=plugin_type,
                    use_parcel_naming=use_parcel_naming,
                    multi_graph=multi_graph,
                    smooth=smooth,
                    smooth_list=smooth_list,
                    disp_filt=disp_filt,
                    clust_type=clust_type,
                    clust_type_list=clust_type_list,
                    mask=mask_sub,
                    norm=norm,
                    binary=binary,
                    fbval=fbval_sub,
                    fbvec=fbvec_sub,
                    target_samples=target_samples,
                    curv_thr_list=curv_thr_list,
                    step_list=step_list,
                    track_type=track_type,
                    min_length=min_length,
                    maxcrossing=maxcrossing,
                    error_margin=error_margin,
                    directget=directget,
                    tiss_class=tiss_class,
                    runtime_dict=runtime_dict,
                    execution_dict=execution_dict,
                    embed=embed,
                    multi_directget=multi_directget,
                    multimodal=multimodal,
                    hpass=hpass,
                    hpass_list=hpass_list,
                    vox_size=vox_size,
                    multiplex=multiplex,
                    waymask=waymask,
                    local_corr=local_corr,
                    min_length_list=min_length_list,
                    error_margin_list=error_margin_list,
                    extract_strategy=extract_strategy,
                    extract_strategy_list=extract_strategy_list,
                    outdir=subj_dir,
                )
                wf_single_subject._n_procs = procmem[0]
                wf_single_subject._mem_gb = procmem[1]
                wf_single_subject.n_procs = procmem[0]
                wf_single_subject.mem_gb = procmem[1]
                wf_multi.add_nodes([wf_single_subject])
                wf_multi.get_node(wf_single_subject.name)._n_procs = procmem[0]
                wf_multi.get_node(wf_single_subject.name)._mem_gb = procmem[1]
                wf_multi.get_node(wf_single_subject.name).n_procs = procmem[0]
                wf_multi.get_node(wf_single_subject.name).mem_gb = procmem[1]
                i = i + 1

            # Restrict nested meta-meta wf resources at the level of the group
            # wf
            wf_multi.get_node(wf_single_subject.name).get_node(
                "NetworkAnalysis"
            )._n_procs = 1
            wf_multi.get_node(wf_single_subject.name).get_node(
                "NetworkAnalysis"
            )._mem_gb = 4
            wf_multi.get_node(wf_single_subject.name).get_node(
                "CombineOutputs"
            )._n_procs = 1
            wf_multi.get_node(wf_single_subject.name).get_node(
                "CombineOutputs"
            )._mem_gb = 2

        return wf_multi, dir_list

    # Workflow generation
    # Multi-subject workflow generator
    if (
        (func_file_list or dwi_file_list)
        or (func_file_list and dwi_file_list)
        or multi_subject_graph
        or multi_subject_multigraph
    ):
        wf_multi, dir_list = wf_multi_subject(
            ID,
            func_file_list,
            dwi_file_list,
            mask_list,
            fbvec_list,
            fbval_list,
            conf_list,
            anat_file_list,
            atlas,
            network,
            node_size,
            roi,
            thr,
            uatlas,
            multi_nets,
            conn_model,
            dens_thresh,
            conf,
            plot_switch,
            dwi_file,
            multi_thr,
            multi_atlas,
            min_thr,
            max_thr,
            step_thr,
            anat_file,
            parc,
            ref_txt,
            procmem,
            k,
            clust_mask,
            k_list,
            k_clustering,
            user_atlas_list,
            clust_mask_list,
            prune,
            node_size_list,
            conn_model_list,
            min_span_tree,
            verbose,
            plugin_type,
            use_parcel_naming,
            multi_subject_graph,
            multi_subject_multigraph,
            smooth,
            smooth_list,
            disp_filt,
            clust_type,
            clust_type_list,
            mask,
            norm,
            binary,
            fbval,
            fbvec,
            target_samples,
            curv_thr_list,
            step_list,
            track_type,
            min_length,
            maxcrossing,
            error_margin,
            directget,
            tiss_class,
            runtime_dict,
            execution_dict,
            embed,
            multi_directget,
            multimodal,
            hpass,
            hpass_list,
            vox_size,
            multiplex,
            waymask,
            local_corr,
            min_length_list,
            error_margin_list,
            extract_strategy,
            extract_strategy_list,
            outdir,
        )

        os.makedirs(
            f"{work_dir}/wf_multi_subject_{'_'.join(ID)}",
            exist_ok=True)
        wf_multi.base_dir = f"{work_dir}/wf_multi_subject_{'_'.join(ID)}"
        retval["run_uuid"] = 'GROUP'

        if verbose is True:
            import logging
            from nipype import config, logging as lg
            from nipype.utils.profiler import log_nodes_cb

            cfg_v = dict(
                logging={
                    "workflow_level": "INFO",
                    "utils_level": "INFO",
                    "interface_level": "DEBUG",
                    "filemanip_level": "DEBUG",
                    "log_directory": str(wf_multi.base_dir),
                    "log_to_file": True,
                },
                monitoring={
                    "enabled": True,
                    "sample_frequency": "0.1",
                    "summary_append": True,
                    "summary_file": str(wf_multi.base_dir),
                },
            )
            lg.update_logging(config)
            config.update_config(cfg_v)
            config.enable_resource_monitor()
            callback_log_path = f"{wf_multi.base_dir}/run_stats.log"
            logger = logging.getLogger("callback")
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(callback_log_path)
            logger.addHandler(handler)
            plugin_args = {
                "n_procs": int(procmem[0]),
                "memory_gb": int(procmem[1]),
                "status_callback": log_nodes_cb,
                "scheduler": "mem_thread",
            }
        else:
            plugin_args = {
                "n_procs": int(procmem[0]),
                "memory_gb": int(procmem[1]),
                "scheduler": "mem_thread",
            }

        execution_dict["crashdump_dir"] = str(wf_multi.base_dir)
        execution_dict["plugin"] = str(plugin_type)
        cfg = dict(execution=execution_dict)
        for key in cfg.keys():
            for setting, value in cfg[key].items():
                wf_multi.config[key][setting] = value
        try:
            wf_multi.write_graph(graph2use="colored", format="png")
        except BaseException:
            pass

        print(f"Running with {str(plugin_args)}\n")
        retval["execution_dict"] = execution_dict
        retval["plugin_settings"] = plugin_args
        retval["workflow"] = wf_multi
        wf_multi.run(plugin=plugin_type, plugin_args=plugin_args)
        retval["return_code"] = 0
        if verbose is True:
            from nipype.utils.draw_gantt_chart import generate_gantt_chart

            if os.path.isfile(callback_log_path):
                print("Plotting resource profile from run...")
                generate_gantt_chart(callback_log_path, cores=int(procmem[0]))
                handler.close()
                logger.removeHandler(handler)
            else:
                print(f"Cannot plot resource usage. {callback_log_path} not "
                      f"found...")

        # Clean up temporary directories
        print("Cleaning up...")
        import shutil
        for dir in dir_list:
            if "func" in dir:
                for cnfnd_tmp_dir in glob.glob(f"{dir}/*/confounds_tmp"):
                    shutil.rmtree(cnfnd_tmp_dir)
                shutil.rmtree(f"{dir}/reg_fmri", ignore_errors=True)
                for file_ in [i for i in glob.glob(
                        f"{dir}/func/*") if os.path.isfile(i)]:
                    if ("reor-RAS" in file_) or ("res-" in file_):
                        try:
                            os.remove(file_)
                        except BaseException:
                            continue
            if "dwi" in dir:
                shutil.rmtree(f"{dir}/dmri_tmp", ignore_errors=True)
                shutil.rmtree(f"{dir}/reg_dmri", ignore_errors=True)
                for file_ in [i for i in glob.glob(
                        f"{dir}/dwi/*") if os.path.isfile(i)]:
                    if ("reor-RAS" in file_) or ("res-" in file_):
                        try:
                            os.remove(file_)
                        except BaseException:
                            continue

    # Single-subject workflow generator
    else:
        try:
            subj_dir = f"{outdir}/sub-{ID.split('_')[0]}/" \
                       f"ses-{ID.split('_')[1]}"
        except BaseException:
            subj_dir = f"{outdir}/{ID}"
        os.makedirs(subj_dir, exist_ok=True)

        # Single-subject pipeline
        wf = init_wf_single_subject(
            ID,
            func_file,
            atlas,
            network,
            node_size,
            roi,
            thr,
            uatlas,
            multi_nets,
            conn_model,
            dens_thresh,
            conf,
            plot_switch,
            dwi_file,
            multi_thr,
            multi_atlas,
            min_thr,
            max_thr,
            step_thr,
            anat_file,
            parc,
            ref_txt,
            procmem,
            k,
            clust_mask,
            k_list,
            k_clustering,
            user_atlas_list,
            clust_mask_list,
            prune,
            node_size_list,
            graph,
            conn_model_list,
            min_span_tree,
            verbose,
            plugin_type,
            use_parcel_naming,
            multi_graph,
            smooth,
            smooth_list,
            disp_filt,
            clust_type,
            clust_type_list,
            mask,
            norm,
            binary,
            fbval,
            fbvec,
            target_samples,
            curv_thr_list,
            step_list,
            track_type,
            min_length,
            maxcrossing,
            error_margin,
            directget,
            tiss_class,
            runtime_dict,
            execution_dict,
            embed,
            multi_directget,
            multimodal,
            hpass,
            hpass_list,
            vox_size,
            multiplex,
            waymask,
            local_corr,
            min_length_list,
            error_margin_list,
            extract_strategy,
            extract_strategy_list,
            subj_dir,
        )
        import warnings

        warnings.filterwarnings("ignore")
        import shutil
        import os
        import uuid
        from time import strftime

        if (func_file is not None) and (dwi_file is None):
            base_dirname = f"wf_single_subject_fmri_{str(ID)}"
        elif (dwi_file is not None) and (func_file is None):
            base_dirname = f"wf_single_subject_dmri_{str(ID)}"
        else:
            base_dirname = f"wf_single_subject_{str(ID)}"

        run_uuid = f"{strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
        retval["run_uuid"] = run_uuid

        os.makedirs(
            f"{work_dir}/{ID}_{run_uuid}_{base_dirname}",
            exist_ok=True)
        wf.base_dir = f"{work_dir}/{ID}_{run_uuid}_{base_dirname}"

        if verbose is True:
            import logging
            from nipype import config, logging as lg
            from nipype.utils.profiler import log_nodes_cb

            cfg_v = dict(
                logging={
                    "workflow_level": "INFO",
                    "utils_level": "INFO",
                    "interface_level": "DEBUG",
                    "filemanip_level": "DEBUG",
                    "log_directory": str(wf.base_dir),
                    "log_to_file": True,
                },
                monitoring={
                    "enabled": True,
                    "sample_frequency": "0.1",
                    "summary_append": True,
                    "summary_file": str(wf.base_dir),
                },
            )
            lg.update_logging(config)
            config.update_config(cfg_v)
            config.enable_resource_monitor()
            callback_log_path = f"{wf.base_dir}/run_stats.log"
            logger = logging.getLogger("callback")
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(callback_log_path)
            logger.addHandler(handler)

            plugin_args = {
                "n_procs": int(procmem[0]),
                "memory_gb": int(procmem[1]),
                "status_callback": log_nodes_cb,
                "scheduler": "mem_thread",
            }
        else:
            plugin_args = {
                "n_procs": int(procmem[0]),
                "memory_gb": int(procmem[1]),
                "scheduler": "mem_thread",
            }
        execution_dict["crashdump_dir"] = str(wf.base_dir)
        execution_dict["plugin"] = str(plugin_type)
        cfg = dict(execution=execution_dict)
        for key in cfg.keys():
            for setting, value in cfg[key].items():
                wf.config[key][setting] = value
        try:
            wf.write_graph(graph2use="colored", format="png")
        except BaseException:
            pass

        print(f"Running with {str(plugin_args)}\n")
        retval["execution_dict"] = execution_dict
        retval["plugin_settings"] = plugin_args
        retval["workflow"] = wf
        try:
            wf.run(plugin=plugin_type, plugin_args=plugin_args)
            retval["return_code"] = 0
        except RuntimeError as e:
            print(e)
            retval["return_code"] = 1
            return retval

        if verbose is True:
            from nipype.utils.draw_gantt_chart import generate_gantt_chart

            if os.path.isfile(callback_log_path):
                print("Plotting resource profile from run...")
                generate_gantt_chart(callback_log_path, cores=int(procmem[0]))
                handler.close()
                logger.removeHandler(handler)
            else:
                print(f"Cannot plot resource usage. {callback_log_path} not "
                      f"found...")
        # Clean up temporary directories
        print("Cleaning up...")
        if func_file:
            for file_ in [i for i in glob.glob(
                    f"{subj_dir}/func/*") if os.path.isfile(i)] + \
                [i for i in glob.glob(
                    f"{subj_dir}/func/*/*") if os.path.isfile(i)]:
                if ("reor-RAS" in file_) or ("res-" in file_):
                    try:
                        os.remove(file_)
                    except BaseException:
                        continue
        if dwi_file:
            for file_ in [i for i in glob.glob(
                    f"{subj_dir}/dwi/*") if os.path.isfile(i)] + \
                [i for i in glob.glob(
                    f"{subj_dir}/dwi/*/*") if os.path.isfile(i)]:
                if ("reor-RAS" in file_) or ("res-" in file_) or \
                   ("_bvecs_reor.bvec" in file_):
                    try:
                        os.remove(file_)
                    except BaseException:
                        continue

    print("\n\n------------FINISHED-----------")
    print("Subject: ", ID)
    print(
        "Execution Time: ", str(
            timedelta(
                seconds=timeit.default_timer() - start_time)))
    print("-------------------------------")
    return retval


def main():
    """Initializes main script from command-line call to generate
    single-subject or multi-subject workflow(s)"""
    import gc
    import sys
    import multiprocessing as mp
    import warnings
    warnings.filterwarnings("ignore")

    try:
        import pynets
    except ImportError:
        print(
            "PyNets not installed! Ensure that you are referencing the correct"
            " site-packages and using Python3.6+"
        )
        return 1

    if len(sys.argv) < 1:
        print("\nMissing command-line inputs! See help options with the -h"
              " flag.\n")
        return 1

    args = get_parser().parse_args()

    mp.set_start_method("forkserver")
    with mp.Manager() as mgr:
        retval = mgr.dict()
        p = mp.Process(target=build_workflow, args=(args, retval))
        p.start()
        p.join()

        retcode = p.exitcode or retval.get("return_code", 0)

        pynets_wf = retval.get("workflow", None)
        work_dir = retval.get("work_dir")
        plugin_settings = retval.get("plugin_settings", None)
        execution_dict = retval.get("execution_dict", None)
        run_uuid = retval.get("run_uuid", None)

        retcode = retcode or int(pynets_wf is None)

    if p.is_alive():
        p.terminate()
    mgr.shutdown()
    gc.collect()
    if args.noclean is False and work_dir:
        from shutil import rmtree

        rmtree(work_dir, ignore_errors=True)

    return retcode


if __name__ == "__main__":
    from pynets.core.utils import watchdog
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen" \
               "_importlib.BuiltinImporter'>)"

    sys.exit(watchdog().run())

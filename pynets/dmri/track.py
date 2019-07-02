# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:40:07 2017
Copyright (C) 2018
@author: Derek Pisner (dPys)
"""
import numpy as np
import nibabel as nib
import warnings
warnings.filterwarnings("ignore")


def reconstruction(conn_model, gtab, dwi_file, wm_in_dwi):
    '''
    Estimate a tensor model from dwi data.

    Parameters
    ----------
    conn_model : str
        Connectivity reconstruction method (e.g. 'csa', 'tensor', 'csd').
    gtab : Obj
        DiPy object storing diffusion gradient information.
    dwi_file : str
        File path to diffusion weighted image.
    wm_in_dwi : str
        File path to white-matter tissue segmentation Nifti1Image.

    Returns
    -------
    mod : obj
        Connectivity reconstruction model.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    try:
        import cPickle as pickle
    except ImportError:
        import _pickle as pickle
    from pynets.dmri.estimation import tens_mod_est, csa_mod_est, csd_mod_est
    dwi_img = nib.load(dwi_file)
    data = dwi_img.get_fdata()
    if conn_model == 'tensor':
        mod = tens_mod_est(gtab, data, wm_in_dwi)
    elif conn_model == 'csa':
        mod = csa_mod_est(gtab, data, wm_in_dwi)
    elif conn_model == 'csd':
        mod = csd_mod_est(gtab, data, wm_in_dwi)
    else:
        raise ValueError('Error: Either no seeds supplied, or no valid seeds found in white-matter interface')

    return mod


def prep_tissues(B0_mask, gm_in_dwi, vent_csf_in_dwi, wm_in_dwi, tiss_class, cmc_step_size=0.2):
    '''
    Estimate a tissue classifier for tractography.

    Parameters
    ----------
    B0_mask : str
        File path to B0 brain mask.
    gm_in_dwi : str
        File path to grey-matter tissue segmentation Nifti1Image.
    vent_csf_in_dwi : str
        File path to ventricular CSF tissue segmentation Nifti1Image.
    wm_in_dwi : str
        File path to white-matter tissue segmentation Nifti1Image.
    tiss_class : str
        Tissue classification method.
    cmc_step_size : float
        Step size from CMC tissue classification method.

    Returns
    -------
    tiss_classifier : obj
        Tissue classifier object.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    try:
        import cPickle as pickle
    except ImportError:
        import _pickle as pickle
    from dipy.tracking.local import ActTissueClassifier, CmcTissueClassifier, BinaryTissueClassifier
    # Loads mask and ensures it's a true binary mask
    mask_img = nib.load(B0_mask)
    # Load tissue maps and prepare tissue classifier
    gm_mask = nib.load(gm_in_dwi)
    gm_mask_data = gm_mask.get_fdata()
    wm_mask = nib.load(wm_in_dwi)
    wm_mask_data = wm_mask.get_fdata()
    if tiss_class == 'act':
        vent_csf_in_dwi = nib.load(vent_csf_in_dwi)
        vent_csf_in_dwi_data = vent_csf_in_dwi.get_fdata()
        background = np.ones(mask_img.shape)
        background[(gm_mask_data + wm_mask_data + vent_csf_in_dwi_data) > 0] = 0
        include_map = gm_mask_data
        include_map[background > 0] = 1
        exclude_map = vent_csf_in_dwi_data
        tiss_classifier = ActTissueClassifier(include_map, exclude_map)
    elif tiss_class == 'bin':
        wm_in_dwi_data = nib.load(wm_in_dwi).get_fdata().astype('bool')
        tiss_classifier = BinaryTissueClassifier(wm_in_dwi_data)
    elif tiss_class == 'cmc':
        vent_csf_in_dwi = nib.load(vent_csf_in_dwi)
        vent_csf_in_dwi_data = vent_csf_in_dwi.get_fdata()
        voxel_size = np.average(wm_mask.get_header()['pixdim'][1:4])
        tiss_classifier = CmcTissueClassifier.from_pve(wm_mask_data, gm_mask_data, vent_csf_in_dwi_data,
                                                       step_size=cmc_step_size, average_voxel_size=voxel_size)
    else:
        B0_mask_data = nib.load(B0_mask).get_fdata().astype('bool')
        tiss_classifier = BinaryTissueClassifier(B0_mask_data)

    return tiss_classifier


def run_LIFE_all(data, gtab, streamlines):
    '''
    Filters tractography streamlines using Linear Fascicle Evaluation (LiFE).

    Parameters
    ----------
    data : array
        4D numpy array of diffusion image data.
    gtab : Obj
        DiPy object storing diffusion gradient information.
    streamlines : ArraySequence
        DiPy list/array-like object of streamline points from tractography.

    Returns
    -------
    streamlines_filt : ArraySequence
        DiPy list/array-like object of filtered streamline fibers with positive beta-coefficients
        after fitting LiFE model.
    mean_rmse : float
        Root Mean-Squared Error (RMSE) when using LiFE-filtered fibers to predict diffusion data.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    import dipy.tracking.life as life
    import dipy.core.optimize as opt
    fiber_model = life.FiberModel(gtab)
    fiber_fit = fiber_model.fit(data, streamlines, affine=np.eye(4))
    streamlines_filt = list(np.array(streamlines)[np.where(fiber_fit.beta > 0)[0]])
    beta_baseline = np.zeros(fiber_fit.beta.shape[0])
    pred_weighted = np.reshape(opt.spdot(fiber_fit.life_matrix, beta_baseline),
                               (fiber_fit.vox_coords.shape[0], np.sum(~gtab.b0s_mask)))
    mean_pred = np.empty((fiber_fit.vox_coords.shape[0], gtab.bvals.shape[0]))
    S0 = fiber_fit.b0_signal
    mean_pred[..., gtab.b0s_mask] = S0[:, None]
    mean_pred[..., ~gtab.b0s_mask] = (pred_weighted + fiber_fit.mean_signal[:, None]) * S0[:, None]
    mean_error = mean_pred - fiber_fit.data
    mean_rmse = np.sqrt(np.mean(mean_error ** 2, -1))
    return streamlines_filt, mean_rmse


def save_streams(dwi_img, streamlines, streams):
    '''
    Save streamlines as .trk file with DTK-compatible trackvis header.

    Parameters
    ----------
    dwi_img : Nifti1Image
        File path to diffusion weighted Nifti1Image.
    streamlines : ArraySequence
        DiPy list/array-like object of streamline points from tractography.
    streams : str
        File path to save streamline array sequence in .trk format.

    Returns
    -------
    streams : str
        File path to saved streamline array sequence in DTK-compatible trackvis (.trk) format.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    hdr = dwi_img.header

    # Save streamlines
    trk_affine = np.eye(4)
    trk_hdr = nib.streamlines.trk.TrkFile.create_empty_header()
    trk_hdr['hdr_size'] = 1000
    trk_hdr['dimensions'] = hdr['dim'][1:4].astype('float32')
    trk_hdr['voxel_sizes'] = hdr['pixdim'][1:4]
    trk_hdr['voxel_to_rasmm'] = trk_affine
    trk_hdr['voxel_order'] = 'LPS'
    trk_hdr['pad2'] = 'LPS'
    trk_hdr['image_orientation_patient'] = np.array([1., 0., 0., 0., 1., 0.]).astype('float32')
    trk_hdr['endianness'] = '<'
    trk_hdr['_offset_data'] = 1000
    trk_hdr['nb_streamlines'] = len(streamlines)
    tractogram = nib.streamlines.Tractogram(streamlines, affine_to_rasmm=trk_affine)
    trkfile = nib.streamlines.trk.TrkFile(tractogram, header=trk_hdr)
    nib.streamlines.save(trkfile, streams)
    return streams


def filter_streamlines(dwi_file, dir_path, gtab, streamlines, life_run, min_length, conn_model, target_samples,
                       node_size, curv_thr_list, step_list, network, roi):
    '''
    Perform various routines for reducing false-positive streamlines from tractography.

    Parameters
    ----------
    dwi_file : str
        File path to diffusion weighted image.
    dir_path : str
        Path to directory containing subject derivative data for a given pynets run.
    gtab : Obj
        DiPy object storing diffusion gradient information.
    streamlines : ArraySequence
        DiPy list/array-like object of streamline points from tractography.
    life_run : bool
        Indicates whether to perform Linear Fascicle Evaluation (LiFE).
    min_length : int
        Minimum fiber length threshold in mm.
    conn_model : str
        Connectivity reconstruction method (e.g. 'csa', 'tensor', 'csd').
    target_samples : int
        Total number of streamline samples specified to generate streams.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    curv_thr_list : list
        List of integer curvature thresholds used to perform ensemble tracking.
    step_list : list
        List of float step-sizes used to perform ensemble tracking.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default')
        used to filter nodes in the study of brain subgraphs.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.

    Returns
    -------
    streams : str
        File path to saved streamline array sequence in DTK-compatible trackvis (.trk) format.
    dir_path : str
        Path to directory containing subject derivative data for a given pynets run.
    dm_path : str
        File path to fiber density map Nifti1Image.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    import os.path as op
    from dipy.tracking import utils
    from pynets.dmri.track import save_streams, run_LIFE_all

    dwi_img = nib.load(dwi_file)
    data = dwi_img.get_fdata()

    # Flatten streamlines list, and apply min length filter
    print('Filtering streamlines...')
    streamlines = nib.streamlines.array_sequence.ArraySequence([s for s in streamlines if len(s) > float(min_length)])

    # Fit LiFE model
    if life_run is True:
        print('Fitting LiFE...')
        # Fit Linear Fascicle Evaluation (LiFE)
        [streamlines, rmse] = run_LIFE_all(data, gtab, streamlines)
        mean_rmse = np.mean(rmse)
        print("%s%s" % ('Mean RMSE: ', mean_rmse))
        if mean_rmse > 50:
            print('WARNING: LiFE revealed high model error. Check streamlines output and review tracking parameters '
                  'used.')

    # Create density map
    dm = utils.density_map(streamlines, dwi_img.shape, affine=np.eye(4))

    # Save density map
    dm_img = nib.Nifti1Image(dm.astype('int16'), dwi_img.affine)
    dm_path = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (dir_path, '/density_map_',
                                                '%s' % (network + '_' if network is not None else ''),
                                                '%s' % (
                                                    op.basename(roi).split('.')[0] + '_' if roi is not None else ''),
                                                conn_model, '_', target_samples, '_',
                                                '%s' % ("%s%s" % (node_size, 'mm_') if node_size != 'parc' else ''),
                                                'curv', str(curv_thr_list).replace(', ', '_'),
                                                '_step', str(step_list).replace(', ', '_'), '.nii.gz')
    dm_img.to_filename(dm_path)

    # Save streamlines to trk
    streams = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (dir_path, '/streamlines_',
                                                '%s' % (network + '_' if network is not None else ''),
                                                '%s' % (
                                                    op.basename(roi).split('.')[0] + '_' if roi is not None else ''),
                                                conn_model, '_', target_samples, '_',
                                                '%s' % ("%s%s" % (node_size, 'mm_') if node_size != 'parc' else ''),
                                                'curv', str(curv_thr_list).replace(', ', '_'),
                                                '_step', str(step_list).replace(', ', '_'), '.trk')
    streams = save_streams(dwi_img, streamlines, streams)

    return streams, dir_path, dm_path


def track_ensemble(target_samples, atlas_data_wm_gm_int, parcels, mod_fit, tiss_classifier, sphere, directget,
                   curv_thr_list, step_list, track_type, maxcrossing, max_length, n_seeds_per_iter=200,
                   pft_back_tracking_dist=2, pft_front_tracking_dist=1, particle_count=15, roi_neighborhood_tol=8):
    """
    Perform native-space ensemble tractography, restricted to a vector of ROI masks.

    target_samples : int
        Total number of streamline samples specified to generate streams.
    atlas_data_wm_gm_int : array
        3D int32 numpy array of atlas parcellation intensities from Nifti1Image in T1w-warped native diffusion space,
        restricted to wm-gm interface.
    parcels : list
        List of 3D boolean numpy arrays of atlas parcellation ROI masks from a Nifti1Image in T1w-warped native
        diffusion space.
    mod : obj
        Connectivity reconstruction model.
    tiss_classifier : str
        Tissue classification method.
    sphere : obj
        DiPy object for modeling diffusion directions on a sphere.
    directget : str
        The statistical approach to tracking. Options are: det (deterministic), closest (clos), boot (bootstrapped),
        and prob (probabilistic).
    curv_thr_list : list
        List of integer curvature thresholds used to perform ensemble tracking.
    step_list : list
        List of float step-sizes used to perform ensemble tracking.
    track_type : str
        Tracking algorithm used (e.g. 'local' or 'particle').
    maxcrossing : int
        Maximum number if diffusion directions that can be assumed per voxel while tracking.
    max_length : int
        Maximum fiber length threshold in mm to restrict tracking.
    n_seeds_per_iter : int
        Number of seeds from which to initiate tracking for each unique ensemble combination.
        By default this is set to 200.
    particle_count
        pft_back_tracking_dist : float
        Distance in mm to back track before starting the particle filtering
        tractography. The total particle filtering tractography distance is
        equal to back_tracking_dist + front_tracking_dist. By default this is set to 2 mm.
    pft_front_tracking_dist : float
        Distance in mm to run the particle filtering tractography after the
        the back track distance. The total particle filtering tractography
        distance is equal to back_tracking_dist + front_tracking_dist. By
        default this is set to 1 mm.
    particle_count : int
        Number of particles to use in the particle filter.
    roi_neighborhood_tol : float
        Distance (in the units of the streamlines, usually mm). If any
        coordinate in the streamline is within this distance from the center
        of any voxel in the ROI, the filtering criterion is set to True for
        this streamline, otherwise False. Defaults to the distance between
        the center of each voxel and the corner of the voxel.

    Returns
    -------
    streamlines : ArraySequence
        DiPy list/array-like object of streamline points from tractography.
    """
    import warnings
    warnings.filterwarnings("ignore")
    from colorama import Fore, Style
    from dipy.tracking import utils
    from dipy.tracking.streamline import Streamlines, select_by_rois
    from dipy.tracking.local import LocalTracking, ParticleFilteringTracking
    from dipy.direction import ProbabilisticDirectionGetter, BootDirectionGetter, ClosestPeakDirectionGetter, DeterministicMaximumDirectionGetter

    # Commence Ensemble Tractography
    parcel_vec = np.ones(len(parcels)).astype('bool')
    streamlines = nib.streamlines.array_sequence.ArraySequence()
    ix = 0
    circuit_ix = 0
    stream_counter = 0
    while int(stream_counter) < int(target_samples):
        for curv_thr in curv_thr_list:
            print("%s%s" % ('Curvature: ', curv_thr))

            # Instantiate DirectionGetter
            if directget == 'prob':
                dg = ProbabilisticDirectionGetter.from_shcoeff(mod_fit, max_angle=float(curv_thr),
                                                               sphere=sphere)
            elif directget == 'boot':
                dg = BootDirectionGetter.from_shcoeff(mod_fit, max_angle=float(curv_thr),
                                                      sphere=sphere)
            elif directget == 'clos':
                dg = ClosestPeakDirectionGetter.from_shcoeff(mod_fit, max_angle=float(curv_thr),
                                                             sphere=sphere)
            elif directget == 'det':
                dg = DeterministicMaximumDirectionGetter.from_shcoeff(mod_fit, max_angle=float(curv_thr),
                                                                      sphere=sphere)
            else:
                raise ValueError('ERROR: No valid direction getter(s) specified.')

            for step in step_list:
                print("%s%s" % ('Step: ', step))
                # Perform wm-gm interface seeding, using n_seeds at a time
                seeds = utils.random_seeds_from_mask(atlas_data_wm_gm_int > 0, seeds_count=n_seeds_per_iter,
                                                     seed_count_per_voxel=False, affine=np.eye(4))
                if len(seeds) == 0:
                    raise RuntimeWarning('Warning: No valid seed points found in wm-gm interface...')

                print(seeds)
                # Perform tracking
                if track_type == 'local':
                    streamline_generator = LocalTracking(dg, tiss_classifier, seeds, np.eye(4),
                                                         max_cross=int(maxcrossing), maxlen=int(max_length),
                                                         step_size=float(step), return_all=True)
                elif track_type == 'particle':
                    streamline_generator = ParticleFilteringTracking(dg, tiss_classifier, seeds, np.eye(4),
                                                                     max_cross=int(maxcrossing),
                                                                     step_size=float(step),
                                                                     maxlen=int(max_length),
                                                                     pft_back_tracking_dist=pft_back_tracking_dist,
                                                                     pft_front_tracking_dist=pft_front_tracking_dist,
                                                                     particle_count=particle_count, return_all=True)
                else:
                    raise ValueError('ERROR: No valid tracking method(s) specified.')

                # Filter resulting streamlines by roi-intersection characteristics
                roi_proximal_streamlines = Streamlines(select_by_rois(streamline_generator, parcels, parcel_vec,
                                                                      mode='any', affine=np.eye(4),
                                                                      tol=roi_neighborhood_tol))

                # Repeat process until target samples condition is met
                ix = ix + 1
                for s in roi_proximal_streamlines:
                    stream_counter = stream_counter + len(s)
                    streamlines.append(s)
                    if int(stream_counter) >= int(target_samples):
                        break
                    else:
                        continue

        circuit_ix = circuit_ix + 1
        print("%s%s%s%s%s" % ('Completed hyperparameter circuit: ', circuit_ix, '...\nCumulative Streamline Count: ',
                              Fore.CYAN, stream_counter))
        print(Style.RESET_ALL)

    print('\n')
    return streamlines


def run_track(B0_mask, gm_in_dwi, vent_csf_in_dwi, wm_in_dwi, tiss_class, labels_im_file_wm_gm_int,
              labels_im_file, target_samples, curv_thr_list, step_list, track_type, max_length, maxcrossing, directget,
              conn_model, gtab_file, dwi_file, network, node_size, dens_thresh, ID, roi, min_span_tree, disp_filt, parc,
              prune, atlas, uatlas, labels, coords, norm, binary, atlas_mni, life_run, min_length,
              fa_path):
    '''
    Run all ensemble tractography and filtering routines.

    Parameters
    ----------
    B0_mask : str
        File path to B0 brain mask.
    gm_in_dwi : str
        File path to grey-matter tissue segmentation Nifti1Image.
    vent_csf_in_dwi : str
        File path to ventricular CSF tissue segmentation Nifti1Image.
    wm_in_dwi : str
        File path to white-matter tissue segmentation Nifti1Image.
    tiss_class : str
        Tissue classification method.
    labels_im_file_wm_gm_int : str
        File path to atlas parcellation Nifti1Image in T1w-warped native diffusion space, restricted to wm-gm interface.
    labels_im_file : str
        File path to atlas parcellation Nifti1Image in T1w-warped native diffusion space.
    target_samples : int
        Total number of streamline samples specified to generate streams.
    curv_thr_list : list
        List of integer curvature thresholds used to perform ensemble tracking.
    step_list : list
        List of float step-sizes used to perform ensemble tracking.
    track_type : str
        Tracking algorithm used (e.g. 'local' or 'particle').
    max_length : int
        Maximum fiber length threshold in mm to restrict tracking.
    maxcrossing : int
        Maximum number if diffusion directions that can be assumed per voxel while tracking.
    directget : str
        The statistical approach to tracking. Options are: det (deterministic), closest (clos), boot (bootstrapped),
        and prob (probabilistic).
    conn_model : str
        Connectivity reconstruction method (e.g. 'csa', 'tensor', 'csd').
    gtab_file : str
        File path to pickled DiPy gradient table object.
    dwi_file : str
        File path to diffusion weighted image.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default')
        used to filter nodes in the study of brain subgraphs.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    dens_thresh : bool
        Indicates whether a target graph density is to be used as the basis for
        thresholding.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    min_span_tree : bool
        Indicates whether local thresholding from the Minimum Spanning Tree
        should be used.
    disp_filt : bool
        Indicates whether local thresholding using a disparity filter and
        'backbone network' should be used.
    parc : bool
        Indicates whether to use parcels instead of coordinates as ROI nodes.
    prune : bool
        Indicates whether to prune final graph of disconnected nodes/isolates.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to graph nodes.
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    norm : int
        Indicates method of normalizing resulting graph.
    binary : bool
        Indicates whether to binarize resulting graph edges to form an
        unweighted graph.
    atlas_mni : str
        File path to atlas parcellation Nifti1Image in T1w-warped MNI space.
    life_run : bool
        Indicates whether to perform Linear Fascicle Evaluation (LiFE).
    min_length : int
        Minimum fiber length threshold in mm.
    fa_path : str
        File path to FA Nifti1Image.

    Returns
    -------
    streams : str
        File path to save streamline array sequence in .trk format.
    track_type : str
        Tracking algorithm used (e.g. 'local' or 'particle').
    target_samples : int
        Total number of streamline samples specified to generate streams.
    conn_model : str
        Connectivity reconstruction method (e.g. 'csa', 'tensor', 'csd').
    dir_path : str
        Path to directory containing subject derivative data for a given pynets run.
    network : str
        Resting-state network based on Yeo-7 and Yeo-17 naming (e.g. 'Default')
        used to filter nodes in the study of brain subgraphs.
    node_size : int
        Spherical centroid node size in the case that coordinate-based centroids
        are used as ROI's for tracking.
    dens_thresh : bool
        Indicates whether a target graph density is to be used as the basis for
        thresholding.
    ID : str
        A subject id or other unique identifier.
    roi : str
        File path to binarized/boolean region-of-interest Nifti1Image file.
    min_span_tree : bool
        Indicates whether local thresholding from the Minimum Spanning Tree
        should be used.
    disp_filt : bool
        Indicates whether local thresholding using a disparity filter and
        'backbone network' should be used.
    parc : bool
        Indicates whether to use parcels instead of coordinates as ROI nodes.
    prune : bool
        Indicates whether to prune final graph of disconnected nodes/isolates.
    atlas : str
        Name of atlas parcellation used.
    uatlas : str
        File path to atlas parcellation Nifti1Image in MNI template space.
    labels : list
        List of string labels corresponding to graph nodes.
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    norm : int
        Indicates method of normalizing resulting graph.
    binary : bool
        Indicates whether to binarize resulting graph edges to form an
        unweighted graph.
    atlas_mni : str
        File path to atlas parcellation Nifti1Image in T1w-warped MNI space.
    curv_thr_list : list
        List of integer curvature thresholds used to perform ensemble tracking.
    step_list : list
        List of float step-sizes used to perform ensemble tracking.
    fa_path : str
        File path to FA Nifti1Image.
    dm_path : str
        File path to fiber density map Nifti1Image.
    '''
    import warnings
    warnings.filterwarnings("ignore")
    try:
        import cPickle as pickle
    except ImportError:
        import _pickle as pickle
    from dipy.io import load_pickle
    from colorama import Fore, Style
    from dipy.data import get_sphere
    from pynets import utils
    from pynets.dmri.track import prep_tissues, reconstruction, filter_streamlines, track_ensemble

    # Load gradient table
    gtab = load_pickle(gtab_file)

    # Fit diffusion model
    mod_fit = reconstruction(conn_model, gtab, dwi_file, wm_in_dwi)

    # Load atlas parcellation (and its wm-gm interface reduced version for seeding)
    atlas_img = nib.load(labels_im_file)
    atlas_data = atlas_img.get_fdata().astype('int')
    atlas_img_wm_gm_int = nib.load(labels_im_file_wm_gm_int)
    atlas_data_wm_gm_int = atlas_img_wm_gm_int.get_fdata().astype('int')

    # Build mask vector from atlas for later roi filtering
    parcels = []
    i = 0
    for roi_val in np.unique(atlas_data)[1:]:
        parcels.append(atlas_data == roi_val)
        i = i + 1

    # Get sphere
    sphere = get_sphere('repulsion724')

    # Instantiate tissue classifier
    tiss_classifier = prep_tissues(B0_mask, gm_in_dwi, vent_csf_in_dwi, wm_in_dwi, tiss_class)

    if np.sum(atlas_data) == 0:
        raise ValueError('ERROR: No non-zero voxels found in atlas. Check any roi masks and/or wm-gm interface images '
                         'to verify overlap with dwi-registered atlas.')

    # Iteratively build a list of streamlines for each ROI while tracking
    print("%s%s%s%s" % (Fore.GREEN, 'Target number of samples: ', Fore.BLUE, target_samples))
    print(Style.RESET_ALL)
    print("%s%s%s%s" % (Fore.GREEN, 'Using curvature threshold(s): ', Fore.BLUE, curv_thr_list))
    print(Style.RESET_ALL)
    print("%s%s%s%s" % (Fore.GREEN, 'Using step size(s): ', Fore.BLUE, step_list))
    print(Style.RESET_ALL)
    print("%s%s%s%s" % (Fore.GREEN, 'Tracking type: ', Fore.BLUE, track_type))
    print(Style.RESET_ALL)
    if directget == 'prob':
        print("%s%s%s" % ('Using ', Fore.MAGENTA, 'Probabilistic Direction...'))
    elif directget == 'boot':
        print("%s%s%s" % ('Using ', Fore.MAGENTA, 'Bootstrapped Direction...'))
    elif directget == 'closest':
        print("%s%s%s" % ('Using ', Fore.MAGENTA, 'Closest Peak Direction...'))
    elif directget == 'det':
        print("%s%s%s" % ('Using ', Fore.MAGENTA, 'Deterministic Maximum Direction...'))
    print(Style.RESET_ALL)

    # Commence Ensemble Tractography
    streamlines = track_ensemble(target_samples, atlas_data_wm_gm_int, parcels, mod_fit, tiss_classifier, sphere,
                                 directget, curv_thr_list, step_list, track_type, maxcrossing, max_length)
    print('Tracking Complete')

    # Perform streamline filtering routines
    dir_path = utils.do_dir_path(atlas, dwi_file)
    [streams, dir_path, dm_path] = filter_streamlines(dwi_file, dir_path, gtab, streamlines, life_run, min_length,
                                                      conn_model, target_samples, node_size, curv_thr_list, step_list,
                                                      network, roi)

    return streams, track_type, target_samples, conn_model, dir_path, network, node_size, dens_thresh, ID, roi, min_span_tree, disp_filt, parc, prune, atlas, uatlas, labels, coords, norm, binary, atlas_mni, curv_thr_list, step_list, fa_path, dm_path

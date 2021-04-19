#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 11:25:59 2021

@author: Kaelen Saythongkham
"""

import os
from sklearn.metrics.pairwise import (
    cosine_distances,
    haversine_distances,
    manhattan_distances,
    euclidean_distances,
)
import numpy as np
from sklearn.datasets import make_classification
from pathlib import Path
from pynets.stats import benchmarking
import networkx as nx
import pytest
import logging

logger = logging.getLogger(__name__)
logger.setLevel(50)

#@pytest.mark.parametrize("dissimilarity", ["euclidean", "precomputed"])
@pytest.mark.parametrize("remove_isolates", [True, False])
@pytest.mark.parametrize("n_informative", [5, 25, 49])
@pytest.mark.parametrize("n_redundant", [0, 5, 25, 49])
@pytest.mark.parametrize("n_features", [100, 1000])
@pytest.mark.parametrize("n_samples", [100, 1000])
def test_discr_stat(
        remove_isolates,
        n_informative,
        n_redundant,
        n_features,
        n_samples):
    from pynets.stats import benchmarking
    
    dissimilarity = "euclidean"
    X, Y = make_classification(n_samples, n_features, n_informative, 
                                   n_redundant, n_repeated=0, n_classes=2,
                                   n_clusters_per_class=2, weights=None, 
                                   flip_y=0.01, class_sep=1.0, hypercube=True, 
                                   shift=0.0, scale=1.0, shuffle=True, random_state=42)
    dissimilarities = euclidean_distances(X)
    uniques, counts = np.unique(Y, return_counts=True)
    idx = np.isin(Y, uniques[counts != 1])
    labels = Y[idx]
    rdfs = benchmarking._discr_rdf(dissimilarities, labels)
    
    assert labels.shape[0] == rdfs.shape[0] == dissimilarities.shape[0] == n_samples
    
    disc = benchmarking.discr_stat(X, Y)[0]
    
    if n_features > n_samples:
        print(f"n_features > n_samples: {disc}")
        assert disc is not None
       
    elif n_features < n_samples:
        print(f"n_features < n_samples: {disc}")
        assert disc is not None
    
    elif (n_features == n_samples) and (n_informative >= n_redundant):
        print(f"n_features == n_samples & n_informative >= n_redundant: {disc}")
        assert disc is not None
    
    elif (n_features == n_samples) and (n_informative < n_redundant):
        print(f"n_features == n_samples & n_informative < n_redundant: {disc}")
        assert disc is not None
        
      
for remove_isolates in [True, False]:
    for n_informative in [5, 25, 49]:
        for n_redundant in [5, 25, 49]:
            for n_features in [100, 1000]:
                for n_samples in [100, 1000]:
                    dissimilarity = "euclidean"
                    X, Y = make_classification(n_samples, n_features, n_informative, 
                                                   n_redundant, n_repeated=0, n_classes=2,
                                                   n_clusters_per_class=2, weights=None, 
                                                   flip_y=0.01, class_sep=1.0, hypercube=True, 
                                                   shift=0.0, scale=1.0, shuffle=True, random_state=42)
                    dissimilarities = euclidean_distances(X)
                    uniques, counts = np.unique(Y, return_counts=True)
                    idx = np.isin(Y, uniques[counts != 1])
                    labels = Y[idx]
                    rdfs = benchmarking._discr_rdf(dissimilarities, labels)
                    
                    assert labels.shape[0] == rdfs.shape[0] == dissimilarities.shape[0] == n_samples
                    
                    disc = benchmarking.discr_stat(X, Y)[0]
                    
                    if n_features > n_samples:
                        print(f"n_features > n_samples: {disc}")
                       
                    elif n_features < n_samples:
                        print(f"n_features < n_samples: {disc}")
                    
                    elif (n_features == n_samples) and (n_informative >= n_redundant):
                        print(f"n_features == n_samples & n_informative >= n_redundant: {disc}")
                    
                    elif (n_features == n_samples) and (n_informative < n_redundant):
                        print(f"n_features == n_samples & n_informative < n_redundant: {disc}")
                        

@pytest.mark.parametrize("dissimilarities", ["euclidean_distances(X)", "cosine_distances(X)", 
                                             "haversine_distances(X)", "manhattan_distances(X)"])
@pytest.mark.parametrize("n_informative", [5, 25, 49])
@pytest.mark.parametrize("n_redundant", [0, 5, 25, 49])
@pytest.mark.parametrize("n_features", [100, 1000])
@pytest.mark.parametrize("n_samples", [100, 1000])
def test_discr_rdf(
        dissimilarities,
        labels,
        n_informative,
        n_redundant,
        n_features,
        n_samples):
    from pynets.stats import benchmarking
    
    X, Y = make_classification(n_samples, n_features, n_informative, 
                                   n_redundant, n_repeated=0, n_classes=2,
                                   n_clusters_per_class=2, weights=None, 
                                   flip_y=0.01, class_sep=1.0, hypercube=True, 
                                   shift=0.0, scale=1.0, shuffle=True, random_state=42)
    
    
    
    
    assert X.shape[0] == Y.shape
    

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 16:55:42 2017

@author: aki.nikolaidis
"""



def dim_reduce(X, n_clusters):
    
    import pandas as pd
    import numpy as np
    import scipy as sp
    from sklearn import cluster
    
    #Clean up X matrix
    data=X.filter(regex='DMN*',axis=1)
    
    #Calculate Distance matrix
    dist_of_1 = sp.spatial.distance.pdist(data.T, metric = 'correlation')
    dist_of_1[np.isnan((dist_of_1))]=1
    dist_matrix = sp.spatial.distance.squareform(dist_of_1)
    sim_matrix=1-dist_matrix
    sim_matrix[sim_matrix<0.1]=0


    spectral = cluster.SpectralClustering(n_clusters, eigen_solver='arpack', random_state = 5, affinity="precomputed", assign_labels='discretize')
    spectral.fit(sim_matrix)
    

    y_pred = spectral.labels_.astype(np.int)
    y_pred=y_pred+1
    clust_dim=pd.DataFrame([])
    for i in range(1,max(y_pred)+1):
        a=y_pred==i
        a=a*1
        temp=data[a].mean(axis=1)
        clust_dim=pd.concat([newmat,temp], axis=1)

    return newmat

X=pd.read_csv('/Users/aki.nikolaidis/git_repo/PyNets/all_subjects_DMN.csv')
n_clusters=5

clust_dim = dim_reduce(X, n_clusters)
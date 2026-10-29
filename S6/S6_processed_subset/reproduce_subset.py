from pathlib import Path
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics.pairwise import pairwise_distances_argmin
from threadpoolctl import threadpool_limits
import json
root=Path(__file__).resolve().parent
with np.load(root/'S6_training_subset.npz',allow_pickle=False) as h:
 y=h['smoothed_LOS_mm'];c=h['final_displacement_mm'];stored=h['features'];mask=h['common_inlier_mask'];labels=h['reference_labels']
with threadpool_limits(limits=1):
 x=np.arange(y.shape[1],dtype=float)
 f=np.column_stack([c,y@np.polyfit(x,np.eye(len(x)),1)[0],y@np.polyfit(x,np.eye(len(x)),2)[0]])
 got=IsolationForest(contamination=.05,random_state=42,n_jobs=1).fit_predict(f)==1
 assert np.array_equal(got,mask)
 sc=RobustScaler().fit(f[mask]);s=sc.transform(f[mask]);km=KMeans(n_clusters=2,n_init=10,random_state=42).fit(s)
 reps=s[pairwise_distances_argmin(km.cluster_centers_,s)]
 pred=pairwise_distances_argmin(sc.transform(f),reps)
 result={'feature_max_abs_difference':float(abs(f-stored).max()),'inliers':int(mask.sum()),'IF_mask_exact':bool(np.array_equal(got,mask)),'ARI_sample':float(adjusted_rand_score(labels,pred))}
 assert result['ARI_sample']==1.0
 print(json.dumps(result,indent=2))

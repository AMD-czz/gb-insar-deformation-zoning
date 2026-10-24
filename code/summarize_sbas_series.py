"""Recalculate summaries of the publicly released final SBAS LOS rasters."""
import argparse
import csv
import datetime as dt
from pathlib import Path
import re
import numpy as np
from sbas_statistics import read_envi


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',required=True,type=Path)
    p.add_argument('--mask',required=True,type=Path,help='Boolean study polygon, not a different ROI')
    p.add_argument('--velocity-name',default='G_SI_velocity_geo')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    velocity,nd=read_envi(a.directory/a.velocity_name,a.directory/(a.velocity_name+'.hdr'))
    mask=np.load(a.mask,allow_pickle=False)
    if mask.shape!=velocity.shape or mask.dtype!=bool:
        raise ValueError('Mask must be boolean and match the velocity raster')
    valid=mask&np.isfinite(velocity)
    if np.isfinite(nd):valid&=velocity!=nd
    if not valid.any():raise ValueError('No valid velocity pixels')
    point=np.unravel_index(np.argmin(np.where(valid,velocity,np.inf)),velocity.shape)
    files=sorted([f for f in a.directory.iterdir() if re.fullmatch(r'G_SI_\d{8}_\d+_disp_geo',f.name)],key=lambda f:f.name.split('_')[2])
    if not files:raise ValueError('No final LOS epoch rasters')
    rows=[]
    for file in files:
        z,nd=read_envi(file,Path(str(file)+'.hdr'))
        if z.shape!=velocity.shape:raise ValueError('Epoch grid shape differs')
        m=valid&np.isfinite(z)
        if np.isfinite(nd):m&=z!=nd
        if not m.any():raise ValueError('No observations at epoch '+file.name)
        rows.append({'date':dt.datetime.strptime(file.name.split('_')[2],'%Y%m%d').date().isoformat(),
          'regional_mean_LOS_mm':float(z[m].mean()),'mean_valid_cells':int(m.sum()),
          'fixed_min_velocity_point_LOS_mm':float(z[point]),'raster':file.name})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Epochs:',len(rows),'velocity-valid study cells:',int(valid.sum()),'last mean mm:',rows[-1]['regional_mean_LOS_mm'])


if __name__=='__main__':main()

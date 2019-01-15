""" Script form Lukas to calculate the difference between two analyses and write them as new
analysis files.

TODO: Rewrite nicely and put into omc3.
"""

#!/afs/cern.ch/work/o/omc/anaconda/bin/python
import sys
import os
from optparse import OptionParser

from tfs_files.tfs_pandas import read_tfs, write_tfs
import numpy as np
import pandas as pd


def _parse_args():
    parser = OptionParser()
    parser.add_option("--folder1",
                    help="Folder containing first analysis - to be corrected",
                    metavar="FOLDER1", default="", dest="folder1")
    parser.add_option("--folder2",
                    help="Folder containing second analysis - to be targeted",
                    metavar="FOLDER2", default="", dest="folder2")
    parser.add_option("--output",
                    help="Output folder",
                    metavar="OUTPUT", default="", dest="output")
    options, _ = parser.parse_args()

    return options.folder1, options.folder2, options.output


def get_merged_measurement(folder1, folder2, file_name):
    f1=read_tfs(folder1 + file_name)
    f2=read_tfs(folder2 + file_name)
    a=pd.merge(f1,f2,how='inner',on='NAME',suffixes=('', '_t'))
    return a


def get_merged_measurement_with_header(folder1, folder2, file_name):
    f1=read_tfs(folder1 + file_name)
    header=f1.headers
    f2=read_tfs(folder2 + file_name)
    a=pd.merge(f1,f2,how='inner',on='NAME',suffixes=('', '_t'))
    return a, header
    

def get_ndx(folder1, folder2):
    file_name="/getNDx.out"
    result = get_merged_measurement(folder1,folder2,file_name)
    meas='NDX'
    model='NDXMDL'
    err="STDNDX"
    result.loc[:,meas]=(result.loc[:,meas]+result.loc[:,model]-result.loc[:,meas+'_t'])
    model_diff= np.std(result.loc[:,model].values-result.loc[:,model+'_t'].values)
    if model_diff:
        print("Models are different")
        print(model_diff)
    result.loc[:,err] = np.sqrt(np.square(result.loc[:,err].values) + np.square(result.loc[:,err+'_t'].values))
    write_tfs(rfold + file_name, result, {})
    return result  


def get_beta_from_phase(folder1, folder2, plane='x', free=True):
    file_name="/getbeta" + plane + free* "_free" + ".out"
    result = get_merged_measurement(folder1, folder2, file_name)
    meas='BET' + plane.upper()
    model='BET'+ plane.upper() + 'MDL'
    err="ERRBET" + plane.upper()
    result.loc[:,meas]=(result.loc[:,meas]+result.loc[:,model]-result.loc[:,meas+'_t'])
    model_diff= np.std(result.loc[:,model].values-result.loc[:,model+'_t'].values)
    if model_diff:
        print("Models are different")
        print(model_diff)
    result.loc[:,err] = np.sqrt(np.square(result.loc[:,err].values) + np.square(result.loc[:,err+'_t'].values))
    file_name="/getbeta" + plane + ".out"
    write_tfs(rfold + file_name, result, {})
    return result 


def get_phase(folder1, folder2, plane='x', free=True):
    file_name="/getphase" + plane + free* "_free" + ".out"
    res, header = get_merged_measurement_with_header(folder1,folder2,file_name)
    mask = res.loc[:,'NAME2'] == res.loc[:,'NAME2_t']
    result = res.loc[res.index[mask],:]
    meas='PHASE' + plane.upper()
    model='PH'+ plane.upper() + 'MDL'
    err="STDPH" + plane.upper() 
    result.loc[:,meas]=(result.loc[:,meas]+result.loc[:,model]-result.loc[:,meas+'_t'])
    model_diff= np.std(result.loc[:,model].values-result.loc[:,model+'_t'].values)
    if model_diff:
        print("Models are different")
        print(model_diff)
    result.loc[:,err] = np.sqrt(np.square(result.loc[:,err].values) + np.square(result.loc[:,err+'_t'].values))
    file_name="/getphase" + plane + ".out"
    write_tfs(rfold + file_name, result, header)
    return result


def get_couple(folder1, folder2, plane='x', free=True):
    file_name="/getcouple.out"
    res=get_merged_measurement(folder1,folder2,file_name)
    write_tfs(rfold + file_name, res, {})
    return res


def get_tunes(folder1, free=True):
    file_namex ="/getphasex" + free* "_free" + ".out"
    twx=read_tfs(folder1 + file_namex) 
    file_namey ="/getphasey" + free* "_free" + ".out"
    twy=read_tfs(folder1 + file_namey)   
    return twx.headers['Q1'], twx.headers['Q2']


if __name__ == '__main__':

    # folder1, folder2, rfold = _parse_args()
    folder1 ="/media/jdilly/Storage/Repositories/Gui_Output/HLLHC-DA/LHCB2/Results/b2_md2148_afterglobal"
    folder2 = "/media/jdilly/Storage/Repositories/Gui_Output/HLLHC-DA/LHCB2/Results/b2_md3312_forcoupling"
    rfold = "/media/jdilly/Storage/Repositories/Gui_Output/HLLHC-DA/LHCB2/Results/b2_diff_june_oct"

    if not os.path.exists(rfold):
        os.makedirs(rfold)


    betax = get_beta_from_phase(folder1, folder2, plane='x', free=True)
    betay = get_beta_from_phase(folder1, folder2, plane='y', free=True)
    phasex = get_phase(folder1, folder2, plane='x', free=True)
    phasey = get_phase(folder1, folder2, plane='y', free=True)
    couple = get_couple(folder1, folder2)
    # ndx = get_ndx(folder1, folder2)
    # TODO write files
    #write_tfs(rfold)
    #write_tfs(result,{},os.path.join(options.path, options.comment + ".tfs"))

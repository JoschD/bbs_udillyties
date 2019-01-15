""" Felix way of getting BBQ data.

Will not run as the database thing is not installed. For research purposes only. """


from __future__ import print_function
import os, sys

import pytimber
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import pandas as pd
from tfs_files import tfs_pandas

from scipy import stats
from scipy.odr import *

matplotlib.style.use('ggplot')
matplotlib.rc('axes',edgecolor='black')
plt.rcParams['axes.facecolor']='w'


####################################
##    CONSTANTS 
####################################

EMITTANCE = 5.4e-10
DETUNING_PAIRS_H = [ ('2JXRES', 'NATQX_CORRECTED', '2JXSTDRES', 'NATQXRMS'), 
                     ('2JXRES', 'NATQY_CORRECTED', '2JXSTDRES', 'NATQYRMS') ] 
DETUNING_PAIRS_V = [ ('2JYRES', 'NATQX_CORRECTED', '2JYSTDRES', 'NATQXRMS'), 
                     ('2JYRES', 'NATQY_CORRECTED', '2JYSTDRES', 'NATQYRMS')  ]

LABELS_H = [(r'$2J_x \quad [\mu m]$', r'$\Delta Q_x$'), (r'$2J_x \quad [\mu m]$', r'$\Delta Q_y$')]
LABELS_V = [(r'$2J_y \quad [\mu m]$', r'$\Delta Q_x$'), (r'$2J_y \quad [\mu m]$', r'$\Delta Q_y$')]


####################################
##    PyTimber functions 
####################################

def extract_BBQ_Data(ldb, t1, t2):
    bbq_x_b1 = ldb.get('LHC.BOFSU:EIGEN_FREQ_1_B1', t1, t2)['LHC.BOFSU:EIGEN_FREQ_1_B1']
    bbq_y_b1 = ldb.get('LHC.BOFSU:EIGEN_FREQ_2_B1', t1, t2)['LHC.BOFSU:EIGEN_FREQ_2_B1']
    bbq_x_b2 = ldb.get('LHC.BOFSU:EIGEN_FREQ_1_B2', t1, t2)['LHC.BOFSU:EIGEN_FREQ_1_B2']
    bbq_y_b2 = ldb.get('LHC.BOFSU:EIGEN_FREQ_2_B2', t1, t2)['LHC.BOFSU:EIGEN_FREQ_2_B2']
    return bbq_x_b1, bbq_y_b1, bbq_x_b2, bbq_y_b2


def extract_BSRT_Data(ldb, t1, t2):
    BSRT_H = ldb.get('LHC.BSRT.5L4.B2:FIT_SIGMA_H', t1, t2)
    BSRT_V = ldb.get('LHC.BSRT.5L4.B2:FIT_SIGMA_V', t1, t2)

    resH = np.zeros(len(BSRT_H[BSRT_H.keys()[0]][1]))
    stdH = np.zeros(len(BSRT_H[BSRT_H.keys()[0]][1]))
    resV = np.zeros(len(BSRT_V[BSRT_V.keys()[0]][1]))
    stdV = np.zeros(len(BSRT_V[BSRT_V.keys()[0]][1]))
    
    for i in range(len(BSRT_H[BSRT_H.keys()[0]][1])):
        resH[i] = np.average(BSRT_H[BSRT_H.keys()[0]][1][i])
        stdH[i] = np.std(BSRT_H[BSRT_H.keys()[0]][1][i])
    
    for i in range(len(BSRT_V[BSRT_V.keys()[0]][1])):
        resV[i] = np.average(BSRT_V[BSRT_V.keys()[0]][1][i])
        stdV[i] = np.std(BSRT_V[BSRT_V.keys()[0]][1][i])
    
    timeH = BSRT_H[BSRT_H.keys()[0]][0]
    timeV = BSRT_V[BSRT_V.keys()[0]][0]
    bsrt_h = {'TIME':timeH, 'DATA':resH, 'STD_DATA':stdH }
    bsrt_v = {'TIME':timeV, 'DATA':resV, 'STD_DATA':stdV }
    return bsrt_h, bsrt_v


def store_DataBase(datadb, datadb_dir, t1, t2):
    print('Saving in DataBase.')
    mydb = pagestore.PageStore(datadb, datadb_dir)
    mydb.store(db.get('LHC.BSRT.5R4.B1:FIT_SIGMA_H', t1, t2))
    mydb.store(db.get('LHC.BSRT.5R4.B1:FIT_SIGMA_V', t1, t2))
    mydb.store(db.get('LHC.BSRT.5L4.B2:FIT_SIGMA_H', t1, t2))
    mydb.store(db.get('LHC.BSRT.5L4.B2:FIT_SIGMA_V', t1, t2))
    mydb.store(db.get('LHC.BOFSU:EIGEN_FREQ_1_B1', t1, t2))
    mydb.store(db.get('LHC.BOFSU:EIGEN_FREQ_2_B1', t1, t2))
    mydb.store(db.get('LHC.BOFSU:EIGEN_FREQ_1_B2', t1, t2))
    mydb.store(db.get('LHC.BOFSU:EIGEN_FREQ_2_B2', t1, t2))
    mydb.store(db.get('LHC.BWS.5R4.B1H.APP.IN:EMITTANCE_NORM' , t1, t2))
    mydb.store(db.get('LHC.BWS.5R4.B1H.APP.OUT:EMITTANCE_NORM', t1, t2))
    mydb.store(db.get('LHC.BWS.5R4.B1V.APP.IN:EMITTANCE_NORM' , t1, t2))
    mydb.store(db.get('LHC.BWS.5R4.B1V.APP.OUT:EMITTANCE_NORM', t1, t2))
    mydb.store(db.get('LHC.BWS.5L4.B2H.APP.IN:EMITTANCE_NORM' , t1, t2))
    mydb.store(db.get('LHC.BWS.5L4.B2H.APP.OUT:EMITTANCE_NORM', t1, t2))
    mydb.store(db.get('LHC.BWS.5L4.B2V.APP.IN:EMITTANCE_NORM' , t1, t2))
    mydb.store(db.get('LHC.BWS.5L4.B2V.APP.OUT:EMITTANCE_NORM', t1, t2))
    mydb.store(db.get('LHC.BCTFR.A6R4.B1:BEAM_INTENSITY', t1, t2))        
    mydb.store(db.get('LHC.BCTFR.A6R4.B2:BEAM_INTENSITY', t1, t2))        
    print('Saving done.')


####################################
##    Fitting and plotting functions 
####################################


def lin_function(p, x):
    m, c = p
    return m*x + c


def do_odr(selected_data):
    x, y, x_err, y_err = selected_data
    lin_model = Model(lin_function)
    data = RealData(x, y, sx=x_err, sy=y_err)
    odr = ODR(data, lin_model, beta0=[0., 1.])
    out = odr.run()
    out.pprint()
    return out


def get_sigmas(xdat):
    x, x_err = xdat
    x_sig = np.sqrt(x/EMITTANCE)
    x_err_sig = ((x_sig*0.5*x_err)/x)**2
    return x_sig, x_err_sig


def do_plot(data_tuple, labels, colorplot):
    xdata, ydata, xdata_err, ydata_err = data_tuple
    fig = plt.figure(figsize=(7,4))
    fig.patch.set_facecolor('white')
    axt = fig.add_subplot(111)

    odr_output = do_odr(data_tuple)
    xi = np.linspace(0,0.018,3)
    line = odr_output.beta[0]*xi
    axt.plot(xi, line, linestyle='--', color='k', label='${:.4f}\, \pm\, {:.4f}$'.format(odr_output.beta[0], odr_output.sd_beta[0]))
    axt.errorbar(xdata, ydata-odr_output.beta[1], xerr=xdata_err, yerr=ydata_err, fmt='o', color=colorplot, label='IP5 Xing')
    

    com = tfs_pandas.read_tfs('/media/jdilly/Storage/Projects/NOTE.18.MD1_Amplitude_Detuning/overleaf/results/2018_commissioning/B1_crossing_H_amp_det.dat')
    xdata_com = com['2JXRES']
    ydata_com = com['NATQX'] - com['BBQb1qx']
    xdata_err_com = com['2JXSTDRES']
    ydata_err_com = com['NATQXRMS']
    data_tuple_com = xdata_com, ydata_com, xdata_err_com, ydata_err_com
    
    odr_output_com = do_odr(data_tuple_com)
    line_com = odr_output_com.beta[0]*xi
    axt.errorbar(xdata_com, ydata_com-odr_output_com.beta[1], xerr=xdata_err_com, yerr=ydata_err_com, fmt='o', color='c', label='Crossing angles')
    axt.plot(xi, line_com, linestyle='--', color='m', label='${:.4f}\, \pm\, {:.4f}$'.format(odr_output_com.beta[0], odr_output_com.sd_beta[0]))
    

    axt.set_xlim([0., 0.017])
    axt.set_ylim([-0.0008, 0.0013])
    axt.set_xlabel(labels[0], fontsize=14)
    axt.set_ylabel(labels[1], fontsize=14)
    fig.tight_layout()
    plt.legend(fontsize=14, ncol=2, loc='lower right')


def get_data(data, pair):
    x = getattr(data, pair[0])
    y = getattr(data, pair[1])
    x_err = getattr(data, pair[2])
    y_err = getattr(data, pair[3])
    return x, y, x_err, y_err


####################################
##    BBQ processing functions 
####################################


def get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan):
    bbq_x_b1, bbq_y_b1, bbq_x_b2, bbq_y_b2 = extract_BBQ_Data(ldb, start_scan, end_scan)
    
    if beam==1:
        bbq_x = bbq_x_b1
        bbq_y = bbq_y_b1
    elif beam==2:
        bbq_x = bbq_x_b2
        bbq_y = bbq_y_b2

    df_bbq_x = pd.DataFrame(bbq_x[1], index=bbq_x[0], columns=['BBQ'])
    df_bbq_y = pd.DataFrame(bbq_y[1], index=bbq_y[0], columns=['BBQ'])
    
    df_bbq_x['BBQ'] = df_bbq_x.ix[df_bbq_x['BBQ'] > (tunex-0.0004)]
    df_bbq_x['BBQ'] = df_bbq_x.ix[df_bbq_x['BBQ'] < (tunex+0.0004)]
    df_bbq_y['BBQ'] = df_bbq_y.ix[df_bbq_y['BBQ'] > (tuney-0.0004)]
    df_bbq_y['BBQ'] = df_bbq_y.ix[df_bbq_y['BBQ'] < (tuney+0.0004)]
    
    df_bbq_x.dropna(axis=0, inplace=True)
    df_bbq_y.dropna(axis=0, inplace=True)

    df_bbq_x['MAV'] = df_bbq_x['BBQ'].rolling(15).mean()
    df_bbq_y['MAV'] = df_bbq_y['BBQ'].rolling(15).mean()
    
    df_bbq_x.dropna(axis=0, inplace=True)
    df_bbq_y.dropna(axis=0, inplace=True)
   
    df_bbq_x['date'] = pd.to_datetime(df_bbq_x.index,unit='s')
    df_bbq_y['date'] = pd.to_datetime(df_bbq_y.index,unit='s')
    
    acd = add_BBQ_to_df(acd, df_bbq_x, df_bbq_y)
    do_bbq_plot(df_bbq_x, df_bbq_y, acd, tunex, tuney)
    
    return df_bbq_x, df_bbq_y, acd


def do_bbq_plot(df_bbq_x, df_bbq_y, acd, tunex, tuney):
    fig1 = plt.figure(figsize=(7,8))
    fig1.patch.set_facecolor('white')
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)
    
    df_bbq_x.plot(x='date',y='BBQ',ax=ax1, color='c', alpha=0.5, label='Qx Beam 1')
    df_bbq_x.plot(x='date', y='MAV',ax=ax1, color='b', label='Moving average Qx Beam 1')
    
    df_bbq_y.plot(x='date',y='BBQ',ax=ax2, color='m', alpha=0.3, label='Qy Beam 1')
    df_bbq_y.plot(x='date', y='MAV',ax=ax2, color='r', label='Moving average Qy Beam 1')
    
    ax1.plot(acd['BBQ_MAV_QX_TIME'], acd['BBQ_MAV_QX'], 'o', color='r', label='Correction value for AC dipole kick')
    ax2.plot(acd['BBQ_MAV_QY_TIME'], acd['BBQ_MAV_QY'], 'o', color='b', label='Correction value for AC dipole kick')

    ax1.set_ylim([tunex-0.0005, tunex+0.0005]) 
    ax2.set_ylim([tuney-0.0005, tuney+0.0005]) 
   
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Tune')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Tune')
    hours = mdates.HourLocator()   # every year
    hoursFmt = mdates.DateFormatter('%H:%M:%S')
    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_major_formatter(hoursFmt)
    ax2.xaxis.set_major_locator(hours)
    ax2.xaxis.set_major_formatter(hoursFmt)
    ax1.legend(fontsize=14)
    ax2.legend(fontsize=14)
    plt.tight_layout()


def add_BBQ_to_df(acd, df_bbq_x, df_bbq_y):
    valsx = []
    valsy = []
    valsx_time = []
    valsy_time = []
    
    for idx, kick_time_stamp in enumerate(acd.TIME):
        valx_time = df_bbq_x.index.get_loc(kick_time_stamp,method='nearest')
        valy_time = df_bbq_y.index.get_loc(kick_time_stamp,method='nearest')
        valx = df_bbq_x.iloc[valx_time]
        valy = df_bbq_y.iloc[valy_time]
        valsx_time.append(valx['date'])
        valsy_time.append(valy['date'])
        valsx.append(valx['MAV'])
        valsy.append(valy['MAV'])

    acd['BBQ_MAV_QX'] = valsx
    acd['BBQ_MAV_QY'] = valsy
    
    acd['BBQ_MAV_QX_TIME'] = valsx_time
    acd['BBQ_MAV_QY_TIME'] = valsy_time
    
    acd['NATQX_CORRECTED'] = acd['NATQX']# - acd['BBQ_MAV_QX']
    acd['NATQY_CORRECTED'] = acd['NATQY']# - acd['BBQ_MAV_QY']
    return acd



####################################
##    MAIN function 
####################################

def _main():

    '''
    ---------------------------
    Flat orbit + IP5 xing horizontal kicks
    ---------------------------
    '''
    
    fig = plt.figure(figsize=(7,4))
    fig.patch.set_facecolor('white')
    axt = fig.add_subplot(111)
    xi = np.linspace(0,0.018,3)
    com = tfs_pandas.read_tfs('/media/jdilly/Storage/Projects/NOTE.18.MD1_Amplitude_Detuning/overleaf/results/2018_commissioning/B1_crossing_H_amp_det.dat')
    xdata_com = com['2JXRES']
    ydata_com = com['NATQY'] - com['BBQb1qy']
    xdata_err_com = com['2JXSTDRES']
    ydata_err_com = com['NATQYRMS']
    data_tuple_com = xdata_com, ydata_com, xdata_err_com, ydata_err_com

    odr_output_com = do_odr(data_tuple_com)
    line_com = odr_output_com.beta[0]*xi
    axt.errorbar(xdata_com, ydata_com-odr_output_com.beta[1], xerr=xdata_err_com, yerr=ydata_err_com, fmt='o', color='c', label='Crossing angles')
    axt.plot(xi, line_com, linestyle='--', color='m', label='${:.4f}\, \pm\, {:.4f}$'.format(odr_output_com.beta[0], odr_output_com.sd_beta[0]))
    plt.show()
    exit()

    # '''
    # ---------------------------
    # Flat orbit + IP5 xing vertical kicks
    # ---------------------------
    # '''
    # 
    # tunex, tuney = 0.31 , 0.32
    # beam = 1

    # results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam1/B1_flatorbit_IP5xing_V/'
    # kick_file = 'getkickac.out'
    # final_file = './B1_flatorbit_IP5xing_V_amp_det.dat'
    # 
    # acd_file = os.path.join(results_path, kick_file)
    # acd = tfs_pandas.read_tfs(acd_file)
    # start_scan = acd['TIME'].iloc[0] - 2
    # end_scan   = acd['TIME'].iloc[-1] + 2
    # 
    # df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    # tfs_pandas.write_tfs(final_file, acd)
    # 
    # for i in range(len(DETUNING_PAIRS_V)):
    #     data_tuple = get_data(acd, DETUNING_PAIRS_V[i])
    #     do_plot(data_tuple, acd, LABELS_V[i], 'b')
    # 
    # plt.show()
    


    # '''
    # ---------------------------
    # Flat orbit + IP5 xing vertical kicks with Q shift
    # ---------------------------
    # '''
    # 
    # tunex, tuney = 0.304 , 0.315
    # beam = 1

    # results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam1/B1_flatorbit_IP5xing_V_Qshift/'
    # kick_file = 'getkickac.out'
    # final_file = './B1_flatorbit_IP5xing_V_Qshift_amp_det.dat'
    # 
    # acd_file = os.path.join(results_path, kick_file)
    # acd = tfs_pandas.read_tfs(acd_file)
    # start_scan = acd['TIME'].iloc[0] - 2
    # end_scan   = acd['TIME'].iloc[-1] + 2
    # 
    # df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    # tfs_pandas.write_tfs(final_file, acd)
    # 
    # for i in range(len(DETUNING_PAIRS_V)):
    #     data_tuple = get_data(acd, DETUNING_PAIRS_V[i])
    #     do_plot(data_tuple, acd, LABELS_V[i], 'b')
    # 
    # plt.show()
    # 






















    # 
    # '''
    # ---------------------------
    # Flat orbit horizontal kicks
    # ---------------------------
    # '''
    # 
    # tunex, tuney = 0.31 , 0.32
    # beam = 2

    # results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam2/B2_flatorbit_H/'
    # kick_file = 'getkickac.out'
    # final_file = './B2_flatorbit_H_amp_det.dat'
    # 
    # acd_file = os.path.join(results_path, kick_file)
    # acd = tfs_pandas.read_tfs(acd_file)
    # start_scan = acd['TIME'].iloc[0] - 2
    # end_scan   = acd['TIME'].iloc[-1] + 2
    # 
    # df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    # tfs_pandas.write_tfs(final_file, acd)
    # 
    # for i in range(len(DETUNING_PAIRS_H)):
    #     data_tuple = get_data(acd, DETUNING_PAIRS_H[i])
    #     do_plot(data_tuple, acd, LABELS_H[i], 'b')
    # 
    # plt.show()
    # 

    
    '''
    ---------------------------
    Flat orbit vertical kicks
    ---------------------------
    '''
    
    tunex, tuney = 0.31 , 0.32
    beam = 2

    results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam2/B2_flatorbit_V/'
    kick_file = 'getkickac.out'
    final_file = './B2_flatorbit_V_amp_det.dat'
    
    acd_file = os.path.join(results_path, kick_file)
    acd = tfs_pandas.read_tfs(acd_file)
    start_scan = acd['TIME'].iloc[0] - 2
    end_scan   = acd['TIME'].iloc[-1] + 2
    
    df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    tfs_pandas.write_tfs(final_file, acd)
    
    for i in range(len(DETUNING_PAIRS_V)):
        data_tuple = get_data(acd, DETUNING_PAIRS_V[i])
        do_plot(data_tuple, acd, LABELS_V[i], 'b')
    
    plt.show()
    



    
    '''
    ---------------------------
    Flat orbit + IP5 xing horizontal kicks
    ---------------------------
    '''
    
    tunex, tuney = 0.3105 , 0.32
    beam = 2

    results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam2/B2_flatorbit_IP5xing_H/'
    kick_file = 'getkickac.out'
    final_file = './B2_flatorbit_IP5xing_H_amp_det.dat'
    
    acd_file = os.path.join(results_path, kick_file)
    acd = tfs_pandas.read_tfs(acd_file)
    start_scan = acd['TIME'].iloc[0] - 2
    end_scan   = acd['TIME'].iloc[-1] + 2
    
    df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    tfs_pandas.write_tfs(final_file, acd)
    
    for i in range(len(DETUNING_PAIRS_H)):
        data_tuple = get_data(acd, DETUNING_PAIRS_H[i])
        do_plot(data_tuple, acd, LABELS_H[i], 'b')
    
    plt.show()
    

    
    '''
    ---------------------------
    Flat orbit + IP5 xing vertical kicks
    ---------------------------
    '''
    
    tunex, tuney = 0.3105 , 0.32
    beam = 2

    results_path = '/afs/cern.ch/work/f/fcarlier/public/data/MD18/MD1_amp_det/Results/beam2/B2_flatorbit_IP5xing_V/'
    kick_file = 'getkickac.out'
    final_file = './B2_flatorbit_IP5xing_V_amp_det.dat'
    
    acd_file = os.path.join(results_path, kick_file)
    acd = tfs_pandas.read_tfs(acd_file)
    start_scan = acd['TIME'].iloc[0] - 2
    end_scan   = acd['TIME'].iloc[-1] + 2
    
    df_bbq_x, df_bbq_y, acd = get_BBQ_moving_average(beam, ldb, acd, tunex, tuney, start_scan, end_scan)
    tfs_pandas.write_tfs(final_file, acd)
    
    for i in range(len(DETUNING_PAIRS_V)):
        data_tuple = get_data(acd, DETUNING_PAIRS_V[i])
        do_plot(data_tuple, acd, LABELS_V[i], 'b')
    
    plt.show()
    


if __name__ == '__main__':
    _main()

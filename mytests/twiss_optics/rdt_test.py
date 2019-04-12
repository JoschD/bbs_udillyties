import matplotlib.pyplot as plt

from Python_Classes4MAD import metaclass
from tfs_files import tfs_pandas
from twiss_optics import optics_class
import numpy as np




if __name__ == '__main__':

    tw_metaclass = metaclass.twiss( 'twiss.mqsx.dat' )
    tw_pandas = tfs_pandas.read_tfs( 'twiss.mqsx.dat', index='NAME' )


    tw_metaclass.Cmatrix()

    tw_optics_class = optics_class.TwissOptics( tw_pandas )

    coupling_rdts = tw_optics_class.get_coupling( method='rdt' )
    coupling_cmatrix = tw_optics_class.get_coupling( method='cmatrix' )

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,10) )

    ax.plot( tw_metaclass.S, tw_metaclass.F1001R , label='metaclass', marker="o")
    ax.plot( coupling_rdts['S'], np.real(coupling_rdts['F1001']) , label='opticsclass rdt', marker="x")
    ax.plot( coupling_cmatrix['S'], np.real(coupling_cmatrix['F1001']) , label='opticsclass cmatrix', marker="d")
    ax.legend()
    plt.show()



    # fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(20,20) )
    #
    # ax[0,0].plot( tw_metaclass.S, tw_metaclass.F1001R , label='metaclass')
    # ax[0,0].plot( coupling_rdts['S'], np.real(coupling_rdts['F1001']) , label='opticsclass rdt')
    # ax[0,0].plot( coupling_cmatrix['S'], np.real(coupling_cmatrix['F1001']) , label='opticsclass cmatrix')
    # ax[0,0].legend()
    #
    # ax[0,1].plot( tw_metaclass.S, tw_metaclass.F1001I , label='metaclass')
    # ax[0,1].plot( coupling_rdts['S'], np.imag(coupling_rdts['F1001']) , label='opticsclass rdt')
    # ax[0,1].plot( coupling_cmatrix['S'], np.imag(coupling_cmatrix['F1001']) , label='opticsclass cmatrix')
    # ax[0,1].legend()
    #
    #
    # ax[1,0].plot( tw_metaclass.S, tw_metaclass.F1010R , label='metaclass')
    # ax[1,0].plot( coupling_rdts['S'], np.real(coupling_rdts['F1010']) , label='opticsclass rdt')
    # ax[1,0].plot( coupling_cmatrix['S'], np.real(coupling_cmatrix['F1010']) , label='opticsclass cmatrix')
    # ax[1,0].legend()
    #
    # ax[1,1].plot( tw_metaclass.S, tw_metaclass.F1010I , label='metaclass')
    # ax[1,1].plot( coupling_rdts['S'], np.imag(coupling_rdts['F1010']) , label='opticsclass rdt')
    # ax[1,1].plot( coupling_cmatrix['S'], np.imag(coupling_cmatrix['F1010']) , label='opticsclass cmatrix')
    # ax[1,1].legend()
    #
    # plt.show()
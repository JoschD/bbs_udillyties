from predefined import plotly_wrapper, get_layout, get_scatter_for_df
from tfs_files import tfs_pandas as tfs

if __name__ == '__main__':
    data = "/media/jdilly/Storage/Repositories/Gui_Output/2018-04-25/models/LHCB1/b1_with_newTunes/twiss.dat"
    s = get_scatter_for_df(tfs.read_tfs(data), x_col="S", y_col="BETX", e_col=None, name="twiss.dat", legendgroup="1")
    plotly_wrapper([s], get_layout(), name="outplot")


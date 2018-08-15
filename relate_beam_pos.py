""" Circleshift the beampositions of B1 and B2 to be comparable """

from tfs_files import tfs_pandas as tfs

LENGTH = {
    "lhc_runII_2017": 26658.8832,
}


def merge(df_a, df_b,  suffixes, columns=None, index_rep=None):
    """ Merges two tfs into one by index, using S of the first."""
    df_a, df_b = _get_dfs(df_a, df_b)
    df_a, df_b = _replace_in_index(df_a, df_b, index_rep)

    if columns is None:
        columns = df_a.columns.tolist()
        [columns.pop(idx) for idx, val in enumerate(columns) if val == "S"]
    elif not isinstance(columns, list):
        columns = [columns]

    df = df_a.loc[:, ["S"] + columns].merge(df_b.loc[:, columns],
                                            left_index=True, right_index=True,
                                            how="inner", suffixes=suffixes)
    return df


def shift(df_a, df_b, accel, column="S", index_rep=None):
    """ Shifts the values of 'column' in df_b to align with df_a """
    df_a, df_b = _get_dfs(df_a, df_b)
    old_idx = df_b.index.tolist()
    df_a, df_b = _replace_in_index(df_a, df_b, index_rep)

    length = LENGTH[accel]  # if you want to be fance, replace by accel-class

    #TODO: Finish this

def _replace_all(list_s, rep, by):
    for idx, s in enumerate(list_s):
        list_s[idx] = s.replace(rep, by)
    return list_s


def _replace_in_index(df_a, df_b, index_rep):
    if index_rep:
        if not isinstance(index_rep, list):
            index_rep = [index_rep]
        lir = len(index_rep)

        for key in index_rep[0]:
            df_a.index = _replace_all(df_a.index.tolist(), key, index_rep[0][key])

        for key in index_rep[1 % lir]:
            df_b.index = _replace_all(df_b.index.tolist(), key, index_rep[1 % lir][key])
    return df_a, df_b


def _get_dfs(df_a, df_b):
    if isinstance(df_a, basestring):
        df_a = tfs.read_tfs(df_a)

    if isinstance(df_b, basestring):
        df_b = tfs.read_tfs(df_b)
    return df_a, df_b


if __name__ == "__main__":
    b1x = '/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM1X.tfs'
    b2y = '/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM2Y.tfs'

    df_1x2y = merge(b1x, b2y, suffixes=("_b1", "_b2"),
              index_rep=[{'.b1': "", ".B1": ""}, {'.b2': "", ".B2": ""}])
    tfs.write_tfs('/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM1X_2Y.tfs', df_1x2y,  save_index=True)

    b1y = '/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM1Y.tfs'
    b2x = '/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM2X.tfs'

    df_1y2x = merge(b1y, b2x, suffixes=("_b1", "_b2"),
              index_rep=[{'.b1': "", ".B1": ""}, {'.b2': "", ".B2": ""}])
    tfs.write_tfs('/media/jdilly/Storage/Jupyter/jupyter2slides/static/Beta_Flatoptics_data/BEAM1Y_2X.tfs', df_1y2x, save_index=True)
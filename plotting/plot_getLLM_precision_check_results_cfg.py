"""
Example config file for plot_getLLM_check_results.py
Will run when you specify _MADX_TRACKING as the name of the output-folder of getLLM_check_results.py
Plots are not shown but saved into opt['dir']['plots']
"""
import os

_MADX_TRACKING = 'test_getllm_temp'
_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
_SRC = os.path.join(_ROOT, 'GetLLM')

opt = {
    'filename': 'ALLBPMs',

    # ================ Paths ==================
    'dir': {
        'model': os.path.join(_SRC, _MADX_TRACKING),   # folder containing model data
        'src': os.path.join(_SRC, _MADX_TRACKING),  # parent folder of results in subfolders (s. prefix)
        'plots': os.path.join(_SRC, _MADX_TRACKING, 'plots'),  # output folder for plots
    },

    'prefix': {
        'getllm': 'getllm_',    # gellm-subfolder prefix
        'results': 'results_',  # results-subfolder prefix
    },

    # ================ Analysis Parameters ==================
    'analysis': {
        'methods': ['sussix', 'harpy_svd', 'harpy_fast'],
        'compare_to': 'model',  # method or 'model' or ''
    },

    # ================ Plot Parameters ==================
    "plot": {
        'style': 'presentation',     # 'presentation' or 'standard'
        'ext': ['pdf', 'svg'],       # file-types to export to
        'legend': True,              # activates a legend
        'manual_style': {            # add manual rc-style-options to the figure
            u'figure.figsize': [20.48, 5.76],
            u'lines.linestyle': u'-',
            u'axes.grid.axis': u'y',
        },
    },
}

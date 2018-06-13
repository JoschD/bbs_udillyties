from __future__ import print_function
from predefined import get_vertical_line
from widgets import get_rerange_button
import json
import numpy as np


# Limit Related ##############################################################


def get_y_limits(list_df, columns, bpms=None, scaled=False):
    """ Get the min and max values in the columns of dataframes of list_df

     Use bpms to get them at positions (column "S") between certain bmps only.
     """
    low_lim, up_lim = None, None
    for df in list_df:
        for col in columns:
            try:
                if bpms is None:
                    l = df.loc[:, col].min()
                    u = df.loc[:, col].max()
                else:
                    if df.loc[bpms[0], "S"] > df.loc[bpms[1], "S"]:
                        l = min(df.loc[bpms[0]:, col].min(), df.loc[:bpms[1], col].min())
                        u = max(df.loc[bpms[0]:, col].max(), df.loc[:bpms[1], col].max())
                    else:
                        l = df.loc[bpms[0]:bpms[1], col].min()
                        u = df.loc[bpms[0]:bpms[1], col].max()
            except KeyError:
                pass
            else:
                low_lim = l if low_lim is None else min(l, low_lim)
                up_lim = u if up_lim is None else max(u, up_lim)

    limits = [low_lim, up_lim]
    if scaled:
        limits = scale_limits(limits)
    return limits


def scale_limits(lim, factor=0.05):
    """ Scale the limits in lim by the factor (Default: 5%)"""
    d = (lim[1] - lim[0]) * factor
    return lim[0] - d, lim[1] + d


# IP related functions #######################################################


def get_ip_gui_elements(df_list, columns):
    """ Gets approximate IP lines, buttons to set view and y_limits of IPs """
    ip_dict = find_close_bmps_to_ips(df_list[0])
    lines = []
    y_limits = get_y_limits(df_list, columns)
    y_limits = scale_limits(y_limits)

    buttons = dict()
    for ip in ip_dict:
        bpm_lim = []
        ip_x_lim = []

        for side in ip_dict[ip]:
            x = ip_dict[ip][side]['s']
            name = ip_dict[ip][side]['name']
            lines.append(get_vertical_line(x, y_limits, name))
            bpm_lim.append(name)
            ip_x_lim.append(x)

        ip_y_lim = get_y_limits(df_list, columns, bpm_lim)
        ip_y_lim = scale_limits(ip_y_lim)

        if ip_x_lim[0] < ip_x_lim[1]:
            ip_x_lim = scale_limits(ip_x_lim)
            buttons[ip] = get_rerange_button(ip_x_lim, ip_y_lim, "IP" + ip)
        else:
            super_x_min = min([df["S"].min() for df in df_list])
            super_x_max = max([df["S"].max() for df in df_list])

            ip_x_lim_start = scale_limits([super_x_min, ip_x_lim[1]])
            ip_x_lim_end = scale_limits([ip_x_lim[0], super_x_max])
            buttons[ip] = get_rerange_button(ip_x_lim_end, ip_y_lim, "IP" + ip)
            buttons[ip + ".5"] = get_rerange_button(ip_x_lim_start, ip_y_lim, "IP" + ip + ".5")

    buttons = [buttons[key] for key in sorted(buttons.keys())]
    return lines, buttons, y_limits


def ip_dict2name(ip_dict, ip, side):
    """ Builds the bpm-name from IP dict (see find_close_bpms_to_ips). """
    return "BPM." + str(ip_dict[ip][side]) + side + str(ip)


def find_close_bmps_to_ips(df):
    """ Finds (by name) the bpms closest to the IPs present in df """
    ips = dict.fromkeys([str(i) for i in range(1, 9)])
    for bpm in df.index:
        if bpm.lower().startswith("bpm."):
            bpm_short = bpm.lower().replace("bpm.", "")
            ip = bpm_short[-1]
            side = bpm_short[-2].upper()
            dist = int(bpm_short[:-2])
            if ips[ip] is None:
                ips[ip] = {'L': None, 'R': None}
                ips[ip][side] = {'dist': dist, 'name': bpm, 's': df.loc[bpm, "S"]}
            else:
                if ips[ip][side] is None:
                    ips[ip][side] = {'dist': dist, 'name': bpm, 's': df.loc[bpm, "S"]}
                elif ips[ip][side]['dist'] > dist:
                    ips[ip][side] = {'dist': dist, 'name': bpm, 's': df.loc[bpm, "S"]}
                else:
                    pass
    return ips


# Other ######################################################################


def rms_from_json_plots(file, show=True, results_per_line=1):
    def _rms(a):
        return np.sqrt(np.mean(np.square(a)))

    with open(file, "r") as f:
        fig = json.loads(f.read())

    results = {}
    for line in fig["data"]:
        results[line["name"]] = {}
        results[line["name"]]["rms"] = _rms(line["y"])

    if show:
        rms_from_json_dict(results, results_per_line)

    return results


def rms_from_json_dict(file_or_dict, results_per_line=1):
    try:
        with open(file_or_dict, "r") as f:
            d = json.loads(f.read())
    except TypeError:
        d = file_or_dict

    intro_str = "RMS: "
    max_name = max([len(name) for name in d])
    line_str = "{:" + str(max_name) + "s}: {:.3e}, "
    break_str = "\n" + "    "

    try:
        results_per_line[0]
    except TypeError:
        results_per_line = [results_per_line]
    rpl_idx = 0
    rpl = results_per_line[rpl_idx]

    out = break_str
    for idx, name in enumerate(sorted(d.keys())):
        try:
            value = d[name]["rms_f"]
            intro_str = "RMS (filtered): "
        except KeyError:
            value = d[name]["rms"]
        out += line_str.format(name, value)
        if (idx+1) % rpl == 0:
            rpl_idx += 1
            rpl += results_per_line[rpl_idx % len(results_per_line)]
            out += break_str
    print(intro_str + out)








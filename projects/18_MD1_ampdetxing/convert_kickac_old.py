from tfs_files import tfs_pandas as tfs
import datetime
import calendar


def make_kickac_compatible(path):
    df = tfs.read_tfs(path)
    unix_time = [calendar.timegm(datetime.datetime.strptime(t, "%Y-%m-%d__%H:%M:%S.%f").timetuple())
                 for t in df.loc[:, "KickTime"]]
    df = df.drop(["LocalTime", "KickTime"], axis=1)
    df.insert(0, "TIME", unix_time)
    tfs.write_tfs(path + "_conv", df)


if __name__ == '__main__':
    make_kickac_compatible("/media/jdilly/Storage/Projects/NOTE.18.MD1_Amplitude_Detuning/overleaf/results/2018_commissioning/B1_crossing_H_amp_det.dat")

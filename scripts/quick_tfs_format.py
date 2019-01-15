from tfs_files import tfs_pandas as tfs

files = [
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/on_virgin/b1.diff.bumps1.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/on_virgin/b1.diff.bumps2.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/on_virgin/b2.diff.bumps1.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/on_virgin/b2.diff.bumps2.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/with_other_corrections/b1.diff.bumps1.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/with_other_corrections/b1.diff.bumps2.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/with_other_corrections/b2.diff.bumps1.diff_betastarXY.tfs",
"/media/jdilly/Storage/Projects/STUDY.18.ions.ip2_problems/results.bfpp_bumps_wise/images/with_other_corrections/b2.diff.bumps2.diff_betastarXY.tfs",
]



if __name__ == '__main__':
    for filename in files:
        df = tfs.read_tfs(filename, index="NAME")
        df = df.applymap(lambda x: "{: 5.1e}".format(x).replace("e-0", " \\cdot 10^-").replace("e+0", " \\cdot 10^+"))
        tfs.write_tfs(filename + "_format", df, save_index="NAME")
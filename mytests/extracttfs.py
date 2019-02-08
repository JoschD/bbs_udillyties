from tfs_files import tfs_pandas as tfs
import os

src = "/home/jdilly/link_afs_work/private/STUDY.18.LHC.MD3311/error_check/results_per_seed/seed_0001/output_3030.errors_B4_B5_A5_B6_A6.in_all_IPs.noXing"
df1 = tfs.read_tfs(os.path.join(src, "Beam1.errors")).loc[:, ["NAME", "K3L", "K4L", "K5L", "K4SL", "K5SL"]]
df2 = tfs.read_tfs(os.path.join(src, "Beam2.errors")).loc[:, ["NAME", "K3L", "K4L", "K5L", "K4SL", "K5SL"]]

tfs.write_tfs(os.path.join(src, "Beam1_shorter.errors"), df1)
tfs.write_tfs(os.path.join(src, "Beam2_shorter.errors"), df2)

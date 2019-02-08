import os
from extract_online_model import main
TIME = "2018-06-16 15:30:00.000"
CWD = "/afs/cern.ch/user/j/jdilly/extractor/"
main(function="overview", time=TIME, cwd=os.path.join(CWD, "entrypointtest"), server="cs-ccr-dev3")

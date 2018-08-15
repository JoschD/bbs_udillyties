
def get_tfs_name(folder, rdt, state, beam, error_src):
    return os.path.join(folder, "collected_results.{id:s}.tfs".format(
        id=get_id(rdt, state, beam, error_src)))


def get_plot_file(folder, rdt, state, beam, error_src, extension):
    return os.path.join(folder, "{id:s}_errors{extension:s}".format(
        id=get_id(rdt, state, beam, error_src),
        extension=extension))

# Naming Helper ################################################################


def get_id(rdt, state, beam, error_src):
    return "B{beam:d}.F{rdt:s}.{state:s}.{error_src:s}".format(
        rdt=rdt,
        state=get_proper_state(state, beam),
        beam=get_proper_beam(state, beam),
        error_src=error_src,
    )


def get_rdt_column(rdt):
    return "GNFA_{}_{}_{}_{}_0_0".format(rdt[0], rdt[1], rdt[2], rdt[3])

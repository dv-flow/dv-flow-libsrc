import os

def dvfm_packages():
    src_dir = os.path.dirname(os.path.abspath(__file__))

    return {
        'src': os.path.join(src_dir, "flow.dv"),
    }
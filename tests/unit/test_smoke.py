import os
import pytest
from pytest_dfm import *


def test_smoke(tmpdir, dvflow):
    flow_dv = """
package:
  name: foo

  tasks:
  - name: files
    uses: src.FileList
    with:
      file: filelist.f
      filetype: systemVerilogSource
"""

    filelist_f = """
file1.svh
file2.svh
file3.svh
"""

    with open(os.path.join(tmpdir, "flow.dv"), "w") as fp:
        fp.write(flow_dv)
        
    with open(os.path.join(tmpdir, "filelist.f"), "w") as fp:
        fp.write(filelist_f)


    status,out = dvflow.runFlow(
        os.path.join(tmpdir, "flow.dv"), 
        "foo.files")

    assert status == 0
    assert len(out.output) == 1
    assert len(out.output[0].files) == 3

    assert out.output[0].basedir == str(tmpdir)
    print("Files: %s" % out.output[0].files)
    for file in ("file1.svh", "file2.svh", "file3.svh"):
        assert file in out.output[0].files


    pass
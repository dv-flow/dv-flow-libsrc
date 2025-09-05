import os
import pytest
from pytest_dfm import *

def write_flow(tmpdir, include=None, exclude=None):
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
    if include is not None:
        flow_dv += "      include: %s\n" % include
    if exclude is not None:
        flow_dv += "      exclude: %s\n" % exclude

    with open(os.path.join(tmpdir, "flow.dv"), "w") as fp:
        fp.write(flow_dv)

def write_filelist(tmpdir, files):
    with open(os.path.join(tmpdir, "filelist.f"), "w") as fp:
        fp.write("\n".join(files) + "\n")

def test_filelist_no_include_exclude(tmpdir, dvflow):
    write_flow(tmpdir)
    write_filelist(tmpdir, ["a.txt", "b.log", "c.md"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert sorted(out.output[0].files) == ["a.txt", "b.log", "c.md"]

def test_filelist_include(tmpdir, dvflow):
    write_flow(tmpdir, include="['*.txt']")
    write_filelist(tmpdir, ["a.txt", "b.log", "c.md"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert out.output[0].files == ["a.txt"]

def test_filelist_exclude(tmpdir, dvflow):
    write_flow(tmpdir, exclude="['*.log']")
    write_filelist(tmpdir, ["a.txt", "b.log", "c.md"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert sorted(out.output[0].files) == ["a.txt", "c.md"]

def test_filelist_include_exclude(tmpdir, dvflow):
    write_flow(tmpdir, include="['*.txt', '*.md']", exclude="['*/a.txt']")
    write_filelist(tmpdir, ["a.txt", "b.log", "c.md"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert out.output[0].files == ["c.md"]

def test_filelist_include_no_match(tmpdir, dvflow):
    write_flow(tmpdir, include="['*.md']")
    write_filelist(tmpdir, ["a.txt", "b.log"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert len(out.output) == 0 or len(out.output[0].files) == 0

def test_filelist_exclude_all(tmpdir, dvflow):
    write_flow(tmpdir, exclude="['*']")
    write_filelist(tmpdir, ["a.txt", "b.log"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files")
    assert status == 0
    assert len(out.output) == 0 or len(out.output[0].files) == 0

def test_filelist_env_var(tmpdir, dvflow):
    import os
    # Set env variable in both dvflow and os.environ
    env = os.environ.copy()
    env["FOO"] = "envdir"

    # Create the directory and file
    envdir = os.path.join(tmpdir, "envdir")
    os.makedirs(envdir)
    with open(os.path.join(envdir, "file.txt"), "w") as fp:
        fp.write("test")
    write_flow(tmpdir)
    write_filelist(tmpdir, ["$FOO/file.txt"])
    status, out = dvflow.runFlow(os.path.join(tmpdir, "flow.dv"), "foo.files", env=env)
    assert status == 0
    assert sorted(out.output[0].files) == ["envdir/file.txt"]

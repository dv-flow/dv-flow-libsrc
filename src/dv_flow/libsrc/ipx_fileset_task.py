import asyncio
import os
from dv_flow.libsrc.ipx_fileset import IPXFileSet

from dv_flow.mgr import TaskRunCtxt, TaskDataInput, TaskDataResult

async def IPXFileSetTask(ctxt: TaskRunCtxt, input: TaskDataInput) -> TaskDataResult:
    status = 0
    output = []

    path = input.params.file
    if not os.path.isabs(path):
        path = os.path.join(input.srcdir, path)

    filesets = input.params.filesets if hasattr(input.params, "filesets") else []
    print("IPXFileSetTask: filesets param value =", filesets)
    ipx = IPXFileSet(path, filesets)
    result = ipx.run()

    from dv_flow.mgr import FileSet
    for fs in result:
        basedir = os.path.dirname(path)
        # FileSet(basedir, filetype, files)
        filetype = fs["files"][0]["type"] if fs["files"] and "type" in fs["files"][0] else None
        files = [f["name"] for f in fs["files"]]
        file_set = FileSet(
            basedir=basedir,
            filetype=filetype,
            files=files
        )
        file_set.name = fs["name"]
        output.append(file_set)

    return TaskDataResult(
        status=status,
        output=output
    )

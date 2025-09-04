import glob
import logging
import os
import fnmatch
from typing import List
from dv_flow.mgr import TaskRunCtxt, TaskDataInput, TaskDataResult, FileSet
from fltools import FilelistParser


async def FileList(ctxt : TaskRunCtxt, input : TaskDataInput) -> TaskDataResult:
    status = 0
    output : List[FileSet] = []

    path = input.params.file
    if not os.path.isabs(path):
        path = os.path.join(input.srcdir, path)
    print("Path: %s (%s)" % (path, input.params.file))

    file = glob.glob(path, recursive=True)

    if file is None or len(file) == 0:
        raise Exception("Input file \"%s\" did not match" % input.params.file)
    elif not os.path.isfile(file[0]):
        raise Exception("Input file \"%s\" does not exist" % file[0])


    parser = FilelistParser()
    paths = parser.parse(
        path=file[0],
        relative_path_basedir=os.path.dirname(file[0])
    )

    filelist = FileSet(
        basedir=os.path.dirname(file[0]),
        filetype=input.params.filetype)

    include_patterns = getattr(input.params, "include", [])
    exclude_patterns = getattr(input.params, "exclude", [])

    def matches_any(filename, patterns):
        return any(fnmatch.fnmatch(filename, pat) for pat in patterns)

    if paths is not None:
        for path in paths:
            filename = path.resolve(expand_env=False)
            if filename.startswith(filelist.basedir):
                filename = filename[len(filelist.basedir)+1:]
            # Exclude filtering
            if matches_any(filename, exclude_patterns):
                continue
            # Include filtering
            if include_patterns and not matches_any(filename, include_patterns):
                continue
            filelist.files.append(filename)
    else:
        status = 1

    output.append(filelist)

    return TaskDataResult(
        status=status,
        output=output
    )

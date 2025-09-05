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

    file = glob.glob(path, recursive=True)

    if file is None or len(file) == 0:
        raise Exception("Input file \"%s\" did not match" % input.params.file)
    elif not os.path.isfile(file[0]):
        raise Exception("Input file \"%s\" does not exist" % file[0])


    parser = FilelistParser(env=ctxt.env)
    paths = parser.parse(
        path=file[0],
        relative_path_basedir=os.path.dirname(file[0])
    )

    basedir = os.path.dirname(file[0])

    include_patterns = getattr(input.params, "include", [])
    exclude_patterns = getattr(input.params, "exclude", [])

    def matches_any(filename, patterns):
        return any(fnmatch.fnmatch(filename, pat) for pat in patterns)

    if paths is not None:
        full_paths = []
        incdirs = set()
        for path in paths:
            # Detect +incdir+<path> tokens
            if hasattr(path, "img") and isinstance(path.img, str) and path.img.startswith("+incdir+"):
                # Strip +incdir+ prefix before resolving
                incdir_img = path.img
                while incdir_img.startswith("+incdir+"):
                    incdir_img = incdir_img[len("+incdir+") :]
                # Use resolve to expand env vars on the stripped value
                if hasattr(path, "resolve"):
                    # Temporarily patch path.img for resolve
                    orig_img = path.img
                    path.img = incdir_img
                    incdir_path = path.resolve(expand_env=True)
                    path.img = orig_img
                else:
                    incdir_path = incdir_img
                # Always use only the leaf directory name for incdir
                leaf_incdir = os.path.basename(os.path.normpath(incdir_path))
                incdirs.add(leaf_incdir)
                continue

            filename = path.resolve(expand_env=True)
            if not os.path.isabs(filename):
                filename = os.path.join(basedir, filename)

            # Exclude filtering
            if matches_any(filename, exclude_patterns):
                continue
            # Include filtering
            if include_patterns and not matches_any(filename, include_patterns):
                continue

            full_paths.append(filename)

        if len(full_paths) > 0:
            if len(full_paths) > 1:
                common_base = os.path.commonpath(full_paths)
            else:
                common_base = basedir

            fs = FileSet(basedir=common_base, filetype=input.params.filetype)
            if input.params.add_incdir:
                fs.incdirs.append(".")
            # Add detected incdirs as just the leaf directory name
            for incdir in incdirs:
                if incdir not in fs.incdirs:
                    fs.incdirs.append(incdir)

            for f in full_paths:
                fs.files.append(f[len(fs.basedir)+1:])
            output.append(fs)
    else:
        status = 1


    return TaskDataResult(
        status=status,
        output=output
    )

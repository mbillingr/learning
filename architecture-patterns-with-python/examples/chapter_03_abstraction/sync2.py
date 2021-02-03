import hashlib
import os
import shutil
from pathlib import Path


def sync(reader, filesystem, source_root, dest_root):
    source_hashes = reader(source_root)
    dest_hashes = reader(dest_root)

    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source_root) / filename
            destpath = Path(dest_root) / filename
            filesystem.copy(sourcepath, destpath)

        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest_root) / dest_hashes[sha]
            newdestpath = Path(dest_root) / filename
            filesystem.move(olddestpath, newdestpath)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(Path(dest_root) / filename)


BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open('rb') as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()

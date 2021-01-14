from sync2 import sync
from pathlib import Path


class FakeFileSystem(list):
    def copy(self, src, dest):
        self.append(('COPY', src, dest))

    def move(self, src, dest):
        self.append(('MOVE', src, dest))

    def delete(self, dest):
        self.append(('DELETE', dest))


def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source = {'hash1': 'my-file'}
    dest = {}
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}
    sync(reader.pop, filesystem, "/source", "/dest")

    assert filesystem == [('COPY', Path('/source/my-file'), Path('/dest/my-file'))]


def test_whan_a_file_has_been_renamed_in_the_source():
    source = {'hash1': 'renamed-file'}
    dest = {'hash1': 'original-file'}
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}
    sync(reader.pop, filesystem, "/source", "/dest")

    assert filesystem == [('MOVE', Path('/dest/original-file'), Path('/dest/renamed-file'))]

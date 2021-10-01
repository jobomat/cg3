"""
This module contains classes for creation of virtual directory structures.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from shutil import copyfile
from typing import List, Tuple
from pathlib import Path


@dataclass
class File:
    """Class of a virtual file to use with virtual directories (class Dir)."""
    name: str
    template: str = ""
    find_replace: List[Tuple[str]] = field(default_factory=list)

    def create(self, path: Path, template_dir: Path) -> None:
        """Create a real file from the virtual representation.

        :param path: The path where the file will be created.
        :type path: Path
        :param template_dir: A directory where the file 'self.template' can be found.
        :type template_dir: Path
        """
        filepath = path / self.name
        if self.template:
            template_file = template_dir / self.template
            if template_file.exists():
                print(f"Using '{template_file}' as template file.")
                if self.find_replace:
                    with template_file.open() as t_file:
                        content = t_file.read()
                    for find, repl in self.find_replace:
                        content = content.replace(find, repl)
                        print(f"Replacing '{find}' with '{repl}'")
                    with filepath.open("w") as f_path:
                        f_path.write(content)
                    print(f"Writing modified template to '{filepath}'.")
                    return
                copyfile(str(template_file), str(filepath))
                print(f"Copying unmodified template to '{filepath}'")
                return
            print(f"Template file '{template_file}' not found.")

        with filepath.open("w") as f:
            f.write("")
        print(f"File '{filepath}' created as empty text file.")


@dataclass
class Dir:
    """Class for building virtual directory trees."""
    name: str = ""
    dirs: List[Dir] = field(default_factory=list)
    files: List[File] = field(default_factory=list)

    def add_new_dir(self, name: str) -> None:
        """Add a virtual subdirectory."""
        self.dirs.append(Dir(name))

    def add_new_dirs(self, dirs: List[str]) -> None:
        """Add multiple virtual subdirectories"""
        for directory in dirs:
            self.add_new_dir(directory)

    def add_new_file(self, name: str, template: str = "") -> None:
        """Add a virtual file."""
        self.files.append(File(name, template))

    def add_new_files(self, files: List[str]) -> None:
        """Add multiple virtual files."""
        for file in files:
            self.add_new_file(file)

    def create(self, path: Path = Path.home(), template_dir: Path = None) -> None:
        """Create a real diretroy structure out of the virtual one.

        :param path: The path where the structure will be created, defaults to Path.home()
        :type path: Path, optional
        :param template_dir: The path that contains templates for virtual files, defaults to None
        :type template_dir: Path, optional
        """
        path = path / self.name
        path.mkdir()
        print(f"mkdir {path}")
        for file in self.files:
            file.create(path, template_dir)
        for directory in self.dirs:
            directory.create(path, template_dir)

    def read_from_path(self, path: Path) -> Dir:
        """Read an existing directory structure and
        create a virtual structure out of it. """
        self.name = path.name
        for item in path.iterdir():
            if item.is_dir():
                directory = Dir().read_from_path(item)
                self.dirs.append(directory)
            elif item.is_file():
                self.add_new_file(item.name)
        return self

    def as_dict(self) -> dict:
        """Returns a dictionary of the virtual directory structure."""
        return {
            "name": self.name,
            "files": [
                {
                    "name": f.name,
                    "template": f.template,
                    "find_replace": f.find_replace
                } for f in self.files
            ],
            "dirs": [d.as_dict() for d in self.dirs]
        }

    def from_dict(self, dir_dict: dict) -> Dir:
        """"Create a virtual Dir structure from dictionary."""
        self.name = self.name or dir_dict["name"]
        self.files = [
            File(name=f.name, template=f.template, find_replace=f.find_replace)
            for f in dir_dict["files"]    
        ]
        self.dirs = [
            Dir().from_dict(d) for d in dir_dict["dirs"]
        ]
        return self

    def get_file(self, name: str) -> File:
        """Get the virtual file object called 'name' in the current Dir object."""
        try:
            return [f for f in self.files if f.name == name][0]
        except IndexError:
            raise ValueError(f"File {name} not in {self.name}") from None

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            dirs = super().__getattribute__("dirs")
            name = super().__getattribute__("name")
            directory = [d for d in dirs if d.name == attr]
            try:
                return directory[0]
            except IndexError:
                raise ValueError(f"{name} contains no Dir named {attr}") from None



# d = Dir("bob")
# d.add_new_dirs(["versions", "release_history"])
# d.versions.add_new_dirs(["mod", "rig", "shade", "anim", "render"])
# d.versions.mod.add_new_files(["test.ma", "test2.txt"])
# d.versions.mod.get_file("test.ma").template = "test_template.ma"
# d.versions.mod.get_file("test.ma").find_replace.append(("##TIME##", "film"))
# d.versions.mod.get_file("test.ma").find_replace.append(
#     ("##OCIO_PATH##", "C:/OCIO/aces_1.1/config.ocio"))

# d.create(Path.home() / "Documents", Path.home() / "Documents")

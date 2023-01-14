from pathlib import Path
from src.section import Section


class IniWriter:
    def __init__(self) -> None:
        pass

    @classmethod
    def write_sections(cls, path: Path, root_sections: list[Section], override=True):
        to_write = "".join([section.get_writable_string() for section in root_sections])
        cls.write_file(path, to_write, override)

    @classmethod
    def write_file(cls, path: Path, to_write: str, override=True):
        if not override:
            if path.exists():
                raise FileExistsError("The file already exists!")
        with open(path, 'w') as f:
            f.write(to_write)
            f.close()

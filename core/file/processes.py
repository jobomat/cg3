from pathlib import Path


def search_and_replace_in_file(file: str, search_replace: dict, py3_exe: str):
    fp = Path(file)
    with fp.open("r") as f:
        text = f.read()
    for s, r in search_replace.items():
        text = text.replace(s, r)
    return text


def write_text_to_file(text:str, filepath: str):
    fp = Path(filepath)
    with fp.open("w") as f:
        f.write(text)

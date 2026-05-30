"""Generate README.md from documentation files."""

from typing import Optional

DOCS_PATH = "./docs/source/"
ELEMENTS = [
    ("badges", "", ""),
    ("home", "", ""),
]


def extract_content(file_path: str, start_marker: Optional[str] = None, end_marker: Optional[str] = None) -> str:
    """Extract content between markers from a file."""
    with open(file_path, "r") as f:
        content = f.read()

    if start_marker or end_marker:
        start = content.find(str(start_marker))
        end = content.find(str(end_marker))
        if start != -1 and end != -1:
            return content[start + len(str(start_marker)) : end].strip()
    return content


def generate_readme() -> None:
    """Generate README.md from documentation files."""
    readme = []

    for element in ELEMENTS:
        content = extract_content(DOCS_PATH + element[0] + ".md", element[1], element[2])
        readme.append(content)

    with open("README.md", "w") as f:
        f.write("\n".join(readme))


if __name__ == "__main__":
    generate_readme()

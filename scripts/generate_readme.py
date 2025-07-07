"""Generate README.md from documentation files."""

DOCS_PATH = "./docs/source/"
ELEMENTS = [
    ("badges", "", ""),
    ("home", "", ""),
    ("guides", "", ""),
]


def extract_content(file_path: str, start_marker: str = "", end_marker: str = "") -> str:
    """Extract content between markers from a file."""
    with open(file_path, "r") as f:
        content = f.read()

    if start_marker or end_marker:
        start = content.find(start_marker)
        end = content.find(end_marker)
        if start != -1 and end != -1:
            return content[start + len(start_marker) : end].strip()
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

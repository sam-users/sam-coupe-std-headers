#!/usr/bin/env python3
"""Generate '_l' variants of .z80/.z80s files with label names lowercased.

For every .z80 / .z80s source file in the project root whose name doesn't
already end in '_l', this writes a sibling '<name>_l.<ext>' file in which
every assembly label (an identifier defined as `name:` at the start of a
line, plus every later reference to that same identifier) is rewritten in
lowercase. Quoted strings and ';' comments are left untouched, so labels
mentioned there keep their original casing.
"""

import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_GLOBS = ("*.z80", "*.z80s")

LABEL_DEFINITION_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:")
IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def split_into_segments(line):
    """Split a line into (text, is_code) chunks.

    Quoted strings ('...' or "...") and ';' comments are marked as
    non-code so label rewriting skips over them entirely.
    """
    segments = []
    code_start = 0
    index = 0
    length = len(line)
    while index < length:
        char = line[index]
        if char in "\"'":
            if index > code_start:
                segments.append((line[code_start:index], True))
            quote = char
            end = index + 1
            while end < length and line[end] != quote:
                end += 1
            end = min(end + 1, length)
            segments.append((line[index:end], False))
            index = end
            code_start = index
        elif char == ";":
            if index > code_start:
                segments.append((line[code_start:index], True))
            segments.append((line[index:], False))
            return segments
        else:
            index += 1
    if code_start < length:
        segments.append((line[code_start:], True))
    return segments


def find_label_names(lines):
    labels = set()
    for line in lines:
        segments = split_into_segments(line)
        if segments and segments[0][1]:
            match = LABEL_DEFINITION_RE.match(segments[0][0])
            if match:
                labels.add(match.group(1))
    return labels


def lowercase_known_labels(text, labels):
    return IDENTIFIER_RE.sub(
        lambda m: m.group(0).lower() if m.group(0) in labels else m.group(0), text
    )


def lowercase_labels_in_file(source_path, labels):
    text = source_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    rewritten_lines = []
    for line in lines:
        rewritten_lines.append(
            "".join(
                lowercase_known_labels(chunk, labels) if is_code else chunk
                for chunk, is_code in split_into_segments(line)
            )
        )

    destination_path = source_path.with_name(f"{source_path.stem}_l{source_path.suffix}")
    destination_path.write_text("".join(rewritten_lines), encoding="utf-8")
    return destination_path


def find_source_files():
    files = []
    for pattern in SOURCE_GLOBS:
        for path in ROOT_DIR.glob(pattern):
            if not path.stem.endswith("_l"):
                files.append(path)
    return sorted(files)


def main():
    source_paths = find_source_files()

    # Labels are gathered across every source file up front (rather than
    # per-file) because files reference labels defined in others, e.g.
    # colours.z80 uses COLOUR_RED_1, which is defined in base.z80.
    labels = set()
    for source_path in source_paths:
        lines = source_path.read_text(encoding="utf-8").splitlines(keepends=True)
        labels.update(find_label_names(lines))

    print(f"Found {len(labels)} unique labels across {len(source_paths)} files")

    for source_path in source_paths:
        destination_path = lowercase_labels_in_file(source_path, labels)
        print(f"{source_path.name} -> {destination_path.name}")


if __name__ == "__main__":
    main()

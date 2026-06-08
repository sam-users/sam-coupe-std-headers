#!/usr/bin/env python3
"""List every EQU-defined label across the project's .z80/.z80s sources as a table.

Scans each non-'_l' .z80 / .z80s source file in the project root, collects
every label defined via an EQU directive (e.g. `CLUT: EQU 248`), and prints
them as a Markdown table sorted alphabetically by label name. Columns:
Label, Source File, Definition (the EQU value). Labels that aren't EQU
definitions (e.g. program labels) are omitted.
"""

import re

from generate_lowercase_labels import find_source_files, split_into_segments

LABEL_EQU_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*EQU\s+(.+?)\s*$", re.IGNORECASE
)


def find_equ_labels(source_path):
    entries = []
    for line in source_path.read_text(encoding="utf-8").splitlines():
        code_text = "".join(chunk for chunk, is_code in split_into_segments(line) if is_code)
        match = LABEL_EQU_RE.match(code_text)
        if match:
            entries.append((match.group(1), source_path.name, match.group(2)))
    return entries


def render_markdown_table(rows):
    header = ("Label", "Source File", "Definition")
    columns = range(len(header))
    widths = [max(len(header[i]), max((len(row[i]) for row in rows), default=0)) for i in columns]

    def render_row(values):
        return "| " + " | ".join(values[i].ljust(widths[i]) for i in columns) + " |"

    lines = [render_row(header), render_row(["-" * widths[i] for i in columns])]
    lines.extend(render_row(row) for row in rows)
    return "\n".join(lines)


def main():
    rows = []
    for source_path in find_source_files():
        rows.extend(find_equ_labels(source_path))

    rows.sort(key=lambda row: row[0].lower())

    print(render_markdown_table(rows))
    print(f"\n{len(rows)} EQU-defined labels across the project")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""repo2txt - Dump a repository or directory into a single text file."""

__version__ = "1.1.0"

import argparse
import fnmatch
import os
import sys

TEXT_CHARS = bytearray(({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100))) - {0x7f})


def is_binary(s: bytes) -> bool:
    return bool(s.translate(None, TEXT_CHARS))


def load_gitignore(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    if not os.path.exists(gitignore_path):
        return []
    try:
        with open(gitignore_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = [line.strip() for line in f]
        return [p.rstrip('/') for p in lines if p and not p.startswith('#')]
    except OSError:
        return []


def should_ignore(path, ignore_patterns, cache):
    if path in cache:
        return cache[path]
    basename = os.path.basename(path)
    result = any(
        fnmatch.fnmatch(candidate, pattern)
        for pattern in ignore_patterns
        for candidate in (path, basename)
    )
    cache[path] = result
    return result


def generate_tree(directory, ignore_patterns, cache, strip_prefix='', indent='', visited=None):
    if visited is None:
        visited = set()
    real = os.path.realpath(directory)
    if real in visited:
        return ''
    visited.add(real)

    try:
        items = os.listdir(directory)
    except OSError as e:
        print(f"Warning: {directory}: {e}", file=sys.stderr)
        return ''

    items = sorted(item for item in items
                   if not should_ignore(os.path.join(directory, item), ignore_patterns, cache))

    display_path = directory
    if strip_prefix and directory.startswith(strip_prefix):
        display_path = directory[len(strip_prefix):].lstrip('/') or '.'
    print(f"Generating tree for {display_path}: {len(items)} items...", file=sys.stderr)

    parts = []
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        corner = '\u2514' if is_last else '\u251c'
        item_path = os.path.join(directory, item)
        if os.path.islink(item_path):
            parts.append(f"{indent}{corner}\u2500\u2500 {item} -> [symlink]\n")
        elif os.path.isdir(item_path):
            parts.append(f"{indent}{corner}\u2500\u2500 {item}\n")
            child_indent = indent + ('   ' if is_last else '\u2502  ')
            parts.append(generate_tree(item_path, ignore_patterns, cache, strip_prefix,
                                       child_indent, visited))
        else:
            parts.append(f"{indent}{corner}\u2500\u2500 {item}\n")
    return ''.join(parts)


def dump_files(directory, ignore_patterns, include_headers, binary, out_file,
               cache, strip_prefix='', done=None, visited=None):
    if done is None:
        done = set()
    if visited is None:
        visited = set()
    real = os.path.realpath(directory)
    if real in visited:
        return
    visited.add(real)

    try:
        items = os.listdir(directory)
    except OSError as e:
        print(f"Warning: {directory}: {e}", file=sys.stderr)
        return

    items = sorted(item for item in items
                   if not should_ignore(os.path.join(directory, item), ignore_patterns, cache))

    for item in items:
        item_path = os.path.join(directory, item)
        if item_path in done:
            continue
        done.add(item_path)
        if os.path.islink(item_path):
            print(f"Skipping symlink {item_path}", file=sys.stderr)
            continue
        if os.path.isdir(item_path):
            dump_files(item_path, ignore_patterns, include_headers, binary, out_file,
                       cache, strip_prefix, done, visited)
        else:
            try:
                with open(item_path, 'rb') as f:
                    head = f.read(1024)
                    if is_binary(head) and not binary:
                        print(f"Skipping binary file {item_path}", file=sys.stderr)
                        continue
                    display_path = item_path
                    if strip_prefix and item_path.startswith(strip_prefix):
                        display_path = item_path[len(strip_prefix):].lstrip('/')
                    if include_headers:
                        out_file.write(f"\n\n--- Path: {display_path} ---\n\n".encode())
                    print(f"Dumping {display_path}", file=sys.stderr)
                    out_file.write(head)
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        out_file.write(chunk)
                    out_file.write(b"\n")
            except OSError as e:
                print(f"Warning: {item_path}: {e}", file=sys.stderr)
                continue


def main():
    print(r"""
     ____              ____  __       __
    / _  |__ ___  ___ |__  |/ /___ __/ /_
   / , _/ -_) _ \/ _ \/ __// __/\ \ / __/
  /_/|_|\__/ ,__/\___/____/\__//_\_\\__/
          /_/    for llms & text-mining
""", file=sys.stderr)

    parser = argparse.ArgumentParser(
        prog="repo2txt",
        description="Dump any repo or directory's contents into a single text file.")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-d', '--directory', required=True, help='Directory to dump')
    parser.add_argument('-t', '--tree', default=False, action='store_true',
                        help='Generate tree only (no file contents)')
    parser.add_argument('--embed', default=True, action=argparse.BooleanOptionalAction,
                        help='Embed the tree as dump file head')
    parser.add_argument('-b', '--binary', default=False, action='store_true',
                        help='Dump binary files as well')
    parser.add_argument('--gitignore', default=True, action=argparse.BooleanOptionalAction,
                        help='Use .gitignore file to exclude files')
    parser.add_argument('-i', '--ignore', required=False,
                        default=".venv,.git,.gitignore,*.lock,.editorconfig,.env.*",
                        help='Custom patterns to ignore, separated by commas')
    parser.add_argument('-o', '--output', required=False,
                        help='Output file (default: <dirname>-dump.txt)')
    parser.add_argument('-s', '--strip-prefix', required=False, default='',
                        help='Strip this prefix from displayed paths')
    parser.add_argument('-n', '--name', required=False, default='',
                        help='Display name for the directory in header')

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    if not args.output:
        dir_name = os.path.basename(os.path.abspath(args.directory))
        args.output = f"{dir_name}-dump.txt" if not args.tree else f"{dir_name}-tree.txt"

    options = vars(args)
    strvals = [str(v) for v in options.values()]
    klen = max(len(k) for k in options.keys())
    vlen = max(len(v) for v in strvals)
    print(f"\n  +-{'-'*klen}-+-{'-'*vlen}-+", file=sys.stderr)
    print(f"  | {'Option':<{klen}} | {'Value':<{vlen}} |", file=sys.stderr)
    print(f"  +-{'-'*klen}-+-{'-'*vlen}-+", file=sys.stderr)
    for key, val in zip(options.keys(), strvals):
        print(f"  | {key:<{klen}} | {val:<{vlen}} |", file=sys.stderr)
    print(f"  +-{'-'*klen}-+-{'-'*vlen}-+", file=sys.stderr)

    ignore_patterns = args.ignore.split(',') + (load_gitignore(args.directory) if args.gitignore else [])
    cache = {}
    strip_prefix = args.strip_prefix.rstrip('/') if args.strip_prefix else ''
    display_dir = args.name if args.name else ('.' if strip_prefix else args.directory)

    try:
        with open(args.output, 'wb') as out_file:
            if args.tree or args.embed:
                dirlen = len(display_dir)
                header = (f"\n+-{'-'*(24+dirlen)}-+\n"
                          f"| Dump tree for directory: {display_dir} |\n"
                          f"+-{'-'*(24+dirlen)}-+\n"
                          f"{generate_tree(args.directory, ignore_patterns, cache, strip_prefix)}\n")
                out_file.write(header.encode())

            if not args.tree:
                dump_files(args.directory, ignore_patterns, args.embed, args.binary,
                           out_file, cache, strip_prefix=strip_prefix)

        size = os.path.getsize(args.output)
        print(f"\nDumped {size} bytes to {args.output}. Bye!", file=sys.stderr)
    except OSError as e:
        print(f"Error writing to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

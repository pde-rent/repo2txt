import os
import argparse
import fnmatch

# NB: identifying UTF-8 and UTF-16 boms could be faster
textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
def is_binary(s: bytes) -> bool:
  global textchars
  return bool(s.translate(None, textchars))

def load_gitignore(directory):
  gitignore_path = os.path.join(directory, '.gitignore')
  if os.path.exists(gitignore_path):
    with open(gitignore_path, 'r') as f:
      patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    for i in range(len(patterns)):
      if patterns[i].endswith('/'):
        patterns[i] = patterns[i][:-1]
    return patterns
  return []

exclusion_cache = {}
def should_ignore(path, ignore_patterns):
  global exclusion_cache
  return exclusion_cache.setdefault(path, any(fnmatch.fnmatch(part, pattern) for pattern in ignore_patterns for part in (path, os.path.basename(path))))

def generate_tree(directory, ignore_patterns, strip_prefix='', indent=''):
  tree = ''
  items = os.listdir(directory)
  items = sorted([item for item in items if not should_ignore(os.path.join(directory, item), ignore_patterns)])
  display_path = directory
  if strip_prefix and directory.startswith(strip_prefix):
    display_path = directory[len(strip_prefix):].lstrip('/') or '.'
  print(f"Generating tree for {display_path}: {len(items)} items...")
  for item in items:
    corner = '└' if item == items[-1] else '├'
    item_path = os.path.join(directory, item)
    if os.path.isdir(item_path):
      tree += f"{indent}{corner}── {item}\n"
      tree += generate_tree(item_path, ignore_patterns, strip_prefix, indent + ('   ' if item == items[-1] else '│  '))
    else:
      tree += f"{indent}{corner}── {item}\n"
  return tree

def dump_files(directory, ignore_patterns, embed_tree, binary, done = set(), strip_prefix=''):
  items = os.listdir(directory)
  items = sorted([item for item in items if not should_ignore(os.path.join(directory, item), ignore_patterns)])
  dump = bytes()
  for item in items:
    item_path = os.path.join(directory, item)
    if item_path in done:
      continue
    done.add(item_path)
    if os.path.isdir(item_path):
      dump += dump_files(item_path, ignore_patterns, embed_tree, binary, done, strip_prefix)
    else:
      with open(item_path, 'rb') as f:
        tmp = f.read(1024)
        if is_binary(tmp) and not binary:
          print(f"Skipping binary file {item_path}")
          continue
        display_path = item_path
        if strip_prefix and item_path.startswith(strip_prefix):
          display_path = item_path[len(strip_prefix):].lstrip('/')
        if embed_tree:
          dump += f"""\n\n--- Path: {display_path} ---\n\n""".encode()
        print(f"Dumping {display_path}")
        dump += tmp + f.read() + b"\n"
  return dump

def main():
  print(r"""
     ____              ____  __       __
    / _  |__ ___  ___ |__  |/ /___ __/ /_
   / , _/ -_) _ \/ _ \/ __// __/\ \ / __/
  /_/|_|\__/ ,__/\___/____/\__//_\_\\__/
          /_/    for llms & text-mining
""")
  parser = argparse.ArgumentParser(description=f"With Repo2txt, dump any repo or directory's contents into a single text file.")
  parser.add_argument('-v', '--version', action='version', version='Repo2txt v1.0')
  parser.add_argument('-d', '--directory', required=True, help='Directory to dump')
  parser.add_argument('-t', '--tree', default=False, action='store_true', help='Generate tree only and not dump file contents to the output file')
  parser.add_argument('-e', '--embed', default=True, help='Embed the tree as dump file head')
  parser.add_argument('-b', '--binary', default=False, action='store_true', help='Dump binary files as well')
  parser.add_argument('-g', '--gitignore', required=False, default=True, help='Use .gitignore file of the directory to exclude files')
  parser.add_argument('-i', '--ignore', required=False, default=".venv,.git,.gitignore,*.lock,.editorconfig,.env.*,LICENCE", help='Custom patterns to ignore, separated by commas')
  parser.add_argument('-o', '--output', required=False, help='Output file to write the dump to')
  parser.add_argument('-s', '--strip-prefix', required=False, default='', help='Strip this prefix from displayed paths (e.g., temp dir path)')

  args = parser.parse_args()

  if not args.output:
    args.output = args.directory.split('/')[-1] + ('-dump.txt' if not args.tree else '-tree.txt')

  if not os.path.isdir(args.directory):
    print(f"Error: {args.directory} is not a valid directory.")

  options = vars(args)
  strvals = [str(value) for value in options.values()]
  klen, vlen = max(len(key) for key in options.keys()), max(len(value) for value in strvals)
  print(f"""
  +-{'-'*klen}-+-{'-'*vlen}-+
  | Option {' '*(klen-6)}| Value {' '*(vlen-5)}|
  +-{'-'*klen}-+-{'-'*vlen}-+""")
  for i, key in enumerate(options.keys()):
    print(f"  | {key}{' '*(klen-len(key))} | {strvals[i]}{' '*(vlen-len(strvals[i]))} |")
  print(f"  +-{'-'*klen}-+-{'-'*vlen}-+")
  ignore_patterns = args.ignore.split(',') + (load_gitignore(args.directory) if args.gitignore else [])

  output = b''
  strip_prefix = args.strip_prefix.rstrip('/') if args.strip_prefix else ''
  display_dir = '.' if strip_prefix else args.directory

  if args.tree or args.embed:
    dirlen = len(display_dir)
    output += f"""
+--------------------------{'-'*dirlen}--+
| Dump tree for directory: {display_dir} |
+--------------------------{'-'*dirlen}--+
{generate_tree(args.directory, ignore_patterns, strip_prefix)}
""".encode()

  if not args.tree:
    output += dump_files(args.directory, ignore_patterns, args.embed, args.binary, strip_prefix=strip_prefix)

  with open(args.output, 'wb') as f:
    f.write(output)

  print(f"Dumped {len(output)} characters to {args.output}. Bye!")

if __name__ == "__main__":
  main()

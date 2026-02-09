```
     ____              ____  __       __
    / _  |__ ___  ___ |__  |/ /___ __/ /_
   / , _/ -_) _ \/ _ \/ __// __/\ \ / __/
  /_/|_|\__/ ,__/\___/____/\__//_\_\\__/
          /_/    for llms & text-mining

```

# Repo2txt: Dump a Repo to a Single Text File

Consolidate all files within a repo or any directory into a single, structured, searchable text file.
Ideal for text mining, LLM fine-tuning, embedding generation, and more.

## Key Features

* **No Dependencies:** Pure Python, single file, no external dependency.
* **Binary File Support:** Optionally include binary files alongside text.
* **Gitignore Integration:** Exclude files and patterns specified in the target directory `.gitignore`.
* **Symlink Safe:** Detects and skips symlinks to prevent cycles and path traversal.
* **Human/LLM Friendly Output:** Generates structured output with directory tree and file contents.

## Usage

```bash
# Clone and run
git clone https://github.com/pde-rent/repo2txt.git
cd repo2txt

# Dump a directory (default: tree + file contents)
python3 main.py -d /path/to/your/repository -o output.txt

# Tree structure only
python3 main.py -d /path/to/your/repo -t -o my_repo_tree.txt

# Include binary files
python3 main.py -d /path/to/your/repo -b -o my_repo_dump.txt

# Disable gitignore integration
python3 main.py -d /path/to/your/repo --no-gitignore -o output.txt

# Disable tree embedding
python3 main.py -d /path/to/your/repo --no-embed -o output.txt

# Custom ignore patterns
python3 main.py -d /path/to/your/repo -i "*.lock,*.md,dist" -o output.txt
```

**Options:**

* `-d, --directory` — **(Required)** The directory to dump.
* `-t, --tree` — Generate tree only (no file contents).
* `--embed / --no-embed` — Embed tree at the beginning of output (default: on).
* `-b, --binary` — Include binary files (default: off).
* `--gitignore / --no-gitignore` — Use `.gitignore` to exclude files (default: on).
* `-i, --ignore` — Comma-separated patterns to ignore.
* `-o, --output` — Output file name (default: `<dirname>-dump.txt`).
* `-s, --strip-prefix` — Strip this prefix from displayed paths.
* `-n, --name` — Display name for the directory in header.
* `-v, --version` — Show version and exit.

## How It Works

Repo2txt walks the target directory recursively, building a visual tree and concatenating file
contents into a single output file. Binary files are detected by checking the first 1024 bytes
for non-text characters. Symlinks are flagged and skipped to prevent cycles. The `.gitignore`
parser supports basic glob patterns (via `fnmatch`) but does not handle negation (`!`), `**`
recursive wildcards, or nested `.gitignore` files.

## Disclaimers

* **Binary Data:** Including binary files can significantly increase output size. Use `-b` with caution.
* **Ignore Patterns:** The `.gitignore` parser is simplified — negation patterns, `**` globs, and nested `.gitignore` files are not supported.
* **Output Size:** Be mindful of output size with large repositories.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENCE](LICENCE).

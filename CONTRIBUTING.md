# Contributing to Repo2txt

We welcome contributions! Here are some areas where help is appreciated:

- Support for fetching remote repositories
- More robust `.gitignore` parsing (negation, `**` globs, nested files)
- New output formats (markdown, HTML)
- Better filtering options (by extension, by size)
- Cross-platform testing (Windows, Linux)

## Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes (keep it single-file, no external deps)
4. Test against real directories of varying size
5. Submit a pull request

## Guidelines

- **No external dependencies** — pure Python stdlib only
- **Single file** — all logic stays in `main.py`
- **Python 3.9+** — minimum supported version
- **Keep it lean** — avoid over-engineering, prefer simple solutions

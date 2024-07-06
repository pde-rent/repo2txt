```
     ____              ____  __       __
    / _  |__ ___  ___ |__  |/ /___ __/ /_
   / , _/ -_) _ \/ _ \/ __// __/\ \ / __/
  /_/|_|\__/ ,__/\___/____/\__//_\_\\__/
          /_/    for llms & text-mining

```

# Repo2txt: Dump a Repo to a Single Text File

Effortlessly consolidate all files within a repo (e.g., GitHub) or any directory into a single, structured, easily searchable text file.
Ideal for text mining, LLM fine-tuning, embedding generation, and more.

## Key Features

* **No Dependencies:**  Pure Python, single file, no external dependency.
* **Multithreaded:** Fast enough, leverages multithreads for better IO performance.
* **Binary File Support:** Optionally include binary files (encoded images, sounds, executables...) alongside text.
* **Gitignore Integration:** Exclude files and patterns specified in the target directory `.gitignore`.
* **Human/LLM Friendly Output:**  Generates a human-readable and structured output, that can be used directly or tokenized to train and fine-tune models.

## Use Cases

* **LLM Fine-tuning Data Preparation:** Create large text datasets for training language models.
* **Text Mining & Analysis:** Extract insights from codebases, documentation, and other textual sources.
* **Embedding Generation:** Generate text representations for tasks like semantic search and similarity comparison, helpful to build RAGs.
* **Repository Backups:** Create compact, searchable backups of your code projects.
* **Data Versioning:** Track changes in code and content over time with a single file to diff (or not).

## Usage 📖

1. **Clone this Repository:**
   ```bash
   git clone https://github.com/pde-rent/repo2txt.git
   cd repo2txt
   ```
2. **Run `main.py` from within the cloned repository:**
  ```bash
  python main.py -d /path/to/your/repository/to/dump [-t] [-e] [-b] [-g] [-i "*.lock,*.md"] [-o output.txt]
  ```

**Options:**

* `-d, --directory`: **(Required)** The path to the directory you want to dump.
* `-t, --tree`: Generate the dump tree only (no file contents, false by default).
* `-e, --embed`: Embed the tree at the beginning of the output file (true by default).
* `-b, --binary`: Include binary files in the dump (disabled by default).
* `-g, --gitignore`: Use the `.gitignore` file to exclude files (enabled by default).
* `-i, --ignore`: Specify additional comma-separated patterns to ignore.
* `-o, --output`: Specify the output file name (default is based on directory name).


## Examples 💡

**Dumping All Files (Including Binaries):**

```bash
python main.py -d /path/to/your/repo -e -b -o my_repo_dump.txt
```

**Generating Tree Structure Only:**

```bash
python main.py -d /path/to/your/repo -t -o my_repo_tree.txt
```

**Output Sample (Tree Only):**

```
+----------------------------------------+
| Dump tree for directory: ../collector/ |
+----------------------------------------+
├── .env.test
├── README.md
├── dbs
│ ├── Dockerfile.dbs
│ └── start-test.bash
├── forwarder
│ ├── cargo.toml
│ ├── main.rs
│ ├── messages.rs
│ └── server.rs
├── main.py
├── presets
│ └── markets.yml
└── tests
  ├── fowarder.rs
  └── server.rs
```


## Disclaimers ⚠️

* **Binary Data:** Including binary files (images, videos, executables) can significantly increase the output file size and introduce noise. Use the `-b` option with caution.
* **Ignore Patterns:** Utilize `.gitignore` and the `-i` option to exclude unnecessary files like logs, caches, and artifacts, which can make the output more manageable and relevant.
* **Output Size:** Be mindful of the potential size of the output file, especially when including binary data or large repositories.

## Contributing

We welcome contributions! This can be enhanced in many ways:
- add support for fetching remote repositories (or even ftp) to fetch and dump in seconds
- performance increase by working on better IO and threading
- add complex pattern support for fine grained file ignoring
- add ignore preset files for language specific use cases (this was mostly used with Python repositories)
- and more...

Feel free to fork the repository, make your changes, and submit a pull request ❤️

## License

This project is licensed under the MIT License.

## 1. Overview:
The script is designed to process a specified source, which can either be a single .jack file or a directory with multiple .jack files. In token mode, it tokenizes the files and generates an `xxxT.xml` output, while in the default parse mode, it parses the files and produces an `xxx.xml` output. The resulting files are saved in the same directory as the original .jack file(s).

## 2. Compilation: 
This program is written in Python. There is no need for compilation. To run the script, Python 3.x needs to be installed.

## 3. Running the program:
* Launch a terminal;
* Navigate to the `src` directory where `JackAnalyzer.py` resides;
* Usage: `JackAnalyzer.py [-h] -p PATH [--token] [--parse]`
    * To parse a specific .jack file, enter the command: `python3 JackAnalyzer.py -p <filename>.jack`.
    * To parse all .jack files within a directory, enter the command: `python3 JackAnalyzer.py -p <directory>`. Ensure the directory contains one or more .jack files
    * To tokenize instead of parsing the files, add `--token` to the end of the command. For example: `python3 JackAnalyzer.py -p <directory> --token`. 

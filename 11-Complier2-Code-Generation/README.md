## 1. Overview:

The script is designed to compile Jack source code, which can either be a single .jack file or multiple .jack files within a directory. It compile the files and produces an `xxx.vm` output file for each source file. The resulting `.vm` files are saved in the same directory as the original .jack file(s).

## 2. Compilation: 
This script is written in Python and does not require compilation. Python 3.x should be installed to run the script.

## 3. Running the program:
* Launch a terminal;
* Navigate to the `src` directory where `JackCompiler.py` resides;
* Usage: `JackCompiler.py PATH`
    * To compile a specific .jack file, enter the command: `python3 JackCompiler.py <filename>.jack`.
    * To parse all .jack files within a directory, enter the command: `python3 JackCompiler.py <directory>`. Ensure the directory contains one or more .jack files
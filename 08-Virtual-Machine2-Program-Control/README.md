## 1. Overview:
The script accept a single command line parameter which specifies the source of the .vm file. This source can either be an individual .vm file or a directory containing one or more .vm files. The outcome of this translation is a single assembly language file named `xxx.asm`, created in the same directpry as the input .vm file.

## 2. Compilation: 
This program is written in Python, so there is no need for compilation. To run the script, Python 3.x needs to be installed.

## 3. Running the program:
* Launch a terminal;
* Navigate to the directory where `VMtranslator.py` resides;
* To translate a specific .vm file, enter the command: `python3 VMtranslator.py <filename>.vm`
* To translate all .vm files within a directory, enter the command: `python3 VMtranslator.py <directory>`. Ensure the directory contains one or more .vm files

## 4. Limitation:
This script assumes that the vm file provided are error-free.
# Repository Documentation

## Overview

This repository structure consists of two main components:

1. README.md: This file typically contains information about the project, such as a brief description, installation instructions, usage guidelines, and any other relevant details. README.md is often the first file users encounter when accessing a repository and serves as a guide for understanding the project.

2. main.py: This file is likely the main Python script or program of the project. It may contain the core functionality, logic, and execution flow of the application. main.py is where the primary code implementation resides and is executed when the program is run.

Interactions:
- Users accessing the repository will first see the README.md file, which provides essential information about the project, helping them understand its purpose and how to use it.
- Developers working on the project will primarily interact with the main.py file, where they will write, modify, and debug the code that drives the project's functionality.
- The README.md file can also reference or provide instructions related to the main.py file, guiding users and developers on how to run the program, understand its structure, and contribute to its development.

Overall, this repository structure is simple and common for many projects, with the README.md file serving as a documentation hub and main.py containing the core code implementation.

## Table of Contents

- [Root](#root)
  - [README.md](#readme-md)
  - [main.py](#main-py)

## Directories and Files

### Root

#### README.md <a id='readme-md'></a>

**Path:** `README.md`

**Language:** Markdown

**Documentation:**

# README.md

This Markdown file provides an overview of the `processa-edocs` script written in Python. The script is designed to process XML files for electronic invoices.

### Installation Instructions
- Clone the repository:
  ```
  git clone https://github.com/cilas/processa-edocs.git
  cd processa-edocs
  ```
- Create a virtual environment:
  ```
  python -m venv venv
  ```
- Install the required dependencies:
  ```
  pip install -r requirements.txt
  ```

### Usage
- Copy the XML files to the `xml` folder.
- Run the script using the following command:
  ```
  python main.py
  ```
- The script will generate a SQLite3 database named `database.db`.

---

The `processa-edocs` script serves as a tool for processing XML files related to electronic invoices. It provides functionality to parse and extract relevant information from these XML files, storing the data in a SQLite3 database for further analysis or processing.

Key components of the script include:
- `main.py`: This is the main entry point of the script where the processing logic is implemented. It orchestrates the parsing of XML files and the creation of the database.
  
- `requirements.txt`: This file lists all the dependencies required by the script. These dependencies can be installed using `pip` to ensure the script runs smoothly.

The script follows a simple workflow where XML files are provided as input, processed by the script, and the extracted data is stored in a SQLite3 database for easy access and querying. This script can be integrated into larger projects or used as a standalone tool for handling electronic invoice data efficiently.

---

#### main.py <a id='main-py'></a>

**Path:** `main.py`

**Language:** Python

**Dependencies:**

- `os`
- `shutil`
- `sys`
- `pprint`
- `time`
- `csv`
- `sqlite3`
- `logging`
- `xml.etree.ElementTree`
- `pathlib`
- `lxml`
- `lxml`

**Documentation:**

```python
# Author: Cilas Cavalcanti
# Email: cilas.acms@gmail.com

import os
import shutil
from pathlib import Path
import sys
import pprint
import time
import csv
import sqlite3
import logging
from lxml import etree
from lxml import objectify
import xml.etree.ElementTree as ET

# Configuring logging to write to a log file
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='logs/processa-edocs.log', level=logging.DEBUG)


class ProcessaEdocs(object):
    """
    Class responsible for processing XML files of electronic invoices
    """
    def __init__(self, data={}):
        self.data = data

    def decompor_chave(self, chave, elemento):
        """
        Decomposes the NFe key into its components and returns the specified element.

        Parameters:
        chave (str): The NFe key to be decomposed.
        elemento (str): The specific element to be returned.

        Returns:
        str: The specified element of the decomposed NFe key.
        """
        # Implementation details...

    def ajusta_cancelados(self):
        """
        Adjusts canceled invoices in the database by updating their status.

        This method checks for canceled invoices and updates their status in the database.
        """
        # Implementation details...

    def carrega_xml(self, path):
        """
        Loads and parses an XML file from the specified path.

        Parameters:
        path (str): The path to the XML file.

        Returns:
        objectify.ObjectifiedElement: The root element of the parsed XML.
        """
        # Implementation details...

    def salva_no_db(self):
        """
        Saves the extracted data from XML files into the SQLite database.

        This method inserts the extracted data from XML files into the SQLite database tables.
        """
        # Implementation details...

    def pega_dados_xml(self, root, path):
        """
        Extracts relevant data from the XML root element based on its type.

        Parameters:
        root (objectify.ObjectifiedElement): The root element of the XML.
        path (str): The path to the XML file.

        Returns:
        dict: Extracted data from the XML file.
        """
        # Implementation details...

    def walk(self, dirname):
        """
        Recursively walks through a directory to process XML files.

        This method walks through a directory, processes XML files, and extracts data from them.
        
        Parameters:
        dirname (str): The directory path to walk through.
        """
        # Implementation details...

    def create_csv_file(self):
        """
        Creates a CSV file with the extracted data from XML files.

        This method creates a CSV file and writes the extracted data from XML files into it.
        """
        # Implementation details...


if __name__ == '__main__':
    print('Creating a database to store information...')

    # Implementation details...

    try:
        eDoc = ProcessaEdocs()
        print('''
                -------------------------------
               |   ANALYZING XML FILES!    |
                -------------------------------
        ''')
        eDoc.walk('xml')
        print(len(eDoc.data), 'XML files analyzed.')
        print('Done!')
        print('''
                -------------------------------
               |        SAVING DATA!        |
                -------------------------------
        ''')
        eDoc.salva_no_db()

        print('Done!')
        print('''
                -------------------------------------
               |        Adjusting Canceled!        |
                -------------------------------------
        ''')
        eDoc.ajusta_cancelados()
        print('Done!')

    except KeyboardInterrupt:
        print('Bye! ;)')
```

This Python file defines a class `ProcessaEdocs` that is responsible for processing XML files of electronic invoices. The class contains methods for decomposing NFe keys, adjusting canceled invoices, loading XML files, saving data to a database, extracting data from XML files, walking through directories to process XML files, and creating a CSV file with extracted data. The script also includes a main block that creates a SQLite database, processes XML files, saves data to the database, and adjusts canceled invoices.

---


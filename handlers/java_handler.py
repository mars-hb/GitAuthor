#!/usr/bin/env python

__author__ = "Marius Schäffer"

import glob
import logging
import os
import shutil
import tempfile
from subprocess import Popen, PIPE

from handlers.language_handler import LanguageHandler

_HANDLER_LANG = "java"


class JavaHandler(LanguageHandler):

    def __init__(self, args):
        super(JavaHandler, self).__init__(_HANDLER_LANG, args)
        self._endings = ["java"]

    @staticmethod
    def does_handle(language):
        return language == _HANDLER_LANG

    @staticmethod
    def for_language():
        return _HANDLER_LANG

    def get_authors(self, byte_array):
        result = []
        for b in byte_array:
            s = b.decode("utf-8")
            parts = s.split("\n")
            for part in parts:
                if "author" in part:
                    result.append(part.replace("author", "").strip())
        unique = set(result)
        authors = []
        for a in unique:
            authors.append(a)
        authors.sort(key=lambda string: string.split(" ")[-1])
        return authors

    def _javadoc_author(self, author, indentation):
        return (indentation * " " + "* @author {}\n").format(author)

    def _insert_authors(self, lines, insertion_line, authors, generate_docstring=False, file_name=None):
        fd, path = tempfile.mkstemp()

        with os.fdopen(fd, "w") as tmp:
            for index, line in enumerate(lines):
                if index == insertion_line:
                    indentation = len(line) - len(line.lstrip(' ')) if not generate_docstring else 1
                    if len(line.strip()) > 1 and not generate_docstring:
                        tmp.write(indentation * " " + "*\n")
                    elif generate_docstring:
                        tmp.write("/**\n")
                        if file_name is not None:
                            tmp.write(
                                indentation * " " + "* Class {}\n".format(file_name.split(os.sep)[-1].replace(".java", "")
                                                                        if os.sep in file_name else file_name.replace(".java", "")))
                    for author in authors:
                        tmp.write(self._javadoc_author(author, indentation))
                    if generate_docstring:
                        tmp.write(indentation * " " + "*/\n")
                if "@author" not in line:
                    tmp.write(line)
            tmp.flush()
        return path

    def _generate_docstring(self, lines, insertion_line, authors, file_name=None):
        for index, line in enumerate(lines):
            # insertion line = public class ...
            if index == insertion_line:
                break
            if "@" in line and "@author" not in line:
                # annotation found
                insertion_line = index
                break
        logging.warning("Generating docstring for {}".format(file_name))
        return self._insert_authors(lines, insertion_line, authors, generate_docstring=True, file_name=file_name)

    def _update_file(self, file, authors):
        with open(file, "r") as f:
            lines = f.readlines()
        for index, line in enumerate(lines):
            insertion_line = index
            if "class" in line and "{" in line and "}" not in line:
                path = self._generate_docstring(lines, insertion_line, authors, file_name=file)
            if "*/" in line:
                logging.debug("Found end of class docstring at line {} for file {}".format(index + 1, file))
                path = self._insert_authors(lines, insertion_line, authors)
                shutil.move(path, file)
                logging.info("Updated authors for file {}".format(file))
                break

    def _handle_file(self, file):
        p = Popen('git blame {} --porcelain | grep  "^author "'.format(file),
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        result = p.communicate()
        authors = self.get_authors(result)
        logging.debug("Found authors {} for file {}".format(authors, file))
        self._update_file(file, authors)

    def _run_for_dir(self, directory):
        if not os.path.isdir(directory):
            raise ValueError("Not a directory {}".foramt(directory))
        os.chdir(directory)
        pattern = os.path.join("**", "*.java")
        files = glob.glob(pattern, recursive=True)
        for file in files:
            self._handle_file(file)

    def run(self):
        logging.info("Language handler for {} started.".format(_HANDLER_LANG))
        logging.debug("Entered directories {}".format(self._args.dir))
        for d in self._args.dir:
            self._run_for_dir(d)

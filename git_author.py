#!/usr/bin/env python

__author__ = "Marius Schäffer"

import argparse
import logging

from handlers.java_handler import JavaHandler

REGISTERED_HANDLERS = [JavaHandler]


def _init_argpase():
    parser = argparse.ArgumentParser(
        description="Script that modifies docstring of source files to display authors based on git history.")
    parser.add_argument('-l', '--language', dest='language', nargs="+", required=True,
                        help='Specify used language. Supported languages: {}'.format(
                            [h.for_language() for h in REGISTERED_HANDLERS]))
    parser.add_argument('-d', '--dir', dest='dir', nargs='+', required=True, help="Directory to look for source files.")
    parser.add_argument('-v', '--verbose', dest='verbose', nargs="?", const=True, default=False,
                        help="Enables verbose output.")
    return parser.parse_args()


def _setup_logging(args):
    fmt = "%(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=fmt, level=logging.DEBUG)
    else:
        logging.basicConfig(format=fmt, level=logging.INFO)


def _handle_language_selection(args):
    languages = args.language
    for language in languages:
        for H in REGISTERED_HANDLERS:
            if H.does_handle(language):
                handler = H(args)
                handler.run()


def main():
    args = _init_argpase()
    _setup_logging(args)
    supported_languages = [h.for_language() for h in REGISTERED_HANDLERS]
    languages = args.language
    for language in languages:
        if language not in supported_languages:
            raise ValueError("Language {} not supported. Select one of the supported languages: {}"
                             .format(language, supported_languages))
    _handle_language_selection(args)


if __name__ == "__main__":
    main()

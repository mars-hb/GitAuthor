#!/usr/bin/env python

__author__ = "Marius Schäffer"


class LanguageHandler(object):

    def __init__(self, language, args):
        self.language = language
        self._args = args

    @staticmethod
    def does_handle(language):
        return False

    @staticmethod
    def for_language():
        return None

    def run(self):
        return

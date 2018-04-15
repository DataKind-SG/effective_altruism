#!/usr/bin/ev python3
# -*- coding: utf-8 -*-
################################################################################

""" word lexer. GNU GPLv3.
"""

import os
import sys
import re
import ply.lex as plex
from ply.lex import TOKEN

################################################################################

DATA_DIR = "data/input/web_scraping/"
FILE = "Changemakers_EastTimor.csv"
FILE = "wikiwand_thailand.csv"
LEX_DEBUG = False

################################################################################

class WordLexer(object):
    """
    """
    tokens = [
        "WORD",
        "OTHER", "NL"
    ]
    _nb_valid_tok = None
    _nb_line = None

    ################
    _re_word = r'[a-zA-Z0-9]+'
    _re_other = r'.'
    _re_nl = r'([\r]*\n)+'

    ################

    def __init__(self):
        self._nb_valid_tok = 0
        self._nb_line = 0
        self.build()

    def build(self, **kwargs):
        self.lexer = plex.lex(module=self, debug=LEX_DEBUG, **kwargs)
    ################

    @TOKEN(_re_word)
    def t_WORD(self, t):
        """
        """
        return t
        print("OK: {}".format(t.value))

    @TOKEN(_re_other)
    def t_OTHER(self, t):
        """
        """
        return
        print("KO: {}".format(t.value))

    @TOKEN(_re_nl)
    def t_NL(self, t):
        """
        """
        return
        print("FOUND newline")
    ################ public interface

    def tokenize(self, data):
        self.lexer.input(data)
        more_token = True
        while more_token:
            tok = self.lexer.token()
            if tok:
                yield tok
            else:
                more_token = False
    ################

def update_dict(dico, value):
    """
    """
    value = value.lower()
    if value in dico:
        dico[value] += 1
    else:
        dico[value] = 1
    return dico

################################################################################

if __name__ == "__main__":
    data = None
    all_words = {}
    wl = WordLexer()
    with open(DATA_DIR + '/' + FILE, mode='r', encoding="utf-8") as fr:
        data = fr.read()

    for i, tok_word in enumerate(wl.tokenize(data)):
        all_words = update_dict(all_words, tok_word.value)

    print(all_words)

################################################################################
# EOF
################################################################################

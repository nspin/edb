import sys
from pathlib import Path
from contextlib import contextmanager

import code
from pdb import Pdb

import readline
original_completer = readline.get_completer()
import rlcompleter
readline.set_completer(original_completer)

__all__ = [
    'debug',
    'interact',
    ]

DEBUG_HISTORY = Path('~/.python_edb_debug_history').expanduser()
INTERACT_HISTORY = Path('~/.python_edb_interact_history').expanduser()

def code_completer(namespace):
    return rlcompleter.Completer(namespace=namespace).complete

def try_read_history_file(path):
    readline.clear_history()
    if path.is_file():
        readline.read_history_file(path)

@contextmanager
def completer(temporary_completer):
    saved_completer = readline.get_completer()
    readline.set_completer(temporary_completer)
    try:
        yield
    finally:
        readline.set_completer(saved_completer)

@contextmanager
def history(path):
    try_read_history_file(path)
    try:
        yield
    finally:
        readline.write_history_file(path)

class PdbBetterReadline(Pdb):

    def cmdloop(self, *args, **kwargs):
        with history(DEBUG_HISTORY):
            super().cmdloop(*args, **kwargs)

    def do_interact(self, *args, **kwargs):
        ns = self.curframe.f_globals.copy()
        ns.update(self.curframe_locals)
        with completer(code_completer(ns)):
            with history(INTERACT_HISTORY):
                super().do_interact(*args, **kwargs)
        try_read_history_file(DEBUG_HISTORY)

class PdbJustInteract(Pdb):

    def cmdloop(self):
        ns = self.curframe.f_globals.copy()
        ns.update(self.curframe_locals)
        with completer(code_completer(ns)):
            with history(INTERACT_HISTORY):
                code.interact(banner='', local=ns)
                # HACK: use Pdb.do_continue instead of Bdb.set_continue to restore signal handlers
                self.do_continue(None)

def debug(header=None):
    pdb = PdbBetterReadline()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)

def interact(header=None):
    pdb = PdbJustInteract()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)

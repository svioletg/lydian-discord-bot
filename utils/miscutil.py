"""General-purpose, miscellaneous utility methods."""

# Standard imports
from inspect import currentframe
import logging
import re
import time
from pathlib import Path
from sys import stdout
from typing import Callable, Optional

# External imports
import colorlog

# Local imports
import utils.configuration as cfg
from utils.palette import Palette

plt = Palette()

class Stopwatch:
    """Basic debugging tool for timing actions. While `time_func()` from this same module is meant to measure specific functions/callables,
    the usage of the `Stopwatch` class is more for usage in before and after lines, when that is more convenient.
    """
    def __init__(self, name: str='generic'):
        """
        @name: A name to assign this instance. Will be displayed upon using `lap()`, no other purpose.
        """
        self.name = name
        self.lap_start: float = 0.0
        self.lap_end: float = 0.0

    def lap(self, label: str=''):
        """Prints out the time elapsed between now and the last call to `lap()`.
        @label: A message to attach. Useful for more clearly indicating progress or line numbers.
        """
        self.lap_end = time.perf_counter()
        print(f'[WATCH <{self.name}>{('/'+label) if label else ''}]: LAP ... {self.lap_end - self.lap_start}')
        self.lap_start = time.perf_counter()

def line():
    """Prints the current line number. Should only be used for debugging during development."""
    cf = currentframe()
    print(f'----= {cf.f_back.f_lineno}')

def seconds_to_hms(seconds: int | float, format_zero: bool = True) -> str | None:
    """Returns a formatted string in either MM:SS or HH:MM:SS from the given time in seconds.

    @format_zero: By default, `0:00` is returned if the input is `0`. Setting this to `False` will instead
        return `None`.
    """
    if (seconds == 0) and (not format_zero):
        return None

    frmt: str = ''
    if seconds < 60:
        frmt = '0:%S'
    elif seconds < 3600:
        frmt = '%M:%S'
    else:
        frmt = '%H:%M:%S'
    stamp: list[str] = time.strftime(frmt, time.gmtime(seconds)).split(':')
    stamp[0] = str(int(stamp[0]))
    return ':'.join(stamp)

def time_func(func: Callable, printout: bool=True) -> float:
    """Times the execution of a callable, prints out the result if allowed, and returns the result of the called function

    @printout: Whether to print a string containing the time elapsed
    """
    ta = time.perf_counter()
    func_result = func()
    tb = time.perf_counter()
    if printout:
        print(f'{func} ... completed in ... {tb - ta}s')
    return func_result

def create_logger(logger_name: str, logfile: Optional[str | Path]=None) -> logging.Logger:
    """Sets up a new logger, using `colorlog` for colored console output and `logging` for file output.
    A file handler is only created if `logfile` has a value.
    """
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    use_color: bool = not cfg.DISABLE_LOG_COLORS
    new_logger = colorlog.getLogger(logger_name)
    date_format = '%y-%m-%d %H:%M:%S'
    log_string_pre = '[{c_timer_}%(asctime)s%(reset)s] [{c_module_}%(module)s%(reset)s/{c_}%(levelname)s%(reset)s]'+\
        ' in {c_function_}%(funcName)s%(reset)s: {c_}%(message)s'

    log_string_no_color = re.sub(r"({c_(.*?)})", '', log_string_pre)
    log_string_no_color = re.sub(r"%\(reset\)s", '', log_string_no_color)

    log_string_colored = re.sub(r"({c_(.*?)})", r'%(\2log_color)s', log_string_pre)

    def get_log_colors(use_color: bool=True):
        log_colors = {
            'DEBUG':    plt.debug if use_color else '',
            'INFO':     plt.info  if use_color else '',
            'WARNING':  plt.warn  if use_color else '',
            'ERROR':    plt.error  if use_color else '',
            'CRITICAL': plt.critical if use_color else ''
        }
        return log_colors

    def get_secondary_log_colors(use_color: bool=True):
        secondary_log_colors = {
            'timer': {l:plt.timer if use_color else '' for l in levels},
            'module': {l:plt.module if use_color else '' for l in levels},
            'function': {l:plt.function if use_color else '' for l in levels}
        }
        return secondary_log_colors

    log_format_no_color = logging.Formatter(log_string_no_color, datefmt=date_format)
    log_format_colored = colorlog.ColoredFormatter(log_string_colored, datefmt=date_format,
        log_colors=get_log_colors(use_color=use_color),
        secondary_log_colors=get_secondary_log_colors(use_color=use_color)
    )

    stdout_handler = colorlog.StreamHandler(stream=stdout)
    stdout_handler.setFormatter(log_format_colored)
    stdout_handler.setLevel(logging.getLevelName(cfg.LOG_LEVEL.upper()))
    new_logger.addHandler(stdout_handler)

    if logfile:
        file_handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='w')
        file_handler.setFormatter(log_format_no_color)
        file_handler.setLevel(logging.DEBUG)
        new_logger.addHandler(file_handler)

    new_logger.setLevel(colorlog.DEBUG)

    return new_logger

import logging
import random
import time

from functools import partial

from .compat import decorator


logging_logger = logging.getLogger(__name__)


def __retry_internal(f, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0,
                     logger=logging_logger):
    """
    Executes a function and retries it if it failed.

    :param f: the function to execute.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    _tries, _delay = tries, delay
    while _tries:
        if not f():
            _tries -= 1
            if not _tries:
                logger.error("Exceeded the number of retry attempts.")
                return False

            if logger is not None:
                logger.warning(f'Running {f.func.__name__} again. Attempts remaining: {_tries}. Retrying in {_delay} seconds...')

            time.sleep(_delay)
            _delay *= backoff

            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter

            if max_delay is not None:
                _delay = min(_delay, max_delay)
        else:
            return True


def retry(tries=-1, delay=0, max_delay=None, backoff=1, jitter=0, logger=logging_logger):
    """Returns a retry decorator.

    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :returns: a retry decorator.
    """

    @decorator
    def retry_decorator(f, *fargs, **fkwargs):
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return __retry_internal(partial(f, *args, **kwargs), tries, delay, max_delay, backoff, jitter,
                                logger)

    return retry_decorator


def retry_call(f, fargs=None, fkwargs=None, tries=-1, delay=0, max_delay=None, backoff=1,
               jitter=0,
               logger=logging_logger):
    """
    Calls a function and re-executes it if it failed.

    :param f: the function to execute.
    :param fargs: the positional arguments of the function to execute.
    :param fkwargs: the named arguments of the function to execute.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    args = fargs if fargs else list()
    kwargs = fkwargs if fkwargs else dict()
    return __retry_internal(partial(f, *args, **kwargs), tries, delay, max_delay, backoff, jitter, logger)

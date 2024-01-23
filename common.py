LOG_UNEXPECTED_EXCEPTIONS_DEFAULT = True
RETHROW_UNEXPECTED_DEFAULT = True
import logging

try:
    from celery.exceptions import SoftTimeLimitExceeded as maybe_celery_softtimeout
except ImportError:
    maybe_celery_softtimeout = None


# returns true if we need to rethrow (this will allow throwing in the right place and not from here)
def default_exception(e, rethrow_unexpected: bool = RETHROW_UNEXPECTED_DEFAULT, logging_prefix: str = None,
                      log_unexpected_exceptions=LOG_UNEXPECTED_EXCEPTIONS_DEFAULT,
                      printer=logging.error):
    if maybe_celery_softtimeout is not None:
        if isinstance(e, maybe_celery_softtimeout):
            return True
    if log_unexpected_exceptions:
        out_str = ""
        if logging_prefix is not None:
            out_str += f"{logging_prefix} "
        out_str = f"{e.__class__.__name__}:{e}"
        printer(out_str)
    return rethrow_unexpected

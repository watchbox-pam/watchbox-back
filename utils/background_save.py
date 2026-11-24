import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Hashable

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="db-save")
_in_flight: set[Hashable] = set()
_lock = threading.Lock()

def save_in_background(key: Hashable, fn: Callable, *args) -> None:
    with _lock:
        if key in _in_flight:
            return
        _in_flight.add(key)

    def task():
        try:
            fn(*args)
        except Exception:
            logger.exception("Sauvegarde %s échouée", key)
        finally:
            with _lock:
                _in_flight.discard(key)

    _executor.submit(task)

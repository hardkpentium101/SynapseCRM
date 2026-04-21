"""
Async Runner - Run async code from sync context
"""

import asyncio
import threading
from functools import wraps

_local = threading.local()


def run_async(coro):
    """Run an async coroutine from sync context"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            return result
        finally:
            loop.close()
    else:
        if loop.is_running():
            if not hasattr(_local, "thread_loop") or _local.thread_loop is None:
                _local.thread_loop = asyncio.new_event_loop()
                _local.thread = threading.Thread(
                    target=_local.thread_loop.run_forever, daemon=True
                )
                _local.thread.start()

            future = asyncio.run_coroutine_threadsafe(coro, _local.thread_loop)
            try:
                return future.result(timeout=30)
            except TimeoutError:
                return {"error": "Database operation timed out"}
        else:
            return loop.run_until_complete(coro)

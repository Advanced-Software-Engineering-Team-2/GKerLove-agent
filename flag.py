import threading

sessions_busy_lock = threading.Lock()
sessions_busy = {}


def mark_session_busy(session_id):
    with sessions_busy_lock:
        sessions_busy[session_id] = True


def mark_session_idle(session_id):
    with sessions_busy_lock:
        sessions_busy[session_id] = False


def get_session_busy(session_id):
    with sessions_busy_lock:
        return sessions_busy.get(session_id, False)

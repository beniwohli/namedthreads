import ctypes
import ctypes.util
import platform
import threading

# this was originally based on https://bugs.python.org/issue15500#msg230736

_libpthread = None
PTHREAD_NAME_LIMIT = 15


def _get_libpthread():
    global _libpthread
    if not _libpthread:
        libpthread_path = ctypes.util.find_library("pthread")

        if not libpthread_path and platform.system() == "Darwin":
            # This cant be found by Python 2.7
            libpthread_path = "/usr/lib/libpthread.dylib"

        if not libpthread_path:
            # pthread library not found
            return

        _libpthread = ctypes.CDLL(libpthread_path)

    return _libpthread


def _get_thread_id(libpthread):
    pthread_self = libpthread.pthread_self
    pthread_self.restype = ctypes.c_void_p
    return pthread_self()


def _set_current_thread_name(libpthread, name):
    if hasattr(name, "encode"):
        name = name.encode("ascii", "replace")
    name = name[:PTHREAD_NAME_LIMIT] + b"\0"

    pthread_setname_np = libpthread.pthread_setname_np
    if platform.system() == "Darwin":
        pthread_setname_np.argtypes = [ctypes.c_char_p]
        pthread_setname_np.restype = ctypes.c_int
        pthread_setname_np(name)
    else:
        thread_id = _get_thread_id(libpthread)
        pthread_setname_np.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        pthread_setname_np.restype = ctypes.c_int
        pthread_setname_np(thread_id, name)


def patch():
    if getattr(threading.Thread, "_namedthreads_patched", None):
        # threading module is already patched
        return

    libpthread = _get_libpthread()

    if not libpthread:
        # pthread library not found, not patching"
        return

    if not hasattr(libpthread, "pthread_setname_np"):
        # pthread library does not have pthread_setname_np function, not patching
        return

    def set_thread_name(self):
        try:
            name = self.name
            if name:
                _set_current_thread_name(libpthread, name)
        except Exception:
            pass  # Don't care about failure to set name
        threading.Thread._namedthreads_orig(self)

    threading.Thread._namedthreads_patched = True
    if hasattr(threading.Thread, "_bootstrap"):  # Python 3
        threading.Thread._namedthreads_orig = threading.Thread._bootstrap
        threading.Thread._bootstrap = set_thread_name
    else:
        # Python 2.7 has a __bootstrap which cant be accessed,
        # but it immediately calls _set_ident, so we use that instead
        threading.Thread._namedthreads_orig = threading.Thread._set_ident
        threading.Thread._set_ident = set_thread_name
    return True


def unpatch():
    if not getattr(threading.Thread, "_namedthreads_patched", None):
        # threading module is not patched
        return
    if hasattr(threading.Thread, "_bootstrap"):
        threading.Thread._bootstrap = threading.Thread._namedthreads_orig
    else:
        threading.Thread._set_ident = threading.Thread._namedthreads_orig

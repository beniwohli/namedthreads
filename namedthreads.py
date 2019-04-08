import ctypes
import ctypes.util
import threading

# this is mostly copied from https://bugs.python.org/issue15500#msg230736

def patch():
    if getattr(threading.Thread.start, "_namedthreads_patched", None):
        # threading module is already patched
        return

    libpthread_path = ctypes.util.find_library("pthread")

    if not libpthread_path:
        # pthread library not found, not patching"
        return

    libpthread = ctypes.CDLL(libpthread_path)

    if not hasattr(libpthread, "pthread_setname_np"):
        # pthread library does not have pthread_setname_np function, not patching
        return

    pthread_setname_np = libpthread.pthread_setname_np
    pthread_setname_np.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    pthread_setname_np.restype = ctypes.c_int
    orig_start = threading.Thread.start

    def start(self):
        orig_start(self)
        try:
            name = self.name
            if name:
                if hasattr(name, "encode"):
                    name = name.encode('ascii', 'replace')
                ident = getattr(self, "ident", None)
                if ident is not None:
                    pthread_setname_np(ident, name[:15])
        except Exception:
            pass  # Don't care about failure to set name

    start._namedthreads_patched = True
    start._namedthreads_orig = threading.Thread.start
    threading.Thread.start = start
    return True


def unpatch():
    if not getattr(threading.Thread.start, "_namedthreads_patched", None):
        # threading module is not patched
        return
    patched_start = threading.Threading.start
    threading.Thread.start = patched_start._namedthreads_orig

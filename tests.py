import ctypes
import unittest
import sys
import time


def get_thread_name():
    import namedthreads

    libpthread = namedthreads._get_libpthread()
    thread_id = namedthreads._get_thread_id(libpthread)

    pthread_getname_np = libpthread.pthread_getname_np

    pthread_getname_np.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    pthread_getname_np.restype = ctypes.c_int

    name_buf = (ctypes.c_ubyte * 16)(0)
    name_buf_ptr = ctypes.cast(name_buf, ctypes.c_char_p)
    name_buf_size = ctypes.c_size_t(16)

    pthread_getname_np(thread_id, name_buf_ptr, name_buf_size)
    s = ctypes.cast(
        name_buf_ptr, ctypes.POINTER(ctypes.c_char * name_buf_size.value)
    ).contents
    return s.value.decode("ascii", "replace")


class ThreadBase(object):
    """Thread for testing the OS-visible name was set"""

    def __init__(self, name):
        super(ThreadBase, self).__init__(name=name)
        self.os_thread_name = None

    def run(self):
        self.os_thread_name = get_thread_name()


class TestThreadNames(unittest.TestCase):
    def setUp(self):
        try:
            del sys.modules["threading"]
        except KeyError:
            pass

    def test_unpatched(self):
        import threading

        self.assertFalse(hasattr(threading.Thread.start, "_namedthreads_patched"))

        class ThreadClass(ThreadBase, threading.Thread):
            pass

        thread = ThreadClass(name="mysupersleepythread")
        thread.start()
        time.sleep(1)

        self.assertNotIn("mysuper", thread.os_thread_name)
        thread.join()

    def test_patched(self):
        import namedthreads

        self.assertTrue(namedthreads.patch())

        import threading

        self.assertTrue(hasattr(threading.Thread, "_namedthreads_patched"))

        class ThreadClass(ThreadBase, threading.Thread):
            pass

        thread = ThreadClass(name="mysupersleepythread")
        thread.start()
        time.sleep(1)

        self.assertEqual("mysupersleepyth", thread.os_thread_name)
        thread.join()


if __name__ == "__main__":
    unittest.main()

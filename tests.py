import unittest
import sys
import time
import os


def target():
    time.sleep(0.5)


class TestThreadNames(unittest.TestCase):
    def setUp(self):
        try:
            del sys.modules["threading"]
        except KeyError:
            pass

    def test_unpatched(self):
        import threading
        self.assertFalse(hasattr(threading.Thread.start, "_namedthreads_patched"))
        thread = threading.Thread(target=target, name="mysupersleepythread")
        thread.start()
        # wait_for_thread(thread)
        thread_status = get_thread_status()
        self.assertNotIn("mysupersleepythread", thread_status)
        thread.join()

    def test_patched(self):
        import namedthreads
        self.assertTrue(namedthreads.patch())

        import threading

        self.assertTrue(hasattr(threading.Thread.start, "_namedthreads_patched"))
        thread = threading.Thread(target=target, name="mysupersleepythread")
        thread.start()
        # wait_for_thread(thread)
        thread_status = get_thread_status()
        self.assertNotIn("mysupersleepythread", thread_status)
        self.assertIn("mysupersleepyth", thread_status)
        thread.join()
        

def get_thread_status():
    s_pid = str(os.getpid())
    thread_id = int(list(p for p in os.listdir("/proc/{}/task".format(s_pid)) if p != s_pid)[0])
    with open("/proc/{}/task/{}/status".format(s_pid, thread_id), mode="r") as f:
        return f.read()


def wait_for_thread(thread_obj):
    for i in range(10):
        if thread_obj.is_alive():
            return
        time.sleep(0.1)
    assert False

if __name__ == '__main__':
    unittest.main()
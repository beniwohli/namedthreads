# namedthreads

![](https://api.travis-ci.org/beniwohli/namedthreads.svg?branch=master)

This is a hack to propagate thread names set in Python to the system.

*WARNING*: This is only meant for testing/debugging purposes. Do *NOT* run in production.

## The problem

You can name threads in Python like so:

    import threading

    my_thread = threading.Thread(target=my_func, name="my-thread")

But when running `ps`, `top` and similar, you'll notice that the thread name isn't visible in these tools,
making threading bugs somewhat harder to debug.

## The solution

A comment in [bpo-15500](https://bugs.python.org/issue15500#msg230736) lines out a monkeypatch that uses `ctypes` to set the name using `libpthread.pthread_setname_np`.
While this works beautifully, it hasn't been included in core python due to compatibility reasons. This module packages the monkeypatch in an easy to install package.

| *Before*                                   | *After*	                                 |
|--------------------------------------------|-------------------------------------------|
|![](http://s.woh.li/before_namedthreads.png)|![](http://s.woh.li/after_namedthreads.png)|


## Usage

### Install

    pip install namedthreads

### Manual patching

Run this as early as possible in your code:

    import namedthreads
    namedthreads.patch()

### Automatic patching

Inspired by Graham Dumpleton's [autowrapt](https://github.com/GrahamDumpleton/autowrapt), this module can
be activated automatically. Due to the [hacky nature](http://blog.dscpl.com.au/2015/04/automatic-patching-of-python.html)
of this approach, it is guarded by checking the presence of an environment variable, `NAMEDTHREADS`.
Automatic patching is only activated if this environment variable is set

    NAMEDTHREADS=1 python myscript.py
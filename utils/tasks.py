# Module taken from Bradley Shay's Eleos project
# (https://git.intrpt.net/bs/Eleos/blob/master/utils/task.py)
import threading
import time


class Task(object):
    def __init__(self, func, args=(), kwargs=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self._task)
        self.thread.daemon = False

    def _task(self):
        while True:
            if self.is_stopped():
                break
            self.func(*self.args, **self.kwargs)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()


class IntervalTask(Task):
    def __init__(self, interval, func, args=(), kwargs=None):
        super(IntervalTask, self).__init__(func, args, kwargs)
        self.interval = interval

    def _task(self):
        while True:
            time.sleep(self.interval - time.time() % self.interval)
            if self.is_stopped():
                break
            self.func(*self.args)


class ScheduleTask(Task):
    def __init__(self, runtime, func, args=(), kwargs=None):
        super(ScheduleTask, self).__init__(func, args, kwargs)
        self.runtime = runtime

    def _task(self):
        while True:
            started = time.time()
            if self.is_stopped():
                break
            if started >= self.runtime:
                self.func(*self.args)
                break
            else:
                interval = self.runtime - started
                time.sleep(interval - started % interval)


def run(func, daemon=False, args=(), kwargs=None):
    t = Task(func, args, kwargs)
    t.thread.daemon = daemon
    t.start()
    return t


def run_every(interval, func, daemon=False, args=(), kwargs=None):
    t = IntervalTask(interval, func, args, kwargs)
    t.thread.daemon = daemon
    t.start()
    return t


def run_at(runtime, func, daemon=False, args=(), kwargs=None):
    t = ScheduleTask(runtime, func, args, kwargs)
    t.thread.daemon = daemon
    t.start()
    return t


def run_in(delay, func, daemon=False, args=(), kwargs=None):
    t = ScheduleTask(time.time() + delay, func, args, kwargs)
    t.thread.daemon = daemon
    t.start()
    return t

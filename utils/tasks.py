# Module taken from Bradley Shay's Eleos project
# (https://git.intrpt.net/bs/Eleos/blob/master/utils/task.py)
import threading
import time

class Task(object):
    def __init__(self, func, args=()):
        self.func = func
        self.args = args
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self._task)
        self.thread.daemon = True

    def _task(self):
        pass

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()

class IntervalTask(Task):
    def __init__(self, interval, func, args=()):
        super(IntervalTask, self).__init__(func, args)
        self.interval = interval

    def _task(self):
        while True:
            time.sleep(self.interval - time.time() % self.interval)
            if self.is_stopped():
                break
            self.func(*self.args)

class ScheduleTask(Task):
    def __init__(self, runtime, func, args=()):
        super(ScheduleTask, self).__init__(func, args)
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

def run_every(interval, func, args=()):
    t = IntervalTask(interval, func, args)
    t.start()
    return t

def run_at(runtime, func, args=()):
    t = ScheduleTask(runtime, func, args)
    t.start()
    return t

def run_in(delay, func, args=()):
    t = ScheduleTask(time.time() + delay, func, args)
    t.start()
    return t

import threading
import numpy as np
import scipy.fftpack
import scipy.signal
from Queue import Queue

class Periodic():
    def __init__(self):
       self.refresh_rate = 0.25

    def do_every (self, interval, worker_func, iterations = 0):
        if iterations != 1:
          threading.Timer (
            interval,
            self.do_every, [interval, worker_func, 0 if iterations == 0 else iterations-1]
          ).start ()

        worker_func ()

    def run(self):
        self.do_every(self.refresh_rate, self.update)

class PerceptionModule(Periodic):
    def __init__(self, model):
        Periodic.__init__(self)
        self._buffer = Queue()
        self.pot = 0
        self.pots = []
        self.fft = []
        self.peaks = []

        self.model = model


    def update(self):
        self.pot = self.pot * 0.95
        if not self._buffer.empty():
           g = self._buffer.get()
           self.pot = len(g)
           self.model.recall(g)
           self.model.memorize(g)

        self.pots.append(self.pot)
        self.pots = self.pots[-100:]
        #print self.pots
        yf = scipy.fftpack.fft(self.pots)
        xf = np.linspace(0.0, 1.0/(2.0*0.25), len(self.pots)/2)
        if (len(self.pots) > 10):
           self.fft = zip(xf,2.0/len(self.pots) * np.abs(yf[0:len(self.pots)/2]))
           peaks = scipy.signal.find_peaks_cwt(2.0/len(self.pots) * np.abs(yf[0:len(self.pots)/2]), np.arange(1,5))
           self.peaks = np.zeros(len(xf))
           for each in peaks:
               self.peaks[each] = 10 * self.fft[each][1]
           self.peaks = zip(xf, self.peaks)
           print peaks #(self.fft)

    def push(self, data):
        self._buffer.put(data)




class MemoryModule(Periodic):
    def __init__(self, model):
        Periodic.__init__(self)
        self.model = model
        self.memory = {}
        self.novelty = 0

    def recall(self, m):
        if not hasattr(self.memory, m):
           self.novelty = self.novelty + 1

    def update(self):
        self.novelty = self.novelty * 0.95


class DecisionModule(Periodic):
    def __init__(self, model):
        Periodic.__init__(self)
        self.model = model
        self.noise = 0
        self.effection = 0

    def update(self):
        import numpy as np
        self.noise = np.random.normal(0,1,1)[0]
        self.effection = self.effection * 0.95
        if self.noise > 2.1:
           self.effection = 1
           self.model.action('EFFECTION@toto')


class Model():
    def __init__(self, **kwargs):
        self.per = PerceptionModule(self)
        self.mem = MemoryModule(self)
        self.dec = DecisionModule(self)

    def run(self):
        self.per.run()
        self.mem.run()
        self.dec.run()

    def sense(self, name):
       n = 0
       for each in [self.per, self.mem, self.dec]:
          if hasattr(each, name):
             n = n + 1
             val = getattr(each, name)
       if n == 0:
          raise Exception('%s not found'%name)
       elif n != 1:
          raise Exception('%s found multiple times'%name)
       return val

    def perceive(self, p):
       self.per.push(p)

    def memorize(self, m):
       self.mem.memory.setdefault(m, 0)
       self.mem.memory[m] = self.mem.memory[m] + 1

    def recall(self, m):
       self.mem.recall(m)




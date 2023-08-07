import matplotlib.pyplot as plt
import pyaudio
import numpy
import matplotlib
matplotlib.use('TkAgg')


class SwhRecorder:
    """Simple, cross-platform class to record from the microphone."""

    def __init__(self):
        """minimal garb is executed when class is loaded."""
        self.RATE = 48100
        self.BUFFERSIZE = 2**12
        self.secToRecord = .1
        self.threadsDieNow = False
        self.newAudio = False

    def setup(self):
        """initialize sound card."""
        self.buffersToRecord = int(self.RATE*self.secToRecord/self.BUFFERSIZE)
        if self.buffersToRecord == 0:
            self.buffersToRecord = 1
        self.samplesToRecord = int(self.BUFFERSIZE*self.buffersToRecord)
        self.chunksToRecord = int(self.samplesToRecord/self.BUFFERSIZE)
        self.secPerPoint = 1.0/self.RATE

        self.p = pyaudio.PyAudio()
        self.inStream = self.p.open(format=pyaudio.paInt16, channels=1,
                                    rate=self.RATE, input=True, frames_per_buffer=self.BUFFERSIZE)

        self.xsBuffer = numpy.arange(self.BUFFERSIZE)*self.secPerPoint
        self.xs = numpy.arange(self.chunksToRecord *
                               self.BUFFERSIZE)*self.secPerPoint
        self.audio = numpy.empty(
            (self.chunksToRecord*self.BUFFERSIZE), dtype=numpy.int16)
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.counter = 0

    def close(self):
        """cleanly back out and release sound card."""
        self.p.close(self.inStream)

    def getAudio(self):
        """get a single buffer size worth of audio."""
        audioString = self.inStream.read(self.BUFFERSIZE)
        return numpy.frombuffer(audioString, dtype=numpy.int16)

    def record(self, forever=True):
        """record secToRecord seconds of audio."""
        while True:
            if self.threadsDieNow:
                break
            for i in range(self.chunksToRecord):
                self.audio[i*self.BUFFERSIZE:(i+1)
                           * self.BUFFERSIZE] = self.getAudio()
            self.newAudio = True
            if forever == False:
                break
            # print(self.audio.flatten())
            self.fft()
            
    def fft(self, data=None, trimBy=10, logScale=False, divBy=100):

        if data == None:
            data = self.audio.flatten()
        left, right = numpy.split(numpy.abs(numpy.fft.fft(data)), 2)
        ys = numpy.add(left, right[::-1])
        if logScale:
            ys = numpy.multiply(20, numpy.log10(ys))
        xs = numpy.arange(self.BUFFERSIZE/2, dtype=float)
        if trimBy:
            i = int((self.BUFFERSIZE/2)/trimBy)
            ys = ys[:i]
            xs = xs[:i]*self.RATE/self.BUFFERSIZE
        if divBy:
            ys = ys/float(divBy)
        self.counter += 1
        if self.counter % 2 == 0:
            # print(xs, ys)
            self.ax.plot(xs, ys)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.ax.cla()
        return xs, ys


record = SwhRecorder()
record.setup()
record.record()

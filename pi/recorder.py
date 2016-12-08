import os
import sys
import time
import datetime
import json
import serial
import wave
import pyaudio
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import click

class Arduino:
    def __init__(self, port):
        self._port = port
        serial_from_arduino = None

    def connect(self):
        self._serial_from_arduino = serial.Serial(self._port, 115200)
        self._serial_from_arduino.flushInput()
        
    def get_data(self):
        if(self._serial_from_arduino.inWaiting() > 0):
            try:
                return json.loads(self._serial_from_arduino.readline().decode())
            except UnicodeDecodeError:
                return None
            except json.decoder.JSONDecodeError:
                return None
        else:
            return None

    def close(self):
        self._serial_from_arduino.close()


class EMG:
    def __init__(self):
        self._chunk = 1024
        self._format = pyaudio.paInt16
        self._channels = 1
        self._rate = 44100
        self._pyaudio = None

    def connect(self):
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(format=self._format, channels=self._channels, rate=self._rate,
                                          input=True, frames_per_buffer=self._chunk)

    def get_data(self):
        return self._stream.read(self._chunk)
        
    def close(self):
        self._stream.stop_stream()
        self._stream.close()
        self._pyaudio.terminate()
        
    @property
    def channels(self):
        return self._channels
        
    @property
    def sample_size(self):
        return self._pyaudio.get_sample_size(self._format)

    @property
    def sample_rate(self):
        return self._rate


class Data:
    def __init__(self):
        self._emgs = {}
        self._accX = {}
        self._accY = {}
        self._accZ = {}
        self._timestamp = None
        
    def set_timestamp(self, timestamp):
        self._timestamp = int(timestamp * 1000000)

    def append_acc(self, x, y, z):
        self._accX['%s_%04d' % (self._timestamp, 0)] = x
        self._accY['%s_%04d' % (self._timestamp, 0)] = y
        self._accZ['%s_%04d' % (self._timestamp, 0)] = z

    def append_emgs(self, data):
        for i, datum in enumerate(data):
            self._emgs['%s_%04d' % (self._timestamp, i)] = datum

    def get_dataframe(self):
        meg_series = pd.Series(self._emgs)
        accX_series = pd.Series(self._accX)
        accY_series = pd.Series(self._accY)
        accZ_series = pd.Series(self._accZ)
        return pd.DataFrame({'emg': meg_series, 'accX': accX_series, 'accY': accY_series, 'accZ':accZ_series})


class DataRecorder:
    def __init__(self, arduino_port):
        self._arduino = Arduino(arduino_port)
        self._emg = EMG()
        self._data = None

    def record(self, duration):
        self._arduino.connect()
        self._emg.connect()

        self._data = Data()
        
        print('Start recording...')
        start_time = time.time()
        while time.time() - start_time < duration:
            arduino_data = self._arduino.get_data()
            emg_data = self._emg.get_data()
            
            self._data.set_timestamp(time.time())
            if arduino_data is not None:
                try:
                    self._data.append_acc(arduino_data['accX'], arduino_data['accY'], arduino_data['accZ'])
                except KeyError:
                    pass
            self._data.append_emgs(np.fromstring(emg_data, dtype=np.int16))
        print('End recording. Recording time is %s.' % np.round(time.time() - start_time, 2))

        self._arduino.close()
        self._emg.close()

    def get_dataframe(self):
        return self._data.get_dataframe()

    def to_csv(self, fname):
        self._data.get_dataframe().to_csv(fname, sep=',', encoding='utf-8')

    def to_wav(self, fname):
        wf = wave.open(fname, 'wb')
        wf.setnchannels(self._emg.channels)
        wf.setsampwidth(self._emg.sample_size)
        wf.setframerate(self._emg.sample_rate)
        wf.writeframes(b''.join([item[1] for item in sorted(self._data._emgs.items(), key=lambda x: x[0])]))
        wf.close()
        

@click.command()
@click.option('--duration', default=10, help='Recording duration in sec')
@click.option('--path', default='.', help='Path to save directory.')
@click.option('--arduino_port', default='/dev/ttyACM0', help='Port used by arduino')
def record(duration, path, arduino_port):
    recorder = DataRecorder(arduino_port)
    recorder.record(duration)
    
    fname = os.path.join(path, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    recorder.to_csv('%s.csv' % fname)
    recorder.to_wav('%s.wav' % fname)
    
    
if __name__ == '__main__':
    record()

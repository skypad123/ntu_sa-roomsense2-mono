import pyaudio
import wave

class RpiMic: 

    def __init__(self, format= pyaudio.paInt16, \
    device_index = 1, audio_channel =2 , samp_rate = 44100, \
    chunk = 4096, file_location = 'temp/audio.wav'):
        self.format = format
        self.device_index = device_index
        self.audio_channel = audio_channel
        self.samp_rate = samp_rate
        self.chunk = chunk
        self.file_location = file_location
        self.mic = pyaudio.PyAudio()

    def capture(self, record_len = 2):
        stream = self.mic.open(format = self.format,rate = self.samp_rate,\
        channels = self.audio_channel, input_device_index = self.device_index, \
        input = True, frames_per_buffer=self.chunk)

        frames = []
       # loop through stream and append audio chunks to frame array
        for ii in range(0,int((self.samp_rate/self.chunk)* record_len)):
            data = stream.read(self.chunk)
            frames.append(data) 
        stream.stop_stream()
        stream.close()

        wavefile = wave.open(self.file_location,'wb')
        wavefile.setnchannels(self.audio_channel)
        wavefile.setsampwidth(self.mic.get_sample_size(format))
        wavefile.setframerate(self.samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()



# import wave
# import sys

# import pyaudio

# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1 if sys.platform == 'darwin' else 2
# RATE = 44100
# RECORD_SECONDS = 5

# with wave.open('output.wav', 'wb') as wf:
#     p = pyaudio.PyAudio()
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)

#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

#     print('Recording...')
#     for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
#         wf.writeframes(stream.read(CHUNK))
#     print('Done')

#     stream.close()
#     p.terminate()

if __name__ == "__main__":
    mic = RpiMic(file_location="temp/audio.wav")
    mic.capture()
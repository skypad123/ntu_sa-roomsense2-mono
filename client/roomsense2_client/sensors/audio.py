import pyaudio
import wave

class RpiMic: 

    def __init__(self, format= pyaudio.paInt16, \
    device_index = 0, audio_channel =2 , samp_rate = 44100, \
    chunk = 1024, file_location = 'temp/audio.wav'):
        self.format = format
        self.device_index = device_index
        self.audio_channel = audio_channel
        self.samp_rate = samp_rate
        self.chunk = chunk
        self.file_location = file_location

    def capture(self, record_len = 2):
        p = pyaudio.PyAudio()
        stream = p.open(format = self.format,rate = self.samp_rate,\
        channels = self.audio_channel, input_device_index = self.device_index, \
        input = True, frames_per_buffer=self.chunk)

        frames = []
       # loop through stream and append audio chunks to frame array
        for ii in range(0,int((self.samp_rate/self.chunk)* record_len)):
            data = stream.read(self.chunk)
            frames.append(data) 
        stream.stop_stream()
        stream.close()
        p.terminate()

        wavefile = wave.open(self.file_location,'wb')
        wavefile.setnchannels(self.audio_channel)
        wavefile.setsampwidth(p.get_sample_size(self.format))
        wavefile.setframerate(self.samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

if __name__ == "__main__":

    # p = pyaudio.PyAudio()
    # info = p.get_host_api_info_by_index(0)
    # numdevices = info.get('deviceCount')

    # for i in range(0, numdevices):
    #     if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
    #         print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            
    mic = RpiMic(file_location="temp/audio.wav")
    mic.capture(record_len=10)

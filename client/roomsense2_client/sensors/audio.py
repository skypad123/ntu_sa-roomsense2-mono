import pyaudio
import wave
import logging

class RpiMic: 

    def __init__(self, format= pyaudio.paInt16, \
        audio_channel = 2 , samp_rate = 44100, \
        chunk = 1024, file_location = 'temp/audio.wav'):

        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        mic_map = dict()

        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                mic_map[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i

        if "dmic_sv" in mic_map.keys():
            self.device_index = mic_map["dmic_sv"]
        else: 
            self.device_index = 0

        self.format = format
        self.audio_channel = audio_channel
        self.samp_rate = samp_rate
        self.chunk = chunk
        self.file_location = file_location

    def capture(self, record_len = 2):

        chunk = self.chunk      # Each chunk will consist of 1024 samples
        sample_format = self.format     # 16 bits per sample
        channels = self.format      # Number of audio channels
        fs = self.samp_rate       # Record at 44100 samples per second
        time_in_seconds = record_len
        filename = self.file_location

        p = pyaudio.PyAudio()  # Create an interface to PortAudio
    
        #Open a Stream with the values we just defined
        stream = p.open(format=sample_format,
                        channels = channels,
                        rate = fs,
                        frames_per_buffer = chunk,
                        input = True,input_device_index=self.device_index)
        
        frames = []  # Initialize array to store frames
        
        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * time_in_seconds)):
            data = stream.read(chunk)
            frames.append(data)
        
        # Stop and close the Stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Open and Set the data of the WAV file
        file = wave.open(filename, 'wb')
        file.setnchannels(channels)
        file.setsampwidth(p.get_sample_size(sample_format))
        file.setframerate(fs)
        
        #Write and Close the File
        file.writeframes(b''.join(frames))
        file.close()

if __name__ == "__main__":

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    mic_map = dict()

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            mic_map[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i

    
    mic = RpiMic(file_location="audio.wav")
    mic.capture(record_len=10)

## Project Requirements



## Enviroment File Temple

```
# give the device a uniqiue name used to filter its data in the database
DEVICE_NAME="prototype #2"
# OPTIONAL: you can add this to give a hint as to the actual location of the sensor vairable
DEVICE_LOCATION="Nanyang Techonological University, Room 1"

# insert the api endpoint in this variable
API_ENDPOINT="http://192.168.1.236:8000"
```

## Headless Client Software Configuration
### Step-by-step Instructions

#### Flash RPI Zero
  1. install rpi imager @ https://www.raspberrypi.com/software/
  2. mount rpi SD card
  3. run the rpi imager
  4. select `Raspberry Pi Zero w` as the device
  5. select `Raspberry Pi OS Lite(Legacy)` as the operating system.
  6. select the rpi SD card as the storage device
  7. on clicking next, edit the setting such as the username and password of the rpi admin as well as entering wlan config information for network connectivity
  and optionally, the hostname under general section.
  8. enable ssh using password auth under the services sections
  9. flash the SD by clicking `Yes`
  10.  insert sd card into rpi, and wait for rpi to connect to wifi stated in flashing state

#### Setup RPI Zero
  -  in the terminal use either the cmd ```arp -a``` to find the rpi's ip address or any alternative ip scanner 
  - ssh into rpi via terminal with the cmd ```ssh <admin-username>@<rpi-ip_address>```
  -  enter the admin account's password stated in the flashing state when prompted
  -  run the cmd ```sudo apt-get upgrade && sudo apt-get update``` to update and upgrade the apt package manager
  -  run the cmd ```sudo apt install make build-essential libssl-dev zlib1g-dev 
                libbz2-dev libreadline-dev libsqlite3-dev 
                wget curl llvm libncursesw5-dev xz-utils 
                tk-dev libxml2-dev libxmlsec1-dev libffi-dev 
                liblzma-dev libc6 python3-dev gcc``` to install essential build tools
  -  run the cmd ```sudo raspi-config```
  - enable 'ARM I2C Interface' & 'Legacy Camera' under 'Interface Options'
  - enable GPIO

  
#### Install git & python/pip
  - run the cmd ```sudo apt-get install git python3-pip``` to install git
  <!-- 18.   run the cmd ```sudo apt-get install python3-pip``` to install pip, the python package manager -->
  - run the cmd ```sudo pip3 install virtualenv``` to install virtualenv, the python virtual environment manager

#### Install poetry
  - run the cmd ```curl -sSL https://install.python-poetry.org | python3 -``` to install poetry
  - edit the bash config via `nano ~/.bashrc` and append the line `export PATH="/home/rpi/.local/bin:$PATH"`

#### Install pyenv
  -   run the cmd ```curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash``` to install pyenv, the python version manager 
  -  run the cmd ```nano ~/.bashrc``` to open PATH config and append the lines
  ``` 
  export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)" 
  ```
   to the bottom of the file and save the buffer
  -  reconnect the ssh session for PATH to take effect

#### Install driver for mic
  -    run the cmd ```sudo pip3 install --upgrade adafruit-python-shell``` to install adafruit-shell
  -    run the cmd ```wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py``` to download script
  -    run the cmd ```sudo python3 i2smic.py``` to run the installation script
  -    type `y` and enter to have the i2s mic module support to be load at boot
  -    type `y` and enter to reboot rpi

####  Install python interface to mic driver
  -    run ``` sudo apt-get install python3-pyaudio portaudio19-dev```


#### Increase audio gain of micphone
- modify ~/.asoundrc via  ``` nano ~/.asoundrc``` and append the following

```
#This section makes a reference to your I2S hardware, adjust the card name
# to what is shown in arecord -l after card x: before the name in []
#You may have to adjust channel count also but stick with default first
pcm.dmic_hw {
	type hw
	card sndrpii2scard
	channels 2
	format S32_LE
}

#This is the software volume control, it links to the hardware above and after
# saving the .asoundrc file you can type alsamixer, press F6 to select
# your I2S mic then F4 to set the recording volume and arrow up and down
# to adjust the volume
# After adjusting the volume - go for 50 percent at first, you can do
# something like 
# arecord -D dmic_sv -c2 -r 48000 -f S32_LE -t wav -V mono -v myfile.wav
pcm.dmic_sv {
	type softvol
	slave.pcm dmic_hw
	control {
		name "Boost Capture Volume"
		card sndrpii2scard
	}
	min_dB -3.0
	max_dB 30.0
}
```
- run ```arecord -D dmic_sv -c2 -r 44100 -f S32_LE -t wav -V mono -v file.wav``` for one second and cancel it with ctrl + c.
- run `alsamixer` and press F6 and select ```snd_rpi_i2s_card```
- press F4 and increase the gain with up arrow key till 15.96
- exit the app with esc key


#### run the application
  - run the cmd ```git clone "https://github.com/skypad123/ntu_sa-roomsense2-mono.git"``` to clone the project into the rpi 
  - run the cmd ```cd ntu_sa-roomsense2-mono/client``` to target project folder
  - run the cmd ```pyenv install 3.11``` to install the latest python3.11 version used in the project; this step will take a while
  - run the cmd `pyenv local 3.11.x` to set the correct local env for the project folder
  - run the cmd `poetry shell` to run the venv for current project
  - copy .env file into the dir via ``` nano .env```.
  - run the cmd `poetry install` to install the dependencies for the current project
  - run the cmd `python roomsense2_client/main.py` to run the project
  - configuration of the client is now completed

### Optional actions

#### Debugging: Checking I2C Interface
  1.    run the cmd ```sudo apt-get install i2c-tools``` to install i2cdetect tools
  2.    run the cmd ```sudo raspi-config``` to ensure that 'ARM I2C Interface' is enabled under 'Interface Options'
  3.    run the cmd ```sudo i2cdetect -y 1``` to scan and check for all i2c based sensors (29,40,48,62)

#### Debugging: Download file for view/monitoring
  1. run  ```scp <admin>@<ip-address>:~/git-projects/ntu_sa-roomsense2-mono/client/temp/image.jpg ~/Desktop/image.jpg ``` to copy the temp image file to local computer


### I2C Modules
- 3.3v 
  - TSL2591 : Light Sensor - i2c addr  0x29
  - BH1750 : Light Sensor - i2x addr 0x23
  - HTU2x : Humidity Sensor - i2c addr 0x40
  - SDC41: Co2 sensor - i2c addr 0x62
  - 

### Libraries & Datasheets Used
1. https://github.com/adafruit/Adafruit_CircuitPython_SCD4x
2. https://github.com/adafruit/Adafruit_CircuitPython_TSL2591
3. https://github.com/adafruit/Adafruit_CircuitPython_HTU21D
4. https://files.waveshare.com/upload/2/2f/SGM58031.pdf
5. https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test
6. https://python-sounddevice.readthedocs.io/en/0.3.12/installation.html
7. https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout

### More References
- running rpi headless -
https://learn.sparkfun.com/tutorials/headless-raspberry-pi-setup/wifi-with-dhcp#:~:text=Enable%20WiFi,wpa_supplicant%2F%20directory%20in%20the%20filesystem.
- scanning network ip -
https://www.dnsstuff.com/scan-network-for-device-ip-address
- scanning i2c devices -
https://learn.adafruit.com/scanning-i2c-addresses/i2c-basics



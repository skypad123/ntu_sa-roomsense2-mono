## Project Requirements


## Headless Client Software Configuration
### Step-by-step Instructions

1. install rpi imager @ https://www.raspberrypi.com/software/
2. mount rpi SD card
3. run the rpi imager
4. select `Raspberry Pi Zero 2w` as the device
5. select `Raspberry Pi OS Lite(Legacy)` as the operating system.
6. select the rpi SD card as the storage device
7. on clicking next, edit the setting such as the username and password of the rpi admin as well as entering wlan config information for network connectivity
and optionally, the hostname under general section.
8. enable ssh using password auth under the services sections
9. flash the SD by clicking `Yes`
10.  insert sd card into rpi, and wait for rpi to connect to wifi stated in flashing state
11.  in the terminal use either the cmd ```arp -a``` to find the rpi's ip address or any alternative ip scanner 
12.  ssh into rpi via terminal with the cmd ```ssh <admin-username>@<rpi-ip_address>```
13.  enter the admin account's password stated in the flashing state when prompted
14.  run the cmd ```sudo apt-get upgrade && sudo apt-get update``` to update and upgrade the apt package manager
15.  run the cmd ```sudo apt install make build-essential libssl-dev zlib1g-dev 
               libbz2-dev libreadline-dev libsqlite3-dev 
               wget curl llvm libncursesw5-dev xz-utils 
               tk-dev libxml2-dev libxmlsec1-dev libffi-dev 
               liblzma-dev git python3-pip libc6 python3-dev gcc`` to install essential build tools
16.  run the cmd ```sudo raspi-config``` to enable 'ARM I2C Interface' under 'Interface Options'
17.  run the cmd ```sudo apt-get install git``` to install git
18.   run the cmd ```sudo apt-get install python3-pip``` to install pip, the python package manager
19.    run the cmd ```sudo pip3 install virtualenv``` to install virtualenv, the python virtual environment manager
20.   run the cmd ```curl https://pyenv.run | bash``` to install pyenv, the python version manager 
21.   run the cmd ```curl -sSL https://install.python-poetry.org | python3 -``` to install poetry
22.   run the cmd ```nano ~/.bashrc``` to open PATH config and add the line ```export PATH="/home/rpi/.local/bin:$PATH"``` and ```export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"```to the bottom of the file and save the buffer
23.   reconnect the ssh session for PATH to take effect
24.   run the cmd ```cd ~ && mkdir git-projects && cd git-projects``` to create project dir and target it
25.   run the cmd ```git clone "https://github.com/skypad123/ntu_sa-roomsense2-client.git"``` to clone the project into the rpi the git-projects folder
26.   run the cmd ```cd ntu_sa-roomsense2-client``` to target project folder
27.   run the cmd ```pyenv install 3.11``` to install the latest python3.11 version used in the project; this step will take a while
28.   run the cmd `pyenv local 3.11.x` to set the correct local env for the project folder
29.   run the cmd `poetry shell` to run the venv for current project
30.   run the cmd `poetry install` to install the dependencies for the current project
31.   run the cmd `python main.py` to run the project
32.   configuration of the client is now completed
    
### Optional: Checking of I2C sensors connections
1.    run the cmd ```sudo apt-get install i2c-tools``` to install i2cdetect tools
2.    run the cmd ```sudo raspi-config``` to ensure that 'ARM I2C Interface' is enabled under 'Interface Options'
3.    run the cmd ```sudo i2cdetect -y 1``` to scan and check for all i2c based sensors (29,40,48,62)


### install script for mic
1.    run the cmd ```sudo pip3 install --upgrade adafruit-python-shell``` to install adafruit-shell
2.    run the cmd ```wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py``` to download script
3.    run the cmd ```sudo python3 i2smic.py``` to run the installation script
4.    type `y` and enter to have the i2s mic module support to be load at boot
5.    type `y` and enter to reboot rpi


enable gpio

### Configuration References
- running rpi headless -
https://learn.sparkfun.com/tutorials/headless-raspberry-pi-setup/wifi-with-dhcp#:~:text=Enable%20WiFi,wpa_supplicant%2F%20directory%20in%20the%20filesystem.
- scanning network ip -
https://www.dnsstuff.com/scan-network-for-device-ip-address
- scanning i2c devices -
https://learn.adafruit.com/scanning-i2c-addresses/i2c-basics

### Libraries & Datasheets Used
https://github.com/adafruit/Adafruit_CircuitPython_SCD4x
https://github.com/adafruit/Adafruit_CircuitPython_TSL2591
https://github.com/adafruit/Adafruit_CircuitPython_HTU21D
https://files.waveshare.com/upload/2/2f/SGM58031.pdf
https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test

### Modules
- 3.3v 
  - TSL2591 : Light Sensor - i2c addr  0x29
  - HTU2x : Humidity Sensor - i2c addr 0x40
- 5.0v 
  - SDC41: Co2 sensor - i2c addr 0x62



sudo apt install libc6


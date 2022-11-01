# Make sure that send_trigs.py file exists in home directory where we want it
FILE=send_trigs.py
if test -f "$FILE"; then
	echo "Found $FILE ... running from correct directory"
else
	echo "Did not find path to $FILE ."
	echo " "
	echo "SETUP FAILED ... change directory to stimulation_162 folder then rerun setup."
	return 1
fi

# Get the absolute path to the stimulation_162 folder
DIR_PATH=$(pwd)

# Make sure packages are installed on Pi
pip3 install -r requirements.txt

# Insert the alias to run stimulation into the raspi bash file
sudo echo "alias stim=\"python3 ${DIR_PATH}/send_trigs.py\"" >> ~/.bashrc

# Insert the alias to help with command to run stimulation in bash file
sudo echo "alias help-stim=\"sh ${DIR_PATH}/help.sh\"" >> ~/.bashrc

# Implement changes to bashrc
source ~/.bashrc
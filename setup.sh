# Make sure that send_trigs.py file exists in home directory where we want it
FILE = ~/stimulation_162/send_trigs.py
if test -f "$FILE"; then
	echo "Found $FILE."
else
	echo "Did not find path to send_trigs.py."
	echo " "
	echo "  SETUP FAILED ... rerun setup required"
	echo " "
	echo "  Please place stimulation_162 folder from github in home directory (~/)"
fi

# Make sure packages are installed on Pi
pip3 install -r requirements.txt

# Insert the alias to run stimulation into the raspi bash file
sudo echo 'alias stim="python3 ~/stimulation_162/send_trigs.py"' >> ~/.bashrc

# Insert the alias to help with command to run stimulation in bash file
sudo echo 'alias help-stim="~/stimulation_162/help.sh"' >> ~/.bashrc
#!/bin/bash

# Function to append file1 to file2 with backup handling (.bak naming convention)
append_with_backup() {
    local file1="$1"
    local file2="$2"
    local backup_file2="${file2}.bak"

    # Create a backup of file2 if it doesn't already exist
    if [ ! -f "$backup_file2" ]; then
        echo "Creating a backup of $file2 as $backup_file2..."
        cp "$file2" "$backup_file2"
    fi

    # Restore file2 from the backup
    echo "Restoring $file2 from the backup..."
    cp "$backup_file2" "$file2"

    # Append the contents of file1 to file2
    echo "Appending $file1 to $file2..."
    cat "$file1" >> "$file2"

    echo "Operation complete."
}

#########
## ssh ##
#########
cd
echo "installing ssh"
yes | apt update
yes | apt install apache2 # (is it necessary ?)

yes | apt install openssh-server
systemctl enable ssh
systemctl start ssh
cd

#################
## dhcp server ##
#################
cd
echo "Installing ifup-ifdown"
sudo apt install ifupdown

echo "Installing net-tools"
sudo apt install net-tools

echo "Installing isc-dhcp-server"
yes | apt install isc-dhcp-server

# Configuring dhcp server
echo "configuring dhcp server"

# /etc/default/isc-dhcp-server
# todo copy backup
sudo append_with_backup "./isc-dhcp-server" "/etc/default/isc-dhcp-server"
# sudo cat ./isc-dhcp-server >> /etc/default/isc-dhcp-server

# /etc/dhcp/dhcpd.conf
# todo copy backup
sudo append_with_backup "./dhcpd.conf" "/etc/dhcp/dhcpd.conf"
# sudo cat ./dhcpd.conf >> /etc/dhcp/dhcpd.conf

# auto loop back
# todo copy backup
sudo touch  /etc/network/interfaces.d/locals
sudo append_with_backup "./locals" "/etc/network/interfaces.d/locals"
#sudo cat ./locals >> /etc/network/interfaces.d/locals

# Apply
ifdown eth0
ifup eth0

systemctl enable isc-dhcp-server
systemctl status isc-dhcp-server

ifdown eth0

##################
## Witty shield ##
##################
cd
echo "Install for Witty"
yes | apt install curl # needed for witty isntall.sh

cd
mkdir witty
cd witty
wget https://www.uugear.com/repo/WittyPi4/install.sh
yes | sh install.sh
cd

####################
## Drive mounting ## TODO check if tis ok
####################
cd
echo "Installing drive related pakages"
sudo fdisk -l
yes | sudo apt install nfs-common
yes | sudo apt install cifs-utils
sudo ntfsfix -d /dev/sdb1

###########
## samba ##
###########
cd
echo "Installing Samba (drive ethernet)"
yes | sudo apt install samba samba-common-bin smbclient cifs-utils

# todo copy backup
sudo append_with_backup "./smb.conf" "/etc/samba/smb.conf"
#sudo cat ./smb.conf >> /etc/samba/smb.conf

sudo service smbd restart

# todo copy backup
sudo append_with_backup "./fstab" "/etc/fstab"
#sudo cat ./fstab >> /etc/fstab

#####################
## for pin control ##
#####################
cd
echo "Installing ping control"
yes | apt install python3-lgpio
cd

########################
## Installing piradar ##
########################

mkdir "$HOME/program/piradar"
git clone https://github.com/JeromeJGuay/piradar.git

cd "$HOME/program/piradar"
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# install program
.venv/bin/python3 -m pip install -e ../piradar
cd

#####################
## Piradar Service ##
#####################

# will overwrite the piradar.service file pulled from github for proper paths.

cat > "$HOME/program/piradar/raspi_scripts/piradar.service" << EOF
[Unit]
Description=Start radar run app
After=multi-user.target


[Service]
Type=simple
User=root
WorkingDirectory=$HOME/program/piradar
ExecStartPre=ifup eth0
ExecStart=$HOME/program/piradar/.venv/bin/python3 $HOME/program/piradar/piradar/scripts/schedule_recording.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cp "$HOME/program/piradar/raspi_scripts/piradar.service" /etc/systemd/system/piradar.service

systemctl daemon-reload
systemctl enable piradar.service


ifup eth0

echo "Piradar service should be up and running"

systemctl status piradar.service
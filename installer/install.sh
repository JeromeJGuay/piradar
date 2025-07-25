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

HOME=$(eval echo ~"$SUDO_USER")
SCRIPT_DIR=$(dirname "$(realpath "$0")")

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
append_with_backup "$SCRIPT_DIR/isc-dhcp-server" "/etc/default/isc-dhcp-server"
# sudo cat ./isc-dhcp-server >> /etc/default/isc-dhcp-server

# /etc/dhcp/dhcpd.conf
append_with_backup "$SCRIPT_DIR/dhcpd.conf" "/etc/dhcp/dhcpd.conf"
# sudo cat ./dhcpd.conf >> /etc/dhcp/dhcpd.conf

# auto loop back
sudo touch  /etc/network/interfaces.d/locals
append_with_backup "$SCRIPT_DIR/locals" "/etc/network/interfaces.d/locals"
#sudo cat ./locals >> /etc/network/interfaces.d/locals

# Apply
ifdown eth0
ifup eth0

systemctl enable isc-dhcp-server
#systemctl status isc-dhcp-server

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

###########
## samba ##
###########
# samba not working on raspian for some reason.

#echo "Installing Samba (drive ethernet)"
yes | sudo apt install samba samba-common-bin smbclient cifs-utils

yes | sudo apt install exfat-fuse exfat-utils

# making a bakup of smb.conf if none exist.
if [ ! -f /etc/samba/smb.conf.bak ]; then
  sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak
fi

sudo cp "$SCRIPT_DIR/smb.conf" /etc/samba/smb.conf

yes | apt install ufw

sudo ufw allow samba

append_with_backup "$SCRIPT_DIR/fstab" "/etc/fstab"
sudo cat ./fstab >> /etc/fstab
sudo mount -a

### To allow other drive format.


#systemctl daemon-reload

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

mkdir -p "$HOME/program"
cd "$HOME/program"
#git clone https://github.com/JeromeJGuay/piradar.git
git clone -b main-v2.0.0 https://github.com/JeromeJGuay/piradar.git


cd piradar

python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# install program
.venv/bin/python3 -m pip install -e ../piradar
cd

#####################
## Piradar Service ##
#####################
# To test FIXME
cat > /etc/systemd/system/piradar.service << EOF
[Unit]
Description=Start radar run app
After=multi-user.target


[Service]
Type=simple
User=root
WorkingDirectory=$HOME/program/piradar
ExecStartPre=ifup eth0
ExecStart=/bin/bash $HOME/program/piradar/piradar/scripts/schedule_recording.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF


systemctl daemon-reload
systemctl enable piradar.service


ifup eth0

# Optionnal but setting the time zone to utc
sudo timedatectl set-timezone UTC


echo "reboot required"
# systemctl status piradar.service



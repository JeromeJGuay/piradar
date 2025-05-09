#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi


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
apt update
apt install -y apache2 # (is it necessary ?)

apt install -y openssh-server
systemctl enable ssh
systemctl start ssh
cd

#################
## dhcp server ##
#################
cd
echo "Installing ifup-ifdown"
apt install ifupdown

echo "Installing net-tools"
apt install net-tools

echo "Installing isc-dhcp-server"
apt install -y isc-dhcp-server

# Configuring dhcp server
echo "configuring dhcp server"

# /etc/default/isc-dhcp-server
append_with_backup "$SCRIPT_DIR/isc-dhcp-server" "/etc/default/isc-dhcp-server"

systemctl disable dhcpcd
systemctl stop dhcpcd


# /etc/dhcpcd.conf
append_with_backup "$SCRIPT_DIR/dhcpcd.conf" "/etc/dhcpcd.conf"

# auto loop back
touch  /etc/network/interfaces.d/locals
append_with_backup "$SCRIPT_DIR/locals" "/etc/network/interfaces.d/locals"

# Apply
ifdown eth0
ifup eth0

systemctl enable isc-dhcp-server

ifdown eth0

##################
## Witty shield ##
##################
cd
echo "Install for Witty"
apt install -y curl # needed for witty isntall.sh

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
apt install -y samba samba-common-bin smbclient cifs-utils

apt install -y exfat-fuse exfat-utils

# making a bakup of smb.conf if none exist.
if [ ! -f /etc/samba/smb.conf.bak ]; then
  mv /etc/samba/smb.conf /etc/samba/smb.conf.bak
fi

cp "$SCRIPT_DIR/smb.conf" /etc/samba/smb.conf

apt install -y ufw

ufw allow samba

append_with_backup "$SCRIPT_DIR/fstab" "/etc/fstab"
cat ./fstab >> /etc/fstab
mount -a

### To allow other drive format.


#systemctl daemon-reload

#####################
## for pin control ##
#####################
cd
echo "Installing ping control"
apt install -y python3-lgpio
cd

########################
## Installing piradar ##
########################

mkdir -p "$HOME/program"
cd "$HOME/program"
git clone https://github.com/JeromeJGuay/piradar.git

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

echo "\n\n --- reboot required ---"
# systemctl status piradar.service



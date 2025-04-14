cd
echo "installing ssh"
sudo apt update
sudo apt install apache2 # (is it necessary ?)

sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
cd

# NEED TO INSTALL ifup
cd
echo "Installing ifup-ifdown"
sudo apt install ifupdown

# for pin control
cd
echo "Installing ping control"
sudo apt install python3-lgpio
cd


# Witty shield
cd
echo "Install for Witty"
sudo apt install curl # needed for witty isntall.sh

cd mkdir witty
cd witty
wget https://www.uugear.com/repo/WittyPi4/install.sh
sudo sh install.sh
cd

# samba
cd
echo "Installing Samba (drive ethernet)"
sudo apt install samba samba-common-bin smbclient cifs-utils
cd



# drive mounting TODO check if tis ok
cd
echo "Installing drive related pakages"
sudo fdisk -l
sudo apt install nfs-common
sudo apt install cifs-utils
sudo ntfsfix -d /dev/sdb1
cd
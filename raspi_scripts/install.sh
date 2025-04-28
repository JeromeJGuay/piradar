# ssh
cd
echo "installing ssh"
sudo apt update
sudo apt install apache2 # (is it necessary ?)

sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
cd


#### dhcp server
cd
echo "Installing ifup-ifdown"
sudo apt install ifupdown

echo "Installing net-tools"
sudo apt install net-tools

echo "Installing isc-dhcp-server"
sudo apt install isc-dhcp-server

# Configuring dhcp server
echo "configuring dhcp server"

# /etc/default/isc-dhcp-server
echo 'INTERFACESv4="eth0"' >> /etc/default/isc-dhcp-server

# /etc/dhcp/dhcpd.conf
echo 'option domain-name "capteur.local";' >> /etc/dhcp/dhcpd.conf
echo 'option domain-name-servers 1.1.1.1, 8.8.8.8;' >> /etc/dhcp/dhcpd.conf
echo '' >> /etc/dhcp/dhcpd.conf
echo 'subnet 192.168.1.0 netmask 255.255.255.0 {' >> /etc/dhcp/dhcpd.conf
echo '  range 192.168.1.110 192.168.1.210;' >> /etc/dhcp/dhcpd.conf
echo '  option subnet-mask 255.255.255.0;' >> /etc/dhcp/dhcpd.conf
echo '  option routers 192.168.1.100;' >> /etc/dhcp/dhcpd.conf
echo '  option broadcast-address 192.168.1.255;' >> /etc/dhcp/dhcpd.conf
echo '}' >> /etc/dhcp/dhcpd.conf
echo '' >> /etc/dhcp/dhcpd.conf
echo 'default-lease-time 600;' >> /etc/dhcp/dhcpd.conf
echo 'max-lease-time 7200;' >> /etc/dhcp/dhcpd.conf
echo '' >> /etc/dhcp/dhcpd.conf
echo 'authoritative;' >> /etc/dhcp/dhcpd.conf

# auto loop back
touch /etc/network/interfaces.d/locals
echo 'auto lo'  >> /etc/network/interfaces.d/locals
echo 'iface lo inet loopback' >> /etc/network/interfaces.d/locals

echo 'auto eth0'  >> /etc/network/interfaces.d/locals
echo 'allow-hotplug eth0'  >> /etc/network/interfaces.d/locals
echo 'iface eth0 inet static'  >> /etc/network/interfaces.d/locals
echo '        address 192.168.1.100'  >> /etc/network/interfaces.d/locals
echo '        netmask 255.255.255.0'  >> /etc/network/interfaces.d/locals
echo '        broadcast 192.168.1.255'  >> /etc/network/interfaces.d/locals
echo '    		gateway 192.168.1.1'  >> /etc/network/interfaces.d/locals

# Apply

sudo ifdown eth0
sudo ifup eth0

sudo systemctl status isc-dhcp-server
sudo systemctl enable isc-dhcp-server


#### for pin control
cd
echo "Installing ping control"
sudo apt install python3-lgpio
cd


#### Witty shield
cd
echo "Install for Witty"
sudo apt install curl # needed for witty isntall.sh

cd mkdir witty
cd witty
wget https://www.uugear.com/repo/WittyPi4/install.sh
sudo sh install.sh
cd

#### samba
cd
echo "Installing Samba (drive ethernet)"
sudo apt install samba samba-common-bin smbclient cifs-utils
cd



#### drive mounting TODO check if tis ok
cd
echo "Installing drive related pakages"
sudo fdisk -l
sudo apt install nfs-common
sudo apt install cifs-utils
sudo ntfsfix -d /dev/sdb1
cd

#### Add service for radar
cp /home/capteur/program/piradar/raspi_scripts/piradar.service /etc/systemd/system/piradar.service

systemctl daemon-reload
systemctl enable radar_startup.service


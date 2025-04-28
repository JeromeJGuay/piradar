# ssh
cd
echo "installing ssh"
yes | apt update
yes | apt install apache2 # (is it necessary ?)

yes | apt install openssh-server
systemctl enable ssh
systemctl start ssh
cd


#### dhcp server
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
ifdown eth0
ifup eth0

systemctl enable isc-dhcp-server
systemctl status isc-dhcp-server

ifdown eth0


#### Witty shield
cd
echo "Install for Witty"
yes | apt install curl # needed for witty isntall.sh

cd
mkdir witty
cd witty
wget https://www.uugear.com/repo/WittyPi4/install.sh
yes | sh install.sh
cd

#### samba
cd
echo "Installing Samba (drive ethernet)"
yes | sudo apt install samba samba-common-bin smbclient cifs-utils
cd



#### drive mounting TODO check if tis ok
cd
echo "Installing drive related pakages"
sudo fdisk -l
yes | sudo apt install nfs-common
yes | sudo apt install cifs-utils
sudo ntfsfix -d /dev/sdb1
cd


#### for pin control
cd
echo "Installing ping control"
yes | apt install python3-lgpio
cd

#### installing requirements
cd /home/capteur/program/piradar
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# install program
.venv/bin/python3 -m pip install -e ../piradar
cd

#### Add service for radar
cp /home/capteur/program/piradar/raspi_scripts/piradar.service /etc/systemd/system/piradar.service

systemctl daemon-reload
systemctl enable piradar.service


ifup eth0

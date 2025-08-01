En construction...

### Raspberry Pi 4
  + (TODO) Plan de l'électronique de contrôle du radar/gpio 
  + WittyPi
 

  + Installation de RaspberryPi OS (64).
    + Nommé l'utilisateur `capteur`
    + Nommé l'ordinateur: `capteur-desktop`
    
+ Mettre à jour de RaspberryPi OS

+ Télécharger l'installateur dans les releases (v3.0.0).

### Avant l'installation de piradar.
  + Brancher un disque dur externe.

  + Modifier les fichiers `fstab` pour ajouter.
    + Utiliser la commande: lsblk -o "NAME,UUID,SIZE,LABEL,PATH"
    + Mettre le bon <uuid> ainsi que le nom lecteur externe (2To) dans la ligne:
     ```
     /dev/disk/by-uuid/<uuid> media/capteur/2To auto defaults,nofail,umask=000,noatime 0 2
    ```

+ Nom lecteur externe `2To` (`/media/capteur/2To`) doit être le même dans :
  + (avant installation) smb.conf pour le bon nom de lecteur externe.
  ```ini
  [2To]
   path = /media/capteur/2To
  ```
### Installation
```bash
 sudo bash install.sh
  ```
### Après l'installation:
  + Nom du lecteur externe :
    + `/home/capteur/.piradar/piradar_config.ini`
      ```ini
      [DRIVES]
      drive_path = /media/capteur/2To
      ```
+ WITTYPI configuration:
  + todo:
  + stop piradar.service (sudo systemctl stop piradar.service)
  + turn of eth0 interface to access wifi (sudo ifdown eth0)
  + copy the schedule_daily_reboot.wpi file to the witty schedules directory (~/witty/wittypi/schedules/)
  + run the witty/wittypi/wittyPI.sh
    + Sync time with network (opt. 3)
    + chose the schedule_daily_reboot schedule. (opt. 6)

### Reboot !

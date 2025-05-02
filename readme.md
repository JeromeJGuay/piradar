En construction...

+ Installation sur un rasberry pi4.

+ Mettre à jour raspian OS.

+ Télécharger l'installateur dans les releases.

+ Brancher un disque dur externe

+ Modifier les fichiers `fstab`.
 - Type the following for UUID: lsblk -o "NAME,UUID,SIZE,LABEL,PATH"
 - fstab: /dev/disk/by-id/...


+ Lancer `install.sh`

+ Dans le repertoire `~/program/piradar/piradar/scripts/` verifier que le path HOME est le bon.


+ SAMBA (file sharing on network, ne semble pas fonctionner sur raspianOS) 
  + Modifier le ficiher `/etc/samba/smb.conf`
    + Changer les lignes correspondantes :
      ```
      create mask = 0777
      directory mask = 0777
      ```

    + Ajouter ces lignes à la fin.
      ```
      [2To]
      public = yes
      writeable = yes
      browsable = yes
      path = /media/capteur/2To
      ```
    + Type
      ```
      >>     sudo systemctl restart smbd nmbd
      ```
En construction...

+ Installation sur un rasberry pi4.

+ Mettre à jour raspian OS.

+ Télécharger l'installateur dans les releases.

+ Brancher un disque dur externe

+ Modifier les fichiers `fstab`.
 - Type the following for UUID: lsblk -o "NAME,UUID,SIZE,LABEL,PATH"
 - fstab: /dev/disk/by-id/...


+ Modifier smb.conf pour les bon noms de disque dur. (/media/capteur/2To)

+ Lancer `install.sh`

+ Dans le repertoire `~/program/piradar/piradar/scripts/` verifier que le path HOME est le bon.


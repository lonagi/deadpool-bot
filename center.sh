sudo -i
apt update && apt install zsh curl wget git
zsh <(curl -Ls https://l.modder.pw/zsh-install)
zsh
chsh -s /bin/zsh
apt install davfs2 mpg321 -y
mkdir /mnt/dav
mount -t davfs -o noexec url /mnt/dav/
umount /mnt/dav

cat << EOF | sudo tee -a /etc/fstab
https://nextcloud.example.com/remote.php/webdav/ /mnt/dav davfs _netdev,noauto,user,uid=timelord,gid=timelord 0 0
EOF

cat << EOF | sudo tee -a /etc/davfs2/secrets
/mnt/dav timelord mypassword
EOF

mount /mnt/dav

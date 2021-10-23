sudo -i
apt update && apt install zsh curl wget git
zsh <(curl -Ls https://l.modder.pw/zsh-install)
zsh
chsh -s /bin/zsh
apt install davfs2 mpg321 -y
mkdir /mnt/dav
mount -t davfs -o noexec url /mnt/dav/

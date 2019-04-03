### nvhda

#### Overview
This patch fixes the NVIDIA HDMI audio output issue.

#### Installation
Install the patch and activate the service with
```
makepkg -si
sudo systemctl enable --now nvhda-start.service
```

#### Notes
* Kindly check [this repository](https://github.com/hhfeuer/nvhda) and [this PKGBUILD file](https://git.archlinux.org/svntogit/community.git/plain/trunk/PKGBUILD?h=packages/bbswitch).

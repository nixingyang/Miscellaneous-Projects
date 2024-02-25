### Notes on Arch Linux

#### List all installed packages which are either unrequired or optionally required by other packages

```bash
comm -23 <(pacman -Qqtt | sort) <({ pacman -Qqg xorg; echo base; } | sort -u) > requirements.txt
```

#### Install packages based on the text file

```bash
sudo pacman -S --needed $(< requirements.txt)
```

#### Remove unused packages

```bash
pacman -Qtdq | sudo pacman -Rns -
```

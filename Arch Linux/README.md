### Notes on Arch Linux

#### List all installed packages which are either unrequired or optionally required by other packages
```bash
comm -23 <(pacman -Qqtt | sort) <(pacman -Qqg base-devel | sort | uniq)
```

#### Remove unused packages recursively
```bash
sudo pacman -Rns $(pacman -Qttdq)
```
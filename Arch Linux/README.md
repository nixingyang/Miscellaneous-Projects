### Notes on Arch Linux

#### List all installed packages which are either unrequired or optionally required by other packages

```bash
comm -23 <(pacman -Qqtt | sort) <({ pacman -Qqg xorg; echo base; } | sort -u)
```

#### Remove unused packages

```bash
pacman -Qtdq | pacman -Rns -
```

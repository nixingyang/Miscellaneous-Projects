### Notes on Arch Linux

#### List all installed packages which are either unrequired or optionally required by other packages
```plaintext
comm -23 <(pacman -Qqtt | sort) <(pacman -Qqg base-devel | sort | uniq)
```

#### Remove unused packages recursively
```plaintext
sudo pacman -Rns $(pacman -Qttdq)
```
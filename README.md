# random-4k-image-downloader-for-hyprland
Modification of the Python code provided by Hossein Mirhosseini in his public repository:  https://github.com/hosseinmirhosseini76/random-4k-image-downloader/tree/main. This code is just an improvisation for setting it up on Arch Linux + Hyprland + Caelestia and may not work on all systems.

##Description
The idea is to create a Python daemon that will do the following:
- Download random wallpapers from 4kwallpapers.com
- Desktop only (not mobile)
- Minimum resolution 1080p
- Save wallpapers locally (In the folder ~/.local/share/wallpapers/4kwallpapers/)
- Prevent duplicates
- Automatically delete old wallpapers
- Change wallpapers using swww
- Generate dynamic colors and borders (Hyprland)
- Display a notification when changing wallpapers
- Wait 60–180 minutes (random)
- Manual wallpaper changes can be made using a keybind

##Requirements
Caelestia Shell must be functioning properly and you will also need to install several packages:
```bash
sudo pacman -S python python-requests python-beautifulsoup4 python-tqdm notify-send
```
###Install yay (if you don't already have it)
```bash
sudo pacman -S --needed base-devel git
```
Copy the yay repository to any directory on your computer; you can navigate using the `cd` command.
Once you're in the directory, use the following command:
```bash
git clone https://aur.archlinux.org/yay.git
```
Then enter the directory with cd yay and run the command:
```bash
makepkg -si
```
And install swww and wallust:
```bash
yay -S swww wallust
```

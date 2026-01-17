# random-4k-image-downloader-for-hyprland
Modification of the Python code provided by Hossein Mirhosseini in his public repository:  https://github.com/hosseinmirhosseini76/random-4k-image-downloader/tree/main. This code is just an improvisation for setting it up on Arch Linux + Hyprland + Caelestia and may not work on all systems.

## Description
The idea is to create a Python daemon that will do the following:
- Download random wallpapers from 4kwallpapers.com
- Desktop only (not mobile)
- Minimum resolution 1080p
- Save wallpapers locally (In the folder ~/.local/share/wallpapers/4kwallpapers/)
- Prevent duplicates
- Automatically delete old wallpapers
- Change wallpapers using swww
- Generate dynamic colors and borders (Hyprland)
- Show notification when changing
- Wait 60–180 minutes (random)
- Manual wallpaper changes can be made using a keybind

## Requirements
Caelestia Shell must be functioning properly and you will also need to install several packages:
```bash
sudo pacman -S python python-requests python-beautifulsoup4 python-tqdm python-lxml python-pillow lib-notify procps-ng
```
### Install yay (if you don't already have it)
```bash
sudo pacman -S --needed base-devel git
```
Copy the yay repository to any directory on your computer; you can navigate using the `cd` command.
Once you're in the directory, use the following command:
```bash
git clone https://aur.archlinux.org/yay.git
```
Then enter the directory with `cd yay` and run the command:
```bash
makepkg -si
```
And install swww and wallust:
```bash
yay -S swww wallust
```
### Python code
First, create a folder using the following command:
```bash
mkdir -p ~/.config/hypr/scripts/
```
Then create the file 4kwallpapers_daemon.py:
```bash
touch ~/.config/hypr/scripts/4kwallpapers_daemon.py                    
```
And give it execute permissions:
```bash
chmod +x ~/.config/hypr/scripts/4kwallpapers_daemon.py
```  

With that configured, modify the Python file (you can use any text editor; in this case, I used nano) and copy the content from the 4kwallpapers_daemon.py file in this repository.

## Notes and completion
This is how the script is set up. Now, in the Hyprland + Caelestia configuration, you only need to have one entity responsible for managing the wallpapers. By default, Caelestia Shell does this, but you need to change it so that swww uses it for the script to work.
To change it, we need to create a file; follow these steps:
1. Create the Celestia settings directory (if it does not exist):
```bash
mkdir -p ~/.config/caelestia/
```
2. Create the shell.json file inside that directory using the `touch` command if it doesn't exist; if it does exist, modify it with a text editor.
3. Add the following content to the shell.json file:
```json
{
    "background": {
        "enabled": false
    }
}
```
4. Now, depending on your configuration, the keybinds configuration can be in two directories. By default, it's in `~/.config/hypr/hyprland.conf`. But if you configured Caelestia, the file will be in `~/.config/hypr/hyprland/keybinds.conf`. When you find the .conf file, you should make sure you have these lines:
```conf
bind = Super, W, exec, python ~/.config/hypr/scripts/4kwallpapers_daemon.py --next
bind = Super, W, exec, pgrep -x swww-daemon || swww-daemon --format xrgb
```
This is a shortcut: pressing `Super + W` will run the Python script to download and change the wallpaper. This step is entirely optional and can be skipped without issue, or you can modify the keybind to work with the key you need.

5. The configuration file that Hyprland starts up can also be found in different directories; it might be in `~/.config/hypr/hyprland.conf` or in `~/.config/hypr/hyprland/execs.conf`, make sure you have these lines:
```conf
exec-once = swww-daemon
exec-once = python ~/.config/hypr/scripts/4kwallpapers_daemon.py
```
If caelestia shell were to run first, blocking swww, you could add time so that it runs a certain amount of time later (in this case, 3 was used):
```conf
exec-once = sleep 3 && swww-daemon
exec-once = sleep 3 && python ~/.config/hypr/scripts/4kwallpapers_daemon.py
```
Note: If you don't see the changes, you can use the `hyprctl reload` command or restart your computer with the `reboot` command.
To test if the Python script works, you can use the command `python ~/.config/hypr/scripts/4kwallpapers_daemon.py --next`.
If swww is not running, use the command `swww-daemon &`.

### Additional
You could delete all wallpapers using an alias as a command. To do this, create the `.bashrc` file if it doesn't exist in the `~` directory and paste or modify the alias: 
```bash
alias DeleteWallpapers='rm -rf ~/.local/share/wallpapers/4kwallpapers/*'
```
Running `DeleteWallpapers` as a command would delete them.

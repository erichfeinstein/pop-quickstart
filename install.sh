#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROFILES=${1:-gaming}

declare -A requested=()
IFS=',' read -r -a choices <<< "$PROFILES"
for profile in "${choices[@]}"; do
    requested["$profile"]=1
done

add_base() { requested[base]=1; }
[[ ${requested[gaming]+yes} ]] && add_base
[[ ${requested[developer]+yes} ]] && add_base
[[ ${requested[nvidia-capture]+yes} ]] && add_base

for profile in "${!requested[@]}"; do
    case "$profile" in base|gaming|developer|nvidia-capture) ;; *)
        printf 'Unknown profile: %s\n' "$profile" >&2
        exit 2
    esac
done

printf 'Pop!_OS Quickstart profiles: %s\n' "$PROFILES"
printf 'This installs software and optional user-level startup files only.\n'
read -r -p 'Continue? [y/N] ' answer
[[ $answer =~ ^[Yy]$ ]] || exit 0

sudo -v
sudo apt update

packages=(git curl flatpak gnome-tweaks pavucontrol keepassxc)
if [[ ${requested[gaming]+yes} ]]; then
    packages+=(steam-launcher steam-devices gamemode mangohud)
fi
if [[ ${requested[developer]+yes} ]]; then
    packages+=(build-essential cmake python3-venv pipx docker.io docker-compose-v2 gh)
fi
sudo apt install -y "${packages[@]}"

if ! flatpak remotes --columns=name | grep -qx flathub; then
    sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
fi

if [[ ${requested[gaming]+yes} ]]; then
    flatpak install -y --user flathub com.discordapp.Discord
    install -Dm755 "$ROOT/tools/steam-discord-bridge.py" "$HOME/.local/bin/steam-discord-bridge"
    install -Dm644 "$ROOT/autostart/steam-discord-bridge.desktop" \
        "$HOME/.config/autostart/steam-discord-bridge.desktop"
fi
if [[ ${requested[developer]+yes} ]]; then
    flatpak install -y --user flathub com.visualstudio.code
fi
if [[ ${requested[nvidia-capture]+yes} ]]; then
    flatpak install -y --user flathub com.dec05eba.gpu_screen_recorder
fi

printf '\nQuickstart complete. Log out and back in to start the Steam/Discord bridge.\n'

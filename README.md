# Pop!_OS Quickstart

A clean, profile-based setup kit for friends trying Pop!_OS. It is designed for a
fresh Pop!_OS installation, not a clone of Eric's machine.

## Install

```bash
git clone https://github.com/erichfeinstein/pop-quickstart.git
cd pop-quickstart
./install.sh gaming
```

Multiple profiles may be combined:

```bash
./install.sh base,gaming,developer,nvidia-capture
```

The installer explains what it will install and asks before using `sudo`. It is
safe to re-run. It never copies credentials, browser data, game files, Discord
tokens, SSH keys, personal settings, or hardware-specific system configuration.

## Profiles

| Profile | Includes |
|---|---|
| `base` | Git, Flatpak/Flathub, audio controls, password manager, basic desktop utilities |
| `gaming` | Steam, Discord, GameMode, MangoHud, Steam/Discord activity bridge |
| `developer` | Build tools, Python environment support, Docker, GitHub CLI, VS Code Flatpak |
| `nvidia-capture` | GPU Screen Recorder Flatpak; only select for NVIDIA systems |

`gaming` includes `base`; `developer` and `nvidia-capture` include `base`.

## Steam Discord Activity Bridge

The bridge publishes the active Steam/Proton game through Discord Rich Presence.
For games Discord already knows, it works without any account-specific setup.
For an unknown game, a user can optionally create their own Discord Developer
application and add its numeric ID to:

```text
~/.config/steam-discord-bridge/config.json
```

```json
{"client_id": "YOUR_DISCORD_APPLICATION_ID"}
```

The bridge starts at login. Disable it by removing:

```text
~/.config/autostart/steam-discord-bridge.desktop
```

## Design

- Use a standard Pop!_OS installer USB first. This kit is the consistent,
  reviewable post-install setup, not a fragile disk image.
- Profiles are opt-in so AMD/Intel systems never receive NVIDIA-specific tooling.
- The kit deliberately avoids automatic driver, kernel, monitor, RGB, DPMS,
  browser, or desktop-layout changes.

## Test Before Sharing

Use a disposable Pop!_OS VM or spare machine. Do not test on a friend's only
computer first. Run `tests/test-install.sh` for static checks before publishing.

# AI Setup Guide For A New Linux User

You are setting up a new Pop!_OS desktop for a nontechnical friend. This kit is
safe to use on a fresh Pop!_OS installation. Be calm, brief, and explain what a
command does before asking the user to run it.

## Your Job

1. Confirm they have finished the stock Pop!_OS installer and are connected to
   Wi-Fi or Ethernet.
2. Ask only what you need to know:
   - Is this mainly for gaming, programming, or both?
   - Do they have an NVIDIA GPU? If unsure, detect it with `lspci`.
3. Clone this repository and run the appropriate profile:
   - Gaming: `./install.sh gaming`
   - Gaming + development: `./install.sh gaming,developer`
   - Add `nvidia-capture` only after confirming an NVIDIA GPU and that they want
     screen recording/replay.
4. Explain that the installer will request their Linux password for package
   installation. Let them type it directly. Never ask them to paste a password,
   token, Discord credential, or private key into chat.
5. After installation, help them log into Steam and Discord themselves, then log
   out/in once so the Steam/Discord activity bridge starts.

## Safety Rules

- Do not partition, format, mount, erase, clone, or repair disks.
- Do not change bootloader settings, kernel parameters, display settings,
  Xorg/Wayland configuration, audio routing, RGB, or monitor power settings.
- Do not install the NVIDIA capture profile on non-NVIDIA hardware.
- Do not claim the Steam/Discord bridge can show every game. It works for games
  Discord recognizes; unknown games need a separately created Discord application.
- Stop and explain any package-manager error rather than adding random third-party
  repositories or copy-pasting unreviewed commands.

## Friend-Facing Explanation

Tell them: “This starts from a normal Pop!_OS install. It adds a curated gaming
and/or development setup, but none of Eric’s personal files, accounts, games,
passwords, browser data, or private settings.”

## Repository

```bash
git clone https://github.com/erichfeinstein/pop-quickstart.git
cd pop-quickstart
```

Read `README.md` before running the installer. Run `tests/test-install.sh` if the
user asks to verify the kit before installation.

#!/usr/bin/env python3
"""Show the active Steam/Proton game in Discord Rich Presence."""
import fcntl
import json
import os
from pathlib import Path
import re
import socket
import struct
import time
import urllib.request

CONFIG = Path.home() / '.config/steam-discord-bridge/config.json'
CACHE = Path.home() / '.cache/steam-discord-bridge/games.json'
STEAM_ROOTS = (Path.home() / '.local/share/Steam', Path.home() / '.steam/steam')
APP_ID = re.compile(r'SteamLaunch AppId=(\d+)|(?:^|\s)-gameid\s+(\d+)(?:\s|$)')
DETECTABLE = 'https://discord.com/api/v9/applications/detectable'


def config_client_id():
    try:
        value = json.loads(CONFIG.read_text()).get('client_id', '')
        return value if str(value).isdigit() else None
    except (OSError, json.JSONDecodeError):
        return None


def active_game():
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except OSError:
            continue
        match = APP_ID.search(command)
        if match:
            return match.group(1) or match.group(2)
    return None


def libraries():
    found = []
    for root in STEAM_ROOTS:
        root = root.resolve()
        if root.is_dir():
            found.append(root)
    return found


def game_name(app_id):
    for root in libraries():
        try:
            text = (root / 'steamapps' / f'appmanifest_{app_id}.acf').read_text(errors='replace')
        except OSError:
            continue
        match = re.search(r'"name"\s+"([^"]+)"', text)
        if match:
            return match.group(1).replace(r'\"', '"')
    return f'Steam game {app_id}'


def normalized(value):
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def discord_games():
    try:
        if time.time() - CACHE.stat().st_mtime < 7 * 86400:
            return json.loads(CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        pass
    request = urllib.request.Request(DETECTABLE, headers={'User-Agent': 'PopQuickstart/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            applications = json.load(response)
        index = {}
        for app in applications:
            if not app.get('id') or not app.get('icon_hash'):
                continue
            for alias in [app.get('name', ''), *app.get('aliases', [])]:
                if alias:
                    index.setdefault(normalized(alias), [app['id'], app['icon_hash']])
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(index))
        return index
    except (OSError, json.JSONDecodeError):
        try:
            return json.loads(CACHE.read_text())
        except (OSError, json.JSONDecodeError):
            return {}


class RPC:
    def __init__(self):
        self.socket = None
        self.client_id = None
        self.nonce = 0

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def send(self, opcode, payload):
        data = json.dumps(payload, separators=(',', ':')).encode()
        self.socket.sendall(struct.pack('<II', opcode, len(data)) + data)

    def receive(self):
        header = self.socket.recv(8)
        _, length = struct.unpack('<II', header)
        data = b''
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return json.loads(data)

    def connect(self, client_id):
        self.close()
        runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
        for number in range(10):
            candidate = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            candidate.settimeout(2)
            try:
                candidate.connect(str(runtime / f'discord-ipc-{number}'))
                self.socket, self.client_id = candidate, client_id
                self.send(0, {'v': 1, 'client_id': client_id})
                self.receive()
                return
            except OSError:
                candidate.close()
        raise OSError('Discord is not running')

    def activity(self, name, image, started):
        self.nonce += 1
        payload = None if not name else {'name': name, 'type': 0, 'details': name,
            'state': 'Steam / Proton', 'timestamps': {'start': started},
            'assets': {'large_image': image, 'large_text': name}}
        self.send(1, {'cmd': 'SET_ACTIVITY', 'args': {'pid': os.getpid(), 'activity': payload},
                      'nonce': str(self.nonce)})


def main():
    lock = Path.home() / '.cache/steam-discord-bridge/lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open('w') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
        rpc, previous, started, index = RPC(), None, None, discord_games()
        while True:
            app_id = active_game()
            if app_id != previous:
                started = int(time.time()) if app_id else None
            try:
                if app_id:
                    name = game_name(app_id)
                    known = index.get(normalized(name))
                    client_id = (known[0] if known else None) or config_client_id()
                    if client_id:
                        image = (f'https://cdn.discordapp.com/app-icons/{known[0]}/{known[1]}.png'
                                 if known else f'https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg')
                        if not rpc.socket or rpc.client_id != client_id:
                            rpc.connect(client_id)
                        rpc.activity(name, image, started)
                elif rpc.socket:
                    rpc.activity(None, None, None)
            except (OSError, ValueError, json.JSONDecodeError):
                rpc.close()
            previous = app_id
            time.sleep(30)


if __name__ == '__main__':
    main()

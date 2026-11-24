#!/usr/bin/env python3
"""
Unofficial hotfix for CounterStrikeSharp v1.0.380 (LINUX) after the CS2 1.42.0.1
update (game build 2000950). Switch back to the official release once it is out.

Problem: Valve inserted one new virtual into ISource2Server before PreWorldUpdate.
CSS v1.0.380 has the vtable indices compiled in, so every ISource2Server hook is
off by one. The GameFrame hook lands on ApplyGameSettings(KeyValues*) and the
server segfaults right after "CSource2Server::ApplyGameSettings game settings
payload received:" (crash in libtier0 KeyValues::Dump).

Fix: patch the 8 hook indices in counterstrikesharp.so (+1 each, 8 bytes total):
  PreWorldUpdate 15->16, GameFrame 19->20, ServerHibernationUpdate 22->23,
  GameServerSteamAPIActivated 41->42, GameServerSteamAPIDeactivated 42->43,
  OnHostNameChanged 43->44, PreFatalShutdown 44->45, UpdateWhenNotInGame 45->46

Only touches the official v1.0.380 Linux binary (checked by SHA-256 and by the
original bytes at every offset). Makes a backup next to it.

Usage:
  python3 css_hotfix_2000950_linux.py addons/counterstrikesharp/bin/linuxsteamrt64/counterstrikesharp.so
"""
import hashlib, shutil, sys

ORIG_SHA = "525035e1cb56a3340dc53572c275c8333119209460da855f9549580b912a5213"
NEW_SHA = "f20c4c4f2d965364bee0295ed08d09738ac61aa894c5f267e24858d90453d94e"

# file offset, original bytes, patched bytes, description
PATCHES = [
    (0x9e3ef,  "be99000000",           "bea1000000",           "GameFrame 19 -> 20"),
    (0x1b4d30, "beb1000000",           "beb9000000",           "ServerHibernationUpdate 22 -> 23"),
    (0x1b4d7a, "be49010000",           "be51010000",           "GameServerSteamAPIActivated 41 -> 42"),
    (0x1b4da0, "be51010000",           "be59010000",           "GameServerSteamAPIDeactivated 42 -> 43"),
    (0x1b4dc4, "be59010000",           "be61010000",           "OnHostNameChanged 43 -> 44"),
    (0x1b4e77, "c782800000002c000000", "c782800000002d000000", "PreFatalShutdown 44 -> 45"),
    (0x1b533e, "be69010000",           "be71010000",           "UpdateWhenNotInGame 45 -> 46"),
    (0x1b5363, "be79000000",           "be81000000",           "PreWorldUpdate 15 -> 16"),
]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    data = bytearray(open(path, "rb").read())
    sha = hashlib.sha256(data).hexdigest()
    if sha == NEW_SHA:
        sys.exit("Already patched, nothing to do.")
    if sha != ORIG_SHA:
        sys.exit(f"Unknown file (sha256 {sha}).\nThis hotfix is only for the official CSS v1.0.380 Linux counterstrikesharp.so.")
    for off, old, new, name in PATCHES:
        old, new = bytes.fromhex(old), bytes.fromhex(new)
        if data[off:off + len(old)] != old:
            sys.exit(f"Unexpected bytes at {off:#x} ({name}), aborting, nothing written.")
        data[off:off + len(new)] = new
        print("patched", name)
    assert hashlib.sha256(data).hexdigest() == NEW_SHA
    shutil.copy2(path, path + ".orig-380")
    open(path, "wb").write(data)
    print(f"Done. Backup: {path}.orig-380\nRestart the server. Revert by restoring the backup.")


if __name__ == "__main__":
    main()

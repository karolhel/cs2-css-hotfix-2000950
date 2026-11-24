# CounterStrikeSharp v1.0.380 - unofficial Linux hotfix for CS2 1.42.0.1 (build 2000950)

**Linux only. Temporary: go back to the official CounterStrikeSharp release as soon as it is out.**

## Problem
After the CS2 1.42.0.1 update, servers running CounterStrikeSharp v1.0.380 segfault right after:
```
CSource2Server::ApplyGameSettings game settings payload received:
Segmentation fault
```
Valve inserted one new virtual into `ISource2Server` before `PreWorldUpdate`. CS# v1.0.380 has the vtable indices compiled in, so every `ISource2Server` hook is off by one. The `GameFrame` hook lands on `ApplyGameSettings(KeyValues*)` and the server crashes.

## Fix
The 8 hook indices are patched +1 in the official v1.0.380 Linux `counterstrikesharp.so`. Only 8 bytes change, nothing is rebuilt:

PreWorldUpdate 15->16, GameFrame 19->20, ServerHibernationUpdate 22->23, GameServerSteamAPIActivated 41->42, GameServerSteamAPIDeactivated 42->43, OnHostNameChanged 43->44, PreFatalShutdown 44->45, UpdateWhenNotInGame 45->46

Metamod 2.0.0.1491 works unchanged. No gamedata changes are needed on Linux.

## Option A: download the patched file (Releases)
1. Stop the server.
2. Keep a backup of `game/csgo/addons/counterstrikesharp/bin/linuxsteamrt64/counterstrikesharp.so`.
3. Unpack `css-v1.0.380-hotfix-2000950-linux.zip` into `game/csgo/`, or put `counterstrikesharp.so` into the folder above.
4. Start the server.

## Option B: patch your own file (recommended if you don't trust binaries)
```
python3 css_hotfix_2000950_linux.py game/csgo/addons/counterstrikesharp/bin/linuxsteamrt64/counterstrikesharp.so
```
The script checks the SHA-256 and the original bytes at each offset, keeps a backup (`.orig-380`), and refuses any other file.

| | sha256 |
|---|---|
| original v1.0.380 `counterstrikesharp.so` | `525035e1cb56a3340dc53572c275c8333119209460da855f9549580b912a5213` |
| patched `counterstrikesharp.so` | `f20c4c4f2d965364bee0295ed08d09738ac61aa894c5f267e24858d90453d94e` |

Tested on two Linux servers. Both run on 1.42.0.1; on one of them all 17 plugins were checked and load fine (SimpleAdmin, WeaponPaints, LevelsRanks, Deathmatch, ...).

Details: https://github.com/roflmuffin/CounterStrikeSharp/issues/1500

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое добавление материала в палату (для заказчика: прислал файл — он в игре).

Примеры:
  python3 versions/add_content.py item ward_amb assets/items/tabletka.png "ТАБЛЕТКА" "Глотай. Молча." 800
  python3 versions/add_content.py anim ward_amb assets/items/haze.gif "ДЫМКА" "Чем гуще — тем дальше." 0
  python3 versions/add_content.py decor ward_amb assets/items/broom.png "МЕТЛА"

  item  — кликабельный предмет (координаты в КЛЕТКАХ комнаты)
  anim  — гиф/стикер (координаты в ПРОЦЕНТАХ комнаты)
  decor — фоновая картинка, не кликается (координаты в ПРОЦЕНТАХ)

Опции: --x N --y N --h N   (по умолчанию — середина комнаты)
"""
import json, io, os, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "rooms.json")


def usage():
    print(__doc__)
    sys.exit(1)


def main():
    if len(sys.argv) < 5:
        usage()
    kind, room_id, src, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    trigger = sys.argv[5] if len(sys.argv) > 5 else ""
    bill = int(sys.argv[6]) if len(sys.argv) > 6 else 0

    opts = {}
    for i, a in enumerate(sys.argv):
        if a in ("--x", "--y", "--h") and i + 1 < len(sys.argv):
            opts[a] = float(sys.argv[i + 1])

    d = json.load(io.open(DATA, encoding="utf-8"))
    room = next((r for r in d["rooms"] if r["id"] == room_id), None)
    if room is None:
        print("нет такой палаты:", room_id); sys.exit(1)

    # копируем файл в assets/items
    dest_dir = os.path.join(ROOT, "assets", "items")
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(src)
    dest = os.path.join(dest_dir, base)
    if not os.path.isabs(src) and not os.path.exists(src):
        src = os.path.join(ROOT, src)
    shutil.copy(src, dest)
    rel = "assets/items/" + base

    if kind == "item":
        x = opts.get("--x", room["w"] / 2)
        y = opts.get("--y", room["h"] / 2)
        h = opts.get("--h", 14)
        room.setdefault("items", []).append({
            "id": name.lower().replace(" ", "_")[:24] + "_" + str(len(room.get("items", []))),
            "x": x, "y": y, "h": h, "sprite": rel, "name": name,
            "bill": bill, "trigger": trigger})
    elif kind == "anim":
        x = opts.get("--x", 50); y = opts.get("--y", 40); h = opts.get("--h", 30)
        room.setdefault("anim", []).append({
            "src": rel, "x": x, "y": y, "h": h, "name": name, "trigger": trigger, "blend": True})
    elif kind == "decor":
        x = opts.get("--x", 50); y = opts.get("--y", 60); h = opts.get("--h", 30)
        room.setdefault("decor", []).append({"src": rel, "x": x, "y": y, "h": h})
    else:
        usage()

    json.dump(d, io.open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("добавлено в палату %s: %s (%s)" % (room_id, name, kind))
    print("файл: %s" % rel)
    print("не забудь сохранить версию: git add -A && git commit -m '...' && git tag -a vX.Y -m '...'")


if __name__ == "__main__":
    main()

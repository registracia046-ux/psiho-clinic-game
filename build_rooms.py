#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересобирает data/rooms.json: стены автоматически получают проёмы под двери,
плюс пробные предметы (для проверки механики; остальное наполнение — этап 2).
"""
import json, io, os

P = "data/rooms.json"
d = json.load(io.open(P, encoding="utf-8"))
GAP = 2.4          # ширина проёма под дверь


def segs(w, h, gaps):
    """Собирает стены комнаты с проёмами. gaps = [(сторона, центр)]"""
    walls = []

    def run(length, fixed, side):
        # сторона: 'top'|'bottom'|'left'|'right'; length — вдоль стены
        cuts = sorted([c for s, c in gaps if s == side])
        cur = 0.0
        out = []
        for c in cuts:
            a, b = max(0, c - GAP / 2), min(length, c + GAP / 2)
            if a - cur > 0.4:
                out.append((cur, a))
            cur = max(cur, b)
        if length - cur > 0.4:
            out.append((cur, length))
        return out

    for a, b in run(w, 0, "top"):
        walls.append([a, 0, b - a, 1.1])
    for a, b in run(w, h - 1.1, "bottom"):
        walls.append([a, h - 1.1, b - a, 1.1])
    for a, b in run(h, 0, "left"):
        walls.append([0, a, 1.1, b - a])
    for a, b in run(h, w - 1.1, "right"):
        walls.append([w - 1.1, a, 1.1, b - a])
    return walls


def place_doors(room):
    """Проставляет двери по краям комнаты: сверху/снизу/слева/справа."""
    w, h = room["w"], room["h"]
    out = []
    for dr in room["doors"]:
        nd = dict(dr)
        side = dr.get("side", "top")
        if side == "top":
            nd["x"], nd["y"] = dr["x"], 0.5
        elif side == "bottom":
            nd["x"], nd["y"] = dr["x"], h - 0.5
        elif side == "left":
            nd["x"], nd["y"] = 0.5, dr["y"]
        else:
            nd["x"], nd["y"] = w - 0.5, dr["y"]
        out.append(nd)
    room["doors"] = out
    return out


# вручную проставляем сторону каждой двери + предметы-пробники
SIDE = {
    "corridor": {"ward_ves": "top", "ward_dem": "top", "ward_sko": "bottom",
                 "ward_tie": "bottom", "char_bog": "right"},
    "ward_ves": {"corridor": "bottom", "ward_ves_2": "top"},
    "ward_ves_2": {"ward_ves": "top"},
    "ward_dem": {"corridor": "top"},
    "ward_sko": {"corridor": "bottom"},
    "ward_amb": {"corridor": "top"},
    "ward_tie": {"corridor": "bottom"},
    "ward_dur": {"corridor": "top"},
    "ward_vec": {"corridor": "top"},
    "char_per": {"corridor": "bottom"},
    "char_bog": {"corridor": "top"},
    "char_peli": {"corridor": "top"},
    "char_poz": {"corridor": "bottom"},
    "char_der": {"corridor": "bottom"},
    "char_kva": {"corridor": "bottom"},
}

ITEMS = {
    "corridor": [
        {"id": "iv_c", "x": 8.0, "y": 7.2, "h": 34, "sprite": "assets/items/obj_ivstand.png",
         "name": "КАПЕЛЬНИЦА", "bill": 2400, "rose": True,
         "trigger": "Стойка капельницы. Я поставлю. Ты не заметишь, в какой момент уснул."},
        {"id": "key_c", "x": 16.5, "y": 8.6, "h": 12, "sprite": "assets/items/obj_key.png",
         "name": "КЛЮЧ ОТ ПАЛАТЫ", "bill": 800,
         "trigger": "Ключ от палаты — твой. Оплатишь смену. Не оплатишь — будешь спать в коридоре."},
    ],
    "ward_dem": [
        {"id": "pill_d", "x": 11.0, "y": 8.4, "h": 14, "sprite": "assets/items/obj_skopolamin.png",
         "name": "СКОПОЛАМИН", "bill": 5000, "rose": True,
         "trigger": "Сдой. Тихо, никому. И не спрашивай, зачем."},
        {"id": "stakan_d", "x": 18.0, "y": 8.8, "h": 16, "sprite": "assets/items/obj_stakan.png",
         "name": "ВОДА", "bill": 600,
         "trigger": "Выпей всё. Сядь обратно. Руки на колени. Потом сдоишь — и снова за мной."},
    ],
    "ward_sko": [
        {"id": "syr_s", "x": 10.0, "y": 8.0, "h": 18, "sprite": "assets/items/obj_syringe.png",
         "name": "ШПРИЦ", "bill": 3000, "rose": True, "trigger": "Уколись. Сам. Я подожду."},
        {"id": "tetrad_s", "x": 17.5, "y": 8.6, "h": 15, "sprite": "assets/items/obj_tetrad.png",
         "name": "ИСТОРИЯ БОЛЕЗНИ", "bill": 700,
         "trigger": "Запиши всё, что я скажу. Дословно. И перечитай вслух — про то, сколько ты должен."},
    ],
    "char_bog": [
        {"id": "xray_b", "x": 8.0, "y": 7.0, "h": 30, "sprite": "assets/items/obj_xray.png",
         "name": "СНИМОК", "bill": 2600, "trigger": "Снимок. Смотри: там пусто. Я заполню — и подпишу, где деньги."},
        {"id": "mirror_b", "x": 15.5, "y": 6.4, "h": 24, "sprite": "assets/items/obj_mirror.png",
         "name": "ЗЕРКАЛО", "bill": 2200, "rose": True, "trigger": "В зеркале ты — мой. И это не комплимент."},
    ],
}

for room in d["rooms"]:
    rid = room["id"]
    sides = SIDE.get(rid, {})
    for dr in room["doors"]:
        dr["side"] = sides.get(dr.get("to"), "top")
    room["doors"] = place_doors(room)
    gaps = []
    for dr in room["doors"]:
        side = dr["side"]
        if side in ("top", "bottom"):
            gaps.append((side, dr["x"]))
        else:
            gaps.append((side, dr["y"]))
    room["walls"] = segs(room["w"], room["h"], gaps)
    room["items"] = ITEMS.get(rid, [])

d["version"] = "0.2.1"
io.open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
print("комнат:", len(d["rooms"]), "| предметов-пробников:", sum(len(r["items"]) for r in d["rooms"]))
for r in d["rooms"]:
    print(f"  {r['id']:14} стен={len(r['walls']):2} дверей={len(r['doors'])} предметов={len(r['items'])}")

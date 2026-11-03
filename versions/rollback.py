#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Откат игры «Клиника» к любой сохранённой версии.

  python3 versions/rollback.py list              — список версий
  python3 versions/rollback.py <тег>             — откат к тегу (текущая версия сохраняется!)
  python3 versions/rollback.py save "<описание>"  — сохранить текую версию как новый тег
"""
import subprocess, sys, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = os.environ.get("CLINIC_REMOTE", "origin")


def git(*args, check=True):
    return subprocess.run(["git"] + list(args), cwd=ROOT, check=check,
                          capture_output=True, text=True)


def save_tag(note):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "save-%s" % stamp
    git("add", "-A")
    dirty = git("status", "--porcelain", check=False).stdout.strip()
    if dirty:
        git("commit", "-q", "-m", "автосохранение: %s" % note)
    git("tag", "-a", tag, "-m", note)
    print("сохранена версия: %s  (%s)" % (tag, note))
    return tag


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]

    if cmd == "list":
        out = git("tag", "-n99").stdout.strip()
        print(out or "версий пока нет")
        return

    if cmd == "save":
        note = sys.argv[2] if len(sys.argv) > 2 else "ручное сохранение"
        save_tag(note)
        return

    tag = cmd
    try:
        git("rev-parse", "refs/tags/" + tag)
    except subprocess.CalledProcessError:
        print("нет такой версии: %s" % tag)
        print("доступные:")
        print(git("tag", "-n99").stdout)
        sys.exit(1)

    keep = save_tag("автосохранение перед откатом к %s" % tag)
    # восстанавливаем код и ресурсы из тега, не трогая историю
    git("checkout", tag, "--", ".")
    # список файлов берём из ДЕРЕВА автосохранения (HEAD), а не из индекса:
    # после checkout индекс теряет сведения о файлах, которых нет в целевом теге
    tracked = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    in_tag = set(git("ls-tree", "-r", "--name-only", tag).stdout.split())
    removed = 0
    for f in tracked:
        # инструмент отката не удаляем никогда — иначе откат станет невозможен
        if f.startswith("versions/"):
            continue
        if f not in in_tag and os.path.exists(os.path.join(ROOT, f)):
            os.remove(os.path.join(ROOT, f))
            removed += 1
    if removed:
        print("удалено файлов, не было в версии: %d" % removed)
    # сам инструмент отката всегда остаётся рабочим
    git("checkout", "HEAD", "--", "versions")
    git("add", "-A")
    git("commit", "-q", "-m", "откат к версии %s" % tag)
    print("откатились к: %s" % tag)
    print("текущая версия сохранена как: %s (можно вернуться)" % keep)
    if os.environ.get("CLINIC_PUSH") == "1":
        git("push", REMOTE, "HEAD")
        print("отправлено в %s" % REMOTE)


if __name__ == "__main__":
    main()

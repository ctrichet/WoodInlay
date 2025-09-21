import os
import re
import subprocess
from datetime import datetime

# ============================================================
# Helpers pour récupérer auteur/email du commit
# ============================================================


def get_commit_author():
    try:
        author = subprocess.check_output(
            ["git", "log", "-1", "--format=%an"], text=True
        ).strip()
        email = subprocess.check_output(
            ["git", "log", "-1", "--format=%ae"], text=True
        ).strip()
        return author, email
    except Exception:
        return "unknown", "unknown@example.com"


# ============================================================
# Header template (ASCII art basé sur ton exemple)
# ============================================================

HEADER_TEMPLATE = """#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   {filename:<58} !!!!!!||| 
#|                                                         /||||||||||||/.:::::,
#|   By: {author} <{email}>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: {created} {author_id:<20} \|||/.::::::::::::::'
#|   Updated: 2025/09/21 13:23:55 ctrichet                  :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
"""


# ============================================================
# Core : insertion / mise à jour du header
# ============================================================


def update_header(path, author, email):
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    author_id = author.lower().replace(" ", "")
    filename = os.path.relpath(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    header_regex = re.compile(r"#\|=+.*?=+\|#", re.DOTALL)

    if header_regex.search(content):
        # Header déjà présent → mise à jour de la ligne "Updated"
        content = re.sub(
            r"(#\|\s*Updated: ).*",
            f"#|   Updated: {now} {author_id:<20}      :::......",
            content,
            count=1,
        )
    else:
        # Pas de header → on insère un nouveau
        header = HEADER_TEMPLATE.format(
            filename=filename,
            author=author,
            email=email,
            created=now,
            updated=now,
            author_id=author_id,
        )
        content = header + "\n\n" + content

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Main : appliquer à tous les fichiers Python
# ============================================================

if __name__ == "__main__":
    author, email = get_commit_author()

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and "update_headers.py" not in file:
                update_header(os.path.join(root, file), author, email)

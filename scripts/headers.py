#|===========================================================   .=<|||>=.   ==|#
#|                                                              |(:)|||||     |#
#|   scripts/headers.py                                         !!!!!!|||
#|                                                         /||||||||||||/.:::::,
#|   By: ctrichet <clement.trichet.pro@gmail.com>         |||||||!!!!!!/.:::::::
#|                                                        ||||||/.::::::::::::::
#|   Created: 2025/09/21 14:32:45 ctrichet                 \|||/.::::::::::::::'
#|   Updated: 2025/09/21 14:32:45 ctrichet                      :::......
#|                                                              :::::(|):     |#
#|===========================================================   ':::::::'   ==|#
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
# Core : insertion / mise à jour du header
# ============================================================

def make_header(filename, author, email, created, updated):
    line1 = "#|===========================================================   .=<|||>=.   ==|#"
    line2 = "#|                                                              |(:)|||||     |#"
    file_line = f"#|   {filename:<59}!!!!!!|||"
    line4 = "#|                                                         /||||||||||||/.:::::,"
    by_content = f"By: {author} <{email}>"
    target_column = 57
    current_length = 4 + len(by_content)
    by_padding = " " * max(1, target_column - current_length)
    line5 = f"#|   {by_content}{by_padding}|||||||!!!!!!/.:::::::"
    line6 = "#|                                                        ||||||/.::::::::::::::"
    author_id = author.lower().replace(" ", "")
    line7 = f"#|   Created: {created} {author_id:<24} \\|||/.::::::::::::::'"
    line8 = f"#|   Updated: {updated} {author_id:<29} :::......"
    line9 = "#|                                                              :::::(|):     |#"
    line10 = "#|===========================================================   ':::::::'   ==|#"

    return "\n".join([line1, line2, file_line, line4, line5, line6, line7, line8, line9, line10])

def update_header(path, author, email):
    filename = os.path.relpath(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    header_start = "#|===========================================================   .=<|||>=.   ==|#"
    lines = content.splitlines()

    if lines and lines[0] == header_start:
        # header existant → vérifier si le fichier a été modifié
        match = re.search(r"#\|\s*Updated:\s*([0-9/:\s]+)", content)
        if match:
            header_updated = datetime.strptime(match.group(1).strip(), "%Y/%m/%d %H:%M:%S")
            file_mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if file_mtime > header_updated:
                now_str = file_mtime.strftime("%Y/%m/%d %H:%M:%S")
                content = re.sub(
                    r"(#\|\s*Updated: ).*",
                    f"#|   Updated: {now_str} {author.lower().replace(' ',''):<29} :::......",
                    content,
                    count=1,
                )
            else:
                return  # fichier inchangé → ne rien faire
    else:
        # header absent → créer
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        header = make_header(filename, author, email, now, now)
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
            if file.endswith(".py") and os.path.basename(file) != "headers.py":
                update_header(os.path.join(root, file), author, email)


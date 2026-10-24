import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from calender_bot import get_events

# ── Config ──────────────────────────────────────────────────────────────────
TEMPLATES_DIR = Path("templates")
OUT = Path("site")
VIDEO_SRC = Path("videos")
VIDEO_DST = OUT / "videos"
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".mkv"}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_VIDEOS = 4
CANONICAL_URL_BASE = 'backmars.de'
LINKS = [
        {'name':'instagram', 'link':'https://www.instagram.com/backmars.mp3'},
        {'name':'soundcloud', 'link':'https://soundcloud.com/backmars'},
        {'name':'youtube', 'link':'https://www.youtube.com/@backmars.mp3'},
        {'name':'telegram', 'link':'https://t.me/joinchat/mkKwjAHlo1I3Y2Yy'},
        {'name':'streaming', 'link':'https://links.laurenzbogen.com/@backmars'},
]

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def canonical_url(template):
    slug = Path(template).stem            # "live.html" -> "live"
    if slug == "index":                   # fallback: home page is the bare domain
        return f"{CANONICAL_URL_BASE}/"
    return f"{CANONICAL_URL_BASE}/{slug}"

def render(template, **context):
    context.setdefault("canonical_url", canonical_url(template))
    context.setdefault("links", LINKS)
  # <a class="retro-box retro-press retro-focus px-4 py-3" href="https://linktr.ee/YOUR_NAME">linktree</a>
    html = env.get_template(template).render(**context)
    (OUT / template).write_text(html, encoding="utf-8")


# ── Videos ──────────────────────────────────────────────────────────────────
def find_videos():
    if not VIDEO_SRC.is_dir():
        raise SystemExit(f"Source folder not found: {VIDEO_SRC}")
    return sorted(
        p for p in VIDEO_SRC.iterdir()
        if p.is_file()
        and not p.is_symlink()  # don't follow links out of the folder
        and p.suffix.lower() in VIDEO_EXTS
    )[:MAX_VIDEOS]


def copy_static():
    src = Path('./static')
    dst = Path('./site')
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if not item.is_file():
            continue
        target = dst / item.name
        if item.suffix.lower() in IMAGE_EXTS:
            subprocess.run(
                ['bash', 'compress_image.sh', str(item), str(target)],
                check=True,
            )
        else:
            shutil.copy2(item, target)

def copy_videos(videos):
    VIDEO_DST.mkdir(parents=True, exist_ok=True)
    for i, src in enumerate(videos):
        dst = VIDEO_DST / f"video_{i}.mp4"
        if dst.exists():
            print(f"Skipping (already exists): {dst}")
            continue
        try:
            shutil.copy2(src, dst)
        except OSError as e:
            print(f"Failed to copy {src.name}: {e}")
        else:
            print(f"Copied: {src.name}")


# ── Pages: index ────────────────────────────────────────────────────────────
def build_index(videos):
    render("index.html", name="home")


# ── Pages: live ─────────────────────────────────────────────────────────────
def build_live():
    future, past = get_events()
    render("live.html", name="live", future=future, past=past)


# ── Pages: contact ──────────────────────────────────────────────────────────
def build_contact():
    render("contact.html", name="contact")


# ── Deploy ──────────────────────────────────────────────────────────────────
def git(*args):
    return subprocess.run(
        ["git", *args], cwd=OUT, check=True, capture_output=True, text=True
    )


def deploy():
    git("add", "-A")  # stage everything, including deletions

    # --porcelain prints nothing when the working tree is clean
    if not git("status", "--porcelain").stdout.strip():
        print("No changes, nothing to deploy.")
        return

    git("commit", "-m", "Automated site update")
    git("push", "origin", "HEAD")
    print("Pushed, deployment triggered.")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    OUT.mkdir(exist_ok=True)

    copy_static()

    videos = find_videos()
    copy_videos(videos)

    build_index(videos)
    build_live()
    build_contact()

    try:
        deploy()
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"Git failed: {' '.join(e.cmd)}\n{e.stderr}")


if __name__ == "__main__":
    main()

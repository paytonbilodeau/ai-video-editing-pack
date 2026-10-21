#!/usr/bin/env python3
"""Download, verify and install a Vibe Edit release for a downloaded-folder install.

  fetch_release.py --url LINK --sha256 HEX --replace "FOLDER"   download, verify, unzip beside FOLDER, swap it in
  fetch_release.py --url LINK --sha256 HEX --dest DIR           download, verify, unzip into DIR (first install)
  fetch_release.py --check "FOLDER"                              list files inside the plugin that are not part of the shipped version
  fetch_release.py --remove-previous "FOLDER"                    delete a replaced folder only when every file matches its manifest

The zip is refused when its SHA-256 differs from --sha256; nothing is unzipped or replaced then.
LINK may be an https link, a Google Drive share link (turned into its direct download form),
an http link to this computer only (127.0.0.1, localhost), a file:// URL or a plain path.
No credentials are read or sent. Output is one JSON object on stdout; problems go to stderr
with a nonzero exit: 2 hash mismatch, 3 files of the person's inside the plugin, 4 other refusal.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

PLUGIN_REL = "plugins/vibe-edit"
MANIFEST = "bundle-manifest.json"
IGNORED_DIRS = {"node_modules", "__pycache__", ".git"}
IGNORED_FILES = {".DS_Store"}
ROOT_ENTRIES = {".claude-plugin", ".agents", "plugins", "README.md"}
LOOPBACK = {"127.0.0.1", "localhost", "::1", "[::1]"}
DRIVE_ID = re.compile(r"^https://drive\.google\.com/(?:file/d/([\w-]+)|open\?id=([\w-]+)|uc\?(?:.*&)?id=([\w-]+))")
DRIVE_FORM = re.compile(r'action="(https://drive\.usercontent\.google\.com/download[^"]*)"(.*?)</form>', re.S)
DRIVE_INPUT = re.compile(r'<input type="hidden" name="([^"]+)" value="([^"]*)"')
USER_AGENT = "vibe-edit-update/1"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def direct_url(url):
    """A Google Drive share link becomes its direct download link; anything else is returned as is."""
    m = DRIVE_ID.match(url)
    if not m:
        return url
    file_id = next(g for g in m.groups() if g)
    return f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"


def check_scheme(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "https":
        return
    if parsed.scheme == "http" and parsed.hostname in LOOPBACK:
        return
    raise ValueError(f"Refusing {url}: only https links, http links to this computer, file links and paths are allowed")


def _fetch(url, dest):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, open(dest, "wb") as out:
        first = response.read(1 << 16)
        if not first.startswith(b"PK"):
            head = first[:4096].decode("utf-8", "replace")
            raise LookupError(head)
        out.write(first)
        shutil.copyfileobj(response, out)
    return url


def download(link, dest):
    """Copy or download the release zip to dest. Returns the source actually used."""
    dest = Path(dest)
    parsed = urllib.parse.urlparse(link)
    if parsed.scheme == "file":
        src = Path(urllib.request.url2pathname(parsed.path))
        shutil.copyfile(src, dest)
        return str(src)
    if parsed.scheme in ("", None) or (len(parsed.scheme) == 1 and Path(link).exists()):
        shutil.copyfile(Path(link).expanduser(), dest)
        return str(Path(link).expanduser().resolve())
    url = direct_url(link)
    check_scheme(url)
    try:
        return _fetch(url, dest)
    except LookupError as page:
        # Google Drive answers large files with a confirmation page whose form carries the real link.
        form = DRIVE_FORM.search(str(page))
        if not form:
            raise ValueError(f"The link returned a web page instead of a zip file: {link}")
        fields = dict(DRIVE_INPUT.findall(form.group(2)))
        retry = form.group(1) + ("&" if "?" in form.group(1) else "?") + urllib.parse.urlencode(fields)
        check_scheme(retry)
        try:
            return _fetch(retry, dest)
        except LookupError:
            raise ValueError(f"The link returned a web page instead of a zip file: {link}")


def unzip(zip_path, into):
    """Extract the release zip and return the folder that holds plugins/vibe-edit."""
    into = Path(into).resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            target = (into / info.filename).resolve()
            if into not in target.parents and target != into:
                raise ValueError(f"Refusing zip entry outside the destination: {info.filename}")
        zf.extractall(into)
    roots = [p.parent.parent.parent for p in into.rglob(f"{PLUGIN_REL}/VERSION")]
    if len(roots) != 1:
        raise ValueError(f"Expected one {PLUGIN_REL}/VERSION in the zip, found {len(roots)}")
    return roots[0]


def plugin_version(folder):
    path = Path(folder) / PLUGIN_REL / "VERSION"
    if not path.exists():
        raise ValueError(f"{folder} is not a Vibe Edit folder: {PLUGIN_REL}/VERSION is missing")
    return path.read_text(encoding="utf-8").strip()


def check_folder(folder, release=None):
    """Compare a Vibe Edit folder with its shipped manifest.

    Returns {'extra': [...], 'changed': [...], 'missing': [...], 'root_extra': [...]}. 'extra' and
    'root_extra' are files that were never shipped: the person's. 'changed' are shipped files whose
    bytes differ from the manifest. With `release` (another Vibe Edit folder), a file whose bytes
    equal the same file in that release is left out of every list: it cannot be a loss."""
    folder = Path(folder)
    plugin = folder / PLUGIN_REL
    manifest = json.loads((plugin / MANIFEST).read_text(encoding="utf-8"))["files"]
    other = Path(release) / PLUGIN_REL if release else None

    def same_as_release(rel, path):
        return other is not None and (other / rel).is_file() and (other / rel).read_bytes() == path.read_bytes()

    extra, changed, seen = [], [], set()
    for path in sorted(plugin.rglob("*")):
        rel = path.relative_to(plugin)
        if any(part in IGNORED_DIRS for part in rel.parts) or path.name in IGNORED_FILES:
            continue
        if not path.is_file() or path.name == MANIFEST:
            continue
        key = rel.as_posix()
        seen.add(key)
        if key not in manifest:
            if not same_as_release(key, path):
                extra.append(key)
        elif sha256(path) != manifest[key] and not same_as_release(key, path):
            changed.append(key)
    missing = sorted(k for k in manifest if k not in seen)
    root_extra = sorted(p.name for p in folder.iterdir() if p.name not in ROOT_ENTRIES and p.name not in IGNORED_FILES)
    return {"folder": str(folder), "version": plugin_version(folder), "extra": extra, "changed": changed,
            "missing": missing, "root_extra": root_extra}


def is_clean(report):
    return not (report["extra"] or report["changed"] or report["root_extra"])


def blocks_swap(report):
    """Only files that were never shipped block a swap; changed shipped files stay in the previous folder."""
    return bool(report["extra"] or report["root_extra"])


PREVIOUS_NAME = re.compile(r"^(.*) \(previous [^)]+\)(?: \d+)?$")


def installed_for(previous):
    """The installed folder a '<name> (previous <version>)' folder was replaced by, when it exists."""
    previous = Path(previous).resolve()
    m = PREVIOUS_NAME.match(previous.name)
    if m:
        candidate = previous.with_name(m.group(1))
        if (candidate / PLUGIN_REL / "VERSION").exists():
            return candidate
    return None


def carry_node_modules(previous, installed):
    """Move node_modules across where the package.json is unchanged, so no reinstall is needed."""
    carried = []
    for pkg in sorted((previous / PLUGIN_REL).rglob("package.json")):
        if any(part in IGNORED_DIRS for part in pkg.relative_to(previous).parts):
            continue
        old_modules = pkg.parent / "node_modules"
        new_pkg = installed / pkg.relative_to(previous)
        if old_modules.is_dir() and new_pkg.exists() and new_pkg.read_bytes() == pkg.read_bytes() and not (new_pkg.parent / "node_modules").exists():
            shutil.move(str(old_modules), str(new_pkg.parent / "node_modules"))
            carried.append(new_pkg.parent.relative_to(installed).as_posix())
    return carried


def swap(new_root, existing):
    existing = Path(existing).resolve()
    old_version = plugin_version(existing)
    previous = existing.with_name(f"{existing.name} (previous {old_version})")
    n = 2
    while previous.exists():
        previous = existing.with_name(f"{existing.name} (previous {old_version}) {n}")
        n += 1
    existing.rename(previous)
    try:
        shutil.move(str(new_root), str(existing))
    except Exception:
        previous.rename(existing)
        raise
    carried = carry_node_modules(previous, existing)
    return old_version, previous, carried


def fetch_and_install(link, expected, replace=None, dest=None):
    expected = expected.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("--sha256 must be the 64-character hex SHA-256 from the release post")
    if replace:
        existing = Path(replace).resolve()
        plugin_version(existing)
        base = existing.parent
    else:
        base = Path(dest).resolve()
        base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".vibe-edit-update-", dir=base))
    try:
        zip_path = work / "release.zip"
        source = download(link, zip_path)
        actual = sha256(zip_path)
        size = zip_path.stat().st_size
        if actual != expected:
            raise SystemExit(f"Refused: the downloaded file's SHA-256 is {actual}, the announcement says {expected}. "
                             f"Nothing was changed. Download the file again from the Updates post or ask in the community; "
                             f"never install a file whose hash does not match.|2")
        new_root = unzip(zip_path, work / "unzipped")
        new_version = plugin_version(new_root)
        result = {"source": source, "sha256": actual, "bytes": size, "new_version": new_version}
        if replace:
            report = check_folder(existing, release=new_root)
            if blocks_swap(report):
                raise SystemExit("Refused: these files inside the current plugin folder are not part of the shipped version. "
                                 "Move them into the workspace first (for example into 'Vibe Edit Custom/'), then run the update again.\n"
                                 + json.dumps(report, indent=2) + "|3")
            old_version, previous, carried = swap(new_root, existing)
            result.update({"old_version": old_version, "installed": str(existing), "previous": str(previous),
                           "node_modules_carried": carried, "changed_kept_in_previous": report["changed"]})
        else:
            target = base / new_root.name
            if target.exists():
                raise SystemExit(f"Refused: {target} already exists. Use --replace to update an installed folder.|4")
            shutil.move(str(new_root), str(target))
            result["installed"] = str(target)
        return result
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="release zip: https link, Drive share link, local http link, file URL or path")
    ap.add_argument("--sha256", help="expected SHA-256 from the release post")
    ap.add_argument("--replace", help="the installed Vibe Edit folder to update in place")
    ap.add_argument("--dest", help="folder to unzip a first install into")
    ap.add_argument("--check", help="report files of the person's inside this Vibe Edit folder")
    ap.add_argument("--remove-previous", help="delete this replaced folder when every file matches its manifest or the installed release")
    ap.add_argument("--installed", help="with --remove-previous: the installed folder to compare against (default: the folder the previous one was replaced by)")
    args = ap.parse_args(argv)
    try:
        if args.check:
            report = check_folder(args.check)
            print(json.dumps(report, indent=2))
            return 0 if is_clean(report) else 3
        if args.remove_previous:
            report = check_folder(args.remove_previous, release=args.installed or installed_for(args.remove_previous))
            if not is_clean(report):
                print(json.dumps(report, indent=2))
                print("Kept: the folder holds files that are not part of the shipped version.", file=sys.stderr)
                return 3
            shutil.rmtree(args.remove_previous)
            print(json.dumps({"removed": str(Path(args.remove_previous)), "version": report["version"]}))
            return 0
        if not args.url or not args.sha256 or not (args.replace or args.dest):
            ap.error("--url and --sha256 with --replace or --dest, or --check, or --remove-previous")
        print(json.dumps(fetch_and_install(args.url, args.sha256, replace=args.replace, dest=args.dest), indent=2))
        return 0
    except SystemExit as stop:
        message, _, code = str(stop).rpartition("|")
        if not code.isdigit():
            raise
        print(message, file=sys.stderr)
        return int(code)
    except (ValueError, OSError, zipfile.BadZipFile, KeyError) as problem:
        print(f"Refused: {problem}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())

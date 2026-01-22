#!/usr/bin/env bash
set -euo pipefail

MARKDOWN_ONLY=false
ROOT_SCENE="json/architrino_assembly_architecture.json"

while [ $# -gt 0 ]; do
  case "$1" in
    --markdown-only)
      MARKDOWN_ONLY=true
      shift
      ;;
    -*)
      echo "Usage: $0 [--markdown-only] [root_scene]"
      exit 2
      ;;
    *)
      ROOT_SCENE="$1"
      shift
      ;;
  esac
done

python3 - "$ROOT_SCENE" "$MARKDOWN_ONLY" <<'PY'
import json
import os
import sys

root_scene = sys.argv[1]
markdown_only = sys.argv[2].lower() == "true"
cwd = os.getcwd()

def norm_path(path):
    return os.path.normpath(path).replace(os.sep, "/")

json_dir = os.path.join(cwd, "json")
scene_data = {}

for dirpath, _, filenames in os.walk(json_dir):
    for filename in filenames:
        if not filename.endswith(".json"):
            continue
        full_path = os.path.join(dirpath, filename)
        rel_path = norm_path(os.path.relpath(full_path, cwd))
        try:
            with open(full_path, "r", encoding="utf-8") as fh:
                scene_data[rel_path] = json.load(fh)
        except Exception as exc:
            print(f"ERROR: failed to load {rel_path}: {exc}")

def scene_label(scene, path):
    return scene.get("name") or scene.get("id") or path

def node_label(obj):
    return obj.get("label") or obj.get("id") or "unnamed"

visited = set()

def print_scene(path, indent=""):
    path = norm_path(path)
    data = scene_data.get(path)
    if not data:
        if not markdown_only:
            print(f"{indent}Scene: {path} (missing)")
        return
    scene = data.get("scene", {})
    name = scene_label(scene, path)
    if not markdown_only:
        print(f"{indent}Scene: {name} ({path})")
    if path in visited:
        if not markdown_only:
            print(f"{indent}  [already visited]")
        return
    visited.add(path)

    objects = data.get("objects", [])
    for obj in objects:
        label = node_label(obj)
        has_markdown = bool(obj.get("markdownPath"))
        if not markdown_only:
            flags = []
            if has_markdown:
                flags.append("markdown")
                if obj.get("markdownSection"):
                    flags.append("section")
                else:
                    flags.append("index")
            if obj.get("subScenes"):
                flags.append("child")
            flag_text = f" [{', '.join(flags)}]" if flags else ""
            print(f"{indent}  - Node: {label}{flag_text}")
            if has_markdown:
                print(f"{indent}      markdown: {obj.get('markdownPath')}")
            if obj.get("markdownSection"):
                print(f"{indent}      section: {obj.get('markdownSection')}")
        elif has_markdown:
            md_path = obj.get("markdownPath")
            md_name = os.path.basename(md_path) if md_path else ""
            section = obj.get("markdownSection")
            section_text = f" :: {section}" if section else ""
            print(f"{path} -> {label} -> {md_name} ({md_path}){section_text}")
        if obj.get("subScenes"):
            for sub in obj.get("subScenes"):
                print_scene(sub, indent + "    ")

    if scene.get("autoMarkdownPath"):
        heading = scene.get("autoMarkdownHeadingLevel")
        heading_text = f" h{heading}" if isinstance(heading, int) else ""
        if not markdown_only:
            print(f"{indent}  - AutoMarkdownIndex:{heading_text}")
            print(f"{indent}      markdown: {scene.get('autoMarkdownPath')}")
        else:
            md_path = scene.get("autoMarkdownPath")
            md_name = os.path.basename(md_path) if md_path else ""
            print(f"{path} -> autoMarkdownPath{heading_text} -> {md_name} ({md_path})")
    if scene.get("autoMarkdownDirectory"):
        subdirs = " subdirs" if scene.get("autoMarkdownSubdirectories") else ""
        if not markdown_only:
            print(f"{indent}  - AutoMarkdownDirectory:{subdirs}")
            print(f"{indent}      directory: {scene.get('autoMarkdownDirectory')}")
        else:
            print(f"{path} -> autoMarkdownDirectory{subdirs} -> {scene.get('autoMarkdownDirectory')}")

print_scene(root_scene)
PY

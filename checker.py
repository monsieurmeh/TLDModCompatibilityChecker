import os
import json
import re
import tempfile
import requests
from pathlib import Path
from git import Repo
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import sys

# === CONFIGURATION ===
PATCH_MAP_FILE = "patch_map.json"
MOD_CACHE_FILE = "mod_cache.json"
OLDLISTS_CACHE_FILE = "oldlists_cache.json"
MAX_WORKERS = 8  # Number of threads for parallel processing

# === UTILITY FUNCTIONS ===

def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to fetch or parse JSON from {url}: {e}")
        return {}

def save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_json_file(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

# === HARMONY PATCH DETECTION ===

import re

def extract_harmony_patches_from_code(code):
    matches = []

    def normalize(cls, method):
        if not cls:
            cls = '?UnknownClass'
        if not method:
            return cls

        cls_parts = cls.split('.')
        method_parts = method.split('.')

        # Find largest k where last k parts of class == first k parts of method
        max_overlap = 0
        max_k = min(len(cls_parts), len(method_parts))
        for k in range(max_k, 0, -1):
            if cls_parts[-k:] == method_parts[:k]:
                max_overlap = k
                break

        method_suffix = method_parts[max_overlap:] if max_overlap else method_parts

        return f"{cls}.{'.'.join(method_suffix)}"

    # 1. [HarmonyPatch("Class.Method")]
    matches += [
        normalize(*full.rsplit('.', 1))
        for full in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+\.[\w]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 2. [HarmonyPatch("Class", "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+)"\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 3. [HarmonyPatch("Class", nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*"([\w\.]+)"\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 4. [HarmonyPatch(nameof(Class.Method))]
    matches += [
        normalize(*full.rsplit('.', 1))
        for full in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+\.[\w]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 5. [HarmonyPatch(nameof(Class), "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 6. [HarmonyPatch(nameof(Class), nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 7. [HarmonyPatch(typeof(Class))]
    matches += [
        normalize(*cls.rsplit('.', 1)) if '.' in cls else normalize(cls, None)
        for cls in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 8. [HarmonyPatch(typeof(Class), "Method")]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*,\s*"([\w\.]+)"\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    # 9. [HarmonyPatch(typeof(Class), nameof(Method))]
    matches += [
        normalize(cls, method)
        for cls, method in re.findall(
            r'\[HarmonyPatch\s*\(\s*typeof\s*\(\s*([\w\.]+)\s*\)\s*,\s*nameof\s*\(\s*([\w\.]+)\s*\)\s*(?:,\s*new\s+Type\[\]\s*\{[^\}]*\})?\s*\)\]',
            code
        )
    ]

    return matches

# === MOD REPO PROCESSING ===

def process_mod(repo_url, mod_name, mod_version, cache_entry, temp_dir):
    """
    Clones and scans a mod repo for Harmony patches.
    Returns: (mod_name, mod_version, patch_data_dict, status_string)
    """
    patches_found = []
    patch_map_for_mod = {}

    if cache_entry and cache_entry.get("version") == mod_version:
        return mod_name, mod_version, None, "unchanged"

    old_patches = cache_entry.get("patches", []) if cache_entry else []

    try:
        repo_name = repo_url.strip('/').split('/')[-1]
        repo_path = os.path.join(temp_dir, f"{mod_name}_{repo_name}")
        Repo.clone_from(repo_url, repo_path, depth=1)

        for path in Path(repo_path).rglob("*.cs"):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    code = file.read()
                    patches = extract_harmony_patches_from_code(code)
                    for patch in patches:
                        patch_map_for_mod.setdefault(patch, []).append(mod_name)
                        patches_found.append(patch)
            except Exception as e:
                print(f"⚠️ Error reading {path}: {e}")
    except Exception as e:
        print(f"❌ Failed to clone {repo_url}: {e}")
        return mod_name, mod_version, None, "error"

    return mod_name, mod_version, {
        "patches": patch_map_for_mod,
        "old_patches": old_patches
    }, "updated"

# === MOD LIST FETCHING ===

def get_mods_from_list_url(json_url):
    mods = []
    data = fetch_json(json_url)
    for mod in data.get("mods", []):
        repo_url = mod.get("modURL")
        mod_name = mod.get("name") or "UnknownMod"
        mod_version = mod.get("version") or "0.0.0"
        if repo_url and "github.com" in repo_url:
            mods.append((repo_url, mod_name, mod_version))
    return mods

# === MAIN CRAWLER FUNCTION ===

def crawl_from_site_data():
    patch_map = load_json_file(PATCH_MAP_FILE, {})
    mod_cache = load_json_file(MOD_CACHE_FILE, {})

    site_data = fetch_json(SITE_DATA_URL)
    list_urls = site_data.get("lists", [])
    oldlist_urls = site_data.get("oldlists", [])

    save_json_file(OLDLISTS_CACHE_FILE, oldlist_urls)
    print(f"💾 Saved oldlists to {OLDLISTS_CACHE_FILE}")

    mods_to_process = []

    for list_url in list_urls:
        print(f"🌐 Fetching mod list: {list_url}")
        mods = get_mods_from_list_url(list_url)

        for repo_url, mod_name, mod_version in mods:
            cache_entry = mod_cache.get(mod_name)
            mods_to_process.append((repo_url, mod_name, mod_version, cache_entry))

    with tempfile.TemporaryDirectory() as temp_dir, ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_mod = {
            executor.submit(process_mod, repo_url, mod_name, mod_version, cache_entry, temp_dir): mod_name
            for repo_url, mod_name, mod_version, cache_entry in mods_to_process
        }

        for future in as_completed(future_to_mod):
            mod_name = future_to_mod[future]
            try:
                mod_name, mod_version, result, status = future.result()

                if status == "unchanged":
                    print(f"⏩ Skipping {mod_name} (unchanged)")
                    continue
                elif status == "error":
                    continue

                for patch in result["old_patches"]:
                    if patch in patch_map:
                        patch_map[patch] = [m for m in patch_map[patch] if m != mod_name]
                        if not patch_map[patch]:
                            del patch_map[patch]

                for patch, mods in result["patches"].items():
                    patch_map.setdefault(patch, []).extend(mods)

                mod_cache[mod_name] = {
                    "version": mod_version,
                    "patches": list(result["patches"].keys())
                }

                print(f"✅ Updated {mod_name}: {len(result['patches'])} patches")

            except Exception as e:
                print(f"❌ Error processing {mod_name}: {e}")

    for patch in patch_map:
        patch_map[patch] = sorted(set(patch_map[patch]))

    save_json_file(PATCH_MAP_FILE, patch_map)
    save_json_file(MOD_CACHE_FILE, mod_cache)

    print(f"\n✅ Done. {len(patch_map)} patch entries saved to {PATCH_MAP_FILE}")

# === ENTRY POINT ===

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Harmony patch scanner.")
    parser.add_argument(
        "--site-data-url",
        type=str,
        required=True,
        help="URL to the SiteData.json file (required)"
    )

    args = parser.parse_args()
    SITE_DATA_URL = args.site_data_url.strip()

    if not SITE_DATA_URL:
        print("❌ Error: --site-data-url cannot be empty.")
        sys.exit(1)

    crawl_from_site_data()
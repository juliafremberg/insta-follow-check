#!/usr/bin/env python3
"""
Instagram follow checker — uses only your local data export.
No logins, no API, no network. Ever.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any


# Instagram usernames: 1-30 chars, alphanumeric, underscores, periods
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.]{1,30}$")


def extract_usernames_from_json(obj: Any) -> set[str]:
    """
    Recursively walk any JSON structure and extract usernames from
    string_list_data arrays (common in Instagram exports).
    Returns a deduplicated set of valid usernames.
    """
    usernames: set[str] = set()

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "string_list_data" and isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        val = item.get("value")
                        if isinstance(val, str) and USERNAME_PATTERN.match(val):
                            usernames.add(val)
            else:
                usernames |= extract_usernames_from_json(value)
    elif isinstance(obj, list):
        for item in obj:
            usernames |= extract_usernames_from_json(item)

    return usernames


def find_json_files(data_dir: Path, keyword: str) -> list[tuple[Path, int]]:
    """
    Walk data_dir for JSON files whose path contains the keyword.
    Returns list of (path, score) where higher score = better match.
    Files under 'followers_and_following' get a priority boost.
    """
    results: list[tuple[Path, int]] = []
    for path in data_dir.rglob("*.json"):
        rel_str = path.as_posix().lower()
        if keyword not in rel_str:
            continue
        score = 1
        if "followers_and_following" in rel_str:
            score += 10
        results.append((path, score))
    return results


def load_usernames_from_files(paths: list[Path], verbose: bool) -> set[str]:
    """Load and merge usernames from multiple JSON files."""
    all_usernames: set[str] = set()
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            if verbose:
                print(f"  [skip] {path}: {e}")
            continue
        usernames = extract_usernames_from_json(data)
        all_usernames |= usernames
        if verbose:
            print(f"  [ok] {path}: {len(usernames)} usernames")
    return all_usernames


def discover_followers_and_following(data_dir: Path, verbose: bool) -> tuple[set[str], set[str]]:
    """
    Find followers and following JSON files and extract usernames.
    Returns (followers_set, following_set).
    """
    followers_matches = find_json_files(data_dir, "followers")
    following_matches = find_json_files(data_dir, "following")

    # Prefer files under followers_and_following; sort by score descending
    def sort_key(p: tuple[Path, int]) -> int:
        return -p[1]

    followers_matches.sort(key=sort_key)
    following_matches.sort(key=sort_key)

    # Followers: files with "followers" in path, exclude following.json
    # Following: files with "following" in path, exclude followers_*.json
    followers_paths = [p for p, _ in followers_matches if p.name.lower() != "following.json"]
    following_paths = [
        p for p, _ in following_matches
        if not p.name.lower().startswith("followers")
    ]

    if not followers_paths:
        return set(), set()  # Caller will handle the error
    if not following_paths:
        return set(), set()

    followers = load_usernames_from_files(followers_paths, verbose)
    following = load_usernames_from_files(following_paths, verbose)

    return followers, following


def write_output(
    out_dir: Path,
    not_following_back: list[str],
    you_dont_follow_back: list[str],
    fmt: str,
) -> tuple[Path, Path]:
    """Write output files. Returns (path1, path2)."""
    ext = "csv" if fmt == "csv" else "txt"
    path1 = out_dir / f"not_following_back.{ext}"
    path2 = out_dir / f"you_dont_follow_back.{ext}"

    if fmt == "csv":
        with open(path1, "w", encoding="utf-8") as f:
            f.write("username\n")
            for u in not_following_back:
                f.write(f"{u}\n")
        with open(path2, "w", encoding="utf-8") as f:
            f.write("username\n")
            for u in you_dont_follow_back:
                f.write(f"{u}\n")
    else:
        with open(path1, "w", encoding="utf-8") as f:
            f.write("\n".join(not_following_back))
            if not_following_back:
                f.write("\n")
        with open(path2, "w", encoding="utf-8") as f:
            f.write("\n".join(you_dont_follow_back))
            if you_dont_follow_back:
                f.write("\n")

    return path1, path2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check who doesn't follow you back using your Instagram data export. No login, no API."
    )
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="Path to unzipped Instagram export folder",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "csv"],
        default="txt",
        help="Output format (default: txt)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extra debug info and top 10 preview",
    )
    args = parser.parse_args()

    data_dir = args.data.resolve()
    out_dir = args.out.resolve()

    if not data_dir.is_dir():
        print(f"Error: --data path is not a directory: {data_dir}")
        print("  Make sure you've unzipped your Instagram export and point to the top-level folder.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Scanning: {data_dir}")
        print("Looking for followers and following JSON files...")

    followers, following = discover_followers_and_following(data_dir, args.verbose)

    if not followers and not following:
        print("Error: Could not find or parse any followers/following data.")
        print()
        print("Expected folder structure:")
        print("  connections/")
        print("    followers_and_following/")
        print("      followers_1.json")
        print("      followers_2.json   (if you have many followers)")
        print("      following.json")
        print()
        print("Make sure you requested JSON format when downloading from Instagram.")
        print("(Settings → Accounts Center → Download your information → JSON)")
        return

    if not followers:
        print("Error: No followers data found.")
        print("  Look for JSON files under connections/followers_and_following/ containing 'followers' in the path.")
        print("  Confirm your export is in JSON format and includes connections data.")
        return

    if not following:
        print("Error: No following data found.")
        print("  Look for following.json under connections/followers_and_following/.")
        print("  Confirm your export is in JSON format and includes connections data.")
        return

    # People you follow who don't follow you back
    not_following_back = sorted(following - followers)
    # People who follow you that you don't follow back
    you_dont_follow_back = sorted(followers - following)

    path1, path2 = write_output(out_dir, not_following_back, you_dont_follow_back, args.format)

    # Summary
    print()
    print("Results")
    print("-------")
    print(f"People you follow who don't follow you back: {len(not_following_back)}")
    print(f"People who follow you that you don't follow back: {len(you_dont_follow_back)}")
    print()
    print(f"Written to:")
    print(f"  {path1}")
    print(f"  {path2}")

    if args.verbose and (not_following_back or you_dont_follow_back):
        print()
        print("Top 10 preview — not following you back:")
        for u in not_following_back[:10]:
            print(f"  @{u}")
        if len(not_following_back) > 10:
            print(f"  ... and {len(not_following_back) - 10} more")
        print()
        print("Top 10 preview — you don't follow back:")
        for u in you_dont_follow_back[:10]:
            print(f"  @{u}")
        if len(you_dont_follow_back) > 10:
            print(f"  ... and {len(you_dont_follow_back) - 10} more")


if __name__ == "__main__":
    main()

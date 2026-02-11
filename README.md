# insta-follow-check

made this bc my friend got hacked. oops! she downloaded one of those "who doesn't follow you back" apps and gave it her password. 🤦‍♀️

instead of trusting random third-party tools with your login, this script runs **locally** on your own data. you download your info straight from instagram, unzip it, and point this script at it. no logins, no API, no network — ever.

---

## what it does

1. **not_following_back** — accounts you follow that don't follow you back
2. **you_dont_follow_back** — accounts that follow you that you don't follow back

---

## step 1: download your instagram data

in the instagram app:

**Settings and privacy** → **Accounts Center** → **Your information and permissions** → **Download your information**

- select **JSON** format
- include at least connections / following data
- wait for the email, download, then **unzip** the folder

---

## step 2: run it

```bash
python followcheck.py --data "/path/to/unzipped_instagram_folder"
```

### options

| flag | description |
|------|-------------|
| `--data PATH` | **(required)** path to unzipped instagram export folder |
| `--out PATH` | output directory (default: current directory) |
| `--format txt \| csv` | output format (default: txt) |
| `--verbose` | print extra info + top 10 preview |

### examples

```bash
# basic
python followcheck.py --data ~/Downloads/instagram_data

# save to a different folder
python followcheck.py --data ~/Downloads/instagram_data --out ./results

# csv output
python followcheck.py --data ~/Downloads/instagram_data --format csv

# verbose (see top 10 + debug info)
python followcheck.py --data ~/Downloads/instagram_data --verbose
```

---

## output files

| file | contents |
|------|----------|
| `not_following_back.txt` (or `.csv`) | people you follow who don't follow you back |
| `you_dont_follow_back.txt` (or `.csv`) | people who follow you that you don't follow back |

---

## expected folder structure

your export should look roughly like:

```
instagram_data/
  connections/
    followers_and_following/
      followers_1.json
      followers_2.json   (if you have many followers)
      following.json
  ...
```

the script searches for JSON files containing "followers" and "following" in their path, so it should find them even if folder names differ slightly.

---

## requirements

none! python 3.10+ with stdlib only. no `pip install` needed.

---

## Security / Privacy

- **local only** — everything runs on your machine
- **no login** — the script never asks for or touches your instagram password
- **no network** — it doesn't make any internet requests
- **your data stays yours** — it only reads the files you point it at and writes the two output files

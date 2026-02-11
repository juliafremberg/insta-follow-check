# insta-follow-check
this project exists because my friend downloaded one of those “who doesn’t follow you back” apps and her instagram got hacked 😭

oops.

instead of giving your password to random third-party tools, this is a tiny script that runs locally on your computer using the data you download straight from instagram. no logins!

step 1) download your instagram data

in the instagram app:

settings and privacy → accounts center → your information and permissions → download your information

request the download in JSON format, wait for the email, then unzip the folder.

step 2) install

clone the repo:
git clone https://github.com/YOUR-USERNAME/instagram-follow-check.git
cd instagram-follow-check

pip install -r requirements.txt

step 3) run it
python followcheck.py --data "/path/to/unzipped_instagram_folder"

output) 
You'll get these files:
not_following_back.txt
you_dont_follow_back.txt

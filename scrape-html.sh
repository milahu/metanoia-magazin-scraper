#!/usr/bin/env bash

# start_url='https://www.metanoia-magazin.com/einzelausgaben/'
start_url='https://www.metanoia-magazin.com/'

wget_args=(
  wget
  --page-requisites
  --convert-links
  --adjust-extension
  # --mirror # -r -N -l inf --no-remove-listing
  --recursive # -r
  --timestamping # -N
  --level=inf # -l inf
  --no-remove-listing
  # --no-parent
)

"${wget_args[@]}" "$start_url"

# fix image urls
rg -F -l '.jpg.html' www.metanoia-magazin.com/ | xargs sed -i 's/\.jpg\.html/.jpg/g'
rg -l '\.svg[^"]+"' www.metanoia-magazin.com/ | xargs -r sed -i -E 's/\.svg[^"]+"/.svg"/g'
find www.metanoia-magazin.com/ -name '*.svg\?*' | while read -r src; do mv -v "$src" "${src%\?*}"; done

./remove_cookies_popup.py
./remove_chat_popup.py

exit

#####

# not reachable

{
  echo "$start_url"

  curl "$start_url" |
  grep -o -E 'href="https://www.metanoia-magazin.com/[^/"]+/(mm|ez)[0-9.-]+"' |
  sort -u |
  while read -r href
  do
    url="${href:6}" # remove 'href="' prefix
    url="${url:0: -1}" # remove '"' suffix
    echo "$url"
  done
} |
xargs -r "${wget_args[@]}"

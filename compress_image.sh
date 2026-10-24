#!/usr/bin/env bash
# Usage: compress_image.sh <input> <output>
set -euo pipefail

in="$1"
out="$2"
ext="${in##*.}"
ext="${ext,,}"

# Downscale to max 1920px wide (never upscale), keep aspect ratio
scale="scale='min(1920,iw)':-2"

case "$ext" in
  jpg|jpeg)
    ffmpeg -y -loglevel error -i "$in" -vf "$scale" -q:v 4 -map_metadata -1 "$out"
    ;;
  png)
    ffmpeg -y -loglevel error -i "$in" -vf "$scale" -compression_level 9 "$out"
    ;;
  webp)
    ffmpeg -y -loglevel error -i "$in" -vf "$scale" -quality 80 "$out"
    ;;
  *)
    cp -p "$in" "$out"
    exit 0
    ;;
esac

# If "compression" made the file bigger, keep the original instead
if [ "$(wc -c < "$out")" -ge "$(wc -c < "$in")" ]; then
  cp -p "$in" "$out"
fi

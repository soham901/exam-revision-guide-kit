#!/bin/bash
# usage: preview.sh out.pdf  -> writes out-pNN.png (90dpi) and out-sheet.png contact sheet
set -e
pdf="$1"; base="${pdf%.pdf}"
rm -f "$base"-p*.png
pdftoppm -r 90 -png "$pdf" "$base-p"
montage "$base"-p*.png -tile 6x -geometry 330x467+6+6 -background '#888' "$base-sheet.png"
ls "$base"-p*.png | wc -l

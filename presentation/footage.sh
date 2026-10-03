#!/bin/sh
# Renders the clips and stills used in the videos into footage/<name>/NNNN.jpg (30 fps)
# and assets/. Needs the programs in ../build (cmake --build ../build).
set -e
cd "$(dirname "$0")"
B=../build
TMP=$(mktemp -d)
mkdir -p assets

# A clip from the full simulator: name size frames args...
sim() {
  name=$1; size=$2; frames=$3; shift 3
  mkdir -p "footage/$name"
  "$B/blackhole" --size "$size" --sequence "$TMP/f" --frames "$frames" "$@" > /dev/null
  ffmpeg -v error -y -i "$TMP/f%04d.png" -q:v 3 "footage/$name/%04d.jpg"
  rm -f "$TMP"/f*
  echo "footage/$name: $frames frames"
}
# A clip from one of the stage programs: name program frames args...
stage() {
  name=$1; prog=$2; frames=$3; shift 3
  mkdir -p "footage/$name"
  "$B/$prog" --capture "$TMP/f" --frames "$frames" --size 1920x1080 "$@"
  ffmpeg -v error -y -i "$TMP/f%04d.ppm" -q:v 3 "footage/$name/%04d.jpg"
  cp "footage/$name/0001.jpg" "assets/$name.jpg"
  rm -f "$TMP"/f*
  echo "footage/$name: $frames frames"
}

stage stage1 stage01 270
stage stage2 stage02 240
stage stage2_stars stage02 150 --grid 0
stage stage3 stage03 300
stage stage3_plain stage03 2 --doppler 0

# Clips for the opening montage. The camera keeps its distance; the view is tilted (--roll) so the
# disk sits diagonally, and each clip sweeps through the disk plane a different way.
sim hook_1 1920x1080 240 --dist 40 --incl 80 --roll -18 --azim 10 --d-dist -0.0375 --d-azim 0.094 --d-time 0.14
sim hook_2 1920x1080 240 --dist 46 --incl 20 --roll 30 --d-incl 0.144 --d-azim 0.19 --d-time 0.14
sim hook_3 1920x1080 240 --dist 38 --incl 86 --roll 40 --d-roll -0.19 --azim 120 --d-azim -0.156 --d-time 0.14
sim hook_4 1920x1080 240 --dist 44 --incl 125 --roll -25 --d-incl -0.125 --azim 250 --d-azim 0.19 --d-time 0.14
sim hook_5 1920x1080 240 --dist 42 --incl 62 --roll 35 --d-incl 0.19 --azim 40 --d-azim 0.22 --d-time 0.14
sim hook_6 1920x1080 540 --dist 34 --incl 78 --roll 12 --d-roll -0.022 --azim 60 --d-dist 0.016 --d-azim 0.045 --d-time 0.14

sim orbit 1920x1080 300 --dist 30 --incl 81 --azim 20 --d-azim 0.12 --d-incl -0.012 --d-time 0.14
sim tilt 1280x720 240 --dist 34 --incl 20 --d-incl 0.285 --d-azim 0.1 --d-time 0.14
"$B/blackhole" --preset edgeon --size 1920x1080 --screenshot assets/edgeon.png > /dev/null && .venv/bin/python -c "from PIL import Image; Image.open('assets/edgeon.png').convert('RGB').save('assets/edgeon.jpg', quality=92)" && rm assets/edgeon.png
rmdir "$TMP"

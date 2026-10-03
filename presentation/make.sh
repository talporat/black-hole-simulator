#!/bin/sh
# Builds the video series: blackhole_ep1.mp4, blackhole_ep2.mp4, ...
#   ./make.sh                 every episode, 1080p, narrated
#   ./make.sh l ep2           480p preview of episode 2
#   ./make.sh h all --voice am_michael     extra options go to `tts.py speak`
#   NO_TTS=1 ./make.sh        keep whatever clips are in audio/ (silent if none)
set -e
cd "$(dirname "$0")"
export PATH="$PATH:$HOME/Library/TinyTeX/bin/universal-darwin"
[ -x .venv/bin/manim ] && PATH="$PWD/.venv/bin:$PATH"

Q="${1:-h}"
WHICH="${2:-all}"
[ $# -ge 2 ] && shift 2 || shift $#
case "$Q" in
  l) DIR=480p30 ;;
  h) DIR=1080p30 ;;
  *) echo "usage: ./make.sh [l|h] [all|ep1|ep2|...] [tts.py speak options]"; exit 2 ;;
esac
[ "$WHICH" = all ] && WHICH=$(ls ep[0-9]*.py | sed 's/\.py$//')

[ -d footage/stage1 ] || ./footage.sh
if [ -n "$NO_TTS" ]; then python tts.py extract > /dev/null; else python tts.py speak "$@"; fi

for EP in $WHICH; do
  SCENES=$(grep -o '^class E[0-9A-Za-z_]*' "$EP.py" | cut -d' ' -f2)
  manim render -q"$Q" --fps 30 --media_dir media "$EP.py" $SCENES
  : > "media/concat_$EP.txt"
  for s in $SCENES; do echo "file 'videos/$EP/$DIR/$s.mp4'" >> "media/concat_$EP.txt"; done
  ffmpeg -v error -y -f concat -safe 0 -i "media/concat_$EP.txt" -c copy "media/silent_$EP.mp4"
  python tts.py mux "$EP"
done

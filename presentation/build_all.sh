#!/bin/sh
# Full unattended rebuild: voice every sentence (slow with Chatterbox), then render all episodes.
cd "$(dirname "$0")"
.venv/bin/python tts.py speak > media/speak.log 2>&1 || { echo "speak failed"; tail -5 media/speak.log; exit 1; }
grep -c "words matched" media/speak.log
grep "listen to this one" media/speak.log
NO_TTS=1 ./make.sh h all > media/make.log 2>&1
tr '\r' '\n' < media/make.log | grep -E "wrote|Traceback|Error" | cut -c1-200

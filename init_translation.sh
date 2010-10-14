#!/usr/bin/env bash

LANGDIR="locale/$1"

if [ -d $LANGDIR ]; then
	rm -rf $LANGDIR;
fi;

mkdir -p $LANGDIR/LC_MESSAGES

msginit -l $1 -o $LANGDIR/LC_MESSAGES/hometape.po -i hometape.pot

echo "The .po file is located at: $LANGDIR/LC_MESSAGES/hometape.po"

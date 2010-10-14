#!/usr/bin/env bash

for locale_dir in locale/*; do
	msgfmt "${locale_dir}/LC_MESSAGES/hometape.po" -o "${locale_dir}/LC_MESSAGES/hometape.mo"
done;

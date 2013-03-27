#! /usr/bin/env bash
kill $(ps aux | grep '[p]ython src/gc/grooviks1.py' | awk '{print $2}')

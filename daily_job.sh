#!/bin/bash
cd ~/security_syncer
currentDate=`date +'%Y-%m-%d'`
grep -qsi "synced for $currentDate" log/run.log
if [[ $? -ne 0 ]]; then
  rm -f data/adjusted_data.db && /home/pi/.pyenv/versions/3.9.18/envs/security_syncer/bin/python store_daily_data.py >> log/run.log 2>&1
  cp -f data/adjusted_data.db ../security_watcher/data/
else
  echo "The sync has already been run for $currentDate"
fi

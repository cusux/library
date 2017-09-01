#!/bin/bash

#########################################
#                                       #
#               BackRotor               #
#                                       #
#     Configurable Backup Rotation      #
#                                       #
#         2016 - Paul Wetering          #
#                                       #
#########################################

# Backup storage location
# Must contain subfolders backup.monthly backup.weekly and backup.daily
storage=/backup

# Source folder
source=$storage/incoming

# Destination filenames
date_daily=`date +"%d-%m-%Y"`
#date_weekly=`date +"%V sav. %m-%Y"`
#date_monthly=`date +"%m-%Y"`

# Get current month and week day numbers
month_day=`date +"%d"`
week_day=`date +"%u"`

# Optional; check source existance and mail if not
#if [ ! -f $source/kvm_archive.tgz ]; then
#	ls -l $source/ | mail user@host.domain -s "[backup script] Daily backup failed! Please check for missing files."
#fi

# Run daily, take files from source and move to destination

# First of the month perform monthly
if [ "$month_day" -eq 1 ]; then
	destination=$storage/backup.monthly/$date_daily
else
	# On Saturday perform weekly
	if [ "$month_day" -eq 6 ]; then
		destination=$storage/backup.weekly/$date_daily
	else
		destination=$storage/backup.daily/$date_daily
	fi
fi

# Move files
mkdir $destination
mv -v $source/* $destination

# Daily - keep 14 days
find $storage/backup.daily/ -maxdepth 1 -mtime +14 -type d -exec rm -rv {} \;

# Weekly - keep 60 days
find $storage/backup.weekly/ -maxdepth 1 -mtime +60 -type d -exec rm -r {} \;

# Monthly - keep 300 days
find $storage/backup.monthly/ -maxdepth 1 -mtime +300 -type d -exec rm -rv {} \; 

#!/bin/bash

#########################################
#                                       #
#              KVM Backup               #
#                                       #
#           Simple KVM Backup           #
#                                       #
#         2016 - Paul Wetering          #
#                                       #
#########################################

BACKUP_DIR=/backup
FILES_DIR=/kvm-data

# Timestapm
echo "[$(date)] : Starting KVM backup procedure."

# Compress files
echo "[$(date)] : Compressing files."
tar -czf $BACKUP_DIR/incoming/kvm_archive.tgz $FILES_DIR

# Run BackRotor
echo "[$(date)] : Starting log rotation."
bash /root/kvm_backup_rotate.sh
echo "[$(date)] : KVM backup procedure finished."

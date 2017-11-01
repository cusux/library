#Force process output
if [ "$(shell_)command $> /dev/null; echo $?)" -eq "0" ]; then echo yes; else echo no; fi

#Test OCSP
openssl ocsp --issuer ca.pem -nonce -CAfile ca.pem -url http://ocsp.server/ocsp -cert mycert.pem

#freeRDP
rdp<hostname> () {
        xfreerdp -u <user> --no-nla --plugin rdpdr --data disk:Transfer:/ -- <target_host_ip>
}

#ClamAV Scanning
clamscan --log=/var/log/clamav/clamd_daily.scan -a -v -r -z --detect-pua=yes --detect-structured=yes --structured-ssn-format=2 --enable-stats /home
clamscan --log=/var/log/clamav/clamd_monthy.scan -a -v -r -z --detect-pua=yes --detect-structured=yes --structured-ssn-format=2 --enable-stats /
#ClamAV Cron schedule
0 0 */15 * * /usr/bin/clamscan --log=/var/log/clamav/clamd_daily.scan -a -v -r -z --detect-pua=yes --detect-structured=yes --structured-ssn-format=2 --enable-stats /home >/dev/null 2>&1
0 0 1 * * clamscan --log=/var/log/clamav/clamd_monthy.scan -a -v -r -z --detect-pua=yes --detect-structured=yes --structured-ssn-format=2 --enable-stats / >/dev/null 2>&1

# Disk to image
dd bs=65536 if=/dev/%disc% of=%diskimagefile%

# View dd output
pgrep -l '^dd$'
watch -n kill -USR1 %dd_pid%

# Mount a partition inside an image.
# Get blocksize and startingblock number:
fdisk -lu %diskimagefile%
#Mount the device with loopback and offset equal to blocksize*startingblock:
mount -t auto -o loop,offset=$((%startingblock%*%blocksize%)) /path/to/%diskimagefile% /mnt/%mountingpoint%


# Test network segment for duplicate IP addresses using arping
for ip in 10.0.0.{0..255}; do arping -D -I eth0 -c 2 $ip ; done > ./tmp.txt
cat ./tmp.txt | grep Received | grep -v 0 | grep -v 1

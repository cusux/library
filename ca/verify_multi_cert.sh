#!/bin/bash

#########################################
#																				#
#           Verify Multi Cert           #
#																				#
# OCSP request for certificate validity	#
#																				#
#         2016 - Paul Wetering          #
#																				#
#########################################

# Output formatting
b=$(tput bold)
n=$(tput sgr0)

# Output the usage on invalid or missing parameters
[ "$1" == "" ] && { echo -e "\tUsage:\n\t$0 ${b}<filename> ${n}screen\t- All output to screen.\n\t$0 ${b}<filename> ${n}mail test\t- Display mail contents and command on screen.\n\t$0 ${b}<filename> ${n}mail live\t- Output results to email."; exit 1; }
[ "$2" == "" ] && { echo -e "\tUsage:\n\t$0 $1 ${b}<screen> ${n}or ${b}<mail>${n}"; exit 1; }
[ "$2" == "mail" -a "$3" == "" ] && { echo -e "\tUsage:\n\t$0 $1 $2 ${b}<test> ${n}or ${b}<live>${n}"; exit 1; }

# Define base variables#Output usage is no parameters are given
base="/home/pwetering/Documents/Cursus_CA_hands_on/Part_1/ca"	#Base path of the CA
chain="$base/intermediate/certs/ca-chain.cert.pem"						#CA-chain file location after basepath
issuer="$base/intermediate/certs/intermediate.cert.pem"				#Issuer certificate location after basepath
prefix="$base/intermediate/certs/"														#Certificate folder location after basepath
ocsp="http://127.0.0.1:2560"																	#OCSP server

# File contents to array
file=$1
certs=$(cat $file)

# Remove variable
unset result

# Loop through the file
for cert in $certs; do
	# Removing variables
	unset response certstatus certfrom certto now certtos days

	# Perform OCSP request and fill variable with complete response text
	response=$(openssl ocsp -CAfile $chain -url $ocsp -resp_text -issuer $issuer -cert $prefix$cert)

	# Generate variables from request result
	certstatus=$(echo "$response" | awk '/Cert Status/ {print}' | sed 's/^[\t ]*//g')	#Grab the certificate status and trim leading whitespace
	certstatus=${certstatus:13:20}																										#Narrow to a substring containing only the certificate status
	certfrom=$(echo "$response" | awk '/Not Before/ {print}' | sed 's/^[\t ]*//g')		#Grab the certificate starting date and trim leading whitespace
	certfrom=${certfrom:12:20}																												#Narrow to a substring containing only the date
	certfrom=$(date --date="$(printf "%s" "$certfrom")" +"%Y-%m-%d")									#Convert the substring to usable date string
	certto=$(echo "$response" | awk '/Not After/ {print}' | sed 's/^[\t ]*//g')				#Grab the certificate ending date and trim leading whitespace
	certto=${certto:12:20}																														#Narrow to a substring containing only the date
	certto=$(date --date="$(printf "%s" "$certto")" +"%Y-%m-%d")											#Convert the substring to usable date string
	now=$(date +%Y-%m-%d)																															#Fill variable with date string for current day
	now=$(date --date "$now" +%s)																											#Convert date string for today to seconds
	certtos=$(date --date "$certto" +%s)																							#Convert date string for ending date to seconds
	days=$(($certtos - $now))																													#Substract seconds from ending date and today in seconds
	days=$(($days/(3600*24)))																													#Convert the seconds to days

	# Accumulate results
	result="$result\nCertificate ${b}$cert ${n}has a ${b}$certstatus ${n}status and a validity from ${b}$certfrom ${n}until ${b}$certto ${n}(remainder: ${b}$days ${n}days)."
done

# Output
case "$2" in
	"screen") #Screen output
		echo "screen"
		echo -e "$result"
	;;
	"mail") #Mail output
		$(echo "" > /tmp/mail)
		echo "From: validator@company.com" >> /tmp/mail
		echo "To: receiver@company.com" >> /tmp/mail
		echo "Subject: Certificate validity check" >> /tmp/mail
		echo -e "$result" >> /tmp/mail
		[ $3 == "test" ] && { echo -e "$(cat /tmp/mail)\n\nThe command to run would be:\n$ cat /tmp/mail | /usr/sbin/sendmail -t"; exit 1; }
		[ $3 == "live" ] && { echo "$(cat /tmp/mail | /usr/sbin/sendmail -t)"; exit 1;}
	;;
esac

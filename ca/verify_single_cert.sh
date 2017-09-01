#!/bin/bash

#########################################
#          Verify Single Cert           #
#					#
# OCSP request for certificate validity	#
#					#
#         2016 - Paul Wetering          #
#					#
#########################################
[ $# -eq 0 ] && { echo "Usage: $0 <certificate filename>"; exit 1; }	#Output usage is no parameters are given

# Define base variables
base="/base/path/to/the/ca"	#Base path of the CA
chain="$base/intermediate/certs/ca-chain.cert.pem"		#CA-chain file location after basepath
issuer="$base/intermediate/certs/intermediate.cert.pem"		#Issuer certificate location after basepath
prefix="$base/intermediate/certs/"				#Certificate folder location after basepath
ocsp="http://127.0.0.1:2560"					#OCSP server
cert=$1								#Certificate filename			

result=$(openssl ocsp -CAfile $chain -url $ocsp -resp_text -issuer $issuer -cert $prefix$cert)	#Perform OCSP request and fill variable with complete response text

# Generate variables from request result
certstatus=$(echo "$result" | awk '/Cert Status/ {print}' | sed 's/^[\t ]*//g')	#Grab the certificate status and trim leading whitespace
certstatus=${certstatus:13:20}							#Narrow to a substring containing only the certificate status
certfrom=$(echo "$result" | awk '/Not Before/ {print}' | sed 's/^[\t ]*//g')	#Grab the certificate starting date and trim leading whitespace
certfrom=${certfrom:12:20}							#Narrow to a substring containing only the date
certfrom=$(date --date="$(printf "%s" "$certfrom")" +"%Y-%m-%d")		#Convert the substring to usable date string
certto=$(echo "$result" | awk '/Not After/ {print}' | sed 's/^[\t ]*//g')	#Grab the certificate ending date and trim leading whitespace
certto=${certto:12:20}								#Narrow to a substring containing only the date
certto=$(date --date="$(printf "%s" "$certto")" +"%Y-%m-%d")			#Convert the substring to usable date string
now=$(date +%Y-%m-%d)								#Fill variable with date string for current day
nows=$(date --date "$now" +%s)							#Convert date string for today to seconds
certtos=$(date --date "$certto" +%s)						#Convert date string for ending date to seconds
days=$(($certtos - $nows))							#Substract seconds from ending date and today in seconds
days=$(($days/(3600*24)))							#Convert the seconds to days

# Output formatting
b=$(tput bold)
n=$(tput sgr0)

# Screen output
echo "Certificate ${b}$cert ${n}has a ${b}$certstatus ${n}status and a validity from ${b}$certfrom ${n}until ${b}$certto ${n}(remainder: ${b}$days ${n}days)."

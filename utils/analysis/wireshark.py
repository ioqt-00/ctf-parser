#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import os
import random
from scapy.all import *
import pcapkit
import binascii

from utils.other import rdnname,writefile,append_result,execmd

def analyse_wireshark(path_document,ext,formatflag):

	result = []

	# General Commands
	cmd = {
		"Strings":"timeout 10 strings -t x %s"%path_document,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%path_document,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%path_document,
		"Strings Flag Grepped":"timeout 10 strings -t x %s | grep \"{formatflag}\""%path_document,	
		"Binwalk":"timeout 10 binwalk %s"%path_document,
		"SslDump":"timeout 10 ssldump -r %s"%path_document,
		"Tshark Meta-Data":"tshark -r %s -q -z http,tree"%path_document,
		"Tshark HTTP":"tshark -r %s -Y http.request -T fields -e http.host -e http.user_agent"%path_document
		}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append_result(result,command,cnt)			
		except Exception as ex:
			result  = append_result(result,command,str(ex))



	# PcapKit cmd
	try:
		rdn_name = rdnname()
		plist = pcapkit.extract(fin=path_document, fout='/tmp/%s.json'%rdn_name, format='json', store=False)
		if(os.path.isfile('/tmp/%s.json'%rdn_name)):
			result = append_result(result,'PcapKit','/tmp/%s.json'%rdn_name)
	except Exception as ex:
		result  = append_result(result,'PcapKit',str(ex))


	# ChaosReader Analyse
	namefile = rdnname()
	chaos_cmd = 'mkdir -p /tmp/%s;cd /tmp/%s;chaosreader %s;zip -q -r /tmp/%s.zip /tmp/%s echo /tmp/%s.zip;rm -r /tmp/%s'%(namefile,namefile,path_document,namefile,namefile,namefile,namefile);
	try:
		res = execmd(chaos_cmd)		
		if(os.path.isfile('/tmp/%s.zip'%namefile)):
			result = append_result(result,'ChaosReader','/tmp/%s.zip'%namefile)
	except Exception as ex:
		result  = append_result(result,'ChaosReader',str(ex))


	# RdpCap
	packets = rdpcap(path_document)
	all_ = []
	for p in packets:
		try:
			all_.append(p[Raw].load)
		except:
			pass
	rdn_name = rdnname()
	writefile('/tmp/%s.txt'%rdn_name,str(all_))
	result = append_result(result, 'RdpCap_Data','/tmp/%s.txt'%rdn_name)
 
	
	
	# RdpCap unhexlified
	all_hex = ''
	for p in all_:
		try:
			all_hex += str(binascii.unhexlify(p))+'\n'
		except:
			pass				
	rdn_name = rdnname()
	writefile('/tmp/%s.txt'%rdn_name,str(all_hex))
	result = append_result(result,'RdpCap_Data_Unhexlified','/tmp/%s.txt'%rdn_name)


	# Udp packets to files
	rdn_name = rdnname()
	with open('/tmp/%s.raw'%rdn_name, 'wb') as f:
		for p in packets:
			if UDP in p:
				try:
					chunk = bytes(p[Raw])
					f.write(chunk)
				except:
					pass
	result = append_result(result,'UDP Data Dumped','/tmp/%s.raw',rdn_name)


	# File on the Raw file
	path = '/tmp/%s.raw'%rdn_name
	if(os.path.isfile(path) and os.path.getsize(path) > 0):
		cnt = os.popen('file /tmp/%s.raw'%rdn_name).read()
		result = append_result(result,'File on %s.raw'%rdn_name,cnt)

	
	return result
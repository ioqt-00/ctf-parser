#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import pyUnicodeSteganography as usteg
from utils.other import readfile,execmd,append_result

def analyse_document(path_document,ext):
	result = []

	cmd = {
		"Strings":"timeout 10 strings -t x %s"%path_document,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%path_document,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%path_document,
		"Binwalk":"timeout 10 binwalk %s"%path_document,
		"StegSnow":"timeout 10 stegsnow -C %s"%path_document
		}


	# Commande classique   
	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append_result(result,command,cnt)
		except Exception as ex:
			result = append_result(result,command,str(ex))



	# If Word document > Extract Macro	
	olevba_cmd = "timeout 10 olevba %s --decode"%path_document

	if(ext in ['.docx','.odt','.doc','.docm']):
		try:
			cnt = execmd(olevba_cmd)
			result = append_result(result,"Olevba",cnt)
		except Exception as ex:
			result = append_result(result,'Olevba',str(ex))
	


	# If it's Text document > usteg
	if(ext in ['.txt','']):
		try:
			encoded = readfile(path_document)
			cnt = usteg.decode(encoded)
			if(cnt != ''):
				result = append_result(result,"ZWSP",cnt)
		except Exception as ex:
			result = append_result(result,'ZWSP',str(ex))

	if(ext in ['.pdf']):
		try:
			cmd = 'timeout 10 pdf-parser %s'%path_document
			cnt = execmd(cmd)
			result = append_result(result,"Pdf Parser",cnt)
		except Exception as ex:
			result = append_result(result,'Pdf Parser',str(ex))



	return result
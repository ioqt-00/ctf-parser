#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import r2pipe
from utils.other import append_result,execmd

def rad2(file):
	r = r2pipe.open(file)
	final  = '-'*30+'\n'
	final += r.cmd('aaa;afl')
	final += '-'*30+'\n'
	final += r.cmd("iz")
	final += '-'*30+'\n'	
	return final

def rad2_getmain(file):
	r = r2pipe.open(file)
	final = '-'*30+'\n'
	r.cmd("aaa;afl")
	final += r.cmd("pdf @main")
	final += '-'*30+'\n'
	return final


def analyse_elf(file,ext):
	result = []

	cmd = {
		"Strings":"timeout 10 strings %s"%file,
		"File":"timeout 10 file %s"%file,
		"Checksec":"timeout 10 checksec %s"%file,
		"Header":"timeout 10 readelf -h  %s"%file,
		"Header Section":"timeout 10 readelf -S  %s"%file,
		"Strace":"timeout 10 echo 'guess' | strace %s guess2"%file,
		"Ltrace":"timeout 10 echo 'guess' | ltrace %s guess2"%file,		
	}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append_result(result,command,cnt)
		except Exception as ex:
			result = append_result(result,command,str(ex))

	try:
		cnt = rad2(file)
		result = append_result(result,"Radare2",cnt)
	except Exception as ex:
		result = append_result(result,'Radare2',str(ex))

	try:
		cnt = rad2_getmain(file)
		result = append_result(result,"Radare2 Main",cnt)
	except Exception as ex:
		result = append_result(result,'Radare2 Main',str(ex))

	return result  
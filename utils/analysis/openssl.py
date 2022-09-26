#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

from utils.other import rdnname,writefile,append_result,execmd


def analyse_key(path_document,ext):
	result = []

	cmd = {
		"OpenSsl PublicKey":"timeout 10 openssl rsa -noout -text -inform PEM -in '%s' -pubin -modulus"%path_document,
		"OpenSsl PrivateKey":"timeout 10 openssl rsa -noout -text -in '%s' -modulus"%path_document,		
		}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append_result(result,command,cnt)
		except Exception as ex:
			result  = append_result(result,command,str(ex))


	return result
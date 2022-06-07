#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import os
import matplotlib.pyplot as plt
from PIL import Image
import numpy
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
from utils.other import execmd,append_result

def analyseImage(path):
	im = Image.open(path)
	results = {'size': im.size,'mode': 'full',}
	try:
		while True:
			if im.tile:
				tile = im.tile[0]
				update_region = tile[1]
				update_region_dimensions = update_region[2:]
				if update_region_dimensions != im.size:
					results['mode'] = 'partial'
					break
			im.seek(im.tell() + 1)
	except EOFError:
		pass
	return results

def gifextract(path):
	mode = analyseImage(path)['mode']	
	im = Image.open(path)
	i = 0
	p = im.getpalette()
	last_frame = im.convert('RGBA')	
	try:
		while True:
			if not im.getpalette():
				im.putpalette(p)			
			new_frame = Image.new('RGBA', im.size)
			if mode == 'partial':
				new_frame.paste(last_frame)			
			new_frame.paste(im, (0,0), im.convert('RGBA'))
			new_frame.save("/tmp/gifpng/"+'%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')
			i += 1
			last_frame = new_frame
			im.seek(im.tell() + 1)
	except EOFError:
		return True
	return False

def lsb_graph(in_file,savepath):
	BS = 100
	img = Image.open(in_file)
	(width, height) = img.size
	conv = img.convert("RGBA").getdata()
	vr = []
	vg = []
	vb = []
	for h in range(height):
		for w in range(width):
			(r, g, b, a) = conv.getpixel((w, h))
			vr.append(r & 1)
			vg.append(g & 1)
			vb.append(b & 1)
	avgR = []
	avgG = []
	avgB = []
	for i in range(0, len(vr), BS):
		avgR.append(numpy.mean(vr[i:i + BS]))
		avgG.append(numpy.mean(vg[i:i + BS]))
		avgB.append(numpy.mean(vb[i:i + BS]))
	numBlocks = len(avgR)
	blocks = [i for i in range(0, numBlocks)]
	plt.axis([0, len(avgR), 0, 1])
	plt.ylabel('Average LSB per block')
	plt.xlabel('Block number')
	plt.plot(blocks, avgB, 'bo')
	plt.savefig(savepath)

def aperisolve(img):
	mp_encoder = MultipartEncoder(
		fields={
	        'file':("rngcollision.jpg",open(img, 'rb')),
	        'zsteg_ext':'false',
	        'zsteg_all':'false',
	        'use_password':'false',
	        'password':"",
	    }
	)
	res = json.loads(requests.post('https://aperisolve.fr/upload',data=mp_encoder,headers={'Content-Type': mp_encoder.content_type}).text)
	if not (res.get('File') is None):
		return 'https://aperisolve.fr/%s\n'%(str(res["File"]))
	else:
		return 'Error: %s\n'%res["Error"]

def analyse_picture(img,ext):
	result = []

	rockyou = './utils/wordlists/rockyou.txt'

	## All Cmd 
	cmd = {
		"Strings":"timeout 10 strings -t x %s" %img,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%img,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%img,
		"Exiftool":"timeout 10 exiftool %s"%img,
		"Pngcheck":"timeout 10 pngcheck -vtp7 %s"%img,
		"Binwalk":"timeout 10 binwalk %s"%img,
		"Zsteg":"timeout 10 zsteg %s"%img,
		"Stegpy":"timeout 10 stegpy %s"%img,
		"StegoPVD (Line 1-6 = Logo)":"timeout 10 stegopvd bruteforce %s"%img,
		
		}

	
	# Execute Cmd for all
	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append_result(result,command,cnt)
		except Exception as ex:
			result = append_result(result,command,str(ex))
	

	#Cmd with file as output
	cmd2 = {
		"Stegoveritas":"UUID=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`;TMP_DIR=/data/stegoVeritas/$UUID;mkdir -p $TMP_DIR;stegoveritas %s -out $TMP_DIR -meta -imageTransform -colorMap -trailing;zip -q -r /data/stegoVeritas/$UUID.zip /data/stegoVeritas/$UUID ;rm -r /data/stegoVeritas/$UUID;echo UID=$UUID"%img,
		"LsbDetect": "stegolsb stegdetect -i %s -n 2"%img,
		"Jsteg":"timeout 10 jsteg reveal %s 2> /tmp/jsteg_output.txt"%img,
		"StegSeek Brute":"timeout %s stegseek --crack -sf %s -wl %s -f -v -xf /tmp/output_stegseek.txt 2> /tmp/output_stegseek_cmd.txt"%(60*5,img,rockyou),
		"StegSeek Seed":"timeout %s stegseek --seed -sf %s -f 2> /tmp/output_stegseek_seed_cmd.txt"%(60*2,img)
	}


	exec_stegseek_seed = True
	for command in cmd2.keys():
		try:
			if( not (command == 'StegSeek Seed' and exec_stegseek_seed == False)):
				cnt = execmd(cmd2[command])

				result_path = []
				if(command == "Stegoveritas"):
					result_path = ['/data/stegoVeritas/%s.zip'%cnt.split('UID=')[1].strip()]
				elif(command == "Jsteg"):
					result_path = ['/tmp/jsteg_output.txt']
				elif(command == "LsbDetect"):
					result_path = ['%s/%s_2LSBs.%s'%(os.path.dirname(os.path.abspath(img)),os.path.basename(img).split('.')[0],os.path.basename(img).split('.')[1])]
				elif(command == "StegSeek Brute"):
					result_path = ['/tmp/output_stegseek_cmd.txt','/tmp/output_stegseek.txt']
					## Useless to run seed check if data found
					if(os.path.isfile(result_path[0])):
						if('extracting data...done' in open(result_path[0],'r').read()):
							exec_stegseek_seed = False
				elif(command == "StegSeek Seed"):
					result_path = ['/tmp/output_stegseek_seed_cmd.txt']

				for pt in result_path:
					if(os.path.isfile(pt)):
						result = append_result(result,command,pt)
		except Exception as ex:
			result = append_result(result,command,str(ex))



	# If is gif
	# Other Cmd	
	gifpng_cmd = 'zip -q -r /tmp/gifframe.zip /tmp/gifpng;rm -r /tmp/gifpng/%s*'%''.join(os.path.basename(img).split('.')[:-1])

	if('.gif' == ext):
		try:
			if(os.path.isdir('/tmp/gifpng') == False):
				os.mkdir('/tmp/gifpng')
			if(gifextract(img)):				
				execmd(gifpng_cmd)
				if(os.path.isfile('/tmp/gifframe.zip')):
					result = append_result(result,'GifFrames','/tmp/gifframe.zip')
		except Exception as ex:
			result = append_result(result,'GifFrames',str(ex))



	## LsbGraph
	try:
		lsb_graph(img,'/tmp/lsb_graph.png')
		if(os.path.isfile('/tmp/lsb_graph.png')):
			result = append_result(result,'LsbGraph','/tmp/lsb_graph.png')
	except Exception as ex:
		result = append_result(result,'LsbGraph',str(ex))


	## Apérisolve

	try:
		res = aperisolve(img)
		result.append('**Aperi\'Solve**\n%s\n'%res)
	except Exception as ex:
		result = append_result(result,'AperiSolve',str(ex))

	return result
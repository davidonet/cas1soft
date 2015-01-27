#!/usr/bin/python
# -*- coding: utf-8 

from PIL import Image, ImageDraw, ImageFont
import tempfile
import sys
import subprocess
import random

for seq in xrange(1,16):
	output = tempfile.mkdtemp()
	font = ImageFont.truetype("univers.otf", 40)
	nb = random.randint(60,180) * 25
	im = Image.new('RGB', (1280,720), (0,0,0))
	draw = ImageDraw.Draw(im)
	draw.line((0, 0) + im.size, (255,0,0))
	draw.line((0, im.size[1], im.size[0], 0), (255,0,0))
	text = "SEQUENCE "+str(seq).zfill(3)
	w, h = draw.textsize(text,font=font)
	draw.text(((1280-w)/4,(720-h)/2), text,font=font, fill="white")
	for i in xrange(0,nb):
		text = str(i).zfill(4) + ' / ' + str(nb)
		w, h = draw.textsize(text,font=font)
		draw.rectangle(((3*(1280-w)/4,(720-h)/2),(w+3*(1280-w)/4,h+(720-h)/2)), fill="black")
		draw.text((3*(1280-w)/4,(720-h)/2), text,font=font, fill="white")
		im.save(output+'/frame_'+str(i).zfill(5)+'.png', 'PNG')
		sys.stdout.write("Sequence %d - Generating frame : %d / %d\r" % (seq,i,nb))
		sys.stdout.flush()
	subprocess.call(['ffmpeg', '-i', output +'/frame_%5d.png', '-c:v', 'libx264','-pix_fmt','yuv420p','-profile:v','baseline','-tune','animation','-crf','10','-f','mp4', 'sequences/sequence_'+str(seq).zfill(3)+'.mp4'])
	subprocess.call(['rm', '-rf', output])
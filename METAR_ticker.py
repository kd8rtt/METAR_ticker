#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import datetime
import os

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

    def Run(self):
	
        offscreenCanvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../fonts/9x15.bdf")
        green = graphics.Color(0, 255, 0) #vfr
	magenta = graphics.Color(255,0,255) #lifr
	blue = graphics.Color(0,0,255) #mvfr
	red = graphics.Color(255,0,0) #ifr
        pos = offscreenCanvas.width

	icao_code = "KUNI" #enter the ICAO code of the airport you want to check
 

	gap = ""
	com1 = "sudo wget -O "
	com2 = ".TXT "
	com3 = "ftp://tgftp.nws.noaa.gov/data/observations/metar/stations/"
	com4 = ".TXT"
	term = gap.join([com1, icao_code, com2, com3, icao_code, com4])
	print(term)
	
	try:
		os.system(term)
	except Exception:
		os.system('shutdown -r now')	
#	os.system("sudo wget -O K6L4.TXT ftp://tgftp.nws.noaa.gov/data/observations/metar/stations/K6L4.TXT")
	file_name =  gap.join([icao_code, ".TXT"])
	try:
		f = open(file_name)
		f.readline()
		metar_raw = f.readline()
		metar = metar_raw[:-1]
		print(metar)
	finally:
		f.close()

#	if (len(metar) == 0):
#		os.system('shutdown -r now')	
#	metar = "KUNI 211950Z AUTO 29011G18KT 15SM RA BKN013 OVC020 OVC300 10/10 A2991 RMK A02 P0005 T00950096"	#for dev
	

	#parse the METAR to determine VFR, MVFR, IFR, LIFR
	#finding visiblity
	vis_val = 0
	sm_loc = metar.find("SM")
	if sm_loc < 0:
		os.system('sudo reboot')
	elif ((metar[sm_loc-2] == '/') and (metar[sm_loc-4] == ' ') and (metar[sm_loc-6] == ' ')): #if fraction and greater than 1.00
		whole = int(metar[sm_loc-5])
		num = int(metar[sm_loc-3])
		denom = int(metar[sm_loc-1])
		vis_val = float(whole + (float(num)/float(denom)))
	elif (metar[sm_loc-2] == '/') and ((metar[sm_loc-4] == ' ') or (metar[sm_loc-4] == 'M')) and (metar[sm_loc-6] != ' '): #if fraction and less than 1.00
		num = int(metar[sm_loc-3])
		denom = int(metar[sm_loc-1])	
		vis_val = float(num)/float(denom)
	else:
		vis_val = float(metar[sm_loc-2:sm_loc])
		
	#finding cloud ceiling
	#BKN cover
	BKN1 = metar.find("BKN")
	BKN2 = metar.find("BKN",BKN1+3)
	BKNV1 = 999
	BKNV2 = 999
	if(BKN1 > 0):
		BKNV1 = int(metar[BKN1+3:BKN1+6])
	if (BKN2 > 0):
		BKNV2 = int(metar[BKN2+3:BKN2+6])

	#OVC cover
	OVC1 = metar.find("OVC")
	OVC2 = metar.find("OVC",OVC1+3)
	OVCV1 = 999
	OVCV2 = 999

	if (OVC1 > 0):
		OVCV1 = int(metar[OVC1+3: OVC1+6])
	if (OVC2 > 0):
		OVCV2 = int(metar[OVC2+3: OVC2+6])

	ceiling = 0
	if((BKNV1 < BKNV2) and (BKNV1 < OVCV1) and (BKNV1 < OVCV2)):
		ceiling = BKNV1
	elif((BKNV2 < BKNV1) and (BKNV2 < OVCV1) and (BKNV2 < OVCV2)):
		ceiling = BKNV2
	elif((OVCV1 < BKNV1) and (OVCV1 < BKNV2) and (OVCV1 < OVCV2)):
		ceiling = OVCV1
	elif((OVCV2 < BKNV1) and (OVCV2 < OVCV1) and (OVCV2 < BKNV2)):
		ceiling = OVCV1
	else:
		ceiling = 999	


	if((ceiling < 5) or ( vis_val < 1.00)):
		textColor = magenta
	elif((ceiling < 10 and ceiling >= 5) or (vis_val < 3.00 and vis_val >= 1.00)):
		textColor = red
	elif((ceiling <= 30 and ceiling >= 10) or (vis_val <= 5.00 and vis_val >= 3.00)):
		textColor = blue
	else:
		textColor = green


	counter = 0
        while True:
		offscreenCanvas.Clear()
            	len = graphics.DrawText(offscreenCanvas, font, pos, 13, textColor, metar)
            	pos -= 1
            	if (pos + len < 0):
                	pos = offscreenCanvas.width

            	time.sleep(0.09)
            	offscreenCanvas = self.matrix.SwapOnVSync(offscreenCanvas)
		counter = counter + 1
#		print(counter)
		if counter == 6666:
			counter = 0
			offscreenCanvas.Clear()
#			self.matrix.SwapOnVSync(offscreenCanvas)
#			graphics.DrawText(offscreenCanvas, font, 0, 10, textColor, "UPDATING WX")
#			self.matrix.SwapOnVSync(offscreenCanvas)
#			time.sleep(5)
			break
			
# Main function
if __name__ == "__main__":
    while True:
	parser = RunText()
    	if (not parser.process()):
        	parser.print_help()

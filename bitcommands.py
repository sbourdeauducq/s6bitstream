#!/usr/bin/python

import sys

def hexdump(data, desc):
	sys.stdout.write("%-55s" % desc)
	sys.stdout.write("[")
	for c in data:
		sys.stdout.write("%02x" % ord(c))
	sys.stdout.write("]\n")

def str2word(s):
	return (ord(s[0]) << 8) | ord(s[1])

decode_op = ("NOP", "READ", "WRITE", "?")
decode_reg = ("CRC", "FAR_MAJ", "FAR_MIN", "FDRI", "FDRO", "CMD", "CTL", "MASK", "STAT", "LOUT", "COR1", "COR2", "PWRDN_REG", "FLR", "IDCODE", "CWDT", "HC_OPT_REG", "CSBO", "UNKNOWN", "GENERAL1", "GENERAL2", "GENERAL3", "GENERAL4", "GENERAL5", "MODE_REG", "PU_GWE", "PU_GTS", "MFWR", "CCLK_FREQ", "SEU_OPT", "EXP_SIGN", "RDBK_SIGN", "BOOTSTS", "EYE_MASK", "CBC_REG")
decode_cmd = ("NULL", "WCFG", "MFW", "LFRM", "RCFG", "START", "UNKNOWN", "RCRC", "AGHIGH", "UNKNOWN", "GRESTORE", "SHUTDOWN", "UNKNOWN", "DESYNC", "REBOOT")

def main():
	f = open(sys.argv[1], 'rb')

	sync = f.read(20)
	if sync != "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xaa\x99\x55\x66":
		print "Invalid sync"
		sys.exit()
	
	print "Sync OK"
	
	far_val = 0
	
	while 1:
		pstr = f.read(2)
		if pstr == "":
			sys.exit()
		pword = str2word(pstr)
		ptype = (pword & 0x7000) >> 13
		operation = (pword & 0x1800) >> 11;
		regaddr = (pword & 0x07e0) >> 5;
		if ptype == 1:
			wcount = (pword & 0x001f);
			if operation != 0:
				hexdump(pstr, "Type 1 %s %s: %d words (%d bits)" % (decode_op[operation], decode_reg[regaddr], wcount, wcount*16))
			else:
				hexdump(pstr, "Type 1 NOP")
			for i in range(wcount):
				pstr = f.read(2)
				pword = str2word(pstr)
				if regaddr == 1:
					far_val = (far_val << 16) | pword
				if regaddr == 5:
					hexdump(pstr, "    %s" % decode_cmd[pword])
				else:
					hexdump(pstr, "    word %d" % i)
		elif ptype == 2:
			hexdump(pstr, "Type 2 %s %s" % (decode_op[operation], decode_reg[regaddr]))
			pstr = f.read(4)
			wcount = (ord(pstr[0]) << 24) | (ord(pstr[1]) << 16) | (ord(pstr[2]) << 8) | ord(pstr[3])
			hexdump(pstr, "    T2 %d words (%d bits)" % (wcount, wcount*16))
			if regaddr == 3:
				print "    Initial FAR = %08x" % far_val
			for i in range(wcount):
				pstr = f.read(2)
				pword = str2word(pstr)
				hexdump(pstr, "        word %d" % i)
			pstr = f.read(4)
			hexdump(pstr, "CRC")
		else:
			hexdump(pstr, "Unknown");

	f.close()

main()


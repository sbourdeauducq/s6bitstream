#!/bin/sh

set -e

#TILE="CLEXL_X36Y11"
#SLICE="SLICE_X59Y11"

TILE=$1
SLICE=$2

function generate {
	cat > $1.xdl << EOF
design "$1.ncd" xc6slx45fgg484-2 v3.2 ;
inst "\$COMP_5" "SLICEX",placed $TILE $SLICE  ,
  cfg " A5FFSRINIT::#OFF A5LUT::#OFF A6LUT::#OFF AFF::#OFF AFFMUX::#OFF
       AFFSRINIT::#OFF AOUTMUX::#OFF AUSED::#OFF B5FFSRINIT::#OFF B5LUT::#OFF
       B6LUT::#OFF BFF::#OFF BFFMUX::#OFF BFFSRINIT::#OFF BOUTMUX::#OFF
       BUSED::#OFF C5FFSRINIT::#OFF C5LUT::#OFF C6LUT::#OFF CEUSED::#OFF
       CFF::#OFF CFFMUX::#OFF CFFSRINIT::#OFF CLKINV::#OFF COUTMUX::#OFF
       CUSED::#OFF D5FFSRINIT::#OFF D5LUT::#OFF D6LUT:$COMP_5.D6LUT:#LUT:O6=$2
       DFF::#OFF DFFMUX::#OFF DFFSRINIT::#OFF DOUTMUX::#OFF DUSED::0 SRUSED::#OFF
       SYNC_ATTR::#OFF "
  ;
net "\$NET_0" , 
  outpin "\$COMP_5" D ,
  inpin "\$COMP_5" D1 ,
  inpin "\$COMP_5" D2 ,
  inpin "\$COMP_5" D3 ,
  inpin "\$COMP_5" D4 ,
  inpin "\$COMP_5" D5 ,
  inpin "\$COMP_5" D6 ;
EOF
	xdl -xdl2ncd $1.xdl > /dev/null 2>&1
	par -p -w $1.ncd $1-routed.ncd > /dev/null 2>&1
}

generate "b0" "A1+A2+A3+A4+A5+A6"
bitgen -w b0-routed.ncd > /dev/null 2>&1
generate "b1" "A1+A2+A3+A4+A5+~A6"
bitgen -w -g Binary:Yes -r b0-routed.bit b1-routed.ncd diff.bit > /dev/null 2>&1
./bitcommands.py diff.bin | grep "Initial FAR"

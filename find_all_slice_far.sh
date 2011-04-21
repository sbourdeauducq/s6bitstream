#!/bin/sh
while read line
do
	echo -n $line
	./find_slice_far.sh $line
done < "slices.txt"

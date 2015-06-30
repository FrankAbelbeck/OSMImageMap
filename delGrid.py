#!/usr/bin/env python
"""
delGrid.py: remove meridians/parallels guide lines from an Inkscape SVG file
Copyright (C) 2015 Frank Abelbeck <frank.abelbeck@googlemail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys,os,argparse,math
import xml.dom.minidom

if __name__ == "__main__":
	
	# obtain basic program path information
	progpath = os.path.realpath(os.path.abspath(sys.argv[0]))
	progdir,progname = os.path.split(progpath)

	# setup argument parser and parse commandline arguments
	parser = argparse.ArgumentParser(
		description="Remove guide lines for meridians/parallels from an Inkscape SVG file."
	)
	parser.add_argument("FILE",help="name of the SVG file")
	args = parser.parse_args()
	
	# parse SVG XML document
	svg = xml.dom.minidom.parse(args.FILE)
	namedview = svg.getElementsByTagName("sodipodi:namedview")[0]
	
	# remove all sodipodi:guide elements with an meridian/parallel id
	i = 0
	for guide in namedview.getElementsByTagName("sodipodi:guide"):
		guideid = guide.getAttribute("id")
		if guideid.startswith("meridian") or guideid.startswith("parallel"):
			x,y = [float(i) for i in guide.getAttribute("position").split(",")]
			if x == 0:
				pos = y
			else:
				pos = x
			print("Removing guide for {0} {1}° at {2}".format(guideid[0:8],guideid[8:],pos))
			namedview.removeChild(guide)
			i = i + 1
	
	# write back XML
	with open(args.FILE,"w") as f: svg.writexml(f)
	
	if i == 0:
		print("No guides for meridians/parallels found.")
	elif i == 1:
		print("One guide removed.")
	else:
		print("{0} guides removed.".format(i))
	
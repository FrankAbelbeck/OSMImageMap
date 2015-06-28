#!/usr/bin/env python

import sys,os,argparse,math
import xml.dom.minidom
import OSMTools

if __name__ == "__main__":
	
	# obtain basic program path information
	progpath = os.path.realpath(os.path.abspath(sys.argv[0]))
	progdir,progname = os.path.split(progpath)

	# setup argument parser and parse commandline arguments
	parser = argparse.ArgumentParser(
		description="Insert grid lines for parallels/meridians into a blank SVG containing a map image."
	)
	parser.add_argument("--steps",default=1,type=float,help="number of steps between integer meridians/parallels [float]")
	parser.add_argument("--special",action='store_true',help="add visible topics and polar circles (special parallels)")
	parser.add_argument("ZOOM",type=int,help="zoom factor (0..18)")
	parser.add_argument("X0",type=int,help="upper left tile (x coordinate)")
	parser.add_argument("Y0",type=int,help="upper left tile (y coordinate)")
	parser.add_argument("NX",type=int,help="width of map (number of tiles)")
	parser.add_argument("NY",type=int,help="height of map (number of tiles)")
	parser.add_argument("FILE",help="name of the SVG file")
	args = parser.parse_args()
	
	# parse SVG XML document
	svg = xml.dom.minidom.parse(args.FILE)
	
	h_doc = float(svg.getElementsByTagName("svg")[0].getAttribute("height"))
	
	# extract SVG XML elements:
	#   named view -- contains grid line definitions, first in list
	#   image      -- get first image and assume it is the map
	namedview = svg.getElementsByTagName("sodipodi:namedview")[0]
	image     = svg.getElementsByTagName("image")[0]

	# extract image data with respect to different coordinate systems
	#
	# SVG coordinate system: upper left corner, right/down
	#
	# guides are an Inkscape extension and follow Inkscape's coordinate system:
	# lower left corner, right/up
	x         = float(image.getAttribute("x"))
	y         = float(image.getAttribute("y"))
	width     = float(image.getAttribute("width"))
	height    = float(image.getAttribute("height"))
	
	print("potential map image at x={0} y={1} w={2} h={3}".format(x,y,width,height))
	
	lon0 = OSMTools.x_to_lon(args.X0,args.ZOOM)
	lat0 = OSMTools.y_to_lat(args.Y0,args.ZOOM)
	lon1 = OSMTools.x_to_lon(args.X0+args.NX,args.ZOOM)
	lat1 = OSMTools.y_to_lat(args.Y0+args.NY,args.ZOOM)
	
	#
	# prepare lists of meridians and parallels
	#
	
	stepsize = 1/args.steps
	special_meridians = (OSMTools.PRIME_MERIDIAN,)
	special_parallels = (OSMTools.ARCTIC_CIRCLE,OSMTools.TROPIC_CANCER,OSMTools.EQUATOR,OSMTools.TROPIC_CAPRICORN,OSMTools.ANTARCTIC_CIRCLE)
	
	# build meridians list; depends on map boundaries, stepsize and (optional) special meridians
	meridians = list()
	med = math.ceil(lon0*args.steps)/args.steps # round to nearest fraction inside map (round up)
	medend = math.floor(lon1*args.steps)/args.steps # round to nearest fraction inside map (round down)
	while med <= medend:
		meridians.append(med)
		# check if special guides should be inserted
		if args.special == True:
			# yes, check if we would miss such a special longitude
			for specmed in special_meridians:
				if med < specmed < med + stepsize and specmed < medend:
					meridians.append(specmed)
		med = med + stepsize
		# correct near-zero imprecision of floats
		if med > -1e-10 and med < 1e-10: med = 0
	
	# build parallels list; depends on map boundaries, stepsize and (optional) special parallels
	parallels = list()
	par = math.floor(lat0*args.steps)/args.steps # round to nearest fraction inside map (round down)
	parend = math.ceil(lat1*args.steps)/args.steps # round to nearest fraction inside map (round up)
	while par >= parend:
		parallels.append(par)
		# check if special guides should be inserted
		if args.special == True:
			# yes, check if we would miss such a special latitude
			for specpar in special_parallels:
				if par > specpar > par - stepsize and specpar > parend:
					parallels.append(specpar)
		par = par - stepsize
		# correct near-zero imprecision of floats
		if par > -1e-10 and par < 1e-10: par = 0
	
	# avoid multiple guide instances: record all present guides:
	existing_guides = list()
	for guide in namedview.getElementsByTagName("sodipodi:guide"):
		existing_guides.append(guide.getAttribute("id"))
	
	# iterate over meridians list...
	for lon in meridians:
		# calculate position and id
		guide_pos = x + (OSMTools.lon_to_x(lon,args.ZOOM) - args.X0) * width / args.NX
		guide_id  = "meridian{0}".format(lon)
		
		# check if guide is already present (id in use)
		if guide_id not in existing_guides:
			# create Inkscape guide element, populate it and append it to the
			# named view of the SVG document
			guide = svg.createElement("sodipodi:guide")
			guide.setAttribute("id",guide_id)
			guide.setAttribute("orientation","1,0")
			guide.setAttribute("position","{0},{1}".format(guide_pos,0))
			namedview.appendChild(guide)
			print("added guide for meridian={0}° at x={1}".format(lon,guide_pos))
		else:
			print("skipping already existing guide for meridian={0}°".format(lon))
	
	# iterate over parallels list...
	for lat in parallels:
		# calculate position and id; flip y coordinate because guides are an
		# extension by Inkscape which uses a different coordinate system...
		guide_pos = h_doc - (y + (OSMTools.lat_to_y(lat,args.ZOOM) - args.Y0) * height / args.NY)
		guide_id = "parallel{0}".format(lat)
		
		# check if guide is already present (id in use)
		if guide_id not in existing_guides:
			# create Inkscape guide element, populate it and append it to the
			# named view of the SVG document
			guide = svg.createElement("sodipodi:guide")
			guide.setAttribute("id",guide_id)
			guide.setAttribute("orientation","0,1")
			guide.setAttribute("position","{0},{1}".format(0,guide_pos))
			namedview.appendChild(guide)
			print("added guide for parallel={0}° at y={1}".format(lat,guide_pos))
		else:
			print("skipping already existing guide for parallel={0}°".format(lat))
	
	# write back XML
	with open(args.FILE,"w") as f: svg.writexml(f)
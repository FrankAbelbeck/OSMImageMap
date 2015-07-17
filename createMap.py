#!/usr/bin/env python
"""
createMap.py: create a large map image from tile images
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

# My sources of inspiration:
#  - https://github.com/sjev/mapCreator
#  - https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

import sys,os,argparse,time
import OSMTools
import urllib.request,urllib.parse
import PIL.Image


def scaleBytes(n):
	if n > 2**40: #1649267441664:
		num,unit = n / 2**40,"TiB"
	elif n > 2**30: #1610612736:
		num,unit = n / 2**30,"GiB"
	elif n > 2**20: #1572864:
		num,unit = n / 2**20,"MiB"
	elif n > 2**10: #1536:
		num,unit = n / 2**10,"kiB"
	else:
		num,unit = n,"B"
	return "{:.2f}".format(num).rstrip("0").rstrip("."),unit


if __name__ == "__main__":
	
	# obtain basic program path information
	progpath = os.path.realpath(os.path.abspath(sys.argv[0]))
	progdir,progname = os.path.split(progpath)
	
	cachedefault = os.path.join(progdir,"cache")
	
	# setup argument parser and parse commandline arguments
	parser = argparse.ArgumentParser(
		description="Create a raster map from OpenStreetMap tiles.",
		epilog="Note: Besides a tile server URL scheme like 'http://hostname.tld/{z}/{x}/{y}.png', the keywords 'osm' (openstreetmap.de), 'topo' (opentopomap.org), 'sat' (maquest aerial), 'cycle' (opencyclemap.org), tonerhybrid (stamen.com) or 'hybrid' (openmapsurfer.org) are accepted, too."
	)
	parser.add_argument("--source",default="osm",help="URL scheme of a tile server; cf. note below")
	parser.add_argument("--cache",default=cachedefault,help="directory of the tile cache; default: "+cachedefault)
	parser.add_argument("--delay",type=float,help="time in seconds between downloads")
	parser.add_argument("--quality",default=90,type=int,help="JPEG quality factor (integer, 0..95, default={0})".format(90))
	parser.add_argument("--compression",default=9,type=int,help="PNG compression level (integer, 0..9, default={0})".format(9))
	parser.add_argument("--infofile",help="write map information text to file INFOFILE")
	parser.add_argument("ZOOM",type=int,help="zoom factor (0..18)")
	parser.add_argument("WEST",type=float,help="western boundary of the map (longitude in degrees)")
	parser.add_argument("NORTH",type=float,help="northern boundary of the map (latitude in degrees)")
	parser.add_argument("EAST",type=float,help="eastern boundary of the map (longitude in degrees)")
	parser.add_argument("SOUTH",type=float,help="southern boundary of the map (latitude in degrees)")
	parser.add_argument("FILE",help="name of the output image file")
	args = parser.parse_args()
	
	# make sure cache directory exists
	if not os.path.exists(args.cache): os.mkdir(args.cache)
	
	# check tile server url ("source")
	if args.source == "osm":
		source = "http://tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png"
	elif args.source == "topo":
		source = "http://opentopomap.org/{z}/{x}/{y}.png"
	elif args.source == "sat":
		source = "http://otile1.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.jpg"
	elif args.source == "cycle":
		source = "http://a.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png"
	elif args.source == "tonerhybrid":
		source = "http://a.tile.stamen.com/toner-hybrid/{z}/{x}/{y}.png"
	elif args.source == "hybrid":
		source = "http://korona.geog.uni-heidelberg.de/tiles/hybrid/x={x}&y={y}&z={z}"
	else:
		source = args.source
		try:
			source.format(z=1,x=2,y=3)
		except IndexError:
			print("Invalid source URL provided!")
			sys.exit(1)
	
	# check bounding box values
	if args.EAST <= args.WEST or args.NORTH <= args.SOUTH:
		print("Invalid bounding box values! Required: WEST < EAST and SOUTH < NORTH")
		sys.exit(1)
	
	# check zoom factor
	if args.ZOOM < 0 or args.ZOOM > 18:
		print("Invalid zoom factor!")
		sys.exit(1)
	
	# upper left corner of map
	x0 = int(OSMTools.lon_to_x(args.WEST,args.ZOOM))
	y0 = int(OSMTools.lat_to_y(args.NORTH,args.ZOOM))
	
	# lower right corner of map
	# (i.e. lower right tile next to the one which contains EAST/SOUTH -> +1)
	x1 = int(OSMTools.lon_to_x(args.EAST, args.ZOOM))+1
	y1 = int(OSMTools.lat_to_y(args.SOUTH,args.ZOOM))+1
	
	tiles = [(args.ZOOM,x,y) for x in range(x0,x1) for y in range(y0,y1)]
	n     = len(tiles)
	
	# calculate image dimensions based on the standard 256x256 tile
	w = (x1 - x0) * 256
	h = (y1 - y0) * 256
	
	# open map image file
	img = PIL.Image.new("RGBA",(w,h))
	
	# iterate over tiles
	dfiles = 0
	dbytes = 0
	for i,(zoom,x,y) in enumerate(tiles):
		
		# parse tile URL
		url = source.format(z=zoom,x=x,y=y)
		scheme,hostname,path,params,query,fragment = urllib.parse.urlparse(url)
		pathname = os.path.join(args.cache,hostname,path[1:])
		
		# check if tile is already cached; download it otherwise
		if os.path.exists(pathname):
			print("{0}: {1}/{2} cached, skipping.".format(url,i+1,n))
		else:
			print("{0}: {1}/{2} downloading...".format(url,i+1,n),end="")
			dirname,filename = os.path.split(pathname)
			os.makedirs(dirname,exist_ok=True)
			# control download rate
			try:
				time.sleep(args.delay)
			except TypeError: # invalid delay, i.e. not specified: ignore
				pass
			
			try:
				imgbytes = urllib.request.urlopen(url).read()
				if len(imgbytes) == 0:
					raise TypeError
				
				with open(pathname,"wb") as f:
					f.write(imgbytes)
				print(" done ({0} {1})".format(*scaleBytes(len(imgbytes))))
				dbytes = dbytes + len(imgbytes)
				dfiles = dfiles + 1
			except urllib.error.URLError:
				print(" request failed!")
			except TypeError:
				print(" no data was received!")
			except ConnectionResetError:
				print(" connection reset by peer!")
		
		# load tile image
		try:
			tileimg = PIL.Image.open(pathname)
			# paste tile image to map image
			img.paste(tileimg, (256 * (x - x0), 256 * (y - y0)))
		except FileNotFoundError:
			print("Error: tile zoom={zoom} x={x} y={y} not found!".format(zoom=zoom,x=x,y=y))
			sys.exit(1)
	
	# end of tile stitching
	
	# print download statistics
	if dfiles == 0:
		print("No files were downloaded.")
	else:
		if dfiles == 1:
			dfilestr = "One file"
		else:
			dfilestr = "{0} files".format(dfiles)
		print("Downloads: {0}, {1} {2}".format(dfilestr,*scaleBytes(dbytes)))
	
	# save map image file
	# unrecongnised parameters are silently ignored, so both JPEG and PNG
	# quality parameters are provided...
	img.save(args.FILE,quality=args.quality,compress_level=args.compression)
	
	# calculate resolution
	resolution = "   latitude     resolution\n"
	latstep = (args.NORTH - args.SOUTH) / 5
	for i in range(0,6):
		lat = args.SOUTH + i * latstep
		res = OSMTools.resolution(args.ZOOM,lat)
		unit = 1
		while unit/res < 1: unit = unit * 10
		resolution = resolution + "   {0:8.5f}°    {1:.5f} m/px   {2:.5f} px/{3}m\n".format(lat,res,unit/res,unit)
	
	# prepare map information output
	mapinfo = """----- Begin Map Image Information -----
createMap Command Parameters:
   {14}

General
   filename     {0}
   zoom         {1}
   dimensions   {2}x{3}

Coordinates (Longitude,Latitude)
   upper left corner    {4},{5}
   lower right corner   {6},{7}

Tiles (x,y)
   upper left tile    {8},{9}
   lower right tile   {10},{11}
   number of tiles    {12}x{13}

Resolution/Map Scale
{15}

addGrid Parameters
   {1} {8} {9} {12} {13}
----- End Map Image Information -----
""".format(
		args.FILE,
		args.ZOOM,
		w,h,
		OSMTools.x_to_lon(x0,args.ZOOM),OSMTools.y_to_lat(y0,args.ZOOM),
		OSMTools.x_to_lon(x1,args.ZOOM),OSMTools.y_to_lat(y1,args.ZOOM),
		x0,y0,
		x1-1,y1-1,
		x1-x0,y1-y0,
		" ".join(sys.argv[1:]),
		resolution
	)
	
	print(mapinfo)
	if args.infofile != None:
		# user requested info should be written to file
		with open(args.infofile,"w") as f:
			f.write(mapinfo)
	

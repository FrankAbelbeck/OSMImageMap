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


if __name__ == "__main__":
	
	# obtain basic program path information
	progpath = os.path.realpath(os.path.abspath(sys.argv[0]))
	progdir,progname = os.path.split(progpath)
	
	cachedefault = os.path.join(progdir,"cache")
	
	# setup argument parser and parse commandline arguments
	parser = argparse.ArgumentParser(
		description="Create a raster map from OpenStreetMap tiles.",
		epilog="SOURCE may Instead of a tile server URL, the keywords 'osm' (openstreetmap.de), 'topo' (opentopomap.org) or 'sat' (maquest aerial) are accepted."
	)
	parser.add_argument("--source",default="osm",help="URL of a tile server (akin 'http://name.tld/{0}/{1}/{2}.png'); alternatively, bookmark keywords 'osm' (openstreetmap.de; default), 'topo' (opentopomap.org) or 'sat' (maquest aerial) may be used.")
	parser.add_argument("--cache",default=cachedefault,help="directory of the tile cache; default: "+cachedefault)
	parser.add_argument("--delay",type=float,help="time in seconds between downloads")
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
		source = "http://tile.openstreetmap.de/tiles/osmde/{0}/{1}/{2}.png"
	elif args.source == "topo":
		source = "http://opentopomap.org/{0}/{1}/{2}.png"
	elif args.source == "sat":
		source = "http://otile1.mqcdn.com/tiles/1.0.0/sat/{0}/{1}/{2}.jpg"
	else:
		source = args.source
		try:
			source.format(1,2,3)
		except IndexError:
			print("Invalid source URL provided!")
			sys.exit(1)
	
	# check bounding box values
	if args.EAST <= args.WEST or args.NORTH <= args.SOUTH:
		print("Invalid bounding box values! Required: WEST < EAST and SOUTH < NORTH")
		sys.exit(1)
	
	# check zoom factor
	zoom = args.ZOOM
	if zoom < 0 or zoom > 18:
		print("Invalid zoom factor!")
		sys.exit(1)
	
	# upper left corner of map
	x0 = int(OSMTools.lon_to_x(args.WEST,zoom))
	y0 = int(OSMTools.lat_to_y(args.NORTH,zoom))
	
	# lower right corner of map
	x1 = int(OSMTools.lon_to_x(args.EAST,zoom))
	y1 = int(OSMTools.lat_to_y(args.SOUTH,zoom))
	
	tiles = [(zoom,x,y) for x in range(x0,x1) for y in range(y0,y1)]
	n     = len(tiles)
	
	# calculate image dimensions based on the standard 256x256 tile
	w = (x1 - x0) * 256
	h = (y1 - y0) * 256
	
	# open map image file
	img = PIL.Image.new("RGB",(w,h))
	
	# iterate over tiles
	for i,tile in enumerate(tiles):
		
		# parse tile URL
		url = source.format(*tile)
		scheme,hostname,path,params,query,fragment = urllib.parse.urlparse(url)
		pathname = os.path.join(args.cache,hostname,path[1:])
		
		# check if tile is already cached; download it otherwise
		if os.path.exists(pathname):
			print("{0}: {1}/{2} cached, skipping".format(url,i,n))
		else:
			print("{0}: {1}/{2} downloading...".format(url,i,n),end="")
			dirname,filename = os.path.split(pathname)
			os.makedirs(dirname,exist_ok=True)
			# control download rate
			try:
				time.sleep(float(args.delay))
			except:
				pass # no valid delay specified: ignore
			imgbytes = urllib.request.urlopen(url,timeout=5).read()
			with open(pathname,"wb") as f:
				f.write(imgbytes)
			print(" done")
		
		# load tile image
		tileimg = PIL.Image.open(pathname)
		
		# paste tile image to map image
		img.paste(tileimg, (256 * (tile[1] - x0), 256 * (tile[2] - y0)))
		
	
	# save map image file
	img.save(args.FILE)

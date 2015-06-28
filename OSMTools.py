#!/usr/bin/env python
"""
OSMTools.py: collection of helper functions for latitude/longitude calculations
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

#
# source of formulae: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#

import math


def lat_to_y(lat,zoom):
	"""Calculates the y tile coordinate of given latitude at given zoom level.

Args:
	lat  - latitude given in degrees (float; <0 south of equator)
	zoom - zoom level (integer, 0..18)

Returns:
	a float

Raises:
	ValueError - latitude out of range (-90 < lat < 90)"""
	return 2**(zoom-1) * (1 - math.log(math.tan(math.radians(lat)) + (1 / math.cos(math.radians(lat)))) / math.pi)


def lon_to_x(lon,zoom):
	"""Calculates the x tile coordinate of given longitude at given zoom level.

Args:
	lon  - longitude given in degrees (float; <0 west of equator)
	zoom - zoom level (integer, 0..18)

Returns:
	a float"""
	return 2**zoom * (lon + 180) / 360


def y_to_lat(y,zoom):
	"""Calculates the latitude corresponding to given y coordinate and zoom level.

Args:
	y    - y tile coordinate (float)
	zoom - zoom level (integer, 0..18)

Returns:
	a float

Raises:
	OverflowError - y value out of range."""
	return math.degrees(math.atan(math.sinh(math.pi - 2*math.pi*y/2**zoom)))


def x_to_lon(x,zoom):
	"""Calculates the x tile coordinate of given longitude at given zoom level.

Args:
	lon  - longitude given in degrees (float; <0 west of equator)
	zoom - zoom level (integer, 0..18)

Returns:
	a float"""
	return x*360/2**zoom - 180


TROPIC_CANCER    =  (23 + 26/60 + 14.2/3600) # status 2015-06-23, see https://en.wikipedia.org/wiki/Tropic_of_Cancer
TROPIC_CAPRICORN = -(23 + 26/60 + 14.2/3600) # status 2015-06-24, see https://en.wikipedia.org/wiki/Tropic_of_Capricorn
ARCTIC_CIRCLE    =  (66 + 33/60 + 45.8/3600) # status 2015-06-24, see https://en.wikipedia.org/wiki/Arctic_Circle
ANTARCTIC_CIRCLE = -(66 + 33/60 + 45.8/3600) # status 2015-06-24, see https://en.wikipedia.org/wiki/Antarctic_Circle
EQUATOR          = 0
PRIME_MERIDIAN   = 0


def tropic_of_cancer(zoom):
	"""Calculates the y coordinate of the Tropic of Cancer at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the y tile coordinate"""
	return lat_to_y(TROPIC_CANCER,zoom)


def tropic_of_capricorn(zoom):
	"""Calculates the y coordinate of the Tropic of Capricorn at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the y tile coordinate"""
	return lat_to_y(TROPIC_CAPRICORN,zoom)


def arctic_circle(zoom):
	"""Calculates the y coordinate of the Artic Circle at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the y tile coordinate"""
	return lat_to_y(ARCTIC_CIRCLE,zoom)


def antarctic_circle(zoom):
	"""Calculates the y coordinate of the Antartic Circle at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the y tile coordinate"""
	return lat_to_y(ANTARCTIC_CIRCLE,zoom)


def equator(zoom):
	"""Calculates the y coordinate of the Equator at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the y tile coordinate"""
	return lat_to_y(EQUATOR,zoom)


def prime_meridian(zoom):
	"""Calculates the x coordinate of the Prime Meridian at given zoom level.

Args:
	zoom - zoom level (integer, 0..18)

Returns:
	a float with the x tile coordinate"""
	return lat_to_y(PRIME_MERIDIAN,zoom)


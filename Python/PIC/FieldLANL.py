#    Copyright (C) 2014  Jian-Ming Tang <jmtang@mailaps.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy
import struct


class FieldLANL:
	"""
	This class is used to store data in ndarray from LANL PIC data files.
	"""
	def __init__(self, datafiles, grid, time):
		"""
		datafiles: dict of full filenames
		grid: numbers of grid points
		"""
		nx = grid[0]
		nz = grid[2]
		self.data = {}
		skip = (nx * nz + 2) * 4 * (time - 1)
		datatype = numpy.dtype( [('field','f4',(nz,nx))] )
		for k in datafiles:
			print 'Reading ' + datafiles[k] + ' ...'
			f = open(datafiles[k])
			f.seek(skip)
			self.data[k] = (numpy.fromfile(f, datatype))[0][0]
			f.close()

	def __getitem__(self, key):
		return self.data[key]

	def read_from_info(info_file):
		grid = []
		L = []
		f = open(info_file, 'rb')
		f.read(4)
		for i in range(3):
			# Python 3:
			# grid.append(int.from_bytes(f.read(4),
			#	byteorder='little'))
			grid.append(struct.unpack('<I',f.read(4))[0])
		f.read(4)
		f.read(4)
		for i in range(3):
			L.append(struct.unpack('<f',f.read(4))[0])
		f.close()
		return grid, L

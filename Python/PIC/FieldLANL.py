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

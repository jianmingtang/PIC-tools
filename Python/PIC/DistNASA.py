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
"""
Distribution
------------
"""


import numpy


class DistNASA:
	"""
	This class is used to store data in ndarray from a NASA PIC data file.
	Methods for data slicing and summation are provided.
	"""
	data_t = {}
	def __init__(self, fname, grid, nss=4):
		"""
		fname: data filename
		grid: number of grid points
		nss: number of species
		"""
		self.grid = grid
		self.nss = nss
		datatype = numpy.dtype([
			('pad1','i4'),
			('axes','f4',(nss,grid)),
			('xlo','f4'), ('xhi','f4'), ('zlo','f4'),('zhi','f4'),
			('ic','i4',(nss,)),
			('fxyz','f4',(nss,grid,grid,grid)),
			('fxy','f4',(nss,grid,grid)),
			('fxz','f4',(nss,grid,grid)),
			('fyz','f4',(nss,grid,grid)),
			('vxa','f4',(nss,)),
			('vya','f4',(nss,)),
			('vza','f4',(nss,)),
			('pad2','i4')
			])
		self.data = numpy.fromfile(fname, datatype)[0]
		self.truncate([0,grid])

	def __getitem__(self, key):
		return self.data_t[key]

	def __str__(self):
		"""
		"""
		s = '\n'
		s += 'Bin location: '
		s += 'x=(%4g,%4g), z=(%4g,%4g)\n' % (
			self.data['xlo'], self.data['xhi'],
			self.data['zlo'], self.data['zhi'])
# This is broken due to truncation
# This is hard coded to species 1
#		s += '(Hard coded) Axes max: %4g\n' % self['axes'][1][-1]
#		s += '\n'
#		for i in range(self.nss):
#			s += 'v['+str(i)+'] = ({0:g}, {1:g}, {2:g})\n'.format(
#				self['vxa'][i], self['vya'][i], self['vza'][i])
		return s

	def truncate(self, r):
		""" We do basic slicing here, so that no copies are made.
		"""
		b = r[0]
		e = r[1]
		for k in ['fxy','fxz','fyz']:
                        self.data_t[k] = self.data[k][:,b:e,b:e]
                self.data_t['fxyz'] = self.data['fxyz'][:,b:e,b:e,b:e]
		self.data_t['axes'] = self.data['axes'][:,b:e]
#		print help(dict(self.data))
#		print self.data.has_key('cut')
#		if self.data.has_key('cut'):
#			self.data_t['cut'] = self.data['cut'][:,b:e,b:e]

	def cut(self, p):
		"""
		Cut out a 2D slice from the 3D data
		p = [dir,rmin,rmax]
		"""
		rmin = int(p[1])
		rmax = int(p[2])
		A = self['fxyz']
		if p[0] == 'x':
			self.dataCUT = A[:,:,:,rmin]
			for i in range(rmin+1,rmax+1):
				self.dataCUT += A[:,:,:,i]
		elif p[0] == 'y':
			self.dataCUT = A[:,:,rmin,:]
			for i in range(rmin+1,rmax+1):
				self.dataCUT += A[:,:,i,:]
		elif p[0] == 'z':
			self.dataCUT = A[:,rmin,:,:]
			for i in range(rmin+1,rmax+1):
				self.dataCUT += A[:,i,:,:]
		else:
			raise IndexError
		self.data['cut'] = self.dataCUT

	def _check_add(self, sps):
		# Check the ranges of velocities are consistent.
		allowed_error = [1.e-6] * self.grid 
		self.axes = self['axes'][int(sps[0])]
		for s in sps[1:]:
			diff = self['axes'][int(s)] - self.axes
			if numpy.any(diff > allowed_error):
				print addset, ' cannot be combined!!!'
				raise IndexError

	def add2D(self, sps):
		"""
		Combine species for a 2D slice
		sps = [s1,s2,...]
		"""
		self._check_add(sps)
		self.data2D = self.dataCUT[int(sps[0])]
		for s in sps[1:]:
			self.data2D += self.dataCUT[int(s)]

	def add_reduced(self, sps):
		"""
		Combine species for reduced data sets
		sps = [s1,s2,...]
		"""
		self._check_add(sps)
		self.dataR = {}
		for f in ['fxy', 'fxz', 'fyz']:
			self.dataR[f] = self[f][int(sps[0])]
			for s in sps[1:]:
				self.dataR[f] += self[f][int(s)]

	def add3D(self, sps):
		"""
		Combine species for 3D data
		sps = [s1,s2,...]
		"""
		self._check_add(sps)
		self.data3D = self['fxyz'][int(sps[0])]
		for s in sps[1:]:
			self.data3D += self['fxyz'][int(s)]

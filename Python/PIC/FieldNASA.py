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


class FieldNASA:
	""" This class is used to store field data in ndarray from
	NASA PIC simulations.
	"""
	quadlist = ['vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']
	singlelist = ['Bx','By','Bz','Ex','Ey','Ez']
	fieldlist = singlelist + quadlist
	data_t = {}

	def __init__(self, fname, nss=4):
		""" fname: PIC field data filename
		"""
		datatype = numpy.dtype([
			('pad1','i4'),
			('it','i4'),
			('dt','f4'), ('teti','f4'),
			('xmax','f4'),('zmax','f4'),
			('nnx','i4'), ('nnz','i4')
			])
		data = numpy.fromfile(fname, datatype)[0]
		nx = data['nnx']
		nz = data['nnz']
		datatype = numpy.dtype([
			('pad1','i4'),
			('it','i4'),
			('dt','f4'), ('teti','f4'),
			('xmax','f4'),('zmax','f4'),
			('nnx','i4'), ('nnz','i4'),
			('vxs','f4',(nss,nz,nx)),
			('vys','f4',(nss,nz,nx)),
			('vzs','f4',(nss,nz,nx)),
			('Bx','f4',(nz,nx)),
			('By','f4',(nz,nx)),
			('Bz','f4',(nz,nx)),
			('Ex','f4',(nz,nx)),
			('Ey','f4',(nz,nx)),
			('Ez','f4',(nz,nx)),
			('dns','f4',(nss,nz,nx)),
			('xe','f4',(nx,)),
			('ze','f4',(nz,)),
			('mass','f4',(nss,)),
			('q','f4',(nss,)),
			('time','f8'),
			('wpewce','f4'),
			('dfac','f4',(nss,)),
			('pxx','f4',(nss,nz,nx)),
			('pyy','f4',(nss,nz,nx)),
			('pzz','f4',(nss,nz,nx)),
			('pxy','f4',(nss,nz,nx)),
			('pxz','f4',(nss,nz,nx)),
			('pyz','f4',(nss,nz,nx)),
			('pad2','i4')
			])
		self.data = numpy.fromfile(fname, datatype)[0]
		self.truncate([0,nx,0,nz])

	def __getitem__(self, key):
		return self.data_t[key]

	def truncate(self, r):
		""" We do basic slicing here, so that no copies are made.
		"""
		for k in self.singlelist:
			self.data_t[k] = self.data[k][r[2]:r[3],r[0]:r[1]]
		for k in self.quadlist:
			self.data_t[k] = self.data[k][:,r[2]:r[3],r[0]:r[1]]
		self.data_t['xe'] = self.data['xe'][r[0]:r[1]]
		self.data_t['ze'] = self.data['ze'][r[2]:r[3]]

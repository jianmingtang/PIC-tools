#!/usr/bin/env python


#    draw_field.py:
#       Draw field data using matplotlib
#
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


import struct
import math
import numpy
import pylab
import argparse


class FieldLANL:
	"""
	This class is used to store data in ndarray from LANL PIC data files.
	"""
	def __init__(self, datafiles, grid, time):
		"""
		datafiles: dict of full filenames
		grid: numbers of grid points
		"""
		self.data = {}
		skip = (grid[0]*grid[2]+2)*4*(time-1)
		datatype = numpy.dtype( [('field','f4',(grid[2],grid[0]))] )
		for k in datafiles:
			print 'Reading ' + datafiles[k] + ' ...'
			f = open(datafiles[k])
			f.seek(skip)
			self.data[k] = (numpy.fromfile(f, datatype))[0][0]
			f.close()


class FieldNASA:
	"""
	This class is used to store data in ndarray from NASA PIC data files.
	"""
	def __init__(self, fname, nx, nz, nss=4):
		"""
		fname: data filename
		grid: number of grid points
		"""
		self.data = {}
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
#		fcomp = ('Bx','By','Bz','Ex','Ey','Ez',)
#		for k in fcomp:
#			self.data[k]

class Figure2D:
	"""
	This class creates and stores 2D plots using Matplotlib.
	"""
	def __init__(self):
		# self.fig stores a list of figure objects
		self.figs = []

	def add_one(self, name, fZ, L, grid):
		"""
		Create a 1-panel figure
		name: title of the figure
		X: 1D axes data
		fZ: 2D data set (Fortran indexing)
		"""
		title = name.replace(' ','_')
		self.figs.append((title,pylab.figure(title)))
		ax = pylab.subplot('111')
		X = numpy.linspace(0,L[0],grid[0])
		Y = numpy.linspace(0,L[2],grid[2])
		fX,fY = numpy.meshgrid(X,Y)
		pcm = ax.pcolormesh(fX, fY, fZ)
		ax.axis('tight')
		self.figs[-1][1].colorbar(pcm)
		pylab.title(name)

	def savefig(self):
		"""
		Save all figures in PNG format
		"""
		for fig in self.figs:
			fig[1].savefig(fig[0]+'.png',bbox_inches='tight')
			print fig[0] +' saved'


def read_from_info(info_file):
	grid = []
	L = []
	f = open(info_file, 'rb')
	f.read(4)
	for i in range(3):
# Python 3:
#		grid.append(int.from_bytes(f.read(4),byteorder='little'))
		grid.append(struct.unpack('<I',f.read(4))[0])
	f.read(4)
	f.read(4)
	for i in range(3):
		L.append(struct.unpack('<f',f.read(4))[0])
	f.close()
	return grid, L
	


### main program ###
if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description=
        	'Draw EM field at a given t')
	parser.add_argument('datapath', help='the data path')
	parser.add_argument('-s', dest='source',
		help='source of data (LANL or NASA)')
	parser.add_argument('--plot-B', action='store_false',
		help='plot B field')
	parser.add_argument('--plot-E', action='store_true',
		help='plot E field')
	parser.add_argument('-t', dest='time', default=1, type=int,
		help='make 2D plots')
	parser.add_argument('--grid',
		help='number of grid points')
	parser.add_argument('--save-png', action='store_true',
		help='save plots in png')
	args = parser.parse_args()


	if args.source == 'LANL':
		if args.plot_B:
			datafiles={'Bx':'Bx.gda','By':'By.gda','Bz':'Bz.gda'}
		if args.plot_E:
			datafiles={'Ex':'Ex.gda','Ey':'Ey.gda','Ez':'Ez.gda'}
		for k in datafiles:
			datafiles[k] = args.datapath + datafiles[k]
		if args.grid:
			grid = args.grid.strsplit(',')
		else:
			info_file = args.datapath + 'info'
			grid, L = read_from_info(info_file)

		emf = FieldLANL(datafiles, grid, args.time)
		time = str(args.time)

	if args.source == 'NASA':
		fname = args.datapath + 'fields-'
		nx = 1000
		nz = 800
		time = '{0:05d}'.format(args.time)
		fname = fname + time + '.dat'
		grid = [nx, 1, nz]
		L = [320., 0, 64.]
		emf = FieldNASA(fname,nx,nz)

	fig = Figure2D()
	if args.plot_B:
		fcomp = ['Bx','By','Bz']
	if args.plot_E:
		fcomp = ['Ex','Ey','Ez']
	for f in fcomp:
		fig.add_one(args.source+' '+f+' '+time, emf.data[f], L, grid)

	pylab.show()
	if args.save_png: fig.savefig()

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
import matplotlib.pyplot as plt
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


class FieldNASA:
	"""
	This class is used to store data in ndarray from NASA PIC data files.
	"""
	def __init__(self, fname, grid, nss=4):
		"""
		fname: data filename
		grid: number of grid points
		"""
		nx = grid[0]
		nz = grid[2]
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


class Figure2D:
	"""
	This class creates and stores 2D plots using Matplotlib.
	"""
	def __init__(self):
		# self.fig stores a list of figure objects
		self.figs = []

	def add_one(self, name, fZ, X, Y):
		"""
		Create a 1-panel figure
		name: title of the figure
		X: 1D axes data
		fZ: 2D data set (Fortran indexing)
		"""
		title = name.replace(' ','_')
		self.figs.append((title,pylab.figure(title)))
		fX,fY = numpy.meshgrid(X,Y)
		pcm = pylab.pcolormesh(fX, fY, fZ)
		pylab.xlabel('X (de)')
		pylab.ylabel('Z (de)')
		pylab.axis('tight')
		self.figs[-1][1].colorbar(pcm)
		pylab.title(name)

	def add_streamline(self, X, Y, U, V):
		plt.streamplot(X,Y,U,V,color='k',density=[5,0.7])

	def add_vectors(self, X, Y, U, V):
		Q = plt.quiver(X[::50],Y[::50],U[::50,::50],V[::50,::50],pivot='mid',color='k')

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
	parser.add_argument('-t', dest='time',
		help='choose a time slice')
	parser.add_argument('--plot-B', action='store_false',
		help='plot B field')
	parser.add_argument('--plot-E', action='store_true',
		help='plot E field')
	parser.add_argument('--plot-P', action='store_true',
		help='plot pressure tensor')
	parser.add_argument('--plot-V', action='store_true',
		help='plot velocity field')
	parser.add_argument('--sp', default=1,
		help='choose a species to plot (for V or P)')
	parser.add_argument('--grid',
		help='number of grid points, e.g. nx,ny,nz')
	parser.add_argument('--save-png', action='store_true',
		help='save plots in png')
	args = parser.parse_args()


	if args.source == 'LANL':
		if args.plot_B:
			datafiles={'Bx':'Bx.gda','By':'By.gda','Bz':'Bz.gda'}
		if args.plot_E:
			datafiles={'Ex':'Ex.gda','Ey':'Ey.gda','Ez':'Ez.gda'}
		for k in datafiles:
			datafiles[k] = args.datapath + '/' + datafiles[k]
		if args.grid:
			grid = map(int, args.grid.strsplit(','))
		else:
			info_file = args.datapath + '/info'
			grid, L = read_from_info(info_file)

		emf = FieldLANL(datafiles, grid, int(args.time))
		X = numpy.linspace(-L[0]/2,L[0]/2,grid[0])
		Y = numpy.linspace(-L[2]/2,L[2]/2,grid[2])

	elif args.source == 'NASA':
		fname = args.datapath + '/fields-'
#		time = '{0:05d}'.format(args.time)
		fname = fname + args.time.zfill(5) + '.dat'
		if args.grid:
			grid = map(int, args.grid.strsplit(','))
		else:
			grid = [1000, 1, 800]
#		L = [320., 0, 128.]
		emf = FieldNASA(fname, grid)
		X = emf.data['xe']
		Y = emf.data['ze']
		print emf.data['mass']
		print emf.data['q']
		print emf.data['wpewce']

	else:
		print 'No source selected'
		exit(1)

	fig = Figure2D()
	if args.plot_B:
		fcomp = ['Bx','By','Bz']
	if args.plot_E:
		fcomp = ['Ex','Ey','Ez']
	if args.plot_V:
		fcomp = ['vxs','vys','vzs']
	if args.plot_P:
		fcomp = ['pxx','pyy','pzz','pxy','pxz','pyz']
	for f in fcomp:
#		fig.add_one(args.source + ' ' + f + ' t=' + args.time,
		if args.plot_P or args.plot_V:
			plotdata = emf.data[f][1] + emf.data[f][3]
		else:
			plotdata = emf.data[f]
		fig.add_one(f.title() + ' t=' + args.time,
			plotdata, X, Y)
		fig.add_streamline(X,Y,emf.data['Bx'],emf.data['Bz'])
#		fig.add_vectors(X,Y,emf.data['Bx'],emf.data['Bz'])

	plt.show()
	if args.save_png: fig.savefig()

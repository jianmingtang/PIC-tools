#!/usr/bin/env python


#    draw_trace.py:
#       Draw Particle Tracer data using matplotlib
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


import math
import numpy
import pylab
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as ani


class ParticleTrace:
	"""
	This class is used to store particle trace data in ndarray
	"""
	def __init__(self, fname):
		"""
		fname: data filename
		Np: number of particles
		Nts: number of time slices
		"""
		fh = open(fname,'r')
		buf = fh.readline().split(' ')
		self.Np = int(buf[0])
		self.Nts = int(buf[1])
		self.data = numpy.fromfile(fh,'f4',-1,' ').\
			reshape(self.Nts, self.Np * 6)
		fh.close()

	def data_stream(self, cx, cy):
		"""Generator for data stream"""
		i = self.Nts 
		while i > 0:
			i -= 1
			f = self.data[i,:].reshape(self.Np,6)
			yield f[:,cx], f[:,cy]


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
		pylab.axis('tight')
		self.figs[-1][1].colorbar(pcm)
		pylab.title(name)


class AnimatedScatterPlot:
	"""Animated scatter plot using matplotlib.animations.FuncAnimation."""
	def __init__(self, pt, cx, cy):
		self.pt = pt
		self.stream = pt.data_stream(cx, cy)
		self.fig = plt.figure('Particle Tracer')
		# plt.axes([10, 70, -3, 1])
		self.mov = ani.FuncAnimation(self.fig, self.update, interval=1,
			init_func=self.setup_plot, blit=True)

	def setup_plot(self):
		"""Initial drawing of the scatter plot"""
		x, y = next(self.stream)
		self.scat, = plt.plot(x,y,'bo',animated=True)
		# Note that FuncAnimation expects a sequence of artists,
		# thus the trailing comma.
		return self.scat,

	def update(self, i):
		"""Update the scatter plot"""
		x, y = next(self.stream)
		# Set x and y data...
		self.scat.set_data(x, y)
#		self.scat.set_ydata(y)
		return self.scat,

	def show(self):
		plt.show()


class FFMpegWriter:
	"""Create a movie using matplotlib.animations.FFMpegWriter"""
	def __init__(self, pt):
		self.pt = pt
		self.stream = pt.data_stream()
		self.fig = plt.figure('Particle Tracer')
		self.writer = ani.writers['ffmpeg']
#		writer = FFMpegWriter(fps=15, metadata=metadata)

	def setup_plot(self):
		"""Initial drawing of the scatter plot"""
		x, y = next(self.stream)
		self.scat, = plt.plot(x,y,'bo',animated=True)
		# Note that FuncAnimation expects a sequence of artists,
		# thus the trailing comma.
		return self.scat,

	def update(self, i):
		"""Update the scatter plot"""
		x, y = next(self.stream)
		# Set x and y data...
		self.scat.set_data(x, y)
		return self.scat,

	def show(self):
		plt.show()




### main program ###
if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description=
        	'Draw particle trace')
	parser.add_argument('datafile', help='particle tracer data file')
	parser.add_argument('--datapath', help='the data path')
	parser.add_argument('-s', dest='source',
		help='source of data (LANL or NASA)')
	parser.add_argument('--plot-B', action='store_false',
		help='plot B field')
	parser.add_argument('--plot-E', action='store_true',
		help='plot E field')
#	parser.add_argument('--Np', help='number of particles')
#	parser.add_argument('--Nts', help='number of time slices')
	args = parser.parse_args()


	if args.source == 'NASA':
		fname = args.datapath + '/fields-'
#		time = '{0:05d}'.format(args.time)
		fname = fname + args.time.zfill(5) + '.dat'
		if args.grid:
			grid = map(int, args.grid.strsplit(','))
		else:
			grid = [1000, 1, 800]
		emf = FieldNASA(fname, grid)
		X = emf.data['xe']
		Y = emf.data['ze']
		print emf.data['mass']
		print emf.data['q']
		print emf.data['wpewce']


	pt = ParticleTrace(args.datafile)
	myani = AnimatedScatterPlot(pt, 0, 2)
	myani.show()

#	FFMpegWriter = ani.writers['ffmpeg']
	metadata = dict(title='Particle Tracer', artist='Matplotlib',
		comment='velocity grid')
#	mymov = 
#	with writer.saving(fig, "writer_test.mp4", 100):

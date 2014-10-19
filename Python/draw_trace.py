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


import numpy
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
		datatype = numpy.dtype([('pt','f4',(self.Nts,self.Np*6),)])
		self.data = numpy.fromfile(fh, datatype)[0]['pt']
#		self.data = numpy.fromfile(fh,'f4',-1,' ').\
#			reshape(self.Nts, self.Np * 6)
		fh.close()

	def data_stream(self, cx, cy, skip=1):
		"""Generator for data stream"""
		i = self.Nts 
		while i > 0:
			i -= skip
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
		self.figs.append((title,plt.figure(title)))
		fX,fY = numpy.meshgrid(X,Y)
		pcm = plt.pcolormesh(fX, fY, fZ)
		plt.axis('tight')
		self.figs[-1][1].colorbar(pcm)
		plt.title(name)


class AnimatedScatterPlot2D:
	"""Animated scatter plot using matplotlib.animations.FuncAnimation."""
	def __init__(self, fig, pt, cx, cy, skip=1):
		self.pt = pt
		self.stream = pt.data_stream(cx, cy, skip)
		self.fig = fig
		plt.xlim(50, 270)
		plt.ylim(-35, 35)
		plt.xlabel('x')
		self.mov = ani.FuncAnimation(self.fig, self.update, interval=1,
			init_func=self.setup_plot, blit=True)

	def setup_plot(self):
		"""Initial drawing of the scatter plot"""
		x, y = next(self.stream)
		self.scat, = plt.plot(x, y, 'bo', animated=True)
		return self.scat,

	def update(self, i):
		"""Update the scatter plot"""
		x, y = next(self.stream)
		# Set x and y data...
		self.scat.set_data(x, y)
		return self.scat,

	def show(self):
		plt.show()


class FFMpeg:
	"""Create a movie using matplotlib.animations.FFMpegWriter"""
	def __init__(self, fname, fig, pt, cx, cy, skip=1, metadata={}, fps=15, Nf=150):
		self.fname = fname
		self.fig = fig
		self.pt = pt
		self.stream = pt.data_stream(cx, cy, skip)
		self.writer = ani.FFMpegWriter(metadata=metadata, fps=fps)
		self.setup_plot()
		self.make_movie(Nf)

	def setup_plot(self):
		"""Initial drawing of the scatter plot"""
#		self.fig = plt.figure()
		x = []; y = []
		plt.xlim(10, 60)
		plt.ylim(-3, 1)
		self.scat, = plt.plot(x, y, 'bo')

	def make_movie(self, Nf):
		"""Update the scatter plot"""
		with self.writer.saving(self.fig, self.fname, Nf):
			for i in range(Nf):
				x, y = next(self.stream)
				# Set x and y data...
				self.scat.set_data(x, y)
				print i
				self.writer.grab_frame(frame_format='rgba')



### main program ###
if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description=
        	'Draw particle trace')
	parser.add_argument('datafile', help='particle tracer data file')
	parser.add_argument('--datapath', help='the data path')
	parser.add_argument('-s', dest='source',
		help='source of data (LANL or NASA)')
	parser.add_argument('-t', dest='time', help='choose a time slice')
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
#		if args.grid:
#			grid = map(int, args.grid.strsplit(','))
#		else:
		grid = [1000, 1, 800]
		emf = FieldNASA(fname, grid)
		X = emf.data['xe']
		Y = emf.data['ze']
		print emf.data['mass']
		print emf.data['q']
		print emf.data['wpewce']


	fig = plt.figure('Particle Tracer')
	fX,fY = numpy.meshgrid(X,Y)
	fZ = emf.data['Ez']
	pcm = plt.pcolormesh(fX, fY, fZ)
	plt.axis('tight')
	fig.colorbar(pcm)

	
	pt = ParticleTrace(args.datafile)
	myani = AnimatedScatterPlot2D(fig, pt, cx=0, cy=2, skip=2)
	myani.show()

	metadata = dict(title='Particle Tracer', artist='Matplotlib',
		comment='velocity grid')
#	mymov = FFMpeg('test.mp4', fig, pt, cx=0, cy=2, skip=50,
#		metadata=metadata,fps=20,Nf=200)


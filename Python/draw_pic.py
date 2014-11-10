#!/usr/bin/env python


#    draw_pic.py:
#       Draw PIC data in the following formats.
#       1. slices in 2D using matplotlib
#	2. isosurfaces in 3D using VTK
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
import matplotlib.pyplot as plt
import argparse
import ConfigParser
import PIC


class Figure2D:
	"""
	This class creates and stores 2D plots using Matplotlib.
	There are two types of figures:
		1. 4 panels with individual species
		2. 1 panel of combined species
	"""
	def __init__(self):
		# self.fig stores a list of figure objects
		self.figs = []

	def add_quad(self, name, X, Y, fZ):
		"""
		Create a 4-panel figure
		name: title of the figure
		X, Y: 1D axes data
		fZ: 2D data set (Fortran indexing)
		"""
# The default ordering for 2D meshgrid is Fortran style
		title = name.replace(',','_')
		self.figs.append((title, plt.figure(title)))
		for i in range(4):
			ax = plt.subplot('22'+str(i+1))
			fX, fY = numpy.meshgrid(X[i], Y[i])
			pcm = ax.pcolormesh(fX, fY, fZ[i])
			ax.axis('tight')
			self.figs[-1][1].colorbar(pcm)
			plt.title(name+','+str(i))

	def add_one(self, name, X, Y, fZ):
		"""
		Create a 1-panel figure
		name: title of the figure
		X, Y: 1D axes data
		fZ: 2D data set (Fortran indexing)
		"""
		title = name.replace(',','_')
		self.figs.append((title, plt.figure(title)))
		fX, fY = numpy.meshgrid(X, Y)
		pcm = plt.pcolormesh(fX, fY, fZ)
		plt.xlabel('X (de)')
		plt.ylabel('Z (de)')
		plt.axis('tight')
		self.figs[-1][1].colorbar(pcm)
		plt.title(name)

	def add_streamline(self, X, Y, U, V):
		plt.streamplot(X,Y,U,V,color='k',density=[5,0.7])

	def savefig(self):
		"""
		Save all figures in PNG format
		"""
		for fig in self.figs:
			fig[1].savefig(fig[0]+'.png',bbox_inches='tight')
			print fig[0] +' saved'


### main program ###
if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description='Draw PIC data')
#	parser.add_argument('datapath', help='the input data path')
	parser.add_argument('datafile', help='the input data file')
#	parser.add_argument('-s', dest='source',
#		help='source of data (LANL or NASA)')
	parser.add_argument('-t', dest='time',
		help='choose a time slice')
	parser.add_argument('--grid',
		help='number of grid points, e.g. nx,ny,nz')
#	parser.add_argument('--d3', action='store_true',
#		help='make 3D plots')
	parser.add_argument('--nsp', default=4,
		help='number of species (default = 4)')
#	parser.add_argument('--cut',
#		help='make a 2D cut [e.g. x,49,51]')
#	parser.add_argument('--sp', default=1,
#		help='choose a species to plot for 3D')
#	parser.add_argument('--iso',
#		help='Set the iso value (in ratio of fmax) for 3D' \
#			+ '(default = 0.2)')
	parser.add_argument('--add',
		help='Combining species [e.g. 1,3]')
	parser.add_argument('--save-png', action='store_true',
		help='save plots in png')
	parser.add_argument('--plot-B', action='store_true',
		help='plot B field')
	parser.add_argument('--plot-E', action='store_true',
		help='plot E field')
	parser.add_argument('--plot-F', action='store_true',
		help='plot distribution function')
	parser.add_argument('--plot-P', action='store_true',
		help='plot pressure tensor')
	parser.add_argument('--plot-V', action='store_true',
		help='plot velocity field')
	args = parser.parse_args()

# Check parameters range
	if int(args.nsp) < 0: raise ValueError
#	if int(args.sp) < 0 or int(args.sp) >= int(args.nsp): raise ValueError

	if args.grid:
		grid = map(int, args.grid.strsplit(','))
	elif args.plot_F:
		grid = [101] * 3
	else:
		grid = [1000, 1, 800]

	if args.plot_F:
# Load particle data
		data = PIC.DistNASA(args.datafile, grid[0], args.nsp)
		X = data['axes']
		Y = X
		print data
	else:
		data = PIC.FieldNASA(args.datafile, grid)
		X = data['xe']
		Y = data['ze']

	fcomp = []
	if args.plot_F:
		fcomp = ['fxy','fxz','fyz']
	if args.plot_B:
		fcomp = ['Bx','By','Bz']
	if args.plot_E:
		fcomp = ['Ex','Ey','Ez']
	if args.plot_V:
		fcomp = ['vxs','vys','vzs']
	if args.plot_P:
		fcomp = ['pxx','pyy','pzz','pxy','pxz','pyz']

	fig = Figure2D()
	for f in fcomp:
#		fig.add_one(args.source + ' ' + f + ' t=' + args.time,
		fn = f.title() + ',t=' + args.time
		if args.plot_F:
			fig.add_quad(fn, X, Y, data[f])
		elif args.plot_P or args.plot_V:
			fig.add_quad(fn, [X]*4, [Y]*4, data[f])
		else:
			fig.add_one(fn, X, Y, data[f])
#			fig.add_streamline(X,Y,data['Bx'],data['Bz'])

	plt.show()
	if args.save_png: fig.savefig()

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
import thread
import numpy
import PIC
import Figure
import argparse


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


def draw_fields(fig, field, flist, np):
	for f in flist:
		fn = f.title() + ',t=' + args.time
		if np == 4:
			fig.add_quad(fn, [X]*4, [Y]*4, field[f])
		else:
			fig.add_one(fn, X, Y, field[f])
#			fig.add_streamline(X, Y, U, V)
			


### main program ###
if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description=
        	'Draw fields at a given t')
	parser.add_argument('datapath', help='the data path')
	parser.add_argument('-s', dest='source',
		help='source of data (LANL or NASA)')
	parser.add_argument('-t', dest='time',
		help='choose a time slice')
	parser.add_argument('--grid',
		help='number of grid points, e.g. nx,ny,nz')
	parser.add_argument('--plot-B', action='store_true',
		help='plot magnetic field')
	parser.add_argument('--plot-E', action='store_true',
		help='plot electric field')
	parser.add_argument('--plot-P', action='store_true',
		help='plot pressure tensor')
	parser.add_argument('--plot-V', action='store_true',
		help='plot velocity field')
	parser.add_argument('--sp', default=1,
		help='choose a species to plot (for V or P)')
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

		field = PIC.FieldLANL(datafiles, grid, int(args.time))
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
		field = PIC.FieldNASA(fname, grid)
		X = field['xe']
		Y = field['ze']
#		print field['mass']
#		print field['q']
#		print field['wpewce']

	else:
		print 'No source selected'
		exit(1)

	fig = Figure.Figure2D()
	if args.plot_B:
		flist = ['Bx','By','Bz']
		draw_fields(fig, field, flist, 1)
	if args.plot_E:
		flist = ['Ex','Ey','Ez']
		draw_fields(fig, field, flist, 1)
	if args.plot_V:
		flist = ['vxs','vys','vzs']
		draw_fields(fig, field, flist, 4)
	if args.plot_P:
		flist = ['pxx','pyy','pzz','pxy','pxz','pyz']
		draw_fields(fig, field, flist, 4)

# release the memory for data storage
	field = 0

# save or display all figures
# a significant amount of memory is required for the saving operation
# NASA data takes about 6 GB to handle one 4-panel figure at a time
	if args.save_png:  fig.savefig()
	else:  fig.show()

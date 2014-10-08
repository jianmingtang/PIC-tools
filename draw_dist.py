#!/usr/bin/env python


#    draw_dist.py:
#       Draw particle distribution data in the following formats.
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


import math
import vtk
import numpy
import pylab
#from matplotlib.backends.backend_pdf import PdfPages
import argparse

class ParticleDistribution:
	"""
	This class is used to store data in ndarray from a NASA PIC data file.
	Methods for data slicing and summation are provided.
	"""
	def __init__(self, fn, grid, nsp):
		self.grid = grid
		self.nsp = nsp
		datatype = numpy.dtype([
			('pad1','i4'),
			('axes','f4',(nsp,grid)),
			('xlo','f4'), ('xhi','f4'), ('zlo','f4'),('zhi','f4'),
			('ic','i4',(nsp,)),
			('fxyz','f4',(nsp,grid,grid,grid)),
			('fxy','f4',(nsp,grid,grid)),
			('fxz','f4',(nsp,grid,grid)),
			('fyz','f4',(nsp,grid,grid)),
			('vxa','f4',(nsp,)),
			('vya','f4',(nsp,)),
			('vza','f4',(nsp,)),
			('pad2','i4')
			])
		self.data = numpy.fromfile(fn, datatype)[0]
		print self.data['ic']

	def __str__(self):
		s = '\nBin location: '
		s += 'x=(%4g,%4g), z=(%4g,%4g)\n\n' % (self.data['xlo'],
			self.data['xhi'],self.data['zlo'],self.data['zhi'])
		for i in range(self.nsp):
			s += 'v['+str(i)+'] = ({0:g}, {1:g}, {2:g})\n'.format(
				self.data['vxa'][i], self.data['vya'][i],
				self.data['vza'][i] )
		return s

	def avg(self,s):
		v = 0.
		f = 0.
		vx1 = 0.
		vx2 = 0.
		for i in range(self.grid):
			for j in range(self.grid):
				vx1 += self.data['fxy'][s,i,j] * self.data['axes'][s,j]
				vx2 += self.data['fxz'][s,i,j] * self.data['axes'][s,i]
				for k in range(self.grid):
					f += self.data['fxyz'][s,i,j,k]
					v += self.data['fxyz'][s,k,j,i] * self.data['axes'][s,i]

		return v, f, v/f, vx1, vx2

# Cut out a 2D slice from the 3D distribution
	def cut(self, p):
		p[1] = int(p[1])
		p[2] = int(p[2])
		A = self.data['fxyz']
		if p[0] == 'x':
			self.dataCUT = A[:,:,:,p[1]]
			for i in range(p[1]+1,p[2]+1):
				self.dataCUT += A[:,:,:,i]
		elif p[0] == 'y':
			self.dataCUT = A[:,:,p[1],:]
			for i in range(p[1]+1,p[2]+1):
				self.dataCUT += A[:,:,i,:]
		elif p[0] == 'z':
			self.dataCUT = A[:,p[1],:,:]
			for i in range(p[1]+1,p[2]+1):
				self.dataCUT += A[:,i,:,:]
		else:
			raise IndexError

# Combine species for a 2D slice
	def add2D(self,addset):
		allowed_error = [1.e-6] * self.grid 
		self.axes = self.data['axes'][int(addset[0])]
		self.data2D = self.dataCUT[int(addset[0])]
		for s in addset[1:]:
			diff = self.data['axes'][int(s)] - self.axes
			if numpy.any(diff > allowed_error):
				print addset, ' cannot be combined!!!'
				raise IndexError
			self.data2D += self.dataCUT[int(s)]

# Combine species for reduced data sets
	def add_reduced(self,addset):
		self.dataR = {}
		allowed_error = [1.e-6] * self.grid 
		self.axes = self.data['axes'][int(addset[0])]
		for f in ['fxy', 'fxz', 'fyz']:
			self.dataR[f] = self.data[f][int(addset[0])]
			for s in addset[1:]:
				diff = self.data['axes'][int(s)] - self.axes
				if numpy.any(diff > allowed_error):
					print addset, ' cannot be combined!!!'
					raise IndexError
				self.dataR[f] += self.data[f][int(s)]

# Combine species for 3D data
	def add3D(self,addset):
		allowed_error = [1.e-6] * self.grid 
		self.axes = self.data['axes'][int(addset[0])]
		self.data3D = self.data['fxyz'][int(addset[0])]
		for s in addset[1:]:
			diff = self.data['axes'][int(s)] - self.axes
			if numpy.any(diff > allowed_error):
				print addset, ' cannot be combined!!!'
				raise IndexError
			self.data3D += self.data['fxyz'][int(s)]

class Figure2D:
	"""
	This class creates and stores 2D plots using Matplotlib.
	Each figure shows 4 panels of data. 
	"""
	def __init__(self):
		# self.fig stores a list of figure objects
		self.figs = []

	def add_quad(self, name, X, fZ):
# Does not work on chipolata: (older matplotlib?)
#	i = 0
#	fig, axs = pylab.subplots(2,2)
#	for ax in axs.ravel():
#		pcm = ax.pcolormesh(F[i])
#		ax.axis('tight')
#		fig.colorbar(pcm,ax=ax,shrink=0.9)
#		ax.set_title(name+','+str(i))
#		i += 1

# The default ordering for 2D meshgrid is Fortran style
		title = name.replace(',','_')
		self.figs.append((title,pylab.figure(title)))
		for i in range(4):
			fX,fY = numpy.meshgrid(X[i],X[i])
			ax = pylab.subplot('22'+str(i+1))
			pcm = ax.pcolormesh(fX, fY, fZ[i])
			ax.axis('tight')
			self.figs[-1][1].colorbar(pcm,shrink=0.9)
			pylab.title(name+','+str(i))

	def add_one(self, name, X, fZ):
		title = name.replace(',','_')
		self.figs.append((title,pylab.figure(title)))
		ax = pylab.subplot('111')
		fX,fY = numpy.meshgrid(X,X)
		pcm = ax.pcolormesh(fX, fY, fZ)
		ax.axis('tight')
		self.figs[-1][1].colorbar(pcm,shrink=0.9)
		pylab.title(name)

	def savefig(self):
		for fig in self.figs:
			fig[1].savefig(fig[0]+'.png',bbox_inches='tight')
			print fig[0] +' saved'

class Figure3D:
	"""
	This class creates vtk objects for 3D viewing.
	The class elements contain
		vtkStructuredGrid, vtkActor, vtkRenderWindow
	"""
	def __init__(self, axes, data):
		self.vmax = max(data)
		self.sgrid = vtk.vtkStructuredGrid()

		val = vtk.vtkFloatArray()
		val.SetVoidArray(data, len(data), 1)
		points = vtk.vtkPoints()
	
		Lx = numpy.linspace(-1,1,101)
		for x in Lx:
			for y in Lx:
				for z in Lx:
					points.InsertNextPoint(x, y, z)

		self.sgrid.SetDimensions(101,101,101)
		self.sgrid.SetPoints(points)
		self.sgrid.GetPointData().SetScalars(val)

	def set_up_color(self):
		color = vtk.vtkDoubleArray()
		color.SetName("Color")
		color.SetNumberOfComponents(3)
		Lx = numpy.arange(-1,1.01,0.02)
		for x in Lx:
			for y in Lx:
				for z in Lx:
					r = math.sqrt(x*x + y*y + z*z)
					color.InsertNextTuple3((0.4-r)*.1,0,0)
		self.sgrid.GetPointData().SetVectors(color)

	def set_up_iso_surface(self, isovalue):
		iso = vtk.vtkContourFilter()
		iso.SetInput(self.sgrid)
		iso.SetValue(0, isovalue)

		normals = vtk.vtkPolyDataNormals();
		normals.SetInput(iso.GetOutput());
#		normals.SetFeatureAngle(30);

		isoMapper = vtk.vtkPolyDataMapper();
		isoMapper.SetInput(normals.GetOutput());
		isoMapper.SetScalarRange(0, self.vmax);
		isoMapper.SetScalarModeToUsePointFieldData()
		isoMapper.SetColorModeToMapScalars()
		isoMapper.SelectColorArray("Color")

		self.Actor_iso = vtk.vtkActor();
		self.Actor_iso.SetMapper(isoMapper);

	def add_other_stuff(self):
		# add a bounding box
		box = vtk.vtkStructuredGridOutlineFilter()
		box.SetInput(self.sgrid)

		Mapper_box = vtk.vtkPolyDataMapper()
		Mapper_box.SetInput(box.GetOutput())

		self.Actor_box = vtk.vtkActor()
		self.Actor_box.SetMapper(Mapper_box)
		self.Actor_box.GetProperty().SetColor(0, 0, 0)
		self.Actor_box.GetProperty().SetLineWidth(2)

		# add a line of text
		text = vtk.vtkVectorText()
		text.SetText("fxyz")

		Mapper_text = vtk.vtkPolyDataMapper()
		Mapper_text.SetInput(text.GetOutput())

		self.Actor_text = vtk.vtkActor()
		self.Actor_text.SetMapper(Mapper_text)
		self.Actor_text.GetProperty().SetColor(0, 0, 0)
		self.Actor_text.SetScale(0.3125,0.3125,0.3125)
		self.Actor_text.SetPosition(1.1,-0.625,-1.25)
		self.Actor_text.RotateZ(90)

	def rendering(self):
		self.ren = vtk.vtkRenderer()
		self.ren.AddActor(self.Actor_iso)
		self.ren.AddActor(self.Actor_box)
		self.ren.AddActor(self.Actor_text)
		self.ren.SetBackground(1, 1, 1)
		self.ren.ResetCameraClippingRange(-2,2,-2,2,-2,2)

		cam = self.ren.GetActiveCamera()
		cam.SetFocalPoint(0, 0, 0)
		cam.SetPosition(6, 3.5, 2.5)
		cam.SetViewUp(0, 0, 1)

	def show_on_screen(self,title):
		self.renWin = vtk.vtkRenderWindow()
		self.renWin.AddRenderer(self.ren)
		self.renWin.SetSize(500, 500)
		self.renWin.SetWindowName(title)

		iren = vtk.vtkRenderWindowInteractor()
		iren.SetRenderWindow(self.renWin)
		iren.Initialize()
		self.renWin.Render()
		iren.Start()
	def save_png(self,fname):
		renderLarge = vtk.vtkRenderLargeImage()
		renderLarge.SetInput(self.ren)
		renderLarge.SetMagnification(1)
		writer = vtk.vtkPNGWriter()
		writer.SetInput(renderLarge.GetOutput())
		writer.SetFileName(fname)
		writer.Write()
		print 'image saved'


### main program ###

parser = argparse.ArgumentParser(description=
        'Draw distribution function at a given (r,t)')
parser.add_argument('datafile', help='the input data file')
parser.add_argument('--d2', action='store_true',
	help='make 2D plots')
parser.add_argument('--d3', action='store_true',
	help='make 3D plots')
parser.add_argument('--grid', default=101,
	help='number of grid points (default = 101)')
parser.add_argument('--nsp', default=4,
	help='number of species (default = 4)')
parser.add_argument('--cut',
	help='make a 2D cut [e.g. x,49,51]')
parser.add_argument('--sp', default=0,
	help='choose a species to plot for 3D')
parser.add_argument('--iso',
	help='Set the iso value (in ratio of fmax) for 3D (default = 0.2)')
parser.add_argument('--add',
	help='Combining species [e.g. 1,3]')
parser.add_argument('--save-png', action='store_true',
	help='save plots in png')
#parser.add_argument('--save-pdf', action='store_true',
#	help='save plots in pdf')
args = parser.parse_args()

# Check parameters range
if int(args.nsp) < 0: raise ValueError
if int(args.sp) < 0 or int(args.sp) >= int(args.nsp): raise ValueError


# Load particle data with number of grid points and number of species
PD = ParticleDistribution(args.datafile,args.grid,args.nsp)
print PD
#print PD.avg(0)
#print PD.avg(1)
#print PD.avg(2)
#print PD.avg(3)

if args.d2:
	fig = Figure2D()
	for f in ('fxy', 'fxz', 'fyz',):
		fig.add_quad(f, PD.data['axes'], PD.data[f])
	if args.cut:
		PD.cut(args.cut.split(','))
		fig.add_quad('fxyz,'+args.cut, PD.data['axes'], PD.dataCUT)
		if args.add:
			PD.add2D(args.add.split(','))
			fig.add_one('fxyz,cut('+args.cut+')add('+args.add+')',
				PD.axes, PD.data2D)
	elif args.add:
		PD.add_reduced(args.add.split(','))
		for f in ('fxy', 'fxz', 'fyz',):
			fig.add_one(f+',add('+args.add+')', PD.axes,
				PD.dataR[f])
	pylab.show()
	if args.save_png:
		fig.savefig()

#	One can save all images in one PDF file
#	This backend is currently quite slow and the PDF file is huge
#	I'll disable it for now.
#	if args.save_pdf:
#		pp = PdfPages('figure2D.pdf')
#		for f in fig.fig:
#			print "saving pdf ..."
#			pp.savefig(f, box_inches='tight')
#		pp.close()

if args.d3:
	axes = PD.data['axes'][int(args.sp)]
	if args.add:
		splist = args.add
		splist = splist.replace(',','_')
		PD.add3D(args.add.split(','))
		data3D = PD.data3D.ravel()
	else:
		splist = (args.sp)
		data3D = PD.data['fxyz'][int(args.sp)].ravel()
	print 'The iso value is set to ',
	if args.iso:
		isovalue = max(data3D) * float(args.iso)
		print '{1:6g} ({0} of fmax).'.format(
			args.iso,isovalue)
	else:
		isovalue = max(data3D) * 0.2
		print '%6g (0.2 of fmax).' % isovalue
	f3 = Figure3D(axes, data3D)
	f3.set_up_color()
	f3.set_up_iso_surface(isovalue)
	f3.add_other_stuff()
	f3.rendering()
	title = 'distf_sp({0})_iso{1:6g}'.format(splist,isovalue)
	f3.show_on_screen(title)
	if args.save_png:
		fname = title+'_3D.png'
		f3.save_png(fname)

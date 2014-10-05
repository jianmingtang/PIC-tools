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
	Some methods for data slicing and summation are provided.
	"""
	def __init__(self, fn, grid, nsp):
		self.grid = grid
		self.nsp = nsp
		self.data = numpy.fromfile(fn, numpy.dtype( [('pad1','i4'),
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
			('pad2','i4')] ) ) [0]

	def cut(self, p):
		if p[0] == 'x':
			C = self.data['fxyz'][:,:,:,p[1]]
			for i in range(p[1]+1,p[2]+1):
				C += self.data['fxyz'][:,:,:,i]
			return C
		elif p[0] == 'y':
			C = self.data['fxyz'][:,:,p[1],:]
			for i in range(p[1]+1,p[2]+1):
				C += self.data['fxyz'][:,:,i,:]
			return C
		elif p[0] == 'z':
			C = self.data['fxyz'][:,p[1],:,:]
			for i in range(p[1]+1,p[2]+1):
				C += self.data['fxyz'][:,i,:,:]
			return C
		else:
			raise IndexError


class Figure2D:
	"""
	This class creates and stores 2D plots using Matplotlib.
	Each figure shows 4 panels of data. 
	"""
	def __init__(self):
		# self.fig stores a list of figure objects
		self.fig = []
	def add(self, name, F):
# Does not work on chipolata: (older matplotlib?)
#	i = 0
#	fig, axs = pylab.subplots(2,2)
#	for ax in axs.ravel():
#		pcm = ax.pcolormesh(F[i])
#		ax.axis('tight')
#		fig.colorbar(pcm,ax=ax,shrink=0.9)
#		ax.set_title(name+','+str(i))
#		i += 1
		title = name.replace(',','_')
		self.fig.append(pylab.figure(title))
		for i in range(4):
			ax = pylab.subplot('22'+str(i+1))
			pcm = ax.pcolormesh(F[i])
			ax.axis('tight')
			self.fig[-1].colorbar(pcm,shrink=0.9)
			pylab.title(name+','+str(i))
		if args.save_png:
			pylab.savefig(title+'.png',bbox_inches='tight')
			print 'image saved'


class Figure3D:
	"""
	This class creates vtk objects for 3D viewing.
	The class elements contain
		vtkStructuredGrid, vtkActor, vtkRenderWindow
	"""
	def __init__(self, data):
		self.vmax = max(data)
		self.sgrid = vtk.vtkStructuredGrid()

		val = vtk.vtkFloatArray()
		val.SetVoidArray(data, len(data), 1)
		points = vtk.vtkPoints()
	
		Lx = numpy.arange(-1,1.01,0.02)
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

	def show_on_screen(self):
		self.renWin = vtk.vtkRenderWindow()
		self.renWin.AddRenderer(self.ren)
		self.renWin.SetSize(500, 500)

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
	help='number of grid points')
parser.add_argument('--nsp', default=4,
	help='number of species')
parser.add_argument('--cut',
	help='make a 2D cut [e.g. x,49,51]')
parser.add_argument('--sp', default=0,
	help='choose a species to plot for 3D')
parser.add_argument('--iso',
	help='Set the iso value (in ratio of fmax) for 3D')
parser.add_argument('--save-png', action='store_true',
	help='save plots in png')
#parser.add_argument('--save-pdf', action='store_true',
#	help='save plots in pdf')
args = parser.parse_args()


# Load particle data with number of grid points and number of species
PD = ParticleDistribution(args.datafile,args.grid,args.nsp)

if args.d2:
	fig = Figure2D()
	for s in ('fxy', 'fxz', 'fyz',):
		fig.add(s, PD.data[s])
	if args.cut:
		p = args.cut.split(',')
		p[1] = int(p[1])
		p[2] = int(p[2])
		fig.add('fxyz,'+args.cut, PD.cut(p))
	pylab.show()

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
	data3D = PD.data['fxyz'][int(args.sp)].ravel()
	if args.iso:
		isovalue = max(data3D) * float(args.iso)
		print 'The iso value is set to ({0} of fmax) {1:6g}'.format(
			args.iso,isovalue)
	else:
		isovalue = max(data3D) * 0.2
		print 'The iso value is set to (20% of fmax)', isovalue
	f3 = Figure3D(data3D)
	f3.set_up_color()
	f3.set_up_iso_surface(isovalue)
	f3.add_other_stuff()
	f3.rendering()
	f3.show_on_screen()
	if args.save_png:
		fname = 'distf_sp{0}_iso{1:6g}_3D.png'.format(args.sp,isovalue)
		f3.save_png(fname)

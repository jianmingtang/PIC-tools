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
from vtk import *


class Figure3D:
	"""
	This class creates vtk objects for 3D viewing.
	The class elements contain
		vtkStructuredGrid, vtkActor, vtkRenderer, vtkRenderWindow
	"""
	def __init__(self, axes, data):
		self.vmax = max(data)
		self.box = axes[-1]

		val = vtkFloatArray()
		val.SetVoidArray(data, len(data), 1)

		points = vtkPoints()
		for x in axes:
			for y in axes:
				for z in axes:
					points.InsertNextPoint(z, y, x)

		ng = len(axes)
		self.sgrid = vtkStructuredGrid()
		self.sgrid.SetDimensions(ng,ng,ng)
		self.sgrid.SetPoints(points)
		self.sgrid.GetPointData().SetScalars(val)

	def set_up_color(self):
		color = vtkDoubleArray()
		color.SetName("Color")
		color.SetNumberOfComponents(3)
		Lx = numpy.linspace(-1,1,101)
		for x in Lx:
			for y in Lx:
				for z in Lx:
					r = math.sqrt(x*x + y*y + z*z)
					color.InsertNextTuple3((0.4-r)*.1,0,0)
		self.sgrid.GetPointData().SetVectors(color)

	def set_up_iso_surface(self, isovalue):
		iso = vtkContourFilter()
		iso.SetInput(self.sgrid)
		iso.SetValue(0, isovalue)

		normals = vtkPolyDataNormals();
		normals.SetInput(iso.GetOutput());
#		normals.SetFeatureAngle(30);

		isoMapper = vtkPolyDataMapper();
		isoMapper.SetInput(normals.GetOutput());
		isoMapper.SetScalarRange(0, self.vmax);
		isoMapper.SetScalarModeToUsePointFieldData()
		isoMapper.SetColorModeToMapScalars()
		isoMapper.SelectColorArray("Color")

		self.Actor_iso = vtkActor();
		self.Actor_iso.SetMapper(isoMapper);

	def add_other_stuff(self):
		r = self.box
		# add Y axis
		self.Actor_axis = vtkAxisActor()
		self.Actor_axis.SetPoint1(-r,-r,-r)
		self.Actor_axis.SetPoint2(-r,r,-r)
		self.Actor_axis.SetAxisTypeToY()
		self.Actor_axis.SetMajorStart(-(r//5)*5)
		self.Actor_axis.SetMinorStart(-math.floor(r))
		self.Actor_axis.SetDeltaMajor(5)
		self.Actor_axis.SetDeltaMinor(1)
		self.Actor_axis.GetProperty().SetColor(0,0,0)
		self.Actor_axis.GetProperty().SetLineWidth(2)
		# add axes
		self.Actor_axes = vtkAxesActor()
		tf = vtk.vtkTransform()
		Ll = r * 0.5
		lr = r * 0.003
		tf.Translate(-r,-r,-r)
		self.Actor_axes.SetUserTransform(tf)
		self.Actor_axes.SetShaftTypeToCylinder()
		self.Actor_axes.SetTotalLength(Ll,Ll,Ll)
		self.Actor_axes.SetCylinderRadius(lr)
		self.Actor_axes.SetConeRadius(lr*10)

		xca = self.Actor_axes.GetXAxisCaptionActor2D()
		self.Actor_axes.SetXAxisLabelText('x')
		self.Actor_axes.SetYAxisLabelText('y')
		self.Actor_axes.SetZAxisLabelText('z')
		self.Actor_axes.SetNormalizedLabelPosition(1.2,1,1.2)
		tp = vtkTextProperty()
		tp.SetColor(0,0,0)
		self.Actor_axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(tp)
		self.Actor_axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(tp)
		self.Actor_axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(tp)
		# add a bounding box
		box = vtkStructuredGridOutlineFilter()
		box.SetInput(self.sgrid)
		Mapper_box = vtkPolyDataMapper()
		Mapper_box.SetInput(box.GetOutput())
		self.Actor_box = vtkActor()
		self.Actor_box.SetMapper(Mapper_box)
		self.Actor_box.GetProperty().SetColor(0, 0, 0)
		self.Actor_box.GetProperty().SetLineWidth(1)

	def rendering(self):
		self.ren = vtkRenderer()
		self.ren.AddActor(self.Actor_iso)
		self.ren.AddActor(self.Actor_axes)
		self.ren.AddActor(self.Actor_axis)
		self.ren.AddActor(self.Actor_box)
		self.ren.SetBackground(1, 1, 1)
		r = self.box
		self.ren.ResetCameraClippingRange(-r,r,-r,r,-r,r)

		cam = self.ren.GetActiveCamera()
		cam.SetFocalPoint(0, 0, 0)
		cam.SetPosition(r*6, r*2, r*0.5)
		cam.SetViewUp(0, 0, 1)

	def show_on_screen(self,title):
		self.renWin = vtkRenderWindow()
		self.renWin.AddRenderer(self.ren)
		self.renWin.SetSize(500, 500)
		self.renWin.SetWindowName(title)

		iren = vtkRenderWindowInteractor()
		iren.SetRenderWindow(self.renWin)
		iren.Initialize()
		self.renWin.Render()
		iren.Start()

	def save_png(self,fname):
		renderLarge = vtkRenderLargeImage()
		renderLarge.SetInput(self.ren)
		renderLarge.SetMagnification(1)
		writer = vtkPNGWriter()
		writer.SetInput(renderLarge.GetOutput())
		writer.SetFileName(fname)
		writer.Write()
		print 'image saved'

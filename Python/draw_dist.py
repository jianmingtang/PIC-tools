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
from vtk import *
import numpy
import pylab
# from matplotlib.backends.backend_pdf import PdfPages
import argparse


class ParticleDistribution:
    """
    This class is used to store data in ndarray from a NASA PIC data file.
    Methods for data slicing and summation are provided.
    """
    def __init__(self, fname, grid, nsp):
        """
        fname: data filename
        grid: number of grid points
        nsp: number of species
        """
        self.grid = grid
        self.nsp = nsp
        datatype = numpy.dtype([
                ('pad1', 'i4'),
                ('axes', 'f4', (nsp, grid)),
                ('xlo', 'f4'), ('xhi', 'f4'), ('zlo', 'f4'), ('zhi', 'f4'),
                ('ic', 'i4', (nsp,)),
                ('fxyz', 'f4', (nsp, grid, grid, grid)),
                ('fxy', 'f4', (nsp, grid, grid)),
                ('fxz', 'f4', (nsp, grid, grid)),
                ('fyz', 'f4', (nsp, grid, grid)),
                ('vxa', 'f4', (nsp,)),
                ('vya', 'f4', (nsp,)),
                ('vza', 'f4', (nsp,)),
                ('pad2', 'i4')
                ])
        self.data = numpy.fromfile(fname, datatype)[0]
        print self.data['ic']

    def __str__(self):
        s = '\n'
        s += 'Bin location: '
        s += 'x=(%4g,%4g), z=(%4g,%4g)\n' % (self.data['xlo'],
                self.data['xhi'], self.data['zlo'], self.data['zhi'])
# This is hard coded to species 1
        s += '(Hard coded) Axes max: %4g\n' % self.data['axes'][1][-1]
        s += '\n'
        for i in range(self.nsp):
            s += 'v['+str(i)+'] = ({0:g}, {1:g}, {2:g})\n'.format(
                    self.data['vxa'][i], self.data['vya'][i],
                    self.data['vza'][i] )
        return s

    def avg(self, s):
        v = 0.
        f = 0.
        vx1 = 0.
        vx2 = 0.
        for i in xrange(self.grid):
            for j in xrange(self.grid):
                vx1 += self.data['fxy'][s, j, i] * self.data['axes'][s, i]
                vx2 += self.data['fxz'][s, j, i] * self.data['axes'][s, i]
                for k in xrange(self.grid):
                    f += self.data['fxyz'][s, i, j, k]
                    v += self.data['fxyz'][s, k, j, i] * self.data['axes'][s, i]

        return v, f, v/f, vx1, vx2

    def cut(self, p):
        """
        Cut out a 2D slice from the 3D data
        p = [dir,rmin,rmax]
        """
        rmin = int(p[1])
        rmax = int(p[2])
        A = self.data['fxyz']
        if p[0] == 'x':
            self.dataCUT = A[:,:,:, rmin]
            for i in range(rmin+1, rmax+1):
                self.dataCUT += A[:,:,:, i]
        elif p[0] == 'y':
            self.dataCUT = A[:,:, rmin,:]
            for i in range(rmin+1, rmax+1):
                self.dataCUT += A[:,:, i,:]
        elif p[0] == 'z':
            self.dataCUT = A[:, rmin,:,:]
            for i in range(rmin+1, rmax+1):
                self.dataCUT += A[:, i,:,:]
        else:
            raise IndexError

    def _check_add(self, sps):
        # Check the ranges of velocities are consistent.
        allowed_error = [1.e-6] * self.grid
        self.axes = self.data['axes'][int(sps[0])]
        for s in sps[1:]:
            diff = self.data['axes'][int(s)] - self.axes
            if numpy.any(diff > allowed_error):
                print addset, ' cannot be combined!!!'
                raise IndexError

    def add2D(self, sps):
        """
        Combine species for a 2D slice
        sps = [s1,s2,...]
        """
        self._check_add(sps)
        self.data2D = self.dataCUT[int(sps[0])]
        for s in sps[1:]:
            self.data2D += self.dataCUT[int(s)]

    def add_reduced(self, sps):
        """
        Combine species for reduced data sets
        sps = [s1,s2,...]
        """
        self._check_add(sps)
        self.dataR = {}
        for f in ['fxy', 'fxz', 'fyz']:
            self.dataR[f] = self.data[f][int(sps[0])]
            for s in sps[1:]:
                self.dataR[f] += self.data[f][int(s)]

    def add3D(self, sps):
        """
        Combine species for 3D data
        sps = [s1,s2,...]
        """
        self._check_add(sps)
        self.data3D = self.data['fxyz'][int(sps[0])]
        for s in sps[1:]:
            self.data3D += self.data['fxyz'][int(s)]


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

    def add_quad(self, name, X, fZ):
        """
        Create a 4-panel figure
        name: title of the figure
        X: 1D axes data
        fZ: 2D data set (Fortran indexing)
        """
# Does not work on chipolata: (older matplotlib?)
#	i = 0
#	fig, axs = pylab.subplots(2,2)
#	for ax in axs.ravel():
#		pcm = ax.pcolormesh(F[i])
#		ax.axis('tight')
#		fig.colorbar(pcm,ax=ax)
#		ax.set_title(name+','+str(i))
#		i += 1

# The default ordering for 2D meshgrid is Fortran style
        title = name.replace(',', '_')
        self.figs.append((title, pylab.figure(title)))
        for i in range(4):
            fX, fY = numpy.meshgrid(X[i], X[i])
            ax = pylab.subplot('22'+str(i+1))
            pcm = ax.pcolormesh(fX, fY, fZ[i])
            ax.axis('tight')
            self.figs[-1][1].colorbar(pcm)
            pylab.title(name+','+str(i))

    def add_one(self, name, X, fZ):
        """
        Create a 1-panel figure
        name: title of the figure
        X: 1D axes data
        fZ: 2D data set (Fortran indexing)
        """
        title = name.replace(',', '_')
        self.figs.append((title, pylab.figure(title)))
        fX, fY = numpy.meshgrid(X, X)
        pcm = pylab.pcolormesh(fX, fY, fZ)
        pylab.axis('tight')
        self.figs[-1][1].colorbar(pcm)
        pylab.title(name)

    def savefig(self):
        """
        Save all figures in PNG format
        """
        for fig in self.figs:
            fig[1].savefig(fig[0]+'.png', bbox_inches='tight')
            print fig[0] + ' saved'


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
        self.sgrid.SetDimensions(ng, ng, ng)
        self.sgrid.SetPoints(points)
        self.sgrid.GetPointData().SetScalars(val)

    def set_up_color(self):
        color = vtkDoubleArray()
        color.SetName("Color")
        color.SetNumberOfComponents(3)
        Lx = numpy.linspace(-1, 1, 101)
        for x in Lx:
            for y in Lx:
                for z in Lx:
                    r = math.sqrt(x*x + y*y + z*z)
                    color.InsertNextTuple3((0.4-r)*.1, 0, 0)
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
        self.Actor_axis.SetPoint1(-r, -r, -r)
        self.Actor_axis.SetPoint2(-r, r, -r)
        self.Actor_axis.SetAxisTypeToY()
        self.Actor_axis.SetMajorStart(-(r//5)*5)
        self.Actor_axis.SetMinorStart(-math.floor(r))
        self.Actor_axis.SetDeltaMajor(5)
        self.Actor_axis.SetDeltaMinor(1)
        self.Actor_axis.GetProperty().SetColor(0, 0, 0)
        self.Actor_axis.GetProperty().SetLineWidth(2)
        # add axes
        self.Actor_axes = vtkAxesActor()
        tf = vtk.vtkTransform()
        Ll = r * 0.5
        lr = r * 0.003
        tf.Translate(-r, -r, -r)
        self.Actor_axes.SetUserTransform(tf)
        self.Actor_axes.SetShaftTypeToCylinder()
        self.Actor_axes.SetTotalLength(Ll, Ll, Ll)
        self.Actor_axes.SetCylinderRadius(lr)
        self.Actor_axes.SetConeRadius(lr*10)

        xca = self.Actor_axes.GetXAxisCaptionActor2D()
        self.Actor_axes.SetXAxisLabelText('x')
        self.Actor_axes.SetYAxisLabelText('y')
        self.Actor_axes.SetZAxisLabelText('z')
        self.Actor_axes.SetNormalizedLabelPosition(1.2, 1, 1.2)
        tp = vtkTextProperty()
        tp.SetColor(0, 0, 0)
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
        self.ren.ResetCameraClippingRange(-r, r, -r, r, -r, r)

        cam = self.ren.GetActiveCamera()
        cam.SetFocalPoint(0, 0, 0)
        cam.SetPosition(r*6, r*2, r*0.5)
        cam.SetViewUp(0, 0, 1)

    def show_on_screen(self, title):
        self.renWin = vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(500, 500)
        self.renWin.SetWindowName(title)

        iren = vtkRenderWindowInteractor()
        iren.SetRenderWindow(self.renWin)
        iren.Initialize()
        self.renWin.Render()
        iren.Start()

    def save_png(self, fname):
        renderLarge = vtkRenderLargeImage()
        renderLarge.SetInput(self.ren)
        renderLarge.SetMagnification(1)
        writer = vtkPNGWriter()
        writer.SetInput(renderLarge.GetOutput())
        writer.SetFileName(fname)
        writer.Write()
        print 'image saved'


# main program ###
if __name__ == "__main__":

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
    parser.add_argument('--sp', default=1,
            help='choose a species to plot for 3D')
    parser.add_argument('--iso',
            help='Set the iso value (in ratio of fmax) for 3D' \
                    + '(default = 0.2)')
    parser.add_argument('--add',
            help='Combining species [e.g. 1,3]')
    parser.add_argument('--save-png', action='store_true',
            help='save plots in png')
# parser.add_argument('--save-pdf', action='store_true',
#	help='save plots in pdf')
    args = parser.parse_args()

# Check parameters range
    if int(args.nsp) < 0:
        raise ValueError
    if int(args.sp) < 0 or int(args.sp) >= int(args.nsp):
        raise ValueError


# Load particle data with number of grid points and number of species
    PD = ParticleDistribution(args.datafile, args.grid, args.nsp)
    print PD

    if args.d2:
        fig = Figure2D()
        for f in ('fxy', 'fxz', 'fyz',):
            fig.add_quad(f, PD.data['axes'], PD.data[f])
        if args.cut:
            PD.cut(args.cut.split(','))
            fig.add_quad('fxyz,cut('+args.cut+')', PD.data['axes'],
                    PD.dataCUT)
            if args.add:
                PD.add2D(args.add.split(','))
                fig.add_one('fxyz,cut('+args.cut+')add(' \
                        + args.add+')', PD.axes, PD.data2D)
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
            splist = splist.replace(',', '_')
            PD.add3D(args.add.split(','))
# TODO: axes should be changed here
            data3D = PD.data3D.ravel()
        else:
            splist = (args.sp)
            data3D = PD.data['fxyz'][int(args.sp)].ravel()
        print 'The iso value is set to ',
        if args.iso:
            isovalue = max(data3D) * float(args.iso)
            print '{1:6g} ({0} of fmax).'.format(
                    args.iso, isovalue)
        else:
            isovalue = max(data3D) * 0.2
            print '%6g (0.2 of fmax).' % isovalue
        f3 = Figure3D(axes, data3D)
        f3.set_up_color()
        f3.set_up_iso_surface(isovalue)
        f3.add_other_stuff()
        f3.rendering()
        title = 'fxyz_sp({0})_iso{1:6g}'.format(splist, isovalue)
        print 'Plotting ' + title
        f3.show_on_screen(title)
        if args.save_png:
            fname = title+'_3D.png'
            f3.save_png(fname)

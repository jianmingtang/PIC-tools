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
    def __init__(self, fname, reverse=False):
        """
        fname: data filename
        Np: number of particles
        Nts: number of time slices
        """
        self.rev = reverse
        fh = open(fname, 'r')
        buf = fh.readline().split(' ')
        self.Np = int(buf[0])
        self.Nts = int(buf[1])
        datatype = numpy.dtype([('pt', 'f4', (self.Nts, self.Np*6),)])
        self.data = numpy.fromfile(fh, datatype)[0]['pt']
#		self.data = numpy.fromfile(fh,'f4',-1,' ').\
#			reshape(self.Nts, self.Np * 6)
        fh.close()

    def data_stream(self, cx, cy, skip=1):
        """Generator for data stream"""
        if self.rev:
            i = self.Nts - 1
            while i > 0:
                print 'Frame ', i
                f = self.data[i,:].reshape(self.Np, 6)
                i -= skip
                yield f[:, cx], f[:, cy]
        else:
            i = 0
            while i < self.Nts:
                print 'Frame ', i
                f = self.data[i,:].reshape(self.Np, 6)
                i += skip
                yield f[:, cx], f[:, cy]


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
                ('pad1', 'i4'),
                ('it', 'i4'),
                ('dt', 'f4'), ('teti', 'f4'),
                ('xmax', 'f4'), ('zmax', 'f4'),
                ('nnx', 'i4'), ('nnz', 'i4'),
                ('vxs', 'f4', (nss, nz, nx)),
                ('vys', 'f4', (nss, nz, nx)),
                ('vzs', 'f4', (nss, nz, nx)),
                ('Bx', 'f4', (nz, nx)),
                ('By', 'f4', (nz, nx)),
                ('Bz', 'f4', (nz, nx)),
                ('Ex', 'f4', (nz, nx)),
                ('Ey', 'f4', (nz, nx)),
                ('Ez', 'f4', (nz, nx)),
                ('dns', 'f4', (nss, nz, nx)),
                ('xe', 'f4', (nx,)),
                ('ze', 'f4', (nz,)),
                ('mass', 'f4', (nss,)),
                ('q', 'f4', (nss,)),
                ('time', 'f8'),
                ('wpewce', 'f4'),
                ('dfac', 'f4', (nss,)),
                ('pxx', 'f4', (nss, nz, nx)),
                ('pyy', 'f4', (nss, nz, nx)),
                ('pzz', 'f4', (nss, nz, nx)),
                ('pxy', 'f4', (nss, nz, nx)),
                ('pxz', 'f4', (nss, nz, nx)),
                ('pyz', 'f4', (nss, nz, nx)),
                ('pad2', 'i4')
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
        title = name.replace(' ', '_')
        self.figs.append((title, plt.figure(title)))
        fX, fY = numpy.meshgrid(X, Y)
        pcm = plt.pcolormesh(fX, fY, fZ)
        plt.axis('tight')
        self.figs[-1][1].colorbar(pcm)
        plt.title(name)


class AnimatedScatterPlot2D:
    """Animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, fig, pt, cx, cy, fov, skip=1):
        self.pt = pt
        self.stream = pt.data_stream(cx, cy, skip)
        self.fig = fig
        u = map(float, fov.split(','))
        plt.xlim(u[0], u[1])
        plt.ylim(u[2], u[3])
        plt.xlabel('X (de)')
        plt.ylabel('Z (de)')
        self.mov = ani.FuncAnimation(self.fig, self.update, frames=pt.Nts/skip, interval=1, init_func=self.setup_plot, blit=True)

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

    def save(self, fname, metadata, fps, cx, cy, skip):
#		self.stream = pt.data_stream(cx, cy, skip)
#		writer = ani.FFMpegWriter(metadata=metadata, fps=fps)
#		x = []
#		y = []
#		self.scat.set_data(x, y)
        writer = ani.MencoderWriter(metadata=metadata, fps=fps)
        self.mov.save(fname, writer=writer, extra_args=['-vcodec', 'libx264', '--verbose-debug'])


# main program ###
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
            'Draw particle trace')
    parser.add_argument('datafile', help='particle tracer data file')
    parser.add_argument('--path', help='the data path')
    parser.add_argument('-t', dest='time', help='choose a time slice')
    parser.add_argument('--plot', help='plot background field')
    parser.add_argument('--grid', help='nx,ny,nz')
    parser.add_argument('--fov', help='xmin,xmax,zmin,zmax')
    parser.add_argument('--reverse', action='store_true',
            help='xmin,xmax,zmin,zmax')
    args = parser.parse_args()


    fname = args.path + '/fields-'
    fname = fname + args.time.zfill(5) + '.dat'

    if args.grid:
        grid = map(int, args.grid.split(','))
    else:
        grid = [1000, 1, 800]

    emf = FieldNASA(fname, grid)
    X = emf.data['xe']
    Y = emf.data['ze']
    fX, fY = numpy.meshgrid(X, Y)
    fZ = emf.data[args.plot]


    fig = plt.figure('Particle Tracer')
    plt.title(args.plot+', '+str(args.time))
    pcm = plt.pcolormesh(fX, fY, fZ)
    plt.axis('tight')
    fig.colorbar(pcm)

    pt = ParticleTrace(args.datafile, args.reverse)

    myskip = 10
    myani = AnimatedScatterPlot2D(fig, pt, cx=0, cy=2, fov=args.fov, skip=myskip)
    myani.show()

    if args.reverse:
        mname = args.datafile.replace('.dat', '_R.mp4')
    else:
        mname = args.datafile.replace('dat', 'mp4')

#	metadata = dict(title='Particle Tracer', artist='Matplotlib',
#		comment='velocity grid')
#	myani.save(mname, metadata, fps=35,cx=0,cy=2,skip=myskip)

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
from skimage import measure
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


name = [r'$p^+$,lo', r'$e^-$,lo', r'$p^+$,hi', r'$e^-$,hi']


class Figure3D(Figure):

    """ The following draw methods are implemented:
            * 1 subplot
    """

    def __init__(self, *args, **kwargs):
        Figure.__init__(self, *args, **kwargs)

    def rescale(self, V, X, Y, Z, N):
        xs = (X[-1] - X[0]) / N[0]
        ys = (Y[-1] - Y[0]) / N[1]
        zs = (Z[-1] - Z[0]) / N[2]
        for i in xrange(len(V)):
            V[i][0] = V[i][0] * xs + X[0]
            V[i][1] = V[i][1] * ys + Y[0]
            V[i][2] = V[i][2] * zs + Z[0]

    def getcolor(self, V, F):
        dS = numpy.empty(len(F))
        for i, f in enumerate(F):
            v = V[f][0]
            dS[i] = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
        cmap = ScalarMappable(cmap='jet')
        cmap.set_array(dS)
        return cmap, cmap.to_rgba(dS)

    def draw_one(self, title, Lx, Ly, Lz, X, Y, Z, f, iso,
                 elev=None, azim=None):
        """ Draw a single plot
                title: title of the plot
                X, Y, Z: 1D axes data
                f: 3D data set (C style index?!)
        """
        self.clf()
        vert, face = measure.marching_cubes(f, iso)
        self.rescale(vert, X, Y, Z, f.shape)
        self.ax = self.add_subplot(111, projection='3d')
        cmap, col = self.getcolor(vert, face)
        surface = Poly3DCollection(vert[face])
        surface.set_color(col)
        surface.set_edgecolor('')
        self.ax.add_collection3d(surface)
        self.ax.set_xlabel(Lx, fontsize=14)
        self.ax.set_ylabel(Ly, fontsize=14)
        self.ax.set_zlabel(Lz, fontsize=14)
        self.ax.set_xlim(X[0], X[-1])
        self.ax.set_ylim(Y[0], Y[-1])
        self.ax.set_zlim(Z[0], Z[-1])
        self.ax.set_title(title)
        self.ax.view_init(elev, azim)
        self.colorbar(cmap, shrink=0.8, fraction=0.1, label=r'V $^2$')
        self.tight_layout()
        self.canvas.draw()


class Figure2D(Figure):

    """ The following draw methods are implemented:
            * 1 subplot
            * 4 subplots with individual species
    """

    def __init__(self, *args, **kwargs):
        Figure.__init__(self, *args, **kwargs)

    def draw_one(self, title, Lx, Ly, X, Y, fZ, U=None, V=None):
        """ Draw a single plot
                title: title of the plot
                X, Y: 1D axes data
                fZ: 2D data set (Fortran style index)
        """
    # The default ordering for 2D meshgrid is Fortran style
    #
        fX, fY = numpy.meshgrid(X, Y)
        self.clf()
        self.ax = self.add_subplot(111)
        self.ax.set_xlabel(Lx, fontsize=14)
        self.ax.set_ylabel(Ly, fontsize=14)
        pcm = self.ax.pcolormesh(fX, fY, fZ)
        self.ax.axis('tight')
        cb = self.colorbar(pcm)
        cb.formatter.set_powerlimits((-2, 3))
        cb.update_ticks()
        self.ax.set_title(title)
        if U is not None and V is not None:
            self.add_streamline(X, Y, U, V)
        self.tight_layout()
        self.canvas.draw()

    def draw_quad(self, title, Lx, Ly, X, Y, fZ, U=None, V=None):
        """ Draw 4 subplots
                title: main title of the plots
                X, Y: 1D axes data
                fZ: 2D data set (Fortran style index)
        """
    # The default ordering for 2D meshgrid is Fortran style
    #
        self.clf()
        for i in range(4):
            self.ax = self.add_subplot('22' + str(i + 1))
            self.ax.set_xlabel(Lx)
            self.ax.set_ylabel(Ly)
            fX, fY = numpy.meshgrid(X[i], Y[i])
            pcm = self.ax.pcolormesh(fX, fY, fZ[i])
            self.ax.axis('tight')
            cb = self.colorbar(pcm)
            cb.formatter.set_powerlimits((-2, 3))
            cb.update_ticks()
            self.ax.set_title(title + ', ' + name[i])
            if U is not None and V is not None:
                self.add_streamline(X[i], Y[i], U, V)
        self.tight_layout()
        self.canvas.draw()

    def add_streamline(self, X, Y, U, V):
        """ add stream lines defined by (U,V) with fixed densities
        """
        self.ax.streamplot(X, Y, U, V, color='k', density=[5, 0.7])


class Figure1D(Figure):

    """ The following draw methods are implemented:
            * 1 subplot
            * 4 subplots with individual species
    """

    def __init__(self, *args, **kwargs):
        Figure.__init__(self, *args, **kwargs)

    def draw_one(self, title, Lx, Ly, X, Y):
        """ Draw a single plot
                title: title of the plot
                X, Y: 1D data
        """
        self.clf()
        self.ax = self.add_subplot(111)
        self.ax.set_xlabel(Lx, fontsize=14)
        self.ax.set_ylabel(Ly, fontsize=14)
        self.ax.plot(X, Y, linewidth=2)
        self.ax.axis('tight')
        self.ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 3))
        self.ax.set_title(title)
        self.tight_layout()
        self.canvas.draw()

    def draw_quad(self, title, Lx, Ly, X, Y):
        """ Draw 4 subplots
                title: main title of the plots
                X, Y: 1D data
        """
        self.clf()
        for i in range(4):
            self.ax = self.add_subplot('22' + str(i + 1))
            self.ax.set_xlabel(Lx)
            self.ax.set_ylabel(Ly)
            self.ax.plot(X[i], Y[i])
            self.ax.axis('tight')
            self.ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 3))
            self.ax.set_title(title + ', ' + name[i])
        self.tight_layout()
        self.canvas.draw()

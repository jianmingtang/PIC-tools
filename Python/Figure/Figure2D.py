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
		title = title.replace('=','')
		self.figs.append((title, plt.figure(title)))
		for i in range(4):
			ax = plt.subplot('22'+str(i+1))
			fX, fY = numpy.meshgrid(X[i], Y[i])
			pcm = ax.pcolormesh(fX, fY, fZ[i])
			ax.axis('tight')
			self.figs[-1][1].colorbar(pcm)
			plt.title(name+',s='+str(i))

	def add_one(self, name, X, Y, fZ):
		"""
		Create a 1-panel figure
		name: title of the figure
		X, Y: 1D axes data
		fZ: 2D data set (Fortran indexing)
		"""
		title = name.replace(',','_')
		title = title.replace('=','')
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
		while self.figs != []:
			fig = self.figs.pop()
			fig[1].savefig(fig[0]+'.png',bbox_inches='tight')
			print fig[0] +' saved'

	def show(self):
		plt.show()

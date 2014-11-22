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


import wx
import numpy
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar


class FigureF2D(Figure):
	""" The following draw methods are implemented:
		* 1 subplot
		* 4 subplots with individual species
	"""
	def __init__(self, *args, **kwargs):
		Figure.__init__(self, *args, **kwargs)

	def draw_one(self, name, X, Y, fZ, U=None, V=None):
		""" Draw a single plot
			name: title of the plot
			X, Y: 1D axes data
			fZ: 2D data set (Fortran style index)
		"""
	# The default ordering for 2D meshgrid is Fortran style
	#
		fX, fY = numpy.meshgrid(X, Y)
		self.clf()
		self.ax = self.add_subplot(111)
		self.ax.set_xlabel('X (de)',fontsize=14)
		self.ax.set_ylabel('Z (de)',fontsize=14)
		pcm = self.ax.pcolormesh(fX, fY, fZ)
		self.ax.axis('tight')
		self.colorbar(pcm)
		self.ax.set_title(name)
		if U != None and V != None:
			self.add_streamline(X, Y, U, V)
		self.tight_layout()
		self.canvas.draw()

	def draw_quad(self, name, X, Y, fZ, U=None, V=None):
		""" Draw 4 subplots
			name: main title of the plots
			X, Y: 1D axes data
			fZ: 2D data set (Fortran style index)
		"""
	# The default ordering for 2D meshgrid is Fortran style
	#
		fX, fY = numpy.meshgrid(X, Y)
		self.clf()
		for i in range(4):
			self.ax = self.add_subplot('22'+str(i+1))
			self.ax.set_xlabel('X (de)')
			self.ax.set_ylabel('Z (de)')
			pcm = self.ax.pcolormesh(fX, fY, fZ[i])
			self.ax.axis('tight')
			self.colorbar(pcm)
			self.ax.set_title(name+', s='+str(i))
			if U != None and V != None:
				self.add_streamline(X, Y, U, V)
		self.tight_layout()
		self.canvas.draw()

	def add_streamline(self, X, Y, U, V):
		""" add stream lines defined by (U,V) with fixed densities
		"""
		self.ax.streamplot(X,Y,U,V,color='k',density=[5,0.7])


class PanelF2DDisp(wx.Panel):
	""" Display Panel and PIC data
		* Figure Canvas
		* Navigation Toolbar
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to the Main Frame
	#
		self.p = parent
        
        # Create a Figure and a FigCanvas
	#
		self.fig = FigureF2D()
		self.canvas = FigCanvas(self, -1, self.fig)

        # Create the navigation toolbar, tied to the canvas
        #
		self.toolbar = NavigationToolbar(self.canvas)

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		sizer.Add(self.toolbar, 0)
		self.SetSizerAndFit(sizer)
       
	def draw(self, r=None):
		title = self.p.fkey.title()+', t='+str(self.p.time)
		if r:
			self.p.field.truncate(r)
			self.p.X = self.p.field['xe']
			self.p.Y = self.p.field['ze']
		self.p.p.status_message('Drawing')
		if self.p.streamline:
			U = self.p.field['Bx']	
			V = self.p.field['Bz']
		else:
			U = V = None	
		if self.p.fkey in self.p.singlelist:
			self.fig.draw_one(title, self.p.X, self.p.Y,
				self.p.field[self.p.fkey], U, V)
		else:
			self.fig.draw_quad(title, self.p.X, self.p.Y,
				self.p.field[self.p.fkey], U, V)
		self.p.p.status_message('Done')


class PanelF2DCtrl(wx.Panel):
	""" Control Panel
		* Radio Box: select a field
		* Draw Button: redraw figure
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to the Main Frame
	#
		self.p = parent

	# Create a Radio Box for field keys
	#
		self.rb_fkey = wx.RadioBox(self, label = 'Select a field',
				choices = self.p.fieldlist,
				majorDimension = 3, style = wx.RA_SPECIFY_COLS)

		flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL
	# Create a Text Control to modify time
	#
		st_time = wx.StaticText(self, label = 'Time:')
		self.tc_time = wx.TextCtrl(self)
		sizer_time = wx.BoxSizer(wx.HORIZONTAL)
		sizer_time.Add(st_time, 0, flags)
		sizer_time.Add(self.tc_time, 0, flags)

	# Create a Toggle Button to add magnetic field lines
	#
		self.tb_stream = wx.ToggleButton(self,
				label='Magnetic Field Line')

	# Create a Text Control to modify range
	#
		st_range_label = wx.StaticText(self, label = 'Drawing Range:')
		st_range = [ wx.StaticText(self, label = i) \
			for i in ['xmin:','xmax:','zmin:','zmax:']]
		self.tc_range = [wx.SpinCtrl(self,size=(80,-1)) 
			for i in range(4)]
		sizer_range = wx.GridSizer(rows=4, cols=2)
		for i in range(4):
			sizer_range.Add(st_range[i], 0, flags)
			sizer_range.Add(self.tc_range[i], 0, flags)

	# Create Buttons for reloading data and redraw
	#
		self.btn_load = wx.Button(self, label = 'Load')
		self.btn_draw = wx.Button(self, label = 'Draw')
		sizer_refresh = wx.BoxSizer(wx.HORIZONTAL)
		sizer_refresh.Add(self.btn_load, 0, flags)
		sizer_refresh.Add(self.btn_draw, 0, flags)

	# Sizer and Fit
	#
		pad = 3
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.rb_fkey, 0, flags, pad)
		sizer.Add(sizer_time, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(st_range_label, 0, flags)
		sizer.Add(sizer_range, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(self.tb_stream, 0, flags, pad)
		sizer.Add(sizer_refresh, 0, flags, pad)
		self.SetSizerAndFit(sizer)

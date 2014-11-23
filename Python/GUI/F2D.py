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
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar
from mplFig import Figure2D


class PanelF2DDisp(wx.Panel):
	""" Display Panel and PIC data
		* Figure Canvas
		* Navigation Toolbar
	"""
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

        # Create a Figure and a FigCanvas
	#
		self.fig = Figure2D()
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
       
	def draw(self, N, title, Lx, Ly, X, Y, Z, U, V):
		if N == 1:
			self.fig.draw_one(title, Lx, Ly, X, Y, Z, U, V)
		else:
			self.fig.draw_quad(title, Lx, Ly, [X]*4, [Y]*4, Z, U, V)


class PanelF2DCtrl(wx.Panel):
	""" Control Panel
		* Radio Box: select a field
		* Text Ctrl: time
		* Button: magnetic field lines
		* Text Ctrl: grid range
		* Buttons: load data, draw figure
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

	# flags for Text Control
	#
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

	def checklist(self, s):
		for i, j in enumerate(self.p.fieldlist):
			if not j in s:
				self.rb_fkey.EnableItem(i, False)
		

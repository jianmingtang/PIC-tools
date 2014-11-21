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


import os
import wx
import numpy
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar


class FigureF1D(Figure):
	""" The following draw methods are implemented:
		* 1 subplot
		* 4 subplots with individual species
	"""
	def __init__(self, *args, **kwargs):
		Figure.__init__(self, *args, **kwargs)

	def draw_one(self, name, X, Y, Lx, Ly):
		""" Draw a single plot
			name: title of the plot
			X, Y: 1D data
		"""
	# The default ordering for 2D meshgrid is Fortran style
	#
		self.clf()
		self.ax = self.add_subplot(111)
		self.ax.set_xlabel(Lx+' (de)', fontsize=14)
		self.ax.set_ylabel(Ly, fontsize=14)
		self.ax.plot(X, Y)
		self.ax.axis('tight')
		self.ax.set_title(name)
		self.tight_layout()
		self.canvas.draw()

	def draw_quad(self, name, X, Y, Lx, Ly):
		""" Draw 4 subplots
			name: main title of the plots
			X, Y: 1D data
		"""
	# The default ordering for 2D meshgrid is Fortran style
	#
		self.clf()
		for i in range(4):
			self.ax = self.add_subplot('22'+str(i+1))
			self.ax.set_xlabel(Lx+' (de)')
			self.ax.set_ylabel(Ly)
			self.ax.plot(X, Y[i])
			self.ax.axis('tight')
			self.ax.set_title(name+', s='+str(i))
		self.tight_layout()
		self.canvas.draw()


class F1DCtrlPanel(wx.Panel):
	""" Control Panel
		* Radio Box: select a field
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Create a Radio Box for 1D cut direction
	#
		self.rb_cut = wx.RadioBox(self, label = 'Select cut direction',
				choices = ['x','z'])
		self.rb_cut.Bind(wx.EVT_RADIOBOX, self.on_rb_cut)

		flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL

	# Create a Slider for the cut (fixed) value
	#
		self.slr_cut = wx.Slider(self, value = self.p.cut,
				size = (150,-1), minValue = 0,
				style = wx.SL_HORIZONTAL | wx.SL_LABELS)
		self.slr_cut.Bind(wx.EVT_SCROLL,
				self.on_slr_cut)

	# Create Buttons for reloading data and redraw
	#
		btn_load = wx.Button(self, label = 'Reload')
		btn_load.Bind(wx.EVT_BUTTON, self.on_btn_load)
		btn_draw = wx.Button(self, label = 'Redraw')
		btn_draw.Bind(wx.EVT_BUTTON, self.on_btn_draw)
		sizer_refresh = wx.BoxSizer(wx.HORIZONTAL)
		sizer_refresh.Add(btn_load, 0, flags)
		sizer_refresh.Add(btn_draw, 0, flags)

	# Sizer and Fit
	#
		pad = 3
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.rb_cut, 0, flags, pad)
		sizer.Add(self.slr_cut, 100, flags, pad)
		sizer.Add(sizer_refresh, 0, flags, pad)
		self.SetSizerAndFit(sizer)

# Error:
#		if self.p.p.field:
#			self.on_btn_load(None)
#			self.on_btn_draw(None)

	def on_rb_cut(self, event):
		""" Change the field key
		"""
		self.p.cut_dir = self.rb_cut.GetItemLabel(
				self.rb_cut.GetSelection())

	def on_slr_cut(self, event):
		""" Change the cut value
		"""
		self.p.cut = self.slr_cut.GetValue()
		self.on_btn_load(event)
		self.on_btn_draw(event)

	def on_btn_load(self, event):
		""" Reload the data
		"""
		fk = self.p.p.field[self.p.p.fkey]
		if self.p.cut_dir == 'x':
			self.p.X = self.p.p.field['ze']
			self.p.C = self.p.p.field['xe']
		else:
			self.p.X = self.p.p.field['xe']
			self.p.C = self.p.p.field['ze']
		self.slr_cut.SetMax(len(self.p.C)-1)

		if self.p.p.fkey in self.p.p.singlelist:
			if self.p.cut_dir == 'x':
				self.p.Y = fk[:,self.p.cut]
			else:
				self.p.Y = fk[self.p.cut]
		else:
			if self.p.cut_dir == 'x':
				self.p.Y = fk[:,:,self.p.cut]
			else:
				self.p.Y = fk[:,self.p.cut]

	def on_btn_draw(self, event):
		""" Redraw the figure
		"""
		self.p.disp_panel.draw()


class F1DDispPanel(wx.Panel):
	""" Display Panel for F1D
		* Figure Canvas
		* Navigation Toolbar
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent
        
        # Create a Figure and a FigCanvas
	#
		self.fig = FigureF1D()
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
		title = self.p.cut_dir + '= ' + str(self.p.C[self.p.cut])
		title += ', t='+str(self.p.p.time)
		if self.p.cut_dir == 'x':
			Lx = 'Z'
		else:
			Lx = 'X'
		Ly = self.p.p.fkey.title()
		self.p.status_message('Drawing')
		if self.p.p.fkey in self.p.p.singlelist:
			self.fig.draw_one(title, self.p.X, self.p.Y, Lx, Ly)
		else:
			self.fig.draw_quad(title, self.p.X, self.p.Y, Lx, Ly)
		self.p.status_message('Done')

        
class FrameF1D(wx.Frame):
	""" Frame for 1D fields and control parameters
		* Display Panel on the left
		* Control Panel on the right
		* Status Bar at bottom 
	"""
	cut_dir = 'x'
	cut = 0
	X = Y = C = None
	def __init__(self, parent, *args, **kwargs):
		""" Create the Main Frame
		"""
		wx.Frame.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Create a Display Panel
	#
		self.disp_panel = F1DDispPanel(self)

	# Create a Control Panel
	#
		self.ctrl_panel = F1DCtrlPanel(self)

	# Create the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.disp_panel, 1, wx.EXPAND)
		sizer.Add(self.ctrl_panel, 0)
		self.SetSizerAndFit(sizer)

	def status_message(self, msg):
		""" Display a message in Status Bar
		"""
		self.status_bar.SetStatusText(msg)

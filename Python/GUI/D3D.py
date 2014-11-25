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
from mplFig import Figure3D
import PIC


class PanelD3DDisp(wx.Panel):
	""" Display Panel and PIC data
		* Figure Canvas
		* Navigation Toolbar
	"""
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

        # Create a Figure and a FigCanvas
	#
		self.fig = Figure3D()
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
       
	def draw(self, title, Lx, Ly, Lz, X, Y, Z, f, iso):
		self.fig.draw_one(title, Lx, Ly, Lz, X, Y, Z, f, iso)


class PanelD3DCtrl(wx.Panel):
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
#		self.rb_fkey = wx.RadioBox(self, label = 'Select a field',
#				choices = self.p.fieldlist,
#				majorDimension = 3, style = wx.RA_SPECIFY_COLS)

	# flags for Text Control
	#
		flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL

	# Create a Text Control to show isovalue
	#
		st_iso = wx.StaticText(self, label = 'isovalue:')
		self.tc_iso = wx.TextCtrl(self)
		sizer_iso = wx.BoxSizer(wx.HORIZONTAL)
		sizer_iso.Add(st_iso, 0, flags)
		sizer_iso.Add(self.tc_iso, 0, flags)

		self.slr_iso = wx.Slider(self, value = self.p.iso,
				size = (150,-1), minValue = 0, maxValue = 1,
				style = wx.SL_HORIZONTAL | wx.SL_LABELS)

	# Create a Text Control to modify range
	#
		st_range_label = wx.StaticText(self, label = 'Drawing Range:')
		st_range = [ wx.StaticText(self, label = i+j) \
			for i in ['x','y','z'] for j in ['min:','max:'] ]
		self.tc_range = [wx.SpinCtrl(self,size=(80,-1)) 
			for i in range(6)]
		sizer_range = wx.GridSizer(rows=6, cols=2)
		for i in range(6):
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
#		sizer.Add(self.rb_fkey, 0, flags, pad)
		sizer.Add(sizer_iso, 0, flags, pad)
		sizer.Add(self.slr_iso, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(st_range_label, 0, flags)
		sizer.Add(sizer_range, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(sizer_refresh, 0, flags, pad)
		self.SetSizerAndFit(sizer)


class PanelD3D(wx.Panel):
	""" D3D Panel (Controller)
	"""
# control variables
#
	grid = 101
	iso = 0.2

# data
#
	pdist = None

	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Add a control Panel and a display Panel
	#
		self.ctrl = PanelD3DCtrl(self)
		self.disp = PanelD3DDisp(self)

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.disp, 1, wx.EXPAND)
		sizer.Add(self.ctrl, 0)
		self.SetSizerAndFit(sizer)

	# Load data from file
	#
		self.load_data()
		self.set_range()

	# Draw
	#
		self.on_btn_draw(None)

	# Bind to control Panel events
	#
#		self.Bind(wx.EVT_RADIOBOX, self.on_rb_key,
#				self.ctrl.rb_key)
		self.Bind(wx.EVT_BUTTON, self.on_btn_load,
				self.ctrl.btn_load)
		self.Bind(wx.EVT_BUTTON, self.on_btn_draw,
				self.ctrl.btn_draw)

	def load_data(self):
		""" Update pdist if the file is valid
		"""
		if not self.p.pathname: return

		f = self.p.pathname
		try:
			self.p.status_message('Loading')
			self.pdist = PIC.DistNASA(f, self.grid)
			self.p.status_message('Done')
		except:
			self.p.status_message('Error: Load Fail!')
			self.pdist = None
		if self.pdist:
			self.p.status_message('Loaded ' + f)

	def set_range(self):
		""" Reset the grid range
		"""
		for i in range(6):
			self.ctrl.tc_range[i].SetRange(0, self.grid)
		for i in range(3):
			self.ctrl.tc_range[i+i].SetValue(0)
			self.ctrl.tc_range[i+i+1].SetValue(self.grid)

	def on_btn_load(self, event):
		""" Load the data
		"""
		self.p.get_path_from_dirctrl(None)
		self.load_data()

	def on_btn_draw(self, event):
		""" Draw the figure
		"""
		if not self.pdist:
			dlg = wx.MessageDialog(self, 'Load Data First!',
					'Error', wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		r = [self.ctrl.tc_range[i].GetValue() for i in range(6)]
		if r[0] >= r[1] or r[2] >= r[3] or r[4] >= r[5] or min(r) < 0:
			r = None
		else:
			self.pdist.truncate(r)
		title = 'f(V)'
		Lx = 'Vx'
		Ly = 'Vy'
		Lz = 'Vz'
		X = Y = Z = self.pdist['axes'][0]
		f = self.pdist['fxyz'][1].transpose()
		iso = max(f.ravel()) * self.iso
		self.p.status_message('Drawing')
		self.disp.draw(title, Lx, Ly, Lz, X, Y, Z, f, iso)
		self.p.status_message('Done')

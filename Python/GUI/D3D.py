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
       
	def draw(self, title, Lx, Ly, Lz, X, Y, Z, f, iso, elev, azim):
		self.fig.draw_one(title,Lx,Ly,Lz,X,Y,Z,f,iso,elev,azim)


class PanelD3DCtrl(wx.Panel):
	""" Control Panel
		* Radio Box: select a plot
		* Text Ctrl: angles
		* Buttons: load data, draw figure
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to the Main Frame
	#
		self.p = parent

	# Create a Radio Box for plot type
	#
		plotlist = ['io1','el1','io2','el2','ion','ele']
		self.rb_plot = wx.RadioBox(self, label = 'Select a plot',
				choices = plotlist,
				majorDimension = 3, style = wx.RA_SPECIFY_COLS)

	# flags for Text Control
	#
		flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL

	# Create a Text Control and a Slider to modify isovalue
	#
		st_iso = wx.StaticText(self, label = 'isovalue:')
		self.tc_iso = wx.TextCtrl(self)
		sizer_iso = wx.BoxSizer(wx.HORIZONTAL)
		sizer_iso.Add(st_iso, 0, flags)
		sizer_iso.Add(self.tc_iso, 0, flags)

		self.slr_iso = wx.Slider(self, value = self.p.iso,
				size = (150,-1), minValue = 10, maxValue = 90,
				style = wx.SL_HORIZONTAL | wx.SL_LABELS)

	# Create a Text Control to modify range
	#
		st_range_label = wx.StaticText(self, label = 'Drawing Range:')
		st_range = [ wx.StaticText(self, label = i+j) \
			for i in ['x','y','z'] for j in ['min:','max:'] ]
		self.sc_range = [wx.SpinCtrl(self,size=(80,-1)) 
			for i in range(6)]
		for i in range(2,6):
			self.sc_range[i].Enable(False)
		sizer_range = wx.GridSizer(rows=6, cols=2)
		for i in range(6):
			sizer_range.Add(st_range[i], 0, flags)
			sizer_range.Add(self.sc_range[i], 0, flags)

	# Create a Text Control for viewing angles
	#
		st_elev = wx.StaticText(self, label = 'elevation:')
		st_azim = wx.StaticText(self, label = 'azimuth:')
		self.sc_elev = wx.SpinCtrl(self, min=-90, max=90, initial=20)
		self.sc_azim = wx.SpinCtrl(self, min=-179, max=180, initial=40)
		sizer_view = wx.BoxSizer(wx.VERTICAL)
		sizer_view.Add(st_elev, 0, flags)
		sizer_view.Add(self.sc_elev, 0, flags)
		sizer_view.Add(st_azim, 0, flags)
		sizer_view.Add(self.sc_azim, 0, flags)

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
		sizer.Add(self.rb_plot, 0, flags, pad)
		sizer.Add(sizer_iso, 0, flags, pad)
		sizer.Add(self.slr_iso, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(st_range_label, 0, flags)
		sizer.Add(sizer_range, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(sizer_view, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(sizer_refresh, 0, flags, pad)
		self.SetSizerAndFit(sizer)


class PanelD3D(wx.Panel):
	""" D3D Panel (Controller)
	"""
# control variables
#
	grid = 101
	iso = 20

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

	# Initialize key and Draw
	#
		self.on_rb_plot(None)

	# Bind to control Panel events
	#
		self.Bind(wx.EVT_RADIOBOX, self.on_rb_plot, self.ctrl.rb_plot)
		self.Bind(wx.EVT_SCROLL, self.on_slr_iso, self.ctrl.slr_iso)
		self.Bind(wx.EVT_BUTTON, self.on_btn_load, self.ctrl.btn_load)
		self.Bind(wx.EVT_BUTTON, self.on_btn_draw, self.ctrl.btn_draw)

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
			self.ctrl.sc_range[i].SetRange(0, self.grid)
		for i in range(3):
			self.ctrl.sc_range[i+i].SetValue(0)
			self.ctrl.sc_range[i+i+1].SetValue(self.grid)

	def on_rb_plot(self, event):
		self.plot = self.ctrl.rb_plot.GetSelection()
		self.on_btn_draw(None)

	def on_slr_iso(self, event):
		""" Set iso percentage
		"""
		self.iso = self.ctrl.slr_iso.GetValue()

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

		r = [self.ctrl.sc_range[i].GetValue() for i in range(6)]
		if r[0] >= r[1] or r[2] >= r[3] or r[4] >= r[5] or min(r) < 0:
			r = None
		else:
			self.pdist.truncate(r)
		location = 'x=(%4g,%4g), z=(%4g,%4g)\n' % (
			self.pdist.data['xlo'], self.pdist.data['xhi'],
			self.pdist.data['zlo'], self.pdist.data['zhi'])
		title = 'f(V), ' + location
		Lx = 'Vx'
		Ly = 'Vy'
		Lz = 'Vz'
		if self.plot < 4:
			X = Y = Z = self.pdist['axes'][self.plot]
			f = self.pdist['fxyz'][self.plot]
		elif self.plot == 4:
			X = Y = Z = self.pdist['axes'][0]
			f = self.pdist['fxyz'][0]+self.pdist['fxyz'][2]
		elif self.plot == 5:
			X = Y = Z = self.pdist['axes'][1]
			f = self.pdist['fxyz'][1]+self.pdist['fxyz'][3]
		print f.shape
		iso = max(f.ravel()) * self.iso / 100
		self.ctrl.tc_iso.SetValue(str(iso))
		elev = self.ctrl.sc_elev.GetValue()
		azim = self.ctrl.sc_azim.GetValue()
		self.p.status_message('Drawing')
		self.disp.draw(title, Lx, Ly, Lz, X, Y, Z, f.transpose(),
				iso, elev, azim)
		self.p.status_message('Done')

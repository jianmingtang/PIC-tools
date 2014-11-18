#!/usr/bin/env python


#    Draw PIC field data using matplotlib and wxPython
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


import os
import wx
import numpy
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar
import PIC


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
		self.ax.streamplot(X,Y,U,V,color='k',density=[5,0.7])


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
				style = wx.SL_LABELS)
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


class F2DCtrlPanel(wx.Panel):
	""" Control Panel
		* Radio Box: select a field
		* Draw Button: redraw figure
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Create a Radio Box for field keys
	#
		self.rb_fkey = wx.RadioBox(self, label = 'Select a field',
				choices = self.p.fieldlist,
				majorDimension = 3, style = wx.RA_SPECIFY_COLS)
		self.rb_fkey.Bind(wx.EVT_RADIOBOX, self.on_rb_fkey)

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
		tb_stream = wx.ToggleButton(self, label='Magnetic Field Line')
		tb_stream.Bind(wx.EVT_TOGGLEBUTTON, self.on_tb_stream)
		tb_stream.SetValue(False)

	# Create a Text Control to modify range
	#
		st_range_label = wx.StaticText(self, label = 'Drawing Range:')
		st_range = [ wx.StaticText(self, label = i) \
			for i in ['xmin:','xmax:','zmin:','zmax:']]
		self.tc_range = [wx.SpinCtrl(self,size=(80,-1)) 
			for i in range(4)]
		self.tc_range[0].SetRange(0, self.p.grid[0])
		self.tc_range[1].SetRange(0, self.p.grid[0])
		self.tc_range[2].SetRange(0, self.p.grid[2])
		self.tc_range[3].SetRange(0, self.p.grid[2])
		sizer_range = wx.GridSizer(rows=4, cols=2)
		for i in range(4):
			sizer_range.Add(st_range[i], 0, flags)
			sizer_range.Add(self.tc_range[i], 0, flags)

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
		sizer.Add(self.rb_fkey, 0, flags, pad)
		sizer.Add(sizer_time, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(st_range_label, 0, flags)
		sizer.Add(sizer_range, 0, flags, pad)
		sizer.Add(wx.StaticLine(self), 0, flags|wx.EXPAND, pad)
		sizer.Add(tb_stream, 0, flags, pad)
		sizer.Add(sizer_refresh, 0, flags, pad)
		self.SetSizerAndFit(sizer)

	def on_rb_fkey(self, event):
		""" Change the field key
		"""
		self.p.fkey = self.rb_fkey.GetItemLabel(
				self.rb_fkey.GetSelection())

	def on_tb_stream(self, event):
		""" Toggle stream lines
		"""
		self.p.streamline = not self.p.streamline
		self.p.disp_panel.draw()

	def on_btn_load(self, event):
		""" Reload the data
		"""
		time = self.tc_time.GetValue()
		self.p.filename = 'fields-' + time.zfill(5) + '.dat'
		f = os.path.join(self.p.dirname, self.p.filename)
		if os.path.isfile(f):
			self.p.time = time.lstrip('0')
			self.p.update_data()

	def on_btn_draw(self, event):
		""" Redraw the figure
		"""
		r = [self.tc_range[i].GetValue() for i in range(4)]
		if r[0] >= r[1] or r[2] >= r[3]:
			r = None
		if self.p.field:
			self.p.disp_panel.draw(r)
		else:
			dlg = wx.MessageDialog(self, 'Load Data First!',
					'Error', wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
        
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

        
class F2DDispPanel(wx.Panel):
	""" Display Panel and PIC data
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
		self.p.status_message('Drawing')
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
		self.p.status_message('Done')


class MainMenuBar(wx.MenuBar):
	""" Main Menu Bar
		* File Menu
		* Help Menu
	"""
	def __init__(self, parent, *args, **kwargs):
		""" Create the Main Menu Bar
		"""
		wx.MenuBar.__init__(self, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Create a File Menu
	#
		menu_file = wx.Menu()
		m_file_open = menu_file.Append(wx.ID_OPEN, 'Open',
			'Open a PIC data file')
		self.Bind(wx.EVT_MENU, self.on_file_open, m_file_open)
		m_file_save = menu_file.Append(wx.ID_SAVE, 'Save',
			'Save the figure to a PNG file')
		self.Bind(wx.EVT_MENU, self.on_file_save, m_file_save)
		menu_file.AppendSeparator()
		m_file_exit = menu_file.Append(wx.ID_EXIT, 'Quit')
		self.Bind(wx.EVT_MENU, self.on_file_exit, m_file_exit)
		self.Append(menu_file, 'File')

       	# Create a Window Menu
	#
		menu_frame = wx.Menu()
		m_frame_F1D = menu_frame.Append(wx.ID_ANY, 'Field 1D Plot',
			'Open a Frame for 1D field plot')
		self.Bind(wx.EVT_MENU, self.on_frame_F1D, m_frame_F1D)
		m_frame_D3D = menu_frame.Append(wx.ID_ANY, 'Dist 3D Plot',
			'Open a Frame for 3D distribution plot')
		self.Bind(wx.EVT_MENU, self.on_frame_D3D, m_frame_D3D)
		self.Append(menu_frame, 'Window')

       	# Create a Help Menu
	#
		menu_help = wx.Menu()
		m_help_about = menu_help.Append(wx.ID_ABOUT, 'About',
			'About PIC Draw')
		self.Bind(wx.EVT_MENU, self.on_help_about, m_help_about)
		self.Append(menu_help, 'Help')

	# Attach the Menu Bar to the Main Frame
	#
		parent.SetMenuBar(self)

	def on_file_open(self, event):
		""" Open a single PIC data file for plotting
		"""
		dlg = wx.FileDialog(self, defaultDir = os.getcwd(),
				style = wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.p.dirname = dlg.GetDirectory()
			self.p.filename = dlg.GetFilename()
			self.p.time = self.p.filename[7:12].lstrip('0')
			self.p.update_data()
			self.p.ctrl_panel.tc_time.SetValue(self.p.time)
			self.p.ctrl_panel.tc_range[1].SetValue(self.p.grid[0])
			self.p.ctrl_panel.tc_range[3].SetValue(self.p.grid[2])

	def on_file_save(self, event):
		""" Save the current Figure to a PNG file
		"""
		ffilter = 'Portable Network Graphics (*.png)|*.png'
		fname = self.p.fkey.title()+'_t'+str(self.p.time)
        
		dlg = wx.FileDialog(self, defaultDir = os.getcwd(),
				defaultFile = fname, wildcard = ffilter,
				style = wx.FD_SAVE)
        
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.p.disp_panel.canvas.print_figure(path)
			self.p.status_message("Saved to %s" % path)
        
	def on_file_exit(self, event):
		""" Close the Main Frame
		"""
		if self.p.frame_F1D:  self.p.frame_F1D.Destroy()
		if self.p.frame_D3D:  self.p.frame_D3D.Destroy()
		self.p.Destroy()
       
	def on_frame_F1D(self, event):
		self.p.frame_F1D = FrameF1D(self.p, title = 'Field 1D')
		self.p.frame_F1D.Show()

	def on_frame_D3D(self, event):
		self.p.frame_D3D = FrameD3D(self.p, title = 'Distribution 3D')
		self.p.frame_D3D.Show()

	def on_help_about(self, event):
		msg = """ PIC Draw 0.1
	* Draw PIC data using matplotlib and wxPython
	* Copyright (C) 2014 Jian-Ming Tang <jmtang@mailaps.org>
	"""
		dlg = wx.MessageDialog(self, msg, 'About', wx.OK)
		dlg.ShowModal()
		dlg.Destroy()


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


class FrameD3D(wx.Frame):
	""" Frame for 3D distributions and control parameters
		* Display Panel on the left
		* Control Panel on the right
		* Status Bar at bottom 
	"""
	def __init__(self, parent, *args, **kwargs):
		""" Create the Main Frame
		"""
		wx.Frame.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Create a Display Panel
	#
#		self.disp_panel = DispPanel(self)

	# Create a Control Panel
	#
#		self.ctrl_panel = CtrlPanel(self)

	# Create the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.HORIZONTAL)
#		sizer.Add(self.disp_panel, 1, wx.EXPAND)
#		sizer.Add(self.ctrl_panel, 0)
		self.SetSizerAndFit(sizer)

	def status_message(self, msg):
		""" Display a message in Status Bar
		"""
		self.status_bar.SetStatusText(msg)


class FrameF2D(wx.Frame):
	""" (Main Frame) Frame for 2D fields and control parameters
		* Menu Bar at top
		* Display Panel on the left
		* Control Panel on the right
		* Status Bar at bottom 
	"""
	dirname = ''
	filename = ''
	grid = [1000, 1, 800]
	time = ''
	fkey = 'Bx'
	fieldlist = ['Bx','By','Bz','Ex','Ey','Ez','vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']
	singlelist = fieldlist[:6]
	streamline = False
	X = None; Y = None; field = None
	frame_F1D = None
	frame_D3D = None

	def __init__(self, *args, **kwargs):
		""" Create the Main Frame
		"""
		wx.Frame.__init__(self, *args, **kwargs)

	# Create the Main Menu Bar
	#
		MainMenuBar(self)

	# Create a Display Panel
	#
		self.disp_panel = F2DDispPanel(self)

	# Create a Control Panel
	#
		self.ctrl_panel = F2DCtrlPanel(self)

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

	def update_data(self):
		f = os.path.join(self.dirname, self.filename)
		self.status_message('Loading')
		self.field = PIC.FieldNASA(f, self.grid)
		self.status_message('Loaded data from %s' % f)
		self.X = self.field['xe']
		self.Y = self.field['ze']


### main program ###
if __name__ == "__main__": 

	app = wx.App()
	frame = FrameF2D(None, title='PIC Draw (Field 2D)')
	frame.Show()
	app.MainLoop()

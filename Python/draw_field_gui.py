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


class Figure2D(Figure):
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

			
class CtrlPanel(wx.Panel):
	""" Control Panel
		* Radio Box: select a field
		* Draw Button: redraw figure
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

		self.rb_fkey = wx.RadioBox(self, label = 'Select a field',
				choices = self.p.fieldlist,
				majorDimension = 3, style = wx.RA_SPECIFY_COLS)
		self.rb_fkey.Bind(wx.EVT_RADIOBOX, self.on_field_select)

		self.btn_draw = wx.Button(self, label = 'Draw')
		self.Bind(wx.EVT_BUTTON, self.on_draw_button, self.btn_draw)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.rb_fkey, 0, wx.ALIGN_LEFT|wx.ALL, 10)
		sizer.Add(self.btn_draw, 0, border=3)
		self.SetSizerAndFit(sizer)

	def on_field_select(self, event):
		""" Change the field key
		"""
		self.p.fkey = self.rb_fkey.GetItemLabel(
				self.rb_fkey.GetSelection())

	def on_draw_button(self, event):
		""" Redraw the figure
		"""
		self.p.disp_panel.draw()
		
        
class DispPanel(wx.Panel):
	""" Display Panel and PIC data
		* Figure Canvas
		* Navigation Toolbar
	"""
	X = None; Y = None; field = None

	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent
        
        # Create a Figure and a FigCanvas
	#
		self.fig = Figure2D()
		self.canvas = FigCanvas(self, -1, self.fig)

        # Create the navigation toolbar, tied to the canvas
        #
		self.toolbar = NavigationToolbar(self.canvas)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		sizer.Add(self.toolbar, 0)
		self.SetSizerAndFit(sizer)
       
	def draw(self):
		title = self.p.fkey.title()+', t='+str(self.p.time)
		if self.p.fkey in self.p.singlelist:
			self.fig.draw_one(title, self.X, self.Y,
				self.field[self.p.fkey],
				self.field['Bx'],self.field['Bz'])
		else:
			self.fig.draw_quad(title, self.X, self.Y,
				self.field[self.p.fkey],
				self.field['Bx'],self.field['Bz'])

	def update_data(self):
		f = os.path.join(self.p.dirname, self.p.filename)
		self.field = PIC.FieldNASA(f, self.p.grid)
		self.p.status_message("Loaded data from %s" % f)
		self.X = self.field['xe']
		self.Y = self.field['ze']
		 

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
			self.p.dirname = dirname = dlg.GetDirectory()
			self.p.filename = filename = dlg.GetFilename()
			self.p.time = int(filename[7:12])
			self.p.disp_panel.update_data()

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
		self.p.Destroy()
        
	def on_help_about(self, event):
		msg = """ PIC Draw 0.1
* Draw PIC data using matplotlib and wxPython
* Copyright (C) 2014 Jian-Ming Tang <jmtang@mailaps.org>
"""
		dlg = wx.MessageDialog(self, msg, "About", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()


class MainFrame(wx.Frame):
	""" Main Frame and control parameters
		* Menu Bar at top
		* Display Panel on the left
		* Control Panel on the right
		* Status Bar at bottom 
	"""
	dirname = ''
	filename = ''
	grid = [1000, 1, 800]
	time = 0
	fkey = 'Bx'
	fieldlist = ['Bx','By','Bz','Ex','Ey','Ez','vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']
	singlelist = fieldlist[:6]

	def __init__(self, *args, **kwargs):
		""" Create the Main Frame
		"""
		wx.Frame.__init__(self, *args, **kwargs)

	# Create the Main Menu Bar
	#
		MainMenuBar(self)

	# Create a Display Panel
	#
		self.disp_panel = DispPanel(self)

	# Create a Control Panel
	#
		self.ctrl_panel = CtrlPanel(self)

	# Create the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.disp_panel, 1, wx.EXPAND)
		sizer.Add(self.ctrl_panel, 0)
		self.SetSizerAndFit(sizer)

	def status_message(self, msg):
		""" Display a message in Status Bar
		"""
		self.status_bar.SetStatusText(msg)
    

### main program ###
if __name__ == "__main__": 

	app = wx.App()
	frame = MainFrame(None, title="PIC Draw")
	frame.Show()
	app.MainLoop()

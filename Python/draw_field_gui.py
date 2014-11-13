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
	""" This class draw two types of figures:
		1. 4 panels with individual species
		2. 1 panel
	"""
	def __init__(self, *args, **kwargs):
		Figure.__init__(self, *args, **kwargs)

	def draw_quad(self, name, X, Y, fZ):
		""" Create a 4-panel figure
			name: title of the figure
			X, Y: 1D axes data
			fZ: 2D data set (Fortran indexing)
		"""
# The default ordering for 2D meshgrid is Fortran style
		fX, fY = numpy.meshgrid(X, Y)
		self.clf()
		for i in range(4):
			ax = self.add_subplot('22'+str(i+1))
			ax.set_xlabel('X (de)')
			ax.set_ylabel('Z (de)')
			pcm = ax.pcolormesh(fX, fY, fZ[i])
			ax.axis('tight')
			self.colorbar(pcm)
			ax.set_title(name+', s='+str(i))
		self.canvas.draw()

	def draw_one(self, name, X, Y, fZ):
		""" Create a 1-panel figure
			name: title of the figure
			X, Y: 1D axes data
			fZ: 2D data set (Fortran indexing)
		"""
		fX, fY = numpy.meshgrid(X, Y)
		self.clf()
		ax = self.add_subplot(111)
		ax.set_xlabel('X (de)',fontsize=14)
		ax.set_ylabel('Z (de)',fontsize=14)
		pcm = ax.pcolormesh(fX, fY, fZ)
		ax.axis('tight')
		self.colorbar(pcm)
		ax.set_title(name)

		self.canvas.draw()

#	def add_streamline(self, X, Y, U, V):
#		plt.streamplot(X,Y,U,V,color='k',density=[5,0.7])

			
class CtrlPanel(wx.Panel):
	""" Main Panel
		* mpl navigation toolbar
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

		self.p = parent

		listoffields = ['Bx','By','Bz','Ex','Ey','Ez',
			'vxs','vys','vzs','pxx','pyy','pzz','pxy','pxz','pyz',
			'dns']
		self.RB = wx.RadioBox(self, label='Select a field',
				choices=listoffields,
				majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.RB.Bind(wx.EVT_RADIOBOX, self.on_field_select)

		self.drawbutton = wx.Button(self, label='Draw')
		self.Bind(wx.EVT_BUTTON, self.on_draw_button, self.drawbutton)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.RB, 0, wx.ALIGN_LEFT|wx.ALL, 10)
		sizer.Add(self.drawbutton, 0, border=3)
		self.SetSizerAndFit(sizer)

	def on_field_select(self, event):
		self.p.key = self.RB.GetItemLabel(self.RB.GetSelection())

	def on_draw_button(self, event):
		title = self.p.key.title() + ', t=' + str(self.p.time)
#		quad = ['vxs','vys','vzs','pxx','pyy','pzz','pxy','pxz','pyz']
		single = ['Bx','By','Bz','Ex','Ey','Ez']
		if self.p.key in single:
			self.p.fig.draw_one(title,
				self.p.X, self.p.Y, self.p.field[self.p.key])
		else:
			self.p.fig.draw_quad(title,
				self.p.X, self.p.Y, self.p.field[self.p.key])
		
        
class DispPanel(wx.Panel):
	""" Main Panel
		* mpl navigation toolbar
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

		self.p = parent
        
        # Create the mpl Figure and FigCanvas objects. 
#		self.fig = Figure2D(title)
		self.canvas = FigCanvas(self, -1, self.p.fig)

        # Create the navigation toolbar, tied to the canvas
        #
		self.toolbar = NavigationToolbar(self.canvas)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		sizer.Add(self.toolbar, 0)
		self.SetSizerAndFit(sizer)
        

class MainMenuBar(wx.MenuBar):
	""" Main menu.
	"""
	def __init__(self, parent, *args, **kwargs):
		wx.MenuBar.__init__(self, *args, **kwargs)

		self.p = parent

		# Set up File Menu
		menu_file = wx.Menu()
		m_file_open = menu_file.Append(wx.ID_OPEN, 'Open',
			'Open data file')
		self.Bind(wx.EVT_MENU, self.on_file_open, m_file_open)
		m_file_save = menu_file.Append(wx.ID_SAVE, 'Save',
			'Save figure to file')
		self.Bind(wx.EVT_MENU, self.on_file_save, m_file_save)
		menu_file.AppendSeparator()
		m_file_exit = menu_file.Append(wx.ID_EXIT, 'Quit')
		self.Bind(wx.EVT_MENU, self.on_file_exit, m_file_exit)
		self.Append(menu_file, 'File')

        	# Set up Help Menu
		menu_help = wx.Menu()
		m_help_about = menu_help.Append(wx.ID_ABOUT, 'About',
			'About PIC Draw')
		self.Bind(wx.EVT_MENU, self.on_help_about, m_help_about)
		self.Append(menu_help, 'Help')

		parent.SetMenuBar(self)

	def on_file_open(self, event):
		dlg = wx.FileDialog(self, message = 'Open data file',
			defaultDir = os.getcwd(), style=wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.p.dirname = dirname = dlg.GetDirectory()
			self.p.filename = filename = dlg.GetFilename()
			f = os.path.join(dirname, filename)
			self.p.field = field = PIC.FieldNASA(f, self.p.grid)
			self.status_message("Load data from %s" % f)
			self.p.X = field['xe']
			self.p.Y = field['ze']
			self.p.time = int(filename[7:12])

	def on_file_save(self, event):
		file_choices = 'PNG (*.png)|*.png'
        
		dlg = wx.FileDialog(self, message = 'Save current figure',
			defaultDir = os.getcwd(), defaultFile = 'plot.png',
			wildcard = file_choices, style = wx.FD_SAVE)
        
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.p.disp_panel.canvas.print_figure(path)
			self.status_message("Saved to %s" % path)
        
	def on_file_exit(self, event):
		self.p.Destroy()
        
	def on_help_about(self, event):
		msg = """ PIC Draw uses matplotlib and wxPython:
		 * matplotlib navigation bar
		 * File menu
		"""
		dlg = wx.MessageDialog(self, msg, "About", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
    
	def status_message(self, msg, flash_len_ms=3000):
		self.p.statusbar.SetStatusText(msg)
#		self.timeroff = wx.Timer(self)
#		self.Bind(wx.EVT_TIMER, self.on_status_off, self.timeroff)
#		self.timeroff.Start(flash_len_ms, oneShot=True)
    
	def on_status_off(self, event):
		self.parent.statusbar.SetStatusText('')


class MainFrame(wx.Frame):
	""" Main window frame and control variables.
	"""
	dirname = ''
	filename = ''
	grid = [1000, 1, 800]
	field = None
	time = 0
	X = []
	Y = []
	key = 'Bx'
	fig = Figure2D()

	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)

		MainMenuBar(self)
		self.disp_panel = DispPanel(self)
		self.ctrl_panel = CtrlPanel(self)
		self.statusbar = self.CreateStatusBar()

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.disp_panel, 1, wx.EXPAND)
		sizer.Add(self.ctrl_panel, 0)
		self.SetSizerAndFit(sizer)




### main program ###
if __name__ == "__main__": 

	app = wx.App()
	frame = MainFrame(None, title="PIC Draw")
	frame.Show()
	app.MainLoop()

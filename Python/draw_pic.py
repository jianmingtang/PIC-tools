#!/usr/bin/env python


#    Draw PIC data using matplotlib and wxPython
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
from wx.lib.pubsub import pub
import PIC
import GUI


class PanelF2D(wx.Panel):
	""" F2D Panel (Controller)
	"""
# control variables
#
	fieldlist = ['Bx','By','Bz','Ex','Ey','Ez','vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']
	singlelist = fieldlist[:6]
	fkey = fieldlist[0]
	streamline = False

	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

		self.ctrlF2D = GUI.PanelF2DCtrl(self)
		self.dispF2D = GUI.PanelF2DDisp(self)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.dispF2D, 1, wx.EXPAND)
		sizer.Add(self.ctrlF2D, 0)
		self.SetSizerAndFit(sizer)

		self.ctrlF2D.tb_stream.SetValue(False)
		
		if self.p.dirname and self.p.filename:
			self.update_data()

		self.Bind(wx.EVT_RADIOBOX, self.on_rb_fkey,
				self.ctrlF2D.rb_fkey)
		self.Bind(wx.EVT_TOGGLEBUTTON, self.on_tb_stream,
				self.ctrlF2D.tb_stream)
		self.Bind(wx.EVT_BUTTON, self.on_btn_load,
				self.ctrlF2D.btn_load)
		self.Bind(wx.EVT_BUTTON, self.on_btn_draw,
				self.ctrlF2D.btn_draw)
		pub.subscribe(self.update_data, 'File Open')

	def update_data(self):
		f = os.path.join(self.p.dirname, self.p.filename)
		try:
			self.field = PIC.FieldNASA(f)
		except:
			self.p.status_message('Error: Load Fail!')
			self.field = None
		if self.field:
			self.p.status_message('Loaded ' + f)
			self.time = self.p.filename[7:12].lstrip('0')
			self.ctrlF2D.tc_time.SetValue(self.time)
			self.set_range()

	def set_range(self):
		nx = self.field.data['nnx']
		nz = self.field.data['nnz']
		self.ctrlF2D.tc_range[0].SetRange(0, nx)
		self.ctrlF2D.tc_range[1].SetRange(0, nx)
		self.ctrlF2D.tc_range[1].SetValue(nx)
		self.ctrlF2D.tc_range[2].SetRange(0, nz)
		self.ctrlF2D.tc_range[3].SetRange(0, nz)
		self.ctrlF2D.tc_range[3].SetValue(nz)

	def on_rb_fkey(self, event):
		""" Change the field key
		"""
		self.fkey = self.ctrlF2D.rb_fkey.GetItemLabel(
				self.ctrlF2D.rb_fkey.GetSelection())

	def on_tb_stream(self, event):
		""" Toggle stream lines
		"""
		self.streamline = not self.streamline
		self.dispF2D.draw()

	def on_btn_load(self, event):
		""" Load the data
		"""
		time = self.ctrlF2D.tc_time.GetValue()
		self.p.filename = 'fields-' + time.zfill(5) + '.dat'
		self.update_data()

	def on_btn_draw(self, event):
		""" Draw the figure
		"""
		r = [self.ctrlF2D.tc_range[i].GetValue() for i in range(4)]
		if r[0] >= r[1] or r[2] >= r[3]:
			r = None
		if self.field:
			self.dispF2D.draw(r)
		else:
			dlg = wx.MessageDialog(self, 'Load Data First!',
					'Error', wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()


class PanelD3D(wx.Panel):
	""" D3D Panel (Controller)
	"""
# control variables
#
	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

#		ctrl_panel = GUI.PanelD3DCtrl(self)
#		disp_panel = GUI.PanelD3DDisp(self)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
#		sizer.Add(disp_panel, 1, wx.EXPAND)
#		sizer.Add(ctrl_panel, 0)
		self.SetSizerAndFit(sizer)
		self.p.Fit()


class PanelBackground(wx.Panel):
	"""  Panel with a background image
	"""
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

	# Add the backgroud image
	#
		image = wx.StaticBitmap(self, bitmap = wx.BitmapFromImage(
			wx.Image('draw_pic.png', wx.BITMAP_TYPE_PNG)))

		sizer = wx.GridSizer()
		sizer.Add(image, 0, wx.ALIGN_CENTER)
		self.SetSizer(sizer)		


class MainMenuBar(wx.MenuBar):
	""" Main Menu Bar
		* File Menu
		* Window Menu
		* Help Menu
	"""
	labelF2D = 'Field 2D Plot'
	labelF1D = 'Field 1D Plot'
	labelD3D = 'Distribution 3D Plot'
	labelD2D = 'Distribution 2D Plot'

	def __init__(self, *args, **kwargs):
		""" Create the Main Menu Bar
		"""
		wx.MenuBar.__init__(self,  *args, **kwargs)

	# Create a File Menu
	#
		menu_file = wx.Menu()
		self.file_new = menu_file.Append(wx.ID_NEW, 'New',
			'Open a new window')
		self.file_open = menu_file.Append(wx.ID_OPEN, 'Open',
			'Open a PIC data file')
		self.file_save = menu_file.Append(wx.ID_SAVE, 'Save',
			'Save the figure to a PNG file')
		self.file_save.Enable(False)
		menu_file.AppendSeparator()
		self.file_exit = menu_file.Append(wx.ID_EXIT, 'Quit')
		self.Append(menu_file, 'File')

	# Create a Window Menu
	#
		menu_frame = wx.Menu()
		self.frame_F2D = menu_frame.Append(wx.ID_ANY, self.labelF2D,
			'Open a Frame for 2D field plot')
		self.frame_F1D = menu_frame.Append(wx.ID_ANY, self.labelF1D,
			'Open a Frame for 1D field plot')
		self.frame_F1D.Enable(False)
		self.frame_D3D = menu_frame.Append(wx.ID_ANY, self.labelD3D,
			'Open a Frame for 3D distribution plot')
		self.frame_D2D = menu_frame.Append(wx.ID_ANY, self.labelD2D,
			'Open a Frame for 2D distribution plot')
		self.frame_D2D.Enable(False)
		self.Append(menu_frame, 'Window')

       	# Create a Help Menu
	#
		menu_help = wx.Menu()
		help_about = menu_help.Append(wx.ID_ABOUT, 'About',
			'About PIC Draw')
		self.Bind(wx.EVT_MENU, self.on_help_about, help_about)
		self.Append(menu_help, 'Help')

	def on_help_about(self, event):
		msg = """ PIC Draw 0.2
* Draw PIC data using matplotlib and wxPython
* Copyright (C) 2014 Jian-Ming Tang <jmtang@mailaps.org> """
		dlg = wx.MessageDialog(self, msg, 'About', wx.OK)
		dlg.ShowModal()
		dlg.Destroy()


class MainFrame(wx.Frame):
	""" Main Frame (Controller)
		* MenuBar
		* Panel (Background/F2D/D3D)
		* StatusBar
	"""
	dirname = ''
	filename = ''

	def __init__(self, *args, **kwargs):
		""" Create the Main Frame with MainMenuBar/Panel/StatusBar
		"""
		wx.Frame.__init__(self, *args, **kwargs)

	# Add the Main Menu Bar
	#
		self.menu = MainMenuBar()
		self.SetMenuBar(self.menu)

	# Add a backgroud image
	#
		self.panel = PanelBackground(self)

	# Add the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.panel, 100, wx.EXPAND)
		self.SetSizerAndFit(sizer)

	# Bind to menu events
	#
		self.Bind(wx.EVT_MENU, self.on_file_new, self.menu.file_new)
		self.Bind(wx.EVT_MENU, self.on_file_open, self.menu.file_open)
		self.Bind(wx.EVT_MENU, self.on_file_save, self.menu.file_save)
		self.Bind(wx.EVT_MENU, self.on_file_exit, self.menu.file_exit)
		self.Bind(wx.EVT_MENU, self.on_frame_F2D, self.menu.frame_F2D)
		self.Bind(wx.EVT_MENU, self.on_frame_F1D, self.menu.frame_F1D)
		self.Bind(wx.EVT_MENU, self.on_frame_D3D, self.menu.frame_D3D)
		self.Bind(wx.EVT_MENU, self.on_frame_D2D, self.menu.frame_D2D)

	def status_message(self, msg):
		""" Display a message in the Status Bar
		"""
		self.status_bar.SetStatusText(msg)
 
	def renew_panel(self, panel):
		""" replace the background image with dist/ctrl panels
		"""
		self.panel.Destroy()
		self.panel = panel
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.panel, 100, wx.EXPAND)
		self.SetSizerAndFit(sizer)

	def on_file_new(self, event):
		""" Open a new root Frame
		"""
		frame = MainFrame(None, title='PIC Draw')
		frame.Show()

	def on_file_open(self, event):
		""" Choose a PIC data file
		"""
		dlg = wx.FileDialog(self, defaultDir = os.getcwd(),
				style = wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.dirname = dlg.GetDirectory()
			self.filename = dlg.GetFilename()
			f = os.path.join(self.dirname, self.filename)
			if os.path.isfile(f):
				pub.sendMessage('File Open')
			else:
				self.dirname = ''
				self.filename = ''
				self.status_message('Error: File Not Found!')

	def on_file_save(self, event):
		""" Save the current Figure to a PNG file
		"""
		ffilter = 'Portable Network Graphics (*.png)|*.png'
		fname = self.fkey.title()+'_t'+str(self.time)

		dlg = wx.FileDialog(self, defaultDir = os.getcwd(),
				defaultFile = fname, wildcard = ffilter,
				style = wx.FD_SAVE)

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.disp_panel.canvas.print_figure(path)
			self.status_message("Saved to %s" % path)

	def on_file_exit(self, event):
		""" Close a root Frame
		"""
		self.Destroy()

	def on_frame_F2D(self, event):
		self.renew_panel(PanelF2D(self))
		self.SetTitle(self.menu.labelF2D)
		self.menu.frame_F2D.Enable(False)
		self.menu.frame_F1D.Enable(True)
		self.menu.frame_D3D.Enable(True)
		self.menu.frame_D2D.Enable(False)
		if not (self.dirname or self.filename):
			self.on_file_open(None)

	def on_frame_F1D(self, event):
		frame = GUI.FrameF1D(self.panel, title = self.menu.labelF1D)
		frame.Show()

	def on_frame_D3D(self, event):
		self.renew_panel(PanelD3D(self))
		self.SetTitle(self.menu.labelD3D)
		self.menu.frame_F2D.Enable(True)
		self.menu.frame_F1D.Enable(False)
		self.menu.frame_D3D.Enable(False)
		self.menu.frame_D2D.Enable(True)
		if not (self.dirname or self.filename):
			self.on_file_open(None)

	def on_frame_D2D(self, event):
		frame = GUI.FrameD2D(self.panel, title = self.menu.labelD2D)
		frame.Show()


class myApp(wx.App):
	def OnInit(self):
		frame = MainFrame(None, title='PIC Draw')
#		frame.CenterOnScreen()
#		self.SetTopWindow(frame)
		frame.Show()
		return True


### main program ###
if __name__ == "__main__": 

	app = myApp()
	app.MainLoop()

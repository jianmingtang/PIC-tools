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
import PIC
import GUI


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

	def on_file_exit(self, event):
		""" Close the Main Frame
		"""
#		if self.p.frame_F1D:  self.p.frame_F1D.Destroy()
#		if self.p.frame_D3D:  self.p.frame_D3D.Destroy()
		self.p.Destroy()
       
	def on_help_about(self, event):
		msg = """ PIC Draw 0.2
* Draw PIC data using matplotlib and wxPython
* Copyright (C) 2014 Jian-Ming Tang <jmtang@mailaps.org> """
		dlg = wx.MessageDialog(self, msg, 'About', wx.OK)
		dlg.ShowModal()
		dlg.Destroy()


class MainFrame(wx.Frame):
	""" Main Frame
		* Selections of next-level Frames
	"""
# data variables
#
	field = None
	dist = None

# control variables
#
	dirname = ''
	filename = ''
	time = 0
	fkey = 'Bx'
	fieldlist = ['Bx','By','Bz','Ex','Ey','Ez','vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']
	singlelist = fieldlist[:6]

# GUI variables
#
	frameF2D = None
	frameF1D = None
	frameD3D = None
	frameD2D = None

	labelF2D = 'Field 2D Plot'
	labelF1D = 'Field 1D Plot'
	labelD3D = 'Distribution 3D Plot'
	labelD2D = 'Distribution 2D Plot'

	def __init__(self, *args, **kwargs):
		""" Create the Main Frame with MainMenuBar/Buttons/StatusBar
		"""
		wx.Frame.__init__(self, *args, **kwargs)

	# Add the Main Menu Bar
	#
		MainMenuBar(self)

	# Add Buttons for child Frames
	#
		btn_F2D = wx.Button(self, label = self.labelF2D)
		btn_F2D.Bind(wx.EVT_BUTTON, self.on_btn_F2D)
		btn_F1D = wx.Button(self, label = self.labelF1D)
		btn_F1D.Bind(wx.EVT_BUTTON, self.on_btn_F1D)
		btn_D3D = wx.Button(self, label = self.labelD3D)
		btn_D3D.Bind(wx.EVT_BUTTON, self.on_btn_D3D)
		btn_D2D = wx.Button(self, label = self.labelD2D)
		btn_D2D.Bind(wx.EVT_BUTTON, self.on_btn_D2D)

	# Add the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

	# Sizer and Fit
	#
		pad = 2
		flags = wx.EXPAND | wx.ALL 
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(btn_F2D, 100, flags, pad)
		sizer.Add(btn_F1D, 100, flags, pad)
		sizer.Add(btn_D3D, 100, flags, pad)
		sizer.Add(btn_D2D, 100, flags, pad)
		self.SetSizerAndFit(sizer)

	def status_message(self, msg):
		""" Display a message in the Status Bar
		"""
		self.status_bar.SetStatusText(msg)

	def open_data_file(self):
		""" Choose a PIC data file for plotting
		"""
		dlg = wx.FileDialog(self, defaultDir = os.getcwd(),
				style = wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.dirname = dlg.GetDirectory()
			self.filename = dlg.GetFilename()

	def file_not_found(self):
		""" if file not found
		"""
		dlg = wx.MessageDialog(self, 'File not found!',
				'Error', wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()

	def update_field_data(self):
		if self.dirname and self.filename:
			f = os.path.join(self.dirname, self.filename)
		else:
			f = ''
		if os.path.isfile(f):
			self.field = PIC.FieldNASA(f)
			self.time = self.filename[7:12].lstrip('0')
		else:
#			self.status_message('File not found!')
			self.file_not_found()
			f = ''
		return f

	def on_btn_F2D(self, event):
		""" Open Field 2D Frame
		"""
		self.open_data_file()
		self.update_field_data()
		if self.field and self.frameF2D == None:
			self.frameF2D = GUI.FrameF2D(self,
					title = self.labelF2D)
			self.frameF2D.Show()

	def on_btn_F1D(self, event):
		""" Open Field 1D Frame
		"""
		if self.field and self.frameF1D == None:
			self.frameF1D = GUI.FrameF1D(self,
					title = self.labelF1D)
			self.frameF1D.Show()

	def on_btn_D3D(self, event):
		""" Open Distribution 3D Frame
		"""
		f = self.open_data_file()
		if os.path.isfile(f):
			self.dist = PIC.DistNASA(f)
			if self.frameD3D == None:
				self.frameD3D = GUI.FrameD3D(self,
						title = self.labelD3D)
				self.frameD3D.Show()
		else:
			self.file_not_found()

	def on_btn_D2D(self, event):
		""" Open Distribution 2D Frame
		"""
		if self.dist and self.frameD2D == None:
			self.frameD2D = GUI.FrameD2D(self,
					title = self.labelD2D)
			self.frameD2D.Show()
		

### main program ###
if __name__ == "__main__": 

	app = wx.App()
	frame = MainFrame(None, title='PIC Draw')
	frame.Show()
	app.MainLoop()

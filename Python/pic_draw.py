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
#from wx.lib.pubsub import pub
import GUI


class PanelF2D(wx.Panel):
	""" F2D Panel (Controller)
	"""
	fieldlist = ['Bx','By','Bz','Ex','Ey','Ez','vxs','vys','vzs',
		'pxx','pyy','pzz','pxy','pxz','pyz','dns']

# data
#
	field = None

	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

	# Save a local reference to Main Frame
	#
		self.p = parent

	# Add a control Panel and a display Panel
	#
		self.ctrl = GUI.PanelF2DCtrl(self)
		self.disp = GUI.PanelF2DDisp(self)

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.disp, 1, wx.EXPAND)
		sizer.Add(self.ctrl, 0)
		self.SetSizerAndFit(sizer)

	# Load data from file
	#
		self.load_data()

	# Set fkey and Draw
	#
		self.on_rb_fkey(None)

	# Bind to control Panel events
	#
		self.Bind(wx.EVT_RADIOBOX, self.on_rb_fkey,
				self.ctrl.rb_fkey)
		self.Bind(wx.EVT_TOGGLEBUTTON, self.on_tb_stream,
				self.ctrl.tb_stream)
		self.Bind(wx.EVT_BUTTON, self.on_btn_load,
				self.ctrl.btn_load)
		self.Bind(wx.EVT_BUTTON, self.on_btn_draw,
				self.ctrl.btn_draw)

	def load_data(self):
		""" Update field if the file is valid
		"""
		if not self.p.pathname: return

		f = self.p.pathname
		try:
			self.p.status_message('Loading')
			self.field = PIC.FieldNASA(f)
			self.p.status_message('Done')
		except:
			self.p.status_message('Error: Load Fail!')
			self.field = None
		if self.field:
			self.p.status_message('Loaded ' + f)
			head, tail = os.path.split(f)
			self.time = tail[7:12].lstrip('0')
			self.ctrl.tc_time.SetValue(self.time)
			self.set_range()
			self.ctrl.update_rb_list(self.field.fieldlist)

	def set_range(self):
		""" Reset the grid range
		"""
		nx = self.field.data['nnx']
		nz = self.field.data['nnz']
		self.ctrl.tc_range[0].SetRange(0, nx)
		self.ctrl.tc_range[1].SetRange(0, nx)
		self.ctrl.tc_range[2].SetRange(0, nz)
		self.ctrl.tc_range[3].SetRange(0, nz)
		# Set the upper bound only if it is zero.
		if self.ctrl.tc_range[1].GetValue() == 0:
			self.ctrl.tc_range[1].SetValue(nx)
		if self.ctrl.tc_range[3].GetValue() == 0:
			self.ctrl.tc_range[3].SetValue(nz)

	def on_rb_fkey(self, event):
		""" Change the field key
		"""
		self.fkey = self.ctrl.rb_fkey.GetItemLabel(
				self.ctrl.rb_fkey.GetSelection())
		self.on_btn_draw(event)

	def on_tb_stream(self, event):
		""" Toggle stream lines
		"""
		self.on_btn_draw(event)

	def on_btn_load(self, event):
		""" Load the data
		"""
#		time = self.ctrl.tc_time.GetValue()
#		self.p.filename = 'fields-' + time.zfill(5) + '.dat'
		self.p.get_path_from_dirctrl(None)
		self.load_data()

	def on_btn_draw(self, event):
		""" Draw the figure
		"""
		if not self.field:
			dlg = wx.MessageDialog(self, 'Load Data First!',
					'Error', wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		title = self.fkey.title() + ', t=' + str(self.time)
		r = [self.ctrl.tc_range[i].GetValue() for i in range(4)]
		if r[0] >= r[1] or r[2] >= r[3] or min(r) < 0:
			r = None
		else:
			self.field.truncate(r)
		Lx = 'X (de)'
		Ly = 'Z (de)'
		X = self.field['xe']
		Y = self.field['ze']
		Z = self.field[self.fkey]
		if self.ctrl.tb_stream.GetValue():
			U = self.field['Bx']
			V = self.field['Bz']
		else:
			U = V = None
		if self.fkey in self.field.singlelist:
			N = 1
		else:
			N = 4
		self.p.status_message('Drawing')
		self.disp.draw(N, title, Lx, Ly, X, Y, Z, U, V)
		self.p.status_message('Done')


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
		self.ctrl = GUI.PanelD3DCtrl(self)
		self.disp = GUI.PanelD3DDisp(self)

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
		title = 'f(v)'
		Lx = 'Vx'
		Ly = 'Vy'
		Lz = 'vz'
		X = Y = Z = self.pdist['axes'][0]
		f = self.pdist['fxyz'][1].transpose()
		iso = max(f.ravel()) * self.iso
		self.p.status_message('Drawing')
		self.disp.draw(title, Lx, Ly, Lz, X, Y, Z, f, iso)
		self.p.status_message('Done')


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

	def load_data(self):
		""" Do nothing if on_file_open() is called.
		"""
		pass

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
	pathname = ''

	def __init__(self, *args, **kwargs):
		""" Create the Main Frame with MainMenuBar/Panel/StatusBar
		"""
		wx.Frame.__init__(self, *args, **kwargs)

	# Add the Main Menu Bar
	#
		self.menu = MainMenuBar()
		self.SetMenuBar(self.menu)

	# Add a directory control tree
	#
		self.tree = wx.GenericDirCtrl(self, size=(200,-1),
				dir = os.getcwd())

	# Add a backgroud image
	#
		self.panel = PanelBackground(self)

	# Add the Status Bar
	#
		self.status_bar = self.CreateStatusBar()

	# Sizer and Fit
	#
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.tree, 0, wx.EXPAND)
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

#		self.Bind(wx.EVT_DIRCTRL_FILEACTIVATED, self.on_tree,
#				self.tree)

	def status_message(self, msg):
		""" Display a message in the Status Bar
		"""
		self.status_bar.SetStatusText(msg)
 
	def replace_panel(self, panel):
		""" replace the background image with dist/ctrl panels
		"""
		self.panel.Destroy()
		self.panel = panel
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.tree, 0, wx.EXPAND)
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
			f = dlg.GetPath()
			if os.path.isfile(f):
				self.pathname = f
				self.tree.SetPath(f)
				self.panel.load_data()
			else:
				self.pathname = ''
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
			self.panel.disp.canvas.print_figure(path)
			self.status_message("Saved to %s" % path)

	def on_file_exit(self, event):
		""" Close a root Frame
		"""
		self.Destroy()

	def on_frame_F2D(self, event):
		""" Replace panel for Field 2D plot
		"""
		self.on_file_open(None)
		self.replace_panel(GUI.PanelF2D(self))
		self.SetTitle(self.menu.labelF2D)
		self.menu.frame_F2D.Enable(False)
		self.menu.frame_F1D.Enable(True)
		self.menu.frame_D3D.Enable(True)
		self.menu.frame_D2D.Enable(False)

	def on_frame_F1D(self, event):
		""" Open a new sub frame for Field 1D plot
		"""
		frame = GUI.FrameF1D(self.panel, title = self.menu.labelF1D)
		frame.Show()

	def on_frame_D3D(self, event):
		""" Replace panel for Distribution 3D plot
		"""
		self.on_file_open(None)
		self.replace_panel(GUI.PanelD3D(self))
		self.SetTitle(self.menu.labelD3D)
		self.menu.frame_F2D.Enable(True)
		self.menu.frame_F1D.Enable(False)
		self.menu.frame_D3D.Enable(False)
		self.menu.frame_D2D.Enable(True)

	def on_frame_D2D(self, event):
		""" Open a new sub frame for Distribution 2D plot
		"""
		frame = GUI.FrameD2D(self.panel, title = self.menu.labelD2D)
		frame.Show()

	def get_path_from_dirctrl(self, event):
		f = self.tree.GetPath()
		if os.path.isfile(f):
			self.pathname = f
		

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

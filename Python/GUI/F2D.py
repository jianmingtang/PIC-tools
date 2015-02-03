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


#
# TODO: check scaling factors for V, T, n, ...
#

import os
import wx
import numpy
from math import sqrt
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from mplFig import Figure2D
import PIC


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
            self.fig.draw_quad(title, Lx, Ly, [X] * 4, [Y] * 4, Z, U, V)


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
        self.jlist = ['jx', 'jy', 'jz']
        self.jilist = [s + '_i' for s in self.jlist]
        self.jelist = [s + '_e' for s in self.jlist]
        self.plist = ['pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz']
        self.pilist = [s + '_i' for s in self.plist]
        self.pelist = [s + '_e' for s in self.plist]
        self.vlist = ['Vx', 'Vy', 'Vz']
        self.vilist = [s + '_i' for s in self.vlist]
        self.velist = [s + '_e' for s in self.vlist]
        self.olist = ['T_i', 'T_e']
        fkeylist = ['Bx', 'By', 'Bz', 'Ex', 'Ey', 'Ez',
                    'dns', 'n_i', 'n_e', 'vxs', 'vys', 'vzs'] \
            + self.jilist + self.jelist + self.vilist + self.velist \
            + self.plist + self.pilist + self.pelist + self.olist

        self.rb_fkey = wx.RadioBox(self, label='Select a field',
                                   choices=fkeylist, majorDimension=3,
                                   style=wx.RA_SPECIFY_COLS)

    # flags for Text Control
    #
        flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL

    # Create a Text Control to modify time
    #
        st_time = wx.StaticText(self, label='Time:')
        self.tc_time = wx.TextCtrl(self)
        sizer_time = wx.BoxSizer(wx.HORIZONTAL)
        sizer_time.Add(st_time, 0, flags)
        sizer_time.Add(self.tc_time, 0, flags)

    # Create a Toggle Button to add magnetic field lines
    #
        self.tb_stream = wx.ToggleButton(self, label='Magnetic Field Line')

    # Create a Toggle Button to use MHD units
    #
        self.tb_scale = wx.ToggleButton(self, label='MHD units')

    # Create a Text Control to modify range
    #
        st_range_label = wx.StaticText(self, label='Drawing Range:')
        st_range = [wx.StaticText(self, label=i + j)
                    for i in ['x', 'z'] for j in ['min:', 'max:']]
        self.tc_range = [wx.SpinCtrl(self, size=(80, -1))
                         for i in range(4)]
        sizer_range = wx.GridSizer(rows=4, cols=2)
        for i in range(4):
            sizer_range.Add(st_range[i], 0, flags)
            sizer_range.Add(self.tc_range[i], 0, flags)

    # Create Buttons for reloading data and redraw
    #
        self.btn_load = wx.Button(self, label='Load')
        self.btn_draw = wx.Button(self, label='Draw')
        sizer_refresh = wx.BoxSizer(wx.HORIZONTAL)
        sizer_refresh.Add(self.btn_load, 0, flags)
        sizer_refresh.Add(self.btn_draw, 0, flags)

    # Sizer and Fit
    #
        pad = 3
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_fkey, 0, flags, pad)
        sizer.Add(sizer_time, 0, flags, pad)
        sizer.Add(wx.StaticLine(self), 0, flags | wx.EXPAND, pad)
        sizer.Add(st_range_label, 0, flags)
        sizer.Add(sizer_range, 0, flags, pad)
        sizer.Add(wx.StaticLine(self), 0, flags | wx.EXPAND, pad)
        sizer.Add(self.tb_stream, 0, flags, pad)
        sizer.Add(self.tb_scale, 0, flags, pad)
        sizer.Add(sizer_refresh, 0, flags, pad)
        self.SetSizerAndFit(sizer)

#    def update_rb_list(self, s):
#        """ Reset the rb list according to the info in data file
#        """
#        for i, j in enumerate(self.fkeylist):
#            if j not in s:
#                self.rb_fkey.EnableItem(i, False)


class PanelF2D(wx.Panel):

    """ F2D Panel (Controller)
    """

# data
#
    smi = 1
    field = None

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

    # Save a local reference to Main Frame
    #
        self.p = parent

    # Add a control Panel and a display Panel
    #
        self.ctrl = PanelF2DCtrl(self)
        self.disp = PanelF2DDisp(self)

    # Sizer and Fit
    #
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.disp, 1, wx.EXPAND)
        sizer.Add(self.ctrl, 0)
        self.SetSizerAndFit(sizer)

    # Load data from file
    #
        self.load_data()

    # Initialize fkey and Draw
    #
        self.on_rb_fkey(None)

    # Bind to control Panel events
    #
        self.Bind(wx.EVT_RADIOBOX, self.on_rb_fkey, self.ctrl.rb_fkey)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_tb_stream, self.ctrl.tb_stream)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_tb_scale, self.ctrl.tb_scale)
        self.Bind(wx.EVT_BUTTON, self.on_btn_load, self.ctrl.btn_load)
        self.Bind(wx.EVT_BUTTON, self.on_btn_draw, self.ctrl.btn_draw)

    def load_data(self):
        """ Update field if the file is valid
        """
        if not self.p.pathname:
            return

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
            self.smi = sqrt(self.field.data['mass'][0])

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

    def on_tb_scale(self, event):
        """ Toggle MHD units
        """
        self.on_btn_draw(event)

    def on_btn_load(self, event):
        """ Load the data
        """
#       time = self.ctrl.tc_time.GetValue()
#       self.p.filename = 'fields-' + time.zfill(5) + '.dat'
        self.p.get_path_from_dirctrl(None)
        self.load_data()

    def dni(self):
        return self.field['dns'][0] + self.field['dns'][2]

    def dne(self):
        return self.field['dns'][1] + self.field['dns'][3]

    def scaling(self):
        """ scale from electron units to ion units
        """
        wpewce = self.field.data['wpewce']
        if self.fkey[0] == 'B':
            return wpewce
        if self.fkey[0] == 'E':
            return wpewce**2 * self.smi
        elif self.fkey[0] == 'j':
            return wpewce * self.smi
        elif self.fkey[0] == 'n':
            return self.smi**2 
        elif self.fkey[0] == 'p':
            return wpewce**2
        elif self.fkey[0] == 'T':
            return (wpewce/self.smi)**2
        elif self.fkey[0] == 'V':
            return wpewce/self.smi
        else:
            return 1

    def on_btn_draw(self, event):
        """ Draw the figure
        """
        if not self.field:
            dlg = wx.MessageDialog(self, 'Load Data First!',
                                   'Error', wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        title = self.fkey + '  t=' + str(self.time)
        title = title.replace('_', ',')
        if title[0] != 'n':
            title = title[0].upper() + title[1:]
        r = [self.ctrl.tc_range[i].GetValue() for i in range(4)]
        # temp fix of unphysical pressure/density near the boundaries
        if self.fkey[0] in ['n','p','T','V']:
            if r[0] < 1:
                r[0] = 1
                self.ctrl.tc_range[0].SetValue(1)
            if r[2] < 1:
                r[2] = 1
                self.ctrl.tc_range[2].SetValue(1)
        # check range (no check for maximum)
        if r[0] < r[1] and r[2] < r[3] and min(r) >= 0:
            self.field.truncate(r)
        Lx = 'X'
        Ly = 'Z'
        X = self.field['xe']
        Y = self.field['ze']
        if self.fkey == 'n_i':
            self.Z = self.dni()
        elif self.fkey == 'n_e':
            self.Z = self.dne()
        elif self.fkey in self.ctrl.jilist:
            key = 'v' + self.fkey[1] + 's'
            self.Z = self.field[key][0] + self.field[key][2]
        elif self.fkey in self.ctrl.jelist:
            key = 'v' + self.fkey[1] + 's'
            self.Z = self.field[key][1] + self.field[key][3]
        elif self.fkey in self.ctrl.pilist:
            key = self.fkey[:-2]
            key1 = 'v' + self.fkey[1] + 's'
            key2 = 'v' + self.fkey[2] + 's'
            j1 = self.field[key1][0] + self.field[key1][2]
            j2 = self.field[key2][0] + self.field[key2][2]
            dn = self.dni()
            self.Z = (self.field[key][0] + self.field[key][2] - j1 * j2 / dn) \
                * self.field.data['mass'][0]
        elif self.fkey in self.ctrl.pelist:
            key = self.fkey[:-2]
            key1 = 'v' + self.fkey[1] + 's'
            key2 = 'v' + self.fkey[2] + 's'
            j1 = self.field[key1][1] + self.field[key1][3]
            j2 = self.field[key2][1] + self.field[key2][3]
            dn = self.dne()
            self.Z = (self.field[key][1] + self.field[key][3] - j1 * j2 / dn) \
                * self.field.data['mass'][1]
        elif self.fkey == 'T_i':
            keyplist = ['pxx','pyy','pzz']
            keyjlist = ['vxs','vys','vzs']
            dn = self.dni()
            tmp = numpy.zeros(numpy.shape(self.field['pxx'][0]))
            for i in range(3):
                keyp = keyplist[i]
                keyj = keyjlist[i]
                jc = self.field[keyj][0] + self.field[keyj][2]
                tmp += (self.field[keyp][0] + self.field[keyp][2] - jc*jc/dn) \
                        * self.field.data['mass'][0]
            self.Z = tmp / dn / 3.
        elif self.fkey == 'T_e':
            keyplist = ['pxx','pyy','pzz']
            keyjlist = ['vxs','vys','vzs']
            dn = self.dne()
            tmp = numpy.zeros(numpy.shape(self.field['pxx'][1]))
            for i in range(3):
                keyp = keyplist[i]
                keyj = keyjlist[i]
                jc = self.field[keyj][1] + self.field[keyj][3]
                tmp += (self.field[keyp][1] + self.field[keyp][3] - jc*jc/dn) \
                        * self.field.data['mass'][1]
            self.Z = tmp / dn / 3.
        elif self.fkey in self.ctrl.vilist:
            dn = self.dni()
            key = 'v' + self.fkey[1] + 's'
            self.Z = (self.field[key][0] + self.field[key][2]) / dn
        elif self.fkey in self.ctrl.velist:
            dn = self.dne()
            key = 'v' + self.fkey[1] + 's'
            self.Z = (self.field[key][1] + self.field[key][3]) / dn
        else:
            self.Z = self.field[self.fkey]
        if self.ctrl.tb_stream.GetValue():
            U = self.field['Bx']
            V = self.field['Bz']
        else:
            U = V = None
        if self.ctrl.tb_scale.GetValue():
            self.Z = self.Z.copy() * self.scaling()
            X = X.copy() / self.smi
            Y = Y.copy() / self.smi
            title += '  (MHD)'
            Lx += ' (di)'
            Ly += ' (di)'
        else:
            Lx += ' (de)'
            Ly += ' (de)'
        if self.fkey in self.field.quadlist:
            N = 4
        else:
            # assuming all processed data only needs a single panel
            N = 1
        self.p.status_message('Drawing')
        self.disp.draw(N, title, Lx, Ly, X, Y, self.Z, U, V)
        self.p.status_message('Done')

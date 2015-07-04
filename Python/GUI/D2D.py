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
"""
D2D
---
"""


import wx
import numpy
import matplotlib
matplotlib.use('wxAgg')
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
        NavigationToolbar2WxAgg as NavigationToolbar
from mplFig import Figure2D


class PanelD2DDisp(wx.Panel):

    """ Display Panel for D2D
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

    def draw(self, N, title, Lx, Ly, X, Y, Z):
        if N == 1:
            self.fig.draw_one(title, Lx, Ly, X, Y, Z)
        else:
            self.fig.draw_quad(title, Lx, Ly, X, Y, Z)


class PanelD2DCtrl(wx.Panel):

    """ Control Panel
            * Radio Box: select a cut direction
    """

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

    # Save a local reference to the F2D Panel
    #
        self.p = parent

    # Create a Radio Box for 2D plot selections
    #
        plist = ['fxy', 'fxz', 'fyz', 'xcut', 'ycut', 'zcut']
        self.rb_key = wx.RadioBox(self, label='Select a plot',
                                  choices=plist,
                                  majorDimension=3, style=wx.RA_SPECIFY_COLS)

        flags = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL

    # Create a Slider for the cut (fixed) value
    #
        self.slr_cut = wx.Slider(self, value=self.p.cut,
                                 size=(150, -1), minValue = 0,
                                 style = wx.SL_HORIZONTAL | wx.SL_LABELS)

    # Create Buttons for reloading data and redraw
    #
        self.btn_apply = wx.Button(self, label='Apply')
        self.btn_draw = wx.Button(self, label='Draw')
        sizer_refresh = wx.BoxSizer(wx.HORIZONTAL)
        sizer_refresh.Add(self.btn_apply, 0, flags)
        sizer_refresh.Add(self.btn_draw, 0, flags)

    # Sizer and Fit
    #
        pad = 3
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_key, 0, flags, pad)
        sizer.Add(self.slr_cut, 100, flags, pad)
        sizer.Add(sizer_refresh, 0, flags, pad)
        self.SetSizerAndFit(sizer)


class FrameD2D(wx.Frame):

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
        self.disp = PanelD2DDisp(self)

    # Create a Control Panel
    #
        self.ctrl = PanelD2DCtrl(self)

    # Create the Status Bar
    #
        self.status_bar = self.CreateStatusBar()

    # Sizer and Fit
    #
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.disp, 1, wx.EXPAND)
        sizer.Add(self.ctrl, 0)
        self.SetSizerAndFit(sizer)

    # Initialize key and Draw
    #
        self.on_rb_key(None)

    # Bind to control Panel events
    #
        self.Bind(wx.EVT_RADIOBOX, self.on_rb_key, self.ctrl.rb_key)
        self.Bind(wx.EVT_SCROLL, self.on_slr_cut, self.ctrl.slr_cut)
        self.Bind(wx.EVT_BUTTON, self.on_btn_apply,
                  self.ctrl.btn_apply)
        self.Bind(wx.EVT_BUTTON, self.on_btn_draw,
                  self.ctrl.btn_draw)

    def status_message(self, msg):
        """ Display a message in the Status Bar
        """
        self.status_bar.SetStatusText(msg)

    def on_rb_key(self, event):
        """ Change the field key
        """
        self.key = self.ctrl.rb_key.GetItemLabel(
            self.ctrl.rb_key.GetSelection())
        if self.key in ['xcut', 'ycut', 'zcut']:
            cut_range = [self.key[0], 40, 60]
            self.p.pdist.cut(cut_range)
        self.on_btn_apply(event)
        self.on_btn_draw(event)

    def on_slr_cut(self, event):
        """ Change the cut value
        """
        self.cut = self.ctrl.slr_cut.GetValue()
        self.on_btn_apply(event)
        self.on_btn_draw(event)

    def on_btn_apply(self, event):
        """ Apply settings
        """
        self.X = self.Y = self.p.pdist['axes']

    def on_btn_draw(self, event):
        """ Draw the figure
        """
        title = self.key
        if self.key in ['fxy', 'zcut']:
            Lx = 'Vx'
            Ly = 'Vy'
        elif self.key in ['fxz', 'ycut']:
            Lx = 'Vx'
            Ly = 'Vz'
        elif self.key in ['fyz', 'xcut']:
            Lx = 'Vy'
            Ly = 'Vz'
        else:
            Lx = ''
            Ly = ''
        if self.p.plot < 4:
            N = 4
            if self.key in ['fxy', 'fxz', 'fyz']:
                self.Z = self.p.pdist[self.key]
            else:
                self.Z = self.p.pdist[self.key.lstrip('xyz')]
        else:
            N = 1
        self.status_message('Drawing')
        self.disp.draw(N, title, Lx, Ly, self.X, self.Y, self.Z)
        self.status_message('Done')

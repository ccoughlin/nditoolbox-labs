""" plotwindow.py - wxPython control for displaying matplotlib plots

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import ui_defaults
from controllers.plotwindow_ctrl import PlotWindowController, ImgPlotWindowController
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
import os.path

class PlotWindow(wx.Frame):
    """Basic wxPython UI element for displaying matplotlib plots"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = PlotWindowController(self)
        self.has_data = self.controller.load_data(self.data_file)
        if self.has_data:
            self.title = 'Plot - {0}'.format(os.path.basename(self.data_file))
            wx.Frame.__init__(self, id=wx.ID_ANY, parent=self.parent, title=self.title)
            self.init_menu()
            self.init_ui()
            self.controller.plot(self.controller.data)

    def init_ui(self):
        """Creates the PlotWindow UI"""
        parent_x, parent_y = self.parent.GetPositionTuple()
        parent_w, parent_h = self.parent.GetSize()
        self.SetPosition((parent_x + parent_w + ui_defaults.widget_margin,
                          ui_defaults.widget_margin))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.figure)
        self.axes = self.figure.add_subplot(111, picker=True)
        self.axes.grid(True)
        #self.cursor = Cursor(self.axes, useblit=True, color='green', alpha=0.5, linestyle='--', linewidth=2)
        self.sizer.Add(self.canvas, 1, ui_defaults.sizer_flags, 0)
        self.add_toolbar()
        self.SetIcon(self.parent.GetIcon())
        self.SetSizerAndFit(self.sizer)

    def add_toolbar(self):
        """Creates the matplotlib toolbar (zoom, pan/scroll, etc.)
        for the plot"""
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            self.SetToolBar(self.toolbar)
        else:
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND, 0)
        self.toolbar.update()

    def init_menu(self):
        """Creates the main menu"""
        self.menubar = wx.MenuBar()
        self.init_file_menu()
        self.init_plot_menu()
        self.init_ops_menu()
        self.init_tools_menu()
        self.init_help_menu()
        self.SetMenuBar(self.menubar)

    def init_file_menu(self):
        """Creates the File menu"""
        self.file_mnu = wx.Menu()
        savedata_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Save Current Data",
                                    help="Save current data to disk")
        self.Bind(wx.EVT_MENU, self.controller.on_save_data, id=savedata_mnui.GetId())
        self.file_mnu.AppendItem(savedata_mnui)
        close_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Close Window", help="Close the plot window")
        self.Bind(wx.EVT_MENU, self.controller.on_close, id=close_mnui.GetId())
        self.file_mnu.AppendItem(close_mnui)
        self.menubar.Append(self.file_mnu, "&File")

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()
        plottitle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.controller.on_set_plottitle, id=plottitle_mnui.GetId())
        self.plot_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_xlabel, id=xlbl_mnui.GetId())
        self.plot_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_ylabel, id=ylbl_mnui.GetId())
        self.plot_mnu.AppendItem(ylbl_mnui)
        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_ops_menu(self):
        """Creates the Operations menu"""
        self.ops_mnu = wx.Menu()
        self.revert_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text='Revert To Original',
                                       help='Revert to original data set')
        self.Bind(wx.EVT_MENU, self.controller.on_revert, id=self.revert_mnui.GetId())
        self.ops_mnu.AppendItem(self.revert_mnui)
        self.init_specific_ops_menu()
        self.menubar.Append(self.ops_mnu, '&Operations')

    def init_specific_ops_menu(self):
        """Creates any plot-specific Operations menu items"""
        self.rect_mnu = wx.Menu() # Rectification operations
        self.fullrect_mnui = wx.MenuItem(self.rect_mnu, wx.ID_ANY, text="Full",
                                         help="Full Rectification")
        self.Bind(wx.EVT_MENU, self.controller.on_rectify, id=self.fullrect_mnui.GetId())
        self.rect_mnu.AppendItem(self.fullrect_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Rectify', self.rect_mnu)

        self.gate_mnu = wx.Menu() # Gates operations
        for gate_idx, params in self.controller.get_gates().items():
            gate_lbl = params[0]
            gate_id = params[1]
            gate_desc = "Applies a {0} gate function to the data".format(gate_lbl)
            gate_mnui = wx.MenuItem(self.gate_mnu, id=gate_id, text=gate_lbl, help=gate_desc)
            self.gate_mnu.AppendItem(gate_mnui)
            self.Bind(wx.EVT_MENU, self.controller.on_apply_gate, id=gate_mnui.GetId())
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Gates', self.gate_mnu)

    def init_tools_menu(self):
        """Initializes the Tools Menu (Plugins and external scripts)"""
        self.tools_mnu = wx.Menu()
        self.plugins_mnu = wx.Menu()
        plugins = self.controller.available_plugins
        for plugin_id, plugin in plugins.items():
            plugin_name = plugin[1].name
            plugin_description = plugin[1].description
            script_mnui = wx.MenuItem(self.tools_mnu, id=plugin_id, text=plugin_name,
                                      help=plugin_description)
            self.Bind(wx.EVT_MENU, self.controller.on_run_plugin, id=script_mnui.GetId())
            self.plugins_mnu.AppendItem(script_mnui)
        self.tools_mnu.AppendMenu(wx.ID_ANY, "Plugins", self.plugins_mnu)
        self.menubar.Append(self.tools_mnu, '&Tools')

    def init_help_menu(self):
        pass

class ImgPlotWindow(PlotWindow):
    """Specialized PlotWindow for handling imgplots"""

    def __init__(self, parent, data_file):
        self.parent = parent
        self.data_file = data_file
        self.controller = ImgPlotWindowController(self)
        self.has_data = self.controller.load_data(self.data_file)
        if self.has_data:
            self.title = 'Plot - {0}'.format(os.path.basename(self.data_file))
            wx.Frame.__init__(self, id=wx.ID_ANY, parent=self.parent, title=self.title)
            self.init_menu()
            self.init_ui()
            self.controller.plot(self.controller.data)

    def init_plot_menu(self):
        """Creates the Plot menu"""
        self.plot_mnu = wx.Menu()
        plottitle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Plot Title",
                                     help="Set Plot Title")
        self.Bind(wx.EVT_MENU, self.controller.on_set_plottitle, id=plottitle_mnui.GetId())
        self.plot_mnu.AppendItem(plottitle_mnui)
        xlbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set X Axis Label",
                                help="Set X Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_xlabel, id=xlbl_mnui.GetId())
        self.plot_mnu.AppendItem(xlbl_mnui)
        ylbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Set Y Axis Label",
                                help="Set Y Axis Label")
        self.Bind(wx.EVT_MENU, self.controller.on_set_ylabel, id=ylbl_mnui.GetId())
        self.plot_mnu.AppendItem(ylbl_mnui)
        cbarlbl_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text='Set Colorbar Label',
                                   help='Set Colorbar Label')
        self.Bind(wx.EVT_MENU, self.controller.on_set_cbarlbl, id=cbarlbl_mnui.GetId())
        self.plot_mnu.AppendItem(cbarlbl_mnui)
        gridtoggle_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text="Toggle Grid",
                                      help="Turns grid on or off")
        self.plot_mnu.AppendItem(gridtoggle_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_toggle_grid, id=gridtoggle_mnui.GetId())
        self.preview_cmaps_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text='Preview Colormaps',
                                              help='Preview available colormaps')
        self.Bind(wx.EVT_MENU, self.controller.on_preview_cmaps, id=self.preview_cmaps_mnui.GetId())
        self.plot_mnu.AppendItem(self.preview_cmaps_mnui)
        self.select_cmap_mnui = wx.MenuItem(self.plot_mnu, wx.ID_ANY, text='Select Colormap...',
                                            help='Selects colormap')
        self.Bind(wx.EVT_MENU, self.controller.on_select_cmap, id=self.select_cmap_mnui.GetId())
        self.plot_mnu.AppendItem(self.select_cmap_mnui)
        self.menubar.Append(self.plot_mnu, "&Plot")

    def init_specific_ops_menu(self):
        """Implements imgplot-specific operations for the Operations menu"""
        self.detrend_mnu = wx.Menu() # Detrending menu
        self.detrend_constantx_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY, text="Constant Horizontal")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_meanx, id=self.detrend_constantx_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_constantx_mnui)
        self.detrend_constanty_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY, text="Constant Vertical")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_meany, id=self.detrend_constanty_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_constanty_mnui)
        self.detrend_linearx_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY, text="Linear Horizontal")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_linearx, id=self.detrend_linearx_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_linearx_mnui)
        self.detrend_lineary_mnui = wx.MenuItem(self.detrend_mnu, wx.ID_ANY, text="Linear Vertical")
        self.Bind(wx.EVT_MENU, self.controller.on_detrend_lineary, id=self.detrend_lineary_mnui.GetId())
        self.detrend_mnu.AppendItem(self.detrend_lineary_mnui)
        self.ops_mnu.AppendMenu(wx.ID_ANY, 'Detrend Data', self.detrend_mnu)

    
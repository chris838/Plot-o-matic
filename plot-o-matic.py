import plugins.io_drivers.test as td
import plugins.io_drivers.simple_file as sf
import plugins.decoders.csv_decoder as csvd
import plugins.decoders.regex_decoder as rxd
import plugins.decoders.null_decoder as nulld
import inspect as ins
from io_driver import IODriver
from data_decoder import DataDecoder
from variables import Variables
from plots import Plots, Plot, figure_view

from enthought.traits.api \
    import HasTraits, Str, Regex, List, Instance, DelegatesTo
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, View, Item, VSplit, \
           HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor
from enthought.traits.ui.menu \
    import Menu, Action, Separator
from enthought.traits.ui.wx.tree_editor \
    import NewAction, CopyAction, CutAction, \
           PasteAction, DeleteAction, RenameAction

class IODriverList(HasTraits):
  """
      Maintains the list of input drivers currently in use and provides
      facilities to add and remove drivers (also used as a handler for
      menu operations).
  """
  io_drivers = List(IODriver)
  plots = DelegatesTo('plots_instance')
  plots_instance = Instance(Plots)
  
class TreeHandler(Handler):
  remove_action = Action(name='Remove', action='handler.remove(editor,object)')
  new_io_driver_action = Action(name='Add Input Driver', action='handler.new_io_driver(editor,object)')
  
  def remove(self, editor, object):
    io_driver_object.stop()
    io_drivers.remove(io_driver_object)
    
  def new_io_driver(self, editor, object):
    try:
      print "Adding IO driver"
      #object.io_drivers += [td.TestDriver()]
      print editor.__dict__
      editor.insert_child(0, td.TestDriver())
      print editor.nodes[0].get_children()
      print object.io_drivers
    except Exception as e:
      print e

class Project(HasTraits):
  io_driver_list = Instance(IODriverList)
  variables = Instance(Variables)
  plots = Instance(Plots)
  visible_plots = List(Plot)
  selected_plot = Instance(Plot)
  
  plot_node = TreeNode( 
    node_for  = [Plot],
    auto_open = True,
    label     = 'name',
    icon_path = 'icons/',
    icon_item = 'plot.png'
  )
  
  tree_editor = TreeEditor(
    nodes = [
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'io_drivers',
        label     = '=Input Drivers',
        view      = View(),
        menu      = Menu(TreeHandler.new_io_driver_action)
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        menu      = Menu( 
          NewAction,
          Separator(),
          TreeHandler.remove_action,
          Separator(),
          RenameAction
        ),
        add       = [DataDecoder],
        icon_path = 'icons/',
        icon_open = 'input.png',
        icon_group = 'input.png'
      ),
      TreeNode( 
        node_for  = [DataDecoder],
        auto_open = True,
        children  = '',
        label     = 'name',
        menu      = Menu(
          DeleteAction,
          Separator(),
          RenameAction
        ),
        icon_path = 'icons/',
        icon_item = 'decoder.png'
      ),
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'plots',
        label     = '=Plots',
        view      = View()
      ),
      plot_node
    ],
    hide_root = True,
    orientation = 'vertical'
  )

  view = View(
    HSplit(
      Item(
        name = 'io_driver_list',
        editor = tree_editor,
        resizable = True,
        show_label = False,
        width = .32
      ),
      VSplit(
        #Item(
        #  name = 'visible_plots',
        #  style= 'custom',
        #  show_label = False,
        #  editor = ListEditor(
        #    use_notebook = True,
        #    deletable = True,
        #    export = 'DockShellWindow',
        #    page_name = '.name',
        #    view = 'figure_view',
        #    selected = 'selected_plot'
        #  )
        #),
        Item(
          name = 'selected_plot',
          style = 'custom',
          resizable = True,
          show_label = False,
          editor = InstanceEditor(
            view = 'figure_view'
          )
        ),
        Item(
          name = 'variables', 
          show_label = False,
          style = 'custom',
          height = .3
        )
      )
    ),
    title = 'Plot-o-matic',
    resizable = True,
    width = 1000,
    height = 600,
    handler = TreeHandler()
  )
  
  def __init__(self, **kwargs):
    HasTraits.__init__(self, **kwargs)
    self.plot_node.on_select = self.click_plot
    
  def click_plot(self, plot):
    if plot not in self.visible_plots:
      self.visible_plots = [plot] + self.visible_plots
    self.selected_plot = plot
      

a = td.TestDriver()
f = sf.SimpleFileDriver()

vs = Variables()
pls = Plots(variables = vs)
pls.add_plot('a+b')
pls.add_plot('c+d')

iodl = IODriverList(io_drivers = [a, f], plots_instance = pls)
proj = Project(io_driver_list = iodl, variables = vs, plots = pls)
  
c = csvd.CSVDecoder(variables = vs)
r = rxd.RegexDecoder(variables = vs)

f._register_decoder(c)
f._register_decoder(r)

a.start()
f.start()

proj.configure_traits()

a.stop()
f.stop()
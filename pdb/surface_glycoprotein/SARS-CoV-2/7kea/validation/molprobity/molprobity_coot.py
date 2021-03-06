# script auto-generated by phenix.molprobity


from __future__ import absolute_import, division, print_function
from six.moves import cPickle as pickle
from six.moves import range
try :
  import gobject
except ImportError :
  gobject = None
import sys

class coot_extension_gui(object):
  def __init__(self, title):
    import gtk
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    scrolled_win = gtk.ScrolledWindow()
    self.outside_vbox = gtk.VBox(False, 2)
    self.inside_vbox = gtk.VBox(False, 0)
    self.window.set_title(title)
    self.inside_vbox.set_border_width(0)
    self.window.add(self.outside_vbox)
    self.outside_vbox.pack_start(scrolled_win, True, True, 0)
    scrolled_win.add_with_viewport(self.inside_vbox)
    scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

  def finish_window(self):
    import gtk
    self.outside_vbox.set_border_width(2)
    ok_button = gtk.Button("  Close  ")
    self.outside_vbox.pack_end(ok_button, False, False, 0)
    ok_button.connect("clicked", lambda b: self.destroy_window())
    self.window.connect("delete_event", lambda a, b: self.destroy_window())
    self.window.show_all()

  def destroy_window(self, *args):
    self.window.destroy()
    self.window = None

  def confirm_data(self, data):
    for data_key in self.data_keys :
      outlier_list = data.get(data_key)
      if outlier_list is not None and len(outlier_list) > 0 :
        return True
    return False

  def create_property_lists(self, data):
    import gtk
    for data_key in self.data_keys :
      outlier_list = data[data_key]
      if outlier_list is None or len(outlier_list) == 0 :
        continue
      else :
        frame = gtk.Frame(self.data_titles[data_key])
        vbox = gtk.VBox(False, 2)
        frame.set_border_width(6)
        frame.add(vbox)
        self.add_top_widgets(data_key, vbox)
        self.inside_vbox.pack_start(frame, False, False, 5)
        list_obj = residue_properties_list(
          columns=self.data_names[data_key],
          column_types=self.data_types[data_key],
          rows=outlier_list,
          box=vbox)

# Molprobity result viewer
class coot_molprobity_todo_list_gui(coot_extension_gui):
  data_keys = [ "rama", "rota", "cbeta", "probe" ]
  data_titles = { "rama"  : "Ramachandran outliers",
                  "rota"  : "Rotamer outliers",
                  "cbeta" : "C-beta outliers",
                  "probe" : "Severe clashes" }
  data_names = { "rama"  : ["Chain", "Residue", "Name", "Score"],
                 "rota"  : ["Chain", "Residue", "Name", "Score"],
                 "cbeta" : ["Chain", "Residue", "Name", "Conf.", "Deviation"],
                 "probe" : ["Atom 1", "Atom 2", "Overlap"] }
  if (gobject is not None):
    data_types = { "rama" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "rota" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cbeta" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "probe" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT] }
  else :
    data_types = dict([ (s, []) for s in ["rama","rota","cbeta","probe"] ])

  def __init__(self, data_file=None, data=None):
    assert ([data, data_file].count(None) == 1)
    if (data is None):
      data = load_pkl(data_file)
    if not self.confirm_data(data):
      return
    coot_extension_gui.__init__(self, "MolProbity to-do list")
    self.dots_btn = None
    self.dots2_btn = None
    self._overlaps_only = True
    self.window.set_default_size(420, 600)
    self.create_property_lists(data)
    self.finish_window()

  def add_top_widgets(self, data_key, box):
    import gtk
    if data_key == "probe" :
      hbox = gtk.HBox(False, 2)
      self.dots_btn = gtk.CheckButton("Show Probe dots")
      hbox.pack_start(self.dots_btn, False, False, 5)
      self.dots_btn.connect("toggled", self.toggle_probe_dots)
      self.dots2_btn = gtk.CheckButton("Overlaps only")
      hbox.pack_start(self.dots2_btn, False, False, 5)
      self.dots2_btn.connect("toggled", self.toggle_all_probe_dots)
      self.dots2_btn.set_active(True)
      self.toggle_probe_dots()
      box.pack_start(hbox, False, False, 0)

  def toggle_probe_dots(self, *args):
    if self.dots_btn is not None :
      show_dots = self.dots_btn.get_active()
      overlaps_only = self.dots2_btn.get_active()
      if show_dots :
        self.dots2_btn.set_sensitive(True)
      else :
        self.dots2_btn.set_sensitive(False)
      show_probe_dots(show_dots, overlaps_only)

  def toggle_all_probe_dots(self, *args):
    if self.dots2_btn is not None :
      self._overlaps_only = self.dots2_btn.get_active()
      self.toggle_probe_dots()

class rsc_todo_list_gui(coot_extension_gui):
  data_keys = ["by_res", "by_atom"]
  data_titles = ["Real-space correlation by residue",
                 "Real-space correlation by atom"]
  data_names = {}
  data_types = {}

class residue_properties_list(object):
  def __init__(self, columns, column_types, rows, box,
      default_size=(380,200)):
    assert len(columns) == (len(column_types) - 1)
    if (len(rows) > 0) and (len(rows[0]) != len(column_types)):
      raise RuntimeError("Wrong number of rows:\n%s" % str(rows[0]))
    import gtk
    self.liststore = gtk.ListStore(*column_types)
    self.listmodel = gtk.TreeModelSort(self.liststore)
    self.listctrl = gtk.TreeView(self.listmodel)
    self.listctrl.column = [None]*len(columns)
    self.listctrl.cell = [None]*len(columns)
    for i, column_label in enumerate(columns):
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn(column_label)
      self.listctrl.append_column(column)
      column.set_sort_column_id(i)
      column.pack_start(cell, True)
      column.set_attributes(cell, text=i)
    self.listctrl.get_selection().set_mode(gtk.SELECTION_SINGLE)
    for row in rows :
      self.listmodel.get_model().append(row)
    self.listctrl.connect("cursor-changed", self.OnChange)
    sw = gtk.ScrolledWindow()
    w, h = default_size
    if len(rows) > 10 :
      sw.set_size_request(w, h)
    else :
      sw.set_size_request(w, 30 + (20 * len(rows)))
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    box.pack_start(sw, False, False, 5)
    inside_vbox = gtk.VBox(False, 0)
    sw.add(self.listctrl)

  def OnChange(self, treeview):
    import coot # import dependency
    selection = self.listctrl.get_selection()
    (model, tree_iter) = selection.get_selected()
    if tree_iter is not None :
      row = model[tree_iter]
      xyz = row[-1]
      if isinstance(xyz, tuple) and len(xyz) == 3 :
        set_rotation_centre(*xyz)
        set_zoom(30)
        graphics_draw()

def show_probe_dots(show_dots, overlaps_only):
  import coot # import dependency
  n_objects = number_of_generic_objects()
  sys.stdout.flush()
  if show_dots :
    for object_number in range(n_objects):
      obj_name = generic_object_name(object_number)
      if overlaps_only and not obj_name in ["small overlap", "bad overlap"] :
        sys.stdout.flush()
        set_display_generic_object(object_number, 0)
      else :
        set_display_generic_object(object_number, 1)
  else :
    sys.stdout.flush()
    for object_number in range(n_objects):
      set_display_generic_object(object_number, 0)

def load_pkl(file_name):
  pkl = open(file_name, "rb")
  data = pickle.load(pkl)
  pkl.close()
  return data

data = {}
data['rama'] = [('A', ' 133 ', 'PHE', 0.04932194665851048, (202.726, 183.959, 114.244)), ('A', ' 381 ', 'GLY', 0.021902607807035093, (167.572, 146.008, 126.576)), ('B', ' 112 ', 'SER', 0.024193484807600044, (154.667, 110.667, 111.197)), ('B', ' 113 ', 'LYS', 0.030478612506860445, (151.876, 113.26899999999998, 110.95900000000003)), ('B', ' 395 ', 'VAL', 0.049364882462946284, (126.393, 159.01399999999998, 111.886)), ('B', ' 422 ', 'ASN', 0.040211460687649886, (130.87899999999993, 162.403, 93.363)), ('B', ' 441 ', 'LEU', 0.01479816437451272, (113.42899999999997, 144.929, 91.965)), ('B', ' 503 ', 'VAL', 0.07701882929864047, (123.78999999999999, 143.731, 89.182)), ('B', ' 571 ', 'ASP', 0.03455880264217708, (134.426, 159.055, 147.91300000000004)), ('B', ' 582 ', 'LEU', 0.00022954417389166757, (114.556, 152.281, 138.517)), ('C', '  97 ', 'LYS', 0.0, (102.238, 185.071, 138.086)), ('C', '  98 ', 'SER', 0.021881163817942476, (101.257, 185.225, 134.402))]
data['omega'] = []
data['rota'] = [('A', ' 130 ', 'VAL', 0.14011960203173054, (195.26, 184.323, 117.56800000000003)), ('A', ' 227 ', 'VAL', 0.06494087698834278, (189.271, 187.818, 129.744)), ('A', ' 336 ', 'CYS', 0.11229463992039608, (178.692, 133.059, 113.29800000000003)), ('A', ' 414 ', 'GLN', 0.044440044398668804, (152.751, 146.43, 120.65)), ('A', ' 461 ', 'LEU', 0.29558236480416233, (148.811, 134.587, 119.951)), ('A', ' 760 ', 'CYS', 0.10174212209699936, (150.584, 169.737, 150.809)), ('A', '1004 ', 'LEU', 0.08041107778525074, (159.741, 168.461, 152.33400000000003)), ('A', '1096 ', 'VAL', 0.007351242675213143, (179.482, 153.7, 215.176)), ('B', '  88 ', 'ASP', 0.06056210373017422, (152.347, 120.81399999999996, 131.934)), ('B', ' 122 ', 'ASN', 0.054140645443082634, (171.968, 101.888, 125.09600000000002)), ('B', ' 227 ', 'VAL', 0.09858264611851428, (169.978, 117.84299999999998, 129.209)), ('B', ' 567 ', 'ARG', 0.03246187229896262, (128.47499999999994, 157.944, 147.613)), ('B', ' 582 ', 'LEU', 0.03276086991111273, (114.556, 152.281, 138.517)), ('B', ' 604 ', 'THR', 0.14346784023867806, (155.963, 120.288, 168.51)), ('B', ' 760 ', 'CYS', 0.08853264142323734, (173.184, 161.41399999999993, 150.77600000000004)), ('B', ' 820 ', 'ASP', 0.1946083670228784, (177.90499999999997, 134.69599999999997, 180.406)), ('B', ' 907 ', 'ASN', 0.06859228758705849, (163.635, 150.587, 206.31200000000004)), ('B', ' 916 ', 'LEU', 0.18708302230966006, (166.206, 141.48899999999995, 208.726)), ('B', ' 996 ', 'LEU', 0.09636433966871227, (167.158, 152.362, 140.34)), ('B', '1004 ', 'LEU', 0.08323773791040971, (167.32199999999995, 153.998, 152.148)), ('C', ' 130 ', 'VAL', 0.05763715138597707, (119.981, 174.151, 117.219)), ('C', ' 336 ', 'CYS', 0.28287423343693857, (172.113, 190.055, 114.143)), ('C', ' 424 ', 'LYS', 0.10837403924156078, (178.90699999999995, 165.972, 117.98600000000002)), ('C', ' 544 ', 'ASN', 0.09783126552567376, (167.574, 189.777, 130.763)), ('C', ' 615 ', 'VAL', 0.18565775959881145, (153.292, 191.394, 157.993)), ('C', ' 760 ', 'CYS', 0.13233990427554626, (154.459, 146.001, 150.43000000000004)), ('C', ' 996 ', 'LEU', 0.21921671416993208, (150.03799999999995, 155.9, 140.04)), ('C', '1004 ', 'LEU', 0.091805830378543, (150.863, 154.546, 151.894))]
data['cbeta'] = [('A', ' 130 ', 'VAL', ' ', 0.2799162469112084, (194.333, 183.191, 118.061)), ('A', '1041 ', 'ASP', ' ', 0.27550514007717514, (171.439, 160.43999999999994, 190.15300000000002)), ('B', '1041 ', 'ASP', ' ', 0.2747225839600987, (154.578, 148.024, 190.0)), ('C', ' 130 ', 'VAL', ' ', 0.2586913202556003, (121.23200000000003, 173.85399999999996, 118.086)), ('C', ' 536 ', 'ASN', ' ', 0.30355337824722517, (159.282, 201.248, 147.171)), ('C', '1041 ', 'ASP', ' ', 0.2798056918734165, (152.147, 168.808, 190.14600000000002))]
data['probe'] = [(' A 118  LEU  CB ', ' A 133  PHE  CZ ', -1.05, (200.455, 186.829, 119.491)), (' A 118  LEU  HB2', ' A 133  PHE  CZ ', -1.045, (200.854, 185.218, 119.907)), (' A 118  LEU  HB3', ' A 133  PHE  HZ ', -0.985, (199.852, 186.956, 119.341)), (' C 607  GLN  OE1', ' C 674  TYR  HE1', -0.915, (131.395, 190.187, 167.038)), (' A 118  LEU  HB3', ' A 133  PHE  CZ ', -0.9, (199.896, 186.591, 118.742)), (' A 340  GLU  O  ', ' A 344  ALA  HB2', -0.893, (170.673, 133.539, 105.275)), (' A 118  LEU  CB ', ' A 133  PHE  HZ ', -0.741, (199.724, 186.198, 119.956)), (' C 607  GLN  OE1', ' C 674  TYR  CE1', -0.712, (131.084, 189.895, 167.784)), (' A 116  SER  HB2', ' A 133  PHE  HD1', -0.627, (200.766, 181.505, 117.354)), (' B 582  LEU  N  ', ' B 582  LEU HD23', -0.513, (114.546, 151.78, 136.577)), (' A 118  LEU HD22', ' A 133  PHE  CE2', -0.493, (201.892, 187.452, 118.523)), (' A 712  ILE  CG2', ' A1096  VAL  CG1', -0.483, (180.212, 153.912, 211.086)), (' B 582  LEU  H  ', ' B 582  LEU HD23', -0.474, (114.03, 151.878, 136.582)), (' A 381  GLY  O  ', ' B 984  LEU HD21', -0.442, (169.681, 148.115, 127.262)), (' C 342  PHE  HB2', ' C1306  NAG  H82', -0.425, (167.991, 181.828, 107.26)), (' A 712  ILE HG21', ' A1096  VAL HG13', -0.408, (179.444, 153.37, 211.311))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

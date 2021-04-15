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
data['rama'] = []
data['omega'] = [('C', '   8 ', 'PRO', None, (289.166, 229.08299999999994, 217.749)), ('D', '   8 ', 'PRO', None, (224.221, 271.021, 217.749)), ('K', '   8 ', 'PRO', None, (293.0129999999999, 306.296, 217.749))]
data['rota'] = [('A', ' 319 ', 'ARG', 0.01108898567396003, (296.925, 258.325, 288.637)), ('B', ' 319 ', 'ARG', 0.011158731868831555, (263.809, 298.394, 288.637)), ('J', ' 319 ', 'ARG', 0.011078846819360395, (245.6660000000002, 249.68100000000007, 288.637))]
data['cbeta'] = []
data['probe'] = [(' B1418  HOH  O  ', ' M 106  TRP  HZ3', -0.931, (275.621, 286.606, 240.175)), (' A1418  HOH  O  ', ' F 106  TRP  HZ3', -0.919, (280.996, 253.999, 240.047)), (' E 106  TRP  HZ3', ' J1418  HOH  O  ', -0.914, (249.992, 265.334, 240.201)), (' J 878  LEU HD12', ' J1500  HOH  O  ', -0.889, (285.91, 250.544, 329.136)), (' B 878  LEU HD12', ' B1500  HOH  O  ', -0.88, (244.525, 262.973, 329.136)), (' A 878  LEU HD12', ' A1500  HOH  O  ', -0.879, (275.981, 292.601, 329.119)), (' J 458  LYS  HG3', ' J1515  HOH  O  ', -0.726, (261.202, 297.746, 251.885)), (' A 458  LYS  HG3', ' A1515  HOH  O  ', -0.719, (247.527, 247.641, 251.899)), (' B 458  LYS  HG3', ' B1515  HOH  O  ', -0.711, (297.478, 260.882, 251.935)), (' A 878  LEU  CD1', ' A1500  HOH  O  ', -0.626, (276.587, 292.573, 329.178)), (' B 878  LEU  CD1', ' B1500  HOH  O  ', -0.593, (244.506, 263.537, 329.125)), (' J1142  GLN  N  ', ' J1143  PRO  CD ', -0.583, (263.311, 262.929, 376.506)), (' B1142  GLN  N  ', ' B1143  PRO  CD ', -0.581, (266.515, 276.558, 376.342)), (' A1142  GLN  N  ', ' A1143  PRO  CD ', -0.575, (276.647, 266.923, 376.362)), (' J 878  LEU  CD1', ' J1500  HOH  O  ', -0.566, (285.563, 250.493, 329.135)), (' B1418  HOH  O  ', ' M 106  TRP  CZ3', -0.556, (275.686, 286.508, 240.295)), (' B 406  GLU  OE2', ' B1401  HOH  O  ', -0.553, (283.498, 267.596, 244.031)), (' A 406  GLU  OE2', ' A1401  HOH  O  ', -0.547, (260.652, 256.424, 244.019)), (' J 406  GLU  OE2', ' J1401  HOH  O  ', -0.543, (262.376, 281.987, 243.928)), (' E 106  TRP  CZ3', ' J1418  HOH  O  ', -0.529, (250.132, 266.12, 240.602)), (' A 230  PRO  CB ', ' B 357  ARG  NH1', -0.527, (295.535, 289.39, 261.54)), (' A 357  ARG  NH1', ' J 230  PRO  CB ', -0.525, (273.411, 235.439, 261.668)), (' B 230  PRO  CB ', ' J 357  ARG  NH1', -0.525, (237.605, 281.598, 261.588)), (' A 230  PRO  HB2', ' B 357  ARG  NH1', -0.523, (295.523, 289.93, 261.022)), (' A 357  ARG  NH1', ' J 230  PRO  HB2', -0.52, (273.479, 235.493, 261.076)), (' B 230  PRO  HB2', ' J 357  ARG  NH1', -0.517, (237.597, 281.324, 261.016)), (' B1006  THR  O  ', ' B1010  GLN  HG2', -0.517, (262.628, 269.989, 297.357)), (' J1006  THR  O  ', ' J1010  GLN  HG2', -0.517, (270.981, 262.77, 297.399)), (' B 389  ASP  HA ', ' B 528  LYS  HE3', -0.511, (274.68, 297.649, 265.107)), (' A1006  THR  O  ', ' A1010  GLN  HG2', -0.511, (273.432, 273.761, 297.724)), (' A1418  HOH  O  ', ' F 106  TRP  CZ3', -0.511, (280.59, 253.986, 240.416)), (' J 898  PHE  N  ', ' J 899  PRO  CD ', -0.507, (283.582, 251.252, 346.647)), (' A 389  ASP  HA ', ' A 528  LYS  HE3', -0.507, (290.881, 249.343, 265.047)), (' A 898  PHE  N  ', ' A 899  PRO  CD ', -0.506, (276.57, 290.249, 346.685)), (' J 389  ASP  HA ', ' J 528  LYS  HE3', -0.502, (241.068, 259.881, 264.899)), (' B 898  PHE  N  ', ' B 899  PRO  CD ', -0.491, (246.155, 264.694, 346.751)), (' A  44  ARG  O  ', ' A 283  GLY  HA2', -0.481, (294.344, 295.301, 288.04)), (' B  44  ARG  O  ', ' B 283  GLY  HA2', -0.48, (233.114, 277.736, 288.04)), (' J  44  ARG  O  ', ' J 283  GLY  HA2', -0.477, (278.811, 233.842, 287.96)), (' B 986  PRO  N  ', ' B 987  PRO  CD ', -0.461, (257.894, 258.109, 266.579)), (' A 986  PRO  N  ', ' A 987  PRO  CD ', -0.459, (265.096, 283.868, 266.942)), (' J 986  PRO  HB2', ' J 987  PRO  HD3', -0.457, (284.33, 266.024, 266.855)), (' J 763  LEU HD21', ' J1005  GLN  HG2', -0.457, (276.338, 267.907, 293.267)), (' A 986  PRO  HB2', ' A 987  PRO  HD3', -0.456, (263.199, 283.74, 267.231)), (' J 407  VAL HG12', ' J1600  HOH  O  ', -0.45, (259.989, 270.588, 249.414)), (' B 986  PRO  HB2', ' B 987  PRO  HD3', -0.449, (258.623, 256.588, 266.766)), (' J 986  PRO  N  ', ' J 987  PRO  CD ', -0.449, (283.552, 264.768, 266.621)), (' C   5  MET  HB2', ' C   5  MET  HE2', -0.445, (297.644, 231.101, 224.296)), (' B 763  LEU HD21', ' B1005  GLN  HG2', -0.444, (264.507, 263.13, 293.148)), (' A 763  LEU HD21', ' A1005  GLN  HG2', -0.443, (265.867, 275.754, 293.324)), (' B 407  VAL HG12', ' B1600  HOH  O  ', -0.441, (274.765, 275.425, 249.459)), (' J1090  PRO  HD3', ' J1095  PHE  CE2', -0.441, (254.654, 264.909, 358.885)), (' A1090  PRO  HD3', ' A1095  PHE  CE2', -0.438, (279.401, 258.535, 358.74)), (' A 407  VAL HG12', ' A1600  HOH  O  ', -0.437, (271.493, 260.335, 249.505)), (' L   7  PRO  HA ', ' L   8  PRO  HD3', -0.432, (337.55, 313.011, 231.323)), (' D   5  MET  HB2', ' D   5  MET  HE2', -0.43, (221.68, 262.68, 224.329)), (' J 396  TYR  HB2', ' J 514  SER  OG ', -0.428, (246.373, 277.523, 258.326)), (' J 329  PHE  CZ ', ' J 528  LYS  HD2', -0.428, (238.378, 260.823, 266.827)), (' B 294  ASP  HB2', ' B 295  PRO  HD2', -0.427, (248.27, 300.076, 295.753)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.427, (286.126, 298.645, 322.228)), (' A 294  ASP  HB2', ' A 295  PRO  HD2', -0.427, (306.268, 271.316, 295.549)), (' J 294  ASP  HB2', ' J 295  PRO  HD2', -0.426, (252.034, 235.382, 295.795)), (' B1090  PRO  HD3', ' B1095  PHE  CE2', -0.426, (272.436, 283.099, 358.775)), (' J1016  ALA  HB3', ' J1424  HOH  O  ', -0.425, (270.225, 266.159, 308.928)), (' B 396  TYR  HB2', ' B 514  SER  OG ', -0.424, (287.485, 283.961, 258.349)), (' A 862  PRO  HA ', ' A 863  PRO  HD3', -0.424, (270.833, 292.875, 308.239)), (' B 811  LYS  NZ ', ' B 820  ASP  OD2', -0.423, (234.36, 268.858, 322.306)), (' J 898  PHE  HB3', ' J 899  PRO  HD3', -0.423, (283.372, 250.209, 345.967)), (' J 811  LYS  NZ ', ' J 820  ASP  OD2', -0.423, (285.905, 238.853, 322.312)), (' A 329  PHE  CZ ', ' A 528  LYS  HD2', -0.422, (290.972, 246.368, 266.738)), (' C  59  ILE  HA ', ' C  60  PRO  HD3', -0.422, (276.043, 246.157, 220.899)), (' A 396  TYR  HB2', ' A 514  SER  OG ', -0.42, (272.399, 245.043, 258.256)), (' E  47  TRP  CZ2', ' E  49  GLY  HA2', -0.418, (237.819, 249.621, 228.748)), (' B 329  PHE  CZ ', ' B 528  LYS  HD2', -0.417, (277.158, 299.295, 266.763)), (' M  47  TRP  CZ2', ' M  49  GLY  HA2', -0.416, (267.709, 305.268, 228.706)), (' A1016  ALA  HB3', ' A1424  HOH  O  ', -0.414, (270.425, 271.415, 308.913)), (' B 898  PHE  HB3', ' B 899  PRO  HD3', -0.414, (245.459, 265.396, 345.967)), (' A 898  PHE  HB3', ' A 899  PRO  HD3', -0.413, (277.569, 290.636, 345.967)), (' B1016  ALA  HB3', ' B1424  HOH  O  ', -0.412, (265.884, 268.869, 308.741)), (' J 891  GLY  HA3', ' J 892  PRO  HD2', -0.409, (288.434, 269.215, 339.785)), (' A 123  ALA  HB3', ' A1314  NAG  H82', -0.408, (317.544, 305.573, 263.234)), (' B 123  ALA  HB3', ' B1314  NAG  H82', -0.407, (212.519, 292.609, 263.637)), (' J 123  ALA  HB3', ' J1314  NAG  H82', -0.405, (276.23, 208.278, 263.253)), (' F  47  TRP  CZ2', ' F  49  GLY  HA2', -0.404, (301.124, 251.756, 228.428)), (' B 811  LYS  HA ', ' B 812  PRO  HD3', -0.404, (230.51, 262.098, 322.752)), (' B 891  GLY  HA3', ' B 892  PRO  HD2', -0.402, (259.376, 251.482, 339.776)), (' A 478  THR  HA ', ' A 479  PRO  HD3', -0.402, (233.883, 248.22, 249.778)), (' O  42  ALA  HA ', ' O  43  PRO  HD3', -0.401, (253.733, 182.775, 238.791))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

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
data['omega'] = []
data['rota'] = [('B', ' 133 ', 'CYS', 0.012204796803416684, (201.75899999999996, 192.472, 204.443)), ('E', ' 432 ', 'CYS', 0.018307194113731384, (170.7019999999999, 141.545, 149.018)), ('D', ' 133 ', 'CYS', 0.012204796803416684, (189.825, 198.962, 204.417)), ('F', ' 432 ', 'CYS', 0.018307194113731384, (221.1519999999999, 249.648, 148.987))]
data['cbeta'] = []
data['probe'] = [(' B 524  GLN  NE2', ' B 580  ASN  H  ', -1.156, (195.33, 146.036, 198.149)), (' D 524  GLN  NE2', ' D 580  ASN  H  ', -1.154, (196.251, 245.496, 198.161)), (' D 327  PHE  HZ ', ' D 358  ILE HD12', -1.05, (196.462, 227.955, 172.964)), (' B 327  PHE  HZ ', ' B 358  ILE HD12', -1.043, (195.311, 163.548, 172.783)), (' F 350  VAL HG12', ' F 422  ASN  HB3', -0.964, (230.121, 239.198, 160.519)), (' E 350  VAL HG12', ' E 422  ASN  HB3', -0.939, (161.721, 151.089, 160.971)), (' B 524  GLN HE22', ' B 580  ASN  H  ', -0.921, (194.476, 145.887, 198.596)), (' B 385  TYR  HE1', ' B 393  ARG  HB3', -0.889, (180.642, 156.389, 181.113)), (' B 327  PHE  CZ ', ' B 358  ILE HD12', -0.879, (194.91, 163.425, 172.231)), (' D 524  GLN HE22', ' D 580  ASN  H  ', -0.876, (196.771, 245.022, 198.405)), (' D 327  PHE  CZ ', ' D 358  ILE HD12', -0.875, (196.791, 228.125, 172.24)), (' D 385  TYR  HE1', ' D 393  ARG  HB3', -0.872, (211.111, 235.33, 181.15)), (' D 524  GLN  NE2', ' D 580  ASN  N  ', -0.798, (195.647, 245.56, 199.278)), (' B 524  GLN  NE2', ' B 580  ASN  N  ', -0.78, (194.999, 145.993, 199.258)), (' D 429  GLN HE21', ' D 430  GLU  HG3', -0.773, (168.503, 242.636, 184.059)), (' E 379  CYS  HA ', ' E 432  CYS  HB2', -0.768, (172.687, 139.908, 148.912)), (' F 379  CYS  HA ', ' F 432  CYS  HB2', -0.763, (219.136, 251.781, 149.265)), (' B 429  GLN HE21', ' B 430  GLU  HG3', -0.757, (223.704, 148.468, 183.998)), (' D 524  GLN HE21', ' D 580  ASN  H  ', -0.756, (195.565, 245.604, 198.43)), (' D 385  TYR  CE1', ' D 393  ARG  HB3', -0.756, (210.245, 235.391, 180.712)), (' B 524  GLN HE21', ' B 580  ASN  H  ', -0.751, (196.156, 145.762, 198.591)), (' B 385  TYR  CE1', ' B 393  ARG  HB3', -0.744, (181.334, 155.848, 180.603)), (' D 524  GLN HE22', ' D 580  ASN  N  ', -0.715, (196.837, 245.82, 199.16)), (' D 429  GLN  HG3', ' D 430  GLU  H  ', -0.707, (167.119, 241.112, 183.906)), (' B 524  GLN HE22', ' B 580  ASN  N  ', -0.705, (194.751, 145.546, 199.106)), (' B 435  GLU  OE1', ' B 540  HIS  NE2', -0.704, (215.597, 149.655, 190.835)), (' B 429  GLN  HG3', ' B 430  GLU  H  ', -0.702, (225.142, 150.153, 183.907)), (' F 336  CYS  HB3', ' F 337  PRO  HD3', -0.696, (227.261, 240.02, 134.986)), (' E 336  CYS  HB3', ' E 337  PRO  HD3', -0.684, (164.364, 151.431, 135.216)), (' D 435  GLU  OE1', ' D 540  HIS  NE2', -0.662, (175.951, 242.033, 190.786)), (' E 461  LEU HD12', ' E 465  GLU  HB3', -0.66, (154.853, 146.046, 160.011)), (' B 288  LYS  NZ ', ' B 433  GLU  OE1', -0.649, (227.455, 156.564, 191.974)), (' D 288  LYS  NZ ', ' D 433  GLU  OE1', -0.645, (163.985, 235.128, 192.437)), (' F 461  LEU HD12', ' F 465  GLU  HB3', -0.641, (236.47, 245.381, 159.626)), (' B 327  PHE  HZ ', ' B 358  ILE  CD1', -0.629, (194.743, 162.609, 173.39)), (' B 385  TYR  HE1', ' B 393  ARG  CB ', -0.625, (180.462, 155.764, 181.332)), (' B 429  GLN  HG3', ' B 430  GLU  N  ', -0.62, (224.676, 150.686, 184.319)), (' E 484  GLU  HG2', ' E 489  TYR  HA ', -0.617, (152.804, 161.011, 175.887)), (' B 653  GLN  OE1', ' D 638  ASN  ND2', -0.616, (206.559, 202.785, 233.519)), (' D 385  TYR  HE1', ' D 393  ARG  CB ', -0.616, (211.173, 235.304, 181.648)), (' E 350  VAL  CG1', ' E 422  ASN  HB3', -0.611, (162.419, 151.68, 160.832)), (' F 484  GLU  HG2', ' F 489  TYR  HA ', -0.608, (238.279, 230.59, 175.936)), (' D 429  GLN  HG3', ' D 430  GLU  N  ', -0.606, (166.717, 240.43, 184.131)), (' B 638  ASN  ND2', ' D 653  GLN  OE1', -0.605, (184.904, 188.534, 233.416)), (' B 697  ARG  NH1', ' B 701  GLU  OE2', -0.592, (213.847, 182.079, 236.383)), (' B 312  GLU  O  ', ' B 316  VAL HG23', -0.587, (198.911, 153.368, 170.065)), (' D 697  ARG  NH1', ' D 701  GLU  OE2', -0.587, (177.595, 209.288, 236.19)), (' B 524  GLN HE22', ' B 579  MET  HA ', -0.586, (194.177, 146.08, 198.025)), (' D 312  GLU  O  ', ' D 316  VAL HG23', -0.586, (192.577, 238.179, 169.979)), (' D  90  ASN  HB3', ' D  93  VAL HG12', -0.585, (225.331, 245.81, 186.506)), (' D 524  GLN HE22', ' D 579  MET  HA ', -0.585, (197.382, 245.282, 198.063)), (' B 145  GLU  HB3', ' B 146  PRO  HD3', -0.58, (198.724, 182.661, 193.556)), (' B  90  ASN  HB3', ' B  93  VAL HG12', -0.573, (166.778, 145.221, 186.233)), (' D 327  PHE  HZ ', ' D 358  ILE  CD1', -0.571, (196.964, 228.747, 173.422)), (' F 350  VAL  CG1', ' F 422  ASN  HB3', -0.57, (229.262, 239.732, 160.919)), (' F 350  VAL HG12', ' F 422  ASN  CB ', -0.567, (229.61, 240.183, 161.159)), (' D 145  GLU  HB3', ' D 146  PRO  HD3', -0.567, (193.16, 208.189, 193.419)), (' B 621  ARG  HD3', ' B 678  ARG HH21', -0.563, (199.988, 174.412, 243.223)), (' D 621  ARG  HD3', ' D 678  ARG HH21', -0.559, (191.66, 216.997, 243.636)), (' F 371  SER  OG ', ' F 372  ALA  N  ', -0.557, (208.954, 237.865, 143.836)), (' B 327  PHE  CZ ', ' B 358  ILE  CD1', -0.553, (194.128, 163.343, 173.328)), (' E 371  SER  OG ', ' E 372  ALA  N  ', -0.541, (182.913, 153.431, 143.893)), (' B 503  LEU HD12', ' B 504  PHE  H  ', -0.538, (194.488, 173.085, 200.843)), (' D 503  LEU HD12', ' D 504  PHE  H  ', -0.537, (197.047, 218.225, 200.894)), (' D 269  ASP  N  ', ' D 269  ASP  OD1', -0.537, (186.137, 219.377, 202.061)), (' F 379  CYS  CA ', ' F 432  CYS  HB2', -0.535, (218.769, 250.925, 148.898)), (' D 327  PHE  CZ ', ' D 358  ILE  CD1', -0.534, (197.463, 228.258, 173.386)), (' E 347  PHE  CE2', ' E 399  SER  HB2', -0.533, (167.796, 155.873, 149.817)), (' E 350  VAL HG12', ' E 422  ASN  CB ', -0.532, (161.973, 151.008, 160.967)), (' B 269  ASP  N  ', ' B 269  ASP  OD1', -0.53, (205.765, 172.458, 202.103)), (' B 385  TYR  CE1', ' B 393  ARG  CA ', -0.528, (180.478, 155.376, 181.782)), (' F 347  PHE  CE2', ' F 399  SER  HB2', -0.527, (223.905, 235.414, 149.815)), (' D 346  PRO  HA ', ' D 359  LEU  O  ', -0.526, (195.933, 221.674, 179.187)), (' B 346  PRO  HA ', ' B 359  LEU  O  ', -0.521, (195.727, 169.554, 179.161)), (' D 385  TYR  CE1', ' D 393  ARG  CA ', -0.521, (211.089, 235.913, 182.083)), (' F 358  ILE  HB ', ' F 395  VAL HG13', -0.512, (228.649, 244.756, 139.539)), (' E 412  PRO  HB3', ' E 427  ASP  HA ', -0.51, (166.356, 136.025, 156.721)), (' F 412  PRO  HB3', ' F 427  ASP  HA ', -0.508, (225.17, 254.923, 156.903)), (' D  21  ILE HG22', ' D  22  GLU  N  ', -0.507, (234.235, 245.635, 185.763)), (' E 358  ILE  HB ', ' E 395  VAL HG13', -0.506, (162.863, 146.699, 139.261)), (' D 406  GLU  OE1', ' D 518  ARG  NH1', -0.505, (193.223, 233.179, 191.784)), (' B  21  ILE HG22', ' B  22  GLU  N  ', -0.503, (157.405, 145.799, 185.605)), (' B 287  GLN  N  ', ' B 287  GLN  OE1', -0.501, (227.432, 163.302, 194.302)), (' B 121  ASN  O  ', ' B 125  THR HG23', -0.5, (182.953, 183.461, 198.062)), (' B 406  GLU  OE1', ' B 518  ARG  NH1', -0.499, (198.442, 158.291, 191.818)), (' F 451  TYR  O  ', ' F 452  LEU HD23', -0.497, (228.837, 228.966, 163.408)), (' E 451  TYR  O  ', ' E 452  LEU HD23', -0.497, (162.849, 162.372, 163.297)), (' F 470  THR  O  ', ' F 470  THR  OG1', -0.495, (241.965, 231.16, 166.298)), (' D  23  GLU  O  ', ' D  27  THR HG23', -0.494, (232.751, 242.132, 180.743)), (' D 121  ASN  O  ', ' D 125  THR HG23', -0.493, (208.415, 208.435, 198.538)), (' B  23  GLU  O  ', ' B  27  THR HG23', -0.492, (158.631, 149.462, 180.163)), (' F 398  ASP  N  ', ' F 398  ASP  OD1', -0.492, (227.661, 242.061, 148.759)), (' B 548  THR  O  ', ' B 548  THR HG22', -0.49, (197.524, 139.561, 174.865)), (' B 615  ASP  N  ', ' B 615  ASP  OD1', -0.49, (212.586, 176.639, 225.379)), (' D 615  ASP  N  ', ' D 615  ASP  OD1', -0.487, (178.893, 214.904, 225.292)), (' D 287  GLN  N  ', ' D 287  GLN  OE1', -0.487, (164.248, 227.994, 194.275)), (' E 470  THR  O  ', ' E 470  THR  OG1', -0.486, (149.755, 160.035, 166.108)), (' D 429  GLN  NE2', ' D 430  GLU  HG3', -0.485, (168.088, 242.917, 183.759)), (' E 398  ASP  N  ', ' E 398  ASP  OD1', -0.485, (163.861, 149.411, 148.351)), (' E 383  SER  HB2', ' E 386  LYS  CG ', -0.483, (176.724, 133.763, 142.418)), (' D 105  SER  HB2', ' D 190  MET  HE2', -0.483, (218.59, 222.213, 200.388)), (' F 376  THR HG22', ' F 378  LYS  HG3', -0.477, (215.04, 246.372, 153.487)), (' F 516  GLU  N  ', ' F 516  GLU  OE1', -0.474, (229.926, 252.027, 142.892)), (' D 429  GLN  CG ', ' D 430  GLU  H  ', -0.474, (166.602, 241.198, 183.588)), (' E 516  GLU  N  ', ' E 516  GLU  OE1', -0.474, (162.38, 138.809, 142.816)), (' F 383  SER  HB2', ' F 386  LYS  CG ', -0.474, (215.383, 257.56, 142.319)), (' D 548  THR  O  ', ' D 548  THR HG22', -0.472, (194.484, 251.788, 175.274)), (' B 429  GLN  CG ', ' B 430  GLU  H  ', -0.472, (225.018, 150.155, 183.683)), (' B 105  SER  HB2', ' B 190  MET  HE2', -0.466, (173.002, 169.167, 200.238)), (' D 329  GLU  N  ', ' D 329  GLU  OE1', -0.466, (200.165, 226.015, 163.912)), (' B 385  TYR  CE1', ' B 393  ARG  HA ', -0.466, (180.921, 154.939, 181.749)), (' E 379  CYS  CA ', ' E 432  CYS  HB2', -0.463, (173.183, 140.424, 149.076)), (' B 385  TYR  CE1', ' B 393  ARG  CB ', -0.462, (180.453, 155.529, 181.268)), (' E 431  GLY  O  ', ' E 432  CYS  HB3', -0.462, (171.006, 140.139, 147.474)), (' E 376  THR HG22', ' E 378  LYS  HG3', -0.461, (176.761, 144.409, 153.633)), (' B 620  VAL  O  ', ' B 680  SER  HA ', -0.46, (200.264, 177.949, 237.138)), (' B 429  GLN  NE2', ' B 430  GLU  HG3', -0.46, (223.613, 148.714, 183.838)), (' D 385  TYR  CE1', ' D 393  ARG  CB ', -0.46, (211.205, 235.933, 181.313)), (' D 620  VAL  O  ', ' D 680  SER  HA ', -0.459, (191.227, 213.373, 237.332)), (' F 431  GLY  O  ', ' F 432  CYS  HB3', -0.456, (220.869, 251.055, 147.355)), (' D 385  TYR  CE1', ' D 393  ARG  HA ', -0.454, (210.628, 236.434, 182.001)), (' B 450  LEU  HB2', ' B 451  PRO  HD3', -0.452, (201.589, 158.264, 205.319)), (' B  75  GLU  O  ', ' B  78  THR HG22', -0.449, (161.185, 165.997, 188.782)), (' B  54  ILE HD11', ' B 343  VAL HG13', -0.446, (190.9, 180.757, 180.089)), (' E 383  SER  HB2', ' E 386  LYS  HD2', -0.445, (176.515, 133.126, 142.663)), (' D 685  VAL HG12', ' D 686  THR  N  ', -0.444, (183.521, 202.319, 225.033)), (' D  39  LEU  HA ', ' D  39  LEU HD23', -0.444, (220.987, 222.486, 176.006)), (' D 187  LYS  HD2', ' D 199  TYR  CZ ', -0.444, (213.932, 223.289, 203.707)), (' B  21  ILE  CG2', ' B  22  GLU  N  ', -0.443, (156.832, 145.344, 185.796)), (' B 329  GLU  N  ', ' B 329  GLU  OE1', -0.442, (191.476, 165.453, 163.973)), (' D 450  LEU  HB2', ' D 451  PRO  HD3', -0.442, (189.758, 233.236, 205.238)), (' F 383  SER  HB2', ' F 386  LYS  HD2', -0.441, (215.589, 258.508, 142.488)), (' B 685  VAL HG12', ' B 686  THR  N  ', -0.44, (207.858, 189.075, 225.17)), (' B 187  LYS  HD2', ' B 199  TYR  CZ ', -0.439, (177.641, 168.192, 203.541)), (' E 467  ASP  OD1', ' E 468  ILE  N  ', -0.439, (151.25, 152.942, 161.006)), (' B 305  GLN  O  ', ' B 309  LYS  HG2', -0.439, (202.784, 162.229, 167.148)), (' D  75  GLU  O  ', ' D  78  THR HG22', -0.439, (230.146, 225.491, 188.5)), (' B  54  ILE  HB ', ' B 341  LYS  HB2', -0.439, (190.501, 184.449, 176.889)), (' D 305  GLN  O  ', ' D 309  LYS  HG2', -0.438, (189.056, 228.813, 167.381)), (' B 249  MET  HB3', ' B 249  MET  HE2', -0.438, (221.835, 168.265, 214.034)), (' D  54  ILE  HB ', ' D 341  LYS  HB2', -0.438, (201.589, 207.216, 176.982)), (' F 467  ASP  OD1', ' F 468  ILE  N  ', -0.436, (240.205, 237.966, 160.973)), (' D  21  ILE  CG2', ' D  22  GLU  N  ', -0.436, (234.803, 246.173, 186.015)), (' D 235  PRO  O  ', ' D 239  HIS  HD2', -0.434, (180.003, 239.605, 210.135)), (' B 218  SER  OG ', ' B 219  ARG  N  ', -0.434, (178.811, 149.547, 206.273)), (' B 476  LYS  HB3', ' B 476  LYS  HE3', -0.431, (191.528, 165.198, 219.242)), (' B 370  LEU HD21', ' B 413  ALA  HB2', -0.431, (208.433, 158.742, 182.082)), (' D  54  ILE HD11', ' D 343  VAL HG13', -0.431, (200.395, 210.894, 180.39)), (' D 370  LEU HD21', ' D 413  ALA  HB2', -0.431, (183.379, 232.654, 182.15)), (' E 350  VAL  CG1', ' E 422  ASN  CB ', -0.431, (162.606, 151.487, 161.087)), (' D 582  ARG HH21', ' D 586  ASN HD21', -0.43, (184.963, 249.513, 200.643)), (' B 307  ILE HG23', ' B 369  PHE  HD1', -0.427, (206.806, 162.064, 174.882)), (' E 420  ASP  HB3', ' E 460  ASN  HB3', -0.427, (159.163, 142.887, 166.601)), (' D  22  GLU  N  ', ' D  22  GLU  OE1', -0.426, (233.077, 246.348, 187.375)), (' D  64  ASN  OD1', ' D  65  ALA  N  ', -0.426, (218.598, 213.6, 178.339)), (' B 429  GLN  CG ', ' B 430  GLU  N  ', -0.424, (225.104, 150.474, 183.71)), (' B 235  PRO  O  ', ' B 239  HIS  HD2', -0.424, (211.162, 151.605, 210.029)), (' D 307  ILE HG23', ' D 369  PHE  HD1', -0.424, (184.893, 229.304, 174.904)), (' D 249  MET  HB3', ' D 249  MET  HE2', -0.424, (169.803, 223.042, 213.978)), (' F 383  SER  HB2', ' F 386  LYS  HG3', -0.423, (214.534, 257.635, 141.945)), (' D 293  VAL  O  ', ' D 293  VAL HG23', -0.423, (177.571, 228.381, 177.676)), (' B  64  ASN  OD1', ' B  65  ALA  N  ', -0.422, (173.211, 177.917, 178.354)), (' D 295  ASP  HA ', ' D 298  VAL HG22', -0.422, (173.7, 222.455, 174.306)), (' B  22  GLU  N  ', ' B  22  GLU  OE1', -0.422, (158.834, 144.877, 187.45)), (' F 350  VAL  CG1', ' F 422  ASN  CB ', -0.422, (229.345, 240.048, 161.399)), (' D 218  SER  OG ', ' D 219  ARG  N  ', -0.422, (212.966, 242.214, 206.565)), (' D 148  LEU  HA ', ' D 148  LEU HD23', -0.421, (186.899, 207.683, 200.939)), (' B 385  TYR  HE1', ' B 393  ARG  CA ', -0.421, (181.053, 155.79, 181.9)), (' B 582  ARG HH21', ' B 586  ASN HD21', -0.421, (206.56, 141.578, 200.961)), (' D 689  LYS  HB2', ' D 689  LYS  HE3', -0.421, (184.693, 195.865, 215.361)), (' B 542  CYS  SG ', ' B 543  ASP  N  ', -0.42, (207.59, 146.018, 184.199)), (' B 699  GLU  H  ', ' B 699  GLU  HG2', -0.419, (216.833, 188.028, 230.43)), (' B 295  ASP  HA ', ' B 298  VAL HG22', -0.418, (218.102, 168.98, 174.348)), (' B 439  LEU  HA ', ' B 439  LEU HD23', -0.418, (212.502, 154.633, 194.259)), (' D 542  CYS  SG ', ' D 543  ASP  N  ', -0.417, (184.035, 245.841, 184.461)), (' E 516  GLU  O  ', ' E 517  LEU HD12', -0.416, (163.013, 135.086, 140.949)), (' D 476  LYS  HB3', ' D 476  LYS  HE3', -0.414, (200.22, 226.238, 219.194)), (' F 420  ASP  HB3', ' F 460  ASN  HB3', -0.413, (232.439, 248.438, 166.603)), (' F 516  GLU  O  ', ' F 517  LEU HD12', -0.412, (228.939, 256.035, 140.813)), (' B 293  VAL  O  ', ' B 293  VAL HG23', -0.412, (214.175, 163.444, 177.584)), (' B  62  MET  HB3', ' B  62  MET  HE2', -0.412, (179.423, 179.371, 179.997)), (' F 399  SER  HB3', ' F 511  VAL HG22', -0.412, (224.535, 237.954, 149.022)), (' E 383  SER  HB2', ' E 386  LYS  HG3', -0.411, (177.401, 133.647, 142.075)), (' F 439  ASN  O  ', ' F 443  SER  OG ', -0.408, (214.805, 225.784, 157.685)), (' B 148  LEU  HA ', ' B 148  LEU HD23', -0.408, (204.691, 183.848, 200.951)), (' B 582  ARG  NH2', ' B 586  ASN HD21', -0.408, (206.641, 142.112, 200.801)), (' B 424  LEU  HA ', ' B 424  LEU HD23', -0.407, (219.812, 158.715, 176.033)), (' D 344  CYS  SG ', ' D 361  CYS  N  ', -0.406, (193.333, 218.104, 177.058)), (' D 459  TRP  O  ', ' D 463  VAL HG23', -0.406, (204.277, 225.537, 213.68)), (' D 385  TYR  CD1', ' D 393  ARG  HA ', -0.406, (210.737, 237.095, 181.824)), (' E 493  GLN  HB3', ' E 493  GLN HE21', -0.405, (162.601, 160.92, 170.817)), (' D 596  LYS  HB2', ' D 596  LYS  HE3', -0.405, (175.754, 242.714, 208.255)), (' E 439  ASN  O  ', ' E 443  SER  OG ', -0.404, (177.003, 165.308, 157.279)), (' E 399  SER  HB3', ' E 511  VAL HG22', -0.404, (166.998, 153.536, 148.969)), (' D 693  ASP  OD1', ' D 694  ILE  N  ', -0.402, (178.078, 203.777, 220.758)), (' D 582  ARG  NH2', ' D 586  ASN HD21', -0.402, (184.827, 249.505, 201.118)), (' B 459  TRP  O  ', ' B 463  VAL HG23', -0.402, (187.25, 165.975, 213.56)), (' B 344  CYS  SG ', ' B 361  CYS  N  ', -0.401, (198.425, 173.311, 177.174)), (' B 270  MET  HB2', ' B 270  MET  HE2', -0.4, (202.252, 178.095, 202.145)), (' B 693  ASP  OD1', ' B 694  ILE  N  ', -0.4, (213.168, 187.34, 220.874)), (' D 270  MET  HB2', ' D 270  MET  HE2', -0.4, (189.391, 213.278, 201.985))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

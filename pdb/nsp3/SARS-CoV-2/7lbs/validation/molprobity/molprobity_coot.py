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
data['rota'] = [('A', '  30 ', 'GLN', 0.16120753719373201, (10.668000000000005, 33.469, 31.113999999999997)), ('A', ' 104 ', 'ILE', 0.06742181538211645, (25.91, 0.05599999999999999, 26.254)), ('A', ' 133 ', 'GLN', 0.1850305961152336, (15.306000000000001, 7.879999999999999, 12.684)), ('A', ' 198 ', 'THR', 0.2116330777052647, (-4.561, -12.731000000000002, 8.751)), ('A', ' 270 ', 'CYS', 0.15903662599082283, (14.651, -8.711000000000002, 38.30799999999999)), ('A', ' 286 ', 'ASP', 0.18317374298374703, (26.609, -8.877, 27.495)), ('B', '  18 ', 'THR', 0.2228974687548119, (18.93, 23.095, 9.834)), ('B', '  44 ', 'ILE', 0.13230637625453728, (26.989999999999995, 27.97500000000001, -6.8)), ('B', '  48 ', 'ASN', 0.2258601882925747, (33.16, 22.56, 2.68)), ('B', ' 104 ', 'ILE', 0.15940098587658205, (29.131, 56.422000000000004, 5.684)), ('B', ' 270 ', 'CYS', 0.04091837810849474, (22.510999999999992, 64.687, -9.553)), ('B', ' 280 ', 'GLU', 0.1302983875013192, (28.601000000000003, 73.198, 20.892))]
data['cbeta'] = []
data['probe'] = [(' A 243  MET  HE3', ' A 304  PHE  CZ ', -1.314, (12.92, -9.156, 19.019)), (' B  22  ASP  H  ', ' B  30  GLN  NE2', -1.004, (21.959, 18.82, -1.89)), (' A  84  MET  HA ', ' A  84  MET  HE2', -1.001, (15.886, 14.879, 27.349)), (' A 243  MET  HE3', ' A 304  PHE  HZ ', -0.969, (13.433, -8.693, 20.155)), (' B  22  ASP  N  ', ' B  30  GLN HE22', -0.948, (22.847, 18.746, -1.523)), (' B  22  ASP  H  ', ' B  30  GLN HE22', -0.934, (22.21, 19.312, -1.779)), (' B  21  VAL HG12', ' B  31  PHE  HZ ', -0.911, (21.11, 22.788, 1.426)), (' A 188  VAL HG12', ' A 194  GLN  HG2', -0.901, (-6.777, -26.889, 9.461)), (' B   3  ARG  HB3', ' B  23  MET  HE2', -0.876, (29.674, 16.751, 0.239)), (' B   3  ARG  NH1', ' B  23  MET  HG2', -0.869, (30.858, 17.931, -2.401)), (' B 222  ILE HD13', ' B 232  LYS  HB2', -0.861, (-1.755, 78.437, 4.573)), (' B  21  VAL HG12', ' B  31  PHE  CZ ', -0.784, (20.526, 22.859, 1.014)), (' A 189  CYS  HB3', ' A 192  CYS  HB2', -0.764, (-11.983, -27.457, 15.691)), (' A 243  MET  HE3', ' A 304  PHE  CE2', -0.732, (12.248, -8.895, 18.797)), (' A 243  MET  CE ', ' A 304  PHE  CZ ', -0.73, (12.012, -9.592, 19.594)), (' A  95  TYR  CD2', ' A 144  ALA  HB3', -0.701, (25.259, 4.431, 22.967)), (' A  34  THR HG22', ' A  41  VAL  CG2', -0.7, (17.432, 25.323, 30.477)), (' B 211  LEU HD11', ' B 300  ILE  O  ', -0.685, (16.521, 74.823, 1.842)), (' A 133 BGLN  HA ', ' A 133 BGLN  OE1', -0.683, (15.324, 6.728, 11.91)), (' B  28  GLY  N  ', ' B  42  THR  O  ', -0.674, (21.225, 27.082, -6.504)), (' A 117  LEU  HG ', ' A 121  GLN HE21', -0.668, (21.938, -0.481, 19.115)), (' B 117  LEU  O  ', ' B 121  GLN  HG3', -0.66, (22.102, 58.286, 11.969)), (' A  84  MET  CE ', ' A  84  MET  HA ', -0.653, (15.855, 15.576, 26.82)), (' A  10  THR HG21', ' A  13  ASN  HA ', -0.644, (16.851, 22.516, 18.713)), (' B 283  TYR  HD1', ' B 290  LEU HD11', -0.636, (32.214, 68.434, 12.837)), (' B 222  ILE  CD1', ' B 232  LYS  HB2', -0.63, (-2.177, 78.025, 4.093)), (' A 274  LYS  HD3', ' A 286  ASP  HB2', -0.626, (25.774, -11.33, 28.285)), (' B  38  GLY  O  ', ' B  88  ASN  HB2', -0.62, (24.945, 40.133, -1.949)), (' A  33  PRO  HB2', ' A  58  LEU HD13', -0.608, (9.258, 22.354, 29.598)), (' B 303  VAL HG12', ' B 305  TYR  CE1', -0.604, (14.04, 72.956, 10.906)), (' A 117  LEU  HG ', ' A 121  GLN  NE2', -0.601, (22.42, -0.512, 19.351)), (' A 243  MET  HG3', ' A 304  PHE  CE2', -0.594, (12.214, -9.861, 17.66)), (' A  38  GLY  O  ', ' A  88  ASN  HB2', -0.589, (18.258, 15.733, 31.389)), (' B 175  HIS  HA ', ' B 403  SO4  O3 ', -0.589, (5.926, 50.715, 9.137)), (' B   3  ARG HH12', ' B  23  MET  HG2', -0.583, (31.704, 18.178, -2.428)), (' A  27  TYR  HB2', ' A  41  VAL  O  ', -0.582, (16.63, 27.388, 33.565)), (' A  34  THR HG22', ' A  41  VAL HG23', -0.577, (16.835, 25.818, 31.004)), (' B  99  ASN HD21', ' B 279  LYS  HD2', -0.575, (27.81, 66.836, 17.715)), (' A 211  LEU HD11', ' A 300  ILE  O  ', -0.575, (13.356, -18.742, 24.615)), (' A 181  CYS  HA ', ' A 238  GLU  O  ', -0.573, (4.884, -8.464, 5.784)), (' B  41  VAL  HB ', ' B  44  ILE HG22', -0.568, (26.076, 29.831, -3.84)), (' A 122  GLN  OE1', ' A 277  THR  OG1', -0.565, (23.515, -10.475, 15.306)), (' B  56  TYR  CD2', ' B  84  MET  HE3', -0.561, (18.701, 36.957, 4.088)), (' B 255  HIS  NE2', ' B 279  LYS  O  ', -0.557, (25.881, 73.971, 19.714)), (' B 243  MET  HE3', ' B 304  PHE  CZ ', -0.552, (14.703, 65.632, 7.135)), (' B  62  ASP  O  ', ' B  66  VAL HG23', -0.552, (3.843, 31.487, 7.207)), (' A 236  GLN  HA ', ' A 310  TYR  O  ', -0.55, (3.848, -17.753, 3.693)), (' B 265  THR HG22', ' B 299  PRO  HG3', -0.548, (24.265, 74.152, -1.966)), (' B 189  CYS  HB3', ' B 192  CYS  HB2', -0.541, (-10.976, 82.797, 3.101)), (' B  48  ASN  H  ', ' B  48  ASN HD22', -0.536, (34.118, 22.463, 0.178)), (' B 265  THR HG22', ' B 299  PRO  CG ', -0.534, (24.155, 73.914, -1.977)), (' B 276  ILE  N  ', ' B 276  ILE HD12', -0.532, (24.862, 69.651, 6.982)), (' A   5  ILE HG13', ' A  21  VAL HG22', -0.531, (20.943, 34.762, 27.264)), (' B  88  ASN  OD1', ' B  91  LYS  NZ ', -0.528, (28.978, 40.195, -0.357)), (' A  89  HIS  HB2', ' A 159  VAL HG21', -0.526, (19.022, 8.709, 32.418)), (' B 243  MET  HG3', ' B 304  PHE  CE2', -0.526, (13.659, 66.017, 8.253)), (' B  14  ILE HD11', ' B  71  TYR  CE1', -0.524, (14.819, 39.494, 13.54)), (' B 170  SER  O  ', ' B 174  GLN  HG2', -0.521, (6.96, 56.913, 4.943)), (' A 166  ARG  NH1', ' A 502  HOH  O  ', -0.52, (5.0, -8.871, 26.718)), (' B  25  MET  O  ', ' B  46  PRO  HD3', -0.519, (25.359, 22.368, -4.692)), (' A   8  PHE  CE1', ' A  18  THR HG23', -0.507, (19.689, 31.759, 16.525)), (' B 181  CYS  HA ', ' B 238  GLU  O  ', -0.502, (2.695, 64.17, 17.375)), (' A 116  ALA  O  ', ' A 120  LEU  HG ', -0.501, (17.063, -3.086, 18.892)), (' B  99  ASN HD21', ' B 279  LYS  CD ', -0.498, (27.785, 66.717, 17.142)), (' B 252  GLU  HG3', ' B 297  LYS  HG3', -0.495, (24.619, 81.953, 6.771)), (' A 222  ILE HD13', ' A 232  LYS  HE3', -0.495, (-3.177, -20.848, 17.92)), (' A 115  THR  OG1', ' A 407  BO3  O3 ', -0.49, (20.618, -6.901, 25.972)), (' A  28  GLY  HA3', ' A  42  THR  O  ', -0.489, (12.87, 28.066, 35.332)), (' A  95  TYR  CE2', ' A 144  ALA  HB3', -0.485, (23.982, 4.668, 23.561)), (' B  36  LEU  HB2', ' B  55  PHE  CD2', -0.484, (25.22, 31.234, 1.549)), (' A 207  TYR  CD2', ' A 210  THR HG22', -0.484, (5.526, -18.991, 18.489)), (' A   8  PHE  CE1', ' A  18  THR  CG2', -0.481, (20.151, 32.096, 17.058)), (' A 301  THR HG21', ' A 401  XR8  C01', -0.481, (12.387, -12.606, 28.672)), (' A 129  PRO  HG2', ' A 132  LEU HD12', -0.479, (9.265, 7.347, 16.39)), (' B  36  LEU  HB2', ' B  55  PHE  CE2', -0.478, (25.619, 31.144, 1.68)), (' A   5  ILE HG13', ' A  21  VAL  CG2', -0.477, (20.554, 34.44, 27.83)), (' B 128  ASN  HB2', ' B 129  PRO  HD3', -0.476, (7.044, 49.377, 11.267)), (' B 118  LEU  O  ', ' B 122  GLN  HG3', -0.472, (21.942, 62.481, 13.304)), (' B  37  ASP  OD1', ' B 406  BO3  O1 ', -0.472, (26.859, 40.121, 5.883)), (' B 211  LEU HD21', ' B 301  THR  C  ', -0.472, (15.363, 72.169, 3.141)), (' A  82  ARG  CB ', ' A  82  ARG HH11', -0.472, (8.864, 10.735, 29.436)), (' B 166  ARG  HA ', ' B 243  MET  HE1', -0.469, (13.136, 64.325, 4.407)), (' B  47  HIS  O  ', ' B  50  HIS  HB2', -0.465, (30.135, 24.484, 1.829)), (' B   3  ARG  HB3', ' B  23  MET  CE ', -0.464, (30.699, 16.687, 0.491)), (' B  99  ASN HD21', ' B 279  LYS  CE ', -0.459, (27.665, 66.311, 17.079)), (' B 116  ALA  O  ', ' B 120  LEU  HG ', -0.457, (17.793, 58.861, 9.458)), (' A 262  SER  HB2', ' A 302  ASP  HB2', -0.457, (14.861, -12.033, 23.335)), (' B 115  THR  O  ', ' B 119  THR  OG1', -0.444, (20.097, 63.08, 8.315)), (' A 129  PRO  HG3', ' A 403  SO4  O4 ', -0.442, (6.599, 7.987, 15.572)), (' A  82  ARG  HB2', ' A  82  ARG  NH1', -0.442, (8.725, 10.568, 28.761)), (' A  18  THR  HG1', ' B  14  ILE  C  ', -0.44, (16.621, 33.782, 15.28)), (' B 187  VAL HG13', ' B 222  ILE HD11', -0.439, (-3.921, 78.352, 4.152)), (' A  18  THR  OG1', ' B  14  ILE HG23', -0.438, (16.376, 35.106, 16.62)), (' B  41  VAL  HB ', ' B  44  ILE  CG2', -0.436, (26.834, 29.657, -3.779)), (' B 147  PHE  CE2', ' B 151  ILE HD11', -0.433, (18.3, 53.793, 7.926)), (' A 136  TYR  O  ', ' A 139  ALA  HB3', -0.433, (21.331, 4.661, 15.781)), (' A 147  PHE  CE2', ' A 151  ILE HD11', -0.431, (16.499, 2.396, 20.482)), (' B  10  THR  O  ', ' B  56  TYR  HA ', -0.431, (17.38, 32.918, 4.887)), (' B 211  LEU HD22', ' B 303  VAL HG23', -0.429, (15.869, 73.317, 5.778)), (' B  47  HIS  HB2', ' B  50  HIS  CD2', -0.426, (31.305, 26.919, 0.502)), (' B 283  TYR  CD1', ' B 290  LEU HD11', -0.426, (31.552, 68.268, 13.577)), (' A 219  GLY  HA2', ' A 232  LYS  O  ', -0.425, (1.27, -24.516, 14.104)), (' A   5  ILE  CG1', ' A  21  VAL  CG2', -0.423, (20.782, 34.592, 28.446)), (' B  28  GLY  CA ', ' B  42  THR  O  ', -0.423, (20.694, 27.708, -6.718)), (' A 213  TYR  HB2', ' A 305  TYR  CE1', -0.422, (12.302, -18.064, 14.38)), (' B 207  TYR  CE2', ' B 210  THR HG22', -0.422, (6.085, 75.337, 5.111)), (' A 248  PRO  HG3', ' A 301  THR  HB ', -0.422, (12.72, -15.246, 29.003)), (' A 188  VAL  O  ', ' A 188  VAL HG23', -0.421, (-5.729, -28.851, 13.787)), (' B 255  HIS  CD2', ' B 279  LYS  O  ', -0.419, (25.357, 74.198, 19.359)), (' B 165  VAL  O  ', ' B 169  MET  HG2', -0.419, (14.838, 61.458, 4.47)), (' A  18  THR  OG1', ' B  14  ILE  CG2', -0.417, (15.866, 35.013, 16.248)), (' A 207  TYR  CE2', ' A 210  THR HG22', -0.415, (4.699, -19.321, 18.813)), (' B  22  ASP  N  ', ' B  30  GLN  NE2', -0.414, (22.441, 18.586, -1.537)), (' A 211  LEU HD22', ' A 303  VAL HG23', -0.414, (13.755, -17.232, 21.175)), (' A 265  THR HG23', ' A 505  HOH  O  ', -0.413, (20.957, -14.324, 31.369)), (' B  28  GLY  CA ', ' B  42  THR HG23', -0.411, (19.272, 29.013, -6.603)), (' A 243  MET  CE ', ' A 304  PHE  HZ ', -0.41, (12.68, -8.849, 20.723)), (' A 125  LEU HD23', ' A 127  PHE  CZ ', -0.402, (13.074, 0.936, 15.341)), (' B 249  ALA  O  ', ' B 299  PRO  HA ', -0.401, (20.282, 76.716, 0.267)), (' B 243  MET  HE3', ' B 304  PHE  HZ ', -0.4, (14.817, 64.888, 7.103))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

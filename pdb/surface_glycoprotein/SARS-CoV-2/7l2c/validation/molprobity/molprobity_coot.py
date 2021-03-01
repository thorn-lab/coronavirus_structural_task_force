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
data['omega'] = [('C', ' 147 ', 'PRO', None, (-50.956, 22.013, 47.68)), ('C', ' 149 ', 'PRO', None, (-52.93299999999997, 26.028, 43.306)), ('D', ' 141 ', 'PRO', None, (-40.265, 51.25299999999999, 38.371)), ('H', ' 147 ', 'PRO', None, (-25.146, -27.572999999999986, 64.424)), ('H', ' 149 ', 'PRO', None, (-19.545, -30.204, 64.977)), ('L', ' 141 ', 'PRO', None, (-16.257, -59.163, 56.203))]
data['rota'] = [('A', ' 118 ', 'LEU', 0.017507041037132378, (15.914, -9.227999999999994, 21.757)), ('H', '   3 ', 'GLN', 0.22775998554482546, (-2.411999999999999, -28.949, 42.089))]
data['cbeta'] = [('A', '  58 ', 'PHE', ' ', 0.38861532548134803, (40.904, -18.255, 6.0760000000000005)), ('A', ' 126 ', 'VAL', ' ', 0.255298493359244, (12.11, -11.212999999999992, 12.393)), ('B', '  17 ', 'ASN', ' ', 0.2518912109637961, (-13.14, 19.42399999999999, 8.226)), ('B', '  86 ', 'PHE', ' ', 0.2594494892827966, (8.775, 11.238999999999999, -2.638)), ('B', '  95 ', 'THR', ' ', 0.2817371235627653, (15.08800000000001, 29.482999999999997, 8.194)), ('L', ' 170 ', 'ASN', ' ', 0.3106323664705446, (-8.385999999999994, -54.368, 61.85800000000002)), ('C', '  99 ', 'LYS', ' ', 0.4071460628691669, (-6.087999999999999, 32.992, 29.905)), ('C', ' 100A', 'THR', ' ', 0.4776244930863847, (-8.864, 35.928, 32.581))]
data['probe'] = [(' B 121  ASN  OD1', ' B 126  VAL HG22', -0.713, (13.151, 14.141, 15.939)), (' A  33  THR  HB ', ' A 219  GLY  HA3', -0.702, (35.721, -21.434, 2.164)), (' A 126  VAL HG22', ' A 174  PRO  HA ', -0.687, (12.17, -13.275, 10.02)), (' B 245 BHIS  H  ', ' B 260  ALA  HB2', -0.682, (-0.569, 25.961, 16.649)), (' L  33  VAL HG22', ' L  90  SER  HB3', -0.646, (-15.323, -45.554, 28.382)), (' D  49  TYR  CD2', ' D  50  GLU  HG3', -0.639, (-11.09, 39.096, 29.123)), (' H  40  ALA  HB3', ' H  43  LYS  HB2', -0.628, (-24.344, -40.313, 46.211)), (' D   6  GLN  NE2', ' D  86  TYR  O  ', -0.625, (-25.478, 43.496, 38.396)), (' D 186  LYS  O  ', ' D 189  ARG  NH2', -0.623, (-45.674, 44.436, 74.068)), (' B 245 AHIS  H  ', ' B 260  ALA  HB2', -0.618, (-0.504, 25.918, 16.745)), (' B  38  TYR  CE1', ' B 222  ALA  HB1', -0.616, (30.01, 16.561, 4.689)), (' A  34  ARG  HE ', ' A 217  PRO  HD2', -0.609, (30.384, -24.126, 5.265)), (' C  37  VAL HG12', ' C  47  TRP  HA ', -0.602, (-21.052, 30.203, 42.304)), (' H  37  VAL HG12', ' H  47  TRP  HA ', -0.601, (-18.41, -35.703, 36.956)), (' B  38  TYR  HE1', ' B 222  ALA  HB1', -0.593, (29.303, 16.543, 5.193)), (' B 277  LEU HD23', ' B 285  ILE HD13', -0.575, (31.041, 15.272, -1.189)), (' D 138  ASP  OD1', ' D 167  GLN  NE2', -0.575, (-50.848, 48.545, 40.542)), (' H  52  ASP  HB2', ' H  58  ILE HD11', -0.573, (-17.443, -30.727, 24.951)), (' D  86  TYR  CE1', ' D 104  LEU HD12', -0.566, (-29.52, 45.439, 31.469)), (' B 206  LYS  HE3', ' B 221  SER  HB3', -0.564, (27.39, 23.143, 6.38)), (' B 121  ASN  ND2', ' B 177  MET  H  ', -0.56, (13.468, 17.871, 16.405)), (' A  56  LEU HD12', ' A  57  PRO  HD2', -0.559, (37.512, -15.92, 12.389)), (' A  34  ARG HH12', ' A 221  SER  HB2', -0.552, (30.212, -20.666, 2.201)), (' B 100  ILE HG22', ' B 242  LEU HD12', -0.55, (4.034, 24.614, 10.754)), (' B 104  TRP  H  ', ' B 119  ILE HG23', -0.542, (8.104, 13.473, 9.198)), (' A 251  PRO  HD2', ' L  55  PRO  HB3', -0.541, (-0.963, -40.319, 35.231)), (' B 121  ASN HD21', ' B 177  MET  H  ', -0.536, (13.913, 18.127, 16.692)), (' D   9  SER  HB2', ' D 143  ALA  HB3', -0.531, (-35.224, 47.566, 40.763)), (' B 147  LYS  HE2', ' C  30  ILE  HA ', -0.529, (-9.507, 18.971, 32.391)), (' L  35  TRP  HB2', ' L  48  ILE  HB ', -0.525, (-8.398, -47.683, 34.684)), (' A  40  ASP  OD1', ' A  41  LYS  N  ', -0.525, (28.919, -2.051, -0.733)), (' B 153  MET  HE1', ' B 403  NAG  H61', -0.52, (-0.4, 13.059, 29.085)), (' L 111  ALA  HB3', ' L 140  TYR  H  ', -0.519, (-16.222, -59.813, 60.289)), (' B 143  VAL HG22', ' B 154  GLU  HG2', -0.518, (2.356, 19.276, 20.938)), (' A 276  LEU HD22', ' A 301  CYS  HA ', -0.516, (46.351, -10.337, -2.028)), (' A  34  ARG  NE ', ' A 217  PRO  HD2', -0.514, (30.656, -23.672, 5.147)), (' B  29  THR HG23', ' B  62  VAL HG23', -0.509, (14.144, 27.455, -4.267)), (' L  34  SER  OG ', ' L  89  SER  OG ', -0.505, (-13.006, -41.975, 32.614)), (' H  66  ARG  NH2', ' H  86  ASP  OD2', -0.502, (-29.713, -29.299, 44.095)), (' B 119  ILE HD12', ' B 128  ILE HG12', -0.501, (10.772, 9.916, 12.515)), (' L 145  THR  HB ', ' L 196  THR  HB ', -0.497, (-28.474, -57.491, 54.424)), (' L 132  LEU HD12', ' L 178  LEU HD23', -0.496, (-38.151, -49.23, 64.203)), (' C 150  VAL HG12', ' C 200  HIS  HB2', -0.48, (-56.558, 27.124, 48.54)), (' D 156  LYS  H  ', ' D 156  LYS  HG2', -0.477, (-32.567, 40.414, 63.054)), (' D  66  LYS  HA ', ' D  71  ALA  HA ', -0.474, (-14.646, 49.699, 37.74)), (' C  87  THR HG23', ' C 110  THR  HA ', -0.472, (-36.428, 22.686, 44.944)), (' B 105  ILE HG22', ' B 118  LEU HD12', -0.471, (3.253, 10.947, 10.009)), (' A  71  SER  HB2', ' A  75  GLY  HA3', -0.467, (20.463, -38.773, 30.049)), (' C   2  VAL HG12', ' C  27  TYR  HB2', -0.466, (-14.486, 23.156, 25.086)), (' L 194  GLN  HG2', ' L 203  GLU  HG3', -0.464, (-34.932, -59.648, 61.985)), (' C  83  ARG  HG2', ' C  84  SER  H  ', -0.464, (-34.347, 22.999, 54.579)), (' A 143  VAL HG12', ' A 154  GLU  HG2', -0.462, (5.659, -20.734, 20.833)), (' D 105  THR HG21', ' D 141  PRO  HB3', -0.457, (-38.182, 49.431, 36.188)), (' A 105  ILE HG22', ' A 118  LEU HD22', -0.456, (16.507, -11.947, 23.822)), (' A 105  ILE HD13', ' A 105  ILE HG21', -0.455, (17.523, -13.73, 26.06)), (' B 251  PRO  HD2', ' D  55  PRO  HB3', -0.453, (-16.958, 36.036, 24.593)), (' B  47  VAL HG12', ' B 279  TYR  HB2', -0.452, (38.761, 12.637, -0.647)), (' A 289  VAL HG21', ' A 300  LYS  HD2', -0.452, (46.24, -15.924, -1.039)), (' H 185  PRO  HB2', ' H 188  SER  HB3', -0.451, (-18.914, -55.221, 84.953)), (' C  42  GLY  HA3', ' D 163  THR HG21', -0.45, (-36.911, 35.968, 42.797)), (' B  36  VAL  O  ', ' B 223  LEU  HB2', -0.45, (25.48, 17.501, 1.716)), (' H 127  SER  H  ', ' H 130  SER  HB2', -0.449, (-29.593, -55.098, 78.807)), (' C   2  VAL HG11', ' C  32  LEU HD13', -0.448, (-14.816, 24.406, 26.933)), (' B 206  LYS  NZ ', ' B 208  THR  OG1', -0.446, (25.187, 24.857, 8.609)), (' B 130  VAL HG21', ' B 231  ILE  HB ', -0.445, (9.556, 1.999, 7.156)), (' H 159  LEU HD21', ' H 182  VAL HG21', -0.445, (-18.106, -47.772, 79.854)), (' A 177  MET  HB3', ' A 177  MET  HE2', -0.445, (9.964, -20.577, 11.517)), (' A 185  ASN  O  ', ' A 186  PHE  C  ', -0.443, (19.305, -32.97, 4.605)), (' C 141  LEU  CD2', ' C 143  LYS  HB2', -0.44, (-52.069, 32.553, 56.988)), (' D  83  GLU  HB2', ' D 106  VAL HG23', -0.439, (-35.112, 46.737, 29.371)), (' A 185  ASN  HB3', ' A 187  LYS  HG3', -0.432, (21.573, -33.641, 6.673)), (' C  32  LEU HD12', ' C  94  THR  OG1', -0.432, (-15.065, 25.222, 30.0)), (' A 127  VAL HG11', ' A 129  LYS  HE3', -0.431, (8.647, -8.062, 19.206)), (' D 132  LEU HD12', ' D 178  LEU HD23', -0.431, (-42.437, 41.574, 61.49)), (' A  77  LYS  HB3', ' A  77  LYS  HE2', -0.429, (15.641, -34.351, 25.916)), (' C 126  PRO  HG3', ' C 138  LEU HD12', -0.429, (-62.108, 45.838, 57.3)), (' D 145  THR  HB ', ' D 196  THR HG23', -0.429, (-35.056, 48.739, 49.217)), (' C 139  GLY  HA3', ' C 181  VAL HG12', -0.429, (-56.19, 42.371, 53.279)), (' C  35  HIS  ND1', ' C  50  GLY  HA3', -0.429, (-14.731, 26.741, 40.4)), (' B  95  THR HG22', ' B 187  LYS  HB3', -0.427, (16.102, 30.768, 10.445)), (' D 167  GLN  HG3', ' D 169  ASN  H  ', -0.426, (-51.336, 45.842, 37.729)), (' C 121  VAL  H  ', ' C 312  PGE  H5 ', -0.425, (-58.816, 29.51, 58.377)), (' H 139  GLY  HA2', ' H 154  TRP  CZ2', -0.423, (-23.643, -45.112, 76.746)), (' C  98 BTYR  CE1', ' C  99  LYS  HG2', -0.422, (-7.043, 30.77, 27.941)), (' L  85  ASP  OD1', ' L 103  LYS  HD3', -0.422, (-15.438, -49.691, 48.479)), (' L  33  VAL HG22', ' L  90  SER  CB ', -0.421, (-15.78, -45.384, 28.439)), (' H 142  VAL  HB ', ' H 178  LEU  HG ', -0.421, (-24.829, -38.08, 69.233)), (' A 187  LYS  HB2', ' A 210  ILE HG13', -0.418, (23.22, -30.356, 5.57)), (' A 104  TRP  CD1', ' A 240  THR HG22', -0.417, (21.939, -17.376, 19.533)), (' A  34  ARG  HD2', ' A 219  GLY  HA2', -0.416, (33.584, -22.274, 3.713)), (' A 100  ILE HG22', ' A 242  LEU HD12', -0.415, (17.003, -24.68, 21.095)), (' A  89  GLY  HA3', ' A 270  LEU HD12', -0.415, (31.947, -9.473, 14.301)), (' C  52  ASP  HB2', ' C  58  ILE HD11', -0.415, (-8.357, 27.361, 43.744)), (' H 145  TYR  HE1', ' H 148  GLU  HG2', -0.415, (-22.69, -33.403, 64.27)), (' L 165  SER  O  ', ' L 172  TYR  HA ', -0.414, (-16.12, -50.99, 60.857)), (' A  34  ARG HH22', ' A 221  SER  HB2', -0.413, (29.282, -20.929, 2.613)), (' B  95  THR  HA ', ' B 189  LEU  HA ', -0.413, (16.214, 27.393, 9.051)), (' D 115  VAL HG22', ' D 136  ILE HG23', -0.407, (-45.216, 49.104, 49.485)), (' D  19  VAL HG23', ' D  78  LEU HD11', -0.407, (-29.927, 52.815, 30.263)), (' B  49  HIS  NE2', ' B  51  THR  OG1', -0.405, (31.534, 8.881, -5.302)), (' D   6  GLN  HG2', ' D 102  THR  OG1', -0.405, (-26.642, 45.688, 40.89)), (' A 193  VAL HG13', ' A 270  LEU HD11', -0.402, (30.529, -11.036, 11.643)), (' A 277  LEU HD23', ' A 285  ILE HD13', -0.401, (33.677, -10.947, -0.665)), (' C 165  THR HG23', ' C 180  SER  HB2', -0.4, (-56.32, 37.357, 47.194)), (' A 274  THR HG23', ' A 291  CYS  HB2', -0.4, (45.812, -9.085, 4.502))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

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
data['rama'] = [('H', '  25 ', 'ALA', 0.0020848359333289187, (129.45499999999996, 156.21500000000006, 133.817)), ('H', '  31 ', 'SER', 0.0005428274330222609, (137.72299999999993, 160.213, 135.29)), ('H', '  32 ', 'SER', 8.517961602210994e-05, (137.80299999999994, 164.00300000000004, 135.001))]
data['omega'] = [('A', ' 146 ', 'PRO', None, (184.15799999999993, 150.20300000000003, 163.361)), ('H', ' 113 ', 'ASP', None, (123.46499999999999, 167.52800000000005, 132.582))]
data['rota'] = [('E', ' 493 ', 'GLN', 0.16503541222831056, (146.358, 170.37100000000004, 141.507)), ('E', ' 493 ', 'GLN', 0.0036975846218620903, (146.33, 170.34400000000005, 141.509))]
data['cbeta'] = []
data['probe'] = [(' H  29  THR  N  ', ' H  99  ARG HH22', -1.011, (131.788, 162.869, 130.492)), (' H   5  LEU HD23', ' H  26  SER  H  ', -1.007, (126.378, 157.901, 133.64)), (' H  29  THR HG23', ' H  99  ARG  NH2', -0.912, (132.544, 163.197, 131.459)), (' H   6  GLN  HB2', ' H  24  LYS  HB3', -0.889, (126.156, 152.255, 134.277)), (' H  30  PHE  O  ', ' H  32  SER  N  ', -0.863, (136.526, 162.602, 134.785)), (' H  29  THR HG21', ' H  33  TYR  CE2', -0.822, (134.413, 165.706, 130.744)), (' H  29  THR  CG2', ' H  99  ARG  NH2', -0.807, (132.377, 163.729, 130.289)), (' H  31  SER  OG ', ' H  75  LYS  HB2', -0.758, (139.351, 156.855, 136.002)), (' H  33  TYR  HE1', ' H 101  ARG  HA ', -0.756, (131.329, 169.79, 133.669)), (' H  33  TYR  HD1', ' H 100  GLU  O  ', -0.75, (131.37, 167.877, 135.551)), (' H   5  LEU HD23', ' H  26  SER  N  ', -0.75, (126.713, 157.148, 133.513)), (' H 112  PHE  HB3', ' H 114  TYR  H  ', -0.722, (124.298, 165.61, 132.809)), (' H  29  THR  N  ', ' H  99  ARG  NH2', -0.693, (132.262, 162.932, 130.697)), (' H  34  ALA  O  ', ' H 100  GLU  HB3', -0.679, (130.362, 166.741, 138.673)), (' A 524  GLN  HB3', ' A 574  VAL HG11', -0.679, (187.867, 180.906, 142.52)), (' H  29  THR  H  ', ' H  99  ARG HH22', -0.66, (131.842, 162.73, 129.633)), (' H  34  ALA  HB3', ' H 100  GLU  HB3', -0.655, (131.355, 167.79, 138.964)), (' E 376  THR  HB ', ' E 435  ALA  HB3', -0.644, (148.373, 188.07, 154.4)), (' H  29  THR HG21', ' H  33  TYR  HE2', -0.623, (134.466, 166.339, 130.663)), (' H  87  LEU  HB3', ' H  91  ASP  HB2', -0.611, (118.13, 157.324, 156.233)), (' H 113  ASP  HA ', ' L  48  LEU HD23', -0.609, (121.803, 168.627, 133.371)), (' A 574  VAL HG23', ' A 576  ALA  H  ', -0.605, (187.39, 183.21, 138.758)), (' H   5  LEU HD23', ' H  26  SER  HB3', -0.605, (126.416, 158.11, 133.476)), (' H  33  TYR  CE1', ' H 101  ARG  HA ', -0.594, (132.172, 169.204, 134.029)), (' E 401  VAL HG22', ' E 509  ARG  HG2', -0.594, (143.159, 179.504, 154.438)), (' L  51  TYR  HB3', ' L  55  ASN  HB3', -0.592, (122.713, 178.616, 129.955)), (' A 285  PHE  HB2', ' A 437  ASN HD21', -0.59, (204.704, 174.13, 166.117)), (' H  29  THR  CG2', ' H  33  TYR  CD2', -0.587, (133.973, 165.028, 131.392)), (' E 355  ARG  NE ', ' E 398  ASP  OD1', -0.585, (134.223, 188.125, 146.403)), (' H  29  THR  CG2', ' H  33  TYR  CE2', -0.576, (133.409, 165.49, 130.951)), (' A 190  MET  O  ', ' A 194  ASN  ND2', -0.572, (173.078, 154.986, 129.545)), (' L  67  SER  HG ', ' L  74  SER  HG ', -0.564, (114.8, 187.156, 135.932)), (' L  63  ARG  NH1', ' L  84  ASP  OD2', -0.563, (105.588, 175.896, 128.005)), (' L  34  ASP  HB3', ' L  53  ASN  HB2', -0.563, (124.211, 182.006, 137.245)), (' H  33  TYR  CD1', ' H 100  GLU  O  ', -0.56, (131.863, 168.105, 135.025)), (' H  24  LYS  O  ', ' H  26  SER  N  ', -0.557, (127.083, 155.9, 133.688)), (' H  29  THR HG23', ' H  33  TYR  CD2', -0.549, (133.526, 164.706, 131.734)), (' A 378  HIS  HE1', ' A 402  GLU  HA ', -0.548, (179.064, 170.203, 150.811)), (' A  35  GLU  OE2', ' E 493 BGLN  NE2', -0.538, (150.358, 166.91, 140.665)), (' A 177  ARG  NH2', ' A 495  GLU  O  ', -0.538, (192.56, 141.362, 139.43)), (' A 381  TYR  HD1', ' A 558  LEU HD22', -0.538, (176.049, 178.604, 147.768)), (' A 145  GLU  OE1', ' A 149  ASN  ND2', -0.538, (185.753, 153.654, 159.941)), (' E 366  SER  O  ', ' E 370  ASN  ND2', -0.537, (140.29, 198.03, 165.957)), (' A 375  GLU  HA ', ' A 378  HIS  HD2', -0.537, (176.627, 171.044, 155.802)), (' A  85  LEU  HA ', ' A  88  ILE HD12', -0.535, (164.891, 169.933, 123.573)), (' A 245  ARG  NH2', ' A 260  GLY  O  ', -0.534, (210.709, 159.076, 148.208)), (' H  99  ARG  HB3', ' H 112  PHE  HB2', -0.533, (127.185, 165.605, 134.576)), (' H  42  PRO  HD3', ' H  93  ALA  HA ', -0.529, (112.738, 159.831, 149.058)), (' L  22  CYS  HB3', ' L  73  ALA  HB3', -0.527, (115.897, 182.136, 141.705)), (' H   5  LEU  CD2', ' H  26  SER  HB3', -0.525, (126.112, 158.603, 133.143)), (' A 126  ILE HG22', ' A 172  VAL HG13', -0.525, (184.529, 143.723, 150.129)), (' A  30  ASP  OD2', ' E 417  LYS  NZ ', -0.525, (152.075, 177.104, 135.122)), (' A 515  TYR  HD1', ' A 518  ARG HH11', -0.523, (185.593, 166.224, 149.399)), (' A 402  GLU  HB3', ' A 518  ARG  HG3', -0.516, (182.443, 169.258, 148.0)), (' H   7  GLN  O  ', ' H 117  GLN  NE2', -0.516, (120.284, 151.884, 137.298)), (' L  91  GLN HE21', ' L 100  SER  HB2', -0.513, (124.939, 173.492, 143.249)), (' E 418  ILE HD13', ' E 422  ASN HD22', -0.509, (146.85, 179.717, 142.007)), (' L  80  LEU HD23', ' L 110  VAL HG12', -0.509, (100.628, 176.195, 132.648)), (' A  83  TYR  O  ', ' A 101  GLN  NE2', -0.504, (163.04, 165.73, 125.205)), (' A 227  GLU  OE2', ' A 458  LYS  NZ ', -0.495, (195.923, 161.772, 132.046)), (' A 144  LEU HD12', ' A 148  LEU  HB2', -0.494, (189.24, 148.493, 158.367)), (' A 201  ASP  OD2', ' A 219  ARG  NE ', -0.494, (180.307, 162.705, 127.339)), (' A 346  PRO  HB3', ' A 360  MET  HE2', -0.492, (177.437, 167.475, 161.036)), (' H   5  LEU HD23', ' H  26  SER  CB ', -0.491, (126.033, 157.833, 133.165)), (' H  34  ALA  O  ', ' H 100  GLU  N  ', -0.491, (130.263, 166.229, 138.104)), (' A 403  ALA  HB2', ' A 518  ARG  HG2', -0.489, (183.82, 172.445, 146.83)), (' A 524  GLN  HG2', ' A 583  PRO  HG2', -0.487, (191.159, 180.463, 142.541)), (' H  33  TYR  O  ', ' H  54  PRO  HD2', -0.484, (134.611, 163.476, 138.491)), (' H  40  GLN  HB2', ' H  46  LEU HD23', -0.477, (115.174, 164.99, 144.497)), (' A 148  LEU HD23', ' A 151  ILE HD12', -0.476, (192.139, 146.647, 161.988)), (' H  74  ASP  HB3', ' H  77  THR HG22', -0.474, (135.674, 151.546, 139.794)), (' H   7  GLN  NE2', ' H  95  TYR  O  ', -0.47, (120.595, 157.123, 142.559)), (' A 131  LYS  HB3', ' A 143  LEU HD23', -0.462, (183.43, 142.544, 159.422)), (' A 184  VAL HG22', ' A 464  PHE  HE1', -0.461, (184.589, 150.344, 135.595)), (' L  20  ILE  HB ', ' L  75  LEU  HB3', -0.461, (110.658, 180.317, 137.516)), (' H  41  ALA  HB3', ' H  44  GLN  HB2', -0.46, (111.769, 164.68, 150.357)), (' A 419  LYS  HE2', ' A 428  PHE  HB3', -0.455, (194.522, 184.872, 170.914)), (' A 305  GLN HE21', ' A 309  LYS  HE2', -0.449, (169.032, 178.107, 169.027)), (' A 557  MET  HG2', ' A 569  ALA  HB1', -0.449, (177.661, 180.35, 141.324)), (' E 457  ARG  NH1', ' E 459  SER  O  ', -0.448, (141.951, 181.962, 131.917)), (' H  29  THR HG21', ' H  33  TYR  CD2', -0.448, (134.139, 165.659, 131.621)), (' L  39  GLN  HG3', ' L  88  TYR  HE1', -0.448, (110.565, 171.805, 134.131)), (' E 418  ILE  HA ', ' E 422  ASN  HB2', -0.447, (145.518, 181.459, 141.737)), (' H  34  ALA  O  ', ' H 100  GLU  CB ', -0.444, (130.172, 167.222, 138.66)), (' H  11  GLU  HB2', ' H 121  VAL HG22', -0.442, (117.885, 151.266, 147.693)), (' A 119  ILE HG22', ' A 123  MET  HE2', -0.441, (178.917, 145.203, 141.328)), (' H  32  SER  O  ', ' H  33  TYR  CD2', -0.441, (135.081, 165.611, 133.56)), (' L  48  LEU  HB3', ' L  57  PRO  HG3', -0.441, (119.769, 172.297, 130.682)), (' L  36  HIS  N  ', ' L  91  GLN  O  ', -0.436, (121.166, 177.727, 140.548)), (' A 381  TYR  CD1', ' A 558  LEU HD22', -0.435, (176.003, 178.096, 147.811)), (' A 177  ARG  HB2', ' A 498  CYS  HB2', -0.431, (189.288, 142.345, 142.377)), (' H  31  SER  O  ', ' H  55  ILE HD13', -0.429, (140.389, 161.223, 135.342)), (' L   6  GLN  NE2', ' L  88  TYR  O  ', -0.429, (111.382, 175.992, 141.929)), (' A 159  ASN  HA ', ' A 162  LEU  HB3', -0.425, (202.793, 144.919, 159.528)), (' A 168  TRP  CD1', ' A 502  SER  HB2', -0.425, (189.666, 147.647, 151.273)), (' E 350  VAL HG22', ' E 422  ASN  HB3', -0.424, (143.155, 180.714, 143.173)), (' H  25  ALA  C  ', ' H  27  GLY  N  ', -0.422, (128.068, 157.051, 131.475)), (' A 430  GLU  OE1', ' A 541  LYS  NZ ', -0.418, (197.258, 185.529, 163.206)), (' A 307  ILE HG23', ' A 369  PHE  HD1', -0.418, (180.174, 175.295, 167.816)), (' H 113  ASP  HB3', ' L  48  LEU  HB2', -0.415, (120.6, 169.575, 131.685)), (' A 232  GLU  HB2', ' A 581  VAL HG21', -0.414, (198.65, 174.401, 139.984)), (' A 237  TYR  CZ ', ' A 451  PRO  HG2', -0.413, (200.454, 163.904, 146.899)), (' L  41  LEU HD23', ' L  86  ALA  HB2', -0.413, (107.368, 168.927, 134.102)), (' E 417  LYS  O  ', ' E 422  ASN  ND2', -0.411, (146.686, 180.064, 140.597)), (' A 382  ASP  OD1', ' A 385  TYR  OH ', -0.411, (171.72, 173.051, 147.739)), (' A 458  LYS  HG2', ' A 462  MET  HE2', -0.41, (195.085, 157.563, 134.354)), (' H  32  SER  O  ', ' H  32  SER  OG ', -0.408, (137.675, 165.735, 133.807)), (' H 110  TYR  HB3', ' L  36  HIS  CE1', -0.408, (124.479, 175.764, 136.761)), (' A 229  THR  HB ', ' A 581  VAL HG13', -0.406, (195.059, 173.247, 139.905)), (' L   4  LEU  HB2', ' L 103  GLY  HA2', -0.405, (116.429, 177.121, 147.312)), (' A 446  ILE HD13', ' A 523  PHE  HZ ', -0.404, (192.409, 173.757, 151.87)), (' L  38  TYR  HE1', ' L  48  LEU HD22', -0.402, (120.612, 171.184, 135.494)), (' E 407  VAL HG21', ' E 508  TYR  HD2', -0.4, (150.77, 184.558, 153.63)), (' E 358  ILE  HB ', ' E 395  VAL  HB ', -0.4, (130.459, 193.96, 153.221))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

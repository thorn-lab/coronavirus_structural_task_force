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
data['rota'] = [('A', ' 190 ', 'ARG', 0.0928752520190699, (210.991, 162.184, 195.078)), ('A', ' 834 ', 'ILE', 0.26231449755582836, (220.729, 183.83999999999995, 220.72999999999996)), ('A', ' 841 ', 'LEU', 0.23411063960752454, (222.74, 191.233, 221.57299999999998)), ('B', ' 190 ', 'ARG', 0.09281159857816988, (167.927, 232.38599999999994, 195.084)), ('B', ' 740 ', 'MET', 0.115700029164414, (193.53999999999996, 197.69699999999995, 209.112)), ('B', ' 841 ', 'LEU', 0.17749797815726653, (187.20699999999982, 207.41999999999996, 221.65600000000003)), ('C', ' 190 ', 'ARG', 0.09265460057628946, (250.24100000000016, 234.582, 195.081)), ('C', ' 466 ', 'ARG', 0.24323598665677193, (203.935, 182.90799999999996, 173.128)), ('C', ' 841 ', 'LEU', 0.1472723678205413, (219.048, 230.36999999999998, 221.489)), ('H', '   5 ', 'VAL', 0.14750007761866915, (189.41499999999996, 125.577, 165.407)), ('G', '   5 ', 'VAL', 0.14782383711534347, (147.003, 269.40299999999985, 165.456)), ('I', '   5 ', 'VAL', 0.14751334141829275, (292.748, 234.213, 165.433))]
data['cbeta'] = [('A', '  14 ', 'GLN', ' ', 0.30111757323291216, (202.287, 154.727, 166.632)), ('A', '  63 ', 'THR', ' ', 0.33417073532066743, (194.37200000000004, 164.40599999999995, 195.14899999999997)), ('A', '  66 ', 'HIS', ' ', 0.28883189975307544, (197.824, 153.154, 193.081)), ('A', '  82 ', 'PRO', ' ', 0.35499146278481974, (193.71399999999997, 161.349, 186.64700000000002)), ('A', '  91 ', 'TYR', ' ', 0.3333339119494389, (203.40399999999997, 169.61099999999996, 195.74999999999997)), ('A', ' 192 ', 'PHE', ' ', 0.31662068179611624, (208.79499999999996, 167.80299999999997, 191.39100000000002)), ('A', ' 259 ', 'THR', ' ', 0.3458267363650092, (204.049, 144.313, 193.595)), ('A', ' 837 ', 'TYR', ' ', 0.31163931696078573, (221.987, 187.852, 218.103)), ('B', '  14 ', 'GLN', ' ', 0.3021209736918698, (165.8, 243.671, 166.646)), ('B', '  63 ', 'THR', ' ', 0.33296061328156296, (178.168, 245.66299999999993, 195.15299999999996)), ('B', '  66 ', 'HIS', ' ', 0.2892944146174506, (166.69599999999997, 248.307, 193.09700000000004)), ('B', '  82 ', 'PRO', ' ', 0.3534681019290738, (175.84199999999998, 247.768, 186.65499999999997)), ('B', '  91 ', 'TYR', ' ', 0.33235005055225747, (178.156, 235.238, 195.747)), ('B', ' 192 ', 'PHE', ' ', 0.31562659509714863, (173.88799999999983, 231.47799999999998, 191.39)), ('B', ' 259 ', 'THR', ' ', 0.34634526419762374, (155.92799999999994, 247.33999999999995, 193.62099999999998)), ('C', '  14 ', 'GLN', ' ', 0.3023929750796593, (261.066, 230.78599999999994, 166.639)), ('C', '  63 ', 'THR', ' ', 0.33323176714856984, (256.626, 219.079, 195.148)), ('C', '  66 ', 'HIS', ' ', 0.28955342689292746, (264.646, 227.695, 193.088)), ('C', '  82 ', 'PRO', ' ', 0.35236144139907655, (259.608, 220.04099999999994, 186.648)), ('C', '  91 ', 'TYR', ' ', 0.33267412514223865, (247.602, 224.297, 195.74599999999998)), ('C', ' 192 ', 'PHE', ' ', 0.31584375070464993, (246.47499999999997, 229.87299999999996, 191.38899999999998)), ('C', ' 259 ', 'THR', ' ', 0.3453398144276689, (269.189, 237.50599999999994, 193.60899999999998)), ('H', '  39 ', 'GLN', ' ', 0.2525566810331985, (202.146, 128.935, 156.03)), ('G', '  39 ', 'GLN', ' ', 0.25168264749421226, (143.53, 256.7059999999998, 156.074)), ('I', '  39 ', 'GLN', ' ', 0.2513558863133589, (283.479, 243.56399999999996, 156.055))]
data['probe'] = [(' Z   1  NAG  H62', ' Z   2  NAG  H82', -1.097, (236.114, 224.048, 265.436)), (' Z   1  NAG  C6 ', ' Z   2  NAG  H82', -0.83, (236.931, 223.39, 265.674)), (' Z   1  NAG  H62', ' Z   2  NAG  C8 ', -0.772, (235.871, 224.641, 265.839)), (' C 231  ILE HD12', ' C 233  ILE HG12', -0.605, (241.161, 222.546, 178.559)), (' C 537  LYS  HE2', ' C 628  GLN HE21', -0.601, (245.482, 200.453, 201.19)), (' A 231  ILE HD12', ' A 233  ILE HG12', -0.6, (205.08, 175.967, 178.588)), (' C1028  LYS  NZ ', ' C1042  PHE  O  ', -0.6, (219.985, 215.199, 249.325)), (' B 537  LYS  HE2', ' B 628  GLN HE21', -0.595, (199.791, 245.29, 201.18)), (' G   6  GLU  HA ', ' G  22  CYS  HA ', -0.589, (151.218, 268.577, 163.503)), (' I   6  GLU  HA ', ' I  22  CYS  HA ', -0.588, (290.019, 231.56, 163.117)), (' H  57  LYS  H  ', ' P   1  NAG  H81', -0.587, (194.734, 148.653, 166.75)), (' B 231  ILE HD12', ' B 233  ILE HG12', -0.584, (182.832, 229.971, 178.844)), (' I  57  LYS  H  ', ' f   1  NAG  H81', -0.583, (270.127, 227.319, 166.694)), (' H   6  GLU  HA ', ' H  22  CYS  HA ', -0.581, (188.279, 129.33, 163.032)), (' C 877  LEU HD23', ' C 888  PHE  HE2', -0.581, (208.242, 227.805, 253.005)), (' G 100B TYR  HE2', ' J  50  LYS  HE2', -0.573, (145.689, 246.698, 177.709)), (' C 442  ASP  O  ', ' C 448  ASN  ND2', -0.572, (210.013, 191.654, 153.906)), (' I 100B TYR  HE2', ' K  50  LYS  HE2', -0.571, (273.69, 246.752, 177.71)), (' B1141  LEU HD21', ' C1145  LEU HD22', -0.569, (211.462, 211.906, 299.743)), (' H 100B TYR  HE2', ' L  50  LYS  HE2', -0.569, (209.638, 135.77, 177.612)), (' B 442  ASP  O  ', ' B 448  ASN  ND2', -0.567, (224.76, 218.816, 153.645)), (' A 442  ASP  O  ', ' A 448  ASN  ND2', -0.566, (194.416, 218.162, 153.787)), (' A1145  LEU HD22', ' C1141  LEU HD21', -0.565, (210.995, 207.18, 299.166)), (' B 720  ILE HG13', ' B 923  ILE HG23', -0.562, (188.8, 217.105, 264.571)), (' C 977  LEU HD11', ' C 997  ILE HD11', -0.562, (208.813, 223.208, 202.519)), (' G  57  LYS  H  ', ' X   1  NAG  H81', -0.562, (164.261, 253.035, 166.729)), (' A 230  PRO  HB3', ' C 355  ARG HH11', -0.558, (212.507, 182.343, 178.071)), (' B  14  GLN  HB2', ' J  95A THR  HB ', -0.555, (164.731, 242.631, 165.528)), (' A  44  ARG  O  ', ' A 283  GLY  HA2', -0.555, (222.457, 179.697, 204.711)), (' K  24  SER  HB2', ' K  69  THR HG22', -0.554, (266.499, 258.409, 164.455)), (' G  95  ASP  OD1', ' G 100C SER  HB3', -0.554, (150.522, 251.943, 171.547)), (' J  24  SER  HB2', ' J  69  THR HG22', -0.553, (138.709, 234.627, 164.087)), (' G  34  MET  CE ', ' G  78  LEU HD22', -0.553, (152.522, 262.242, 167.531)), (' I  34  MET  CE ', ' I  78  LEU HD22', -0.552, (283.729, 233.0, 167.562)), (' A 720  ILE HG13', ' A 923  ILE HG23', -0.55, (214.202, 187.683, 264.837)), (' C 722  VAL HG22', ' C1065  VAL HG22', -0.55, (224.963, 224.82, 256.819)), (' A1141  LEU HD21', ' B1145  LEU HD22', -0.548, (206.924, 209.725, 299.228)), (' B  44  ARG  O  ', ' B 283  GLY  HA2', -0.547, (177.811, 213.714, 204.587)), (' H  95  ASP  OD1', ' H 100C SER  HB3', -0.547, (202.744, 137.454, 171.441)), (' A1086  LYS  HD2', ' A1122  VAL HG21', -0.546, (194.891, 213.363, 288.649)), (' A  14  GLN  HB2', ' L  95A THR  HB ', -0.546, (203.498, 153.962, 165.406)), (' L  24  SER  HB2', ' L  69  THR HG22', -0.544, (223.858, 136.186, 164.262)), (' B1086  LYS  HD2', ' B1122  VAL HG21', -0.543, (220.626, 220.493, 288.265)), (' H  34  MET  CE ', ' H  78  LEU HD22', -0.542, (192.962, 134.018, 167.468)), (' I  95  ASP  OD1', ' I 100C SER  HB3', -0.542, (275.318, 239.943, 171.453)), (' B 826  VAL  HB ', ' B1057  PRO  HG2', -0.542, (184.545, 211.329, 235.758)), (' C  44  ARG  O  ', ' C 283  GLY  HA2', -0.542, (229.403, 235.182, 204.558)), (' B 355  ARG HH11', ' C 230  PRO  HB3', -0.532, (232.149, 225.647, 178.19)), (' A 837  TYR  OH ', ' A 960  ASN  HA ', -0.53, (216.352, 190.669, 215.654)), (' B1107  ARG HH22', ' C 894  LEU  HB2', -0.529, (205.686, 228.64, 265.899)), (' A 877  LEU HD23', ' A 888  PHE  HE2', -0.527, (226.186, 201.891, 252.684)), (' B 905  ARG  NH1', ' B1049  LEU  O  ', -0.527, (196.766, 209.633, 259.872)), (' C 575  ALA  HA ', ' C 586  ASP  HA ', -0.526, (232.382, 187.912, 201.88)), (' C 458  LYS  HB3', ' O   2  NAG  H61', -0.526, (188.715, 183.815, 175.391)), (' A1049  LEU HD11', ' A1067  TYR  HB2', -0.523, (210.322, 192.959, 263.2)), (' A  69  HIS  CD2', ' A  71  SER  HB2', -0.522, (191.52, 149.896, 192.046)), (' B  69  HIS  CD2', ' B  71  SER  HB2', -0.522, (166.948, 255.397, 191.994)), (' C 179  LEU HD21', ' C 190  ARG HH12', -0.522, (253.42, 240.586, 192.416)), (' C 720  ILE HG13', ' C 923  ILE HG23', -0.521, (226.795, 224.224, 264.708)), (' B 179  LEU HD21', ' B 190  ARG HH12', -0.519, (161.123, 232.117, 192.384)), (' B 571  ASP  HB2', ' C1000  ARG HH21', -0.519, (215.143, 225.129, 203.602)), (' A 179  LEU HD21', ' A 190  ARG HH12', -0.519, (214.38, 156.309, 192.331)), (' B 100  ILE HD11', ' B 263  ALA  HB3', -0.519, (162.681, 243.23, 190.928)), (' C 826  VAL  HB ', ' C1057  PRO  HG2', -0.519, (223.352, 230.592, 236.149)), (' A 826  VAL  HB ', ' A1057  PRO  HG2', -0.518, (221.126, 187.057, 235.785)), (' C  14  GLN  HB2', ' K  95A THR  HB ', -0.518, (260.918, 232.223, 165.442)), (' A 905  ARG  NH1', ' A1049  LEU  O  ', -0.517, (216.292, 198.468, 259.863)), (' C 100  ILE HD11', ' C 263  ALA  HB3', -0.517, (262.246, 233.505, 191.425)), (' A 156  GLU  OE2', ' L  93  ASN  HB3', -0.516, (209.594, 148.938, 170.16)), (' A 376  THR  HB ', ' A 435  ALA  HB3', -0.515, (200.265, 210.752, 169.172)), (' A 715  PRO  HA ', ' A1072  GLU  HA ', -0.515, (198.316, 189.45, 269.046)), (' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.514, (209.393, 198.228, 248.811)), (' A 841  LEU HD13', ' A 956  ALA  HB2', -0.514, (218.379, 189.692, 223.183)), (' C  69  HIS  CD2', ' C  71  SER  HB2', -0.513, (271.268, 223.84, 192.033)), (' A 739  THR HG21', ' C 317  ASN  HB3', -0.513, (232.643, 206.383, 207.846)), (' A 458  LYS  HB3', ' W   2  NAG  H61', -0.512, (197.432, 240.938, 175.73)), (' C 156  GLU  OE2', ' K  93  ASN  HB3', -0.511, (262.641, 239.844, 170.33)), (' A 722  VAL HG22', ' A1065  VAL HG22', -0.511, (215.674, 188.691, 256.955)), (' J  47  VAL HG12', ' J  48  ILE HG12', -0.509, (133.924, 250.166, 171.478)), (' B 156  GLU  OE2', ' J  93  ASN  HB3', -0.509, (156.592, 240.148, 170.151)), (' A1139  ASP  N  ', ' A1139  ASP  OD1', -0.508, (200.732, 204.109, 294.106)), (' C 553  THR  OG1', ' C 586  ASP  OD1', -0.507, (236.31, 188.383, 206.08)), (' A 384  PRO  HB2', ' C 415  THR HG22', -0.507, (197.826, 201.15, 177.183)), (' A 100  ILE HD11', ' A 263  ALA  HB3', -0.505, (204.531, 152.016, 191.405)), (' B 722  VAL HG22', ' B1065  VAL HG22', -0.505, (189.23, 214.962, 256.987)), (' B 945  LEU HD23', ' B 948  LEU HD12', -0.503, (187.261, 213.653, 238.819)), (' L  47  VAL HG12', ' L  48  ILE HG12', -0.502, (212.464, 123.944, 171.498)), (' K  47  VAL HG12', ' K  48  ILE HG12', -0.502, (282.623, 255.02, 171.509)), (' C 945  LEU HD23', ' C 948  LEU HD12', -0.501, (224.325, 227.309, 238.805)), (' C 250  THR  OG1', ' I  95  ASP  HB3', -0.5, (277.561, 236.096, 174.043)), (' B 317  ASN  HB3', ' C 739  THR HG21', -0.497, (200.846, 231.539, 208.024)), (' B 338  PHE  HB3', ' B 368  LEU HD21', -0.496, (216.424, 231.535, 168.372)), (' C 715  PRO  HA ', ' C1072  GLU  HA ', -0.496, (233.153, 210.17, 269.013)), (' A1107  ARG HH22', ' B 894  LEU  HB2', -0.495, (195.539, 196.865, 265.861)), (' J   6  GLN  NE2', ' J  86  TYR  O  ', -0.495, (136.307, 247.683, 160.769)), (' A 843  ASP  O  ', ' A 843  ASP  OD1', -0.494, (226.268, 191.751, 229.43)), (' B 250  THR  HB ', ' G  97  GLY  O  ', -0.492, (152.448, 253.145, 176.732)), (' A 553  THR  OG1', ' A 586  ASP  OD1', -0.492, (177.924, 197.244, 205.994)), (' B 715  PRO  HA ', ' B1072  GLU  HA ', -0.491, (197.631, 230.162, 268.95)), (' A 563  GLN  O  ', ' A 577  ARG  NH2', -0.489, (175.123, 209.054, 194.458)), (' A 894  LEU  HB2', ' C1107  ARG HH22', -0.488, (228.08, 203.915, 265.94)), (' A 497  PHE  CG ', ' A 507  PRO  HG3', -0.488, (199.033, 217.997, 156.767)), (' A 317  ASN  HB3', ' B 739  THR HG21', -0.487, (195.449, 191.188, 208.14)), (' B 663  ASP  N  ', ' B 663  ASP  OD1', -0.485, (193.995, 231.51, 235.757)), (' A 611  LEU HD22', ' A 666  ILE HG23', -0.485, (192.013, 188.86, 226.989)), (' C 409  GLN  HA ', ' C 414  GLN  HG2', -0.483, (203.489, 200.179, 174.077)), (' H  34  MET  HE2', ' H  78  LEU HD22', -0.48, (192.071, 133.834, 167.666)), (' A 945  LEU HD23', ' A 948  LEU HD12', -0.48, (217.366, 188.641, 238.639)), (' B 458  LYS  HB3', ' e   2  NAG  H61', -0.48, (242.522, 204.415, 175.463)), (' B 856  ASN HD22', ' B 966  LEU HD13', -0.479, (193.92, 206.205, 209.189)), (' A1074  ASN  OD1', ' B 895  GLN  NE2', -0.479, (189.822, 190.867, 268.982)), (' A 550  GLY  HA2', ' A 590  CYS  HB2', -0.479, (187.651, 192.297, 202.797)), (' C 418  ILE  HA ', ' C 422  ASN  HB2', -0.478, (201.461, 191.872, 169.616)), (' C 663  ASP  N  ', ' C 663  ASP  OD1', -0.478, (235.987, 212.314, 235.798)), (' K   6  GLN  NE2', ' K  86  TYR  O  ', -0.478, (279.32, 254.502, 160.832)), (' A 338  PHE  HB3', ' A 368  LEU HD21', -0.477, (187.072, 204.724, 168.481)), (' A 663  ASP  N  ', ' A 663  ASP  OD1', -0.477, (198.729, 185.679, 235.809)), (' C 550  GLY  HA2', ' C 590  CYS  HB2', -0.475, (236.041, 199.742, 203.096)), (' G  34  MET  HE2', ' G  78  LEU HD22', -0.474, (152.803, 262.848, 167.764)), (' L   6  GLN  NE2', ' L  86  TYR  O  ', -0.474, (213.638, 127.138, 160.822)), (' B 497  PHE  CG ', ' B 507  PRO  HG3', -0.473, (222.725, 215.064, 156.49)), (' I  34  MET  HE2', ' I  78  LEU HD22', -0.473, (284.037, 232.122, 167.416)), (' A 409  GLN  HA ', ' A 414  GLN  HG2', -0.472, (204.608, 219.713, 174.544)), (' L  66  SER  HB2', ' L  71  VAL HG12', -0.472, (220.048, 132.847, 170.933)), (' A1082  CYS  HB2', ' A1126  CYS  HB2', -0.469, (187.644, 209.252, 285.068)), (' I   2  VAL  O  ', ' I   2  VAL HG23', -0.469, (289.992, 238.796, 173.019)), (' B 439  ASN  O  ', ' B 443  SER  OG ', -0.468, (218.537, 217.698, 153.302)), (' H   2  VAL  O  ', ' H   2  VAL HG23', -0.468, (195.031, 125.508, 172.963)), (' A 439  ASN  O  ', ' A 443  SER  OG ', -0.467, (198.169, 213.897, 153.316)), (' B1074  ASN  OD1', ' C 895  GLN  NE2', -0.465, (203.716, 236.424, 268.715)), (' G   2  VAL  O  ', ' G   2  VAL HG23', -0.465, (144.349, 264.581, 172.881)), (' B 128  ILE  HB ', ' B 170  TYR  HB3', -0.464, (173.256, 225.544, 178.231)), (' B 709  ASN  HB3', ' C 796  ASP  HB3', -0.464, (217.046, 237.522, 269.389)), (' A 355  ARG HH11', ' B 230  PRO  HB3', -0.464, (184.329, 220.764, 178.525)), (' K  66  SER  HB2', ' K  71  VAL HG12', -0.462, (271.175, 257.178, 170.921)), (' B 376  THR  HB ', ' B 435  ALA  HB3', -0.462, (215.773, 217.647, 169.029)), (' B 409  GLN  HA ', ' B 414  GLN  HG2', -0.462, (221.237, 208.835, 174.467)), (' A 627  ASP  O  ', ' A 634  ARG  NH2', -0.461, (185.915, 177.572, 205.401)), (' A 571  ASP  HB2', ' B1000  ARG HH21', -0.461, (193.745, 206.787, 203.81)), (' C 193  VAL HG13', ' C 270  LEU HD11', -0.461, (242.56, 223.414, 193.459)), (' B 598  ILE HG23', ' B 664  ILE HG21', -0.46, (193.981, 232.29, 228.1)), (' C 439  ASN  O  ', ' C 443  SER  OG ', -0.459, (211.864, 197.722, 153.228)), (' A 415  THR HG22', ' B 384  PRO  HB2', -0.459, (208.199, 224.416, 177.226)), (' A  80  ASP  C  ', ' A  82  PRO  HD3', -0.459, (195.71, 158.306, 186.985)), (' C 376  THR  HB ', ' C 435  ALA  HB3', -0.459, (213.602, 200.95, 169.247)), (' B 802  PHE  HD1', ' B 805  ILE HD11', -0.457, (184.919, 208.527, 256.632)), (' C 497  PHE  CG ', ' C 507  PRO  HG3', -0.457, (207.775, 195.942, 156.466)), (' C  80  ASP  C  ', ' C  82  PRO  HD3', -0.455, (261.26, 223.887, 186.879)), (' A 575  ALA  HA ', ' A 586  ASP  HA ', -0.454, (179.516, 201.189, 202.178)), (' C 324  GLU  HG3', ' C 539  VAL HG23', -0.454, (242.363, 199.999, 196.073)), (' C1086  LYS  HD2', ' C1122  VAL HG11', -0.454, (213.324, 195.17, 288.271)), (' J  66  SER  HB2', ' J  71  VAL HG12', -0.452, (137.658, 239.221, 171.334)), (' C 837  TYR  HB2', ' C 841  LEU HD23', -0.451, (222.254, 231.132, 219.692)), (' C  66  HIS  HD2', ' C  69  HIS  ND1', -0.451, (267.083, 225.119, 193.462)), (' B 553  THR  OG1', ' B 586  ASP  OD1', -0.451, (214.91, 243.425, 206.048)), (' B 977  LEU HD23', ' B 996  LEU HD23', -0.45, (196.985, 205.103, 199.872)), (' J  11  VAL HG21', ' J  21  ILE HD11', -0.45, (128.367, 246.368, 161.353)), (' A  66  HIS  HD2', ' A  69  HIS  ND1', -0.45, (194.427, 152.124, 193.467)), (' B  80  ASP  C  ', ' B  82  PRO  HD3', -0.45, (171.716, 247.387, 186.858)), (' K  11  VAL HG21', ' K  21  ILE HD11', -0.45, (282.087, 261.873, 161.328)), (' C 128  ILE  HB ', ' C 170  TYR  HB3', -0.449, (241.698, 233.541, 178.168)), (' A 128  ILE  HB ', ' A 170  TYR  HB3', -0.449, (214.555, 170.555, 178.062)), (' A 802  PHE  HD1', ' A 805  ILE HD11', -0.449, (223.108, 188.782, 256.661)), (' B 571  ASP  N  ', ' B 571  ASP  OD1', -0.449, (218.132, 226.955, 205.165)), (' H  34  MET  HE3', ' H  78  LEU HD22', -0.449, (193.118, 134.232, 167.477)), (' A 739  THR HG23', ' A 753  LEU HD11', -0.448, (230.611, 207.893, 207.252)), (' B  66  HIS  HD2', ' B  69  HIS  ND1', -0.448, (167.482, 251.801, 193.539)), (' C 905  ARG  NH1', ' C1049  LEU  O  ', -0.448, (216.087, 221.085, 259.971)), (' B 193  VAL HG13', ' B 270  LEU HD11', -0.447, (181.891, 231.385, 193.362)), (' L  11  VAL HG21', ' L  21  ILE HD11', -0.446, (218.721, 120.754, 160.908)), (' C 736  VAL HG11', ' C1004  LEU HD21', -0.446, (207.814, 221.99, 215.248)), (' B 611  LEU HD22', ' B 666  ILE HG23', -0.446, (200.539, 235.556, 226.445)), (' A 193  VAL HG13', ' A 270  LEU HD11', -0.445, (204.812, 174.722, 193.394)), (' I  34  MET  HE3', ' I  78  LEU HD22', -0.445, (283.394, 233.166, 167.336)), (' B 906  PHE  CD2', ' B 916  LEU  HB2', -0.445, (193.133, 214.172, 269.8)), (' H 100C SER  HB2', ' L  96  TRP  HE1', -0.444, (204.937, 138.917, 170.49)), (' B 120  VAL HG21', ' B 157  PHE  CE2', -0.444, (166.148, 234.501, 176.855)), (' C 598  ILE HG23', ' C 664  ILE HG21', -0.443, (236.664, 212.111, 228.256)), (' C 726  ILE HG12', ' C1061  VAL HG22', -0.443, (223.526, 224.99, 243.179)), (' B 353  TRP  O  ', ' B 466  ARG  NH1', -0.442, (233.359, 223.336, 170.339)), (' A 598  ILE HG23', ' A 664  ILE HG21', -0.442, (198.076, 184.975, 228.006)), (' I 100C SER  HB2', ' K  96  TRP  HE1', -0.442, (273.308, 241.038, 170.072)), (' B 866  THR HG22', ' B 868  GLU  H  ', -0.442, (184.483, 197.685, 238.168)), (' C 120  VAL HG21', ' C 157  PHE  CE2', -0.442, (252.947, 234.915, 176.762)), (' A 837  TYR  HB2', ' A 841  LEU HD23', -0.441, (221.508, 187.778, 220.064)), (' A 324  GLU  HG3', ' A 539  VAL HG23', -0.441, (184.687, 186.684, 196.1)), (' B 324  GLU  HG3', ' B 539  VAL HG23', -0.44, (201.895, 243.024, 196.084)), (' G  34  MET  HE3', ' G  78  LEU HD22', -0.44, (152.715, 261.754, 167.509)), (' A 545  GLY  O  ', ' B 982  SER  OG ', -0.439, (189.474, 201.013, 189.616)), (' B 740  MET  HE1', ' B 853  GLN  HA ', -0.438, (188.543, 200.472, 210.208)), (' C 906  PHE  CD2', ' C 916  LEU  HB2', -0.438, (221.902, 222.274, 269.946)), (' A 120  VAL HG21', ' A 157  PHE  CE2', -0.438, (210.126, 159.751, 176.853)), (' B1139  ASP  N  ', ' B1139  ASP  OD1', -0.438, (209.097, 220.214, 294.247)), (' I  12  VAL HG11', ' I  82C LEU HD12', -0.437, (284.183, 229.602, 148.218)), (' B 733  LYS  HE3', ' B 771  ALA  HB1', -0.437, (196.86, 199.178, 228.079)), (' B 303  LEU HD12', ' B 308  VAL HG12', -0.437, (190.46, 224.707, 219.4)), (' B  80  ASP  O  ', ' B  82  PRO  HD3', -0.435, (171.641, 246.976, 187.345)), (' G  12  VAL HG11', ' G  82C LEU HD12', -0.434, (155.582, 264.007, 148.378)), (' A  80  ASP  O  ', ' A  82  PRO  HD3', -0.434, (196.273, 158.482, 187.337)), (' I  34  MET  HB3', ' I  34  MET  HE3', -0.433, (282.312, 233.364, 167.993)), (' H  40  ALA  HB3', ' H  43  LYS  HB3', -0.433, (204.719, 131.164, 151.209)), (' A 726  ILE HG12', ' A1061  VAL HG22', -0.433, (216.034, 190.086, 243.235)), (' G 100C SER  HB2', ' J  96  TRP  HE1', -0.432, (150.701, 249.437, 170.524)), (' A 906  PHE  CD2', ' A 916  LEU  HB2', -0.432, (214.478, 193.115, 270.071)), (' H  12  VAL HG11', ' H  82C LEU HD12', -0.432, (189.764, 135.334, 148.142)), (' G  40  ALA  HB3', ' G  43  LYS  HB3', -0.431, (143.857, 253.065, 151.266)), (' C 802  PHE  HD1', ' C 805  ILE HD11', -0.43, (221.134, 231.694, 256.158)), (' B1009  THR  HA ', ' B1012  LEU  HG ', -0.43, (206.159, 209.317, 221.867)), (' A 895  GLN  NE2', ' C1074  ASN  OD1', -0.43, (235.72, 201.498, 268.876)), (' C 252  GLY  HA3', ' C 256  SER  OG ', -0.428, (275.803, 236.923, 183.518)), (' B 294  ASP  HB3', ' B 632  THR HG21', -0.428, (186.425, 238.392, 213.769)), (' A 866  THR HG22', ' A 868  GLU  H  ', -0.428, (232.715, 194.172, 237.722)), (' B 877  LEU HD23', ' B 888  PHE  HE2', -0.428, (194.737, 199.73, 252.543)), (' A 303  LEU HD12', ' A 308  VAL HG12', -0.427, (206.257, 185.545, 219.487)), (' B1029  MET  HE1', ' B1053  PRO  HB3', -0.427, (193.622, 205.83, 248.191)), (' B1049  LEU HD11', ' B1067  TYR  HB2', -0.426, (194.832, 217.457, 263.192)), (' B 837  TYR  HB2', ' B 841  LEU HD23', -0.425, (184.91, 209.861, 219.63)), (' B 252  GLY  HA3', ' B 256  SER  OG ', -0.425, (153.045, 252.933, 183.57)), (' C1049  LEU HD11', ' C1067  TYR  HB2', -0.425, (223.576, 219.023, 263.361)), (' B 770  ILE HD11', ' B1012  LEU HD23', -0.425, (204.511, 206.344, 224.081)), (' B 418  ILE  HA ', ' B 422  ASN  HB2', -0.425, (229.003, 211.205, 169.745)), (' I  40  ALA  HB3', ' I  43  LYS  HB3', -0.425, (280.251, 245.109, 151.338)), (' A 252  GLY  HA3', ' A 256  SER  OG ', -0.425, (200.221, 138.909, 183.524)), (' A 733  LYS  HE3', ' A 771  ALA  HB1', -0.424, (225.22, 203.745, 228.029)), (' C 708  SER  HB3', ' C 711  SER  HB2', -0.424, (233.878, 196.071, 270.455)), (' B 393  THR  HA ', ' B 522  ALA  HA ', -0.424, (223.233, 235.225, 185.598)), (' C  70  VAL HG11', ' C 260  ALA  HB1', -0.424, (272.07, 231.232, 193.067)), (' P   1  NAG  H2 ', ' P   1  NAG  H83', -0.423, (192.443, 150.756, 167.525)), (' C 627  ASP  O  ', ' C 634  ARG  NH2', -0.423, (249.62, 205.351, 205.784)), (' C  80  ASP  O  ', ' C  82  PRO  HD3', -0.423, (260.977, 223.642, 187.234)), (' A 708  SER  HB3', ' A 711  SER  HB2', -0.422, (185.815, 195.414, 270.378)), (' G   2  VAL  CG2', ' G   2  VAL  O  ', -0.422, (144.271, 264.531, 173.641)), (' A 418  ILE  HA ', ' A 422  ASN  HB2', -0.422, (198.769, 225.719, 169.768)), (' C 105  ILE HG23', ' C 241  LEU HD11', -0.422, (253.109, 227.612, 179.33)), (' B 829  ALA  H  ', ' B 952  VAL HG11', -0.422, (185.761, 211.768, 228.307)), (' A 206  LYS  CB ', ' A 223  LEU HD23', -0.421, (213.277, 168.224, 197.796)), (' I   2  VAL  CG2', ' I   2  VAL  O  ', -0.421, (289.964, 239.028, 173.677)), (' A  70  VAL HG11', ' A 260  ALA  HB1', -0.421, (196.758, 144.865, 192.983)), (' B1105  THR HG22', ' B1112  PRO  HA ', -0.42, (201.303, 225.103, 279.786)), (' G  34  MET  HB3', ' G  34  MET  HE3', -0.42, (153.003, 260.847, 167.995)), (' C 206  LYS  CB ', ' C 223  LEU HD23', -0.42, (243.849, 233.122, 197.74)), (' H  43  LYS  HG2', ' H  44  GLY  H  ', -0.418, (208.129, 130.822, 153.15)), (' H   2  VAL  CG2', ' H   2  VAL  O  ', -0.418, (194.902, 125.634, 173.664)), (' B 105  ILE HG23', ' B 241  LEU HD11', -0.418, (172.565, 238.402, 179.342)), (' B 206  LYS  CB ', ' B 223  LEU HD23', -0.417, (171.988, 227.458, 197.81)), (' A 703  ASN  HB3', ' B 789  TYR  HE1', -0.416, (191.38, 190.589, 256.76)), (' G  43  LYS  HG2', ' G  44  GLY  H  ', -0.414, (142.449, 250.483, 152.898)), (' A 105  ILE HG23', ' A 241  LEU HD11', -0.414, (203.438, 163.597, 179.17)), (' C  54  LEU HD12', ' C 197  ILE HD11', -0.413, (237.275, 218.719, 191.702)), (' H  22  CYS  HB3', ' H  78  LEU  HB3', -0.412, (189.811, 133.154, 165.085)), (' A 722  VAL  HA ', ' A1064  HIS  O  ', -0.412, (212.965, 189.439, 255.322)), (' H  35  HIS  CE1', ' H  50  VAL HG22', -0.412, (200.024, 140.447, 166.804)), (' C 303  LEU HD12', ' C 308  VAL HG12', -0.412, (232.413, 218.795, 219.637)), (' C 466  ARG  HG2', ' C 468  ILE HG23', -0.411, (204.263, 181.169, 170.113)), (' J  61  ARG  H  ', ' J  61  ARG  HG3', -0.41, (125.13, 254.12, 174.064)), (' C 401  VAL HG22', ' C 509  ARG  HG2', -0.41, (212.991, 193.018, 162.058)), (' I  43  LYS  HG2', ' I  44  GLY  H  ', -0.41, (278.765, 247.809, 153.226)), (' K  25  ALA  HB3', ' K  28  LEU  HG ', -0.409, (267.966, 253.062, 164.947)), (' G  35  HIS  CE1', ' G  50  VAL HG22', -0.409, (154.53, 252.848, 166.784)), (' B 708  SER  HB3', ' B 711  SER  HB2', -0.408, (209.626, 237.966, 270.433)), (' L  25  ALA  HB3', ' L  28  LEU  HG ', -0.408, (218.093, 137.601, 164.902)), (' A 961  THR  O  ', ' A 965  GLN  HG3', -0.407, (212.216, 196.109, 212.671)), (' B 415  THR HG22', ' C 384  PRO  HB2', -0.407, (223.176, 203.74, 177.223)), (' J  25  ALA  HB3', ' J  28  LEU  HG ', -0.406, (143.181, 238.523, 164.989)), (' K   7  PRO  HA ', ' K   8  PRO  HD2', -0.405, (275.111, 259.528, 155.123)), (' B  70  VAL HG11', ' B 260  ALA  HB1', -0.404, (160.015, 253.31, 192.832)), (' I  35  HIS  CE1', ' I  50  VAL HG22', -0.404, (274.604, 236.037, 166.718)), (' C 312  ILE HG13', ' C 598  ILE HG13', -0.404, (236.073, 209.582, 225.331)), (' C 100  ILE HD11', ' C 263  ALA  CB ', -0.403, (261.757, 233.937, 191.125)), (' C 961  THR  O  ', ' C 965  GLN  HG3', -0.403, (220.291, 219.027, 212.924)), (' B  54  LEU HD12', ' B 197  ILE HD11', -0.402, (188.199, 229.045, 191.748)), (' C 722  VAL  HA ', ' C1064  HIS  O  ', -0.402, (225.707, 222.628, 255.352)), (' B1028  LYS  NZ ', ' B1042  PHE  O  ', -0.402, (199.62, 216.109, 248.914)), (' C 393  THR  HA ', ' C 522  ALA  HA ', -0.401, (225.437, 185.167, 185.714)), (' I   7  SER  OG ', ' I   8  GLY  N  ', -0.401, (293.052, 229.598, 157.937)), (' B  78  ARG  NH1', ' B  79  PHE  O  ', -0.401, (169.163, 250.508, 183.766)), (' C 992  GLN  H  ', ' C 992  GLN  HG2', -0.4, (209.563, 217.308, 193.109))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

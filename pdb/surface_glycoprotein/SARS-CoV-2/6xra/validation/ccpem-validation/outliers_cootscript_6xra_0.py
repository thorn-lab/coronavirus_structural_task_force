
from __future__ import division
import cPickle
try :
  import gobject
except ImportError :
  gobject = None
import sys

dict_residue_prop_objects = {}
class coot_extension_gui (object) :
  def __init__ (self, title) :
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

  def finish_window (self) :
    import gtk
    self.outside_vbox.set_border_width(2)
    ok_button = gtk.Button("  Close  ")
    self.outside_vbox.pack_end(ok_button, False, False, 0)
    ok_button.connect("clicked", lambda b: self.destroy_window())
    self.window.connect("delete_event", lambda a, b: self.destroy_window())
    self.window.show_all()

  def destroy_window (self, *args) :
    self.window.destroy()
    self.window = None

  def confirm_data (self, data) :
    for data_key in self.data_keys :
      outlier_list = data.get(data_key)
      if outlier_list is not None and len(outlier_list) > 0 :
        return True
    return False

  def create_property_lists (self, data) :
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
        ##save property list frame object
        dict_residue_prop_objects[data_key] = list_obj
# Molprobity result viewer
class coot_molprobity_todo_list_gui (coot_extension_gui) :
  data_keys = [ "clusters","rama", "rota", "cbeta", "probe", "smoc", "cablam",
               "jpred"]
  data_titles = { "clusters"  : "Outlier residue clusters",
                  "rama"  : "Ramachandran outliers",
                  "rota"  : "Rotamer outliers",
                  "cbeta" : "C-beta outliers",
                  "probe" : "Severe clashes",
                  "smoc"  : "Local density fit (SMOC)",
                  "cablam": "Ca geometry (CaBLAM)",
                  "jpred":"SS prediction"}
  data_names = { "clusters"  : ["Chain","Residue","Cluster","Outlier types"],
                 "rama"  : ["Chain", "Residue", "Name", "Score"],
                 "rota"  : ["Chain", "Residue", "Name", "Score"],
                 "cbeta" : ["Chain", "Residue", "Name", "Conf.", "Deviation"],
                 "probe" : ["Atom 1", "Atom 2", "Overlap"],
                 "smoc" : ["Chain", "Residue", "Name", "Score"],
                 "cablam" : ["Chain", "Residue","Name","recommendation","DSSP"],
                 "jpred" : ["Chain", "Residue","Name","predicted SS","current SS"]}
  if (gobject is not None) :
    data_types = {  "clusters" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_INT, gobject.TYPE_STRING,
                             gobject.TYPE_PYOBJECT],
                    "rama" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "rota" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cbeta" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "probe" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "smoc" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cablam" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT],
                   "jpred" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT]}
  else :
    data_types = dict([ (s, []) for s in ["clusters","rama","rota","cbeta","probe","smoc",
                                          "cablam","jpred"] ])

  def __init__ (self, data_file=None, data=None) :
    assert ([data, data_file].count(None) == 1)
    if (data is None) :
      data = load_pkl(data_file)
    if not self.confirm_data(data) :
      return
    coot_extension_gui.__init__(self, "MolProbity to-do list")
    self.dots_btn = None
    self.dots2_btn = None
    self._overlaps_only = True
    self.window.set_default_size(420, 600)
    self.create_property_lists(data)
    self.finish_window()

  def add_top_widgets (self, data_key, box) :
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

  def toggle_probe_dots (self, *args) :
    if self.dots_btn is not None :
      show_dots = self.dots_btn.get_active()
      overlaps_only = self.dots2_btn.get_active()
      if show_dots :
        self.dots2_btn.set_sensitive(True)
      else :
        self.dots2_btn.set_sensitive(False)
      show_probe_dots(show_dots, overlaps_only)

  def toggle_all_probe_dots (self, *args) :
    if self.dots2_btn is not None :
      self._overlaps_only = self.dots2_btn.get_active()
      self.toggle_probe_dots()

class rsc_todo_list_gui (coot_extension_gui) :
  data_keys = ["by_res", "by_atom"]
  data_titles = ["Real-space correlation by residue",
                 "Real-space correlation by atom"]
  data_names = {}
  data_types = {}

class residue_properties_list (object) :
  def __init__ (self, columns, column_types, rows, box,
      default_size=(380,200)) :
    assert len(columns) == (len(column_types) - 1)
    if (len(rows) > 0) and (len(rows[0]) != len(column_types)) :
      raise RuntimeError("Wrong number of rows:\n%s" % str(rows[0]))
    import gtk
    ##adding a column type for checkbox (bool) before atom coordinate
    if gobject is not None:
        column_types = column_types[:-1]+[bool]+[column_types[-1]]
    
    self.liststore = gtk.ListStore(*column_types)
    self.listmodel = gtk.TreeModelSort(self.liststore)
    self.listctrl = gtk.TreeView(self.listmodel)
    self.listctrl.column = [None]*len(columns)
    self.listctrl.cell = [None]*len(columns)
    for i, column_label in enumerate(columns) :
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn(column_label)
      self.listctrl.append_column(column)
      column.set_sort_column_id(i)
      column.pack_start(cell, True)
      column.set_attributes(cell, text=i)
    ##add a cell for checkbox
    cell1 = gtk.CellRendererToggle()
    cell1.connect ("toggled", self.on_selected_toggled)
    column = gtk.TreeViewColumn('Dealt with',cell1,active=i+1)
    self.listctrl.append_column(column)
    #column.set_sort_column_id(i+1)
    #column.pack_start(cell1, True)
    
    self.listctrl.get_selection().set_mode(gtk.SELECTION_SINGLE)
    for row in rows :
      row = row[:-1] + (False,)+(row[-1],)
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

  def OnChange (self, treeview) :
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
  ##check box toggle
  def on_selected_toggled(self,renderer,path):
    if path is not None:
      model = self.listmodel.get_model()
      it = model.get_iter(path)
      #set toggle
      model[it][-2] = not model[it][-2]
      #set checkboxes for same residues in other lists
      try:
        chain = model[it][0]
        residue = model[it][1]
        for data_key in dict_residue_prop_objects:
          prop_obj = dict_residue_prop_objects[data_key]
          for row in prop_obj.listmodel.get_model():
            if data_key == 'probe':
              atom1_split = row[0].split()
              atom2_split = row[1].split()
              if atom1_split[0] == chain and atom1_split[1] == residue:
                row[-2] = model[it][-2]
              elif atom2_split[0] == chain and atom2_split[1] == residue:
                row[-2] = model[it][-2]
            elif row[0] == chain and row[1] == residue:
              row[-2] = model[it][-2]
      except IndexError: pass

  def check_chain_residue(self,chain,residue):
      pass
  
def show_probe_dots (show_dots, overlaps_only) :
  import coot # import dependency
  n_objects = number_of_generic_objects()
  sys.stdout.flush()
  if show_dots :
    for object_number in range(n_objects) :
      obj_name = generic_object_name(object_number)
      if overlaps_only and not obj_name in ["small overlap", "bad overlap"] :
        sys.stdout.flush()
        set_display_generic_object(object_number, 0)
      else :
        set_display_generic_object(object_number, 1)
  else :
    sys.stdout.flush()
    for object_number in range(n_objects) :
      set_display_generic_object(object_number, 0)

def load_pkl (file_name) :
  pkl = open(file_name, "rb")
  data = cPickle.load(pkl)
  pkl.close()
  return data
data = {}
data['rama'] = []
data['jpred'] = []
data['probe'] = [(' A1173  ASN HD21', ' A1417  NAG  C1 ', -1.092, (203.053, 182.576, 150.327)), (' B1173  ASN HD21', ' B1417  NAG  C1 ', -1.085, (208.896, 210.038, 150.392)), (' C1173  ASN HD21', ' C1417  NAG  C1 ', -1.079, (182.133, 201.224, 150.586)), (' A1098  ASN HD21', ' J   1  NAG  C1 ', -0.988, (211.08, 177.591, 280.978)), (' C1098  ASN HD21', ' E   1  NAG  C1 ', -0.987, (174.301, 196.46, 281.029)), (' B1098  ASN HD21', ' O   1  NAG  C1 ', -0.984, (208.445, 219.279, 281.083)), (' C1173  ASN  ND2', ' C1417  NAG  C1 ', -0.947, (183.456, 202.436, 150.919)), (' B1173  ASN  ND2', ' B1417  NAG  C1 ', -0.93, (208.596, 208.821, 150.807)), (' A1173  ASN  ND2', ' A1417  NAG  C1 ', -0.917, (202.051, 183.33, 150.672)), (' C1173  ASN  OD1', ' C1417  NAG  C1 ', -0.906, (182.899, 202.707, 151.143)), (' A1098  ASN  ND2', ' J   1  NAG  C1 ', -0.9, (210.57, 178.484, 280.452)), (' B1098  ASN  ND2', ' O   1  NAG  C1 ', -0.899, (208.637, 218.596, 280.439)), (' C1098  ASN  ND2', ' E   1  NAG  C1 ', -0.893, (174.512, 196.862, 280.458)), (' B1173  ASN  OD1', ' B1417  NAG  C1 ', -0.833, (210.448, 208.529, 151.794)), (' A1173  ASN  OD1', ' A1417  NAG  C1 ', -0.807, (201.036, 182.32, 151.628)), (' A 709  ASN  CB ', ' A1077  THR  O  ', -0.793, (205.149, 174.545, 267.102)), (' C 709  ASN  CB ', ' C1077  THR  O  ', -0.788, (174.859, 204.179, 267.051)), (' B 709  ASN  CB ', ' B1077  THR  O  ', -0.784, (214.855, 215.066, 267.022)), (' B1040  VAL HG22', ' B1047  TYR  CE2', -0.756, (196.66, 208.415, 262.108)), (' C1173  ASN  CG ', ' C1417  NAG  C1 ', -0.747, (183.436, 202.669, 151.18)), (' A1040  VAL HG22', ' A1047  TYR  CE2', -0.745, (207.945, 193.722, 262.526)), (' B 709  ASN  HB2', ' B1077  THR  O  ', -0.744, (214.262, 215.686, 267.241)), (' C1040  VAL HG22', ' C1047  TYR  CE2', -0.742, (189.596, 191.332, 262.49)), (' C 709  ASN  HB2', ' C1077  THR  O  ', -0.74, (174.599, 203.268, 267.253)), (' A 709  ASN  HB2', ' A1077  THR  O  ', -0.736, (205.031, 175.139, 267.334)), (' B1173  ASN  CG ', ' B1417  NAG  C1 ', -0.691, (209.576, 208.292, 151.289)), (' A1173  ASN  CG ', ' A1417  NAG  C1 ', -0.683, (201.484, 183.095, 151.156)), (' C1173  ASN HD21', ' C1417  NAG  C2 ', -0.669, (182.388, 201.75, 150.138)), (' B1173  ASN HD21', ' B1417  NAG  C2 ', -0.637, (209.276, 209.194, 150.131)), (' A1173  ASN HD21', ' A1417  NAG  C2 ', -0.635, (202.62, 182.57, 150.103)), (' A1091  ARG  HD3', ' A1121  PHE  CZ ', -0.632, (191.456, 188.797, 272.241)), (' B1091  ARG  HD3', ' B1121  PHE  CZ ', -0.631, (209.124, 196.909, 272.24)), (' C1091  ARG  HD3', ' C1121  PHE  CZ ', -0.617, (193.246, 207.998, 272.563)), (' A 743  CYS  SG ', ' A 746  SER  O  ', -0.614, (210.509, 207.401, 204.267)), (' C 743  CYS  SG ', ' C 746  SER  O  ', -0.613, (200.329, 182.337, 203.948)), (' C1091  ARG  CZ ', ' C1121  PHE  CE2', -0.613, (193.755, 209.427, 274.16)), (' B 743  CYS  SG ', ' B 746  SER  O  ', -0.609, (183.597, 203.758, 204.299)), (' B1091  ARG  CZ ', ' B1121  PHE  CE2', -0.603, (210.234, 196.035, 273.75)), (' A1091  ARG  CZ ', ' A1121  PHE  CE2', -0.603, (190.188, 188.343, 273.742)), (' A 709  ASN  HB3', ' A1077  THR  O  ', -0.505, (204.142, 174.461, 267.865)), (' A 749  CYS  HB2', ' A 997  ILE HD11', -0.499, (206.374, 204.586, 203.827)), (' B 749  CYS  HB2', ' B 997  ILE HD11', -0.498, (187.772, 202.202, 203.874)), (' C1173  ASN HD21', ' C1417  NAG  H2 ', -0.498, (182.481, 201.503, 149.938)), (' B 709  ASN  HB3', ' B1077  THR  O  ', -0.497, (215.353, 214.883, 267.906)), (' C 709  ASN  HB3', ' C1077  THR  O  ', -0.493, (174.73, 204.633, 267.945)), (' C 749  CYS  HB2', ' C 997  ILE HD11', -0.49, (199.857, 186.99, 204.049)), (' A 752  LEU HD22', ' B 995  ARG  NE ', -0.488, (200.921, 204.813, 200.338)), (' A 980  ILE HD12', ' B 980  ILE HG22', -0.485, (196.547, 200.088, 181.822)), (' B1080  ALA  HB2', ' B1089  PHE  HB3', -0.483, (215.327, 204.518, 268.66)), (' B1091  ARG  NH2', ' B1121  PHE  CE2', -0.476, (209.976, 195.559, 273.622)), (' C1091  ARG  NH2', ' C1121  PHE  CE2', -0.475, (194.221, 209.757, 273.613)), (' A1080  ALA  HB2', ' A1089  PHE  HB3', -0.473, (195.142, 179.45, 268.425)), (' B 752  LEU HD22', ' C 995  ARG  NE ', -0.472, (190.545, 196.988, 200.315)), (' A1091  ARG  NH2', ' A1121  PHE  CE2', -0.471, (189.753, 188.823, 274.254)), (' B 980  ILE HD12', ' C 980  ILE HG22', -0.468, (196.986, 195.403, 182.029)), (' A 995  ARG  NE ', ' C 752  LEU HD22', -0.467, (202.534, 191.631, 200.224)), (' B1098  ASN HD21', ' O   1  NAG  C2 ', -0.464, (209.229, 219.54, 281.898)), (' C1080  ALA  HB2', ' C1089  PHE  HB3', -0.464, (183.294, 209.774, 268.441)), (' A 980  ILE HG22', ' C 980  ILE HD12', -0.458, (200.478, 198.665, 181.771)), (' A 756  TYR  CE2', ' B 995  ARG  HG2', -0.456, (199.851, 204.478, 204.209)), (' C1098  ASN HD21', ' E   1  NAG  C2 ', -0.448, (173.734, 196.986, 281.856)), (' C1082  CYS  HA ', ' C1086  LYS  O  ', -0.443, (179.691, 215.41, 272.535)), (' B1082  CYS  HA ', ' B1086  LYS  O  ', -0.44, (222.155, 205.285, 272.647)), (' A 995  ARG  HG2', ' C 756  TYR  CE2', -0.438, (203.054, 193.055, 204.416)), (' A1082  CYS  HA ', ' A1086  LYS  O  ', -0.436, (192.144, 173.553, 272.588)), (' B 756  TYR  CE2', ' C 995  ARG  HG2', -0.433, (191.33, 196.255, 204.265)), (' B 749  CYS  SG ', ' C1148  PHE  CD2', -0.423, (186.576, 205.743, 204.659)), (' B1173  ASN HD21', ' B1417  NAG  H2 ', -0.423, (208.835, 209.452, 149.809)), (' A1098  ASN HD21', ' J   1  NAG  C2 ', -0.422, (211.215, 177.512, 281.757)), (' K   1  NAG  H62', ' K   2  NAG  C7 ', -0.419, (193.984, 179.479, 236.063)), (' F   1  NAG  H62', ' F   2  NAG  C7 ', -0.419, (183.953, 210.751, 236.069)), (' A1148  PHE  CD2', ' C 749  CYS  SG ', -0.418, (196.621, 184.183, 204.646)), (' P   1  NAG  H62', ' P   2  NAG  C7 ', -0.418, (215.965, 204.017, 235.702)), (' C1172  ILE  O  ', ' C1172  ILE HG22', -0.413, (189.894, 204.381, 152.631)), (' C1126  CYS  O  ', ' C1126  CYS  SG ', -0.413, (178.226, 218.572, 267.893)), (' A1126  CYS  O  ', ' A1126  CYS  SG ', -0.412, (190.064, 170.562, 267.933)), (' B1126  CYS  O  ', ' B1126  CYS  SG ', -0.411, (225.71, 204.837, 267.978)), (' A 749  CYS  SG ', ' B1148  PHE  CD2', -0.41, (210.674, 203.708, 204.579)), (' A1172  ILE  O  ', ' A1172  ILE HG22', -0.409, (196.388, 188.086, 152.723)), (' A1173  ASN HD21', ' A1417  NAG  H2 ', -0.407, (202.873, 182.82, 149.924)), (' A1186  LEU  HB3', ' C 942  ALA  HB2', -0.403, (205.672, 197.422, 123.876))]
data['cbeta'] = [('C', ' 709 ', 'ASN', ' ', 0.46530425959939525, (173.297, 204.40600000000006, 267.683)), ('C', ' 738 ', 'CYS', ' ', 0.28724313652096445, (204.549, 187.114, 214.104)), ('C', ' 749 ', 'CYS', ' ', 0.2590900807304195, (199.234, 185.58600000000007, 203.627)), ('C', '1041 ', 'ASP', ' ', 0.352025427498206, (189.465, 189.532, 255.64299999999997)), ('C', '1043 ', 'CYS', ' ', 0.28187573289480194, (197.56, 187.438, 256.641)), ('C', '1125 ', 'ASN', ' ', 0.3084012417886703, (182.29399999999998, 223.95300000000006, 269.121)), ('A', ' 709 ', 'ASN', ' ', 0.4645996347201478, (204.839, 173.46500000000006, 267.712)), ('A', ' 738 ', 'CYS', ' ', 0.28605224924712014, (204.168, 209.11400000000006, 214.092)), ('A', ' 749 ', 'CYS', ' ', 0.2586202429418372, (208.152, 205.266, 203.62)), ('A', '1041 ', 'ASP', ' ', 0.3520493394246384, (209.622, 194.894, 255.64799999999997)), ('A', '1043 ', 'CYS', ' ', 0.2825427494199168, (207.383, 202.95100000000005, 256.636)), ('A', '1125 ', 'ASN', ' ', 0.3065594486060787, (183.414, 171.47000000000006, 269.151)), ('B', ' 709 ', 'ASN', ' ', 0.4654830817015501, (215.856, 216.26400000000007, 267.696)), ('B', ' 738 ', 'CYS', ' ', 0.28693061715357776, (185.32399999999996, 197.79900000000004, 214.093)), ('B', ' 749 ', 'CYS', ' ', 0.25765822358952684, (186.669, 203.16000000000005, 203.615)), ('B', '1041 ', 'ASP', ' ', 0.35087594487036994, (194.90699999999998, 209.683, 255.636)), ('B', '1043 ', 'CYS', ' ', 0.2831169704916575, (189.048, 203.718, 256.631)), ('B', '1125 ', 'ASN', ' ', 0.30970735259520743, (228.291, 198.70500000000013, 269.16))]
data['smoc'] = [('C', 712, u'ILE', 0.712954003568395, (176.88700000000003, 196.548, 264.42499999999995)), ('C', 725, u'GLU', 0.6699628094337825, (195.73399999999998, 181.698, 249.74099999999999)), ('C', 743, u'CYS', 0.5604850789681658, (198.972, 183.349, 208.24699999999999)), ('C', 753, u'LEU', 0.695971593302061, (204.901, 188.655, 205.92700000000002)), ('C', 763, u'LEU', 0.6649793604554786, (206.33200000000002, 192.127, 219.621)), ('C', 770, u'ILE', 0.31822679930702424, (207.472, 191.85200000000003, 231.04899999999998)), ('C', 912, u'THR', 0.7228692195174078, (194.583, 203.953, 82.574)), ('C', 923, u'ILE', 0.6768571250152936, (197.95700000000002, 202.88400000000001, 98.88199999999999)), ('C', 934, u'ILE', 0.6556969741039405, (201.54, 201.586, 114.657)), ('C', 959, u'LEU', 0.6774061684873129, (202.459, 195.52200000000002, 151.46200000000002)), ('C', 962, u'LEU', 0.6318828434962138, (203.80800000000002, 196.531, 156.01299999999998)), ('C', 984, u'LEU', 0.6739656712216537, (197.975, 193.575, 187.242)), ('C', 990, u'GLU', 0.670438149581089, (198.14499999999998, 190.87800000000001, 196.684)), ('C', 999, u'GLY', 0.6121123316999502, (193.349, 193.091, 210.08)), ('C', 1011, u'GLN', 0.6428251482318366, (199.414, 189.61499999999998, 227.33700000000002)), ('C', 1018, u'ILE', 0.5923420897702899, (201.187, 189.782, 237.67899999999997)), ('C', 1021, u'SER', 0.6221005935448304, (200.45000000000002, 190.45600000000002, 242.51399999999998)), ('C', 1062, u'PHE', 0.670496263162828, (200.184, 181.035, 252.127)), ('C', 1072, u'GLU', 0.6982257950739171, (178.73, 187.478, 266.905)), ('C', 1081, u'ILE', 0.7057486582827482, (178.626, 211.04899999999998, 271.417)), ('C', 1085, u'GLY', 0.7358600522880794, (178.077, 220.444, 273.045)), ('C', 1086, u'LYS', 0.7230669495407512, (181.353, 218.41, 273.449)), ('C', 1094, u'VAL', 0.6624003802522387, (183.737, 201.404, 269.801)), ('C', 1100, u'THR', 0.7101541593071737, (171.471, 201.797, 280.124)), ('C', 1105, u'THR', 0.6958110790015292, (184.494, 197.597, 273.671)), ('C', 1108, u'ASN', 0.6852683044436234, (187.05800000000002, 192.92600000000002, 267.269)), ('C', 1119, u'ASN', 0.6861522583283068, (189.287, 205.08700000000002, 277.254)), ('C', 1128, u'VAL', 0.612929732577203, (181.309, 217.434, 262.188)), ('C', 1135, u'ASN', 0.6998030978428192, (189.23899999999998, 208.04, 243.433)), ('C', 1145, u'LEU', 0.7074461524473457, (188.754, 211.35700000000003, 214.71499999999997)), ('C', 1148, u'PHE', 0.6929992723825534, (186.559, 209.39100000000002, 207.062)), ('C', 1151, u'GLU', 0.7176069476442141, (190.54299999999998, 212.732, 206.51399999999998)), ('C', 1156, u'PHE', 0.6534486428224455, (192.985, 211.678, 198.176)), ('C', 1184, u'ASP', 0.6780654089156023, (187.17, 190.347, 125.71000000000001)), ('C', 1197, u'LEU', 0.7011028537339414, (194.054, 189.61899999999997, 106.093)), ('A', 1027, u'THR', 0.5958012858572758, (199.565, 205.617, 251.518)), ('A', 1062, u'PHE', 0.6377735187516405, (211.612, 208.42200000000003, 252.11599999999999)), ('A', 1072, u'GLU', 0.6871643748874735, (216.77399999999997, 186.642, 266.91999999999996)), ('A', 1080, u'ALA', 0.6534759962793354, (196.82000000000002, 177.70299999999997, 268.98499999999996)), ('A', 1092, u'GLU', 0.6607806746442862, (198.10899999999998, 190.18200000000002, 270.21999999999997)), ('A', 1099, u'GLY', 0.7128803413023573, (210.924, 173.66899999999998, 277.683)), ('A', 1119, u'ASN', 0.7157376271230751, (196.24399999999997, 186.978, 277.267)), ('A', 1148, u'PHE', 0.7174947711462251, (193.89000000000001, 182.38000000000002, 207.08)), ('A', 1151, u'GLU', 0.6982713552970948, (189.003, 184.156, 206.53)), ('A', 1156, u'PHE', 0.6610546308109293, (188.69299999999998, 186.787, 198.18800000000002)), ('A', 1160, u'THR', 0.7879242496423916, (192.655, 185.686, 186.36100000000002)), ('A', 1190, u'ALA', 0.7251037900072594, (208.405, 197.76999999999998, 117.523)), ('A', 1193, u'LEU', 0.7355019708689783, (207.531, 195.701, 112.27199999999999)), ('A', 1197, u'LEU', 0.7163011231799691, (207.262, 198.65, 106.093)), ('A', 703, u'ASN', 0.705287283018653, (193.883, 168.859, 262.83599999999996)), ('A', 712, u'ILE', 0.727011235839677, (209.845, 180.503, 264.447)), ('A', 717, u'ASN', 0.6694753646873216, (217.255, 192.21499999999997, 270.158)), ('A', 725, u'GLU', 0.6385842833404627, (213.266, 204.23499999999999, 249.73499999999999)), ('A', 756, u'TYR', 0.6434068587408286, (197.69, 207.23299999999998, 206.86100000000002)), ('A', 763, u'LEU', 0.65520781226334, (198.935, 208.154, 219.60999999999999)), ('A', 770, u'ILE', 0.3478125773616841, (198.602, 209.292, 231.036)), ('A', 923, u'ILE', 0.725408234232065, (193.82500000000002, 195.38000000000002, 98.88499999999999)), ('A', 931, u'ILE', 0.6515516310145215, (192.77499999999998, 200.39100000000002, 110.09)), ('A', 945, u'LEU', 0.682672136906145, (195.11299999999997, 201.291, 130.502)), ('A', 966, u'LEU', 0.6577336087937171, (198.349, 203.526, 161.665)), ('A', 972, u'ALA', 0.6813425146536096, (198.55800000000002, 206.60299999999998, 170.569)), ('A', 973, u'ILE', 0.5950342573946055, (199.339, 203.111, 171.947)), ('A', 994, u'ASP', 0.6064330583967588, (203.047, 200.353, 202.495)), ('A', 1005, u'GLN', 0.5838614243768017, (201.80800000000002, 200.45200000000003, 218.66299999999998)), ('A', 1006, u'THR', 0.6006004092729075, (203.955, 198.136, 220.871)), ('A', 1018, u'ILE', 0.6623609190690949, (203.539, 204.895, 237.672)), ('B', 1033, u'VAL', 0.6245024472077159, (183.463, 197.869, 257.76)), ('B', 1046, u'GLY', 0.6864890871983501, (192.531, 211.347, 260.328)), ('B', 1050, u'MET', 0.6673931521787067, (183.671, 203.238, 262.214)), ('B', 1062, u'PHE', 0.6769209982353315, (182.195, 204.642, 252.108)), ('B', 1072, u'GLU', 0.6564693160347874, (198.47899999999998, 220.016, 266.89599999999996)), ('B', 1079, u'PRO', 0.7194620599995613, (213.441, 208.569, 266.66700000000003)), ('B', 1080, u'ALA', 0.6970182817387895, (216.192, 207.202, 268.97999999999996)), ('B', 1081, u'ILE', 0.7082235905299203, (218.94299999999998, 208.33100000000002, 271.43899999999996)), ('B', 1086, u'LYS', 0.7275556277106178, (223.954, 202.292, 273.48099999999994)), ('B', 1092, u'GLU', 0.6561725224346782, (204.73899999999998, 202.084, 270.21999999999997)), ('B', 1094, u'VAL', 0.7176636596892912, (208.037, 208.722, 269.81)), ('B', 1096, u'VAL', 0.6843233991181986, (208.461, 213.865, 272.58)), ('B', 1108, u'ASN', 0.6857124123536538, (199.036, 210.08, 267.267)), ('B', 1128, u'VAL', 0.6641382742892529, (223.14399999999998, 202.811, 262.21799999999996)), ('B', 1135, u'ASN', 0.7198221581591574, (211.066, 200.623, 243.45100000000002)), ('B', 1138, u'TYR', 0.7114369579494956, (209.252, 198.02200000000002, 235.041)), ('B', 1142, u'GLN', 0.7339321154220213, (210.975, 199.11399999999998, 223.796)), ('B', 1148, u'PHE', 0.663152007585164, (213.618, 202.24699999999999, 207.08100000000002)), ('B', 1151, u'GLU', 0.685865523942503, (214.52200000000002, 197.126, 206.538)), ('B', 1161, u'SER', 0.7758465185054325, (209.71599999999998, 198.198, 183.191)), ('B', 1164, u'VAL', 0.7184970396849687, (207.85500000000002, 200.46200000000002, 175.094)), ('B', 1183, u'ILE', 0.6713607334449295, (196.73999999999998, 207.638, 127.235)), ('B', 1190, u'ALA', 0.6671962891801995, (193.053, 207.01399999999998, 117.51400000000001)), ('B', 1191, u'LYS', 0.6611216848652988, (192.024, 210.26, 115.733)), ('B', 1197, u'LEU', 0.7034665243149895, (192.864, 205.569, 106.086)), ('B', 720, u'ILE', 0.6659351141824389, (185.068, 214.45700000000002, 264.96799999999996)), ('B', 725, u'GLU', 0.6430310022618697, (184.996, 208.164, 249.72299999999998)), ('B', 743, u'CYS', 0.5963511114642266, (184.85600000000002, 204.507, 208.232)), ('B', 756, u'TYR', 0.7005322980436837, (190.192, 193.118, 206.869)), ('B', 770, u'ILE', 0.3985091210318537, (187.948, 192.91, 231.045)), ('B', 914, u'ASN', 0.7078538390725979, (204.74399999999997, 193.02, 84.94000000000001)), ('B', 928, u'ASN', 0.6519458361065793, (199.629, 190.296, 105.05199999999999)), ('B', 931, u'ILE', 0.6239212604235382, (198.594, 192.156, 110.101)), ('B', 961, u'THR', 0.6905713638505411, (191.359, 191.511, 154.161)), ('B', 962, u'LEU', 0.6910736574632189, (193.91899999999998, 193.698, 156.015)), ('B', 966, u'LEU', 0.7209644307779899, (193.083, 195.484, 161.671)), ('B', 972, u'ALA', 0.6552176835451216, (190.311, 194.13899999999998, 170.576)), ('B', 973, u'ILE', 0.6416493063454172, (192.946, 196.561, 171.95100000000002)), ('B', 987, u'VAL', 0.7080903211604063, (193.49, 199.677, 192.20299999999997)), ('B', 990, u'GLU', 0.6296576962813074, (191.805, 201.454, 196.67899999999997)), ('B', 994, u'ASP', 0.5282216058036174, (193.475, 201.191, 202.494)), ('B', 1001, u'LEU', 0.5557488158566513, (193.206, 200.934, 212.68200000000002)), ('B', 1005, u'GLN', 0.5697403177215878, (194.006, 200.089, 218.66299999999998)), ('B', 1018, u'ILE', 0.63869318716351, (189.288, 199.393, 237.672))]
data['rota'] = [('C', ' 768 ', 'THR', 0.220416990694814, (209.893, 187.962, 226.32)), ('C', ' 977 ', 'LEU', 0.2926507063656209, (200.115, 193.651, 177.107)), ('C', '1041 ', 'ASP', 0.11465845369763333, (190.803, 189.41, 256.412)), ('C', '1074 ', 'ASN', 0.0029834300015148417, (174.647, 193.08800000000005, 266.897)), ('C', '1082 ', 'CYS', 0.2638916337229011, (178.27, 214.8010000000001, 271.925)), ('C', '1173 ', 'ASN', 0.001093766780595055, (186.394, 203.82000000000005, 152.084)), ('C', '1194 ', 'ASN', 0.1949603452375596, (191.925, 187.711, 110.086)), ('C', '1196 ', 'SER', 0.06457308266421341, (190.89199999999997, 191.67200000000005, 106.911)), ('A', ' 768 ', 'THR', 0.21994606037126035, (200.75799999999995, 213.33, 226.30300000000003)), ('A', ' 977 ', 'LEU', 0.2934419347522234, (200.732, 201.96000000000006, 177.103)), ('A', '1041 ', 'ASP', 0.1141676944755729, (209.05799999999994, 196.114, 256.415)), ('A', '1074 ', 'ASN', 0.00297984057324724, (213.961, 180.29900000000006, 266.919)), ('A', '1082 ', 'CYS', 0.2641278019440726, (193.35099999999994, 172.57100000000005, 271.954)), ('A', '1173 ', 'ASN', 0.001126382668791193, (198.799, 184.96300000000005, 152.099)), ('A', '1194 ', 'ASN', 0.19516007479141728, (209.979, 197.76700000000005, 110.088)), ('A', '1196 ', 'SER', 0.06445644535074861, (207.067, 194.886, 106.916)), ('B', ' 768 ', 'THR', 0.22080306725841795, (183.374, 192.754, 226.31)), ('B', ' 977 ', 'LEU', 0.29415882198674814, (193.245, 198.35, 177.105)), ('B', '1041 ', 'ASP', 0.11520881964532563, (194.132, 208.586, 256.405)), ('B', '1074 ', 'ASN', 0.0029792265905641386, (205.379, 220.7490000000001, 266.895)), ('B', '1082 ', 'CYS', 0.2642358154250968, (222.371, 206.76500000000004, 271.952)), ('B', '1173 ', 'ASN', 0.0011075294685787866, (208.93899999999994, 205.138, 152.096)), ('B', '1194 ', 'ASN', 0.19546502237497201, (192.27, 208.369, 110.077)), ('B', '1196 ', 'SER', 0.06473522554782796, (196.221, 207.283, 106.907))]
data['clusters'] = [('C', '1072', 1, 'smoc Outlier', (178.73, 187.478, 266.905)), ('C', '1074', 1, 'Rotamer\nBond angle:CA:CB:CG', (174.647, 193.08800000000002, 266.897)), ('C', '1077', 1, 'Dihedral angle:CA:C', (176.516, 201.73999999999998, 268.744)), ('C', '1078', 1, 'Dihedral angle:N:CA', (177.62, 205.22, 267.862)), ('C', '1081', 1, 'smoc Outlier', (178.626, 211.04899999999998, 271.417)), ('C', '1082', 1, 'Rotamer', (178.27, 214.8010000000001, 271.925)), ('C', '1085', 1, 'smoc Outlier', (178.077, 220.444, 273.045)), ('C', '1086', 1, 'smoc Outlier', (181.353, 218.41, 273.449)), ('C', '1088', 1, 'Bond angle:CB:CG:CD2', (183.4, 212.237, 273.08)), ('C', '1090', 1, 'Planar group:CA:C:O', (186.88700000000003, 206.04899999999998, 271.828)), ('C', '1091', 1, 'Planar group:N\nDihedral angle:CD:NE:CZ:NH1', (190.55200000000002, 205.28, 271.977)), ('C', '1092', 1, 'Dihedral angle:CB:CG:CD:OE1\ncablam Outlier', (191.135, 201.865, 270.21099999999996)), ('C', '1094', 1, 'smoc Outlier', (183.737, 201.404, 269.801)), ('C', '1095', 1, 'Bond angle:CA:CB:CG', (180.88500000000002, 202.559, 272.116)), ('C', '1096', 1, 'Bond angle:CA:CB:CG1', (179.07, 199.20499999999998, 272.574)), ('C', '1100', 1, 'smoc Outlier', (171.471, 201.797, 280.124)), ('C', '1101', 1, 'Bond angle:CB:CG:CD2', (175.23499999999999, 202.57899999999998, 279.673)), ('C', '1102', 1, 'Planar group:CB:CG:CD1:CD2:NE1:CE2:CE3:CZ2:CZ3:CH2', (178.031, 203.19899999999998, 277.13)), ('C', '1105', 1, 'smoc Outlier', (184.494, 197.597, 273.671)), ('C', '1106', 1, 'Bond angle:OE1:CD:NE2', (187.48100000000002, 196.532, 271.57099999999997)), ('C', '1107', 1, 'Dihedral angle:CD:NE:CZ:NH1', (186.18800000000002, 196.585, 267.919)), ('C', '1108', 1, 'smoc Outlier', (187.05800000000002, 192.92600000000002, 267.269)), ('C', '1111', 1, 'cablam Outlier', (184.3, 192.9, 276.3)), ('C', '1113', 1, 'Bond angle:OE1:CD:NE2', (184.89600000000002, 198.736, 279.72099999999995)), ('C', '1119', 1, 'smoc Outlier', (189.287, 205.08700000000002, 277.254)), ('C', '1125', 1, 'C-beta\nside-chain clash', (174.599, 203.268, 267.253)), ('C', '709', 1, 'C-beta', (173.297, 204.40600000000006, 267.683)), ('C', '712', 1, 'smoc Outlier', (176.88700000000003, 196.548, 264.42499999999995)), ('C', '743', 1, 'backbone clash\nside-chain clash\nsmoc Outlier', (174.73, 204.633, 267.945)), ('C', '746', 1, 'backbone clash\nside-chain clash', (174.73, 204.633, 267.945)), ('C', '1010', 2, 'Bond angle:OE1:CD:NE2', (196.171, 191.62800000000001, 226.71399999999997)), ('C', '1011', 2, 'Bond angle:OE1:CD:NE2\nsmoc Outlier', (199.414, 189.61499999999998, 227.33700000000002)), ('C', '1014', 2, 'Dihedral angle:CD:NE:CZ:NH1', (198.159, 190.57, 232.38800000000003)), ('C', '1017', 2, 'Dihedral angle:CB:CG:CD:OE1', (198.787, 192.68800000000002, 236.918)), ('C', '1018', 2, 'smoc Outlier', (201.187, 189.782, 237.67899999999997)), ('C', '1021', 2, 'smoc Outlier', (200.45000000000002, 190.45600000000002, 242.51399999999998)), ('C', '749', 3, 'C-beta\nside-chain clash\nBond angle:CA:CB:SG', (200.518, 185.395, 202.766)), ('C', '752', 3, 'side-chain clash', (202.534, 191.631, 200.224)), ('C', '753', 3, 'smoc Outlier', (204.901, 188.655, 205.92700000000002)), ('C', '756', 3, 'side-chain clash', (203.054, 193.055, 204.416)), ('C', '990', 3, 'smoc Outlier', (198.14499999999998, 190.87800000000001, 196.684)), ('C', '997', 3, 'side-chain clash', (199.857, 186.99, 204.049)), ('C', '763', 4, 'smoc Outlier', (206.33200000000002, 192.127, 219.621)), ('C', '765', 4, 'Dihedral angle:CD:NE:CZ:NH1', (210.86, 192.001, 222.804)), ('C', '768', 4, 'Rotamer', (209.893, 187.962, 226.32)), ('C', '770', 4, 'smoc Outlier', (207.472, 191.85200000000003, 231.04899999999998)), ('C', '1054', 5, 'Bond angle:OE1:CD:NE2', (205.017, 177.55, 250.292)), ('C', '1062', 5, 'Dihedral angle:CA:C\nsmoc Outlier', (200.184, 181.035, 252.127)), ('C', '1063', 5, 'Dihedral angle:N:CA', (198.985, 178.859, 254.954)), ('C', '725', 5, 'smoc Outlier', (195.73399999999998, 181.698, 249.74099999999999)), ('C', '1128', 6, 'smoc Outlier', (181.309, 217.434, 262.188)), ('C', '703', 6, 'Dihedral angle:CA:C', (174.79899999999998, 216.194, 262.802)), ('C', '704', 6, 'Dihedral angle:N:CA', (174.692, 213.692, 259.894)), ('C', '705', 6, 'cablam Outlier', (176.1, 210.2, 260.7)), ('C', '1040', 7, 'Bond angle:C', (190.86800000000002, 191.955, 259.384)), ('C', '1041', 7, 'Rotamer\nC-beta\nBond angle:N:CA\nDihedral angle:CA:CB:CG:OD1', (190.803, 189.41, 256.412)), ('C', '1042', 7, 'Bond angle:N:CA:C', (194.27899999999997, 190.37, 255.117)), ('C', '1043', 7, 'C-beta\ncablam CA Geom Outlier', (197.56, 187.438, 256.641)), ('C', '959', 8, 'smoc Outlier', (202.459, 195.52200000000002, 151.46200000000002)), ('C', '962', 8, 'smoc Outlier', (203.80800000000002, 196.531, 156.01299999999998)), ('C', '965', 8, 'Bond angle:OE1:CD:NE2', (206.30200000000002, 195.461, 160.437)), ('C', '1135', 9, 'smoc Outlier', (189.23899999999998, 208.04, 243.433)), ('C', '1136', 9, 'Dihedral angle:CA:C', (189.117, 208.817, 239.706)), ('C', '1137', 9, 'Dihedral angle:N:CA', (191.062, 205.97899999999998, 238.1)), ('C', '1180', 10, 'Bond angle:OE1:CD:NE2', (187.434, 192.44, 131.536)), ('C', '1184', 10, 'Dihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (187.17, 190.347, 125.71000000000001)), ('C', '1188', 10, 'Dihedral angle:CB:CG:CD:OE1', (187.646, 189.086, 119.73400000000001)), ('C', '1194', 11, 'Rotamer', (191.925, 187.711, 110.086)), ('C', '1196', 11, 'Rotamer', (190.89199999999997, 191.67200000000005, 106.911)), ('C', '1197', 11, 'smoc Outlier', (194.054, 189.61899999999997, 106.093)), ('C', '1148', 12, 'smoc Outlier', (186.559, 209.39100000000002, 207.062)), ('C', '1151', 12, 'smoc Outlier', (190.54299999999998, 212.732, 206.51399999999998)), ('C', '934', 13, 'smoc Outlier', (201.54, 201.586, 114.657)), ('C', '936', 13, 'Dihedral angle:CA:CB:CG:OD1', (204.341, 204.88700000000003, 117.95400000000001)), ('C', '1155', 14, 'cablam Outlier', (195.0, 214.1, 200.4)), ('C', '1156', 14, 'smoc Outlier', (192.985, 211.678, 198.176)), ('C', '920', 15, 'Bond angle:OE1:CD:NE2', (199.816, 202.11499999999998, 93.63799999999999)), ('C', '923', 15, 'smoc Outlier', (197.95700000000002, 202.88400000000001, 98.88199999999999)), ('C', '984', 16, 'smoc Outlier', (197.975, 193.575, 187.242)), ('C', '985', 16, 'Bond angle:CA:CB:CG', (196.212, 190.296, 188.191)), ('C', '977', 17, 'Rotamer', (200.115, 193.651, 177.107)), ('C', '980', 17, 'side-chain clash', (200.478, 198.665, 181.771)), ('C', '912', 18, 'smoc Outlier', (194.583, 203.953, 82.574)), ('C', '914', 18, 'Bond angle:CA:CB:CG', (198.989, 206.15200000000002, 84.925)), ('C', '995', 19, 'side-chain clash', (191.33, 196.255, 204.265)), ('C', '999', 19, 'smoc Outlier', (193.349, 193.091, 210.08)), ('A', '1072', 1, 'smoc Outlier', (216.77399999999997, 186.642, 266.91999999999996)), ('A', '1074', 1, 'Rotamer\nBond angle:CA:CB:CG', (213.961, 180.29899999999998, 266.919)), ('A', '1077', 1, 'Dihedral angle:CA:C', (205.535, 177.58800000000002, 268.769)), ('A', '1078', 1, 'Dihedral angle:N:CA', (201.97, 176.8, 267.887)), ('A', '1080', 1, 'smoc Outlier', (196.82000000000002, 177.70299999999997, 268.98499999999996)), ('A', '1082', 1, 'Rotamer', (193.35099999999994, 172.57100000000005, 271.954)), ('A', '1088', 1, 'Bond angle:CB:CG:CD2', (193.002, 178.297, 273.103)), ('A', '1095', 1, 'Bond angle:CA:CB:CG', (202.63899999999998, 180.964, 272.137)), ('A', '1096', 1, 'Bond angle:CA:CB:CG1', (206.45100000000002, 181.072, 272.59499999999997)), ('A', '1099', 1, 'smoc Outlier', (210.924, 173.66899999999998, 277.683)), ('A', '1101', 1, 'Bond angle:CB:CG:CD2', (205.45000000000002, 176.071, 279.699)), ('A', '1102', 1, 'Planar group:CB:CG:CD1:CD2:NE1:CE2:CE3:CZ2:CZ3:CH2', (203.51299999999998, 178.17899999999997, 277.15400000000005)), ('A', '1125', 1, 'C-beta\nside-chain clash', (205.031, 175.139, 267.334)), ('A', '709', 1, 'C-beta', (204.839, 173.46500000000006, 267.712)), ('A', '712', 1, 'smoc Outlier', (209.845, 180.503, 264.447)), ('A', '717', 1, 'smoc Outlier', (217.255, 192.21499999999997, 270.158)), ('A', '743', 1, 'backbone clash\nside-chain clash', (204.142, 174.461, 267.865)), ('A', '746', 1, 'backbone clash\nside-chain clash', (204.142, 174.461, 267.865)), ('A', '1180', 2, 'Bond angle:OE1:CD:NE2', (208.132, 191.536, 131.545)), ('A', '1184', 2, 'Dihedral angle:CA:CB:CG:OD1', (210.076, 192.349, 125.718)), ('A', '1188', 2, 'Dihedral angle:CB:CG:CD:OE1', (210.93, 193.38500000000002, 119.74100000000001)), ('A', '1190', 2, 'smoc Outlier', (208.405, 197.76999999999998, 117.523)), ('A', '1193', 2, 'smoc Outlier', (207.531, 195.701, 112.27199999999999)), ('A', '1194', 2, 'Rotamer', (209.979, 197.76700000000005, 110.088)), ('A', '1196', 2, 'Rotamer', (207.067, 194.886, 106.916)), ('A', '1197', 2, 'smoc Outlier', (207.262, 198.65, 106.093)), ('A', '1091', 3, 'Dihedral angle:CD:NE:CZ:NH1', (195.444, 187.97, 271.989)), ('A', '1092', 3, 'Dihedral angle:CB:CG:CD:OE1\ncablam Outlier\nsmoc Outlier', (198.10899999999998, 190.18200000000002, 270.21999999999997)), ('A', '1106', 3, 'Bond angle:OE1:CD:NE2', (204.555, 189.69, 271.582)), ('A', '1107', 3, 'Dihedral angle:CD:NE:CZ:NH1', (205.156, 188.54, 267.9309999999999)), ('A', '1111', 3, 'cablam Outlier', (209.3, 188.8, 276.3)), ('A', '1113', 3, 'Bond angle:OE1:CD:NE2', (203.94, 186.359, 279.73499999999996)), ('A', '1119', 3, 'smoc Outlier', (196.24399999999997, 186.978, 277.267)), ('A', '1005', 4, 'smoc Outlier', (201.80800000000002, 200.45200000000003, 218.66299999999998)), ('A', '1006', 4, 'smoc Outlier', (203.955, 198.136, 220.871)), ('A', '1010', 4, 'Bond angle:OE1:CD:NE2', (204.453, 199.61599999999999, 226.71299999999997)), ('A', '1011', 4, 'Bond angle:OE1:CD:NE2', (204.572, 203.43200000000002, 227.33200000000002)), ('A', '1014', 4, 'Dihedral angle:CD:NE:CZ:NH1', (204.373, 201.873, 232.38400000000001)), ('A', '1017', 4, 'Dihedral angle:CB:CG:CD:OE1', (202.225, 201.36200000000002, 236.915)), ('A', '1018', 4, 'smoc Outlier', (203.539, 204.895, 237.672)), ('A', '763', 5, 'smoc Outlier', (198.935, 208.154, 219.60999999999999)), ('A', '765', 5, 'Dihedral angle:CD:NE:CZ:NH1', (196.777, 212.141, 222.788)), ('A', '768', 5, 'Rotamer', (200.75799999999995, 213.33, 226.30300000000003)), ('A', '770', 5, 'smoc Outlier', (198.602, 209.292, 231.036)), ('A', '1054', 6, 'Bond angle:OE1:CD:NE2', (212.20999999999998, 214.349, 250.27499999999998)), ('A', '1062', 6, 'Dihedral angle:CA:C\nsmoc Outlier', (211.612, 208.42200000000003, 252.11599999999999)), ('A', '1063', 6, 'Dihedral angle:N:CA', (214.096, 208.477, 254.944)), ('A', '725', 6, 'smoc Outlier', (213.266, 204.23499999999999, 249.73499999999999)), ('A', '1040', 7, 'Bond angle:C', (206.82200000000003, 194.899, 259.389)), ('A', '1041', 7, 'Rotamer\nC-beta\nBond angle:N:CA\nDihedral angle:CA:CB:CG:OD1', (209.05800000000002, 196.11399999999998, 256.41499999999996)), ('A', '1042', 7, 'Bond angle:N:CA:C', (206.48700000000002, 198.641, 255.117)), ('A', '1043', 7, 'C-beta\ncablam CA Geom Outlier', (207.383, 202.95100000000005, 256.636)), ('A', '703', 8, 'Dihedral angle:CA:C\nsmoc Outlier', (193.883, 168.859, 262.83599999999996)), ('A', '704', 8, 'Dihedral angle:N:CA', (196.10299999999998, 170.015, 259.92699999999996)), ('A', '705', 8, 'cablam Outlier', (198.4, 173.0, 260.7)), ('A', '972', 9, 'smoc Outlier', (198.55800000000002, 206.60299999999998, 170.569)), ('A', '973', 9, 'smoc Outlier', (199.339, 203.111, 171.947)), ('A', '977', 9, 'Rotamer', (200.732, 201.96000000000006, 177.103)), ('A', '1148', 10, 'smoc Outlier', (193.89000000000001, 182.38000000000002, 207.08)), ('A', '1151', 10, 'smoc Outlier', (189.003, 184.156, 206.53)), ('A', '1159', 11, 'Bond angle:CB:CG:CD2', (190.108, 186.424, 189.132)), ('A', '1160', 11, 'smoc Outlier', (192.655, 185.686, 186.36100000000002)), ('A', '1155', 12, 'cablam Outlier', (185.6, 187.4, 200.4)), ('A', '1156', 12, 'smoc Outlier', (188.69299999999998, 186.787, 198.18800000000002)), ('A', '965', 13, 'Bond angle:OE1:CD:NE2', (196.069, 206.39100000000002, 160.42800000000003)), ('A', '966', 13, 'smoc Outlier', (198.349, 203.526, 161.665)), ('A', '920', 14, 'Bond angle:OE1:CD:NE2', (193.561, 197.36800000000002, 93.639)), ('A', '923', 14, 'smoc Outlier', (193.82500000000002, 195.38000000000002, 98.88499999999999)), ('A', '1136', 15, 'Dihedral angle:CA:C', (193.10299999999998, 184.92000000000002, 239.721)), ('A', '1137', 15, 'Dihedral angle:N:CA', (194.58700000000002, 188.02200000000002, 238.112)), ('A', '756', 16, 'smoc Outlier', (197.69, 207.23299999999998, 206.86100000000002)), ('A', '758', 16, 'cablam Outlier', (196.5, 212.0, 211.7)), ('A', '749', 17, 'C-beta\nside-chain clash\nBond angle:CA:CB:SG', (207.67499999999998, 206.472, 202.757)), ('A', '997', 17, 'side-chain clash', (210.674, 203.708, 204.579)), ('A', '945', 18, 'smoc Outlier', (195.11299999999997, 201.291, 130.502)), ('A', '949', 18, 'Bond angle:OE1:CD:NE2', (196.379, 203.97299999999998, 135.95600000000002)), ('B', '1077', 1, 'Dihedral angle:CA:C', (211.937, 214.80800000000002, 268.754)), ('B', '1078', 1, 'Dihedral angle:N:CA', (214.401, 212.11299999999997, 267.876)), ('B', '1079', 1, 'smoc Outlier', (213.441, 208.569, 266.66700000000003)), ('B', '1080', 1, 'smoc Outlier', (216.192, 207.202, 268.97999999999996)), ('B', '1081', 1, 'smoc Outlier', (218.94299999999998, 208.33100000000002, 271.43899999999996)), ('B', '1082', 1, 'Rotamer', (222.371, 206.76500000000004, 271.952)), ('B', '1086', 1, 'smoc Outlier', (223.954, 202.292, 273.48099999999994)), ('B', '1088', 1, 'Bond angle:CB:CG:CD2', (217.585, 203.60299999999998, 273.103)), ('B', '1090', 1, 'Planar group:CA:C:O', (210.484, 203.67399999999998, 271.843)), ('B', '1091', 1, 'Planar group:N\nDihedral angle:CD:NE:CZ:NH1', (207.98600000000002, 200.883, 271.99099999999993)), ('B', '1092', 1, 'Dihedral angle:CB:CG:CD:OE1\ncablam Outlier\nsmoc Outlier', (204.73899999999998, 202.084, 270.21999999999997)), ('B', '1094', 1, 'smoc Outlier', (208.037, 208.722, 269.81)), ('B', '1095', 1, 'Bond angle:CA:CB:CG', (210.459, 210.617, 272.127)), ('B', '1096', 1, 'Bond angle:CA:CB:CG1\nsmoc Outlier', (208.461, 213.865, 272.58)), ('B', '1101', 1, 'Bond angle:CB:CG:CD2', (213.291, 215.506, 279.684)), ('B', '1102', 1, 'Planar group:CB:CG:CD1:CD2:NE1:CE2:CE3:CZ2:CZ3:CH2', (212.434, 212.772, 277.141)), ('B', '1106', 1, 'Bond angle:OE1:CD:NE2', (201.944, 207.914, 271.573)), ('B', '1107', 1, 'Dihedral angle:CD:NE:CZ:NH1', (202.64, 209.006, 267.92099999999994)), ('B', '1108', 1, 'smoc Outlier', (199.036, 210.08, 267.267)), ('B', '1111', 1, 'cablam Outlier', (200.4, 212.5, 276.3)), ('B', '1113', 1, 'Bond angle:OE1:CD:NE2', (205.135, 209.05800000000002, 279.72599999999994)), ('B', '1125', 1, 'C-beta\nside-chain clash', (214.262, 215.686, 267.241)), ('B', '1128', 1, 'smoc Outlier', (223.14399999999998, 202.811, 262.21799999999996)), ('B', '703', 1, 'Dihedral angle:CA:C', (225.32200000000003, 209.07, 262.83099999999996)), ('B', '704', 1, 'Dihedral angle:N:CA', (223.212, 210.411, 259.919)), ('B', '705', 1, 'cablam Outlier', (219.5, 210.9, 260.7)), ('B', '707', 1, 'Planar group:CB:CG:CD1:CD2:CE1:CE2:CZ:OH', (219.474, 210.79399999999998, 266.15900000000005)), ('B', '709', 1, 'C-beta', (215.856, 216.26400000000007, 267.696)), ('B', '997', 1, 'side-chain clash', (215.353, 214.883, 267.906)), ('B', '1180', 2, 'Bond angle:OE1:CD:NE2', (198.586, 209.91, 131.533)), ('B', '1183', 2, 'smoc Outlier', (196.73999999999998, 207.638, 127.235)), ('B', '1184', 2, 'Dihedral angle:CA:CB:CG:OD1', (196.911, 211.181, 125.70400000000001)), ('B', '1188', 2, 'Dihedral angle:CB:CG:CD:OE1', (195.58800000000002, 211.395, 119.727)), ('B', '1190', 2, 'smoc Outlier', (193.053, 207.01399999999998, 117.51400000000001)), ('B', '1191', 2, 'smoc Outlier', (192.024, 210.26, 115.733)), ('B', '1194', 2, 'Rotamer', (192.27, 208.369, 110.077)), ('B', '1196', 2, 'Rotamer', (196.221, 207.283, 106.907)), ('B', '1197', 2, 'smoc Outlier', (192.864, 205.569, 106.086)), ('B', '743', 3, 'backbone clash\nsmoc Outlier', (183.597, 203.758, 204.299)), ('B', '745', 3, 'Dihedral angle:CA:CB:CG:OD1', (179.007, 206.523, 206.657)), ('B', '746', 3, 'backbone clash', (183.597, 203.758, 204.299)), ('B', '749', 3, 'C-beta\nside-chain clash\nBond angle:CA:CB:SG', (185.863, 202.142, 202.753)), ('B', '995', 3, 'side-chain clash', (186.576, 205.743, 204.659)), ('B', '1010', 4, 'Bond angle:OE1:CD:NE2', (193.406, 202.809, 226.70999999999998)), ('B', '1011', 4, 'Bond angle:OE1:CD:NE2', (190.041, 201.006, 227.33)), ('B', '1014', 4, 'Dihedral angle:CD:NE:CZ:NH1', (191.489, 201.61899999999997, 232.38200000000003)), ('B', '1017', 4, 'Dihedral angle:CB:CG:CD:OE1', (193.005, 200.02, 236.915)), ('B', '1018', 4, 'smoc Outlier', (189.288, 199.393, 237.672)), ('B', '1040', 5, 'Bond angle:C', (196.30100000000002, 207.26, 259.38)), ('B', '1041', 5, 'Rotamer\nC-beta\nBond angle:N:CA\nDihedral angle:CA:CB:CG:OD1', (194.132, 208.586, 256.405)), ('B', '1042', 5, 'Bond angle:N:CA:C', (193.228, 205.094, 255.111)), ('B', '1043', 5, 'C-beta\ncablam CA Geom Outlier', (189.048, 203.718, 256.631)), ('B', '1046', 5, 'smoc Outlier', (192.531, 211.347, 260.328)), ('B', '961', 6, 'smoc Outlier', (191.359, 191.511, 154.161)), ('B', '962', 6, 'smoc Outlier', (193.91899999999998, 193.698, 156.015)), ('B', '965', 6, 'Bond angle:OE1:CD:NE2', (191.74099999999999, 192.075, 160.437)), ('B', '966', 6, 'smoc Outlier', (193.083, 195.484, 161.671)), ('B', '1054', 7, 'Bond angle:OE1:CD:NE2', (176.76399999999998, 202.195, 250.26899999999998)), ('B', '1062', 7, 'Dihedral angle:CA:C\nsmoc Outlier', (182.195, 204.642, 252.108)), ('B', '1063', 7, 'Dihedral angle:N:CA', (180.906, 206.76899999999998, 254.933)), ('B', '725', 7, 'smoc Outlier', (184.996, 208.164, 249.72299999999998)), ('B', '985', 8, 'Bond angle:CA:CB:CG', (192.27599999999998, 203.414, 188.185)), ('B', '987', 8, 'smoc Outlier', (193.49, 199.677, 192.20299999999997)), ('B', '990', 8, 'smoc Outlier', (191.805, 201.454, 196.67899999999997)), ('B', '994', 8, 'smoc Outlier', (193.475, 201.191, 202.494)), ('B', '972', 9, 'smoc Outlier', (190.311, 194.13899999999998, 170.576)), ('B', '973', 9, 'smoc Outlier', (192.946, 196.561, 171.95100000000002)), ('B', '977', 9, 'Rotamer', (193.245, 198.35, 177.105)), ('B', '980', 9, 'side-chain clash', (196.986, 195.403, 182.029)), ('B', '1135', 10, 'smoc Outlier', (211.066, 200.623, 243.45100000000002)), ('B', '1136', 10, 'Dihedral angle:CA:C', (211.805, 200.33800000000002, 239.725)), ('B', '1137', 10, 'Dihedral angle:N:CA', (208.376, 200.071, 238.11499999999998)), ('B', '1138', 10, 'smoc Outlier', (209.252, 198.02200000000002, 235.041)), ('B', '765', 11, 'Dihedral angle:CD:NE:CZ:NH1', (186.394, 189.89600000000002, 222.8)), ('B', '768', 11, 'Rotamer', (183.374, 192.754, 226.31)), ('B', '770', 11, 'smoc Outlier', (187.948, 192.91, 231.045)), ('B', '1033', 12, 'smoc Outlier', (183.463, 197.869, 257.76)), ('B', '1036', 12, 'cablam Outlier', (188.7, 199.3, 262.7)), ('B', '1050', 12, 'smoc Outlier', (183.671, 203.238, 262.214)), ('B', '1148', 13, 'smoc Outlier', (213.618, 202.24699999999999, 207.08100000000002)), ('B', '1151', 13, 'smoc Outlier', (214.52200000000002, 197.126, 206.538)), ('B', '1072', 14, 'smoc Outlier', (198.47899999999998, 220.016, 266.89599999999996)), ('B', '1074', 14, 'Rotamer\nBond angle:CA:CB:CG', (205.379, 220.74899999999997, 266.895)), ('B', '928', 15, 'smoc Outlier', (199.629, 190.296, 105.05199999999999)), ('B', '931', 15, 'smoc Outlier', (198.594, 192.156, 110.101)), ('B', '1001', 16, 'smoc Outlier', (193.206, 200.934, 212.68200000000002)), ('B', '1005', 16, 'smoc Outlier', (194.006, 200.089, 218.66299999999998)), ('B', '756', 17, 'smoc Outlier', (190.192, 193.118, 206.869)), ('B', '758', 17, 'cablam Outlier', (186.6, 189.8, 211.7)), ('B', '1159', 18, 'Bond angle:CB:CG:CD2', (212.009, 196.92800000000003, 189.14)), ('B', '1161', 18, 'smoc Outlier', (209.71599999999998, 198.198, 183.191)), ('E', '1', 1, 'side-chain clash', (173.734, 196.986, 281.856)), ('F', '1', 1, 'side-chain clash', (183.953, 210.751, 236.069)), ('F', '2', 1, 'side-chain clash', (183.953, 210.751, 236.069)), ('J', '1', 1, 'side-chain clash', (211.215, 177.512, 281.757)), ('K', '1', 1, 'side-chain clash', (193.984, 179.479, 236.063)), ('K', '2', 1, 'side-chain clash', (193.984, 179.479, 236.063)), ('O', '1', 1, 'side-chain clash', (209.229, 219.54, 281.898)), ('P', '1', 1, 'side-chain clash', (215.965, 204.017, 235.702)), ('P', '2', 1, 'side-chain clash', (215.965, 204.017, 235.702))]
data['cablam'] = [('C', '705', 'VAL', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (176.1, 210.2, 260.7)), ('C', '758', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nG-SHH', (210.9, 192.3, 211.7)), ('C', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nIS---', (201.5, 189.4, 262.7)), ('C', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (191.1, 201.9, 270.2)), ('C', '1111', 'GLU', 'check CA trace,carbonyls, peptide', ' \nS----', (184.3, 192.9, 276.3)), ('C', '1155', 'TYR', 'check CA trace,carbonyls, peptide', 'turn\nHTT--', (195.0, 214.1, 200.4)), ('C', '1043', 'CYS', 'check CA trace', 'turn\nSTTSS', (196.3, 187.1, 255.7)), ('A', '705', 'VAL', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (198.4, 173.0, 260.7)), ('A', '758', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nG-SHH', (196.5, 212.0, 211.7)), ('A', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nIS---', (203.7, 205.4, 262.7)), ('A', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (198.1, 190.2, 270.2)), ('A', '1111', 'GLU', 'check CA trace,carbonyls, peptide', ' \nS----', (209.3, 188.8, 276.3)), ('A', '1155', 'TYR', 'check CA trace,carbonyls, peptide', 'turn\nHTT--', (185.6, 187.4, 200.4)), ('A', '1043', 'CYS', 'check CA trace', 'turn\nSTTSS', (208.3, 202.0, 255.7)), ('B', '705', 'VAL', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (219.5, 210.9, 260.7)), ('B', '758', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nG-SHH', (186.6, 189.8, 211.7)), ('B', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nIS---', (188.7, 199.3, 262.7)), ('B', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (204.7, 202.1, 270.2)), ('B', '1111', 'GLU', 'check CA trace,carbonyls, peptide', ' \nS----', (200.4, 212.5, 276.3)), ('B', '1155', 'TYR', 'check CA trace,carbonyls, peptide', 'turn\nHTT--', (213.4, 192.6, 200.4)), ('B', '1043', 'CYS', 'check CA trace', 'turn\nSTTSS', (189.4, 205.0, 255.7))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22293/6xra/Model_validation_1/validation_cootdata/molprobity_probe6xra_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

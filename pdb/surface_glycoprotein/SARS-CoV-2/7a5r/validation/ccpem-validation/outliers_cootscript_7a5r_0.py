
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
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' H 174  LEU  O  ', ' H 174  LEU HD12', -1.053, (212.981, 258.006, 228.392)), (' I 174  LEU  O  ', ' I 174  LEU HD12', -1.049, (221.993, 177.123, 228.236)), (' M 119  PRO  HB3', ' M 145  PHE  HB3', -0.758, (206.086, 159.002, 227.086)), (' L 119  PRO  HB3', ' L 145  PHE  HB3', -0.733, (228.236, 276.042, 227.355)), (' I  91  THR  HA ', ' I 115  VAL  O  ', -0.716, (219.896, 189.306, 216.089)), (' H  91  THR  HA ', ' H 115  VAL  O  ', -0.716, (214.98, 245.542, 216.613)), (' A 472  ILE HG13', ' A 482  GLY  HA2', -0.661, (244.906, 183.827, 217.828)), (' B 472  ILE HG13', ' B 482  GLY  HA2', -0.66, (189.987, 250.943, 217.886)), (' I 218  LYS  NZ ', ' M 127  SER  OG ', -0.648, (231.431, 155.267, 221.338)), (' I 141  ALA  HB3', ' M 124  PHE  HZ ', -0.629, (217.504, 155.805, 221.596)), (' I 174  LEU  CD1', ' I 174  LEU  O  ', -0.626, (221.766, 177.689, 228.311)), (' H 174  LEU  CD1', ' H 174  LEU  O  ', -0.613, (213.459, 257.405, 228.521)), (' H  38  ARG  HB3', ' H  48  MET  HE2', -0.608, (222.648, 239.852, 217.564)), (' H 198  TYR  HB2', ' H 215  VAL  HB ', -0.598, (210.966, 279.122, 212.497)), (' I  38  ARG  HB3', ' I  48  MET  HE2', -0.596, (212.081, 195.591, 217.248)), (' I 198  TYR  HB2', ' I 215  VAL  HB ', -0.586, (223.886, 155.533, 211.892)), (' L 152  VAL HG11', ' L 183  SER  HB2', -0.579, (219.922, 271.337, 232.367)), (' M 152  VAL HG11', ' M 183  SER  HB2', -0.574, (215.12, 163.91, 231.925)), (' I 170  PHE  CE2', ' M 182  SER  HB2', -0.544, (215.469, 163.867, 223.535)), (' B 393  THR HG22', ' B 394  ASN HD22', -0.539, (174.223, 213.498, 210.164)), (' L  34  ILE HG22', ' L  36  LYS  HG2', -0.533, (252.238, 231.31, 217.252)), (' A 393  THR HG22', ' A 394  ASN HD22', -0.526, (260.414, 221.726, 210.378)), (' M  34  ILE HG22', ' M  36  LYS  HG2', -0.523, (181.965, 203.772, 217.245)), (' H 170  PHE  CE2', ' L 182  SER  HB2', -0.508, (219.076, 270.991, 223.949)), (' H  45  LEU HD11', ' L  50  PRO  HG2', -0.505, (231.587, 245.088, 216.3)), (' H 174  LEU  C  ', ' H 174  LEU HD12', -0.492, (212.258, 257.794, 228.382)), (' A 328  ARG  NH1', ' A 533  LEU  HB2', -0.491, (272.55, 237.194, 197.378)), (' A 493  GLN  NE2', ' I  16  GLU  OE1', -0.488, (232.238, 194.911, 210.986)), (' B 328  ARG  NH1', ' B 533  LEU  HB2', -0.487, (162.246, 197.635, 197.292)), (' I 140  ALA  HA ', ' M 122  PHE  CE2', -0.481, (215.215, 151.497, 221.055)), (' I 174  LEU  C  ', ' I 174  LEU HD12', -0.479, (222.499, 177.196, 228.239)), (' B 493  GLN  NE2', ' H  16  GLU  OE1', -0.465, (202.613, 240.047, 211.122)), (' I 140  ALA  HA ', ' M 122  PHE  HE2', -0.456, (215.374, 151.458, 221.597)), (' H 148  ASP  HA ', ' H 179  LEU  HB2', -0.454, (205.967, 260.578, 223.327)), (' I   2  MET  HB2', ' I   2  MET  HE2', -0.454, (201.989, 199.031, 199.401)), (' B 490  PHE  CD1', ' B 491  PRO  HD2', -0.454, (192.444, 244.716, 214.917)), (' A 490  PHE  CD1', ' A 491  PRO  HD2', -0.451, (242.305, 190.145, 214.856)), (' I 139  THR  HA ', ' I 189  PRO  HA ', -0.449, (212.578, 148.399, 216.433)), (' L  91  VAL  HA ', ' L 108  THR  O  ', -0.448, (236.306, 253.354, 221.522)), (' I 148  ASP  HA ', ' I 179  LEU  HB2', -0.446, (229.122, 174.626, 223.053)), (' B 273  ARG HH21', ' B 275  PHE  HE2', -0.446, (162.424, 172.355, 211.302)), (' H 145  LEU HD13', ' H 183  SER  HB3', -0.445, (212.627, 270.443, 222.453)), (' M 155  LYS  HB2', ' M 199  ALA  HB3', -0.442, (219.277, 154.866, 238.428)), (' I 170  PHE  HE2', ' M 182  SER  HB2', -0.441, (215.475, 163.442, 223.596)), (' L 114  ARG  HG2', ' L 115  THR  N  ', -0.441, (240.327, 273.65, 223.913)), (' I 145  LEU HD13', ' I 183  SER  HB3', -0.44, (222.268, 164.579, 222.375)), (' H 139  THR  HA ', ' H 189  PRO  HA ', -0.439, (222.218, 286.502, 216.813)), (' H 141  ALA  HB3', ' L 124  PHE  HZ ', -0.438, (217.425, 279.316, 221.771)), (' M  91  VAL  HA ', ' M 108  THR  O  ', -0.437, (198.414, 181.53, 221.629)), (' L 155  LYS  HB2', ' L 199  ALA  HB3', -0.437, (215.567, 279.929, 238.359)), (' H   2  MET  HB2', ' H   2  MET  HE2', -0.434, (232.656, 236.226, 199.311)), (' M 114  ARG  HG2', ' M 115  THR  N  ', -0.433, (194.857, 161.12, 223.913)), (' M 119  PRO  HB2', ' M 142  LEU HD22', -0.432, (208.76, 158.08, 228.976)), (' I 172  ALA  HB1', ' I 180  TYR  HB3', -0.432, (221.415, 174.973, 221.66)), (' I  16  GLU  O  ', ' I  85  SER  HA ', -0.429, (226.963, 199.843, 216.357)), (' H  16  GLU  O  ', ' H  85  SER  HA ', -0.429, (207.669, 235.394, 216.168)), (' A 472  ILE HD12', ' A 484  GLU  HG2', -0.428, (241.891, 185.07, 215.841)), (' L 114  ARG HH22', ' L 117  ALA  HB2', -0.428, (235.161, 275.869, 224.196)), (' H 172  ALA  HB1', ' H 180  TYR  HB3', -0.427, (213.14, 260.036, 221.977)), (' M 142  LEU HD21', ' M 202  VAL HG11', -0.426, (211.153, 157.876, 231.549)), (' B 472  ILE HD12', ' B 484  GLU  HG2', -0.425, (193.001, 249.763, 215.899)), (' M 114  ARG HH22', ' M 117  ALA  HB2', -0.425, (199.646, 158.985, 224.476)), (' L 119  PRO  HB2', ' L 142  LEU HD22', -0.423, (226.03, 276.808, 228.829)), (' L 142  LEU HD21', ' L 202  VAL HG11', -0.423, (224.009, 276.916, 231.159)), (' B 503  VAL  HA ', ' B 506  GLN  OE1', -0.422, (207.168, 226.419, 199.179)), (' L  18  ARG  HB3', ' L  18  ARG  HE ', -0.421, (251.269, 256.755, 223.897)), (' A 503  VAL  HA ', ' A 506  GLN  OE1', -0.415, (227.662, 208.527, 199.203)), (' L 121  VAL HG21', ' L 202  VAL HG21', -0.412, (224.364, 279.248, 232.042)), (' A 273  ARG HH21', ' A 275  PHE  HE2', -0.412, (272.302, 262.546, 211.298)), (' A 395  VAL HG12', ' A 524  VAL HG21', -0.411, (255.984, 222.795, 205.303)), (' B 454  ARG  HD3', ' B 457  ARG  HG3', -0.411, (191.395, 237.081, 218.204)), (' I  20  ILE HD12', ' I  83  TRP  HZ3', -0.41, (217.642, 196.287, 212.529)), (' H  20  ILE HD12', ' H  83  TRP  HZ3', -0.408, (217.235, 238.715, 212.609)), (' B 395  VAL HG12', ' B 524  VAL HG21', -0.407, (179.172, 212.259, 205.385)), (' L 156  VAL  O  ', ' L 156  VAL HG23', -0.406, (210.353, 277.562, 242.75)), (' L  52  LEU  HA ', ' L  52  LEU HD12', -0.406, (239.743, 243.837, 214.035)), (' M 121  VAL HG21', ' M 202  VAL HG21', -0.404, (210.525, 155.524, 232.182)), (' M 197  VAL  O  ', ' M 197  VAL HG23', -0.402, (224.561, 152.956, 239.4)), (' M 156  VAL  O  ', ' M 156  VAL HG23', -0.401, (224.79, 157.709, 242.468)), (' M 156  VAL HG12', ' M 198  TYR  CD2', -0.4, (225.284, 157.163, 237.59))]
data['smoc'] = [('H', 22, u'CYS', 0.7121145227404964, (223.472, 236.736, 205.146)), ('H', 34, u'ILE', 0.6716799410675137, (229.905, 232.548, 209.436)), ('H', 39, u'GLN', 0.6798147755364079, (224.566, 245.501, 218.77399999999997)), ('H', 40, u'MET', 0.6600174689734709, (221.872, 247.012, 220.96200000000002)), ('H', 90, u'ASP', 0.6433396456988293, (214.772, 242.563, 219.88200000000003)), ('H', 94, u'TYR', 0.6977363077381066, (222.677, 242.637, 213.534)), ('H', 98, u'GLY', 0.6269367076209391, (232.893, 235.629, 208.448)), ('H', 102, u'ILE', 0.6674106163857234, (237.963, 228.21399999999997, 214.11399999999998)), ('H', 144, u'CYS', 0.535458117032173, (210.753, 273.4359999999999, 217.202)), ('H', 197, u'THR', 0.7719589140426454, (211.60299999999998, 282.66, 207.55)), ('H', 200, u'CYS', 0.6697711103468346, (211.17499999999998, 272.98299999999995, 210.347)), ('H', 210, u'LYS', 0.7526317799920905, (205.538, 264.765, 207.172)), ('L', 13, u'VAL', 0.6697244703591194, (244.02800000000002, 263.371, 224.92100000000002)), ('L', 16, u'GLY', 0.6883181376798573, (249.501, 264.23299999999995, 218.54)), ('L', 17, u'GLU', 0.6438075612425108, (249.695, 262.75, 222.04899999999998)), ('L', 27, u'GLN', 0.7594060449997938, (243.186, 233.448, 232.258)), ('L', 40, u'ALA', 0.5566851446403275, (242.576, 240.89100000000002, 218.795)), ('L', 90, u'ALA', 0.6045685077568924, (236.20299999999997, 256.03499999999997, 217.95800000000003)), ('L', 114, u'ARG', 0.7290516419881214, (240.431, 271.374, 223.696)), ('L', 139, u'VAL', 0.5024713320916723, (213.664, 274.28, 228.26399999999998)), ('L', 186, u'THR', 0.6268057373914127, (207.797, 268.96099999999996, 232.18200000000002)), ('A', 35, u'GLY', 0.7476697077257098, (268.20599999999996, 270.954, 206.42800000000003)), ('A', 47, u'VAL', 0.5647604797095331, (256.73299999999995, 263.574, 221.634)), ('A', 53, u'ASP', 0.7003513439276556, (265.56, 258.69599999999997, 207.17399999999998)), ('A', 277, u'LEU', 0.661600473750541, (263.60400000000004, 265.087, 216.52700000000002)), ('A', 324, u'GLU', 0.8180066936179522, (271.194, 248.66899999999998, 202.655)), ('A', 327, u'VAL', 0.8458841705434412, (265.952, 239.786, 201.641)), ('A', 346, u'ARG', 0.7333405388734063, (246.38700000000003, 204.207, 196.403)), ('A', 349, u'SER', 0.5429967704121464, (243.961, 202.05, 205.23899999999998)), ('A', 350, u'VAL', 0.6201050608029595, (243.02200000000002, 203.983, 208.353)), ('A', 361, u'CYS', 0.7288197224217731, (259.93199999999996, 223.924, 199.48000000000002)), ('A', 367, u'VAL', 0.7758673417230936, (244.657, 223.654, 197.112)), ('A', 373, u'SER', 0.7715418372750409, (235.963, 218.05800000000002, 194.41)), ('A', 381, u'GLY', 0.6969677089963496, (243.756, 226.983, 214.74699999999999)), ('A', 387, u'LEU', 0.6766186685432106, (248.92100000000002, 231.32000000000002, 206.135)), ('A', 406, u'GLU', 0.7464381115127696, (232.936, 208.89000000000001, 210.19)), ('A', 432, u'CYS', 0.5590677714148927, (243.69299999999998, 221.406, 208.31)), ('A', 440, u'ASN', 0.7833773575672728, (234.585, 205.777, 191.02200000000002)), ('A', 461, u'LEU', 0.6852950887529995, (245.349, 205.601, 221.511)), ('A', 472, u'ILE', 0.6395744547458213, (243.672, 187.77899999999997, 218.767)), ('A', 510, u'VAL', 0.5084063073814408, (241.17299999999997, 212.131, 203.73899999999998)), ('A', 519, u'HIS', 0.6967554769201406, (263.38599999999997, 225.86700000000002, 215.618)), ('A', 524, u'VAL', 0.6630904815351581, (258.7, 225.666, 204.43200000000002)), ('A', 525, u'CYS', 0.6856867674733503, (258.334, 229.32000000000002, 203.45700000000002)), ('A', 533, u'LEU', 0.8629506367663137, (273.52599999999995, 239.40800000000002, 197.94299999999998)), ('A', 575, u'ALA', 0.6763436158194305, (275.71799999999996, 231.596, 210.82600000000002)), ('B', 349, u'SER', 0.6253591854881152, (190.905, 232.752, 205.21899999999997)), ('B', 368, u'LEU', 0.7408601578593265, (192.86700000000002, 209.262, 199.016)), ('B', 387, u'LEU', 0.6865109088481657, (185.879, 203.493, 206.112)), ('B', 432, u'CYS', 0.5488725494454076, (191.127, 213.39600000000002, 208.291)), ('B', 461, u'LEU', 0.6691598676474649, (189.496, 229.20499999999998, 221.49)), ('B', 479, u'PRO', 0.7558904063050239, (191.85200000000003, 253.20899999999997, 226.859)), ('B', 492, u'LEU', 0.6612791769709314, (194.142, 240.80100000000002, 211.818)), ('B', 510, u'VAL', 0.5481286161880908, (193.671, 222.665, 203.721)), ('B', 525, u'CYS', 0.6360984732662947, (176.47299999999998, 205.51399999999998, 203.42700000000002)), ('B', 534, u'VAL', 0.7980047298298335, (158.43200000000002, 193.192, 199.039)), ('B', 539, u'VAL', 0.8017251279308213, (161.023, 189.28, 206.134)), ('B', 542, u'ASN', 0.8586010185848134, (168.43200000000002, 195.98000000000002, 206.242)), ('M', 14, u'SER', 0.7260432545430249, (189.54899999999998, 168.54399999999998, 222.965)), ('M', 16, u'GLY', 0.6415008064159949, (185.198, 170.484, 218.85100000000003)), ('M', 21, u'ILE', 0.6090982341915284, (190.434, 183.49, 226.524)), ('M', 40, u'ALA', 0.6249499013825741, (192.065, 193.844, 218.911)), ('M', 43, u'GLN', 0.5911705171665782, (196.61899999999997, 185.029, 215.935)), ('M', 85, u'GLN', 0.6794249748752038, (189.467, 172.49, 214.912)), ('M', 95, u'GLN', 0.6375132550848913, (196.39000000000001, 194.43800000000002, 221.995)), ('M', 124, u'PHE', 0.5511209718830415, (222.22, 155.883, 226.006)), ('M', 139, u'VAL', 0.4774076568654477, (221.17299999999997, 160.575, 228.198)), ('M', 141, u'LEU', 0.5752165097134779, (214.911, 159.319, 226.39000000000001)), ('M', 177, u'SER', 0.6934074566055106, (199.71299999999997, 164.677, 220.137)), ('I', 1, u'GLN', 0.7237617491347454, (196.196, 196.58800000000002, 200.33800000000002)), ('I', 14, u'PRO', 0.6784792442360312, (229.51399999999998, 193.5, 218.20899999999997)), ('I', 24, u'GLY', 0.7087541090050453, (206.414, 199.546, 200.842)), ('I', 34, u'ILE', 0.6212806832121087, (204.875, 202.503, 209.518)), ('I', 45, u'LEU', 0.5835887291666272, (206.035, 190.976, 220.797)), ('I', 61, u'SER', 0.7860521899059851, (208.503, 203.904, 223.33700000000002)), ('I', 79, u'ALA', 0.6544295987803299, (211.463, 203.23899999999998, 206.38400000000001)), ('I', 90, u'ASP', 0.652916915785659, (220.11299999999997, 192.49, 219.813)), ('I', 93, u'ILE', 0.6435127978802619, (213.52800000000002, 189.03, 214.629)), ('I', 97, u'ALA', 0.6380540966695776, (203.933, 196.647, 210.077)), ('I', 98, u'GLY', 0.5553943113913999, (201.876, 199.42200000000003, 208.564)), ('I', 182, u'LEU', 0.5385650267472861, (221.31, 169.36200000000002, 220.665)), ('I', 194, u'GLY', 0.7924088668786896, (221.651, 145.02200000000002, 210.708))]
data['rota'] = [('H', '   2 ', 'MET', 0.0007628155140317855, (234.80500000000006, 237.59, 199.704)), ('H', '   6 ', 'GLN', 0.10658612369063769, (222.941, 241.432, 204.12)), ('A', ' 395 ', 'VAL', 0.003127019590465352, (254.23, 220.48599999999993, 207.735)), ('A', ' 525 ', 'CYS', 0.1213212092402761, (258.334, 229.32, 203.45700000000002)), ('B', ' 395 ', 'VAL', 0.003127019590465352, (180.593, 214.33899999999997, 207.708)), ('B', ' 525 ', 'CYS', 0.12149800777520622, (176.473, 205.51399999999998, 203.427)), ('I', '   2 ', 'MET', 0.0006212475991255027, (199.871, 197.455, 199.842)), ('I', '   6 ', 'GLN', 0.10695641861646366, (211.779, 193.61099999999993, 204.137))]
data['clusters'] = [('H', '20', 1, 'side-chain clash', (217.235, 238.715, 212.609)), ('H', '38', 1, 'side-chain clash', (222.648, 239.852, 217.564)), ('H', '39', 1, 'smoc Outlier', (224.566, 245.501, 218.77399999999997)), ('H', '40', 1, 'smoc Outlier', (221.872, 247.012, 220.96200000000002)), ('H', '46', 1, 'Dihedral angle:CB:CG:CD:OE1', (227.691, 240.68200000000002, 221.993)), ('H', '48', 1, 'side-chain clash', (222.648, 239.852, 217.564)), ('H', '83', 1, 'side-chain clash', (217.235, 238.715, 212.609)), ('H', '94', 1, 'smoc Outlier', (222.677, 242.637, 213.534)), ('H', '152', 2, 'Dihedral angle:CB:CG:CD:OE1\ncablam CA Geom Outlier', (212.85600000000002, 256.389, 216.756)), ('H', '153', 2, 'Ramachandran', (213.783, 258.089, 214.395)), ('H', '172', 2, 'side-chain clash', (213.14, 260.036, 221.977)), ('H', '174', 2, 'side-chain clash\nbackbone clash', (212.258, 257.794, 228.382)), ('H', '180', 2, 'side-chain clash', (213.14, 260.036, 221.977)), ('H', '144', 3, 'smoc Outlier', (210.753, 273.4359999999999, 217.202)), ('H', '145', 3, 'side-chain clash', (212.627, 270.443, 222.453)), ('H', '183', 3, 'side-chain clash', (212.627, 270.443, 222.453)), ('H', '200', 3, 'smoc Outlier', (211.17499999999998, 272.98299999999995, 210.347)), ('H', '115', 4, 'backbone clash', (214.98, 245.542, 216.613)), ('H', '90', 4, 'smoc Outlier', (214.772, 242.563, 219.88200000000003)), ('H', '91', 4, 'backbone clash', (214.98, 245.542, 216.613)), ('H', '22', 5, 'smoc Outlier', (223.472, 236.736, 205.146)), ('H', '6', 5, 'Rotamer', (222.941, 241.432, 204.12)), ('H', '7', 5, 'cablam Outlier', (219.3, 241.0, 203.3)), ('H', '198', 6, 'side-chain clash', (231.587, 245.088, 216.3)), ('H', '215', 6, 'side-chain clash', (231.587, 245.088, 216.3)), ('H', '148', 7, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (205.277, 262.043, 221.85700000000003)), ('H', '179', 7, 'side-chain clash', (205.967, 260.578, 223.327)), ('H', '139', 8, 'side-chain clash', (217.425, 279.316, 221.771)), ('H', '189', 8, 'side-chain clash', (217.425, 279.316, 221.771)), ('H', '16', 9, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (205.73999999999998, 237.32100000000003, 214.474)), ('H', '85', 9, 'side-chain clash', (207.669, 235.394, 216.168)), ('H', '34', 10, 'smoc Outlier', (229.905, 232.548, 209.436)), ('H', '98', 10, 'smoc Outlier', (232.893, 235.629, 208.448)), ('L', '119', 1, 'side-chain clash', (226.03, 276.808, 228.829)), ('L', '121', 1, 'side-chain clash', (224.364, 279.248, 232.042)), ('L', '124', 1, 'side-chain clash', (217.425, 279.316, 221.771)), ('L', '139', 1, 'smoc Outlier', (213.664, 274.28, 228.26399999999998)), ('L', '141', 1, 'Dihedral angle:CA:C', (219.907, 275.51099999999997, 226.376)), ('L', '142', 1, 'side-chain clash\nDihedral angle:N:CA', (223.62800000000001, 275.455, 227.099)), ('L', '145', 1, 'side-chain clash', (228.236, 276.042, 227.355)), ('L', '182', 1, 'side-chain clash', (219.076, 270.991, 223.949)), ('L', '202', 1, 'side-chain clash', (224.364, 279.248, 232.042)), ('L', '40', 2, 'smoc Outlier', (242.576, 240.89100000000002, 218.795)), ('L', '52', 2, 'side-chain clash', (239.743, 243.837, 214.035)), ('L', '56', 2, 'cablam CA Geom Outlier', (247.6, 237.8, 217.6)), ('L', '57', 2, 'cablam Outlier', (248.1, 241.0, 219.7)), ('L', '13', 3, 'smoc Outlier', (244.02800000000002, 263.371, 224.92100000000002)), ('L', '16', 3, 'smoc Outlier', (249.501, 264.23299999999995, 218.54)), ('L', '17', 3, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (249.695, 262.75, 222.04899999999998)), ('L', '18', 3, 'side-chain clash', (251.269, 256.755, 223.897)), ('L', '114', 4, 'backbone clash\nside-chain clash\nsmoc Outlier', (235.161, 275.869, 224.196)), ('L', '115', 4, 'backbone clash', (240.327, 273.65, 223.913)), ('L', '117', 4, 'side-chain clash', (235.161, 275.869, 224.196)), ('L', '108', 5, 'backbone clash', (236.306, 253.354, 221.522)), ('L', '90', 5, 'smoc Outlier', (236.20299999999997, 256.03499999999997, 217.95800000000003)), ('L', '91', 5, 'backbone clash', (236.306, 253.354, 221.522)), ('L', '152', 6, 'side-chain clash', (219.922, 271.337, 232.367)), ('L', '183', 6, 'side-chain clash', (219.922, 271.337, 232.367)), ('L', '155', 7, 'side-chain clash', (215.567, 279.929, 238.359)), ('L', '199', 7, 'side-chain clash', (215.567, 279.929, 238.359)), ('L', '34', 8, 'side-chain clash', (252.238, 231.31, 217.252)), ('L', '36', 8, 'side-chain clash', (252.238, 231.31, 217.252)), ('A', '332', 1, 'cablam Outlier', (260.6, 230.2, 193.1)), ('A', '333', 1, 'cablam CA Geom Outlier', (260.9, 226.6, 191.9)), ('A', '334', 1, 'cablam Outlier', (261.0, 223.3, 193.7)), ('A', '361', 1, 'smoc Outlier', (259.93199999999996, 223.924, 199.48000000000002)), ('A', '363', 1, 'Dihedral angle:CA:C', (254.5, 225.761, 199.406)), ('A', '364', 1, 'Dihedral angle:N:CA', (251.772, 227.635, 197.585)), ('A', '393', 1, 'side-chain clash', (260.414, 221.726, 210.378)), ('A', '394', 1, 'side-chain clash', (260.414, 221.726, 210.378)), ('A', '395', 1, 'Rotamer\nside-chain clash', (255.984, 222.795, 205.303)), ('A', '516', 1, 'Dihedral angle:CB:CG:CD:OE1', (254.393, 222.61299999999997, 213.728)), ('A', '518', 1, 'cablam CA Geom Outlier', (260.0, 224.7, 216.9)), ('A', '519', 1, 'cablam CA Geom Outlier\nsmoc Outlier', (263.4, 225.9, 215.6)), ('A', '522', 1, 'cablam Outlier', (264.5, 227.4, 207.2)), ('A', '523', 1, 'cablam Outlier', (262.2, 224.8, 205.6)), ('A', '524', 1, 'side-chain clash\nsmoc Outlier', (255.984, 222.795, 205.303)), ('A', '525', 1, 'Rotamer\nsmoc Outlier', (258.334, 229.32, 203.45700000000002)), ('A', '378', 2, 'cablam Outlier', (238.1, 222.9, 208.3)), ('A', '379', 2, 'cablam Outlier', (241.6, 224.3, 209.3)), ('A', '381', 2, 'smoc Outlier', (243.756, 226.983, 214.74699999999999)), ('A', '430', 2, 'cablam Outlier', (246.9, 223.6, 214.5)), ('A', '432', 2, 'smoc Outlier', (243.69299999999998, 221.406, 208.31)), ('A', '472', 3, 'side-chain clash\nsmoc Outlier', (241.891, 185.07, 215.841)), ('A', '482', 3, 'side-chain clash', (244.906, 183.827, 217.828)), ('A', '484', 3, 'side-chain clash', (241.891, 185.07, 215.841)), ('A', '490', 3, 'side-chain clash', (242.305, 190.145, 214.856)), ('A', '491', 3, 'side-chain clash', (242.305, 190.145, 214.856)), ('A', '419', 4, 'cablam Outlier', (239.0, 208.5, 217.2)), ('A', '420', 4, 'Dihedral angle:CA:CB:CG:OD1', (239.65200000000002, 205.88800000000003, 219.984)), ('A', '461', 4, 'smoc Outlier', (245.349, 205.601, 221.511)), ('A', '465', 4, 'Dihedral angle:CB:CG:CD:OE1', (250.146, 206.563, 217.708)), ('A', '467', 4, 'Dihedral angle:CA:CB:CG:OD1', (249.371, 200.379, 216.51399999999998)), ('A', '349', 5, 'smoc Outlier', (243.961, 202.05, 205.23899999999998)), ('A', '350', 5, 'smoc Outlier', (243.02200000000002, 203.983, 208.353)), ('A', '574', 6, 'Dihedral angle:CA:CB:CG:OD1', (275.268, 233.40800000000002, 214.14899999999997)), ('A', '575', 6, 'smoc Outlier', (275.71799999999996, 231.596, 210.82600000000002)), ('A', '273', 7, 'side-chain clash', (272.302, 262.546, 211.298)), ('A', '275', 7, 'side-chain clash', (272.302, 262.546, 211.298)), ('A', '40', 8, 'Dihedral angle:CA:CB:CG:OD1', (256.242, 262.36400000000003, 207.86700000000002)), ('A', '41', 8, 'cablam Outlier', (252.9, 264.2, 208.0)), ('A', '503', 9, 'side-chain clash', (227.662, 208.527, 199.203)), ('A', '506', 9, 'side-chain clash', (227.662, 208.527, 199.203)), ('A', '328', 10, 'side-chain clash', (232.238, 194.911, 210.986)), ('A', '533', 10, 'side-chain clash\nsmoc Outlier', (232.238, 194.911, 210.986)), ('A', '440', 11, 'smoc Outlier', (234.585, 205.777, 191.02200000000002)), ('A', '442', 11, 'Dihedral angle:CA:CB:CG:OD1', (237.056, 202.72299999999998, 195.376)), ('B', '363', 1, 'Dihedral angle:CA:C', (180.318, 209.064, 199.379)), ('B', '364', 1, 'Dihedral angle:N:CA', (183.04299999999998, 207.184, 197.56)), ('B', '393', 1, 'side-chain clash', (174.223, 213.498, 210.164)), ('B', '394', 1, 'side-chain clash', (174.223, 213.498, 210.164)), ('B', '395', 1, 'Rotamer\nside-chain clash', (179.172, 212.259, 205.385)), ('B', '522', 1, 'cablam Outlier', (170.3, 207.5, 207.2)), ('B', '523', 1, 'cablam Outlier', (172.6, 210.0, 205.6)), ('B', '524', 1, 'side-chain clash', (179.172, 212.259, 205.385)), ('B', '525', 1, 'Rotamer\nsmoc Outlier', (176.473, 205.51399999999998, 203.427)), ('B', '419', 2, 'cablam Outlier', (195.8, 226.3, 217.2)), ('B', '420', 2, 'Dihedral angle:CA:CB:CG:OD1', (195.19299999999998, 228.906, 219.967)), ('B', '454', 2, 'side-chain clash', (191.395, 237.081, 218.204)), ('B', '457', 2, 'side-chain clash', (191.395, 237.081, 218.204)), ('B', '461', 2, 'smoc Outlier', (189.496, 229.20499999999998, 221.49)), ('B', '465', 2, 'Dihedral angle:CB:CG:CD:OE1', (184.7, 228.254, 217.683)), ('B', '467', 2, 'Dihedral angle:CA:CB:CG:OD1', (185.489, 234.436, 216.489)), ('B', '472', 3, 'side-chain clash', (193.001, 249.763, 215.899)), ('B', '482', 3, 'side-chain clash', (189.987, 250.943, 217.886)), ('B', '484', 3, 'side-chain clash', (193.001, 249.763, 215.899)), ('B', '490', 3, 'side-chain clash', (192.444, 244.716, 214.917)), ('B', '491', 3, 'side-chain clash', (192.444, 244.716, 214.917)), ('B', '492', 3, 'smoc Outlier', (194.142, 240.80100000000002, 211.818)), ('B', '378', 4, 'cablam Outlier', (196.7, 211.8, 208.3)), ('B', '379', 4, 'cablam Outlier', (193.2, 210.5, 209.3)), ('B', '432', 4, 'smoc Outlier', (191.127, 213.39600000000002, 208.291)), ('B', '332', 5, 'cablam Outlier', (174.2, 204.6, 193.1)), ('B', '333', 5, 'cablam CA Geom Outlier', (174.0, 208.2, 191.9)), ('B', '334', 5, 'cablam Outlier', (173.8, 211.6, 193.6)), ('B', '516', 6, 'Dihedral angle:CB:CG:CD:OE1', (180.42000000000002, 212.21299999999997, 213.7)), ('B', '518', 6, 'cablam CA Geom Outlier', (174.8, 210.1, 216.9)), ('B', '519', 6, 'cablam CA Geom Outlier', (171.4, 209.0, 215.6)), ('B', '273', 7, 'side-chain clash', (162.424, 172.355, 211.302)), ('B', '275', 7, 'side-chain clash', (162.424, 172.355, 211.302)), ('B', '40', 8, 'Dihedral angle:CA:CB:CG:OD1', (178.48800000000003, 172.466, 207.84)), ('B', '41', 8, 'cablam Outlier', (181.8, 170.7, 208.0)), ('B', '503', 9, 'side-chain clash', (207.168, 226.419, 199.179)), ('B', '506', 9, 'side-chain clash', (207.168, 226.419, 199.179)), ('B', '328', 10, 'side-chain clash', (202.613, 240.047, 211.122)), ('B', '533', 10, 'side-chain clash', (202.613, 240.047, 211.122)), ('B', '477', 11, 'cablam Outlier', (196.3, 250.1, 230.3)), ('B', '479', 11, 'smoc Outlier', (191.85200000000003, 253.20899999999997, 226.859)), ('M', '114', 1, 'backbone clash\nside-chain clash', (199.646, 158.985, 224.476)), ('M', '115', 1, 'backbone clash', (194.857, 161.12, 223.913)), ('M', '117', 1, 'side-chain clash', (199.646, 158.985, 224.476)), ('M', '119', 1, 'side-chain clash', (208.76, 158.08, 228.976)), ('M', '121', 1, 'side-chain clash', (210.525, 155.524, 232.182)), ('M', '122', 1, 'side-chain clash', (215.374, 151.458, 221.597)), ('M', '124', 1, 'side-chain clash\nsmoc Outlier', (217.504, 155.805, 221.596)), ('M', '139', 1, 'smoc Outlier', (221.17299999999997, 160.575, 228.198)), ('M', '141', 1, 'Dihedral angle:CA:C\nsmoc Outlier', (214.911, 159.319, 226.39000000000001)), ('M', '142', 1, 'side-chain clash\nDihedral angle:N:CA', (211.19899999999998, 159.369, 227.156)), ('M', '145', 1, 'side-chain clash', (206.086, 159.002, 227.086)), ('M', '182', 1, 'side-chain clash', (215.475, 163.442, 223.596)), ('M', '202', 1, 'side-chain clash', (210.525, 155.524, 232.182)), ('M', '155', 2, 'side-chain clash', (219.277, 154.866, 238.428)), ('M', '156', 2, 'side-chain clash', (225.284, 157.163, 237.59)), ('M', '197', 2, 'side-chain clash', (224.561, 152.956, 239.4)), ('M', '198', 2, 'side-chain clash', (225.284, 157.163, 237.59)), ('M', '199', 2, 'side-chain clash', (219.277, 154.866, 238.428)), ('M', '14', 3, 'smoc Outlier', (189.54899999999998, 168.54399999999998, 222.965)), ('M', '16', 3, 'smoc Outlier', (185.198, 170.484, 218.85100000000003)), ('M', '17', 3, 'Dihedral angle:CB:CG:CD:OE1', (185.041, 171.983, 222.35500000000002)), ('M', '85', 3, 'smoc Outlier', (189.467, 172.49, 214.912)), ('M', '87', 3, 'Dihedral angle:CB:CG:CD:OE1', (194.126, 174.317, 212.48200000000003)), ('M', '40', 4, 'smoc Outlier', (192.065, 193.844, 218.911)), ('M', '56', 4, 'cablam CA Geom Outlier', (187.0, 196.9, 217.8)), ('M', '57', 4, 'cablam Outlier', (186.6, 193.8, 219.9)), ('M', '95', 4, 'smoc Outlier', (196.39000000000001, 194.43800000000002, 221.995)), ('M', '108', 5, 'backbone clash', (198.414, 181.53, 221.629)), ('M', '43', 5, 'smoc Outlier', (196.61899999999997, 185.029, 215.935)), ('M', '91', 5, 'backbone clash', (198.414, 181.53, 221.629)), ('M', '152', 6, 'side-chain clash', (215.12, 163.91, 231.925)), ('M', '183', 6, 'side-chain clash', (215.12, 163.91, 231.925)), ('M', '176', 7, 'Dihedral angle:CA:CB:CG:OD1', (199.33100000000002, 162.371, 217.132)), ('M', '177', 7, 'smoc Outlier', (199.71299999999997, 164.677, 220.137)), ('M', '127', 8, 'side-chain clash', (231.431, 155.267, 221.338)), ('M', '129', 8, 'Dihedral angle:CB:CG:CD:OE1', (234.767, 159.80100000000002, 221.752)), ('M', '34', 9, 'side-chain clash', (181.965, 203.772, 217.245)), ('M', '36', 9, 'side-chain clash', (181.965, 203.772, 217.245)), ('I', '145', 1, 'side-chain clash', (222.268, 164.579, 222.375)), ('I', '152', 1, 'Dihedral angle:CB:CG:CD:OE1\ncablam CA Geom Outlier', (221.99, 178.66, 216.67899999999997)), ('I', '153', 1, 'Ramachandran', (221.037, 176.959, 214.329)), ('I', '172', 1, 'side-chain clash', (221.415, 174.973, 221.66)), ('I', '179', 1, 'side-chain clash', (215.475, 163.442, 223.596)), ('I', '180', 1, 'side-chain clash', (221.415, 174.973, 221.66)), ('I', '182', 1, 'smoc Outlier', (221.31, 169.36200000000002, 220.665)), ('I', '183', 1, 'side-chain clash', (222.268, 164.579, 222.375)), ('I', '198', 1, 'side-chain clash', (215.469, 163.867, 223.535)), ('I', '215', 1, 'side-chain clash', (215.469, 163.867, 223.535)), ('I', '115', 2, 'backbone clash\nside-chain clash', (217.504, 155.805, 221.596)), ('I', '139', 2, 'side-chain clash', (212.578, 148.399, 216.433)), ('I', '174', 2, 'side-chain clash\nbackbone clash', (215.374, 151.458, 221.597)), ('I', '189', 2, 'side-chain clash', (212.578, 148.399, 216.433)), ('I', '91', 2, 'backbone clash\nside-chain clash', (217.504, 155.805, 221.596)), ('I', '38', 3, 'side-chain clash', (212.081, 195.591, 217.248)), ('I', '45', 3, 'smoc Outlier', (206.035, 190.976, 220.797)), ('I', '46', 3, 'Dihedral angle:CB:CG:CD:OE1', (207.21699999999998, 194.37800000000001, 222.05800000000002)), ('I', '48', 3, 'side-chain clash', (212.081, 195.591, 217.248)), ('I', '14', 4, 'smoc Outlier', (229.51399999999998, 193.5, 218.20899999999997)), ('I', '16', 4, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (229.09, 197.72299999999998, 214.30700000000002)), ('I', '85', 4, 'side-chain clash', (226.963, 199.843, 216.357)), ('I', '1', 5, 'smoc Outlier', (196.196, 196.58800000000002, 200.33800000000002)), ('I', '2', 5, 'Rotamer\nside-chain clash', (201.989, 199.031, 199.401)), ('I', '24', 5, 'smoc Outlier', (206.414, 199.546, 200.842)), ('I', '34', 6, 'smoc Outlier', (204.875, 202.503, 209.518)), ('I', '97', 6, 'smoc Outlier', (203.933, 196.647, 210.077)), ('I', '98', 6, 'smoc Outlier', (201.876, 199.42200000000003, 208.564)), ('I', '20', 7, 'side-chain clash', (217.642, 196.287, 212.529)), ('I', '83', 7, 'side-chain clash', (217.642, 196.287, 212.529)), ('I', '6', 8, 'Rotamer', (211.779, 193.61099999999993, 204.137)), ('I', '7', 8, 'cablam Outlier', (215.5, 194.0, 203.2))]
data['omega'] = [('H', ' 151 ', 'PRO', None, (208.216, 254.82399999999996, 217.258)), ('H', ' 153 ', 'PRO', None, (213.318, 256.703, 214.344)), ('I', ' 151 ', 'PRO', None, (226.635, 180.224, 217.131)), ('I', ' 153 ', 'PRO', None, (221.50200000000007, 178.34499999999997, 214.27200000000005)), ('L', '   8 ', 'PRO', None, (241.186, 252.78799999999995, 230.347)), ('L', ' 101 ', 'PRO', None, (232.745, 230.239, 224.014)), ('L', ' 147 ', 'PRO', None, (234.363, 271.656, 229.16800000000006)), ('M', '   8 ', 'PRO', None, (193.622, 182.00699999999998, 230.50300000000004)), ('M', ' 101 ', 'PRO', None, (201.929, 204.546, 223.962)), ('M', ' 147 ', 'PRO', None, (200.48000000000005, 163.15099999999998, 229.33400000000003))]
data['rama'] = [('H', ' 153 ', 'PRO', 0.17627616536357793, (213.783, 258.089, 214.395)), ('I', ' 153 ', 'PRO', 0.17724794184903353, (221.037, 176.959, 214.329))]
data['cablam'] = [('H', '7', 'SER', 'check CA trace,carbonyls, peptide', ' \nEE---', (219.3, 241.0, 203.3)), ('H', '152', 'GLU', 'check CA trace', 'bend\nBSS--', (212.9, 256.4, 216.8)), ('L', '57', 'ALA', ' alpha helix', 'turn\nETTTE', (248.1, 241.0, 219.7)), ('L', '106', 'GLN', ' beta sheet', ' \n----E', (233.4, 246.7, 227.2)), ('L', '56', 'TRP', 'check CA trace', 'turn\nEETTT', (247.6, 237.8, 217.6)), ('L', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (234.2, 229.4, 222.2)), ('A', '41', 'LYS', 'check CA trace,carbonyls, peptide', ' \n---S-', (252.9, 264.2, 208.0)), ('A', '332', 'ILE', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (260.6, 230.2, 193.1)), ('A', '334', 'ASN', 'check CA trace,carbonyls, peptide', ' \nS----', (261.0, 223.3, 193.7)), ('A', '378', 'LYS', ' beta sheet', ' \nEE---', (238.1, 222.9, 208.3)), ('A', '379', 'CYS', 'check CA trace,carbonyls, peptide', ' \nE---S', (241.6, 224.3, 209.3)), ('A', '419', 'ALA', ' alpha helix', 'helix\nSHHHH', (239.0, 208.5, 217.2)), ('A', '430', 'THR', ' beta sheet', ' \nS--EE', (246.9, 223.6, 214.5)), ('A', '446', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (232.1, 193.0, 193.5)), ('A', '477', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (238.6, 184.7, 230.4)), ('A', '522', 'ALA', 'check CA trace,carbonyls, peptide', ' \n---S-', (264.5, 227.4, 207.2)), ('A', '523', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (262.2, 224.8, 205.6)), ('A', '333', 'THR', 'check CA trace', ' \n-S---', (260.9, 226.6, 191.9)), ('A', '518', 'LEU', 'check CA trace', ' \nE--S-', (260.0, 224.7, 216.9)), ('A', '519', 'HIS', 'check CA trace', 'bend\n--S--', (263.4, 225.9, 215.6)), ('B', '41', 'LYS', 'check CA trace,carbonyls, peptide', ' \n---S-', (181.8, 170.7, 208.0)), ('B', '332', 'ILE', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (174.2, 204.6, 193.1)), ('B', '334', 'ASN', 'check CA trace,carbonyls, peptide', ' \nS----', (173.8, 211.6, 193.6)), ('B', '378', 'LYS', ' beta sheet', ' \nEE---', (196.7, 211.8, 208.3)), ('B', '379', 'CYS', 'check CA trace,carbonyls, peptide', ' \nE---S', (193.2, 210.5, 209.3)), ('B', '419', 'ALA', ' alpha helix', 'helix\nSHHHH', (195.8, 226.3, 217.2)), ('B', '430', 'THR', ' beta sheet', ' \nS--EE', (188.0, 211.2, 214.5)), ('B', '446', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (202.8, 241.8, 193.4)), ('B', '477', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (196.3, 250.1, 230.3)), ('B', '522', 'ALA', 'check CA trace,carbonyls, peptide', ' \n---S-', (170.3, 207.5, 207.2)), ('B', '523', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (172.6, 210.0, 205.6)), ('B', '333', 'THR', 'check CA trace', ' \n-S---', (174.0, 208.2, 191.9)), ('B', '518', 'LEU', 'check CA trace', ' \nE--S-', (174.8, 210.1, 216.9)), ('B', '519', 'HIS', 'check CA trace', 'bend\n--S--', (171.4, 209.0, 215.6)), ('M', '57', 'ALA', ' alpha helix', 'turn\nETTTE', (186.6, 193.8, 219.9)), ('M', '106', 'GLN', ' beta sheet', ' \n----E', (201.4, 188.1, 227.2)), ('M', '56', 'TRP', 'check CA trace', 'turn\nEETTT', (187.0, 196.9, 217.8)), ('M', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (200.5, 205.4, 222.2)), ('I', '7', 'SER', 'check CA trace,carbonyls, peptide', ' \nEE---', (215.5, 194.0, 203.2)), ('I', '152', 'GLU', 'check CA trace', 'bend\nBSS--', (222.0, 178.7, 216.7))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11648/7a5r/Model_validation_1/validation_cootdata/molprobity_probe7a5r_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

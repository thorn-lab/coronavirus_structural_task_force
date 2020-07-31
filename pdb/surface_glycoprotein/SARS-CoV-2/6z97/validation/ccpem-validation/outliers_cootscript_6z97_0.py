
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
data['clusters'] = []
data['smoc'] = []
data['jpred'] = []
data['probe'] = [(' C 382  VAL HG11', ' C 387  LEU HD21', -1.013, (204.343, 228.712, 188.958)), (' A 382  VAL HG11', ' A 387  LEU HD21', -0.867, (236.873, 238.193, 188.61)), (' A  29  THR HG23', ' A  62  VAL HG23', -0.817, (204.731, 270.714, 207.592)), (' C 117  LEU HD21', ' C 231  ILE HD13', -0.726, (209.773, 188.395, 188.636)), (' C 722  VAL HG22', ' C1065  VAL HG22', -0.721, (223.451, 203.245, 262.19)), (' B 189  LEU HD11', ' B 217  PRO  HG2', -0.716, (277.984, 231.586, 210.562)), (' B 597  VAL HG12', ' B 599  THR HG23', -0.706, (255.216, 216.636, 228.335)), (' A 722  VAL HG22', ' A1065  VAL HG22', -0.703, (207.829, 235.279, 263.022)), (' A1105  THR HG22', ' A1112  PRO  HA ', -0.702, (222.671, 240.735, 285.066)), (' A 231  ILE HD12', ' A 233  ILE  HB ', -0.65, (204.956, 256.321, 185.97)), (' B 382  VAL HG11', ' B 387  LEU HD21', -0.649, (231.398, 200.02, 177.507)), (' B 100  ILE HG22', ' B 242  LEU  HB2', -0.644, (283.996, 229.301, 194.306)), (' B 961  THR HG21', ' C 765  ARG HH22', -0.642, (238.616, 227.159, 222.672)), (' B 811  LYS  O  ', ' B 813  SER  N  ', -0.642, (245.281, 253.074, 248.939)), (' C1105  THR HG22', ' C1112  PRO  HA ', -0.632, (212.102, 212.666, 285.456)), (' B 908  GLY  O  ', ' B1038  LYS  NZ ', -0.628, (230.876, 225.747, 269.376)), (' A 195  LYS  HD3', ' A 197  ILE HD13', -0.626, (207.491, 252.385, 197.167)), (' A 326  ILE HD12', ' A 539  VAL HG21', -0.625, (240.046, 257.225, 203.465)), (' B 599  THR HG22', ' B 608  VAL HG12', -0.621, (257.598, 217.095, 228.266)), (' B 276  LEU  HB3', ' B 289  VAL HG23', -0.612, (256.386, 226.898, 217.327)), (' A  41  LYS  HD3', ' C 520  ALA  HB2', -0.612, (197.878, 242.762, 198.271)), (' B  31  SER  OG ', ' B  56  LEU HD21', -0.611, (269.853, 223.178, 208.717)), (' C 752  LEU HD21', ' C 990  GLU  HG2', -0.606, (234.612, 219.927, 199.878)), (' B 537  LYS  O  ', ' B 539  VAL HG23', -0.598, (245.408, 193.264, 208.523)), (' A 193  VAL HG23', ' A 223  LEU HD23', -0.596, (199.058, 258.81, 203.007)), (' C 130  VAL HG11', ' C 231  ILE HG22', -0.593, (212.093, 187.301, 185.463)), (' C 201  PHE  HB2', ' C 231  ILE HD11', -0.593, (210.763, 189.738, 190.793)), (' A 328  ARG  NH1', ' A 578  ASP  OD2', -0.585, (248.128, 257.061, 198.926)), (' A 391  CYS  HB3', ' A 522  ALA  HB1', -0.584, (246.087, 244.606, 191.948)), (' A 736  VAL HG11', ' A1004  LEU HD21', -0.581, (209.485, 222.029, 220.496)), (' C 331  ASN  N  ', ' C 331  ASN  OD1', -0.578, (183.844, 233.472, 191.071)), (' C 642  VAL HG22', ' C 651  ILE HG12', -0.577, (187.336, 206.112, 227.776)), (' A  94  SER  O  ', ' A 189  LEU HD12', -0.577, (194.555, 267.591, 205.017)), (' C 382  VAL HG11', ' C 387  LEU  CD2', -0.573, (203.521, 228.653, 189.184)), (' A 117  LEU HD21', ' A 231  ILE HG21', -0.569, (201.866, 256.038, 187.15)), (' B 597  VAL HG12', ' B 599  THR  CG2', -0.568, (255.346, 216.877, 227.905)), (' A 552  LEU  HB3', ' A 585  LEU HD13', -0.568, (245.875, 255.465, 206.439)), (' A 332  ILE HG22', ' A 362  VAL HG23', -0.566, (247.69, 250.448, 183.488)), (' B 726  ILE HG12', ' B1061  VAL HG22', -0.564, (241.568, 233.782, 248.014)), (' A 961  THR HG21', ' B 762  GLN  CD ', -0.563, (214.832, 233.788, 221.829)), (' A 395  VAL HG22', ' A 515  PHE  HD1', -0.563, (243.328, 237.966, 186.428)), (' B 128  ILE  CG2', ' B 229  LEU HD21', -0.561, (266.101, 234.108, 187.241)), (' C 858  LEU HD23', ' C 959  LEU HD22', -0.555, (230.23, 207.764, 222.995)), (' B 705  VAL HG12', ' C 895  GLN  HB3', -0.551, (243.369, 205.811, 269.413)), (' B 722  VAL HG22', ' B1065  VAL HG22', -0.547, (243.887, 232.773, 261.689)), (' A 612  TYR  HE1', ' A 651  ILE HD12', -0.545, (225.815, 261.043, 224.513)), (' A1086  LYS  HD2', ' A1122  VAL HG11', -0.544, (239.581, 229.574, 294.107)), (' B 128  ILE HG21', ' B 229  LEU HD21', -0.541, (265.989, 234.38, 187.631)), (' B 725  GLU  OE1', ' B1028  LYS  NZ ', -0.54, (235.437, 227.064, 253.023)), (' B 599  THR HG22', ' B 608  VAL  CG1', -0.533, (257.546, 216.332, 228.026)), (' A 382  VAL HG11', ' A 387  LEU  CD2', -0.533, (236.707, 239.447, 188.635)), (' B 335  LEU HD23', ' B 336  CYS  N  ', -0.532, (230.435, 185.48, 180.77)), (' B 727  LEU HD11', ' B1028  LYS  HD2', -0.525, (233.648, 229.284, 251.099)), (' C 326  ILE HD11', ' C 534  VAL HG12', -0.524, (183.536, 221.95, 203.828)), (' A 538  CYS  CB ', ' A 551  VAL HG12', -0.523, (238.043, 257.586, 211.007)), (' A 330  PRO  HB2', ' A 332  ILE HD13', -0.523, (250.006, 250.719, 189.333)), (' C 229  LEU  HB3', ' C 231  ILE HG23', -0.522, (213.565, 187.374, 188.536)), (' C 332  ILE HD12', ' C 361  CYS  C  ', -0.52, (190.414, 233.84, 184.892)), (' A1114  ILE  O  ', ' A1119  ASN  ND2', -0.519, (225.066, 236.052, 291.015)), (' B1126  CYS  CB ', ' B1132  ILE HD13', -0.517, (228.751, 201.23, 288.995)), (' A  34  ARG  O  ', ' A  56  LEU HD23', -0.515, (204.279, 261.478, 209.256)), (' B1123  SER  OG ', ' C 914  ASN  ND2', -0.506, (221.39, 208.117, 285.059)), (' A 391  CYS  HA ', ' A 524  VAL  O  ', -0.505, (244.526, 244.694, 189.507)), (' B 811  LYS  CB ', ' B 812  PRO  HD2', -0.503, (247.785, 251.043, 250.718)), (' B1126  CYS  HB2', ' B1132  ILE HG21', -0.5, (230.11, 200.237, 288.717)), (' A 216  LEU  O  ', ' A 216  LEU HD12', -0.498, (199.397, 269.001, 211.715)), (' A 329  PHE  HD1', ' A 391  CYS  SG ', -0.498, (244.192, 248.444, 191.534)), (' A 537  LYS  O  ', ' A 539  VAL HG13', -0.497, (239.176, 259.321, 207.03)), (' B 193  VAL HG23', ' B 223  LEU HD12', -0.494, (266.509, 231.016, 203.873)), (' A 902  MET  HE1', ' A1049  LEU HD13', -0.49, (209.907, 232.728, 269.647)), (' C 393  THR HG21', ' C 519  HIS  NE2', -0.487, (200.814, 240.716, 195.073)), (' C 127  VAL HG23', ' C 171  VAL HG22', -0.486, (213.171, 175.631, 184.553)), (' A 749  CYS  HB2', ' A 977  LEU HD21', -0.485, (207.067, 219.848, 205.932)), (' B 236  THR  O  ', ' B 236  THR HG22', -0.484, (265.855, 216.532, 190.523)), (' C 358  ILE  HB ', ' C 395  VAL  HB ', -0.482, (198.384, 237.705, 183.484)), (' B1126  CYS  HB2', ' B1132  ILE HD13', -0.482, (228.999, 201.16, 288.992)), (' C 520  ALA  HB1', ' C 521  PRO  HD2', -0.481, (195.209, 242.024, 197.599)), (' A1129  VAL HG13', ' B 917  TYR  HB3', -0.481, (242.123, 235.865, 282.32)), (' A 196  ASN  C  ', ' A 197  ILE HD12', -0.48, (209.044, 253.312, 195.105)), (' B  30  ASN  OD1', ' B  31  SER  N  ', -0.48, (272.145, 221.026, 212.917)), (' B  57  PRO  O  ', ' B  60  SER  OG ', -0.48, (266.401, 219.474, 210.208)), (' C 811  LYS  CB ', ' C 812  PRO  HD2', -0.477, (236.944, 190.566, 249.467)), (' C 201  PHE  HE2', ' C 203  ILE HD11', -0.475, (208.531, 184.988, 193.606)), (' B 297  SER  O  ', ' B 301  CYS  SG ', -0.472, (254.929, 221.761, 219.158)), (' B 541  PHE  CZ ', ' B 587  ILE HD13', -0.472, (235.649, 195.254, 207.988)), (' C 611  LEU HD22', ' C 666  ILE HG23', -0.472, (197.239, 210.812, 233.008)), (' A 612  TYR  CE1', ' A 620  VAL HG21', -0.471, (226.781, 260.029, 222.731)), (' C 736  VAL HG22', ' C 858  LEU  HG ', -0.47, (233.091, 209.654, 222.01)), (' B1114  ILE  O  ', ' B1119  ASN  ND2', -0.47, (236.581, 217.523, 290.569)), (' A1093  GLY  O  ', ' A1107  ARG  NH2', -0.47, (229.996, 235.068, 279.377)), (' C  28  TYR  HB3', ' C  61  ASN  OD1', -0.469, (189.052, 187.304, 207.635)), (' C  29  THR HG22', ' C  30  ASN  N  ', -0.468, (192.817, 183.028, 210.593)), (' A1011  GLN  OE1', ' A1014  ARG  NH1', -0.468, (213.3, 228.526, 229.488)), (' B 324  GLU  OE2', ' B 534  VAL HG21', -0.468, (247.727, 192.069, 204.474)), (' C 384  PRO  HA ', ' C 387  LEU  HG ', -0.467, (202.841, 227.131, 187.04)), (' A  37  TYR  HB2', ' A 223  LEU  O  ', -0.467, (198.898, 253.773, 204.184)), (' B 201  PHE  HB3', ' B 229  LEU  HB2', -0.466, (262.436, 232.597, 190.146)), (' B 905  ARG  HD2', ' B1049  LEU  O  ', -0.465, (234.992, 232.45, 266.958)), (' C1114  ILE  O  ', ' C1119  ASN  ND2', -0.465, (215.062, 216.586, 291.172)), (' A  35  GLY  HA3', ' A  56  LEU  HB3', -0.465, (204.671, 260.427, 207.939)), (' A 189  LEU  HB2', ' A 210  ILE HD13', -0.464, (191.96, 268.661, 208.068)), (' C  31  SER  HB3', ' C  62  VAL HG13', -0.461, (196.537, 186.773, 208.452)), (' B 205  SER  HB3', ' B 226  LEU HD12', -0.461, (268.627, 236.773, 199.654)), (' B1116  THR  OG1', ' B1118  ASP  OD1', -0.461, (233.085, 219.034, 292.709)), (' C1088  HIS  CE1', ' C1122  VAL HG22', -0.461, (213.903, 228.661, 293.575)), (' C 560  LEU HD13', ' C 562  PHE  CE2', -0.459, (192.538, 248.498, 205.42)), (' B 858  LEU HD23', ' B 959  LEU HD22', -0.458, (235.298, 238.155, 222.706)), (' A  31  SER  HB2', ' A  56  LEU HD21', -0.457, (204.956, 264.766, 209.033)), (' B 376  THR  HB ', ' B 435  ALA  HB3', -0.457, (236.723, 194.786, 162.743)), (' B 118  LEU HD12', ' B 135  PHE  HE2', -0.456, (274.43, 228.308, 183.493)), (' A 736  VAL HG13', ' A 858  LEU HD23', -0.454, (206.436, 222.931, 220.889)), (' A 284  THR  O  ', ' A 286  THR HG23', -0.454, (194.773, 250.442, 216.002)), (' B 595  VAL HG22', ' B 612  TYR  CD2', -0.454, (251.007, 207.653, 221.471)), (' B  90  VAL HG21', ' B 238  PHE  CE2', -0.453, (269.496, 221.984, 195.693)), (' C  83  VAL HG11', ' C 237  ARG  NH2', -0.452, (193.38, 188.649, 187.252)), (' B 589  PRO  HG2', ' C 855  PHE  CB ', -0.451, (236.485, 199.568, 216.048)), (' C  86  PHE  CD2', ' C  86  PHE  O  ', -0.45, (201.652, 193.41, 194.068)), (' C 715  PRO  HA ', ' C1072  GLU  HA ', -0.45, (207.394, 208.265, 275.174)), (' A  34  ARG  HD2', ' A 216  LEU HD13', -0.449, (199.642, 266.256, 210.401)), (' C 382  VAL HG12', ' C 383  SER  N  ', -0.449, (205.468, 226.988, 189.426)), (' B 722  VAL  O  ', ' B 934  ILE HD11', -0.448, (247.009, 230.187, 257.606)), (' A 595  VAL HG22', ' A 612  TYR  CD2', -0.447, (225.935, 256.194, 222.82)), (' A 303  LEU HD12', ' A 308  VAL HG22', -0.447, (210.761, 249.367, 227.215)), (' B 720  ILE HG13', ' B 923  ILE HG23', -0.446, (245.219, 231.395, 269.994)), (' C 531  THR HG22', ' C 532  ASN  N  ', -0.445, (181.881, 222.383, 197.845)), (' A 393  THR HG21', ' A 520  ALA  HB3', -0.445, (249.546, 239.671, 194.843)), (' B 736  VAL HG13', ' B 858  LEU HD12', -0.445, (230.953, 239.656, 220.504)), (' A 365  TYR  HH ', ' A 392  PHE  HE2', -0.444, (241.667, 242.42, 186.926)), (' A 193  VAL HG23', ' A 223  LEU  CD2', -0.444, (199.331, 258.638, 203.689)), (' C1081  ILE HD11', ' C1137  VAL HG22', -0.443, (210.666, 222.957, 293.074)), (' C 905  ARG  HD2', ' C1049  LEU  O  ', -0.443, (227.577, 210.155, 266.442)), (' C 908  GLY  O  ', ' C1038  LYS  NZ ', -0.443, (224.185, 217.435, 269.382)), (' A 391  CYS  CB ', ' A 522  ALA  HB1', -0.443, (245.912, 244.834, 192.397)), (' A 676  THR  HA ', ' A 690  GLN  HA ', -0.443, (213.033, 266.71, 240.721)), (' B 849  LEU  HB2', ' B 852  ALA  HB3', -0.442, (243.815, 241.876, 220.066)), (' A 612  TYR  CZ ', ' A 620  VAL HG21', -0.442, (226.396, 259.602, 222.656)), (' A 618  THR HG23', ' A 619  GLU  N  ', -0.441, (235.189, 262.109, 221.445)), (' C 320  VAL HG12', ' C 321  GLN  N  ', -0.441, (190.569, 214.381, 212.295)), (' A 395  VAL  HA ', ' A 514  SER  O  ', -0.44, (244.984, 235.321, 185.806)), (' A 376  THR  HB ', ' A 435  ALA  HB3', -0.439, (231.802, 230.066, 175.197)), (' C 726  ILE HG13', ' C1061  VAL HG22', -0.439, (224.566, 204.083, 248.564)), (' C 143  VAL  O  ', ' C 143  VAL HG22', -0.438, (194.947, 164.354, 190.264)), (' B 532  ASN  OD1', ' B 533  LEU  N  ', -0.438, (244.018, 186.097, 201.298)), (' C 224  GLU  N  ', ' C 224  GLU  OE1', -0.437, (213.268, 181.797, 206.813)), (' C  86  PHE  HD2', ' C  86  PHE  O  ', -0.437, (201.465, 193.935, 194.014)), (' C 719  THR HG23', ' C1070  ALA  HB2', -0.437, (212.146, 203.044, 269.464)), (' C 130  VAL HG11', ' C 231  ILE  CG2', -0.437, (211.776, 187.473, 186.383)), (' A 749  CYS  CB ', ' A 977  LEU HD21', -0.435, (207.071, 220.117, 206.531)), (' B 749  CYS  CB ', ' B 977  LEU HD21', -0.435, (227.457, 240.634, 206.184)), (' C  53  ASP  HB2', ' C  55  PHE  CE1', -0.433, (209.705, 195.341, 207.679)), (' C 553  THR HG22', ' C 554  GLU  N  ', -0.433, (182.178, 230.323, 213.032)), (' C 736  VAL HG11', ' C1004  LEU HD21', -0.433, (232.638, 212.773, 219.882)), (' A  57  PRO  HG3', ' A 273  ARG  HE ', -0.432, (212.959, 259.411, 208.966)), (' B 122  ASN  O  ', ' B 124  THR  N  ', -0.431, (280.238, 242.454, 188.898)), (' C 676  THR  HA ', ' C 690  GLN  HA ', -0.431, (191.854, 193.308, 240.769)), (' C 986  PRO  N  ', ' C 987  PRO  CD ', -0.431, (234.259, 215.478, 192.447)), (' A 551  VAL HG22', ' A 588  THR  O  ', -0.43, (240.33, 253.939, 212.684)), (' A 852  ALA  O  ', ' A 856  ASN  ND2', -0.43, (201.412, 227.911, 218.49)), (' B 705  VAL  O  ', ' B 707  TYR  N  ', -0.43, (244.021, 202.069, 269.144)), (' C 401  VAL HG22', ' C 509  ARG  HG2', -0.429, (210.187, 237.223, 168.348)), (' A 612  TYR  CE1', ' A 651  ILE HD12', -0.429, (226.067, 260.963, 224.509)), (' C 382  VAL  CG1', ' C 387  LEU HD21', -0.427, (204.107, 228.533, 189.2)), (' C 734  THR HG21', ' C1007  TYR  OH ', -0.427, (231.322, 210.24, 226.083)), (' B1081  ILE  HA ', ' B1133  VAL  O  ', -0.427, (233.893, 204.189, 289.691)), (' A1006  THR  O  ', ' A1010  GLN  HG2', -0.426, (218.245, 227.446, 225.013)), (' C 354  ASN  O  ', ' C 398  ASP  HA ', -0.424, (206.198, 242.176, 177.759)), (' A 520  ALA  O  ', ' A 522  ALA  N  ', -0.423, (249.52, 243.491, 195.347)), (' B 598  ILE HG23', ' B 664  ILE HG21', -0.422, (252.785, 214.109, 233.852)), (' A 787  GLN  OE1', ' C 703  ASN  ND2', -0.421, (200.09, 211.341, 263.497)), (' C 802  PHE  HD2', ' C 805  ILE HD11', -0.42, (230.56, 199.339, 262.295)), (' A 309  GLU  O  ', ' A 313  TYR  OH ', -0.42, (212.405, 249.53, 232.005)), (' C1029  MET  HE2', ' C1053  PRO  HB3', -0.419, (231.966, 208.562, 253.738)), (' B  65  PHE  CE1', ' B  84  LEU HD11', -0.419, (276.222, 219.855, 197.304)), (' C 533  LEU HD11', ' C 585  LEU HD11', -0.418, (184.195, 229.241, 204.269)), (' A 551  VAL HG22', ' A 588  THR  HB ', -0.418, (241.302, 254.487, 213.188)), (' C 927  PHE  HE1', ' C1065  VAL HG21', -0.418, (225.685, 202.227, 263.537)), (' B 326  ILE HD11', ' B 541  PHE  HB3', -0.418, (240.106, 193.594, 204.814)), (' C 376  THR  HB ', ' C 435  ALA  HB3', -0.418, (213.42, 230.195, 174.977)), (' B 749  CYS  HB2', ' B 977  LEU HD21', -0.417, (227.615, 240.657, 205.702)), (' A1093  GLY  HA3', ' A1105  THR  O  ', -0.417, (226.169, 235.994, 282.356)), (' A1028  LYS  O  ', ' A1032  CYS  CB ', -0.417, (213.989, 225.789, 257.345)), (' A 290  ASP  HB3', ' A 293  LEU  HB2', -0.417, (210.833, 258.828, 216.184)), (' B 382  VAL HG23', ' B 430  THR HG23', -0.416, (229.542, 203.675, 175.269)), (' C 329  PHE  HD2', ' C 391  CYS  SG ', -0.416, (191.732, 231.08, 192.716)), (' C 329  PHE  CD2', ' C 391  CYS  SG ', -0.416, (192.054, 230.818, 192.829)), (' A 569  ILE HD13', ' B 849  LEU  HG ', -0.415, (245.019, 239.081, 220.248)), (' A 196  ASN  O  ', ' A 197  ILE HD12', -0.415, (209.352, 253.696, 194.771)), (' A 900  MET  HB2', ' A 900  MET  HE3', -0.414, (204.866, 224.707, 278.29)), (' A 866  THR  H  ', ' A 866  THR  HG1', -0.413, (197.046, 218.698, 244.191)), (' B 130  VAL  HB ', ' B 233  ILE HD11', -0.413, (264.226, 229.614, 182.225)), (' B 915  VAL  O  ', ' B 919  ASN  ND2', -0.413, (245.194, 229.122, 278.594)), (' B 984  LEU  HB2', ' B 989  ALA  HB2', -0.413, (228.592, 237.842, 196.132)), (' B1116  THR HG22', ' B1138  TYR  HD2', -0.413, (235.852, 217.471, 296.44)), (' A1088  HIS  CE1', ' A1122  VAL HG22', -0.413, (236.234, 230.628, 293.124)), (' A 900  MET  HE1', ' C1077  THR HG23', -0.411, (203.705, 222.347, 280.966)), (' A 613  GLN  O  ', ' A 615  VAL HG13', -0.409, (231.662, 254.101, 224.684)), (' C 749  CYS  HB2', ' C 977  LEU HD21', -0.408, (235.051, 212.007, 205.509)), (' A 585  LEU  O  ', ' A 585  LEU HD12', -0.408, (247.725, 252.661, 207.231)), (' C 391  CYS  HA ', ' C 524  VAL  O  ', -0.408, (195.105, 233.295, 190.266)), (' C  45  SER  O  ', ' C  47  VAL HG23', -0.408, (222.313, 191.046, 220.034)), (' B1028  LYS  O  ', ' B1032  CYS  CB ', -0.408, (231.952, 231.867, 257.389)), (' A 801  ASN  ND2', ' A1312  NAG  O7 ', -0.408, (194.479, 236.433, 267.794)), (' B  48  LEU HD23', ' B 278  LYS  HA ', -0.407, (255.515, 234.208, 218.591)), (' C1103  PHE  HZ ', ' C1312  NAG  H62', -0.407, (207.488, 210.087, 291.945)), (' C 902  MET  HE1', ' C1049  LEU HD13', -0.406, (224.397, 206.246, 269.037)), (' A 106  PHE  HB3', ' A 235  ILE  CD1', -0.406, (205.52, 261.358, 189.134)), (' A 215  ASP  HA ', ' A 266  TYR  OH ', -0.406, (197.734, 273.369, 207.925)), (' A 519  HIS  CD2', ' A 546  LEU HD21', -0.405, (243.162, 241.398, 199.719)), (' B 902  MET  HE1', ' B1049  LEU HD13', -0.404, (240.549, 231.975, 269.102)), (' C1118  ASP  O  ', ' C1118  ASP  OD1', -0.404, (221.201, 221.38, 290.359)), (' C 770  ILE  O  ', ' C 774  GLN  HG2', -0.404, (234.751, 214.665, 234.955)), (' B  86  PHE  CD2', ' B  86  PHE  O  ', -0.404, (264.125, 220.952, 194.494)), (' C 118  LEU  HG ', ' C 120  VAL HG23', -0.403, (205.546, 178.459, 186.015)), (' B 709  ASN  N  ', ' B 709  ASN  OD1', -0.403, (239.91, 198.546, 276.352)), (' C 706  ALA  CB ', ' C1311  NAG  H5 ', -0.403, (196.089, 213.182, 273.402)), (' B 543  PHE  O  ', ' B 544  ASN  C  ', -0.403, (231.675, 193.999, 199.076)), (' B 360  ASN  HA ', ' B 523  THR  HB ', -0.402, (221.905, 189.332, 185.264)), (' A 538  CYS  HB3', ' A 551  VAL HG12', -0.402, (237.377, 257.552, 211.461)), (' A1141  LEU  HG ', ' A1145  LEU HD13', -0.402, (227.741, 226.409, 304.964)), (' A1028  LYS  O  ', ' A1032  CYS  HB3', -0.401, (213.598, 226.005, 257.665)), (' B  34  ARG  NH1', ' B 191  GLU  OE2', -0.401, (272.148, 231.174, 210.061)), (' B 384  PRO  HA ', ' B 387  LEU HD12', -0.401, (234.61, 197.461, 177.579)), (' B  86  PHE  O  ', ' B  87  ASN  C  ', -0.401, (263.272, 219.22, 195.754)), (' B 335  LEU HD23', ' B 336  CYS  H  ', -0.401, (230.509, 185.585, 181.28)), (' B 612  TYR  HE1', ' B 651  ILE HD12', -0.4, (255.418, 205.502, 223.429)), (' A 104  TRP  HB3', ' A 106  PHE  CE1', -0.4, (200.129, 263.39, 191.583)), (' C 320  VAL HG12', ' C 321  GLN  H  ', -0.4, (190.061, 214.413, 212.233))]
data['cbeta'] = []
data['rota'] = [('A', ' 538 ', 'CYS', 0.015466413178673408, (237.313, 257.7550000000001, 209.219)), ('A', ' 615 ', 'VAL', 0.0846149553047036, (233.867, 256.217, 225.06399999999996)), ('A', ' 723 ', 'THR', 0.11257800614351905, (210.711, 238.262, 258.119)), ('A', ' 866 ', 'THR', 0.07992409348480381, (197.38799999999995, 220.524, 243.10199999999998)), ('A', ' 878 ', 'LEU', 0.0, (202.13899999999995, 224.254, 260.496)), ('A', '1133 ', 'VAL', 0.07801268539543511, (239.3370000000001, 242.86499999999995, 289.358)), ('B', ' 229 ', 'LEU', 0.24062006505238895, (261.301, 234.641, 189.263)), ('B', ' 289 ', 'VAL', 0.003127019590465352, (259.253, 225.747, 217.266)), ('B', ' 301 ', 'CYS', 0.0, (252.43800000000002, 224.15199999999996, 219.272)), ('B', ' 302 ', 'THR', 0.25077806074675546, (249.269, 222.531, 220.618)), ('B', ' 603 ', 'ASN', 0.06747038162306661, (261.29, 225.907, 233.623)), ('B', ' 723 ', 'THR', 0.008087669993983582, (244.21200000000007, 228.66, 256.906)), ('B', '1094 ', 'VAL', 0.06215589564197076, (235.766, 212.53299999999993, 281.392)), ('B', '1132 ', 'ILE', 0.24361072159345, (232.755, 201.221, 286.429)), ('C', ' 331 ', 'ASN', 0.0, (184.066, 232.867, 189.465)), ('C', ' 515 ', 'PHE', 0.2221876892734011, (203.293, 236.801, 188.858)), ('C', ' 517 ', 'LEU', 0.14826978349592798, (202.25500000000005, 235.316, 194.891)), ('C', ' 738 ', 'CYS', 0.11299273141627969, (236.15399999999994, 214.576, 217.18699999999998))]
data['omega'] = [('A', ' 123 ', 'ALA', None, (184.814, 267.30099999999993, 190.61)), ('B', ' 815 ', 'ARG', None, (243.03700000000015, 249.18799999999996, 251.23699999999997))]
data['rama'] = []
data['cablam'] = [('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (212.3, 258.8, 197.5)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (210.3, 264.1, 185.3)), ('A', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nS-S--', (205.4, 268.7, 179.9)), ('A', '214', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (196.4, 277.0, 210.9)), ('A', '218', 'GLN', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (198.0, 266.9, 216.2)), ('A', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (253.4, 203.2, 166.0)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (248.4, 198.1, 166.2)), ('A', '521', 'PRO', ' beta sheet', 'bend\nSSS--', (251.8, 243.3, 195.6)), ('A', '527', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (239.2, 251.2, 185.4)), ('A', '544', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (244.3, 248.0, 195.4)), ('A', '617', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\n--TTT', (233.3, 262.6, 226.3)), ('A', '618', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTT-', (234.8, 264.0, 223.0)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (225.3, 252.3, 235.9)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (228.7, 250.9, 236.7)), ('A', '745', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nSTT-H', (201.0, 218.1, 209.6)), ('A', '758', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nG-TTT', (217.2, 211.0, 217.1)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (198.4, 228.8, 272.3)), ('A', '987', 'PRO', 'check CA trace,carbonyls, peptide', 'helix\n-HHHH', (212.8, 218.0, 193.8)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTSSSS', (216.7, 231.8, 258.6)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (205.5, 227.6, 242.0)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSS', (240.7, 235.2, 298.1)), ('A', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (227.5, 231.1, 281.9)), ('A', '1098', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (226.8, 249.5, 286.7)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'beta bridge\nTTB--', (219.8, 239.9, 277.9)), ('A', '1123', 'SER', 'check CA trace,carbonyls, peptide', ' \nEE-S-', (240.2, 228.4, 288.0)), ('A', '34', 'ARG', 'check CA trace', ' \n-S--B', (201.5, 261.4, 210.9)), ('A', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (197.9, 273.6, 210.0)), ('A', '220', 'PHE', 'check CA trace', ' \nS---B', (197.6, 259.9, 214.8)), ('A', '293', 'LEU', 'check CA trace', 'turn\nTTTSH', (213.4, 259.5, 216.9)), ('A', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (212.6, 251.7, 235.2)), ('A', '520', 'ALA', 'check CA trace', 'bend\n-SSS-', (249.6, 240.9, 197.6)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (236.0, 251.6, 206.6)), ('B', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-SS', (266.4, 219.9, 194.6)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (261.4, 220.1, 197.3)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (266.6, 218.8, 185.0)), ('B', '113', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (267.4, 220.9, 174.7)), ('B', '231', 'ILE', ' beta sheet', 'turn\nETT--', (259.7, 231.5, 185.1)), ('B', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (210.2, 189.4, 138.8)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (211.7, 194.6, 134.1)), ('B', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (214.3, 200.5, 184.8)), ('B', '527', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE----', (234.7, 190.1, 186.7)), ('B', '528', 'LYS', ' beta sheet', ' \n-----', (235.8, 192.2, 189.6)), ('B', '544', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (231.2, 192.3, 198.8)), ('B', '545', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (229.6, 195.7, 199.2)), ('B', '570', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (225.1, 200.6, 217.6)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (248.3, 209.4, 235.0)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (245.5, 207.1, 235.9)), ('B', '814', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (241.3, 250.9, 251.2)), ('B', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (229.2, 236.7, 261.1)), ('B', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nSS---', (231.0, 230.7, 264.6)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (235.6, 226.6, 258.1)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (236.7, 238.4, 241.3)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (228.8, 204.4, 298.1)), ('B', '1098', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (247.5, 209.3, 285.7)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (242.3, 220.1, 277.0)), ('B', '1126', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nEETTT', (227.3, 200.4, 289.8)), ('B', '34', 'ARG', 'check CA trace', ' \n-S--E', (268.5, 227.9, 210.9)), ('B', '112', 'SER', 'check CA trace', 'bend\nSSSSS', (270.8, 221.9, 176.2)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (239.7, 199.4, 208.0)), ('B', '797', 'PHE', 'check CA trace', 'bend\n--STT', (242.9, 244.0, 271.0)), ('B', '811', 'LYS', 'check CA trace', 'bend\nTTSSS', (248.0, 252.9, 251.0)), ('B', '812', 'PRO', 'check CA trace', 'bend\nTSSSS', (246.1, 251.9, 247.9)), ('C', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (221.0, 189.5, 205.6)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (202.4, 196.0, 197.6)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (200.1, 192.8, 185.0)), ('C', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nS-SSS', (197.6, 187.2, 178.7)), ('C', '218', 'GLN', 'check CA trace,carbonyls, peptide', ' \n---S-', (199.2, 179.9, 216.3)), ('C', '293', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nTTS-H', (198.7, 197.0, 217.1)), ('C', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (225.5, 261.3, 165.3)), ('C', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (232.3, 259.1, 165.1)), ('C', '517', 'LEU', 'check CA trace,carbonyls, peptide', ' \n---SS', (202.3, 235.3, 194.9)), ('C', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (199.7, 238.9, 199.5)), ('C', '527', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (191.4, 225.7, 185.9)), ('C', '600', 'PRO', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (201.0, 198.3, 235.6)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (198.7, 210.9, 236.4)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (198.4, 214.5, 237.4)), ('C', '756', 'TYR', 'check CA trace,carbonyls, peptide', 'helix-3\nGGGTT', (235.2, 224.9, 210.6)), ('C', '812', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nSSSSS', (238.5, 190.6, 246.6)), ('C', '813', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (240.0, 194.1, 247.3)), ('C', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nSS---', (228.1, 214.8, 264.5)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (221.7, 212.8, 258.3)), ('C', '1045', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSSE', (215.2, 210.8, 260.2)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (208.0, 230.0, 299.0)), ('C', '1092', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (217.7, 221.4, 281.9)), ('C', '1098', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (202.1, 211.4, 287.1)), ('C', '34', 'ARG', 'check CA trace', ' \n-S--E', (202.8, 185.1, 211.3)), ('C', '310', 'LYS', 'check CA trace', 'strand\n-EEEE', (205.1, 200.1, 235.6)), ('C', '518', 'LEU', 'check CA trace', 'bend\n--SSS', (199.6, 235.6, 197.6)), ('C', '520', 'ALA', 'check CA trace', 'bend\nSSS--', (196.3, 240.4, 198.4)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (193.7, 222.0, 207.6)), ('C', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (234.5, 205.0, 216.7))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11119/6z97/Model_validation_9/validation_cootdata/molprobity_probe6z97_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

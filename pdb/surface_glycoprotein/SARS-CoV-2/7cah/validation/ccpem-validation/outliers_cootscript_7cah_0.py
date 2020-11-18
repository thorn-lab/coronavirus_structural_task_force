
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
data['rota'] = []
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' A 379  CYS  HA ', ' A 432  CYS  HB2', -0.869, (99.248, 114.912, 104.055)), (' A 379  CYS  HA ', ' A 432  CYS  CB ', -0.751, (98.6, 115.736, 104.624)), (' E 102  ASP  O  ', ' E 104  TYR  N  ', -0.722, (104.486, 106.755, 90.867)), (' A 365  TYR  HA ', ' A 368  LEU HD13', -0.722, (93.059, 108.949, 112.015)), (' A 456  PHE  H  ', ' A 491  PRO  HB2', -0.72, (85.428, 119.917, 80.316)), (' E  60  ASP  OD2', ' E  65  LYS  NZ ', -0.705, (106.825, 110.433, 111.386)), (' A 470  THR  HB ', ' A 490  PHE  HB2', -0.699, (77.661, 120.311, 81.063)), (' E 119  SER  OG ', ' E 121  ALA  O  ', -0.649, (129.749, 108.143, 121.044)), (' A 437  ASN  OD1', ' A 438  SER  N  ', -0.642, (92.109, 100.808, 92.434)), (' D  34  TRP  O  ', ' D  46  LEU  N  ', -0.638, (115.655, 96.634, 90.867)), (' E   6  GLN  H  ', ' E 112  GLN HE22', -0.627, (126.458, 112.338, 99.051)), (' A 362  VAL  HB ', ' A 526  GLY  HA2', -0.623, (88.946, 111.895, 120.258)), (' A 418  ILE  HA ', ' A 422  ASN  HB2', -0.613, (90.288, 118.421, 88.196)), (' E  35  HIS  CD2', ' E  99  SER  HB2', -0.611, (111.125, 107.535, 96.401)), (' E   6  GLN  H  ', ' E 112  GLN  NE2', -0.593, (126.52, 112.087, 99.23)), (' E  36  TRP  O  ', ' E  48  ILE HG12', -0.593, (113.635, 107.269, 104.847)), (' E  47  TRP  CE3', ' E  61  ASN  HB2', -0.572, (107.262, 104.583, 106.118)), (' A 448  ASN  OD1', ' A 449  TYR  N  ', -0.571, (81.496, 103.081, 85.238)), (' A 353  TRP  CZ3', ' A 355  ARG  HB2', -0.564, (83.494, 119.343, 98.785)), (' D  26  GLN  NE2', ' D  27  SER  OG ', -0.56, (97.3, 93.317, 102.758)), (' A 354  ASN  O  ', ' A 398  ASP  HA ', -0.555, (84.844, 115.61, 100.446)), (' D  21  THR  HA ', ' D  71  THR HG22', -0.553, (110.298, 83.868, 94.21)), (' E  50  TYR  CE1', ' E  59  SER  HB3', -0.546, (104.775, 110.18, 101.67)), (' D  84  ILE  HA ', ' D 102  LYS  HA ', -0.544, (121.824, 89.384, 98.635)), (' D  79  ALA  HA ', ' D  82  PHE  CE2', -0.543, (128.924, 84.509, 91.918)), (' A 405  ASP  N  ', ' A 504  GLY  O  ', -0.54, (96.651, 107.834, 86.723)), (' E  16  ALA  O  ', ' E  86  LEU  HG ', -0.532, (119.331, 112.921, 118.906)), (' A 446  GLY  O  ', ' A 498  GLN  NE2', -0.531, (86.418, 99.013, 79.271)), (' D  65  GLY  HA3', ' D  70  PHE  HA ', -0.526, (105.342, 86.878, 91.017)), (' A 374  PHE  HA ', ' A 436  TRP  HB3', -0.522, (94.876, 103.345, 99.452)), (' E  67  ALA  HB3', ' E  84  SER  HB3', -0.515, (112.268, 113.523, 116.695)), (' E  35  HIS  HD2', ' E  99  SER  HB2', -0.513, (111.383, 107.537, 96.401)), (' D  90  THR  OG1', ' D  91  ASN  N  ', -0.51, (102.516, 100.34, 96.143)), (' D  85  TYR  O  ', ' D 101  THR  N  ', -0.509, (117.204, 89.736, 98.893)), (' D  31  ASN  OD1', ' D  32  LEU  N  ', -0.509, (104.991, 97.657, 91.92)), (' E  39  GLN  O  ', ' E  92  ALA  HB1', -0.507, (120.946, 101.567, 109.137)), (' A 337  PRO  O  ', ' A 340  GLU  HG3', -0.506, (81.953, 108.625, 108.178)), (' E  87  ARG  O  ', ' E 118  VAL HG11', -0.504, (121.625, 104.702, 118.324)), (' E  75  SER  OG ', ' E  76  THR  N  ', -0.501, (118.922, 126.564, 98.291)), (' E  91  THR  HA ', ' E 116  VAL  O  ', -0.501, (123.553, 105.661, 114.024)), (' A 424  LYS  NZ ', ' A 427  ASP  OD2', -0.496, (97.743, 127.347, 96.078)), (' D  12  VAL HG11', ' D  18  VAL HG11', -0.496, (121.423, 79.376, 92.235)), (' A 433  VAL HG22', ' A 512  VAL HG13', -0.485, (94.09, 115.914, 100.153)), (' E  24  VAL HG11', ' E  29  PHE  CD1', -0.481, (116.466, 118.342, 94.207)), (' A 350  VAL HG22', ' A 453  TYR  HA ', -0.481, (85.841, 115.066, 86.988)), (' E  35  HIS  ND1', ' E  50  TYR  HB3', -0.476, (109.827, 108.337, 99.951)), (' D  25  SER  OG ', ' D  26  GLN  N  ', -0.476, (99.658, 89.211, 103.607)), (' A 412  PRO  HB3', ' A 427  ASP  OD1', -0.476, (100.271, 125.101, 97.196)), (' A 340  GLU  OE1', ' A 356  LYS  HE3', -0.473, (81.228, 111.053, 105.034)), (' A 404  GLY  O  ', ' A 407  VAL HG22', -0.472, (97.641, 109.556, 90.479)), (' A 383  SER  O  ', ' A 386  LYS  N  ', -0.471, (101.625, 114.113, 113.498)), (' E  61  ASN  OD1', ' E  63  LYS  HG2', -0.471, (106.432, 102.356, 109.672)), (' A 386  LYS  HG3', ' A 390  LEU HD11', -0.469, (101.335, 118.755, 114.908)), (' D  61  PHE  HA ', ' D  74  ILE  HA ', -0.46, (118.18, 86.493, 87.061)), (' E  87  ARG  NH2', ' E  89  GLU  OE1', -0.455, (115.176, 103.637, 119.882)), (' E  41  PRO  HD2', ' E  43  LYS  NZ ', -0.454, (120.482, 97.333, 112.511)), (' E  51  ILE HG13', ' E  58  THR HG22', -0.454, (108.585, 116.355, 103.446)), (' E  47  TRP  HE3', ' E  61  ASN  HB2', -0.451, (107.493, 104.33, 105.692)), (' E  71  THR HG23', ' E  80  TYR  HB2', -0.451, (115.787, 119.979, 106.193)), (' A 377  PHE  HB3', ' D  93  TRP  CE2', -0.448, (100.782, 107.584, 104.873)), (' A 502  GLY  HA3', ' A 505  TYR  HD1', -0.448, (97.255, 103.572, 81.966)), (' D  67  GLY  O  ', ' D  70  PHE  HE1', -0.445, (101.156, 90.119, 93.206)), (' E  13  LYS  HZ1', ' E  14  PRO  HD2', -0.441, (124.78, 109.703, 125.178)), (' E   6  GLN  NE2', ' E 113  GLY  H  ', -0.441, (123.533, 108.169, 101.273)), (' E  27  TYR  CD2', ' E  32  TYR  HD2', -0.44, (114.356, 115.443, 88.994)), (' A 348  ALA  HB1', ' A 352  ALA  O  ', -0.44, (81.307, 113.851, 94.196)), (' D  93  TRP  HB3', ' D  94  PRO  HD3', -0.438, (100.705, 102.427, 105.338)), (' D  85  TYR  N  ', ' D 101  THR  O  ', -0.437, (119.818, 89.923, 97.581)), (' E  40  ALA  HB1', ' E  43  LYS  NZ ', -0.436, (119.516, 96.733, 111.398)), (' E  13  LYS  HB3', ' E  13  LYS  HE3', -0.435, (124.575, 111.791, 124.52)), (' E  13  LYS  NZ ', ' E  14  PRO  HD2', -0.432, (125.097, 109.6, 124.975)), (' A 339  GLY  O  ', ' A 343  ASN  N  ', -0.432, (84.19, 104.738, 105.114)), (' A 448  ASN  HB3', ' A 497  PHE  CD2', -0.431, (84.814, 103.055, 86.534)), (' E  51  ILE HD12', ' E  70  LEU  HB3', -0.43, (111.115, 116.477, 104.595)), (' A 405  ASP  O  ', ' A 408  ARG  HG2', -0.429, (99.286, 111.944, 88.095)), (' E  48  ILE  HB ', ' E  64  PHE  HZ ', -0.428, (113.126, 106.447, 109.792)), (' E  30  SER  O  ', ' E  53  PRO  HG2', -0.428, (109.545, 119.39, 93.687)), (' E  29  PHE  HE2', ' E  74  THR  HA ', -0.427, (115.05, 122.628, 96.568)), (' D  10  GLN  HB3', ' D 103  LEU  HA ', -0.427, (122.414, 83.632, 96.937)), (' D  91  ASN  OD1', ' D  92  PHE  N  ', -0.419, (100.343, 99.361, 98.701)), (' A 401  VAL HG22', ' A 509  ARG  HA ', -0.418, (88.035, 107.333, 94.142)), (' E  41  PRO  HG3', ' E  91  THR  O  ', -0.418, (123.41, 100.889, 112.826)), (' A 456  PHE  HB2', ' A 491  PRO  HB3', -0.417, (84.98, 121.845, 79.325)), (' A 448  ASN  HB3', ' A 497  PHE  HD2', -0.417, (85.132, 103.108, 86.902)), (' E  61  ASN  OD1', ' E  62  LEU  N  ', -0.417, (105.809, 104.314, 109.955)), (' A 385  THR HG21', ' E  65  LYS  HD2', -0.417, (106.178, 111.296, 115.371)), (' D  94  PRO  O  ', ' D  96  ILE  N  ', -0.417, (106.063, 99.279, 103.465)), (' A 335  LEU  HA ', ' A 362  VAL  O  ', -0.416, (86.001, 110.266, 117.976)), (' E  40  ALA  HB3', ' E  43  LYS  HB2', -0.414, (119.436, 95.551, 109.717)), (' A 449  TYR  O  ', ' A 494  SER  OG ', -0.413, (82.251, 107.598, 83.089)), (' A 354  ASN  HB3', ' A 399  SER  HB3', -0.412, (83.249, 112.148, 99.771)), (' A 425  LEU  HA ', ' A 425  LEU HD23', -0.41, (93.629, 121.73, 98.112)), (' A 341  VAL HG23', ' A 342  PHE  CD1', -0.41, (87.125, 108.591, 105.752)), (' E  47  TRP  HZ2', ' E  50  TYR  HD1', -0.41, (107.78, 108.332, 101.511)), (' A 353  TRP  HZ3', ' A 355  ARG  HB2', -0.409, (83.953, 119.825, 99.417)), (' E  34  ILE  HA ', ' E  34  ILE HD13', -0.407, (113.937, 111.596, 96.346)), (' D  60  ARG  O  ', ' D  75  ASN  N  ', -0.406, (119.045, 85.024, 85.258)), (' A 461  LEU HD11', ' A 467  ASP  H  ', -0.403, (84.0, 123.106, 90.701)), (' A 338  PHE  CE2', ' A 363  ALA  HB1', -0.402, (89.199, 111.057, 113.416)), (' D  90  THR  O  ', ' D  92  PHE  N  ', -0.401, (101.707, 99.706, 99.551)), (' E  20  ILE HG12', ' E  21  SER  H  ', -0.401, (122.435, 114.42, 105.699))]
data['cablam'] = [('D', '8', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\n--S--', (116.8, 84.1, 103.5)), ('D', '15', 'LYS', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (125.2, 79.8, 85.9)), ('D', '31', 'ASN', 'check CA trace,carbonyls, peptide', ' \n-S--E', (103.1, 96.6, 91.8)), ('D', '82', 'PHE', 'check CA trace,carbonyls, peptide', ' \nTT-SE', (125.7, 88.3, 93.2)), ('D', '99', 'GLN', 'check CA trace,carbonyls, peptide', 'bend\nB-S-E', (114.4, 90.9, 104.7)), ('D', '101', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nS-EE-', (117.9, 88.0, 99.2)), ('D', '64', 'SER', 'check CA trace', 'strand\nEEEE-', (107.6, 87.9, 87.4)), ('D', '94', 'PRO', 'check CA trace', 'bend\nSSS--', (104.4, 101.9, 105.0)), ('E', '15', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (119.0, 112.1, 123.9)), ('E', '16', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nSSS-E', (119.7, 115.0, 121.6)), ('E', '41', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nE-TTS', (123.5, 97.4, 110.9)), ('E', '103', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (102.5, 106.5, 92.8)), ('E', '104', 'TYR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (105.2, 104.9, 90.6)), ('E', '105', 'TYR', 'check CA trace,carbonyls, peptide', ' \nSS---', (107.5, 105.0, 93.6)), ('E', '27', 'TYR', 'check CA trace', 'bend\n-SS-G', (117.3, 117.3, 86.7)), ('E', '66', 'GLY', 'check CA trace', 'bend\nS-S--', (111.8, 109.2, 116.9)), ('E', '102', 'ASP', 'check CA trace', 'bend\n-SSSS', (103.7, 110.1, 92.4)), ('A', '336', 'CYS', 'check CA trace,carbonyls, peptide', ' \n----T', (82.7, 110.4, 114.6)), ('A', '345', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nS-S--', (80.5, 102.3, 99.0)), ('A', '346', 'ARG', 'check CA trace,carbonyls, peptide', ' \n-S---', (80.1, 104.9, 96.3)), ('A', '360', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (82.6, 118.1, 117.9)), ('A', '371', 'SER', 'check CA trace,carbonyls, peptide', 'helix\nHHH--', (94.0, 100.5, 108.4)), ('A', '372', 'ALA', 'check CA trace,carbonyls, peptide', ' \nHH---', (97.1, 100.0, 106.3)), ('A', '374', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---SE', (95.8, 103.1, 101.1)), ('A', '375', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (98.4, 103.8, 98.4)), ('A', '389', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nHHTS-', (98.4, 115.7, 119.4)), ('A', '396', 'TYR', ' beta sheet', 'strand\nEEEEE', (86.7, 119.7, 105.7)), ('A', '410', 'ILE', 'check CA trace,carbonyls, peptide', ' \nGG-SS', (96.7, 117.2, 93.6)), ('A', '411', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nG-SSS', (99.3, 119.3, 95.2)), ('A', '417', 'LYS', 'check CA trace,carbonyls, peptide', 'turn\n-STTT', (92.0, 118.9, 84.6)), ('A', '424', 'LYS', ' beta sheet', ' \nS----', (92.9, 123.2, 93.9)), ('A', '464', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-TT--', (88.4, 124.2, 97.3)), ('A', '470', 'THR', ' beta sheet', ' \n-S---', (78.4, 121.4, 83.3)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (89.3, 130.6, 116.2)), ('A', '523', 'THR', 'check CA trace,carbonyls, peptide', ' \n----S', (86.4, 119.0, 120.7)), ('A', '359', 'SER', 'check CA trace', ' \nEE-S-', (83.6, 118.8, 114.3)), ('A', '415', 'THR', 'check CA trace', ' \nS--ST', (97.8, 122.5, 86.3)), ('A', '518', 'LEU', 'check CA trace', 'bend\nE-SS-', (90.8, 129.6, 112.8)), ('A', '522', 'ALA', 'check CA trace', ' \n-----', (87.8, 122.6, 120.8)), ('A', '524', 'VAL', 'check CA trace', ' \n---S-', (88.6, 117.2, 118.2))]
data['clusters'] = [('D', '21', 1, 'side-chain clash', (110.298, 83.868, 94.21)), ('D', '30', 1, 'smoc Outlier', (100.273, 94.02, 91.49900000000001)), ('D', '31', 1, 'backbone clash\ncablam Outlier', (104.991, 97.657, 91.92)), ('D', '32', 1, 'backbone clash', (104.991, 97.657, 91.92)), ('D', '64', 1, 'cablam CA Geom Outlier', (107.6, 87.9, 87.4)), ('D', '65', 1, 'side-chain clash', (105.342, 86.878, 91.017)), ('D', '67', 1, 'side-chain clash', (101.156, 90.119, 93.206)), ('D', '70', 1, 'side-chain clash', (101.156, 90.119, 93.206)), ('D', '71', 1, 'side-chain clash', (110.298, 83.868, 94.21)), ('D', '90', 1, 'backbone clash\nDihedral angle:CA:C', (104.307, 99.195, 97.167)), ('D', '91', 1, 'backbone clash\nRamachandran\nDihedral angle:N:CA', (101.062, 101.11, 97.637)), ('D', '92', 1, 'backbone clash\nDihedral angle:CA:C', (100.248, 99.768, 101.10499999999999)), ('D', '93', 1, 'side-chain clash\nDihedral angle:N:CA', (101.19, 102.80499999999999, 103.09700000000001)), ('D', '94', 1, 'side-chain clash\nbackbone clash\ncablam CA Geom Outlier', (106.063, 99.279, 103.465)), ('D', '95', 1, 'smoc Outlier', (106.296, 100.77199999999999, 101.96100000000001)), ('D', '96', 1, 'backbone clash', (106.063, 99.279, 103.465)), ('D', '10', 2, 'side-chain clash', (122.414, 83.632, 96.937)), ('D', '101', 2, 'backbone clash\ncablam Outlier', (119.818, 89.923, 97.581)), ('D', '102', 2, 'side-chain clash', (121.824, 89.384, 98.635)), ('D', '103', 2, 'side-chain clash', (122.414, 83.632, 96.937)), ('D', '11', 2, 'smoc Outlier', (123.70700000000001, 78.77, 98.088)), ('D', '12', 2, 'side-chain clash\nsmoc Outlier', (121.423, 79.376, 92.235)), ('D', '18', 2, 'side-chain clash', (121.423, 79.376, 92.235)), ('D', '84', 2, 'side-chain clash', (121.824, 89.384, 98.635)), ('D', '85', 2, 'backbone clash', (119.818, 89.923, 97.581)), ('D', '60', 3, 'backbone clash', (119.045, 85.024, 85.258)), ('D', '61', 3, 'side-chain clash', (118.18, 86.493, 87.061)), ('D', '74', 3, 'side-chain clash', (118.18, 86.493, 87.061)), ('D', '75', 3, 'backbone clash', (119.045, 85.024, 85.258)), ('D', '25', 4, 'backbone clash', (99.658, 89.211, 103.607)), ('D', '26', 4, 'side-chain clash\nbackbone clash\nsmoc Outlier', (99.658, 89.211, 103.607)), ('D', '27', 4, 'side-chain clash\nsmoc Outlier', (97.3, 93.317, 102.758)), ('D', '79', 5, 'side-chain clash', (128.924, 84.509, 91.918)), ('D', '82', 5, 'side-chain clash\ncablam Outlier', (128.924, 84.509, 91.918)), ('D', '34', 6, 'backbone clash', (115.655, 96.634, 90.867)), ('D', '46', 6, 'backbone clash\nsmoc Outlier', (115.655, 96.634, 90.867)), ('D', '7', 7, 'smoc Outlier', (114.337, 84.345, 100.55799999999999)), ('D', '8', 7, 'cablam Outlier\nsmoc Outlier', (116.8, 84.1, 103.5)), ('E', '102', 1, 'backbone clash\nDihedral angle:CA:C\ncablam CA Geom Outlier', (103.67399999999999, 110.082, 92.36999999999999)), ('E', '103', 1, 'Dihedral angle:N:CA\ncablam Outlier', (102.54, 106.538, 92.81)), ('E', '104', 1, 'backbone clash\ncablam Outlier', (104.486, 106.755, 90.867)), ('E', '105', 1, 'cablam Outlier', (107.5, 105.0, 93.6)), ('E', '112', 1, 'side-chain clash\nsmoc Outlier', (126.52, 112.087, 99.23)), ('E', '113', 1, 'side-chain clash', (123.533, 108.169, 101.273)), ('E', '20', 1, 'side-chain clash', (122.435, 114.42, 105.699)), ('E', '21', 1, 'side-chain clash', (122.435, 114.42, 105.699)), ('E', '22', 1, 'smoc Outlier', (121.27, 115.512, 100.609)), ('E', '24', 1, 'side-chain clash', (116.466, 118.342, 94.207)), ('E', '26', 1, 'smoc Outlier', (120.96700000000001, 116.452, 86.93)), ('E', '27', 1, 'side-chain clash\ncablam CA Geom Outlier', (114.356, 115.443, 88.994)), ('E', '29', 1, 'side-chain clash', (115.05, 122.628, 96.568)), ('E', '3', 1, 'smoc Outlier', (122.99900000000001, 112.15799999999999, 91.35)), ('E', '30', 1, 'side-chain clash', (109.545, 119.39, 93.687)), ('E', '32', 1, 'side-chain clash', (114.356, 115.443, 88.994)), ('E', '34', 1, 'side-chain clash', (113.937, 111.596, 96.346)), ('E', '35', 1, 'side-chain clash', (109.827, 108.337, 99.951)), ('E', '36', 1, 'side-chain clash', (113.635, 107.269, 104.847)), ('E', '47', 1, 'side-chain clash', (107.78, 108.332, 101.511)), ('E', '48', 1, 'side-chain clash', (113.126, 106.447, 109.792)), ('E', '50', 1, 'side-chain clash', (107.78, 108.332, 101.511)), ('E', '51', 1, 'side-chain clash\nBond length:C', (109.61999999999999, 114.536, 101.309)), ('E', '52', 1, 'Bond length:N', (108.323, 116.199, 98.30199999999999)), ('E', '53', 1, 'side-chain clash', (109.545, 119.39, 93.687)), ('E', '58', 1, 'side-chain clash', (108.585, 116.355, 103.446)), ('E', '59', 1, 'side-chain clash', (104.775, 110.18, 101.67)), ('E', '6', 1, 'side-chain clash', (123.533, 108.169, 101.273)), ('E', '64', 1, 'side-chain clash', (113.126, 106.447, 109.792)), ('E', '70', 1, 'side-chain clash', (111.115, 116.477, 104.595)), ('E', '71', 1, 'side-chain clash\nsmoc Outlier', (115.787, 119.979, 106.193)), ('E', '72', 1, 'smoc Outlier', (114.01400000000001, 120.718, 102.64)), ('E', '74', 1, 'side-chain clash', (115.05, 122.628, 96.568)), ('E', '75', 1, 'backbone clash', (118.922, 126.564, 98.291)), ('E', '76', 1, 'backbone clash', (118.922, 126.564, 98.291)), ('E', '80', 1, 'side-chain clash', (115.787, 119.979, 106.193)), ('E', '95', 1, 'Dihedral angle:CA:C', (119.974, 107.051, 102.386)), ('E', '96', 1, 'Dihedral angle:N:CA', (118.295, 109.73700000000001, 100.44200000000001)), ('E', '99', 1, 'side-chain clash', (111.383, 107.537, 96.401)), ('E', '119', 2, 'backbone clash\nsmoc Outlier', (129.749, 108.143, 121.044)), ('E', '12', 2, 'Bond angle:C', (126.531, 111.26, 118.24100000000001)), ('E', '121', 2, 'backbone clash', (129.749, 108.143, 121.044)), ('E', '122', 2, 'smoc Outlier', (131.568, 110.953, 120.915)), ('E', '13', 2, 'side-chain clash\nBond angle:N:CA', (125.232, 111.009, 121.861)), ('E', '14', 2, 'side-chain clash', (125.097, 109.6, 124.975)), ('E', '15', 2, 'cablam Outlier', (119.0, 112.1, 123.9)), ('E', '16', 2, 'side-chain clash\ncablam Outlier', (119.331, 112.921, 118.906)), ('E', '18', 2, 'smoc Outlier', (120.80199999999999, 115.62599999999999, 114.51)), ('E', '86', 2, 'side-chain clash', (119.331, 112.921, 118.906)), ('E', '116', 3, 'backbone clash', (123.553, 105.661, 114.024)), ('E', '118', 3, 'side-chain clash\nsmoc Outlier', (121.625, 104.702, 118.324)), ('E', '39', 3, 'side-chain clash', (120.946, 101.567, 109.137)), ('E', '40', 3, 'side-chain clash', (119.436, 95.551, 109.717)), ('E', '41', 3, 'side-chain clash\nbackbone clash\ncablam Outlier', (123.41, 100.889, 112.826)), ('E', '43', 3, 'side-chain clash', (119.436, 95.551, 109.717)), ('E', '87', 3, 'side-chain clash', (115.176, 103.637, 119.882)), ('E', '89', 3, 'side-chain clash\nsmoc Outlier', (115.176, 103.637, 119.882)), ('E', '91', 3, 'backbone clash', (123.41, 100.889, 112.826)), ('E', '92', 3, 'side-chain clash', (120.946, 101.567, 109.137)), ('E', '60', 4, 'side-chain clash\nsmoc Outlier', (106.825, 110.433, 111.386)), ('E', '61', 4, 'side-chain clash\nbackbone clash', (105.809, 104.314, 109.955)), ('E', '62', 4, 'backbone clash\nDihedral angle:CA:C', (105.381, 105.38, 111.925)), ('E', '63', 4, 'side-chain clash\nDihedral angle:N:CA', (107.361, 102.259, 112.81700000000001)), ('E', '65', 4, 'side-chain clash\nsmoc Outlier', (106.178, 111.296, 115.371)), ('E', '66', 4, 'cablam CA Geom Outlier', (111.8, 109.2, 116.9)), ('E', '67', 4, 'side-chain clash', (112.268, 113.523, 116.695)), ('E', '84', 4, 'side-chain clash', (112.268, 113.523, 116.695)), ('A', '334', 1, 'smoc Outlier', (82.895, 109.273, 121.603)), ('A', '335', 1, 'backbone clash\nDihedral angle:CA:C\nsmoc Outlier', (83.992, 109.43, 117.96700000000001)), ('A', '336', 1, 'Dihedral angle:N:CA\nDihedral angle:CA:C\ncablam Outlier', (82.694, 110.405, 114.58)), ('A', '337', 1, 'side-chain clash\nDihedral angle:N:CA', (82.512, 107.96400000000001, 111.67299999999999)), ('A', '338', 1, 'side-chain clash', (89.199, 111.057, 113.416)), ('A', '339', 1, 'backbone clash', (84.19, 104.738, 105.114)), ('A', '340', 1, 'side-chain clash', (81.228, 111.053, 105.034)), ('A', '341', 1, 'side-chain clash', (87.125, 108.591, 105.752)), ('A', '342', 1, 'side-chain clash', (87.125, 108.591, 105.752)), ('A', '343', 1, 'backbone clash', (84.19, 104.738, 105.114)), ('A', '348', 1, 'backbone clash', (81.307, 113.851, 94.196)), ('A', '352', 1, 'backbone clash', (81.307, 113.851, 94.196)), ('A', '353', 1, 'side-chain clash', (83.953, 119.825, 99.417)), ('A', '354', 1, 'side-chain clash', (83.249, 112.148, 99.771)), ('A', '355', 1, 'side-chain clash', (83.953, 119.825, 99.417)), ('A', '356', 1, 'side-chain clash', (81.228, 111.053, 105.034)), ('A', '357', 1, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (82.62199999999999, 119.692, 107.52499999999999)), ('A', '359', 1, 'cablam CA Geom Outlier', (83.6, 118.8, 114.3)), ('A', '360', 1, 'cablam Outlier', (82.6, 118.1, 117.9)), ('A', '361', 1, 'Dihedral angle:CA:C', (84.387, 114.807, 117.763)), ('A', '362', 1, 'side-chain clash\nbackbone clash\nDihedral angle:N:CA', (87.27499999999999, 112.819, 119.032)), ('A', '363', 1, 'side-chain clash', (89.199, 111.057, 113.416)), ('A', '365', 1, 'side-chain clash', (93.059, 108.949, 112.015)), ('A', '368', 1, 'side-chain clash', (93.059, 108.949, 112.015)), ('A', '379', 1, 'side-chain clash', (98.6, 115.736, 104.624)), ('A', '383', 1, 'backbone clash', (101.625, 114.113, 113.498)), ('A', '384', 1, 'smoc Outlier', (100.65299999999999, 112.004, 111.07199999999999)), ('A', '389', 1, 'cablam Outlier', (98.4, 115.7, 119.4)), ('A', '391', 1, 'smoc Outlier', (94.24300000000001, 121.13799999999999, 118.44000000000001)), ('A', '396', 1, 'cablam Outlier', (86.7, 119.7, 105.7)), ('A', '398', 1, 'side-chain clash', (84.844, 115.61, 100.446)), ('A', '399', 1, 'side-chain clash\nsmoc Outlier', (83.249, 112.148, 99.771)), ('A', '410', 1, 'cablam Outlier', (96.7, 117.2, 93.6)), ('A', '411', 1, 'cablam Outlier', (99.3, 119.3, 95.2)), ('A', '412', 1, 'side-chain clash', (100.271, 125.101, 97.196)), ('A', '424', 1, 'side-chain clash\ncablam Outlier', (97.743, 127.347, 96.078)), ('A', '425', 1, 'side-chain clash', (93.629, 121.73, 98.112)), ('A', '427', 1, 'side-chain clash', (100.271, 125.101, 97.196)), ('A', '432', 1, 'side-chain clash\nDihedral angle:CA:C', (96.361, 116.137, 104.252)), ('A', '433', 1, 'side-chain clash\nDihedral angle:N:CA', (95.657, 113.641, 101.549)), ('A', '448', 1, 'backbone clash\nside-chain clash', (106.178, 111.296, 115.371)), ('A', '461', 1, 'side-chain clash', (84.0, 123.106, 90.701)), ('A', '462', 1, 'smoc Outlier', (89.666, 128.254, 92.829)), ('A', '464', 1, 'cablam Outlier', (88.4, 124.2, 97.3)), ('A', '466', 1, 'smoc Outlier', (83.045, 123.49000000000001, 93.396)), ('A', '467', 1, 'side-chain clash', (84.0, 123.106, 90.701)), ('A', '497', 1, 'side-chain clash', (106.178, 111.296, 115.371)), ('A', '512', 1, 'side-chain clash', (94.09, 115.914, 100.153)), ('A', '522', 1, 'cablam CA Geom Outlier', (87.8, 122.6, 120.8)), ('A', '523', 1, 'Dihedral angle:CA:C\ncablam Outlier', (86.41900000000001, 118.97, 120.721)), ('A', '524', 1, 'Dihedral angle:N:CA\ncablam CA Geom Outlier', (88.63499999999999, 117.24700000000001, 118.17499999999998)), ('A', '526', 1, 'side-chain clash', (88.946, 111.895, 120.258)), ('A', '527', 1, 'smoc Outlier', (93.17899999999999, 112.571, 123.63799999999999)), ('A', '404', 2, 'side-chain clash', (97.641, 109.556, 90.479)), ('A', '405', 2, 'backbone clash\nside-chain clash', (99.286, 111.944, 88.095)), ('A', '407', 2, 'side-chain clash', (97.641, 109.556, 90.479)), ('A', '408', 2, 'side-chain clash', (99.286, 111.944, 88.095)), ('A', '502', 2, 'side-chain clash', (97.255, 103.572, 81.966)), ('A', '504', 2, 'backbone clash', (96.651, 107.834, 86.723)), ('A', '505', 2, 'side-chain clash\nsmoc Outlier', (97.255, 103.572, 81.966)), ('A', '350', 3, 'side-chain clash', (85.841, 115.066, 86.988)), ('A', '417', 3, 'cablam Outlier\nsmoc Outlier', (92.0, 118.9, 84.6)), ('A', '418', 3, 'side-chain clash', (90.288, 118.421, 88.196)), ('A', '422', 3, 'side-chain clash', (90.288, 118.421, 88.196)), ('A', '453', 3, 'side-chain clash', (85.841, 115.066, 86.988)), ('A', '449', 4, 'backbone clash\nside-chain clash', (82.251, 107.598, 83.089)), ('A', '450', 4, 'smoc Outlier', (79.64, 106.565, 86.145)), ('A', '494', 4, 'side-chain clash', (82.251, 107.598, 83.089)), ('A', '370', 5, 'smoc Outlier', (95.982, 100.599, 111.627)), ('A', '371', 5, 'cablam Outlier', (94.0, 100.5, 108.4)), ('A', '372', 5, 'cablam Outlier', (97.1, 100.0, 106.3)), ('A', '374', 6, 'side-chain clash\ncablam Outlier', (94.876, 103.345, 99.452)), ('A', '375', 6, 'cablam Outlier', (98.4, 103.8, 98.4)), ('A', '436', 6, 'side-chain clash', (94.876, 103.345, 99.452)), ('A', '446', 7, 'side-chain clash', (86.418, 99.013, 79.271)), ('A', '498', 7, 'side-chain clash', (86.418, 99.013, 79.271)), ('A', '470', 8, 'side-chain clash\ncablam Outlier\nsmoc Outlier', (77.661, 120.311, 81.063)), ('A', '490', 8, 'side-chain clash', (77.661, 120.311, 81.063)), ('A', '456', 9, 'side-chain clash', (84.98, 121.845, 79.325)), ('A', '491', 9, 'side-chain clash', (84.98, 121.845, 79.325)), ('A', '345', 10, 'cablam Outlier', (80.5, 102.3, 99.0)), ('A', '346', 10, 'cablam Outlier', (80.1, 104.9, 96.3)), ('A', '386', 11, 'backbone clash\nside-chain clash', (100.782, 107.584, 104.873)), ('A', '390', 11, 'side-chain clash', (100.782, 107.584, 104.873)), ('A', '428', 12, 'Dihedral angle:CA:C\nDihedral angle:CA:CB:CG:OD1', (97.529, 127.973, 103.536)), ('A', '429', 12, 'Dihedral angle:N:CA\nsmoc Outlier', (96.952, 124.311, 104.18799999999999)), ('A', '440', 13, 'smoc Outlier', (87.134, 95.798, 92.57)), ('A', '443', 13, 'smoc Outlier', (86.21600000000001, 98.896, 87.93100000000001)), ('A', '518', 14, 'cablam CA Geom Outlier', (90.8, 129.6, 112.8)), ('A', '519', 14, 'cablam Outlier', (89.3, 130.6, 116.2)), ('A', '437', 15, 'backbone clash', (92.109, 100.808, 92.434)), ('A', '438', 15, 'backbone clash', (92.109, 100.808, 92.434)), ('A', '401', 16, 'side-chain clash', (88.035, 107.333, 94.142)), ('A', '509', 16, 'side-chain clash', (88.035, 107.333, 94.142)), ('A', '415', 17, 'cablam CA Geom Outlier\nsmoc Outlier', (97.8, 122.5, 86.3)), ('A', '500', 17, 'smoc Outlier', (94.137, 96.1, 81.29700000000001))]
data['omega'] = [('A', ' 362 ', 'VAL', None, (85.917, 113.246, 118.736)), ('A', ' 433 ', 'VAL', None, (96.287, 114.317, 102.678)), ('E', ' 103 ', 'PRO', None, (102.404, 107.915, 92.319))]
data['rama'] = [('D', '  91 ', 'ASN', 0.02064436918055289, (101.062, 101.11, 97.637))]
data['smoc'] = [('D', 7, u'SER', 0.7539375012155831, (114.337, 84.345, 100.55799999999999)), ('D', 8, u'PRO', 0.7672971673084267, (116.81400000000001, 84.079, 103.512)), ('D', 11, u'SER', 0.8157198604086482, (123.70700000000001, 78.77, 98.088)), ('D', 12, u'VAL', 0.7826898042048182, (123.84100000000001, 77.111, 94.66499999999999)), ('D', 26, u'GLN', 0.8204399669880381, (97.666, 88.694, 102.337)), ('D', 27, u'SER', 0.8328441731333378, (97.96000000000001, 91.978, 100.429)), ('D', 30, u'SER', 0.870157629702524, (100.273, 94.02, 91.49900000000001)), ('D', 38, u'LYS', 0.8362565914450865, (126.556, 95.438, 97.124)), ('D', 46, u'LEU', 0.8697917702472975, (116.723, 96.232, 89.351)), ('D', 57, u'ILE', 0.7905894936783856, (120.20700000000001, 96.14999999999999, 83.381)), ('D', 95, u'TYR', 0.8821499281984839, (106.296, 100.77199999999999, 101.96100000000001)), ('E', 3, u'GLN', 0.7788683017644303, (122.99900000000001, 112.15799999999999, 91.35)), ('E', 18, u'VAL', 0.8982493329710375, (120.80199999999999, 115.62599999999999, 114.51)), ('E', 22, u'CYS', 0.793715167985739, (121.27, 115.512, 100.609)), ('E', 26, u'GLY', 0.7320225870457764, (120.96700000000001, 116.452, 86.93)), ('E', 60, u'ASP', 0.8291508960915901, (106.09100000000001, 109.468, 107.44700000000002)), ('E', 65, u'LYS', 0.7828651543486729, (108.505, 107.65799999999999, 116.103)), ('E', 71, u'THR', 0.7948014095752721, (112.436, 119.53, 105.87899999999999)), ('E', 72, u'ALA', 0.7151952863429828, (114.01400000000001, 120.718, 102.64)), ('E', 89, u'GLU', 0.8479772615254685, (118.30799999999999, 101.61, 117.337)), ('E', 112, u'GLN', 0.8537469846331034, (126.395, 107.765, 99.386)), ('E', 118, u'VAL', 0.8529892045152632, (125.227, 106.10799999999999, 118.536)), ('E', 119, u'SER', 0.8366826407886839, (127.521, 105.34100000000001, 121.485)), ('E', 122, u'SER', 0.8176910689178537, (131.568, 110.953, 120.915)), ('A', 527, u'PRO', 0.8329919887192927, (93.17899999999999, 112.571, 123.63799999999999)), ('A', 334, u'ASN', 0.7945760073361368, (82.895, 109.273, 121.603)), ('A', 335, u'LEU', 0.811089397737538, (83.992, 109.43, 117.96700000000001)), ('A', 357, u'ARG', 0.871085794560328, (82.62199999999999, 119.692, 107.52499999999999)), ('A', 370, u'ASN', 0.8502207300677863, (95.982, 100.599, 111.627)), ('A', 384, u'PRO', 0.8252484918607154, (100.65299999999999, 112.004, 111.07199999999999)), ('A', 391, u'CYS', 0.8097691844806049, (94.24300000000001, 121.13799999999999, 118.44000000000001)), ('A', 399, u'SER', 0.8566594239359244, (85.692, 112.161, 99.039)), ('A', 415, u'THR', 0.8253523024490018, (97.755, 122.46900000000001, 86.32)), ('A', 417, u'LYS', 0.8043458489470575, (91.95100000000001, 118.887, 84.601)), ('A', 429, u'PHE', 0.8031481260465037, (96.952, 124.311, 104.18799999999999)), ('A', 440, u'ASN', 0.803919711388357, (87.134, 95.798, 92.57)), ('A', 443, u'SER', 0.7714465422854365, (86.21600000000001, 98.896, 87.93100000000001)), ('A', 450, u'ASN', 0.8472593009113858, (79.64, 106.565, 86.145)), ('A', 462, u'LYS', 0.8352697746228958, (89.666, 128.254, 92.829)), ('A', 466, u'ARG', 0.804036522424633, (83.045, 123.49000000000001, 93.396)), ('A', 470, u'THR', 0.8415287044590798, (78.403, 121.4, 83.301)), ('A', 500, u'THR', 0.8104386365786571, (94.137, 96.1, 81.29700000000001)), ('A', 505, u'TYR', 0.8215595952744938, (94.65599999999999, 105.019, 84.389))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30331/7cah/Model_validation_1/validation_cootdata/molprobity_probe7cah_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

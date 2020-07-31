
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
data['rota'] = []
data['cbeta'] = []
data['jpred'] = [('C', '4', 'S', '-', 'H', (98.0, 70.6, 124.3)), ('C', '5', 'D', '-', 'H', (97.7, 71.2, 128.1)), ('B', '79', 'K', '-', 'H', (74.0, 116.0, 122.5)), ('B', '113', 'G', '-', 'H', (101.1, 133.1, 102.6)), ('B', '135', 'Y', '-', 'H', (122.4, 102.7, 122.4))]
data['probe'] = [(' A 884  TYR  O  ', ' A 888  ILE HD12', -0.762, (77.932, 72.114, 119.614)), (' A 819  LEU HD11', ' A 826  TYR  HB3', -0.731, (78.555, 66.017, 92.604)), (' A 223  ILE  O  ', ' A 223  ILE HG13', -0.716, (110.853, 108.516, 55.29)), (' B 120  ILE  O  ', ' B 124  THR  HB ', -0.714, (106.5, 125.656, 112.81)), (' C  35  LEU HD11', ' C  55  LEU HD13', -0.67, (107.024, 82.819, 129.338)), (' D 103  LEU  O  ', ' D 107  ILE HG13', -0.646, (106.63, 73.383, 139.991)), (' A 149  TYR  HE2', ' A 212  LEU HD13', -0.631, (124.298, 96.418, 79.753)), (' A 272  LYS  HE3', ' A 275  PHE  CE1', -0.625, (110.7, 123.373, 93.597)), (' C  28  LEU HD12', ' C  31  GLN HE21', -0.612, (110.78, 89.691, 133.061)), (' A 858  ARG  O  ', ' A 862  LEU HD12', -0.611, (80.784, 79.711, 117.246)), (' A 606  TYR  CE2', ' A 805  LEU HD22', -0.606, (85.516, 72.538, 87.353)), (' D  92  PHE  HA ', ' D  95  LEU  HB2', -0.601, (99.265, 74.923, 138.54)), (' A 531  THR HG21', ' A 567  THR HG21', -0.6, (83.259, 114.555, 102.12)), (' A 333  ILE HG22', ' A 361  LEU  HA ', -0.59, (91.571, 133.026, 105.503)), (' B 159  VAL HG22', ' B 186  VAL HG22', -0.59, (117.596, 111.949, 126.288)), (' A 290  TRP  HE1', ' A 309  HIS  CE1', -0.586, (101.28, 111.035, 77.306)), (' D 166  ILE HG22', ' D 168  GLN  OE1', -0.584, (133.495, 82.812, 151.723)), (' A 309  HIS  HD2', ' A 466  ILE HG12', -0.581, (100.511, 107.784, 79.837)), (' D  94  MET  O  ', ' D  98  LEU HD12', -0.577, (98.932, 70.96, 134.886)), (' C  49  PHE  O  ', ' C  53  VAL HG23', -0.575, (110.202, 74.569, 131.862)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.574, (81.849, 80.443, 90.131)), (' C  13  LEU HD22', ' C  52  MET  HE1', -0.568, (103.064, 77.963, 133.551)), (' A 271  LEU  N  ', ' A 271  LEU HD12', -0.562, (110.434, 127.635, 103.084)), (' A 527  LEU  O  ', ' A 531  THR HG23', -0.547, (81.612, 117.471, 101.476)), (' A 605  VAL HG22', ' A 756  MET  HB2', -0.545, (84.126, 81.942, 89.739)), (' C  17  LEU HD22', ' C  22  VAL HG21', -0.539, (104.557, 88.528, 135.563)), (' A 136  GLU  N  ', ' A 136  GLU  OE2', -0.539, (112.406, 83.514, 89.475)), (' A 419  PHE  HA ', ' A 887  TYR  HE2', -0.535, (83.649, 72.569, 126.188)), (' A 660  ALA  O  ', ' A 665  GLU  HB3', -0.531, (94.928, 110.858, 103.703)), (' A 856  ILE  O  ', ' A 860  VAL HG23', -0.528, (75.014, 78.685, 119.661)), (' A 472  VAL  O  ', ' A 476  VAL HG23', -0.525, (91.193, 96.783, 82.584)), (' A 200  GLY  HA2', ' A 230  GLY  N  ', -0.518, (111.977, 115.452, 59.207)), (' A 413  GLY  HA2', ' A 546  TYR  OH ', -0.515, (92.401, 87.102, 124.867)), (' A 380  MET  HA ', ' A 380  MET  HE3', -0.507, (95.577, 124.177, 114.732)), (' A 855  MET  HE2', ' A 859  PHE  CE2', -0.506, (81.309, 78.061, 123.491)), (' A 820  VAL HG21', ' A 829  LEU HD12', -0.504, (78.403, 67.825, 100.575)), (' A 816  HIS  O  ', ' A 830  PRO  HA ', -0.503, (84.435, 74.097, 101.044)), (' A 128  VAL  O  ', ' A 132  ARG  HG3', -0.501, (111.138, 94.633, 81.072)), (' A 380  MET  HE1', ' B  98  LEU HD22', -0.501, (95.937, 126.634, 115.459)), (' A 755  MET  HG2', ' A 764  VAL HG12', -0.498, (90.225, 84.168, 86.652)), (' A 855  MET  HE1', ' A 858  ARG  HD3', -0.498, (82.287, 80.748, 121.733)), (' A 341  VAL HG21', ' B 103  LEU HD21', -0.49, (99.884, 128.609, 112.112)), (' A 567  THR  HB ', ' A 654  ARG HH12', -0.489, (82.456, 112.829, 100.3)), (' A 707  LEU  O  ', ' A 710  THR HG22', -0.488, (101.191, 86.734, 72.204)), (' A 615  MET  HE2', ' A 764  VAL HG21', -0.486, (94.422, 81.051, 86.844)), (' D 186  VAL  O  ', ' D 186  VAL HG12', -0.485, (124.297, 79.056, 144.564)), (' B 161  ASP  HA ', ' B 184  LEU HD23', -0.485, (114.361, 105.34, 128.644)), (' A 128  VAL HG12', ' A 132  ARG  HD3', -0.485, (109.76, 95.468, 79.362)), (' A 848  VAL HG23', ' A 854  LEU  HB3', -0.485, (79.204, 85.654, 124.497)), (' C  54  SER  O  ', ' C  58  VAL HG23', -0.483, (110.024, 82.957, 134.05)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.479, (87.569, 96.771, 93.182)), (' D 147  PHE  HB2', ' D 156  ILE HD11', -0.476, (125.178, 74.908, 143.615)), (' A 614  LEU  HB2', ' A 802  GLU  HB3', -0.475, (91.9, 73.306, 89.988)), (' A 710  THR  CG2', ' A 715  ILE HD11', -0.472, (101.476, 84.439, 70.555)), (' A 203  GLY  HA3', ' A 222  PHE  CD1', -0.472, (112.359, 105.574, 60.958)), (' A 420  TYR  O  ', ' A 424  VAL HG22', -0.472, (88.994, 68.727, 127.408)), (' A 468  GLN  O  ', ' A 472  VAL HG23', -0.47, (96.416, 97.455, 79.963)), (' A 330  VAL  HA ', ' A 342  VAL  O  ', -0.47, (96.673, 125.728, 105.379)), (' A 186  LEU HD11', ' A 241  LEU HD21', -0.468, (114.582, 104.97, 79.22)), (' A 419  PHE  HA ', ' A 887  TYR  CE2', -0.467, (83.159, 72.558, 126.092)), (' A 379  ALA  HA ', ' B 117  LEU HD13', -0.467, (98.071, 121.767, 109.303)), (' A 545  LYS  HB2', ' A 557  VAL HG23', -0.466, (92.614, 95.208, 114.183)), (' A 272  LYS  HE3', ' A 275  PHE  CD1', -0.465, (110.647, 122.943, 93.424)), (' A 494  ILE  O  ', ' A 573  GLN  NE2', -0.465, (74.52, 102.726, 103.641)), (' A 192  PHE  HZ ', ' A 219  PHE  HE1', -0.461, (118.834, 106.382, 63.97)), (' A 401  LEU  N  ', ' A 401  LEU HD23', -0.46, (101.333, 115.168, 117.924)), (' A  41  LYS  HD2', ' A  41  LYS  N  ', -0.46, (102.578, 90.835, 58.11)), (' A 367  SER  OG ', ' A 368  PHE  N  ', -0.46, (77.988, 124.99, 111.526)), (' A 818  MET  HE1', ' A 868  PRO  O  ', -0.459, (81.313, 68.091, 105.234)), (' D 120  ILE  N  ', ' D 120  ILE HD12', -0.459, (115.249, 81.24, 136.816)), (' A 268  TRP  CZ3', ' A 272  LYS  HE2', -0.458, (113.08, 124.673, 93.284)), (' C  28  LEU HD12', ' C  31  GLN  NE2', -0.457, (111.482, 89.917, 132.702)), (' A 606  TYR  HE2', ' A 805  LEU HD22', -0.457, (85.418, 71.998, 87.812)), (' D 162  ALA  HB2', ' D 183  PRO  HG2', -0.456, (119.918, 88.047, 153.74)), (' A 372  LEU  HG ', ' A 563  CYS  SG ', -0.453, (83.771, 116.298, 109.906)), (' C   6  VAL HG22', ' D  98  LEU HD23', -0.453, (102.596, 71.137, 130.44)), (' A 887  TYR  O  ', ' A 891  LEU  HG ', -0.452, (76.766, 73.861, 125.389)), (' A 196  MET  HE2', ' A 232  PRO  HB3', -0.446, (112.563, 110.239, 65.475)), (' D 156  ILE  H  ', ' D 156  ILE HD12', -0.446, (127.664, 75.424, 142.642)), (' A 602  LEU  O  ', ' A 606  TYR  HD1', -0.446, (81.664, 76.504, 88.687)), (' A 572  HIS  O  ', ' A 576  LEU  HG ', -0.446, (79.507, 102.107, 96.627)), (' A 531  THR  O  ', ' A 657  ASN  ND2', -0.444, (86.243, 116.905, 97.625)), (' A 415  PHE  CZ ', ' A 417  LYS  HA ', -0.444, (89.662, 75.326, 129.848)), (' D 147  PHE  HB3', ' D 154  TRP  HB2', -0.444, (123.387, 74.972, 141.171)), (' A 200  GLY  HA2', ' A 230  GLY  CA ', -0.442, (111.981, 114.941, 59.185)), (' D 124  THR  O  ', ' D 124  THR HG22', -0.442, (125.372, 82.544, 129.244)), (' D 110  ALA  HB1', ' D 115  VAL HG12', -0.441, (109.055, 80.265, 145.905)), (' A 612  PRO  HG2', ' A 805  LEU  CD1', -0.44, (87.294, 71.777, 84.261)), (' D 159  VAL  O  ', ' D 166  ILE HG12', -0.439, (129.788, 84.984, 148.782)), (' A  98  LYS  O  ', ' A 117  GLN  HB3', -0.439, (130.694, 100.982, 64.005)), (' A 696  ILE  O  ', ' A 700  VAL HG23', -0.438, (91.875, 91.861, 84.719)), (' A 488  ILE HD11', ' A 493  VAL HG22', -0.438, (73.357, 107.444, 100.468)), (' B  83  VAL  O  ', ' B  87  MET  HG3', -0.438, (82.077, 119.516, 118.966)), (' A 515  TYR  O  ', ' A 519  MET  HG3', -0.438, (76.395, 113.832, 112.755)), (' A 887  TYR  CE1', ' A 891  LEU HD21', -0.437, (79.236, 74.553, 126.699)), (' A 710  THR HG23', ' A 715  ILE HD11', -0.437, (101.607, 84.075, 70.127)), (' A 388  LEU HD12', ' A 389  LEU  N  ', -0.436, (110.424, 112.543, 117.074)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.432, (119.699, 106.348, 122.229)), (' A 578  SER  O  ', ' A 582  THR HG23', -0.426, (74.942, 94.148, 91.822)), (' C  35  LEU  O  ', ' C  39  ILE HG23', -0.424, (107.307, 79.993, 125.087)), (' C  13  LEU HD23', ' C  55  LEU HD23', -0.424, (103.719, 80.651, 132.107)), (' A 204  VAL HG22', ' A 233  VAL  HB ', -0.424, (107.374, 105.215, 65.482)), (' A 203  GLY  HA3', ' A 222  PHE  HD1', -0.422, (112.253, 105.587, 60.725)), (' A 602  LEU HD21', ' A 809  PRO  HD3', -0.421, (85.481, 75.34, 93.3)), (' A 205  LEU  HB3', ' A 216  TRP  CH2', -0.421, (114.637, 104.343, 69.402)), (' D  93  THR  O  ', ' D  97  LYS  HG3', -0.42, (95.67, 69.727, 137.561)), (' A 478  LYS  HA ', ' A 478  LYS  HD3', -0.42, (82.487, 96.518, 79.99)), (' A 544  LEU HD23', ' A 556  THR HG22', -0.418, (98.443, 97.035, 115.144)), (' C  10  SER  HB2', ' C  39  ILE HD11', -0.414, (103.112, 78.353, 127.557)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.413, (101.876, 84.598, 126.431)), (' B  91  LEU  O  ', ' B  95  LEU HD13', -0.413, (92.181, 126.751, 118.678)), (' C  10  SER  CB ', ' C  39  ILE HD11', -0.412, (102.677, 78.448, 127.649)), (' A 758  LEU HD23', ' A 759  SER  H  ', -0.412, (87.149, 89.516, 98.511)), (' B 115  VAL  HB ', ' B 119  ILE HD11', -0.412, (105.534, 126.667, 105.028)), (' A 268  TRP  CD1', ' A 322  PRO  HD3', -0.41, (113.433, 119.819, 96.597)), (' A 128  VAL  CG1', ' A 132  ARG  HD3', -0.408, (110.248, 96.048, 79.605)), (' A 132  ARG HH12', ' A 240  LEU  HA ', -0.407, (106.563, 98.434, 78.725)), (' A 606  TYR  O  ', ' A 609  VAL HG23', -0.403, (84.044, 77.702, 82.495)), (' A  42  VAL HG23', ' A 712  GLY  HA3', -0.401, (104.024, 86.534, 65.548)), (' A 519  MET  HB3', ' A 519  MET  HE2', -0.4, (75.817, 116.395, 109.31))]
data['smoc'] = [('A', 84, 'GLU', 0.4838609001481879, (121.27400207519531, 102.42400360107422, 53.54800033569336)), ('A', 90, 'LEU', 0.46776829156165345, (122.78600311279297, 111.18499755859375, 61.145999908447266)), ('A', 97, 'ALA', 0.3453246552484785, (126.90899658203125, 104.48400115966797, 66.90799713134766)), ('A', 117, 'GLN', 0.37461543225521116, (131.3560028076172, 98.6709976196289, 65.4530029296875)), ('A', 125, 'ALA', 0.47392217391387537, (115.2770004272461, 95.45800018310547, 75.1240005493164)), ('A', 138, 'ASN', 0.5508232012171391, (116.08699798583984, 81.18299865722656, 84.01499938964844)), ('A', 143, 'LYS', 0.5761412226122473, (122.41300201416016, 88.25299835205078, 86.56199645996094)), ('A', 145, 'ILE', 0.5133074971594357, (123.90399932861328, 92.26100158691406, 83.08000183105469)), ('A', 171, 'ILE', 0.5838499851923803, (118.54900360107422, 94.41699981689453, 96.18699645996094)), ('A', 179, 'GLY', 0.544205332412893, (119.90599822998047, 104.08999633789062, 87.4260025024414)), ('A', 200, 'GLY', 0.5371345767562343, (113.60800170898438, 114.927001953125, 57.86399841308594)), ('A', 226, 'THR', 0.4895477284728309, (111.95800018310547, 117.2040023803711, 53.571998596191406)), ('A', 233, 'VAL', 0.5869885202952687, (107.64099884033203, 107.6500015258789, 66.94100189208984)), ('A', 239, 'SER', 0.4625780973406528, (105.73999786376953, 103.10099792480469, 77.23400115966797)), ('A', 254, 'GLU', 0.5265331170814622, (118.30500030517578, 115.34200286865234, 89.28099822998047)), ('A', 268, 'TRP', 0.58811805398244, (115.75599670410156, 123.47000122070312, 98.14900207519531)), ('A', 274, 'ASP', 0.5131792594462091, (104.93900299072266, 124.4729995727539, 93.43499755859375)), ('A', 286, 'TYR', 0.5826127447444668, (113.72899627685547, 113.60399627685547, 79.16799926757812)), ('A', 291, 'ASP', 0.5524730067681726, (103.36799621582031, 113.33300018310547, 71.58999633789062)), ('A', 312, 'ASN', 0.4676660373773713, (101.70099639892578, 108.56500244140625, 86.01599884033203)), ('A', 333, 'ILE', 0.5425372524483751, (92.87200164794922, 132.97799682617188, 108.4800033569336)), ('A', 334, 'PHE', 0.5481821757943985, (91.28500366210938, 135.25100708007812, 111.08300018310547)), ('A', 340, 'PHE', 0.5116818624103048, (93.95700073242188, 129.9340057373047, 112.76499938964844)), ('A', 360, 'ASN', 0.5954890834038288, (87.23300170898438, 132.82899475097656, 103.29900360107422)), ('A', 369, 'LYS', 0.5871369647267589, (80.3949966430664, 122.1719970703125, 109.08399963378906)), ('A', 375, 'ALA', 0.6008721901902729, (89.10800170898438, 120.03399658203125, 113.81300354003906)), ('A', 382, 'ALA', 0.5761322751031333, (100.88500213623047, 119.62699890136719, 113.55400085449219)), ('A', 390, 'ASP', 0.5642829706807866, (111.45500183105469, 108.89199829101562, 115.64299774169922)), ('A', 393, 'THR', 0.5167188393524489, (110.89600372314453, 103.83799743652344, 111.89600372314453)), ('A', 396, 'PHE', 0.5543515855004866, (108.54100036621094, 110.4739990234375, 107.5780029296875)), ('A', 408, 'GLN', 0.552205598092031, (100.2030029296875, 99.85700225830078, 123.73300170898438)), ('A', 411, 'LYS', 0.5844351260847048, (96.77200317382812, 90.94000244140625, 126.27300262451172)), ('A', 416, 'ASN', 0.513334720026344, (87.47899627685547, 78.54000091552734, 128.42599487304688)), ('A', 430, 'LYS', 0.5662655997142526, (95.44200134277344, 62.73899841308594, 121.7020034790039)), ('A', 436, 'GLU', 0.48631603588247896, (95.17400360107422, 69.87300109863281, 116.95099639892578)), ('A', 440, 'PHE', 0.5892207656160283, (95.85399627685547, 81.26699829101562, 119.45899963378906)), ('A', 445, 'ASP', 0.5728162417026015, (104.66100311279297, 93.7699966430664, 123.74500274658203)), ('A', 452, 'ASP', 0.5290939069801464, (104.01399993896484, 96.78500366210938, 112.33599853515625)), ('A', 464, 'CYS', 0.4994538106053625, (103.52899932861328, 101.8239974975586, 85.18800354003906)), ('A', 471, 'PHE', 0.5813319912677362, (94.03900146484375, 99.48200225830078, 77.72200012207031)), ('A', 482, 'CYS', 0.5536382743488825, (76.65299987792969, 95.25599670410156, 84.79000091552734)), ('A', 497, 'ASN', 0.6035759072966047, (76.8740005493164, 98.875, 112.72599792480469)), ('A', 501, 'SER', 0.48852227940212295, (85.94000244140625, 104.33000183105469, 115.43599700927734)), ('A', 502, 'ALA', 0.5561436235656002, (85.19200134277344, 107.8270034790039, 114.13999938964844)), ('A', 513, 'ARG', 0.5875646563164495, (76.447998046875, 107.06099700927734, 115.98600006103516)), ('A', 522, 'GLU', 0.6117985097057028, (71.0770034790039, 119.1520004272461, 104.86599731445312)), ('A', 535, 'VAL', 0.5522015930914477, (90.13500213623047, 118.98799896240234, 99.58399963378906)), ('A', 553, 'ARG', 0.5222177395260031, (101.9229965209961, 89.04900360107422, 113.66600036621094)), ('A', 555, 'ARG', 0.45561194473354005, (97.06300354003906, 92.58599853515625, 112.95500183105469)), ('A', 556, 'THR', 0.49756161221009526, (96.47899627685547, 96.35600280761719, 113.32099914550781)), ('A', 575, 'LEU', 0.5304938803595766, (77.44499969482422, 101.19499969482422, 93.32099914550781)), ('A', 578, 'SER', 0.5538957904724162, (74.75900268554688, 96.86599731445312, 93.21399688720703)), ('A', 592, 'SER', 0.5098682159665529, (76.2979965209961, 83.97100067138672, 101.13300323486328)), ('A', 601, 'MET', 0.5532100111047621, (79.12300109863281, 80.3290023803711, 92.49299621582031)), ('A', 630, 'LEU', 0.47862911797953783, (96.7969970703125, 101.16799926757812, 90.7509994506836)), ('A', 658, 'GLU', 0.5226299975855874, (89.86499786376953, 110.2509994506836, 98.3740005493164)), ('A', 661, 'GLN', 0.5078416774331937, (91.73899841308594, 111.12699890136719, 102.94100189208984)), ('A', 665, 'GLU', 0.4923879594658539, (96.84700012207031, 110.97799682617188, 104.85099792480469)), ('A', 672, 'SER', 0.4799505487117496, (102.06900024414062, 111.13500213623047, 117.27799987792969)), ('A', 703, 'ASN', 0.5790702800910421, (96.8239974975586, 87.5989990234375, 80.11900329589844)), ('A', 705, 'ASN', 0.6029293827462493, (101.62000274658203, 89.95999908447266, 78.802001953125)), ('A', 706, 'ALA', 0.554339941461509, (101.16000366210938, 86.2300033569336, 78.17500305175781)), ('A', 717, 'ASP', 0.5833841844902392, (95.12799835205078, 79.08699798583984, 65.38300323486328)), ('A', 726, 'ARG', 0.5622348466255154, (95.20700073242188, 93.81999969482422, 66.83699798583984)), ('A', 734, 'ASN', 0.5863147751415787, (96.32599639892578, 103.25599670410156, 68.30500030517578)), ('A', 740, 'ASP', 0.5814490959340173, (84.99400329589844, 96.60900115966797, 69.28299713134766)), ('A', 756, 'MET', 0.5821579822573519, (85.70999908447266, 84.39399719238281, 90.59500122070312)), ('A', 761, 'ASP', 0.528022404302381, (91.30500030517578, 85.9020004272461, 97.03800201416016)), ('A', 785, 'VAL', 0.5258216432086692, (103.46700286865234, 90.99400329589844, 86.69300079345703)), ('A', 786, 'LEU', 0.5658917678501821, (103.60600280761719, 91.16799926757812, 90.48500061035156)), ('A', 794, 'MET', 0.5370860539231481, (105.0260009765625, 85.73500061035156, 94.875)), ('A', 798, 'LYS', 0.5113686770629392, (100.7969970703125, 79.7750015258789, 98.31300354003906)), ('A', 801, 'THR', 0.6185320409230712, (96.58899688720703, 74.447998046875, 90.73200225830078)), ('A', 802, 'GLU', 0.5181067646432175, (93.99400329589844, 71.70600128173828, 90.20600128173828)), ('A', 808, 'GLY', 0.5590069001779683, (86.3270034790039, 71.88899993896484, 94.2959976196289)), ('A', 836, 'ARG', 0.49798445563845445, (90.58899688720703, 76.87100219726562, 113.49500274658203)), ('A', 837, 'ILE', 0.4549856614127972, (87.12300109863281, 75.90399932861328, 114.74199676513672)), ('A', 851, 'ASP', 0.3417986473343514, (77.08599853515625, 86.1719970703125, 129.67100524902344)), ('A', 857, 'GLU', 0.443491268943702, (75.24700164794922, 82.0479965209961, 120.10299682617188)), ('A', 865, 'ASP', 0.5380095614247199, (80.35600280761719, 76.68599700927734, 110.04399871826172)), ('A', 876, 'GLU', 0.5633117886199547, (87.88999938964844, 62.452999114990234, 113.3280029296875)), ('A', 884, 'TYR', 0.6102211073825057, (80.0530014038086, 70.87100219726562, 119.11599731445312)), ('A', 893, 'ASP', 0.511096832756163, (70.25399780273438, 71.96800231933594, 129.30999755859375)), ('A', 911, 'ASN', 0.3444480354524506, (61.53200149536133, 72.98100280761719, 114.54100036621094)), ('A', 919, 'GLU', 0.5292846874439835, (68.5530014038086, 69.29399871826172, 111.20600128173828)), ('A', 928, 'HIS', 0.5438929644111004, (65.5459976196289, 75.78900146484375, 99.04299926757812)), ('B', 80, 'ARG', 0.5691449153396106, (74.9209976196289, 118.02100372314453, 119.34500122070312)), ('B', 94, 'MET', 0.5929288606566684, (94.82599639892578, 124.39600372314453, 121.45099639892578)), ('B', 98, 'LEU', 0.5040283881364889, (99.87300109863281, 127.8550033569336, 118.68399810791016)), ('B', 100, 'ASN', 0.4313075519342708, (105.0510025024414, 131.36300659179688, 118.75399780273438)), ('B', 112, 'ASP', 0.5147194212155626, (100.38600158691406, 133.9669952392578, 98.88200378417969)), ('B', 119, 'ILE', 0.6328445115410575, (107.51499938964844, 122.68900299072266, 107.91699981689453)), ('B', 125, 'ALA', 0.5504661219554448, (107.9209976196289, 124.23699951171875, 117.62699890136719)), ('B', 128, 'LEU', 0.5851936682429876, (111.81300354003906, 118.46199798583984, 120.45500183105469)), ('B', 133, 'PRO', 0.5550799554406859, (115.50299835205078, 102.572998046875, 120.35600280761719)), ('B', 134, 'ASP', 0.6048871913278605, (119.01300048828125, 101.427001953125, 121.30999755859375)), ('B', 143, 'ASP', 0.4705468075086367, (126.01699829101562, 113.36799621582031, 121.8949966430664)), ('B', 157, 'GLN', 0.6231379025884325, (116.16000366210938, 118.96700286865234, 128.93099975585938)), ('B', 167, 'VAL', 0.5562862567540564, (116.80500030517578, 108.87699890136719, 133.83099365234375)), ('B', 190, 'ARG', 0.5952970861170546, (115.29299926757812, 125.09100341796875, 121.22599792480469)), ('C', 5, 'ASP', 0.4328217815201543, (97.65899658203125, 71.19200134277344, 128.10299682617188)), ('C', 40, 'LEU', 0.4882852787562632, (102.75399780273438, 78.69999694824219, 121.3479995727539)), ('C', 52, 'MET', 0.4883103806839943, (107.1780014038086, 76.91100311279297, 130.9219970703125)), ('D', 97, 'LYS', 0.5575691721455276, (98.22899627685547, 67.88600158691406, 136.3000030517578)), ('D', 102, 'ALA', 0.4554045645105643, (111.02300262451172, 70.572998046875, 136.4149932861328)), ('D', 113, 'GLY', 0.213595061114563, (110.30599975585938, 79.85800170898438, 151.1699981689453)), ('D', 119, 'ILE', 0.35642174212972605, (114.62699890136719, 83.96099853515625, 135.76699829101562)), ('D', 125, 'ALA', 0.21180247111470407, (124.48699951171875, 79.97599792480469, 131.8520050048828)), ('D', 140, 'ASN', 0.2703608853454754, (118.54399871826172, 68.8550033569336, 149.51199340820312)), ('D', 143, 'ASP', 0.3687770863920695, (126.02400207519531, 68.78299713134766, 147.593994140625)), ('D', 148, 'THR', 0.41627456931622, (120.37300109863281, 71.2020034790039, 142.26800537109375)), ('D', 156, 'ILE', 0.43089508262072546, (128.39199829101562, 77.78199768066406, 142.39300537109375)), ('D', 189, 'LEU', 0.33957242236521457, (126.36799621582031, 80.37300109863281, 136.50599670410156))]
data['clusters'] = [('A', '330', 1, 'backbone clash\n', (96.673, 125.728, 105.379)), ('A', '333', 1, 'side-chain clash\nsmoc Outlier', (91.571, 133.026, 105.503)), ('A', '334', 1, 'smoc Outlier\n', (91.28500366210938, 135.25100708007812, 111.08300018310547)), ('A', '337', 1, 'cablam Outlier\n', (90.6, 138.4, 115.4)), ('A', '340', 1, 'smoc Outlier\n', (93.95700073242188, 129.9340057373047, 112.76499938964844)), ('A', '342', 1, 'backbone clash\n', (96.673, 125.728, 105.379)), ('A', '360', 1, 'smoc Outlier\n', (87.23300170898438, 132.82899475097656, 103.29900360107422)), ('A', '361', 1, 'side-chain clash\n', (91.571, 133.026, 105.503)), ('A', '380', 1, 'side-chain clash\n', (95.577, 124.177, 114.732)), ('A', '382', 1, 'smoc Outlier\n', (100.88500213623047, 119.62699890136719, 113.55400085449219)), ('A', '401', 1, 'side-chain clash\n', (101.333, 115.168, 117.924)), ('A', '419', 1, 'side-chain clash\n', (98.071, 121.767, 109.303)), ('A', '672', 1, 'smoc Outlier\n', (102.06900024414062, 111.13500213623047, 117.27799987792969)), ('A', '855', 1, 'side-chain clash\n', (99.884, 128.609, 112.112)), ('A', '848', 2, 'side-chain clash\n', (79.204, 85.654, 124.497)), ('A', '851', 2, 'smoc Outlier\n', (77.08599853515625, 86.1719970703125, 129.67100524902344)), ('A', '854', 2, 'side-chain clash\n', (79.204, 85.654, 124.497)), ('A', '856', 2, 'side-chain clash\n', (75.014, 78.685, 119.661)), ('A', '857', 2, 'smoc Outlier\n', (75.24700164794922, 82.0479965209961, 120.10299682617188)), ('A', '858', 2, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1\n', (78.96300000000001, 81.765, 119.315)), ('A', '859', 2, 'side-chain clash\n', (81.309, 78.061, 123.491)), ('A', '860', 2, 'side-chain clash\n', (75.014, 78.685, 119.661)), ('A', '862', 2, 'side-chain clash\n', (80.784, 79.711, 117.246)), ('A', '887', 2, 'side-chain clash\n', (79.236, 74.553, 126.699)), ('A', '891', 2, 'side-chain clash\n', (79.236, 74.553, 126.699)), ('A', '601', 3, 'side-chain clash\nsmoc Outlier', (81.849, 80.443, 90.131)), ('A', '605', 3, 'side-chain clash\n', (84.126, 81.942, 89.739)), ('A', '606', 3, 'cablam Outlier\nside-chain clash', (83.0, 76.7, 85.4)), ('A', '607', 3, 'cablam Outlier\n', (80.5, 78.0, 82.7)), ('A', '608', 3, 'cablam Outlier\n', (81.6, 76.1, 79.6)), ('A', '609', 3, 'side-chain clash\n', (84.044, 77.702, 82.495)), ('A', '612', 3, 'side-chain clash\n', (87.294, 71.777, 84.261)), ('A', '756', 3, 'side-chain clash\nsmoc Outlier', (84.126, 81.942, 89.739)), ('A', '805', 3, 'side-chain clash\n', (87.294, 71.777, 84.261)), ('A', '117', 4, 'side-chain clash\nsmoc Outlier', (130.694, 100.982, 64.005)), ('A', '192', 4, 'side-chain clash\n', (118.834, 106.382, 63.97)), ('A', '217', 4, 'cablam CA Geom Outlier\n', (121.8, 101.7, 65.2)), ('A', '218', 4, 'cablam Outlier\n', (119.9, 99.5, 62.7)), ('A', '219', 4, 'side-chain clash\n', (118.834, 106.382, 63.97)), ('A', '90', 4, 'smoc Outlier\n', (122.78600311279297, 111.18499755859375, 61.145999908447266)), ('A', '97', 4, 'smoc Outlier\n', (126.90899658203125, 104.48400115966797, 66.90799713134766)), ('A', '98', 4, 'side-chain clash\n', (130.694, 100.982, 64.005)), ('A', '42', 5, 'side-chain clash\n', (104.024, 86.534, 65.548)), ('A', '703', 5, 'smoc Outlier\n', (96.8239974975586, 87.5989990234375, 80.11900329589844)), ('A', '705', 5, 'smoc Outlier\n', (101.62000274658203, 89.95999908447266, 78.802001953125)), ('A', '706', 5, 'smoc Outlier\n', (101.16000366210938, 86.2300033569336, 78.17500305175781)), ('A', '707', 5, 'side-chain clash\n', (101.191, 86.734, 72.204)), ('A', '710', 5, 'side-chain clash\n', (101.607, 84.075, 70.127)), ('A', '712', 5, 'side-chain clash\n', (104.024, 86.534, 65.548)), ('A', '715', 5, 'side-chain clash\n', (101.607, 84.075, 70.127)), ('A', '468', 6, 'side-chain clash\n', (96.416, 97.455, 79.963)), ('A', '471', 6, 'smoc Outlier\n', (94.03900146484375, 99.48200225830078, 77.72200012207031)), ('A', '472', 6, 'side-chain clash\n', (96.416, 97.455, 79.963)), ('A', '474', 6, 'Dihedral angle:CB:CG:CD:OE1\n', (89.161, 99.896, 79.505)), ('A', '476', 6, 'side-chain clash\n', (91.193, 96.783, 82.584)), ('A', '696', 6, 'side-chain clash\n', (91.875, 91.861, 84.719)), ('A', '700', 6, 'side-chain clash\n', (91.875, 91.861, 84.719)), ('A', '452', 7, 'smoc Outlier\n', (104.01399993896484, 96.78500366210938, 112.33599853515625)), ('A', '544', 7, 'side-chain clash\n', (98.443, 97.035, 115.144)), ('A', '545', 7, 'side-chain clash\n', (92.614, 95.208, 114.183)), ('A', '553', 7, 'cablam Outlier\nsmoc Outlier', (101.9, 89.0, 113.7)), ('A', '555', 7, 'smoc Outlier\n', (97.06300354003906, 92.58599853515625, 112.95500183105469)), ('A', '556', 7, 'side-chain clash\nsmoc Outlier', (98.443, 97.035, 115.144)), ('A', '557', 7, 'side-chain clash\n', (92.614, 95.208, 114.183)), ('A', '527', 8, 'side-chain clash\n', (81.612, 117.471, 101.476)), ('A', '531', 8, 'side-chain clash\n', (86.243, 116.905, 97.625)), ('A', '533', 8, 'Dihedral angle:CD:NE:CZ:NH1\n', (84.819, 121.612, 95.503)), ('A', '535', 8, 'smoc Outlier\n', (90.13500213623047, 118.98799896240234, 99.58399963378906)), ('A', '567', 8, 'side-chain clash\n', (82.456, 112.829, 100.3)), ('A', '654', 8, 'side-chain clash\n', (82.456, 112.829, 100.3)), ('A', '657', 8, 'side-chain clash\n', (86.243, 116.905, 97.625)), ('A', '196', 9, 'side-chain clash\n', (112.563, 110.239, 65.475)), ('A', '203', 9, 'side-chain clash\n', (112.253, 105.587, 60.725)), ('A', '204', 9, 'side-chain clash\n', (107.374, 105.215, 65.482)), ('A', '222', 9, 'side-chain clash\n', (112.253, 105.587, 60.725)), ('A', '223', 9, 'side-chain clash\n', (110.853, 108.516, 55.29)), ('A', '232', 9, 'side-chain clash\n', (112.563, 110.239, 65.475)), ('A', '233', 9, 'side-chain clash\nsmoc Outlier', (107.374, 105.215, 65.482)), ('A', '136', 10, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\n', (114.21100000000001, 82.482, 88.99900000000001)), ('A', '138', 10, 'smoc Outlier\n', (116.08699798583984, 81.18299865722656, 84.01499938964844)), ('A', '139', 10, 'cablam Outlier\n', (117.1, 84.8, 85.0)), ('A', '143', 10, 'smoc Outlier\n', (122.41300201416016, 88.25299835205078, 86.56199645996094)), ('A', '145', 10, 'smoc Outlier\n', (123.90399932861328, 92.26100158691406, 83.08000183105469)), ('A', '149', 10, 'side-chain clash\n', (124.298, 96.418, 79.753)), ('A', '212', 10, 'side-chain clash\n', (124.298, 96.418, 79.753)), ('A', '125', 11, 'smoc Outlier\n', (115.2770004272461, 95.45800018310547, 75.1240005493164)), ('A', '128', 11, 'side-chain clash\n', (110.248, 96.048, 79.605)), ('A', '132', 11, 'side-chain clash\n', (106.563, 98.434, 78.725)), ('A', '239', 11, 'smoc Outlier\n', (105.73999786376953, 103.10099792480469, 77.23400115966797)), ('A', '240', 11, 'side-chain clash\n', (106.563, 98.434, 78.725)), ('A', '268', 12, 'side-chain clash\nsmoc Outlier', (113.433, 119.819, 96.597)), ('A', '272', 12, 'side-chain clash\n', (113.08, 124.673, 93.284)), ('A', '274', 12, 'cablam Outlier\nsmoc Outlier', (104.9, 124.5, 93.4)), ('A', '275', 12, 'cablam Outlier\nside-chain clash', (107.7, 122.8, 91.4)), ('A', '322', 12, 'side-chain clash\n', (113.433, 119.819, 96.597)), ('A', '290', 13, 'side-chain clash\n', (101.28, 111.035, 77.306)), ('A', '291', 13, 'smoc Outlier\n', (103.36799621582031, 113.33300018310547, 71.58999633789062)), ('A', '309', 13, 'side-chain clash\n', (100.511, 107.784, 79.837)), ('A', '312', 13, 'smoc Outlier\n', (101.70099639892578, 108.56500244140625, 86.01599884033203)), ('A', '466', 13, 'side-chain clash\n', (100.511, 107.784, 79.837)), ('A', '367', 14, 'backbone clash\n', (77.988, 124.99, 111.526)), ('A', '368', 14, 'backbone clash\n', (77.988, 124.99, 111.526)), ('A', '369', 14, 'smoc Outlier\n', (80.3949966430664, 122.1719970703125, 109.08399963378906)), ('A', '372', 14, 'side-chain clash\n', (83.771, 116.298, 109.906)), ('A', '563', 14, 'side-chain clash\n', (83.771, 116.298, 109.906)), ('A', '658', 15, 'smoc Outlier\n', (89.86499786376953, 110.2509994506836, 98.3740005493164)), ('A', '660', 15, 'side-chain clash\n', (94.928, 110.858, 103.703)), ('A', '661', 15, 'smoc Outlier\n', (91.73899841308594, 111.12699890136719, 102.94100189208984)), ('A', '665', 15, 'side-chain clash\nsmoc Outlier', (94.928, 110.858, 103.703)), ('A', '488', 16, 'side-chain clash\n', (73.357, 107.444, 100.468)), ('A', '493', 16, 'side-chain clash\n', (73.357, 107.444, 100.468)), ('A', '494', 16, 'side-chain clash\n', (74.52, 102.726, 103.641)), ('A', '573', 16, 'side-chain clash\n', (74.52, 102.726, 103.641)), ('A', '818', 17, 'backbone clash\n', (81.313, 68.091, 105.234)), ('A', '820', 17, 'side-chain clash\n', (78.403, 67.825, 100.575)), ('A', '829', 17, 'side-chain clash\n', (78.403, 67.825, 100.575)), ('A', '868', 17, 'backbone clash\n', (81.313, 68.091, 105.234)), ('A', '388', 18, 'backbone clash\n', (110.424, 112.543, 117.074)), ('A', '389', 18, 'backbone clash\n', (110.424, 112.543, 117.074)), ('A', '390', 18, 'smoc Outlier\n', (111.45500183105469, 108.89199829101562, 115.64299774169922)), ('A', '393', 18, 'smoc Outlier\n', (110.89600372314453, 103.83799743652344, 111.89600372314453)), ('A', '758', 19, 'side-chain clash\nDihedral angle:CA:C\n', (86.65299999999999, 88.331, 96.088)), ('A', '759', 19, 'cablam Outlier\nside-chain clash\nDihedral angle:N:CA', (88.6, 91.2, 97.6)), ('A', '761', 19, 'smoc Outlier\n', (91.30500030517578, 85.9020004272461, 97.03800201416016)), ('A', '411', 20, 'smoc Outlier\n', (96.77200317382812, 90.94000244140625, 126.27300262451172)), ('A', '413', 20, 'side-chain clash\n', (92.401, 87.102, 124.867)), ('A', '546', 20, 'side-chain clash\n', (92.401, 87.102, 124.867)), ('A', '615', 21, 'side-chain clash\n', (94.422, 81.051, 86.844)), ('A', '755', 21, 'side-chain clash\n', (90.225, 84.168, 86.652)), ('A', '764', 21, 'side-chain clash\n', (94.422, 81.051, 86.844)), ('A', '415', 22, 'side-chain clash\n', (89.662, 75.326, 129.848)), ('A', '416', 22, 'smoc Outlier\n', (87.47899627685547, 78.54000091552734, 128.42599487304688)), ('A', '417', 22, 'side-chain clash\n', (89.662, 75.326, 129.848)), ('A', '572', 23, 'side-chain clash\n', (79.507, 102.107, 96.627)), ('A', '575', 23, 'smoc Outlier\n', (77.44499969482422, 101.19499969482422, 93.32099914550781)), ('A', '576', 23, 'side-chain clash\n', (79.507, 102.107, 96.627)), ('A', '200', 24, 'backbone clash\nsmoc Outlier', (111.981, 114.941, 59.185)), ('A', '226', 24, 'smoc Outlier\n', (111.95800018310547, 117.2040023803711, 53.571998596191406)), ('A', '230', 24, 'backbone clash\n', (111.981, 114.941, 59.185)), ('A', '726', 25, 'smoc Outlier\n', (95.20700073242188, 93.81999969482422, 66.83699798583984)), ('A', '729', 25, 'Dihedral angle:CB:CG:CD:OE1\n', (98.15499999999999, 97.60199999999999, 67.362)), ('A', '734', 25, 'smoc Outlier\n', (96.32599639892578, 103.25599670410156, 68.30500030517578)), ('A', '614', 26, 'side-chain clash\n', (91.9, 73.306, 89.988)), ('A', '801', 26, 'smoc Outlier\n', (96.58899688720703, 74.447998046875, 90.73200225830078)), ('A', '802', 26, 'side-chain clash\nsmoc Outlier', (91.9, 73.306, 89.988)), ('A', '602', 27, 'side-chain clash\n', (85.481, 75.34, 93.3)), ('A', '808', 27, 'smoc Outlier\n', (86.3270034790039, 71.88899993896484, 94.2959976196289)), ('A', '809', 27, 'side-chain clash\n', (85.481, 75.34, 93.3)), ('A', '205', 28, 'side-chain clash\n', (114.637, 104.343, 69.402)), ('A', '216', 28, 'side-chain clash\n', (114.637, 104.343, 69.402)), ('A', '689', 29, 'side-chain clash\n', (87.569, 96.771, 93.182)), ('A', '693', 29, 'side-chain clash\n', (87.569, 96.771, 93.182)), ('A', '819', 30, 'side-chain clash\n', (78.555, 66.017, 92.604)), ('A', '826', 30, 'side-chain clash\n', (78.555, 66.017, 92.604)), ('A', '285', 31, 'Dihedral angle:CD:NE:CZ:NH1\n', (114.68199999999999, 117.29, 79.288)), ('A', '286', 31, 'smoc Outlier\n', (113.72899627685547, 113.60399627685547, 79.16799926757812)), ('A', '816', 32, 'side-chain clash\n', (84.435, 74.097, 101.044)), ('A', '830', 32, 'side-chain clash\n', (84.435, 74.097, 101.044)), ('A', '677', 33, 'cablam CA Geom Outlier\n', (103.7, 106.3, 101.7)), ('A', '678', 33, 'cablam CA Geom Outlier\n', (100.5, 104.7, 100.3)), ('A', '420', 34, 'side-chain clash\n', (88.994, 68.727, 127.408)), ('A', '424', 34, 'side-chain clash\n', (88.994, 68.727, 127.408)), ('A', '836', 35, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (90.589, 76.871, 113.495)), ('A', '837', 35, 'smoc Outlier\n', (87.12300109863281, 75.90399932861328, 114.74199676513672)), ('A', '578', 36, 'side-chain clash\nsmoc Outlier', (74.942, 94.148, 91.822)), ('A', '582', 36, 'side-chain clash\n', (74.942, 94.148, 91.822)), ('A', '186', 37, 'side-chain clash\n', (114.582, 104.97, 79.22)), ('A', '241', 37, 'side-chain clash\n', (114.582, 104.97, 79.22)), ('A', '785', 38, 'smoc Outlier\n', (103.46700286865234, 90.99400329589844, 86.69300079345703)), ('A', '786', 38, 'smoc Outlier\n', (103.60600280761719, 91.16799926757812, 90.48500061035156)), ('A', '515', 39, 'side-chain clash\n', (76.395, 113.832, 112.755)), ('A', '519', 39, 'side-chain clash\n', (75.817, 116.395, 109.31)), ('A', '430', 40, 'smoc Outlier\n', (95.44200134277344, 62.73899841308594, 121.7020034790039)), ('A', '431', 40, 'Dihedral angle:CB:CG:CD:OE1\n', (98.90400000000001, 62.073, 120.30499999999999)), ('A', '254', 41, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (118.30499999999999, 115.342, 89.281)), ('A', '259', 41, 'cablam Outlier\n', (123.0, 117.3, 88.0)), ('A', '884', 42, 'side-chain clash\nsmoc Outlier', (77.932, 72.114, 119.614)), ('A', '888', 42, 'side-chain clash\n', (77.932, 72.114, 119.614)), ('A', '501', 43, 'smoc Outlier\n', (85.94000244140625, 104.33000183105469, 115.43599700927734)), ('A', '502', 43, 'smoc Outlier\n', (85.19200134277344, 107.8270034790039, 114.13999938964844)), ('B', '132', 1, 'side-chain clash\n', (119.699, 106.348, 122.229)), ('B', '133', 1, 'smoc Outlier\n', (115.50299835205078, 102.572998046875, 120.35600280761719)), ('B', '134', 1, 'smoc Outlier\n', (119.01300048828125, 101.427001953125, 121.30999755859375)), ('B', '135', 1, 'jpred outlier', (122.4, 102.7, 122.4)), ('B', '138', 1, 'side-chain clash\n', (119.699, 106.348, 122.229)), ('B', '161', 1, 'side-chain clash\n', (114.361, 105.34, 128.644)), ('B', '162', 1, 'cablam Outlier\n', (109.7, 103.7, 128.6)), ('B', '167', 1, 'smoc Outlier\n', (116.80500030517578, 108.87699890136719, 133.83099365234375)), ('B', '182', 1, 'cablam CA Geom Outlier\n', (114.6, 101.1, 126.0)), ('B', '184', 1, 'side-chain clash\n', (114.361, 105.34, 128.644)), ('B', '103', 2, 'side-chain clash\n', (99.884, 128.609, 112.112)), ('B', '91', 2, 'side-chain clash\n', (92.181, 126.751, 118.678)), ('B', '94', 2, 'smoc Outlier\n', (94.82599639892578, 124.39600372314453, 121.45099639892578)), ('B', '95', 2, 'side-chain clash\n', (92.181, 126.751, 118.678)), ('B', '96', 2, 'Dihedral angle:CD:NE:CZ:NH1\n', (96.903, 129.1, 123.118)), ('B', '98', 2, 'side-chain clash\nsmoc Outlier', (95.937, 126.634, 115.459)), ('B', '120', 3, 'side-chain clash\n', (106.5, 125.656, 112.81)), ('B', '124', 3, 'side-chain clash\n', (106.5, 125.656, 112.81)), ('B', '125', 3, 'smoc Outlier\n', (107.9209976196289, 124.23699951171875, 117.62699890136719)), ('B', '159', 4, 'side-chain clash\n', (117.596, 111.949, 126.288)), ('B', '186', 4, 'side-chain clash\n', (117.596, 111.949, 126.288)), ('B', '115', 5, 'side-chain clash\n', (105.534, 126.667, 105.028)), ('B', '119', 5, 'side-chain clash\nsmoc Outlier', (105.534, 126.667, 105.028)), ('B', '112', 6, 'cablam CA Geom Outlier\nsmoc Outlier', (100.4, 134.0, 98.9)), ('B', '113', 6, 'jpred outlier', (101.1, 133.1, 102.6)), ('B', '83', 7, 'side-chain clash\n', (82.077, 119.516, 118.966)), ('B', '87', 7, 'side-chain clash\n', (82.077, 119.516, 118.966)), ('B', '79', 8, 'jpred outlier', (74.0, 116.0, 122.5)), ('B', '80', 8, 'smoc Outlier\n', (74.9209976196289, 118.02100372314453, 119.34500122070312)), ('B', '100', 9, 'smoc Outlier\n', (105.0510025024414, 131.36300659179688, 118.75399780273438)), ('B', '101', 9, 'cablam Outlier\n', (105.9, 134.4, 116.6)), ('C', '10', 1, 'side-chain clash\n', (102.677, 78.448, 127.649)), ('C', '13', 1, 'side-chain clash\n', (103.719, 80.651, 132.107)), ('C', '14', 1, 'side-chain clash\n', (101.876, 84.598, 126.431)), ('C', '35', 1, 'side-chain clash\n', (107.307, 79.993, 125.087)), ('C', '36', 1, 'side-chain clash\n', (101.876, 84.598, 126.431)), ('C', '39', 1, 'side-chain clash\n', (102.677, 78.448, 127.649)), ('C', '40', 1, 'smoc Outlier\n', (102.75399780273438, 78.69999694824219, 121.3479995727539)), ('C', '52', 1, 'side-chain clash\nsmoc Outlier', (103.064, 77.963, 133.551)), ('C', '54', 1, 'side-chain clash\n', (110.024, 82.957, 134.05)), ('C', '55', 1, 'side-chain clash\n', (103.719, 80.651, 132.107)), ('C', '58', 1, 'side-chain clash\n', (110.024, 82.957, 134.05)), ('C', '28', 2, 'side-chain clash\n', (102.596, 71.137, 130.44)), ('C', '31', 2, 'side-chain clash\n', (102.596, 71.137, 130.44)), ('C', '4', 2, 'jpred outlier', (98.0, 70.6, 124.3)), ('C', '5', 2, 'smoc Outlier\njpred outlier', (97.65899658203125, 71.19200134277344, 128.10299682617188)), ('C', '17', 3, 'side-chain clash\n', (104.557, 88.528, 135.563)), ('C', '22', 3, 'side-chain clash\n', (104.557, 88.528, 135.563)), ('C', '49', 4, 'side-chain clash\n', (110.202, 74.569, 131.862)), ('C', '53', 4, 'side-chain clash\n', (110.202, 74.569, 131.862)), ('C', '23', 5, 'Dihedral angle:CB:CG:CD:OE1\n', (102.76700000000001, 94.692, 131.98600000000002)), ('D', '92', 1, 'side-chain clash\n', (99.265, 74.923, 138.54)), ('D', '93', 1, 'side-chain clash\n', (95.67, 69.727, 137.561)), ('D', '94', 1, 'side-chain clash\n', (98.932, 70.96, 134.886)), ('D', '95', 1, 'side-chain clash\n', (99.265, 74.923, 138.54)), ('D', '97', 1, 'side-chain clash\nsmoc Outlier', (95.67, 69.727, 137.561)), ('D', '98', 1, 'side-chain clash\n', (102.596, 71.137, 130.44)), ('D', '147', 2, 'side-chain clash\n', (123.387, 74.972, 141.171)), ('D', '148', 2, 'smoc Outlier\n', (120.37300109863281, 71.2020034790039, 142.26800537109375)), ('D', '154', 2, 'side-chain clash\n', (123.387, 74.972, 141.171)), ('D', '156', 2, 'side-chain clash\nsmoc Outlier', (127.664, 75.424, 142.642)), ('D', '186', 2, 'side-chain clash\n', (124.297, 79.056, 144.564)), ('D', '159', 3, 'side-chain clash\n', (129.788, 84.984, 148.782)), ('D', '166', 3, 'side-chain clash\n', (129.788, 84.984, 148.782)), ('D', '168', 3, 'side-chain clash\n', (133.495, 82.812, 151.723)), ('D', '110', 4, 'side-chain clash\n', (109.055, 80.265, 145.905)), ('D', '113', 4, 'smoc Outlier\n', (110.30599975585938, 79.85800170898438, 151.1699981689453)), ('D', '115', 4, 'side-chain clash\n', (109.055, 80.265, 145.905)), ('D', '134', 5, 'cablam Outlier\n', (118.3, 79.6, 157.6)), ('D', '162', 5, 'side-chain clash\n', (119.918, 88.047, 153.74)), ('D', '183', 5, 'cablam CA Geom Outlier\nside-chain clash', (118.5, 84.9, 153.3)), ('D', '124', 6, 'cablam Outlier\nside-chain clash', (124.2, 81.0, 128.1)), ('D', '125', 6, 'smoc Outlier\n', (124.48699951171875, 79.97599792480469, 131.8520050048828)), ('D', '189', 6, 'smoc Outlier\n', (126.36799621582031, 80.37300109863281, 136.50599670410156)), ('D', '102', 7, 'smoc Outlier\n', (111.02300262451172, 70.572998046875, 136.4149932861328)), ('D', '103', 7, 'side-chain clash\n', (106.63, 73.383, 139.991)), ('D', '107', 7, 'side-chain clash\n', (106.63, 73.383, 139.991)), ('D', '119', 8, 'smoc Outlier\n', (114.62699890136719, 83.96099853515625, 135.76699829101562)), ('D', '120', 8, 'side-chain clash\n', (115.249, 81.24, 136.816)), ('D', '140', 9, 'smoc Outlier\n', (118.54399871826172, 68.8550033569336, 149.51199340820312)), ('D', '143', 9, 'smoc Outlier\n', (126.02400207519531, 68.78299713134766, 147.593994140625))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (90.308, 113.568, 115.66700000000002)), ('B', ' 183 ', 'PRO', None, (112.63000000000002, 101.92399999999998, 124.669))]
data['cablam'] = [('A', '139', 'CYS', 'check CA trace,carbonyls, peptide', ' \nSS-HH', (117.1, 84.8, 85.0)), ('A', '218', 'ASP', 'check CA trace,carbonyls, peptide', ' \nB----', (119.9, 99.5, 62.7)), ('A', '259', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nTTS-T', (123.0, 117.3, 88.0)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (104.9, 124.5, 93.4)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (107.7, 122.8, 91.4)), ('A', '337', 'GLY', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (90.6, 138.4, 115.4)), ('A', '553', 'ARG', ' beta sheet', ' \nS----', (101.9, 89.0, 113.7)), ('A', '606', 'TYR', 'check CA trace,carbonyls, peptide', 'helix\nHHHSS', (83.0, 76.7, 85.4)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nHHSS-', (80.5, 78.0, 82.7)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nHSS-S', (81.6, 76.1, 79.6)), ('A', '759', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (88.6, 91.2, 97.6)), ('A', '824', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (69.7, 62.5, 94.6)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (126.4, 96.7, 90.0)), ('A', '217', 'TYR', 'check CA trace', ' \n-B---', (121.8, 101.7, 65.2)), ('A', '326', 'PHE', 'check CA trace', ' \nGG-EE', (104.1, 117.6, 100.0)), ('A', '677', 'PRO', 'check CA trace', ' \nE--S-', (103.7, 106.3, 101.7)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (100.5, 104.7, 100.3)), ('B', '101', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n--SHH', (105.9, 134.4, 116.6)), ('B', '162', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nE-TTS', (109.7, 103.7, 128.6)), ('B', '112', 'ASP', 'check CA trace', 'helix-3\nSGGG-', (100.4, 134.0, 98.9)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-S-E', (114.6, 101.1, 126.0)), ('D', '124', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (124.2, 81.0, 128.1)), ('D', '134', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nE-TTS', (118.3, 79.6, 157.6)), ('D', '183', 'PRO', 'check CA trace', ' \n-S-EE', (118.5, 84.9, 153.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30209/7bv1/Model_validation_4/validation_cootdata/molprobity_probe7bv1_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

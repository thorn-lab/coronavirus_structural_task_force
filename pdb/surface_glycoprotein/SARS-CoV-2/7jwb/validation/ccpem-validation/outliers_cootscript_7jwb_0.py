
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
data['smoc'] = []
data['jpred'] = []
data['probe'] = [(' B 332  ILE  HB ', ' B 362  VAL HG21', -0.781, (218.194, 256.317, 183.524)), (' D 100  ARG  HB3', ' D 116  TYR  HB2', -0.679, (208.466, 233.372, 154.927)), (' B 332  ILE HG21', ' B 527  PRO  HA ', -0.65, (216.5, 254.873, 184.243)), (' A 954  GLN  HB3', ' A1014  ARG  HE ', -0.56, (220.635, 201.855, 228.248)), (' C 215  ASP  N  ', ' C 266  TYR  HH ', -0.554, (258.934, 247.055, 205.005)), (' C 811  LYS  NZ ', ' C 820  ASP  OD2', -0.55, (218.524, 248.44, 245.44)), (' B 389  ASP  OD1', ' B 529  LYS  NZ ', -0.547, (210.756, 248.141, 182.329)), (' A1083  HIS  HB2', ' A1137  VAL HG23', -0.542, (200.408, 205.885, 292.827)), (' A 522  ALA  H  ', ' A 544  ASN HD21', -0.54, (179.365, 201.01, 192.6)), (' B 811  LYS  NZ ', ' B 820  ASP  OD2', -0.481, (180.564, 200.612, 248.246)), (' C 574  ASP  OD1', ' C 575  ALA  N  ', -0.475, (237.93, 190.377, 209.07)), (' A 571  ASP  OD2', ' B 964  LYS  NZ ', -0.474, (188.761, 210.759, 212.817)), (' C  92  PHE  HB2', ' C 192  PHE  HB2', -0.472, (247.5, 246.544, 196.643)), (' B 577  ARG HH11', ' B 582  LEU  HB3', -0.467, (223.265, 257.294, 201.327)), (' A1084  ASP  N  ', ' A1084  ASP  OD1', -0.467, (197.37, 209.052, 294.408)), (' A 126  VAL  HB ', ' A 170  TYR  HB2', -0.465, (234.951, 166.496, 187.579)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.456, (241.363, 191.892, 247.616)), (' C1028  LYS  NZ ', ' C1042  PHE  O  ', -0.453, (219.385, 222.17, 251.541)), (' B1084  ASP  N  ', ' B1084  ASP  OD1', -0.443, (218.861, 233.647, 293.607)), (' C1142  GLN  N  ', ' C1143  PRO  CD ', -0.442, (222.984, 216.656, 301.485)), (' A 657  ASN  N  ', ' A 657  ASN  OD1', -0.429, (193.84, 174.958, 242.232)), (' A 327  VAL  H  ', ' A 531  THR HG22', -0.425, (182.268, 187.124, 196.266)), (' B 908  GLY  O  ', ' B1038  LYS  NZ ', -0.422, (207.424, 214.95, 267.359)), (' C 186  PHE  HB3', ' C 187  LYS  H  ', -0.421, (256.16, 259.789, 202.166)), (' B 455  LEU  HB3', ' D 250  PHE  CZ ', -0.42, (224.698, 246.078, 142.826)), (' A 391  CYS  O  ', ' A 392  PHE  HB2', -0.418, (183.791, 202.616, 186.528)), (' C 908  GLY  O  ', ' C1038  LYS  NZ ', -0.418, (217.174, 219.404, 266.565)), (' A1098  ASN  N  ', ' A1098  ASN  OD1', -0.418, (203.667, 192.06, 286.704)), (' C 867  ASP  N  ', ' C 867  ASP  OD1', -0.416, (208.532, 240.418, 239.113)), (' C 395  VAL HG22', ' C 515  PHE  HD2', -0.414, (233.118, 189.954, 174.292)), (' A 440  ASN  N  ', ' A 440  ASN  OD1', -0.414, (192.371, 203.828, 156.961)), (' C1039  ARG  HB2', ' C1042  PHE  HB2', -0.412, (218.142, 218.07, 255.388)), (' C 528  LYS  NZ ', ' C 544  ASN  O  ', -0.41, (239.195, 193.641, 193.144)), (' B1098  ASN  N  ', ' B1098  ASN  OD1', -0.41, (199.706, 236.539, 284.794)), (' A 917  TYR  HA ', ' A 920  GLN  HG3', -0.41, (227.975, 197.758, 277.251)), (' A 866  THR  H  ', ' A 869  MET  HE3', -0.408, (240.081, 209.036, 239.959)), (' B 200  TYR  CG ', ' B 230  PRO  HA ', -0.407, (176.807, 216.611, 185.914)), (' B 440  ASN  N  ', ' B 440  ASN  OD1', -0.404, (214.73, 264.329, 153.417)), (' C1084  ASP  N  ', ' C1084  ASP  OD1', -0.404, (227.909, 202.495, 294.57)), (' B 344  ALA  O  ', ' B 509  ARG  NH1', -0.402, (221.385, 261.851, 159.708))]
data['cbeta'] = [('A', ' 525 ', 'CYS', ' ', 0.2536463488085233, (181.364, 196.384, 187.789)), ('B', ' 333 ', 'THR', ' ', 0.262334425354993, (221.711, 260.74400000000014, 186.162)), ('C', ' 361 ', 'CYS', ' ', 0.31620727960201256, (239.94900000000007, 182.056, 179.916))]
data['rota'] = [('D', ' 148 ', 'GLU', 0.039168615443818944, (208.8, 241.394, 125.363)), ('D', ' 295 ', 'GLU', 8.08463823432474e-06, (233.676, 202.635, 127.725)), ('D', ' 313 ', 'ARG', 0.08755581753692442, (243.651, 180.394, 119.65)), ('A', '  31 ', 'SER', 0.043250290675848166, (215.702, 165.43, 208.945)), ('A', ' 855 ', 'PHE', 0.10336738399597878, (236.015, 203.223, 214.995)), ('A', '1014 ', 'ARG', 0.05528190325620265, (218.84199999999996, 207.322, 230.41)), ('B', '  34 ', 'ARG', 0.000203689161477883, (169.777, 226.799, 207.931)), ('B', ' 140 ', 'PHE', 0.23573229660009332, (155.68999999999994, 231.194, 186.078)), ('B', ' 324 ', 'GLU', 0.0013522207182105619, (200.81, 249.966, 200.881)), ('B', ' 332 ', 'ILE', 0.0, (219.09, 257.014, 186.116)), ('B', ' 334 ', 'ASN', 0.10086882123470323, (222.225, 260.732, 181.88)), ('B', ' 335 ', 'LEU', 0.08384928183471126, (220.667, 258.445, 179.214)), ('B', ' 725 ', 'GLU', 0.28997944260932806, (196.775, 214.226, 249.41899999999998)), ('B', ' 815 ', 'ARG', 0.1861811283041515, (186.926, 198.617, 249.449)), ('B', '1107 ', 'ARG', 0.00939954293087268, (205.047, 225.52700000000004, 274.14)), ('C', ' 140 ', 'PHE', 0.10841003168949993, (255.433, 253.51, 180.58)), ('C', ' 186 ', 'PHE', 0.2528350898430445, (257.292, 257.574, 201.437)), ('C', ' 382 ', 'VAL', 0.006254039180930704, (233.162, 199.139, 172.976)), ('C', '1039 ', 'ARG', 0.0009882846594753093, (218.43900000000005, 216.742, 257.614))]
data['clusters'] = [('D', '100', 1, 'side-chain clash\nBond angle:C', (205.74499999999998, 233.484, 154.736)), ('D', '101', 1, 'Bond angle:N:CA', (203.287, 232.879, 157.637)), ('D', '116', 1, 'side-chain clash', (208.466, 233.372, 154.927)), ('A', '220', 1, 'Bond angle:CA:CB:CG\ncablam CA Geom Outlier', (224.947, 169.201, 212.918)), ('A', '31', 1, 'Rotamer', (215.702, 165.43, 208.945)), ('A', '33', 1, 'cablam CA Geom Outlier', (219.4, 168.1, 211.9)), ('A', '34', 1, 'cablam CA Geom Outlier', (221.1, 167.9, 208.4)), ('A', '55', 1, 'Bond angle:CA:CB:CG', (218.256, 175.172, 203.83)), ('A', '57', 1, 'Bond angle:C', (213.824, 172.52, 207.21399999999997)), ('A', '58', 1, 'Bond angle:N:CA', (214.469, 170.76299999999998, 210.41899999999998)), ('A', '59', 1, 'Bond angle:CA:CB:CG', (212.415, 167.661, 211.024)), ('A', '310', 2, 'cablam CA Geom Outlier', (213.5, 182.0, 232.9)), ('A', '600', 2, 'Bond angle:C', (211.74399999999997, 178.313, 232.9)), ('A', '601', 2, 'Bond angle:N:CA', (215.208, 178.529, 231.565)), ('A', '604', 2, 'cablam Outlier', (215.8, 173.7, 233.8)), ('A', '332', 3, 'cablam Outlier', (174.9, 195.9, 185.9)), ('A', '333', 3, 'Ramachandran', (175.808, 193.453, 183.044)), ('A', '334', 3, 'cablam Outlier', (175.2, 195.1, 179.6)), ('A', '86', 4, 'cablam Outlier', (214.1, 169.9, 191.6)), ('A', '87', 4, 'cablam Outlier', (211.9, 172.8, 193.0)), ('A', '88', 4, 'cablam Outlier', (214.2, 175.5, 194.4)), ('A', '1014', 5, 'Rotamer', (218.84199999999996, 207.322, 230.41)), ('A', '525', 5, 'C-beta\nside-chain clash', (220.635, 201.855, 228.248)), ('A', '955', 5, 'Bond angle:CA:CB:CG', (224.923, 201.44, 227.371)), ('A', '205', 6, 'Bond angle:C', (228.977, 168.849, 200.258)), ('A', '206', 6, 'Bond angle:N:CA', (230.67, 166.54899999999998, 202.83200000000002)), ('A', '208', 6, 'cablam Outlier', (230.5, 162.4, 206.2)), ('A', '1028', 7, 'Bond angle:C', (221.893, 208.937, 251.771)), ('A', '1029', 7, 'Bond angle:N:CA', (225.499, 209.442, 252.353)), ('A', '1034', 7, 'cablam Outlier', (227.3, 211.6, 258.0)), ('A', '100', 8, 'Bond angle:C', (226.72, 153.14499999999998, 193.27899999999997)), ('A', '101', 8, 'Bond angle:N:CA', (225.623, 156.68, 192.686)), ('A', '242', 8, 'Bond length:CB:CG', (223.21699999999998, 153.96, 190.05)), ('A', '666', 9, 'cablam Outlier', (201.7, 186.8, 233.7)), ('A', '667', 9, 'cablam Outlier', (199.2, 189.5, 234.6)), ('A', '986', 10, 'Bond angle:CA:C', (226.63899999999998, 212.448, 190.68800000000002)), ('A', '987', 10, 'Bond angle:N', (223.031, 213.977, 190.754)), ('A', '391', 11, 'side-chain clash\ncablam Outlier', (183.791, 202.616, 186.528)), ('A', '392', 11, 'side-chain clash', (183.791, 202.616, 186.528)), ('A', '126', 12, 'side-chain clash', (234.951, 166.496, 187.579)), ('A', '170', 12, 'side-chain clash', (234.951, 166.496, 187.579)), ('A', '796', 13, 'Bond angle:CA:CB:CG', (240.047, 199.048, 269.617)), ('A', '797', 13, 'Bond angle:CA:CB:CG\ncablam CA Geom Outlier', (236.465, 199.65800000000002, 268.805)), ('A', '327', 14, 'side-chain clash', (182.268, 187.124, 196.266)), ('A', '531', 14, 'side-chain clash', (182.268, 187.124, 196.266)), ('A', '522', 15, 'side-chain clash', (188.761, 210.759, 212.817)), ('A', '544', 15, 'side-chain clash', (188.761, 210.759, 212.817)), ('A', '811', 16, 'side-chain clash', (241.363, 191.892, 247.616)), ('A', '820', 16, 'side-chain clash', (241.363, 191.892, 247.616)), ('A', '917', 17, 'side-chain clash\nBond angle:CA:CB:CG', (226.624, 198.08200000000002, 278.26599999999996)), ('A', '920', 17, 'side-chain clash\nBond length:CG:CD', (228.55, 195.118, 274.7)), ('A', '866', 18, 'side-chain clash', (240.081, 209.036, 239.959)), ('A', '869', 18, 'side-chain clash', (240.081, 209.036, 239.959)), ('B', '332', 1, 'Rotamer\nside-chain clash\ncablam Outlier', (216.5, 254.873, 184.243)), ('B', '333', 1, 'C-beta\ncablam Outlier', (221.711, 260.74400000000014, 186.162)), ('B', '334', 1, 'Rotamer', (222.225, 260.732, 181.88)), ('B', '335', 1, 'Rotamer', (220.667, 258.445, 179.214)), ('B', '362', 1, 'side-chain clash', (218.194, 256.317, 183.524)), ('B', '363', 1, 'Bond angle:N:CA:CB', (218.80100000000002, 252.511, 177.622)), ('B', '527', 1, 'side-chain clash', (216.5, 254.873, 184.243)), ('B', '1036', 2, 'Ramachandran\ncablam Outlier', (205.03, 210.162, 262.044)), ('B', '1042', 2, 'Bond angle:CA:CB:CG', (204.95700000000002, 216.88800000000003, 254.304)), ('B', '1043', 2, 'cablam CA Geom Outlier', (201.7, 215.4, 255.6)), ('B', '1048', 2, 'Bond length:CB:CG', (201.51, 215.805, 261.941)), ('B', '456', 3, 'Bond angle:CA:CB:CG', (229.14899999999997, 241.782, 143.80800000000002)), ('B', '577', 3, 'side-chain clash\nbackbone clash', (224.698, 246.078, 142.826)), ('B', '582', 3, 'side-chain clash\nbackbone clash', (224.698, 246.078, 142.826)), ('B', '130', 4, 'Bond angle:C', (168.907, 221.24899999999997, 179.318)), ('B', '131', 4, 'Bond angle:N:CA', (167.58, 222.259, 175.833)), ('B', '164', 4, 'Bond angle:CA:CB:CG', (166.277, 222.5, 169.99200000000002)), ('B', '200', 5, 'side-chain clash', (176.807, 216.611, 185.914)), ('B', '230', 5, 'side-chain clash', (176.807, 216.611, 185.914)), ('B', '231', 5, 'cablam Outlier', (174.5, 218.6, 182.8)), ('B', '86', 6, 'cablam Outlier', (173.4, 232.0, 191.6)), ('B', '87', 6, 'cablam Outlier', (177.1, 232.6, 192.1)), ('B', '88', 6, 'cablam Outlier', (178.6, 229.3, 193.1)), ('B', '140', 7, 'Rotamer', (155.68999999999994, 231.194, 186.078)), ('B', '242', 7, 'Bond length:CB:CG', (155.798, 230.84, 190.598)), ('B', '81', 7, 'Bond angle:CA:CB:CG', (159.67899999999997, 236.404, 189.414)), ('B', '811', 8, 'side-chain clash', (180.564, 200.612, 248.246)), ('B', '815', 8, 'Rotamer', (186.926, 198.617, 249.449)), ('B', '820', 8, 'side-chain clash\nBond angle:CA:CB:CG', (184.38100000000003, 203.29299999999998, 246.57399999999998)), ('B', '32', 9, 'Ramachandran\nBond angle:CA:CB:CG', (169.40800000000002, 231.24499999999998, 211.596)), ('B', '34', 9, 'Rotamer\ncablam CA Geom Outlier', (169.777, 226.799, 207.931)), ('B', '59', 9, 'Bond angle:CA:CB:CG', (172.694, 234.298, 210.627)), ('B', '666', 10, 'cablam Outlier', (195.9, 236.9, 231.7)), ('B', '667', 10, 'cablam Outlier', (199.6, 237.3, 232.7)), ('B', '796', 11, 'Bond angle:CA:CB:CG', (187.651, 199.82200000000003, 270.843)), ('B', '797', 11, 'Bond angle:CA:CB:CG\ncablam Outlier', (189.77399999999997, 202.60399999999998, 269.597)), ('B', '344', 12, 'side-chain clash', (221.385, 261.851, 159.708)), ('B', '509', 12, 'side-chain clash', (221.385, 261.851, 159.708)), ('B', '543', 13, 'Bond angle:CA:CB:CG\ncablam Outlier', (214.365, 248.82500000000002, 196.899)), ('B', '544', 13, 'cablam Outlier', (217.9, 248.7, 195.5)), ('B', '389', 14, 'side-chain clash', (210.756, 248.141, 182.329)), ('B', '529', 14, 'side-chain clash', (210.756, 248.141, 182.329)), ('B', '123', 15, 'cablam Outlier', (151.5, 218.1, 188.2)), ('B', '124', 15, 'cablam Outlier', (152.1, 214.6, 186.8)), ('B', '53', 16, 'Bond angle:CA:CB:CG', (181.77299999999997, 223.33200000000002, 202.031)), ('B', '55', 16, 'Bond angle:CA:CB:CG', (176.823, 226.207, 202.864)), ('C', '600', 1, 'Bond angle:C', (244.64499999999998, 230.08700000000002, 230.797)), ('C', '601', 1, 'Bond angle:N:CA', (242.393, 232.98100000000002, 230.30700000000002)), ('C', '604', 1, 'cablam Outlier', (246.3, 236.2, 232.0)), ('C', '263', 2, 'Bond angle:C', (258.48799999999994, 252.317, 192.634)), ('C', '264', 2, 'Bond angle:N:CA', (258.868, 251.02100000000002, 196.28)), ('C', '66', 2, 'Bond length:CB:CG', (262.214, 248.91, 194.395)), ('C', '666', 3, 'cablam Outlier', (242.7, 216.1, 231.6)), ('C', '670', 3, 'Bond angle:C', (245.365, 213.555, 235.484)), ('C', '671', 3, 'Bond angle:N:CA', (245.099, 217.44299999999998, 235.786)), ('C', '330', 4, 'Bond angle:C', (246.039, 186.148, 192.64)), ('C', '331', 4, 'Bond angle:N:CA', (248.586, 185.993, 189.961)), ('C', '333', 4, 'cablam CA Geom Outlier', (247.2, 182.9, 184.6)), ('C', '86', 5, 'cablam Outlier', (248.8, 237.3, 190.3)), ('C', '87', 5, 'cablam Outlier', (247.4, 233.9, 191.1)), ('C', '88', 5, 'cablam Outlier', (243.9, 234.2, 192.5)), ('C', '1092', 6, 'cablam CA Geom Outlier', (222.6, 213.4, 279.2)), ('C', '1106', 6, 'Bond angle:C:CA:CB', (226.754, 218.07, 277.375)), ('C', '1108', 6, 'Bond angle:CA:CB:CG', (228.757, 219.033, 272.074)), ('C', '528', 7, 'backbone clash', (239.195, 193.641, 193.144)), ('C', '543', 7, 'Bond angle:CA:CB:CG', (241.70399999999998, 193.12, 197.29399999999998)), ('C', '544', 7, 'backbone clash', (239.195, 193.641, 193.144)), ('C', '220', 8, 'cablam CA Geom Outlier', (245.0, 246.0, 211.2)), ('C', '32', 8, 'Ramachandran\nBond angle:CA:CB:CG\nBond angle:N:CA:CB', (251.262, 241.395, 210.596)), ('C', '34', 8, 'cablam CA Geom Outlier', (247.2, 243.1, 207.0)), ('C', '215', 9, 'side-chain clash', (258.934, 247.055, 205.005)), ('C', '266', 9, 'side-chain clash', (258.934, 247.055, 205.005)), ('C', '140', 10, 'Rotamer', (255.433, 253.51, 180.58)), ('C', '242', 10, 'Bond length:CB:CG', (255.542, 253.363, 186.039)), ('C', '574', 11, 'backbone clash', (237.93, 190.377, 209.07)), ('C', '575', 11, 'backbone clash', (237.93, 190.377, 209.07)), ('C', '192', 12, 'side-chain clash', (247.5, 246.544, 196.643)), ('C', '92', 12, 'side-chain clash', (247.5, 246.544, 196.643)), ('C', '395', 13, 'side-chain clash', (233.118, 189.954, 174.292)), ('C', '515', 13, 'side-chain clash', (233.118, 189.954, 174.292)), ('C', '81', 14, 'Bond angle:CA:C', (259.42599999999993, 246.91299999999998, 187.01899999999998)), ('C', '82', 14, 'Bond angle:N', (259.061, 242.90800000000002, 187.13)), ('C', '186', 15, 'Rotamer\nside-chain clash\nbackbone clash', (217.174, 219.404, 266.565)), ('C', '187', 15, 'side-chain clash\nbackbone clash', (217.174, 219.404, 266.565)), ('C', '811', 16, 'side-chain clash', (218.524, 248.44, 245.44)), ('C', '820', 16, 'side-chain clash\nBond angle:CA:CB:CG', (218.89800000000002, 244.13, 244.10399999999998)), ('C', '359', 17, 'cablam CA Geom Outlier', (235.2, 182.4, 177.9)), ('C', '361', 17, 'C-beta', (239.94900000000007, 182.056, 179.916))]
data['rama'] = [('A', ' 333 ', 'THR', 0.020048110508322222, (175.808, 193.453, 183.044)), ('A', '1112 ', 'PRO', 0.016480137350073823, (210.73800000000003, 196.645, 284.496)), ('B', '  32 ', 'PHE', 0.006066239726991865, (169.40799999999993, 231.245, 211.59600000000003)), ('B', '1036 ', 'GLN', 0.01875880034872368, (205.03, 210.162, 262.044)), ('C', '  32 ', 'PHE', 0.033584853980496515, (251.262, 241.395, 210.596))]
data['cablam'] = [('D', '7', 'SER', 'check CA trace', 'strand\nEEE--', (210.6, 235.4, 139.7)), ('D', '301', 'SER', 'check CA trace', 'strand\nEEE--', (241.0, 189.0, 117.1)), ('A', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (214.1, 169.9, 191.6)), ('A', '87', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nE-TTE', (211.9, 172.8, 193.0)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TTEE', (214.2, 175.5, 194.4)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (214.1, 170.8, 182.4)), ('A', '208', 'THR', ' beta sheet', ' \nE----', (230.5, 162.4, 206.2)), ('A', '231', 'ILE', ' beta sheet', ' \nEE---', (224.3, 177.7, 182.7)), ('A', '332', 'ILE', 'check CA trace,carbonyls, peptide', ' \n-S--S', (174.9, 195.9, 185.9)), ('A', '334', 'ASN', ' beta sheet', 'bend\n--SB-', (175.2, 195.1, 179.6)), ('A', '391', 'CYS', 'check CA trace,carbonyls, peptide', ' \nG---S', (184.2, 199.8, 188.7)), ('A', '604', 'THR', 'check CA trace,carbonyls, peptide', 'turn\nTTT--', (215.8, 173.7, 233.8)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (201.7, 186.8, 233.7)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (199.2, 189.5, 234.6)), ('A', '890', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nGGSSS', (229.7, 218.4, 260.7)), ('A', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (227.3, 211.6, 258.0)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (229.7, 202.7, 238.2)), ('A', '1071', 'GLN', 'check CA trace,carbonyls, peptide', 'bend\nE-SEE', (211.9, 188.5, 271.6)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TTSE', (196.3, 209.0, 295.8)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (213.5, 197.4, 275.2)), ('A', '33', 'THR', 'check CA trace', 'bend\nESS--', (219.4, 168.1, 211.9)), ('A', '34', 'ARG', 'check CA trace', ' \nSS--E', (221.1, 167.9, 208.4)), ('A', '220', 'PHE', 'check CA trace', ' \n-S--E', (224.9, 169.2, 212.9)), ('A', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (213.5, 182.0, 232.9)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (189.7, 191.8, 205.2)), ('A', '797', 'PHE', 'check CA trace', 'bend\n--SSS', (236.5, 199.7, 268.8)), ('A', '1092', 'GLU', 'check CA trace', 'bend\nESSSE', (208.2, 208.5, 280.0)), ('A', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (193.1, 213.5, 288.5)), ('B', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (173.4, 232.0, 191.6)), ('B', '87', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nE-TTE', (177.1, 232.6, 192.1)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TTEE', (178.6, 229.3, 193.1)), ('B', '113', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSSB', (169.5, 231.1, 171.5)), ('B', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (151.5, 218.1, 188.2)), ('B', '124', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (152.1, 214.6, 186.8)), ('B', '231', 'ILE', ' beta sheet', ' \nE----', (174.5, 218.6, 182.8)), ('B', '332', 'ILE', 'check CA trace,carbonyls, peptide', ' \n----S', (219.1, 257.0, 186.1)), ('B', '333', 'THR', 'check CA trace,carbonyls, peptide', ' \n---SB', (220.5, 260.5, 185.3)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (233.5, 242.4, 129.5)), ('B', '543', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-SS', (214.4, 248.8, 196.9)), ('B', '544', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (217.9, 248.7, 195.5)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (195.9, 236.9, 231.7)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (199.6, 237.3, 232.7)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (189.8, 202.6, 269.6)), ('B', '890', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nGGTSS', (208.9, 198.6, 261.7)), ('B', '1036', 'GLN', 'check CA trace,carbonyls, peptide', ' \nTT---', (205.0, 210.2, 262.0)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (218.4, 234.9, 294.8)), ('B', '34', 'ARG', 'check CA trace', 'strand\n-EEEE', (169.8, 226.8, 207.9)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (207.6, 243.2, 204.0)), ('B', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (196.3, 199.0, 214.4)), ('B', '1043', 'CYS', 'check CA trace', 'turn\nBTTBS', (201.7, 215.4, 255.6)), ('B', '1058', 'HIS', 'check CA trace', 'turn\nETTEE', (195.9, 204.5, 239.0)), ('B', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (223.3, 234.8, 287.0)), ('C', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (248.8, 237.3, 190.3)), ('C', '87', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nE-TTE', (247.4, 233.9, 191.1)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TTEE', (243.9, 234.2, 192.5)), ('C', '113', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (248.4, 240.0, 170.1)), ('C', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (247.2, 262.9, 186.7)), ('C', '231', 'ILE', 'check CA trace,carbonyls, peptide', ' \n-----', (236.4, 242.2, 181.5)), ('C', '604', 'THR', 'check CA trace,carbonyls, peptide', 'turn\nTTT--', (246.3, 236.2, 232.0)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (242.7, 216.1, 231.6)), ('C', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (209.2, 227.6, 257.5)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (229.2, 202.4, 295.8)), ('C', '34', 'ARG', 'check CA trace', ' \nTT--E', (247.2, 243.1, 207.0)), ('C', '220', 'PHE', 'check CA trace', ' \nS---E', (245.0, 246.0, 211.2)), ('C', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (247.2, 230.6, 212.9)), ('C', '333', 'THR', 'check CA trace', ' \n----B', (247.2, 182.9, 184.6)), ('C', '359', 'SER', 'check CA trace', ' \nE--SS', (235.2, 182.4, 177.9)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (240.9, 202.1, 204.2)), ('C', '797', 'PHE', 'check CA trace', 'bend\n--STT', (215.4, 241.5, 267.5)), ('C', '1058', 'HIS', 'check CA trace', 'turn\nETTEE', (214.1, 232.8, 237.5)), ('C', '1092', 'GLU', 'check CA trace', 'bend\nESSSE', (222.6, 213.4, 279.2)), ('C', '1098', 'ASN', 'check CA trace', 'bend\nEESSS', (241.0, 217.3, 283.3)), ('C', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (226.8, 197.8, 288.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22514/7jwb/Model_validation_1/validation_cootdata/molprobity_probe7jwb_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)


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
data['smoc'] = []
data['jpred'] = []
data['probe'] = [(' A 378  LYS  NZ ', ' B  57  GLU  OE2', -0.698, (225.869, 214.954, 220.631)), (' E 378  LYS  NZ ', ' H  57  GLU  OE2', -0.697, (225.268, 233.162, 244.808)), (' B 123  PRO  HB3', ' B 149  TYR  HB3', -0.62, (230.2, 260.915, 206.94)), (' H 123  PRO  HB3', ' H 149  TYR  HB3', -0.618, (229.898, 187.016, 258.789)), (' A 383  SER  OG ', ' B 104  THR  OG1', -0.577, (225.761, 215.882, 205.783)), (' E 383  SER  OG ', ' H 104  THR  OG1', -0.568, (223.377, 232.506, 259.564)), (' C 190  ALA  O  ', ' C 194  LYS  HG3', -0.499, (250.255, 276.398, 203.248)), (' L 190  ALA  O  ', ' L 194  LYS  HG3', -0.497, (250.598, 172.407, 263.658)), (' A 485  GLY  O  ', ' H 119  SER  OG ', -0.496, (232.275, 189.889, 246.568)), (' A 517  LEU  HB2', ' C  34  ILE HG22', -0.472, (229.618, 203.699, 202.146)), (' C  67  ARG  HB2', ' C  82  SER  O  ', -0.465, (233.589, 224.567, 183.594)), (' C  34  ILE  O  ', ' C  36  LYS  N  ', -0.464, (234.616, 207.03, 201.898)), (' E 517  LEU  HB2', ' L  34  ILE HG22', -0.462, (227.225, 244.646, 264.114)), (' L  34  ILE  O  ', ' L  36  LYS  N  ', -0.46, (231.75, 240.909, 264.598)), (' L  67  ARG  HB2', ' L  82  SER  O  ', -0.456, (229.05, 222.972, 283.193)), (' E 447  GLY  HA2', ' E 498  GLN  HG2', -0.44, (212.261, 248.396, 225.332)), (' A 489  TYR  HH ', ' H 119  SER  N  ', -0.437, (232.421, 193.774, 246.477)), (' A 447  GLY  HA2', ' A 498  GLN  HG2', -0.436, (210.639, 199.8, 239.101)), (' H 105  PRO  HG3', ' L  97  TYR  CZ ', -0.43, (228.332, 230.756, 262.945)), (' B 105  PRO  HG3', ' C  97  TYR  CZ ', -0.428, (230.62, 217.468, 203.315)), (' A 497  PHE  CE2', ' A 507  PRO  HB3', -0.427, (214.926, 201.387, 231.198)), (' A 379  CYS  HA ', ' A 432  CYS  HA ', -0.426, (223.421, 209.435, 213.099)), (' E 379  CYS  HA ', ' E 432  CYS  HA ', -0.425, (221.906, 238.672, 252.506)), (' A 393  THR  HA ', ' A 522  ALA  HA ', -0.424, (224.994, 197.544, 198.361)), (' E 497  PHE  CE2', ' E 507  PRO  HB3', -0.42, (215.51, 247.058, 233.794)), (' E 393  THR  HA ', ' E 522  ALA  HA ', -0.415, (222.193, 250.489, 267.718)), (' A 393  THR HG21', ' A 518  LEU  H  ', -0.415, (229.757, 198.151, 199.919)), (' E 401  VAL HG22', ' E 509  ARG  HG2', -0.409, (213.955, 247.663, 240.23)), (' H 213  LYS  HA ', ' H 213  LYS  HD2', -0.408, (224.505, 177.253, 266.112)), (' E 347  PHE  HB3', ' E 348  ALA  H  ', -0.408, (215.424, 251.506, 241.453)), (' E 393  THR HG21', ' E 518  LEU  H  ', -0.407, (226.919, 249.856, 266.54)), (' A 360  ASN  H  ', ' A 523  THR  HB ', -0.407, (219.402, 194.668, 199.729)), (' B 188  VAL HG11', ' B 198  TYR  CE1', -0.406, (224.718, 265.686, 185.635)), (' H 188  VAL HG11', ' H 198  TYR  CE1', -0.401, (223.147, 182.618, 280.071)), (' A 412  PRO  HB3', ' A 426  PRO  O  ', -0.4, (233.027, 206.946, 215.963)), (' H 150  PHE  HA ', ' H 151  PRO  HA ', -0.4, (231.528, 193.699, 255.249))]
data['rota'] = [('E', ' 368 ', 'LEU', 0.0, (210.78300000000004, 239.646, 254.18799999999996)), ('E', ' 376 ', 'THR', 0.026958901435136795, (216.89700000000005, 235.697, 245.267)), ('E', ' 387 ', 'LEU', 0.23728738194087884, (217.88, 238.33099999999993, 264.095)), ('E', ' 390 ', 'LEU', 0.18972274031531605, (218.81400000000005, 240.916, 267.857)), ('E', ' 480 ', 'CYS', 0.02232224352802614, (238.59800000000007, 265.488, 225.823)), ('E', ' 483 ', 'VAL', 0.025922069295810545, (233.29900000000006, 266.779, 224.414)), ('E', ' 506 ', 'GLN', 0.015708858779972, (214.557, 241.986, 231.815)), ('H', '   5 ', 'VAL', 0.1050819473832211, (214.67300000000006, 215.103, 255.56099999999998)), ('H', ' 192 ', 'SER', 0.102077545529868, (222.70900000000006, 177.907, 284.57799999999986)), ('H', ' 203 ', 'ASN', 0.29814686419572584, (221.54900000000006, 188.462, 261.3869999999999)), ('L', '   1 ', 'ASP', 0.0851910271072826, (241.94300000000007, 228.487, 253.261)), ('A', ' 368 ', 'LEU', 0.0, (212.43600000000006, 208.639, 210.435)), ('A', ' 376 ', 'THR', 0.026958901435136795, (217.59400000000005, 212.612, 219.931)), ('A', ' 387 ', 'LEU', 0.23199634854242243, (220.57800000000006, 209.784, 201.34399999999994)), ('A', ' 390 ', 'LEU', 0.19119460981400507, (221.88600000000005, 207.152, 197.727)), ('A', ' 480 ', 'CYS', 0.02251363632287639, (236.723, 182.79, 241.86799999999994)), ('A', ' 483 ', 'VAL', 0.025861551615577846, (231.28700000000006, 181.568, 242.70499999999996)), ('A', ' 506 ', 'GLN', 0.015819367649333917, (213.74100000000007, 206.48, 233.104)), ('B', '   5 ', 'VAL', 0.10427751936027821, (216.73000000000005, 233.127, 209.27899999999997)), ('B', ' 192 ', 'SER', 0.1018941928457269, (224.36200000000005, 270.367, 181.059)), ('B', ' 203 ', 'ASN', 0.29752982603826106, (222.14300000000006, 259.795, 204.166)), ('C', '   1 ', 'ASP', 0.08338670517103486, (243.43800000000005, 219.484, 214.63499999999993))]
data['clusters'] = [('A', '360', 1, 'side-chain clash', (219.402, 194.668, 199.729)), ('A', '393', 1, 'side-chain clash', (229.757, 198.151, 199.919)), ('A', '518', 1, 'side-chain clash', (229.757, 198.151, 199.919)), ('A', '519', 1, 'cablam Outlier', (233.3, 197.0, 196.6)), ('A', '522', 1, 'side-chain clash', (224.994, 197.544, 198.361)), ('A', '523', 1, 'side-chain clash', (219.402, 194.668, 199.729)), ('A', '480', 2, 'Rotamer', (236.723, 182.79, 241.86799999999994)), ('A', '481', 2, 'cablam Outlier', (235.6, 179.3, 240.8)), ('A', '483', 2, 'Rotamer', (231.28700000000006, 181.568, 242.70499999999996)), ('A', '484', 2, 'Dihedral angle:CB:CG:CD:OE1', (230.095, 185.031, 243.722)), ('A', '497', 3, 'side-chain clash', (214.926, 201.387, 231.198)), ('A', '506', 3, 'Rotamer', (213.74100000000007, 206.48, 233.104)), ('A', '507', 3, 'side-chain clash', (214.926, 201.387, 231.198)), ('A', '387', 4, 'Rotamer', (220.57800000000006, 209.784, 201.34399999999994)), ('A', '390', 4, 'Rotamer', (221.88600000000005, 207.152, 197.727)), ('A', '447', 5, 'side-chain clash', (210.639, 199.8, 239.101)), ('A', '498', 5, 'side-chain clash', (210.639, 199.8, 239.101)), ('A', '379', 6, 'side-chain clash', (223.421, 209.435, 213.099)), ('A', '432', 6, 'side-chain clash', (223.421, 209.435, 213.099)), ('A', '412', 7, 'backbone clash', (233.027, 206.946, 215.963)), ('A', '426', 7, 'backbone clash', (233.027, 206.946, 215.963)), ('B', '188', 1, 'side-chain clash', (224.718, 265.686, 185.635)), ('B', '192', 1, 'Rotamer', (224.36200000000005, 270.367, 181.059)), ('B', '198', 1, 'side-chain clash', (224.718, 265.686, 185.635)), ('B', '57', 2, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (226.032, 219.339, 222.755)), ('B', '59', 2, 'Dihedral angle:CD:NE:CZ:NH1', (231.88500000000002, 222.142, 220.425)), ('B', '123', 3, 'side-chain clash', (230.2, 260.915, 206.94)), ('B', '149', 3, 'side-chain clash', (230.2, 260.915, 206.94)), ('C', '34', 1, 'side-chain clash\nbackbone clash', (234.616, 207.03, 201.898)), ('C', '35', 1, 'Ramachandran', (235.52300000000005, 205.28, 201.03599999999994)), ('C', '36', 1, 'backbone clash', (234.616, 207.03, 201.898)), ('C', '190', 2, 'side-chain clash', (250.255, 276.398, 203.248)), ('C', '194', 2, 'side-chain clash', (250.255, 276.398, 203.248)), ('C', '67', 3, 'backbone clash', (233.589, 224.567, 183.594)), ('C', '82', 3, 'backbone clash', (233.589, 224.567, 183.594)), ('E', '347', 1, 'side-chain clash', (215.424, 251.506, 241.453)), ('E', '348', 1, 'side-chain clash', (215.424, 251.506, 241.453)), ('E', '401', 1, 'side-chain clash', (213.955, 247.663, 240.23)), ('E', '497', 1, 'side-chain clash', (215.51, 247.058, 233.794)), ('E', '506', 1, 'Rotamer', (214.557, 241.986, 231.815)), ('E', '507', 1, 'side-chain clash', (215.51, 247.058, 233.794)), ('E', '509', 1, 'side-chain clash', (213.955, 247.663, 240.23)), ('E', '393', 2, 'side-chain clash', (226.919, 249.856, 266.54)), ('E', '518', 2, 'side-chain clash', (226.919, 249.856, 266.54)), ('E', '519', 2, 'cablam Outlier', (230.2, 250.9, 270.3)), ('E', '522', 2, 'side-chain clash', (222.193, 250.489, 267.718)), ('E', '480', 3, 'Rotamer', (238.59800000000007, 265.488, 225.823)), ('E', '481', 3, 'cablam Outlier', (237.4, 269.0, 226.8)), ('E', '483', 3, 'Rotamer', (233.29900000000006, 266.779, 224.414)), ('E', '484', 3, 'Dihedral angle:CB:CG:CD:OE1', (232.187, 263.33799999999997, 223.24099999999999)), ('E', '387', 4, 'Rotamer', (217.88, 238.33099999999993, 264.095)), ('E', '390', 4, 'Rotamer', (218.81400000000005, 240.916, 267.857)), ('E', '447', 5, 'side-chain clash', (212.261, 248.396, 225.332)), ('E', '498', 5, 'side-chain clash', (212.261, 248.396, 225.332)), ('E', '379', 6, 'side-chain clash', (221.906, 238.672, 252.506)), ('E', '432', 6, 'side-chain clash', (221.906, 238.672, 252.506)), ('H', '188', 1, 'side-chain clash', (223.147, 182.618, 280.071)), ('H', '192', 1, 'Rotamer', (222.70900000000006, 177.907, 284.57799999999986)), ('H', '198', 1, 'side-chain clash', (223.147, 182.618, 280.071)), ('H', '150', 2, 'side-chain clash', (231.528, 193.699, 255.249)), ('H', '151', 2, 'side-chain clash', (231.528, 193.699, 255.249)), ('H', '57', 3, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (225.52200000000002, 228.899, 243.30700000000002)), ('H', '59', 3, 'Dihedral angle:CD:NE:CZ:NH1', (231.059, 226.01, 246.23)), ('H', '123', 4, 'side-chain clash', (229.898, 187.016, 258.789)), ('H', '149', 4, 'side-chain clash', (229.898, 187.016, 258.789)), ('H', '104', 5, 'side-chain clash', (223.377, 232.506, 259.564)), ('H', '119', 5, 'side-chain clash\nbackbone clash', (228.332, 230.756, 262.945)), ('L', '34', 1, 'side-chain clash\nbackbone clash', (231.75, 240.909, 264.598)), ('L', '35', 1, 'Ramachandran', (232.74900000000005, 242.662, 266.0619999999999)), ('L', '36', 1, 'backbone clash', (231.75, 240.909, 264.598)), ('L', '190', 2, 'side-chain clash', (250.598, 172.407, 263.658)), ('L', '194', 2, 'side-chain clash', (250.598, 172.407, 263.658)), ('L', '67', 3, 'backbone clash', (229.05, 222.972, 283.193)), ('L', '82', 3, 'backbone clash', (229.05, 222.972, 283.193))]
data['omega'] = [('B', ' 151 ', 'PRO', None, (229.737, 255.07099999999997, 211.921)), ('B', ' 153 ', 'PRO', None, (227.278, 252.36599999999993, 206.96999999999994)), ('C', '   8 ', 'PRO', None, (246.79400000000007, 228.495, 194.27799999999993)), ('C', ' 101 ', 'PRO', None, (237.55900000000005, 220.623, 215.437)), ('C', ' 147 ', 'PRO', None, (243.553, 247.296, 182.837)), ('H', ' 151 ', 'PRO', None, (229.448, 193.409, 254.09)), ('H', ' 153 ', 'PRO', None, (226.63100000000006, 196.03499999999994, 258.891)), ('L', '   8 ', 'PRO', None, (242.98000000000005, 219.263, 273.772)), ('L', ' 101 ', 'PRO', None, (236.17500000000007, 227.422, 251.81699999999995)), ('L', ' 147 ', 'PRO', None, (241.32600000000005, 201.501, 283.933))]
data['rama'] = [('C', '  35 ', 'ASN', 0.011132473178877016, (235.52300000000005, 205.28, 201.03599999999994)), ('L', '  35 ', 'ASN', 0.011294462423406579, (232.74900000000005, 242.662, 266.0619999999999))]
data['cablam'] = [('A', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (235.6, 179.3, 240.8)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (234.7, 188.6, 248.1)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\nB-SS-', (233.3, 197.0, 196.6)), ('B', '111', 'GLN', ' beta sheet', ' \nE---E', (222.2, 235.8, 205.1)), ('C', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (235.7, 219.2, 214.7)), ('E', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (237.4, 269.0, 226.8)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (237.2, 259.8, 219.3)), ('E', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\nB-SS-', (230.2, 250.9, 270.3)), ('H', '111', 'GLN', ' beta sheet', ' \nE---E', (219.7, 212.4, 260.3)), ('L', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (234.3, 228.9, 252.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-10863/6yor/Model_validation_12/validation_cootdata/molprobity_probe6yor_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)


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
data['cbeta'] = []
data['jpred'] = []
data['rota'] = [('A', ' 417 ', 'LYS', 1.147647300499344e-05, (211.30499999999995, 190.849, 251.74)), ('A', ' 603 ', 'ASN', 0.12004898171780808, (192.46599999999995, 242.551, 195.38699999999997)), ('B', ' 417 ', 'LYS', 1.3158190740118595e-05, (225.93299999999994, 220.70599999999993, 251.74)), ('B', ' 603 ', 'ASN', 0.12009681663878832, (190.57699999999994, 178.539, 195.38699999999997)), ('C', ' 417 ', 'LYS', 1.2187536542130524e-05, (192.762, 218.44499999999994, 251.74)), ('C', ' 603 ', 'ASN', 0.12059512550764301, (246.95699999999994, 208.909, 195.38699999999997))]
data['clusters'] = [('A', '106', 1, 'smoc Outlier', (186.67399999999998, 247.236, 240.74599999999998)), ('A', '108', 1, 'cablam Outlier', (182.5, 242.3, 243.9)), ('A', '116', 1, 'smoc Outlier', (188.14499999999998, 247.24599999999998, 245.85700000000003)), ('A', '117', 1, 'smoc Outlier', (190.58200000000002, 248.77299999999997, 243.416)), ('A', '118', 1, 'smoc Outlier', (190.17399999999998, 252.508, 243.061)), ('A', '128', 1, 'smoc Outlier', (195.681, 254.20899999999997, 242.92100000000002)), ('A', '237', 1, 'smoc Outlier', (181.833, 243.91899999999998, 238.86800000000002)), ('A', '661', 2, 'smoc Outlier', (185.49800000000002, 227.48600000000002, 181.80200000000002)), ('A', '663', 2, 'Dihedral angle:CA:CB:CG:OD1', (188.094, 228.984, 187.512)), ('A', '666', 2, 'cablam Outlier\nsmoc Outlier', (185.1, 222.9, 193.9)), ('A', '667', 2, 'cablam Outlier', (184.8, 219.3, 192.9)), ('A', '671', 2, 'smoc Outlier', (183.61899999999997, 225.24299999999997, 189.71599999999998)), ('A', '1306', 3, 'smoc Outlier', (170.27499999999998, 197.393, 235.817)), ('A', '331', 3, 'Bond angle:CA:CB:CG', (169.74899999999997, 201.95200000000003, 238.996)), ('A', '391', 3, 'side-chain clash\nbackbone clash', (170.914, 198.465, 234.673)), ('A', '525', 3, 'side-chain clash\nbackbone clash', (170.914, 198.465, 234.673)), ('A', '326', 4, 'smoc Outlier', (173.585, 211.74299999999997, 229.12800000000001)), ('A', '538', 4, 'smoc Outlier', (174.123, 214.92200000000003, 219.39200000000002)), ('A', '539', 4, 'smoc Outlier', (174.89100000000002, 214.34, 223.106)), ('A', '549', 4, 'cablam CA Geom Outlier', (180.3, 212.4, 222.0)), ('A', '1058', 5, 'cablam Outlier', (216.1, 228.0, 188.1)), ('A', '1060', 5, 'smoc Outlier', (214.43200000000002, 226.97299999999998, 181.0)), ('A', '729', 5, 'smoc Outlier', (215.373, 222.721, 185.98000000000002)), ('A', '731', 5, 'smoc Outlier', (215.94, 224.226, 192.985)), ('A', '121', 6, 'smoc Outlier', (192.92200000000003, 261.092, 238.23399999999998)), ('A', '123', 6, 'cablam Outlier', (194.1, 267.5, 237.9)), ('A', '1302', 6, 'Bond angle:C3:C2:N2\nBond angle:C2:N2:C7', (195.651, 267.77299999999997, 242.68200000000002)), ('A', '381', 7, 'cablam Outlier', (195.8, 203.0, 238.9)), ('A', '382', 7, 'smoc Outlier', (193.564, 205.964, 238.62800000000001)), ('A', '383', 7, 'smoc Outlier', (193.404, 209.31, 240.383)), ('A', '738', 8, 'smoc Outlier', (222.059, 219.55, 211.678)), ('A', '741', 8, 'smoc Outlier', (220.18, 223.69899999999998, 214.067)), ('A', '856', 8, 'cablam Outlier', (220.2, 228.7, 212.6)), ('A', '465', 9, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (199.372, 184.562, 245.953)), ('A', '466', 9, 'smoc Outlier', (198.347, 183.42800000000003, 249.46)), ('A', '468', 9, 'Bond length:CB:CG1\nsmoc Outlier', (199.22899999999998, 179.41299999999998, 253.561)), ('A', '811', 10, 'side-chain clash', (217.931, 243.576, 178.87)), ('A', '820', 10, 'side-chain clash', (217.931, 243.576, 178.87)), ('A', '417', 11, 'Rotamer', (211.30499999999995, 190.849, 251.74)), ('A', '420', 11, 'smoc Outlier', (208.68, 189.36, 247.097)), ('A', '291', 12, 'smoc Outlier', (190.35000000000002, 234.782, 213.222)), ('A', '293', 12, 'cablam CA Geom Outlier', (185.1, 237.1, 212.7)), ('A', '111', 13, 'side-chain clash\nBond angle:CA:CB:CG', (180.67499999999998, 248.626, 249.686)), ('A', '112', 13, 'cablam Outlier', (183.6, 248.4, 252.2)), ('A', '80', 14, 'Bond angle:CA:CB:CG\nsmoc Outlier', (175.10899999999998, 257.267, 233.934)), ('A', '81', 14, 'side-chain clash', (176.24, 256.541, 236.589)), ('A', '204', 15, 'smoc Outlier', (196.702, 248.82700000000003, 228.86200000000002)), ('A', '205', 15, 'smoc Outlier', (195.806, 252.172, 227.399)), ('A', '796', 16, 'smoc Outlier', (220.94299999999998, 238.30200000000002, 157.121)), ('A', '797', 16, 'cablam Outlier', (218.5, 235.6, 158.2)), ('A', '1032', 17, 'smoc Outlier', (213.371, 220.112, 170.032)), ('A', '1043', 17, 'cablam Outlier', (207.2, 220.8, 171.2)), ('A', '1308', 18, 'smoc Outlier', (195.626, 243.258, 189.611)), ('A', '603', 18, 'Rotamer', (192.46599999999995, 242.551, 195.38699999999997)), ('A', '770', 19, 'smoc Outlier', (220.39200000000002, 217.04899999999998, 196.503)), ('A', '773', 19, 'smoc Outlier', (222.30700000000002, 216.85100000000003, 191.536)), ('A', '802', 20, 'smoc Outlier', (215.83, 237.14399999999998, 166.07399999999998)), ('A', '805', 20, 'smoc Outlier', (216.024, 236.212, 171.508)), ('B', '1306', 1, 'smoc Outlier', (240.78, 181.901, 235.817)), ('B', '331', 1, 'Bond angle:CA:CB:CG', (237.096, 179.166, 238.996)), ('B', '391', 1, 'side-chain clash\nbackbone clash', (239.616, 182.062, 234.673)), ('B', '525', 1, 'side-chain clash\nbackbone clash', (239.616, 182.062, 234.673)), ('B', '1307', 2, 'smoc Outlier', (228.517, 192.047, 255.47299999999998)), ('B', '342', 2, 'smoc Outlier', (230.067, 196.471, 257.184)), ('B', '811', 2, 'side-chain clash', (229.113, 193.552, 256.05)), ('B', '820', 2, 'side-chain clash', (229.113, 193.552, 256.05)), ('B', '412', 3, 'smoc Outlier', (223.646, 210.694, 241.67499999999998)), ('B', '413', 3, 'smoc Outlier', (221.844, 213.88400000000001, 240.695)), ('B', '428', 3, 'Dihedral angle:CA:CB:CG:OD1', (226.36200000000002, 208.411, 236.10899999999998)), ('B', '365', 4, 'smoc Outlier', (225.19899999999998, 190.009, 247.535)), ('B', '369', 4, 'smoc Outlier', (220.345, 192.383, 250.394)), ('B', '370', 4, 'smoc Outlier', (218.407, 189.899, 252.537)), ('B', '106', 5, 'smoc Outlier', (189.415, 171.181, 240.74599999999998)), ('B', '117', 5, 'smoc Outlier', (186.13, 173.797, 243.416)), ('B', '118', 5, 'smoc Outlier', (183.1, 171.576, 243.061)), ('B', '381', 6, 'cablam Outlier', (223.2, 201.3, 238.9)), ('B', '382', 6, 'smoc Outlier', (221.71299999999997, 197.784, 238.62800000000001)), ('B', '383', 6, 'smoc Outlier', (218.89600000000002, 195.972, 240.383)), ('B', '741', 7, 'smoc Outlier', (193.046, 211.967, 214.067)), ('B', '854', 7, 'smoc Outlier', (185.866, 206.751, 208.642)), ('B', '856', 7, 'cablam Outlier', (188.7, 209.5, 212.6)), ('B', '1032', 8, 'smoc Outlier', (199.55700000000002, 207.864, 170.032)), ('B', '1033', 8, 'smoc Outlier', (195.88200000000003, 208.999, 169.82100000000003)), ('B', '1043', 8, 'cablam Outlier', (202.0, 202.2, 171.2)), ('B', '465', 9, 'Dihedral angle:CB:CG:CD:OE1', (237.344, 213.515, 245.953)), ('B', '466', 9, 'smoc Outlier', (238.83800000000002, 213.194, 249.46)), ('B', '468', 9, 'Bond length:CB:CG1', (241.875, 215.965, 253.561)), ('B', '213', 10, 'smoc Outlier', (177.82600000000002, 158.053, 219.231)), ('B', '215', 10, 'cablam CA Geom Outlier', (183.4, 160.3, 218.7)), ('B', '123', 11, 'cablam Outlier', (168.2, 167.5, 237.9)), ('B', '1302', 11, 'Bond angle:C3:C2:N2\nBond angle:C2:N2:C7', (167.141, 168.687, 242.68200000000002)), ('B', '666', 12, 'cablam Outlier\nsmoc Outlier', (211.3, 182.0, 193.9)), ('B', '667', 12, 'cablam Outlier', (214.6, 183.5, 192.9)), ('B', '661', 13, 'smoc Outlier', (207.108, 180.038, 181.80200000000002)), ('B', '663', 13, 'Dihedral angle:CA:CB:CG:OD1', (204.512, 181.537, 187.512)), ('B', '816', 14, 'smoc Outlier', (180.999, 202.948, 175.35600000000002)), ('B', '819', 14, 'smoc Outlier', (184.28, 201.41299999999998, 178.953)), ('B', '346', 15, 'smoc Outlier', (235.10999999999999, 202.08700000000002, 263.469)), ('B', '347', 15, 'smoc Outlier', (233.977, 203.984, 260.409)), ('B', '549', 16, 'cablam CA Geom Outlier', (222.7, 183.1, 222.0)), ('B', '550', 16, 'smoc Outlier', (225.018, 181.60899999999998, 219.42700000000002)), ('B', '417', 17, 'Rotamer', (225.93299999999994, 220.70599999999993, 251.74)), ('B', '420', 17, 'smoc Outlier', (228.535, 219.177, 247.097)), ('B', '1119', 18, 'smoc Outlier', (211.85100000000003, 202.007, 140.096)), ('B', '1120', 18, 'smoc Outlier', (215.618, 202.256, 140.39000000000001)), ('B', '111', 19, 'Bond angle:CA:CB:CG', (191.21099999999998, 165.291, 249.686)), ('B', '112', 19, 'cablam Outlier', (190.0, 167.9, 252.2)), ('B', '796', 20, 'smoc Outlier', (180.01899999999998, 205.32600000000002, 157.121)), ('B', '797', 20, 'cablam Outlier', (183.6, 204.5, 158.2)), ('B', '243', 21, 'smoc Outlier', (176.141, 159.42800000000003, 237.70399999999998)), ('B', '244', 21, 'smoc Outlier', (176.036, 155.668, 238.18800000000002)), ('B', '1025', 22, 'smoc Outlier', (199.63899999999998, 208.46, 179.7)), ('B', '781', 22, 'smoc Outlier', (195.824, 213.14499999999998, 180.202)), ('B', '31', 23, 'smoc Outlier', (190.04399999999998, 167.82500000000002, 218.262)), ('B', '34', 23, 'cablam CA Geom Outlier', (186.9, 172.6, 218.5)), ('B', '1308', 24, 'smoc Outlier', (188.38500000000002, 180.923, 189.611)), ('B', '603', 24, 'Rotamer', (190.57699999999994, 178.539, 195.38699999999997)), ('B', '1057', 25, 'smoc Outlier', (188.41899999999998, 204.054, 187.162)), ('B', '1058', 25, 'cablam Outlier', (191.4, 206.2, 188.1)), ('B', '40', 26, 'smoc Outlier', (186.47299999999998, 188.944, 225.672)), ('B', '42', 26, 'smoc Outlier', (183.288, 193.04399999999998, 223.24599999999998)), ('C', '663', 1, 'Dihedral angle:CA:CB:CG:OD1', (237.393, 219.47899999999998, 187.512)), ('C', '666', 1, 'cablam Outlier', (233.6, 225.1, 193.9)), ('C', '667', 1, 'cablam Outlier', (230.6, 227.2, 192.9)), ('C', '671', 1, 'smoc Outlier', (236.39100000000002, 225.225, 189.71599999999998)), ('C', '695', 1, 'smoc Outlier', (239.79299999999998, 229.512, 187.84)), ('C', '802', 2, 'smoc Outlier', (230.593, 191.379, 166.07399999999998)), ('C', '805', 2, 'smoc Outlier', (229.689, 191.677, 171.508)), ('C', '816', 2, 'smoc Outlier', (230.608, 188.41, 175.35600000000002)), ('C', '819', 2, 'smoc Outlier', (230.297, 192.01899999999998, 178.953)), ('C', '331', 3, 'Bond angle:CA:CB:CG', (223.155, 248.883, 238.996)), ('C', '332', 3, 'smoc Outlier', (221.024, 248.54299999999998, 242.172)), ('C', '391', 3, 'side-chain clash\nbackbone clash', (219.564, 249.371, 234.352)), ('C', '525', 3, 'side-chain clash\nbackbone clash', (219.564, 249.371, 234.352)), ('C', '412', 4, 'smoc Outlier', (202.576, 221.47, 241.67499999999998)), ('C', '413', 4, 'smoc Outlier', (200.71499999999997, 218.315, 240.695)), ('C', '428', 4, 'Dihedral angle:CA:CB:CG:OD1', (203.195, 224.964, 236.10899999999998)), ('C', '1060', 5, 'smoc Outlier', (222.483, 197.67499999999998, 181.0)), ('C', '1062', 5, 'smoc Outlier', (224.224, 200.24499999999998, 175.20399999999998)), ('C', '725', 5, 'smoc Outlier', (225.68800000000002, 204.661, 177.377)), ('C', '106', 6, 'smoc Outlier', (253.911, 211.583, 240.74599999999998)), ('C', '117', 6, 'smoc Outlier', (253.288, 207.43, 243.416)), ('C', '119', 6, 'smoc Outlier', (257.72299999999996, 203.48100000000002, 240.35800000000003)), ('C', '398', 7, 'smoc Outlier', (203.623, 233.30700000000002, 250.34)), ('C', '510', 7, 'smoc Outlier', (206.376, 227.595, 255.097)), ('C', '512', 7, 'smoc Outlier', (206.68800000000002, 229.69899999999998, 248.977)), ('C', '738', 8, 'smoc Outlier', (212.24099999999999, 194.782, 211.678)), ('C', '741', 8, 'smoc Outlier', (216.77299999999997, 194.334, 214.067)), ('C', '856', 8, 'cablam Outlier', (221.1, 191.8, 212.6)), ('C', '465', 9, 'Dihedral angle:CB:CG:CD:OE1', (193.284, 231.923, 245.953)), ('C', '466', 9, 'smoc Outlier', (192.815, 233.37800000000001, 249.46)), ('C', '468', 9, 'Bond length:CB:CG1', (188.89700000000002, 234.622, 253.561)), ('C', '123', 10, 'cablam Outlier', (267.7, 195.0, 237.9)), ('C', '1302', 10, 'Bond angle:C3:C2:N2\nBond angle:C2:N2:C7', (267.20799999999997, 193.54, 242.68200000000002)), ('C', '454', 11, 'Bond length:NE:CZ', (189.847, 225.659, 255.465)), ('C', '491', 11, 'smoc Outlier', (184.41, 224.154, 256.584)), ('C', '811', 12, 'side-chain clash\nbackbone clash', (245.417, 234.247, 189.187)), ('C', '820', 12, 'side-chain clash\nbackbone clash', (245.417, 234.247, 189.187)), ('C', '1109', 13, 'cablam Outlier', (226.8, 213.6, 151.8)), ('C', '714', 13, 'smoc Outlier', (228.004, 219.823, 152.912)), ('C', '923', 14, 'smoc Outlier', (232.178, 201.447, 156.939)), ('C', '924', 14, 'smoc Outlier', (232.88800000000003, 197.93200000000002, 158.106)), ('C', '291', 15, 'smoc Outlier', (241.287, 214.626, 213.222)), ('C', '293', 15, 'cablam CA Geom Outlier', (245.9, 218.0, 212.7)), ('C', '193', 16, 'smoc Outlier', (251.418, 206.92000000000002, 228.72299999999998)), ('C', '204', 16, 'smoc Outlier', (250.27399999999997, 202.10299999999998, 228.86200000000002)), ('C', '111', 17, 'side-chain clash\nBond angle:CA:CB:CG', (258.113, 216.083, 249.686)), ('C', '112', 17, 'cablam Outlier', (256.5, 213.7, 252.2)), ('C', '80', 18, 'Bond angle:CA:CB:CG', (268.38, 216.583, 233.934)), ('C', '81', 18, 'side-chain clash', (267.133, 216.057, 236.598)), ('C', '796', 19, 'smoc Outlier', (229.039, 186.373, 157.121)), ('C', '797', 19, 'cablam Outlier', (227.9, 189.9, 158.2)), ('C', '381', 20, 'cablam Outlier', (211.0, 225.8, 238.9)), ('C', '383', 20, 'smoc Outlier', (217.7, 224.718, 240.383)), ('C', '101', 21, 'smoc Outlier', (266.05400000000003, 205.789, 233.602)), ('C', '243', 21, 'smoc Outlier', (270.72599999999994, 205.963, 237.70399999999998)), ('C', '220', 22, 'smoc Outlier', (254.136, 204.289, 214.35100000000003)), ('C', '34', 22, 'cablam CA Geom Outlier', (253.9, 208.7, 218.5)), ('C', '501', 23, 'smoc Outlier', (203.02, 216.62800000000001, 269.368)), ('C', '505', 23, 'smoc Outlier', (201.9, 216.95800000000003, 264.16900000000004)), ('C', '1058', 24, 'cablam Outlier', (222.6, 195.8, 188.1)), ('C', '948', 24, 'smoc Outlier', (226.496, 201.44899999999998, 188.30700000000002))]
data['probe'] = [(' A 391  CYS  SG ', ' A 525  CYS  SG ', -1.197, (178.881, 201.933, 236.916)), (' B 391  CYS  SG ', ' B 525  CYS  SG ', -1.194, (232.661, 187.153, 236.864)), (' C 391  CYS  SG ', ' C 525  CYS  SG ', -1.092, (218.796, 240.908, 236.736)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.538, (217.931, 243.576, 178.87)), (' B 391  CYS  CB ', ' B 525  CYS  SG ', -0.535, (231.539, 188.172, 237.766)), (' B 811  LYS  NZ ', ' B 820  ASP  OD2', -0.535, (177.31, 200.291, 179.201)), (' A 391  CYS  CB ', ' A 525  CYS  SG ', -0.532, (180.327, 202.259, 237.771)), (' C 391  CYS  CB ', ' C 525  CYS  SG ', -0.531, (218.078, 239.575, 237.907)), (' C 811  LYS  NZ ', ' C 820  ASP  OD2', -0.53, (234.595, 186.452, 178.984)), (' B 342  PHE  HB2', ' B1307  NAG  H82', -0.472, (229.113, 193.552, 256.05)), (' C 342  PHE  HB2', ' C1307  NAG  H82', -0.471, (214.615, 234.74, 255.878)), (' C 655  HIS  O  ', ' C1310  NAG  H81', -0.461, (245.417, 234.247, 189.187)), (' A 655  HIS  O  ', ' A1310  NAG  H81', -0.455, (171.442, 229.028, 189.317)), (' B  81  ASN  N  ', ' B  81  ASN  OD1', -0.453, (186.627, 157.583, 236.608)), (' A 342  PHE  HB2', ' A1307  NAG  H82', -0.452, (186.667, 201.485, 256.14)), (' B 655  HIS  O  ', ' B1310  NAG  H81', -0.45, (213.288, 167.327, 189.124)), (' C  81  ASN  N  ', ' C  81  ASN  OD1', -0.445, (267.133, 216.057, 236.598)), (' C 391  CYS  HB2', ' C 525  CYS  HA ', -0.444, (217.697, 239.238, 239.473)), (' B 391  CYS  HB2', ' B 525  CYS  HA ', -0.441, (231.686, 188.646, 239.431)), (' A 391  CYS  HB2', ' A 525  CYS  HA ', -0.441, (180.974, 201.926, 239.059)), (' A 111  ASP  N  ', ' A 111  ASP  OD1', -0.438, (181.05, 246.719, 249.337)), (' B 391  CYS  CB ', ' B 525  CYS  HA ', -0.433, (231.254, 188.544, 239.364)), (' C 111  ASP  N  ', ' C 111  ASP  OD1', -0.431, (256.247, 216.592, 249.429)), (' A  81  ASN  N  ', ' A  81  ASN  OD1', -0.428, (176.24, 256.541, 236.589)), (' A1142  GLN  N  ', ' A1143  PRO  HD2', -0.424, (203.017, 213.076, 125.774)), (' A 391  CYS  CB ', ' A 525  CYS  HA ', -0.423, (180.934, 202.408, 238.953)), (' C1142  GLN  N  ', ' C1143  PRO  HD2', -0.423, (216.174, 214.603, 125.841)), (' C 391  CYS  CB ', ' C 525  CYS  HA ', -0.422, (217.915, 239.04, 238.934)), (' B1142  GLN  N  ', ' B1143  PRO  HD2', -0.416, (210.541, 202.098, 125.756)), (' C1028  LYS  O  ', ' C1029  MET  C  ', -0.405, (215.36, 200.011, 172.987)), (' A 579  PRO  O  ', ' A1306  NAG  H82', -0.404, (170.914, 198.465, 234.673)), (' C 579  PRO  O  ', ' C1306  NAG  H82', -0.401, (219.564, 249.371, 234.352)), (' B 579  PRO  O  ', ' B1306  NAG  H82', -0.4, (239.616, 182.062, 234.673))]
data['cablam'] = [('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (186.6, 237.8, 231.9)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (182.5, 242.3, 243.9)), ('A', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (183.6, 248.4, 252.2)), ('A', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (194.1, 267.5, 237.9)), ('A', '381', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (195.8, 203.0, 238.9)), ('A', '618', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTT-', (170.9, 220.2, 207.2)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (185.1, 222.9, 193.9)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (184.8, 219.3, 192.9)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (218.5, 235.6, 158.2)), ('A', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (220.2, 228.7, 212.6)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (207.2, 220.8, 171.2)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (216.1, 228.0, 188.1)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (192.4, 203.0, 130.9)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (198.5, 222.7, 151.8)), ('A', '34', 'ARG', 'check CA trace', ' \nTT---', (189.2, 248.7, 218.5)), ('A', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (180.3, 257.9, 218.7)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (185.1, 237.1, 212.7)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (180.3, 212.4, 222.0)), ('A', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (192.6, 198.0, 138.3)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (197.7, 175.8, 231.9)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (195.8, 170.0, 243.9)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (190.0, 167.9, 252.2)), ('B', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (168.2, 167.5, 237.9)), ('B', '381', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (223.2, 201.3, 238.9)), ('B', '618', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTT-', (220.8, 171.0, 207.2)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (211.3, 182.0, 193.9)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (214.6, 183.5, 192.9)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (183.6, 204.5, 158.2)), ('B', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (188.7, 209.5, 212.6)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (202.0, 202.2, 171.2)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (191.4, 206.2, 188.1)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (224.9, 198.2, 130.9)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (204.7, 193.7, 151.8)), ('B', '34', 'ARG', 'check CA trace', ' \nTT---', (186.9, 172.6, 218.5)), ('B', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (183.4, 160.3, 218.7)), ('B', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (199.0, 174.9, 212.7)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (222.7, 183.1, 222.0)), ('B', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (229.1, 200.9, 138.3)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (245.7, 216.4, 231.9)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (251.7, 217.7, 243.9)), ('C', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (256.5, 213.7, 252.2)), ('C', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nEETTE', (267.7, 195.0, 237.9)), ('C', '381', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (211.0, 225.8, 238.9)), ('C', '618', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTT-', (238.4, 238.8, 207.2)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (233.6, 225.1, 193.9)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (230.6, 227.2, 192.9)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (227.9, 189.9, 158.2)), ('C', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (221.1, 191.8, 212.6)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (220.8, 207.0, 171.2)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (222.6, 195.8, 188.1)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (212.8, 228.8, 130.9)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (226.8, 213.6, 151.8)), ('C', '34', 'ARG', 'check CA trace', ' \nTT---', (253.9, 208.7, 218.5)), ('C', '215', 'ASP', 'check CA trace', 'bend\nSSS--', (266.4, 211.8, 218.7)), ('C', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (245.9, 218.0, 212.7)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (226.9, 234.5, 222.0)), ('C', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (208.3, 231.1, 138.3))]
data['smoc'] = [('A', 42, u'VAL', 0.7048838621246675, (208.672, 241.612, 223.24599999999998)), ('A', 53, u'ASP', 0.7149510920447031, (194.647, 236.304, 224.304)), ('A', 80, u'ASP', 0.5726227388069008, (175.10899999999998, 257.267, 233.934)), ('A', 101, u'ILE', 0.6023267966949645, (185.62, 260.65000000000003, 233.602)), ('A', 106, u'PHE', 0.6078372536485784, (186.67399999999998, 247.236, 240.74599999999998)), ('A', 116, u'SER', 0.5713113526329602, (188.14499999999998, 247.24599999999998, 245.85700000000003)), ('A', 117, u'LEU', 0.506814952094796, (190.58200000000002, 248.77299999999997, 243.416)), ('A', 118, u'LEU', 0.5680832968314712, (190.17399999999998, 252.508, 243.061)), ('A', 121, u'ASN', 0.6030306774288152, (192.92200000000003, 261.092, 238.23399999999998)), ('A', 128, u'ILE', 0.5688391298024335, (195.681, 254.20899999999997, 242.92100000000002)), ('A', 137, u'ASN', 0.6518461260091527, (175.23299999999998, 254.819, 247.417)), ('A', 204, u'TYR', 0.5920007406872794, (196.702, 248.82700000000003, 228.86200000000002)), ('A', 205, u'SER', 0.5855696978386307, (195.806, 252.172, 227.399)), ('A', 237, u'ARG', 0.6351208421425885, (181.833, 243.91899999999998, 238.86800000000002)), ('A', 267, u'VAL', 0.5153059365133621, (182.062, 248.977, 227.869)), ('A', 276, u'LEU', 0.7024492915572565, (196.92600000000002, 237.797, 213.625)), ('A', 285, u'ILE', 0.6667664302268, (200.915, 247.04, 215.406)), ('A', 291, u'CYS', 0.6901513258602187, (190.35000000000002, 234.782, 213.222)), ('A', 326, u'ILE', 0.765717202078039, (173.585, 211.74299999999997, 229.12800000000001)), ('A', 340, u'GLU', 0.8171627347163622, (183.21699999999998, 196.134, 257.117)), ('A', 346, u'ARG', 0.721309962490567, (190.592, 192.21099999999998, 263.469)), ('A', 357, u'ARG', 0.7881215153789893, (184.755, 190.85600000000002, 247.059)), ('A', 382, u'VAL', 0.7569412927167161, (193.564, 205.964, 238.62800000000001)), ('A', 383, u'SER', 0.7535494952750977, (193.404, 209.31, 240.383)), ('A', 390, u'LEU', 0.7365248694026042, (184.478, 205.8, 236.98100000000002)), ('A', 410, u'ILE', 0.7487058027114972, (203.13299999999998, 197.442, 248.771)), ('A', 413, u'GLY', 0.653787320782066, (207.441, 197.80100000000002, 240.695)), ('A', 420, u'ASP', 0.6924403682797924, (208.68, 189.36, 247.097)), ('A', 465, u'GLU', 0.7872471537951257, (199.372, 184.562, 245.953)), ('A', 466, u'ARG', 0.7438393907358677, (198.347, 183.42800000000003, 249.46)), ('A', 468, u'ILE', 0.7564405811738756, (199.22899999999998, 179.41299999999998, 253.561)), ('A', 489, u'TYR', 0.7180075301928918, (214.88100000000003, 176.463, 259.97099999999995)), ('A', 505, u'TYR', 0.8008165511453101, (208.024, 199.506, 264.16900000000004)), ('A', 516, u'GLU', 0.809915678724749, (188.98000000000002, 195.71699999999998, 237.439)), ('A', 519, u'HIS', 0.7279672816753647, (185.07899999999998, 196.76, 229.55)), ('A', 538, u'CYS', 0.7800880469576791, (174.123, 214.92200000000003, 219.39200000000002)), ('A', 539, u'VAL', 0.7850282122413182, (174.89100000000002, 214.34, 223.106)), ('A', 554, u'GLU', 0.7965698128475907, (168.257, 202.435, 217.989)), ('A', 598, u'ILE', 0.6446195606287253, (186.066, 229.946, 198.035)), ('A', 649, u'CYS', 0.6468081181032461, (177.077, 222.02800000000002, 201.047)), ('A', 653, u'ALA', 0.6982632190528202, (177.465, 230.98700000000002, 195.76999999999998)), ('A', 661, u'GLU', 0.7097426340161795, (185.49800000000002, 227.48600000000002, 181.80200000000002)), ('A', 666, u'ILE', 0.6414255693320732, (185.10999999999999, 222.86800000000002, 193.939)), ('A', 671, u'CYS', 0.6478454528843712, (183.61899999999997, 225.24299999999997, 189.71599999999998)), ('A', 713, u'ALA', 0.5969553335406317, (189.135, 219.41899999999998, 154.083)), ('A', 729, u'VAL', 0.5935836195382052, (215.373, 222.721, 185.98000000000002)), ('A', 731, u'MET', 0.6130142598067011, (215.94, 224.226, 192.985)), ('A', 738, u'CYS', 0.5722854765267248, (222.059, 219.55, 211.678)), ('A', 741, u'TYR', 0.5471076178869309, (220.18, 223.69899999999998, 214.067)), ('A', 770, u'ILE', 0.6305310891662078, (220.39200000000002, 217.04899999999998, 196.503)), ('A', 773, u'GLU', 0.5560645368458053, (222.30700000000002, 216.85100000000003, 191.536)), ('A', 796, u'ASP', 0.6940982343717367, (220.94299999999998, 238.30200000000002, 157.121)), ('A', 802, u'PHE', 0.6146473044930604, (215.83, 237.14399999999998, 166.07399999999998)), ('A', 805, u'ILE', 0.5708551556425575, (216.024, 236.212, 171.508)), ('A', 865, u'LEU', 0.639218467685243, (226.795, 227.707, 186.595)), ('A', 877, u'LEU', 0.5719608664116822, (222.447, 226.765, 171.27899999999997)), ('A', 882, u'ILE', 0.6168415725643274, (219.939, 229.72299999999998, 163.561)), ('A', 894, u'LEU', 0.6024112003335251, (227.46200000000002, 223.41899999999998, 159.006)), ('A', 903, u'ALA', 0.5794418985669535, (212.74399999999997, 224.73999999999998, 153.698)), ('A', 923, u'ILE', 0.5204773321668191, (206.318, 233.483, 156.939)), ('A', 930, u'ALA', 0.6215900210841562, (204.61599999999999, 236.045, 166.905)), ('A', 950, u'ASP', 0.6288585993958398, (205.994, 227.89800000000002, 192.536)), ('A', 965, u'GLN', 0.5836489754856161, (209.819, 224.815, 214.516)), ('A', 1002, u'GLN', 0.6206244672041453, (212.333, 214.974, 213.873)), ('A', 1027, u'THR', 0.6018395172274974, (215.136, 215.712, 176.39800000000002)), ('A', 1032, u'CYS', 0.5759664945476536, (213.371, 220.112, 170.032)), ('A', 1040, u'VAL', 0.5850377230501684, (203.039, 215.29899999999998, 168.55200000000002)), ('A', 1049, u'LEU', 0.5360073981525025, (209.42800000000003, 223.45800000000003, 162.915)), ('A', 1060, u'VAL', 0.5812606366551446, (214.43200000000002, 226.97299999999998, 181.0)), ('A', 1070, u'ALA', 0.6616600478494699, (194.859, 228.401, 159.106)), ('A', 1081, u'ILE', 0.5768212303972241, (191.405, 207.43200000000002, 139.691)), ('A', 1137, u'VAL', 0.7517638399006101, (195.62, 210.972, 133.58)), ('A', 1301, u'NAG', 0.6476962548163013, (176.965, 240.506, 217.798)), ('A', 1306, u'NAG', 0.6694050742924071, (170.27499999999998, 197.393, 235.817)), ('A', 1307, u'NAG', 0.823694588662738, (185.19299999999998, 202.94, 255.47299999999998)), ('A', 1308, u'NAG', 0.7609927170046928, (195.626, 243.258, 189.611)), ('B', 31, u'SER', 0.7542965371727206, (190.04399999999998, 167.82500000000002, 218.262)), ('B', 40, u'ASP', 0.7111627792928304, (186.47299999999998, 188.944, 225.672)), ('B', 42, u'VAL', 0.7601133815854744, (183.288, 193.04399999999998, 223.24599999999998)), ('B', 80, u'ASP', 0.6173962450350577, (186.511, 156.15, 233.934)), ('B', 97, u'LYS', 0.6576504429222588, (172.186, 160.718, 226.01)), ('B', 106, u'PHE', 0.5669706787478348, (189.415, 171.181, 240.74599999999998)), ('B', 117, u'LEU', 0.5203281962234554, (186.13, 173.797, 243.416)), ('B', 118, u'LEU', 0.548424790048464, (183.1, 171.576, 243.061)), ('B', 137, u'ASN', 0.6476761070813725, (188.569, 157.48200000000003, 247.417)), ('B', 166, u'CYS', 0.5701998545896337, (184.14, 177.42200000000003, 252.583)), ('B', 201, u'PHE', 0.623264209825358, (188.39100000000002, 180.52800000000002, 237.303)), ('B', 213, u'VAL', 0.7383414065501975, (177.82600000000002, 158.053, 219.231)), ('B', 233, u'ILE', 0.4782941374121313, (192.706, 178.474, 244.29)), ('B', 243, u'ALA', 0.5382553385361302, (176.141, 159.42800000000003, 237.70399999999998)), ('B', 244, u'LEU', 0.6439982615914782, (176.036, 155.668, 238.18800000000002)), ('B', 285, u'ILE', 0.7169524285702172, (182.465, 183.612, 215.406)), ('B', 315, u'THR', 0.6844666934061215, (205.21399999999997, 184.96200000000002, 206.71499999999997)), ('B', 318, u'PHE', 0.7070752855418524, (213.183, 180.60899999999998, 211.064)), ('B', 334, u'ASN', 0.7901073516952913, (237.82000000000002, 183.10399999999998, 247.742)), ('B', 342, u'PHE', 0.8417137235818842, (230.067, 196.471, 257.184)), ('B', 346, u'ARG', 0.7603555621160506, (235.10999999999999, 202.08700000000002, 263.469)), ('B', 347, u'PHE', 0.8213348228203835, (233.977, 203.984, 260.409)), ('B', 360, u'ASN', 0.8160774951881832, (239.903, 188.459, 243.316)), ('B', 365, u'TYR', 0.8624861231573729, (225.19899999999998, 190.009, 247.535)), ('B', 369, u'TYR', 0.8382919910899044, (220.345, 192.383, 250.394)), ('B', 370, u'ASN', 0.8660918835590954, (218.407, 189.899, 252.537)), ('B', 382, u'VAL', 0.7540241695848603, (221.71299999999997, 197.784, 238.62800000000001)), ('B', 383, u'SER', 0.7807569074412749, (218.89600000000002, 195.972, 240.383)), ('B', 412, u'PRO', 0.7105864785519209, (223.646, 210.694, 241.67499999999998)), ('B', 413, u'GLY', 0.734247974823846, (221.844, 213.88400000000001, 240.695)), ('B', 420, u'ASP', 0.7742981870119436, (228.535, 219.177, 247.097)), ('B', 451, u'TYR', 0.8125882690461153, (233.135, 212.55, 263.29799999999994)), ('B', 466, u'ARG', 0.7657668736516415, (238.83800000000002, 213.194, 249.46)), ('B', 489, u'TYR', 0.7552387543727431, (236.60299999999998, 230.996, 259.97099999999995)), ('B', 499, u'PRO', 0.8161599327168293, (221.753, 208.194, 271.73799999999994)), ('B', 513, u'LEU', 0.7648148952527755, (229.429, 200.162, 246.631)), ('B', 516, u'GLU', 0.799264373245166, (232.879, 198.93800000000002, 237.44)), ('B', 519, u'HIS', 0.7140828600828818, (233.92700000000002, 195.038, 229.55)), ('B', 528, u'LYS', 0.8467922810759526, (227.12, 181.029, 240.577)), ('B', 546, u'LEU', 0.8007341976232424, (227.601, 188.788, 229.4)), ('B', 550, u'GLY', 0.7728450737745114, (225.018, 181.60899999999998, 219.42700000000002)), ('B', 570, u'ALA', 0.656647764781483, (226.901, 196.694, 215.6)), ('B', 661, u'GLU', 0.7109978697827305, (207.108, 180.038, 181.80200000000002)), ('B', 666, u'ILE', 0.6371762892715546, (211.30100000000002, 182.011, 193.939)), ('B', 694, u'ALA', 0.7136057583144522, (209.97, 173.88000000000002, 190.96)), ('B', 741, u'TYR', 0.6313098339133609, (193.046, 211.967, 214.067)), ('B', 753, u'LEU', 0.5305674283946196, (199.477, 218.788, 220.35600000000002)), ('B', 767, u'LEU', 0.6298248699349231, (198.125, 215.82200000000003, 201.561)), ('B', 781, u'VAL', 0.5816745189745647, (195.824, 213.14499999999998, 180.202)), ('B', 796, u'ASP', 0.7544151267441869, (180.01899999999998, 205.32600000000002, 157.121)), ('B', 816, u'SER', 0.6359343378710046, (180.999, 202.948, 175.35600000000002)), ('B', 819, u'GLU', 0.659520801684866, (184.28, 201.41299999999998, 178.953)), ('B', 854, u'LYS', 0.7081647709003636, (185.866, 206.751, 208.642)), ('B', 895, u'GLN', 0.5599785351303787, (187.27299999999997, 215.785, 157.784)), ('B', 903, u'ALA', 0.47224580721940024, (195.863, 205.006, 153.698)), ('B', 909, u'ILE', 0.5162999678585932, (204.571, 202.441, 158.306)), ('B', 936, u'ASP', 0.7351216817833772, (186.033, 188.843, 175.35600000000002)), ('B', 979, u'ASP', 0.6049027295169053, (189.876, 206.439, 229.07299999999998)), ('B', 989, u'ALA', 0.6334951498189922, (197.101, 212.268, 232.106)), ('B', 996, u'LEU', 0.6380488146336466, (199.809, 208.636, 222.29)), ('B', 1003, u'SER', 0.5394379325934651, (201.85000000000002, 207.35100000000003, 212.281)), ('B', 1018, u'ILE', 0.5565165046345092, (201.177, 207.889, 189.824)), ('B', 1025, u'ALA', 0.5864848861822586, (199.63899999999998, 208.46, 179.7)), ('B', 1032, u'CYS', 0.5205508788065428, (199.55700000000002, 207.864, 170.032)), ('B', 1033, u'VAL', 0.5709889357936445, (195.88200000000003, 208.999, 169.82100000000003)), ('B', 1057, u'PRO', 0.674113028008411, (188.41899999999998, 204.054, 187.162)), ('B', 1070, u'ALA', 0.6342316634093015, (201.635, 187.687, 159.106)), ('B', 1081, u'ILE', 0.59301244617457, (221.52200000000002, 195.18, 139.691)), ('B', 1096, u'VAL', 0.5544757426674582, (214.102, 189.98100000000002, 145.05700000000002)), ('B', 1119, u'ASN', 0.5970817710085261, (211.85100000000003, 202.007, 140.096)), ('B', 1120, u'THR', 0.6085288867021055, (215.618, 202.256, 140.39000000000001)), ('B', 1142, u'GLN', 0.8044780045482022, (212.10299999999998, 202.484, 124.48)), ('B', 1147, u'SER', 0.7696487475235327, (207.009, 201.82500000000002, 117.584)), ('B', 1301, u'NAG', 0.6663449365656888, (200.098, 166.137, 217.798)), ('B', 1306, u'NAG', 0.7291271571817897, (240.78, 181.901, 235.817)), ('B', 1307, u'NAG', 0.7879734071726979, (228.517, 192.047, 255.47299999999998)), ('B', 1308, u'NAG', 0.7519957713510729, (188.38500000000002, 180.923, 189.611)), ('C', 47, u'VAL', 0.8220942460705055, (238.23999999999998, 198.14499999999998, 210.983)), ('C', 101, u'ILE', 0.5967894939722862, (266.05400000000003, 205.789, 233.602)), ('C', 106, u'PHE', 0.5074767624086802, (253.911, 211.583, 240.74599999999998)), ('C', 117, u'LEU', 0.5090992992699181, (253.288, 207.43, 243.416)), ('C', 119, u'ILE', 0.5119879789747345, (257.72299999999996, 203.48100000000002, 240.35800000000003)), ('C', 193, u'VAL', 0.5415905966343364, (251.418, 206.92000000000002, 228.72299999999998)), ('C', 204, u'TYR', 0.6262876954247334, (250.27399999999997, 202.10299999999998, 228.86200000000002)), ('C', 210, u'ILE', 0.7939418291553341, (265.972, 200.999, 217.948)), ('C', 220, u'PHE', 0.745942125065681, (254.136, 204.289, 214.35100000000003)), ('C', 243, u'ALA', 0.5436577909934487, (270.72599999999994, 205.963, 237.70399999999998)), ('C', 263, u'ALA', 0.6851911773524552, (269.70599999999996, 208.49, 228.24499999999998)), ('C', 267, u'VAL', 0.5415562872735425, (257.724, 214.707, 227.869)), ('C', 273, u'ARG', 0.6991040138716594, (241.512, 214.71899999999997, 220.416)), ('C', 285, u'ILE', 0.7264474041543144, (246.62, 199.348, 215.406)), ('C', 291, u'CYS', 0.7042536595386046, (241.287, 214.626, 213.222)), ('C', 295, u'PRO', 0.6906051877068361, (242.093, 219.96800000000002, 206.816)), ('C', 332, u'ILE', 0.7978871391239958, (221.024, 248.54299999999998, 242.172)), ('C', 346, u'ARG', 0.7513601248031174, (204.298, 235.702, 263.469)), ('C', 350, u'VAL', 0.7786387402259326, (196.89600000000002, 229.05, 255.863)), ('C', 357, u'ARG', 0.797167785995728, (206.04299999999998, 241.435, 247.059)), ('C', 369, u'TYR', 0.8298555812022647, (220.084, 227.768, 250.394)), ('C', 383, u'SER', 0.7800829407167639, (217.7, 224.718, 240.383)), ('C', 390, u'LEU', 0.680525252775621, (219.123, 234.20299999999997, 236.98100000000002)), ('C', 398, u'ASP', 0.7800677900187076, (203.623, 233.30700000000002, 250.34)), ('C', 412, u'PRO', 0.7341173014800155, (202.576, 221.47, 241.67499999999998)), ('C', 413, u'GLY', 0.6927320817929825, (200.71499999999997, 218.315, 240.695)), ('C', 466, u'ARG', 0.7563454857062145, (192.815, 233.37800000000001, 249.46)), ('C', 491, u'PRO', 0.762317827135413, (184.41, 224.154, 256.584)), ('C', 501, u'ASN', 0.7826670083115422, (203.02, 216.62800000000001, 269.368)), ('C', 505, u'TYR', 0.7849078900159256, (201.9, 216.95800000000003, 264.16900000000004)), ('C', 510, u'VAL', 0.824422188342737, (206.376, 227.595, 255.097)), ('C', 512, u'VAL', 0.8181728985604649, (206.68800000000002, 229.69899999999998, 248.977)), ('C', 519, u'HIS', 0.7289861751745295, (210.994, 238.202, 229.55)), ('C', 528, u'LYS', 0.8107259531569032, (226.529, 239.312, 240.577)), ('C', 538, u'CYS', 0.7847553278322691, (232.201, 238.60899999999998, 219.39200000000002)), ('C', 562, u'PHE', 0.7312383128241094, (207.792, 248.685, 228.165)), ('C', 570, u'ALA', 0.6726437293205065, (213.07299999999998, 231.29, 215.6)), ('C', 574, u'ASP', 0.7709507289084166, (217.10399999999998, 239.698, 218.084)), ('C', 603, u'ASN', 0.8227968781417977, (246.95700000000002, 208.909, 195.38700000000003)), ('C', 653, u'ALA', 0.6608186124970611, (244.44299999999998, 227.683, 195.76999999999998)), ('C', 671, u'CYS', 0.6488288638399676, (236.39100000000002, 225.225, 189.71599999999998)), ('C', 695, u'TYR', 0.665526060736139, (239.79299999999998, 229.512, 187.84)), ('C', 699, u'LEU', 0.6686720851178442, (232.166, 226.512, 178.755)), ('C', 714, u'ILE', 0.6143223261340781, (228.004, 219.823, 152.912)), ('C', 725, u'GLU', 0.601622797394602, (225.68800000000002, 204.661, 177.377)), ('C', 738, u'CYS', 0.6280421614576214, (212.24099999999999, 194.782, 211.678)), ('C', 741, u'TYR', 0.6646975969584554, (216.77299999999997, 194.334, 214.067)), ('C', 759, u'PHE', 0.6743500939719407, (204.879, 200.226, 212.687)), ('C', 774, u'GLN', 0.6191345013657299, (213.502, 195.23399999999998, 191.142)), ('C', 796, u'ASP', 0.699362837979396, (229.039, 186.373, 157.121)), ('C', 802, u'PHE', 0.6114292718643585, (230.593, 191.379, 166.07399999999998)), ('C', 805, u'ILE', 0.5918403827482508, (229.689, 191.677, 171.508)), ('C', 816, u'SER', 0.6150616753442834, (230.608, 188.41, 175.35600000000002)), ('C', 819, u'GLU', 0.5229303308643023, (230.297, 192.01899999999998, 178.953)), ('C', 867, u'ASP', 0.6575790234145745, (223.405, 186.905, 185.218)), ('C', 901, u'GLN', 0.5255951763294797, (220.126, 196.04399999999998, 156.72299999999998)), ('C', 923, u'ILE', 0.5808934802101867, (232.178, 201.447, 156.939)), ('C', 924, u'ALA', 0.555890104369163, (232.88800000000003, 197.93200000000002, 158.106)), ('C', 938, u'LEU', 0.6789499866546801, (236.30700000000002, 200.009, 179.329)), ('C', 948, u'LEU', 0.5962287684076453, (226.496, 201.44899999999998, 188.30700000000002)), ('C', 962, u'LEU', 0.5526737019266947, (221.668, 201.168, 209.54299999999998)), ('C', 990, u'GLU', 0.5628804573653687, (211.38000000000002, 198.539, 230.11899999999997)), ('C', 997, u'ILE', 0.5537795488162425, (213.097, 200.812, 220.516)), ('C', 1018, u'ILE', 0.5419705867812022, (216.23999999999998, 203.414, 189.824)), ('C', 1060, u'VAL', 0.6455430300220039, (222.483, 197.67499999999998, 181.0)), ('C', 1062, u'PHE', 0.605015386204655, (224.224, 200.24499999999998, 175.20399999999998)), ('C', 1070, u'ALA', 0.6709804373725686, (233.506, 213.912, 159.106)), ('C', 1095, u'PHE', 0.5901945637894476, (221.58700000000002, 222.947, 144.737)), ('C', 1116, u'THR', 0.6819748070841787, (217.804, 217.38700000000003, 135.454))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-21452/6vxx/Model_validation_1/validation_cootdata/molprobity_probe6vxx_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)


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
data['rota'] = [('A', ' 385 ', 'THR', 0.029869507420391437, (219.52200000000005, 190.205, 173.858)), ('A', ' 985 ', 'CYS', 0.1278395611547893, (206.41000000000005, 219.769, 179.55299999999997)), ('B', ' 385 ', 'THR', 0.029819124922813592, (184.41000000000005, 197.825, 173.855)), ('B', ' 985 ', 'CYS', 0.05466122950362249, (216.62900000000002, 194.352, 179.547)), ('C', ' 385 ', 'THR', 0.029809320338071085, (208.566, 224.423, 173.852)), ('C', ' 985 ', 'CYS', 0.09144262379814702, (189.49900000000005, 198.311, 179.551))]
data['clusters'] = [('A', '270', 1, 'smoc Outlier', (241.721, 204.42700000000002, 189.515)), ('A', '273', 1, 'smoc Outlier', (235.593, 203.637, 195.503)), ('A', '274', 1, 'smoc Outlier', (233.475, 205.721, 197.85200000000003)), ('A', '53', 1, 'smoc Outlier', (233.818, 207.76999999999998, 191.434)), ('A', '54', 1, 'smoc Outlier', (237.071, 206.512, 189.967)), ('A', '55', 1, 'Bond angle:CA:CB:CG', (239.672, 207.681, 192.495)), ('A', '86', 1, 'cablam Outlier\nsmoc Outlier', (245.5, 202.4, 180.8)), ('A', '88', 1, 'cablam Outlier', (239.9, 201.9, 183.7)), ('A', '406', 2, 'smoc Outlier', (195.781, 193.4, 160.45200000000003)), ('A', '407', 2, 'smoc Outlier', (199.406, 192.82000000000002, 161.51399999999998)), ('A', '410', 2, 'smoc Outlier', (198.834, 190.01299999999998, 166.612)), ('A', '411', 2, 'smoc Outlier', (199.542, 190.909, 170.22)), ('A', '425', 2, 'smoc Outlier', (196.806, 185.845, 172.048)), ('A', '664', 3, 'smoc Outlier', (232.181, 198.901, 225.84)), ('A', '666', 3, 'cablam Outlier', (230.2, 193.2, 223.1)), ('A', '667', 3, 'cablam Outlier', (227.8, 190.6, 224.3)), ('A', '671', 3, 'smoc Outlier', (233.201, 193.71699999999998, 227.32200000000003)), ('A', '1043', 4, 'cablam Outlier', (214.2, 209.0, 246.5)), ('A', '1062', 4, 'smoc Outlier', (216.653, 216.319, 242.22)), ('A', '1064', 4, 'smoc Outlier', (218.218, 213.687, 247.512)), ('A', '1066', 4, 'smoc Outlier', (219.577, 210.42600000000002, 252.789)), ('A', '383', 5, 'side-chain clash', (213.357, 191.661, 174.675)), ('A', '384', 5, 'side-chain clash', (213.357, 191.661, 174.675)), ('A', '385', 5, 'Rotamer', (219.52200000000005, 190.205, 173.858)), ('A', '387', 5, 'smoc Outlier', (216.684, 185.341, 174.942)), ('A', '1303', 6, 'Bond angle:C8:C7:N2', (219.824, 165.58100000000002, 179.948)), ('A', '331', 6, 'Bond angle:CA:CB:CG', (224.045, 167.873, 176.57)), ('A', '332', 6, 'smoc Outlier', (221.906, 168.016, 173.403)), ('A', '101', 7, 'smoc Outlier', (258.55, 215.24299999999997, 180.95800000000003)), ('A', '263', 7, 'smoc Outlier', (262.64400000000006, 213.504, 186.184)), ('A', '265', 7, 'smoc Outlier', (257.141, 209.76299999999998, 187.23999999999998)), ('A', '985', 8, 'Rotamer', (206.41000000000005, 219.769, 179.55299999999997)), ('A', '988', 8, 'Dihedral angle:CB:CG:CD:OE1', (205.88000000000002, 214.363, 181.26999999999998)), ('A', '990', 8, 'smoc Outlier', (203.71699999999998, 215.575, 186.295)), ('A', '452', 9, 'smoc Outlier', (190.597, 183.11899999999997, 154.232)), ('A', '492', 9, 'smoc Outlier', (183.997, 183.032, 156.184)), ('A', '189', 10, 'smoc Outlier', (255.095, 218.44899999999998, 191.24699999999999)), ('A', '210', 10, 'smoc Outlier', (258.101, 221.056, 196.031)), ('A', '1072', 11, 'smoc Outlier', (228.85700000000003, 198.972, 263.046)), ('A', '713', 11, 'smoc Outlier', (225.072, 193.98600000000002, 263.775)), ('A', '811', 12, 'side-chain clash', (225.216, 232.198, 238.11)), ('A', '820', 12, 'side-chain clash', (225.216, 232.198, 238.11)), ('A', '1087', 13, 'smoc Outlier', (208.761, 186.636, 278.82599999999996)), ('A', '1125', 13, 'cablam CA Geom Outlier', (206.5, 182.9, 279.2)), ('A', '278', 14, 'smoc Outlier', (235.45700000000002, 217.537, 203.495)), ('A', '279', 14, 'smoc Outlier', (234.806, 221.056, 202.20399999999998)), ('A', '220', 15, 'cablam CA Geom Outlier', (246.7, 216.2, 200.3)), ('A', '34', 15, 'cablam CA Geom Outlier', (247.0, 211.6, 196.3)), ('A', '1058', 16, 'cablam Outlier', (214.4, 220.4, 229.2)), ('A', '731', 16, 'smoc Outlier', (211.24899999999997, 217.92700000000002, 224.237)), ('A', '1039', 17, 'smoc Outlier', (209.5, 203.768, 249.36800000000002)), ('A', '1040', 17, 'smoc Outlier', (212.84, 202.01, 249.065)), ('A', '869', 18, 'smoc Outlier', (209.24499999999998, 231.121, 235.33700000000002)), ('A', '870', 18, 'smoc Outlier', (210.542, 227.64399999999998, 235.977)), ('A', '551', 19, 'smoc Outlier', (227.409, 176.90200000000002, 197.383)), ('A', '552', 19, 'smoc Outlier', (226.21499999999997, 173.767, 195.607)), ('B', '662', 1, 'smoc Outlier', (183.848, 183.76899999999998, 231.79299999999998)), ('B', '664', 1, 'smoc Outlier', (185.599, 182.523, 225.839)), ('B', '666', 1, 'cablam Outlier', (181.7, 187.0, 223.1)), ('B', '667', 1, 'cablam Outlier', (180.6, 190.5, 224.3)), ('B', '670', 1, 'smoc Outlier', (177.894, 186.96200000000002, 227.17)), ('B', '1021', 2, 'smoc Outlier', (206.948, 196.35500000000002, 232.345)), ('B', '1022', 2, 'smoc Outlier', (210.671, 196.418, 233.146)), ('B', '774', 2, 'smoc Outlier', (216.972, 195.666, 226.23)), ('B', '777', 2, 'smoc Outlier', (215.975, 197.01899999999998, 231.10999999999999)), ('B', '781', 2, 'smoc Outlier', (215.666, 194.984, 237.30800000000002)), ('B', '541', 3, 'smoc Outlier', (172.036, 197.818, 188.818)), ('B', '542', 3, 'smoc Outlier', (172.997, 199.96800000000002, 185.82700000000003)), ('B', '544', 3, 'smoc Outlier', (172.79899999999998, 205.29, 182.41899999999998)), ('B', '549', 3, 'cablam CA Geom Outlier', (175.2, 196.4, 193.9)), ('B', '1087', 4, 'smoc Outlier', (186.67299999999997, 208.947, 278.82)), ('B', '1123', 4, 'smoc Outlier', (190.75, 212.624, 276.879)), ('B', '1125', 4, 'cablam CA Geom Outlier', (184.5, 212.8, 279.2)), ('B', '797', 5, 'cablam Outlier', (216.8, 180.2, 259.6)), ('B', '898', 5, 'smoc Outlier', (216.02, 185.258, 260.72999999999996)), ('B', '902', 5, 'smoc Outlier', (210.40200000000002, 188.227, 260.828)), ('B', '122', 6, 'smoc Outlier', (194.011, 149.681, 175.35700000000003)), ('B', '1301', 6, 'Bond angle:C8:C7:N2', (197.165, 145.777, 174.559)), ('B', '1303', 7, 'Bond angle:C8:C7:N2', (162.933, 209.877, 179.936)), ('B', '331', 7, 'Bond angle:CA:CB:CG', (162.809, 205.075, 176.559)), ('B', '763', 8, 'smoc Outlier', (215.813, 201.648, 210.046)), ('B', '767', 8, 'smoc Outlier', (216.51, 198.76, 215.696)), ('B', '811', 9, 'side-chain clash', (217.929, 171.885, 238.021)), ('B', '820', 9, 'side-chain clash', (217.929, 171.885, 238.021)), ('B', '1109', 10, 'cablam Outlier', (194.8, 189.5, 266.0)), ('B', '715', 10, 'smoc Outlier', (190.559, 187.55800000000002, 263.47299999999996)), ('B', '54', 11, 'smoc Outlier', (189.755, 174.478, 189.96800000000002)), ('B', '55', 11, 'Bond angle:CA:CB:CG', (189.466, 171.641, 192.496)), ('B', '216', 12, 'smoc Outlier', (184.64399999999998, 154.63899999999998, 196.08200000000002)), ('B', '217', 12, 'smoc Outlier', (187.147, 154.166, 198.98100000000002)), ('B', '985', 13, 'Rotamer', (216.62900000000002, 194.352, 179.547)), ('B', '988', 13, 'Dihedral angle:CB:CG:CD:OE1', (212.151, 197.563, 181.27299999999997)), ('B', '313', 14, 'smoc Outlier', (188.38600000000002, 184.2, 215.86100000000002)), ('B', '597', 14, 'smoc Outlier', (184.069, 181.369, 214.92000000000002)), ('B', '86', 15, 'cablam Outlier\nsmoc Outlier', (182.0, 169.2, 180.8)), ('B', '88', 15, 'cablam Outlier', (184.4, 174.3, 183.7)), ('B', '84', 16, 'side-chain clash', (176.24, 165.107, 180.697)), ('B', '85', 16, 'side-chain clash', (176.24, 165.107, 180.697)), ('B', '524', 17, 'smoc Outlier', (172.89200000000002, 210.146, 174.167)), ('B', '525', 17, 'smoc Outlier', (172.689, 206.446, 175.171)), ('B', '104', 18, 'smoc Outlier', (186.948, 159.389, 176.617)), ('B', '240', 18, 'smoc Outlier', (183.012, 157.80200000000002, 178.06)), ('B', '223', 19, 'smoc Outlier', (196.98200000000003, 163.787, 191.586)), ('B', '37', 19, 'smoc Outlier', (196.055, 167.791, 192.545)), ('B', '220', 20, 'cablam CA Geom Outlier', (193.3, 161.3, 200.3)), ('B', '34', 20, 'cablam CA Geom Outlier', (189.1, 163.3, 196.3)), ('B', '746', 21, 'smoc Outlier', (222.105, 192.317, 193.497)), ('B', '749', 21, 'smoc Outlier', (218.81, 197.21399999999997, 192.35700000000003)), ('B', '955', 22, 'smoc Outlier', (208.111, 188.664, 218.089)), ('B', '958', 22, 'smoc Outlier', (206.661, 189.555, 213.284)), ('B', '1041', 23, 'smoc Outlier', (198.038, 194.847, 246.601)), ('B', '1043', 23, 'cablam Outlier', (203.4, 193.0, 246.5)), ('C', '106', 1, 'smoc Outlier', (179.85800000000003, 239.447, 174.374)), ('C', '233', 1, 'smoc Outlier', (184.252, 232.26399999999998, 170.873)), ('C', '235', 1, 'smoc Outlier', (185.23499999999999, 237.062, 174.94)), ('C', '270', 1, 'smoc Outlier', (185.15, 236.541, 189.506)), ('C', '273', 1, 'smoc Outlier', (188.899, 231.631, 195.494)), ('C', '53', 1, 'smoc Outlier', (186.207, 228.026, 191.42700000000002)), ('C', '54', 1, 'smoc Outlier', (185.67, 231.472, 189.95800000000003)), ('C', '55', 1, 'Bond angle:CA:CB:CG', (183.35700000000003, 233.14, 192.48600000000002)), ('C', '86', 1, 'cablam Outlier\nsmoc Outlier', (185.0, 240.8, 180.8)), ('C', '88', 1, 'cablam Outlier', (188.2, 236.2, 183.7)), ('C', '647', 2, 'smoc Outlier', (206.512, 234.026, 220.14399999999998)), ('C', '666', 2, 'cablam Outlier', (200.6, 232.2, 223.1)), ('C', '667', 2, 'cablam Outlier', (204.1, 231.4, 224.3)), ('C', '671', 2, 'smoc Outlier', (198.686, 234.529, 227.312)), ('C', '539', 3, 'smoc Outlier', (212.184, 238.765, 192.707)), ('C', '540', 3, 'smoc Outlier', (211.346, 235.97, 190.29399999999998)), ('C', '549', 3, 'cablam CA Geom Outlier', (212.0, 233.1, 193.9)), ('C', '1125', 4, 'cablam CA Geom Outlier', (221.5, 216.8, 279.2)), ('C', '1129', 4, 'smoc Outlier', (220.92200000000003, 220.476, 273.31)), ('C', '1132', 4, 'smoc Outlier', (216.905, 223.931, 275.42499999999995)), ('C', '423', 5, 'smoc Outlier', (226.655, 204.85100000000003, 166.077)), ('C', '425', 5, 'smoc Outlier', (223.7, 206.929, 172.047)), ('C', '429', 5, 'smoc Outlier', (221.108, 210.65800000000002, 176.36200000000002)), ('C', '1304', 6, 'Bond angle:C8:C7:N2', (219.298, 225.48000000000002, 160.691)), ('C', '342', 6, 'smoc Outlier', (221.495, 220.953, 158.503)), ('C', '1303', 7, 'Bond angle:C8:C7:N2', (229.74099999999999, 236.99800000000002, 179.937)), ('C', '331', 7, 'Bond angle:CA:CB:CG', (225.64499999999998, 239.506, 176.559)), ('C', '811', 8, 'side-chain clash', (169.327, 208.478, 237.837)), ('C', '820', 8, 'side-chain clash', (169.327, 208.478, 237.837)), ('C', '131', 9, 'smoc Outlier', (176.155, 235.833, 164.24899999999997)), ('C', '166', 9, 'smoc Outlier', (175.333, 231.824, 163.35200000000003)), ('C', '711', 10, 'smoc Outlier', (208.26299999999998, 229.85700000000003, 266.48599999999993)), ('C', '713', 10, 'smoc Outlier', (202.518, 227.366, 263.768)), ('C', '263', 11, 'smoc Outlier', (166.82800000000003, 250.122, 186.17)), ('C', '265', 11, 'smoc Outlier', (172.82000000000002, 247.226, 187.227)), ('C', '985', 12, 'Rotamer', (189.49900000000005, 198.311, 179.551)), ('C', '988', 12, 'Dihedral angle:CB:CG:CD:OE1', (194.465, 200.531, 181.272)), ('C', '1018', 13, 'smoc Outlier', (195.039, 204.606, 227.511)), ('C', '1022', 13, 'smoc Outlier', (194.202, 202.394, 233.14399999999998)), ('C', '240', 14, 'smoc Outlier', (174.60299999999998, 245.647, 178.046)), ('C', '241', 14, 'smoc Outlier', (171.39600000000002, 246.39100000000002, 176.146)), ('C', '220', 15, 'cablam CA Geom Outlier', (172.5, 235.0, 200.3)), ('C', '34', 15, 'cablam CA Geom Outlier', (176.3, 237.6, 196.3)), ('C', '1037', 16, 'smoc Outlier', (197.58200000000002, 206.101, 251.24599999999998)), ('C', '1043', 16, 'cablam Outlier', (194.9, 210.4, 246.5)), ('C', '942', 17, 'smoc Outlier', (180.18800000000002, 219.79399999999998, 231.415)), ('C', '945', 17, 'smoc Outlier', (184.684, 215.373, 232.485)), ('E', '2', 1, 'Bond angle:C8:C7:N2', (232.02100000000002, 216.317, 259.684)), ('F', '1', 1, 'Bond angle:C8:C7:N2', (226.136, 230.816, 256.375)), ('F', '2', 1, 'Bond angle:C8:C7:N2', (231.583, 230.564, 246.272)), ('H', '2', 1, 'Bond angle:C8:C7:N2', (200.753, 173.96, 259.688)), ('I', '1', 1, 'Bond angle:C8:C7:N2', (216.253, 171.806, 256.383)), ('I', '2', 1, 'Bond angle:C8:C7:N2', (213.313, 167.21299999999997, 246.28)), ('K', '2', 1, 'Bond angle:C8:C7:N2', (179.70399999999998, 222.21699999999998, 259.67900000000003)), ('L', '1', 1, 'Bond angle:C8:C7:N2', (170.09, 209.87, 256.373)), ('L', '2', 1, 'Bond angle:C8:C7:N2', (167.585, 214.71099999999998, 246.26899999999998))]
data['probe'] = [(' C 811  LYS  NZ ', ' C 820  ASP  OD2', -0.557, (169.327, 208.478, 237.837)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.552, (225.216, 232.198, 238.11)), (' B 811  LYS  NZ ', ' B 820  ASP  OD2', -0.541, (217.929, 171.885, 238.021)), (' B1028  LYS  NZ ', ' B1042  PHE  O  ', -0.433, (203.085, 194.514, 243.194)), (' C1028  LYS  NZ ', ' C1042  PHE  O  ', -0.433, (196.154, 209.915, 243.223)), (' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.432, (212.8, 208.081, 242.806)), (' A 383  CYS  HA ', ' A 384  PRO  HD3', -0.417, (213.357, 191.661, 174.675)), (' B  84  LEU  HA ', ' B  85  PRO  HD3', -0.402, (176.24, 165.107, 180.697))]
data['cablam'] = [('A', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (245.5, 202.4, 180.8)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (239.9, 201.9, 183.7)), ('A', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (249.4, 205.1, 163.6)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (230.2, 193.2, 223.1)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (227.8, 190.6, 224.3)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (218.6, 227.1, 259.6)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (214.2, 209.0, 246.5)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (214.4, 220.4, 229.2)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (210.2, 185.9, 287.0)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (221.5, 203.4, 266.0)), ('A', '34', 'ARG', 'check CA trace', ' \nTT---', (247.0, 211.6, 196.3)), ('A', '220', 'PHE', 'check CA trace', ' \n-----', (246.7, 216.2, 200.3)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (240.9, 201.8, 203.4)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (225.3, 183.0, 193.9)), ('A', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (206.5, 182.9, 279.2)), ('B', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (182.0, 169.2, 180.8)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (184.4, 174.3, 183.7)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (182.3, 164.5, 163.6)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (181.7, 187.0, 223.1)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (180.6, 190.5, 224.3)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (216.8, 180.2, 259.6)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (203.4, 193.0, 246.5)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (213.1, 187.2, 229.2)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (185.3, 208.1, 287.0)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (194.8, 189.5, 266.0)), ('B', '34', 'ARG', 'check CA trace', ' \nTT---', (189.1, 163.3, 196.3)), ('B', '220', 'PHE', 'check CA trace', ' \n-----', (193.3, 161.3, 200.3)), ('B', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (183.8, 173.5, 203.4)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (175.2, 196.4, 193.9)), ('B', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (184.5, 212.8, 279.2)), ('C', '86', 'PHE', 'check CA trace,carbonyls, peptide', ' \nEE-TT', (185.0, 240.8, 180.8)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TT-E', (188.2, 236.2, 183.7)), ('C', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (180.7, 242.9, 163.6)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (200.6, 232.2, 223.1)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (204.1, 231.4, 224.3)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (177.1, 205.2, 259.6)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (194.9, 210.4, 246.5)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (185.0, 204.9, 229.2)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (217.0, 218.5, 287.0)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (196.1, 219.6, 266.0)), ('C', '34', 'ARG', 'check CA trace', ' \nTT---', (176.3, 237.6, 196.3)), ('C', '220', 'PHE', 'check CA trace', ' \n-----', (172.5, 235.0, 200.3)), ('C', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (187.8, 237.1, 203.4)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (212.0, 233.1, 193.9)), ('C', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (221.5, 216.8, 279.2))]
data['smoc'] = [('A', 53, u'ASP', 0.48754110510367366, (233.818, 207.76999999999998, 191.434)), ('A', 54, u'LEU', 0.4876645393772769, (237.071, 206.512, 189.967)), ('A', 62, u'VAL', 0.4240829479186266, (252.26, 203.24099999999999, 192.196)), ('A', 80, u'ASP', 0.4702239849854144, (262.59299999999996, 205.266, 180.365)), ('A', 86, u'PHE', 0.4554590061425808, (245.469, 202.433, 180.798)), ('A', 101, u'ILE', 0.38450523332361125, (258.55, 215.24299999999997, 180.95800000000003)), ('A', 126, u'VAL', 0.48147007192452773, (249.51899999999998, 223.24099999999999, 175.648)), ('A', 135, u'PHE', 0.421659320838215, (255.664, 207.048, 166.68)), ('A', 166, u'CYS', 0.2919901970545075, (242.55100000000002, 215.284, 163.36)), ('A', 189, u'LEU', 0.6151349097858655, (255.095, 218.44899999999998, 191.24699999999999)), ('A', 210, u'ILE', 0.7920200513263418, (258.101, 221.056, 196.031)), ('A', 213, u'VAL', 0.7370106787916784, (264.412, 214.692, 195.21899999999997)), ('A', 223, u'LEU', 0.47737235518521426, (242.71599999999998, 218.11599999999999, 191.58100000000002)), ('A', 263, u'ALA', 0.449324633236253, (262.64400000000006, 213.504, 186.184)), ('A', 265, u'TYR', 0.4088766679263136, (257.141, 209.76299999999998, 187.23999999999998)), ('A', 270, u'LEU', 0.49631440297268065, (241.721, 204.42700000000002, 189.515)), ('A', 273, u'ARG', 0.41299654199863906, (235.593, 203.637, 195.503)), ('A', 274, u'THR', 0.553410086708297, (233.475, 205.721, 197.85200000000003)), ('A', 278, u'LYS', 0.56675887527819, (235.45700000000002, 217.537, 203.495)), ('A', 279, u'TYR', 0.5592180835819124, (234.806, 221.056, 202.20399999999998)), ('A', 308, u'VAL', 0.5999735657981692, (234.375, 208.73299999999998, 216.01399999999998)), ('A', 320, u'VAL', 0.6269656710724018, (232.108, 185.839, 200.6)), ('A', 332, u'ILE', 0.6919383982432086, (221.906, 168.016, 173.403)), ('A', 337, u'PRO', 0.6785031246896229, (213.785, 173.484, 163.001)), ('A', 348, u'ALA', 0.7027364882572066, (197.925, 178.523, 156.469)), ('A', 387, u'LEU', 0.6294365044571698, (216.684, 185.341, 174.942)), ('A', 406, u'GLU', 0.4917346720288436, (195.781, 193.4, 160.45200000000003)), ('A', 407, u'VAL', 0.5770716689533243, (199.406, 192.82000000000002, 161.51399999999998)), ('A', 410, u'ILE', 0.49535936239322925, (198.834, 190.01299999999998, 166.612)), ('A', 411, u'ALA', 0.6805506778232426, (199.542, 190.909, 170.22)), ('A', 425, u'LEU', 0.6561608244074645, (196.806, 185.845, 172.048)), ('A', 435, u'ALA', 0.6126859919318303, (206.198, 189.053, 160.491)), ('A', 452, u'LEU', 0.7953816441255817, (190.597, 183.11899999999997, 154.232)), ('A', 468, u'ILE', 0.6691761761253333, (187.447, 175.41, 162.21899999999997)), ('A', 492, u'LEU', 0.6617409650200231, (183.997, 183.032, 156.184)), ('A', 496, u'GLY', 0.7360523042123881, (192.306, 188.493, 146.756)), ('A', 499, u'PRO', 0.8311041824076556, (201.156, 192.504, 143.69899999999998)), ('A', 503, u'VAL', 0.6528439129054382, (201.033, 198.11299999999997, 151.594)), ('A', 524, u'VAL', 0.5481001534597617, (214.61299999999997, 174.069, 174.177)), ('A', 542, u'ASN', 0.6874905059353069, (223.374, 179.252, 185.834)), ('A', 551, u'VAL', 0.7167192675779209, (227.409, 176.90200000000002, 197.383)), ('A', 552, u'LEU', 0.6799561754018878, (226.21499999999997, 173.767, 195.607)), ('A', 562, u'PHE', 0.6293789950354411, (208.256, 166.523, 186.672)), ('A', 620, u'VAL', 0.7375061562972425, (236.60999999999999, 184.364, 208.692)), ('A', 660, u'TYR', 0.6590323502756309, (236.467, 194.60899999999998, 235.395)), ('A', 664, u'ILE', 0.5701153895387909, (232.181, 198.901, 225.84)), ('A', 671, u'CYS', 0.6135312524772188, (233.201, 193.71699999999998, 227.32200000000003)), ('A', 699, u'LEU', 0.5667498388356611, (229.13, 191.73499999999999, 238.411)), ('A', 713, u'ALA', 0.5328703576009682, (225.072, 193.98600000000002, 263.775)), ('A', 731, u'MET', 0.4978398773133118, (211.24899999999997, 217.92700000000002, 224.237)), ('A', 742, u'ILE', 0.4983174066353784, (207.015, 219.15800000000002, 199.571)), ('A', 781, u'VAL', 0.44295108722503673, (206.35700000000003, 218.71299999999997, 237.304)), ('A', 797, u'PHE', 0.5009964778832513, (218.627, 227.05800000000002, 259.59299999999996)), ('A', 805, u'ILE', 0.5104151467869699, (220.664, 225.784, 246.004)), ('A', 819, u'GLU', 0.4948929458120343, (221.29899999999998, 225.61499999999998, 238.45600000000002)), ('A', 826, u'VAL', 0.5269217692645674, (223.317, 220.759, 228.26399999999998)), ('A', 861, u'LEU', 0.5433405293496439, (207.90800000000002, 226.87800000000001, 218.736)), ('A', 864, u'LEU', 0.5781231361459074, (204.82700000000003, 228.655, 227.42000000000002)), ('A', 869, u'MET', 0.5174003919546191, (209.24499999999998, 231.121, 235.33700000000002)), ('A', 870, u'ILE', 0.473686044701976, (210.542, 227.64399999999998, 235.977)), ('A', 905, u'ARG', 0.47230932618091875, (212.36100000000002, 213.562, 259.46999999999997)), ('A', 930, u'ALA', 0.48747121522457143, (227.90800000000002, 216.89600000000002, 250.621)), ('A', 965, u'GLN', 0.48770239745296523, (215.785, 213.623, 202.36)), ('A', 990, u'GLU', 0.5042696871197356, (203.71699999999998, 215.575, 186.295)), ('A', 1031, u'GLU', 0.47729429342615554, (206.575, 212.341, 247.201)), ('A', 1039, u'ARG', 0.485618639636103, (209.5, 203.768, 249.36800000000002)), ('A', 1040, u'VAL', 0.4834439768882902, (212.84, 202.01, 249.065)), ('A', 1062, u'PHE', 0.5128639784859131, (216.653, 216.319, 242.22)), ('A', 1064, u'HIS', 0.45790967551167105, (218.218, 213.687, 247.512)), ('A', 1066, u'THR', 0.4958100568194159, (219.577, 210.42600000000002, 252.789)), ('A', 1072, u'GLU', 0.4693472158377826, (228.85700000000003, 198.972, 263.046)), ('A', 1087, u'ALA', 0.4773513183009744, (208.761, 186.636, 278.82599999999996)), ('A', 1097, u'SER', 0.4949825571146194, (224.665, 191.85000000000002, 275.041)), ('A', 1121, u'PHE', 0.6208855421020025, (206.228, 194.348, 277.802)), ('A', 1137, u'VAL', 0.6863748733234041, (214.553, 193.537, 284.47799999999995)), ('B', 37, u'TYR', 0.5468351755234981, (196.055, 167.791, 192.545)), ('B', 51, u'THR', 0.5342474848440204, (196.49800000000002, 178.12, 196.43800000000002)), ('B', 54, u'LEU', 0.3975840782479939, (189.755, 174.478, 189.96800000000002)), ('B', 62, u'VAL', 0.44336061252430425, (179.32700000000003, 162.959, 192.197)), ('B', 86, u'PHE', 0.48703439955008315, (182.025, 169.24299999999997, 180.798)), ('B', 92, u'PHE', 0.4533466754627152, (186.526, 161.634, 186.691)), ('B', 104, u'TRP', 0.5104551178655304, (186.948, 159.389, 176.617)), ('B', 122, u'ASN', 0.5372643951970231, (194.011, 149.681, 175.35700000000003)), ('B', 166, u'CYS', 0.2822919283558069, (194.618, 165.341, 163.364)), ('B', 187, u'LYS', 0.7731635127725252, (191.04, 146.068, 192.26999999999998)), ('B', 213, u'VAL', 0.7376599282755568, (183.167, 146.70999999999998, 195.22299999999998)), ('B', 216, u'LEU', 0.6112797152183873, (184.64399999999998, 154.63899999999998, 196.08200000000002)), ('B', 217, u'PRO', 0.7064650022744773, (187.147, 154.166, 198.98100000000002)), ('B', 223, u'LEU', 0.5234287391976342, (196.98200000000003, 163.787, 191.586)), ('B', 233, u'ILE', 0.40674206956070313, (189.777, 172.848, 170.883)), ('B', 240, u'THR', 0.4928306987310256, (183.012, 157.80200000000002, 178.06)), ('B', 263, u'ALA', 0.4840950473798916, (183.024, 148.834, 186.18800000000002)), ('B', 279, u'TYR', 0.5733899981076814, (203.47899999999998, 169.168, 202.20899999999997)), ('B', 301, u'CYS', 0.5722400789473494, (192.82100000000003, 178.618, 206.446)), ('B', 313, u'TYR', 0.5258470594197991, (188.38600000000002, 184.2, 215.86100000000002)), ('B', 382, u'VAL', 0.7105743671823478, (186.92200000000003, 205.383, 177.323)), ('B', 406, u'GLU', 0.6211884983175935, (199.05200000000002, 216.786, 160.448)), ('B', 425, u'LEU', 0.6187106613506606, (191.994, 219.678, 172.042)), ('B', 451, u'TYR', 0.729606377486789, (190.965, 223.847, 152.101)), ('B', 468, u'ILE', 0.6912890507375152, (187.63899999999998, 232.999, 162.20999999999998)), ('B', 499, u'PRO', 0.7977417407729678, (195.593, 212.577, 143.696)), ('B', 515, u'PHE', 0.613557199914862, (182.018, 212.91, 174.85500000000002)), ('B', 524, u'VAL', 0.5670807981550219, (172.89200000000002, 210.146, 174.167)), ('B', 525, u'CYS', 0.6634025223330798, (172.689, 206.446, 175.171)), ('B', 541, u'PHE', 0.671767666753663, (172.036, 197.818, 188.818)), ('B', 542, u'ASN', 0.6519543948417049, (172.997, 199.96800000000002, 185.82700000000003)), ('B', 544, u'ASN', 0.6722700431332828, (172.79899999999998, 205.29, 182.41899999999998)), ('B', 567, u'ARG', 0.5707650578973628, (176.73, 211.501, 196.637)), ('B', 590, u'CYS', 0.642378286703297, (173.11599999999999, 194.768, 200.636)), ('B', 593, u'GLY', 0.6634029978927798, (178.548, 191.74699999999999, 208.73999999999998)), ('B', 597, u'VAL', 0.5292193277532088, (184.069, 181.369, 214.92000000000002)), ('B', 649, u'CYS', 0.6370585235057316, (173.407, 186.476, 216.345)), ('B', 662, u'CYS', 0.6029439211109943, (183.848, 183.76899999999998, 231.79299999999998)), ('B', 664, u'ILE', 0.5494685122896552, (185.599, 182.523, 225.839)), ('B', 670, u'ILE', 0.579708988084651, (177.894, 186.96200000000002, 227.17)), ('B', 689, u'SER', 0.740645348540048, (177.496, 164.706, 225.936)), ('B', 703, u'ASN', 0.7089522921172778, (178.27899999999997, 188.123, 250.207)), ('B', 715, u'PRO', 0.5538232762370551, (190.559, 187.55800000000002, 263.47299999999996)), ('B', 746, u'SER', 0.578868690515484, (222.105, 192.317, 193.497)), ('B', 749, u'CYS', 0.5189103922500201, (218.81, 197.21399999999997, 192.35700000000003)), ('B', 763, u'LEU', 0.3849257518466317, (215.813, 201.648, 210.046)), ('B', 767, u'LEU', 0.42773730405173327, (216.51, 198.76, 215.696)), ('B', 774, u'GLN', 0.45347569893966055, (216.972, 195.666, 226.23)), ('B', 777, u'ASN', 0.4081000075157756, (215.975, 197.01899999999998, 231.10999999999999)), ('B', 781, u'VAL', 0.34539279056697436, (215.666, 194.984, 237.30800000000002)), ('B', 789, u'TYR', 0.5436887021898548, (226.162, 187.94299999999998, 248.71399999999997)), ('B', 856, u'ASN', 0.5546607261624739, (217.315, 187.069, 204.32200000000003)), ('B', 871, u'ALA', 0.562986446346714, (221.225, 183.937, 238.35800000000003)), ('B', 878, u'LEU', 0.44571439515905753, (218.05800000000002, 186.431, 247.89800000000002)), ('B', 888, u'PHE', 0.49071697723029495, (221.608, 195.43, 252.35800000000003)), ('B', 898, u'PHE', 0.4981135215214879, (216.02, 185.258, 260.72999999999996)), ('B', 902, u'MET', 0.46154375611273235, (210.40200000000002, 188.227, 260.828)), ('B', 916, u'LEU', 0.5460324648963774, (205.57, 185.33200000000002, 265.827)), ('B', 955, u'ASN', 0.561142100845219, (208.111, 188.664, 218.089)), ('B', 958, u'ALA', 0.5633527097108, (206.661, 189.555, 213.284)), ('B', 979, u'ASP', 0.5258587712341299, (214.38400000000001, 186.16299999999998, 187.38600000000002)), ('B', 996, u'LEU', 0.4852919205855119, (209.788, 195.311, 194.484)), ('B', 1003, u'SER', 0.47258299874971466, (207.503, 196.07899999999998, 204.777)), ('B', 1021, u'SER', 0.43931437184238215, (206.948, 196.35500000000002, 232.345)), ('B', 1022, u'ALA', 0.3725224003008876, (210.671, 196.418, 233.146)), ('B', 1033, u'VAL', 0.45793004390638087, (212.417, 192.51299999999998, 247.88100000000003)), ('B', 1041, u'ASP', 0.516803292432112, (198.038, 194.847, 246.601)), ('B', 1054, u'GLN', 0.5581918429685, (213.563, 184.208, 240.69299999999998)), ('B', 1087, u'ALA', 0.5393498160877578, (186.67299999999997, 208.947, 278.82)), ('B', 1090, u'PRO', 0.5500762795909737, (192.931, 202.618, 273.818)), ('B', 1096, u'VAL', 0.5607672735327232, (185.937, 194.231, 272.98599999999993)), ('B', 1123, u'SER', 0.4912201279508518, (190.75, 212.624, 276.879)), ('B', 1304, u'NAG', 0.7179499123380133, (178.129, 206.58700000000002, 160.69)), ('C', 40, u'ASP', 0.5021987210480868, (178.446, 221.14299999999997, 189.99)), ('C', 53, u'ASP', 0.4926990543423583, (186.207, 228.026, 191.42700000000002)), ('C', 54, u'LEU', 0.38399102212561775, (185.67, 231.472, 189.95800000000003)), ('C', 62, u'VAL', 0.4193641378724385, (180.90800000000002, 246.262, 192.184)), ('C', 83, u'VAL', 0.5304062876886085, (181.52200000000002, 248.765, 177.107)), ('C', 86, u'PHE', 0.37550108054809284, (185.004, 240.781, 180.787)), ('C', 92, u'PHE', 0.5119995268517311, (176.162, 240.689, 186.678)), ('C', 106, u'PHE', 0.5192358649766734, (179.85800000000003, 239.447, 174.374)), ('C', 131, u'CYS', 0.4824927449865458, (176.155, 235.833, 164.24899999999997)), ('C', 166, u'CYS', 0.3173110895250674, (175.333, 231.824, 163.35200000000003)), ('C', 217, u'PRO', 0.6715772256794919, (169.38200000000003, 243.88700000000003, 198.966)), ('C', 223, u'LEU', 0.5357750932970624, (172.798, 230.55800000000002, 191.57399999999998)), ('C', 233, u'ILE', 0.47968929929017257, (184.252, 232.26399999999998, 170.873)), ('C', 235, u'ILE', 0.43156940206013816, (185.23499999999999, 237.062, 174.94)), ('C', 240, u'THR', 0.48014573890207074, (174.60299999999998, 245.647, 178.046)), ('C', 241, u'LEU', 0.493262897513672, (171.39600000000002, 246.39100000000002, 176.146)), ('C', 263, u'ALA', 0.4451089886769892, (166.82800000000003, 250.122, 186.17)), ('C', 265, u'TYR', 0.433984314953335, (172.82000000000002, 247.226, 187.227)), ('C', 270, u'LEU', 0.42368448099514794, (185.15, 236.541, 189.506)), ('C', 273, u'ARG', 0.4206762263732088, (188.899, 231.631, 195.494)), ('C', 279, u'TYR', 0.6013071842896943, (174.207, 222.242, 202.19899999999998)), ('C', 293, u'LEU', 0.5210014905376519, (187.82600000000002, 237.146, 203.39800000000002)), ('C', 309, u'GLU', 0.7175729030290845, (185.85000000000002, 227.067, 219.60299999999998)), ('C', 337, u'PRO', 0.7159746943610625, (225.916, 227.811, 162.994)), ('C', 342, u'PHE', 0.723568243502844, (221.495, 220.953, 158.503)), ('C', 348, u'ALA', 0.6797958891623977, (229.48200000000003, 211.554, 156.467)), ('C', 382, u'VAL', 0.730850661123829, (213.854, 218.47, 177.324)), ('C', 398, u'ASP', 0.6581841941474675, (226.593, 214.423, 165.124)), ('C', 415, u'THR', 0.7113123552529502, (220.32100000000003, 197.782, 169.82700000000003)), ('C', 423, u'TYR', 0.6608806769578816, (226.655, 204.85100000000003, 166.077)), ('C', 425, u'LEU', 0.5956453742815898, (223.7, 206.929, 172.047)), ('C', 429, u'PHE', 0.646411440766044, (221.108, 210.65800000000002, 176.36200000000002)), ('C', 435, u'ALA', 0.5897379277585143, (216.226, 213.455, 160.48800000000003)), ('C', 524, u'VAL', 0.5558629663109383, (224.995, 228.23899999999998, 174.16899999999998)), ('C', 539, u'VAL', 0.6893007809037681, (212.184, 238.765, 192.707)), ('C', 540, u'ASN', 0.6829264955535551, (211.346, 235.97, 190.29399999999998)), ('C', 542, u'ASN', 0.5953543721813415, (216.126, 233.238, 185.82500000000002)), ('C', 571, u'ASP', 0.3746719777099118, (220.122, 220.632, 197.172)), ('C', 574, u'ASP', 0.5830550428443221, (222.701, 228.687, 197.724)), ('C', 590, u'CYS', 0.6076134666088912, (211.559, 235.738, 200.63299999999998)), ('C', 597, u'VAL', 0.44565576841379634, (194.474, 232.954, 214.91299999999998)), ('C', 605, u'SER', 0.7552348886763164, (182.54399999999998, 236.98700000000002, 219.80200000000002)), ('C', 647, u'ALA', 0.5675064413733271, (206.512, 234.026, 220.14399999999998)), ('C', 649, u'CYS', 0.6658789584709391, (204.22899999999998, 239.634, 216.339)), ('C', 671, u'CYS', 0.5549338133631044, (198.686, 234.529, 227.312)), ('C', 711, u'SER', 0.5037802241207758, (208.26299999999998, 229.85700000000003, 266.48599999999993)), ('C', 713, u'ALA', 0.5407056195280789, (202.518, 227.366, 263.768)), ('C', 722, u'VAL', 0.5932469789442834, (186.191, 216.04899999999998, 248.834)), ('C', 775, u'ASP', 0.5387374969936619, (188.595, 194.63, 228.21399999999997)), ('C', 805, u'ILE', 0.4927004639695302, (177.184, 207.64399999999998, 246.003)), ('C', 876, u'ALA', 0.4703943324980777, (180.62, 196.142, 245.782)), ('C', 884, u'SER', 0.5586042695514056, (184.476, 196.651, 256.464)), ('C', 909, u'ILE', 0.49399900433488125, (197.285, 210.967, 259.569)), ('C', 913, u'GLN', 0.5097156773926605, (191.277, 209.409, 267.717)), ('C', 927, u'PHE', 0.5332503774599286, (181.576, 215.512, 254.836)), ('C', 942, u'ALA', 0.5508751755291671, (180.18800000000002, 219.79399999999998, 231.415)), ('C', 945, u'LEU', 0.5475681265857096, (184.684, 215.373, 232.485)), ('C', 954, u'GLN', 0.5675656892400133, (189.935, 211.915, 219.12)), ('C', 979, u'ASP', 0.5713562701849011, (183.476, 204.29899999999998, 187.38000000000002)), ('C', 1004, u'LEU', 0.46218384732080553, (194.667, 202.129, 206.708)), ('C', 1018, u'ILE', 0.44308780247186386, (195.039, 204.606, 227.511)), ('C', 1022, u'ALA', 0.3755785243493057, (194.202, 202.394, 233.14399999999998)), ('C', 1033, u'VAL', 0.416699014265814, (189.94299999999998, 202.83700000000002, 247.87800000000001)), ('C', 1037, u'SER', 0.47560621534470027, (197.58200000000002, 206.101, 251.24599999999998)), ('C', 1067, u'TYR', 0.5083553249524646, (191.813, 216.102, 256.077)), ('C', 1070, u'ALA', 0.5544603914655855, (191.98100000000002, 225.177, 258.54900000000004)), ('C', 1096, u'VAL', 0.5348504312360197, (204.665, 224.915, 272.98299999999995)), ('C', 1129, u'VAL', 0.5336224294809642, (220.92200000000003, 220.476, 273.31)), ('C', 1132, u'ILE', 0.5919163622094341, (216.905, 223.931, 275.42499999999995))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22083/6x79/Model_validation_1/validation_cootdata/molprobity_probe6x79_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

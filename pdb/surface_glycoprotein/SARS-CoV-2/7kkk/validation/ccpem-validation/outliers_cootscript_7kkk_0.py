
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
data['smoc'] = []
data['jpred'] = []
data['rota'] = [('A', ' 331 ', 'ASN', 0.28316914122254033, (211.08100000000005, 254.738, 240.428)), ('A', ' 603 ', 'ASN', 0.11058428814502595, (248.55, 226.707, 196.691)), ('C', ' 331 ', 'ASN', 0.29156834583446384, (179.01000000000005, 190.801, 240.431)), ('C', ' 603 ', 'ASN', 0.11007310414728536, (184.55100000000004, 237.253, 196.694)), ('E', ' 331 ', 'ASN', 0.29643679822596686, (250.43100000000007, 194.987, 240.423)), ('E', ' 603 ', 'ASN', 0.11136896328990073, (207.411, 176.56000000000003, 196.694))]
data['clusters'] = [('A', '1303', 1, 'Bond length:C5:O5\nBond length:C3:C4', (251.314, 222.626, 196.011)), ('A', '600', 1, 'Bond angle:N:CA:C\nBond angle:C', (242.07899999999998, 231.73499999999999, 195.74099999999999)), ('A', '601', 1, 'Bond angle:N:CA', (243.41299999999998, 228.376, 196.60899999999998)), ('A', '603', 1, 'Rotamer', (248.55, 226.707, 196.691)), ('A', '218', 2, 'cablam CA Geom Outlier', (261.3, 230.0, 213.8)), ('A', '220', 2, 'cablam CA Geom Outlier', (257.1, 224.2, 214.6)), ('A', '32', 2, 'Bond angle:C', (256.61, 232.27899999999997, 214.99200000000002)), ('A', '33', 2, 'Bond angle:N:CA', (254.51899999999998, 229.132, 215.712)), ('A', '1072', 3, 'Dihedral angle:CB:CG:CD:OE1', (231.125, 230.835, 156.258)), ('A', '1074', 3, 'Bond angle:CA:CB:CG', (228.24699999999999, 236.085, 152.647)), ('A', '1307', 3, 'Bond angle:C8:C7:O7\nBond length:C5:O5\nBond length:C3:C4', (228.319, 239.503, 156.694)), ('A', '138', 4, 'side-chain clash\nbackbone clash', (248.573, 217.735, 245.286)), ('A', '200', 4, 'Bond length:CB:CG', (248.097, 220.77599999999998, 238.977)), ('A', '231', 4, 'cablam Outlier', (250.2, 220.7, 244.6)), ('A', '914', 5, 'Bond length:CB:CG', (229.365, 213.137, 148.51)), ('A', '916', 5, 'Bond length:CG:CD2', (232.084, 212.88200000000003, 153.117)), ('A', '918', 5, 'Dihedral angle:CB:CG:CD:OE1', (235.297, 213.75, 148.72899999999998)), ('A', '1146', 6, 'Bond angle:C', (218.5, 219.67899999999997, 119.67299999999999)), ('A', '1147', 6, 'Bond angle:N:CA', (222.04399999999998, 217.967, 119.60199999999999)), ('A', '994', 7, 'Bond angle:C', (218.283, 206.112, 226.69899999999998)), ('A', '995', 7, 'Bond angle:N:CA', (219.36200000000002, 209.607, 225.89200000000002)), ('A', '661', 8, 'Bond angle:N:CA:C\ncablam Outlier', (233.816, 235.88100000000003, 182.953)), ('A', '662', 8, 'cablam Outlier', (233.4, 234.5, 186.6)), ('A', '1310', 9, 'Bond angle:C8:C7:N2\nBond length:C5:O5\nBond length:C3:C4', (208.974, 257.42699999999996, 236.58700000000002)), ('A', '331', 9, 'Rotamer\nBond angle:CA:CB:CG', (211.08100000000002, 254.738, 240.42800000000003)), ('A', '986', 10, 'Bond angle:CA:C', (220.376, 200.20499999999998, 236.001)), ('A', '987', 10, 'Bond angle:N', (217.777, 202.666, 237.52700000000002)), ('A', '266', 11, 'Bond length:CB:CG', (261.758, 235.43800000000002, 226.95700000000002)), ('A', '64', 11, 'C-beta\nBond angle:C:CA:CB\nBond angle:CA:CB:CG', (262.774, 240.22299999999998, 226.08800000000002)), ('A', '1109', 12, 'cablam Outlier', (227.6, 223.2, 152.9)), ('A', '1111', 12, 'cablam Outlier', (228.6, 223.4, 146.8)), ('A', '666', 13, 'cablam Outlier', (229.8, 236.4, 195.1)), ('A', '667', 13, 'cablam Outlier', (226.2, 237.3, 194.1)), ('A', '811', 14, 'side-chain clash', (245.979, 201.477, 180.397)), ('A', '820', 14, 'side-chain clash\nBond angle:CA:CB:CG', (242.41, 203.95800000000003, 182.26)), ('A', '568', 15, 'side-chain clash\nbackbone clash', (192.11, 241.48, 245.303)), ('A', '569', 15, 'side-chain clash\nbackbone clash', (192.11, 241.48, 245.303)), ('B', '15', 1, 'cablam Outlier', (174.7, 197.7, 291.7)), ('B', '85', 1, 'cablam Outlier', (174.1, 200.5, 289.2)), ('B', '64', 2, 'side-chain clash', (175.952, 202.963, 279.736)), ('B', '68', 2, 'side-chain clash', (175.952, 202.963, 279.736)), ('C', '218', 1, 'cablam CA Geom Outlier', (175.3, 246.6, 213.9)), ('C', '220', 1, 'cablam CA Geom Outlier', (182.4, 245.9, 214.6)), ('C', '32', 1, 'Bond angle:C', (175.728, 241.455, 214.99)), ('C', '33', 1, 'Bond angle:N:CA', (179.49800000000002, 241.21399999999997, 215.7)), ('C', '59', 1, 'Bond angle:CA:CB:CG', (174.823, 236.068, 216.17899999999997)), ('C', '1303', 2, 'Bond length:C5:O5\nBond length:C3:C4', (186.70899999999997, 241.685, 196.003)), ('C', '600', 2, 'Bond angle:C\nBond angle:N:CA:C', (183.431, 229.141, 195.731)), ('C', '601', 2, 'Bond angle:N:CA', (185.67399999999998, 231.969, 196.621)), ('C', '603', 2, 'Rotamer', (184.55100000000004, 237.253, 196.694)), ('C', '1072', 3, 'Dihedral angle:CB:CG:CD:OE1', (189.683, 220.098, 156.256)), ('C', '1074', 3, 'Bond angle:CA:CB:CG', (186.578, 214.983, 152.64499999999998)), ('C', '1307', 3, 'Bond angle:C8:C7:O7\nBond length:C5:O5\nBond length:C3:C4', (183.585, 213.335, 156.692)), ('C', '266', 4, 'Bond length:CB:CG', (170.36200000000002, 244.371, 226.953)), ('C', '64', 4, 'C-beta\nBond angle:C:CA:CB\nBond angle:CA:CB:CG', (165.728, 242.817, 226.066)), ('C', '92', 4, 'Bond angle:CA:CB:CG', (175.809, 244.334, 228.41899999999998)), ('C', '914', 5, 'Bond length:CB:CG', (205.894, 227.423, 148.512)), ('C', '916', 5, 'Bond length:CG:CD2', (204.754, 229.909, 153.117)), ('C', '918', 5, 'Dihedral angle:CB:CG:CD:OE1', (202.395, 232.253, 148.73)), ('C', '994', 6, 'Bond angle:C', (217.52, 221.296, 226.694)), ('C', '995', 6, 'Bond angle:N:CA', (213.948, 220.506, 225.88200000000003)), ('C', '1146', 7, 'Bond angle:C', (205.64499999999998, 214.74399999999997, 119.67099999999999)), ('C', '1147', 7, 'Bond angle:N:CA', (205.359, 218.67, 119.601)), ('C', '666', 8, 'cablam Outlier', (185.5, 216.1, 195.1)), ('C', '667', 8, 'cablam Outlier', (186.5, 212.6, 194.1)), ('C', '1310', 9, 'Bond angle:C8:C7:N2\nBond length:C5:O5\nBond length:C3:C4', (177.721, 187.637, 236.59)), ('C', '331', 9, 'Rotamer\nBond angle:CA:CB:CG', (179.01, 190.80100000000002, 240.431)), ('C', '661', 10, 'Dihedral angle:CA:C\nBond angle:N:CA:C\ncablam Outlier', (183.871, 219.813, 182.936)), ('C', '662', 10, 'Dihedral angle:N:CA\ncablam Outlier', (185.324, 220.18800000000002, 186.534)), ('C', '200', 11, 'Bond length:CB:CG', (190.015, 239.843, 238.92700000000002)), ('C', '231', 11, 'cablam Outlier', (189.0, 241.6, 244.6)), ('C', '1109', 12, 'cablam Outlier', (198.1, 220.9, 152.9)), ('C', '1111', 12, 'cablam Outlier', (197.4, 221.6, 146.8)), ('C', '811', 13, 'side-chain clash', (207.713, 247.688, 180.436)), ('C', '820', 13, 'side-chain clash\nBond angle:CA:CB:CG', (207.316, 243.30200000000002, 182.256)), ('C', '568', 14, 'side-chain clash\nbackbone clash', (210.45, 218.334, 160.4)), ('C', '569', 14, 'side-chain clash\nbackbone clash', (210.45, 218.334, 160.4)), ('C', '986', 15, 'Bond angle:CA:C', (221.592, 226.16899999999998, 235.983)), ('C', '987', 15, 'Bond angle:N', (220.748, 222.665, 237.447)), ('C', '108', 16, 'cablam Outlier', (175.2, 236.1, 244.9)), ('C', '111', 16, 'side-chain clash\ncablam Outlier', (172.792, 238.607, 250.781)), ('D', '15', 1, 'cablam Outlier', (246.6, 187.8, 291.7)), ('D', '85', 1, 'cablam Outlier', (244.4, 185.9, 289.2)), ('D', '64', 2, 'side-chain clash', (241.497, 186.313, 279.734)), ('D', '68', 2, 'side-chain clash', (241.497, 186.313, 279.734)), ('E', '218', 1, 'cablam CA Geom Outlier', (204.1, 163.9, 213.8)), ('E', '220', 1, 'cablam CA Geom Outlier', (201.0, 170.4, 214.5)), ('E', '32', 1, 'Bond angle:C', (208.227, 166.86700000000002, 215.153)), ('E', '33', 1, 'Bond angle:N:CA', (206.491, 170.23499999999999, 215.767)), ('E', '34', 1, 'cablam CA Geom Outlier', (205.0, 169.1, 219.1)), ('E', '59', 1, 'Bond angle:CA:CB:CG', (213.417, 168.685, 216.252)), ('E', '661', 2, 'side-chain clash\nDihedral angle:CA:C\nBond angle:N:CA:C\ncablam Outlier', (222.85600000000002, 184.685, 182.937)), ('E', '662', 2, 'Dihedral angle:N:CA\ncablam Outlier', (221.804, 185.756, 186.535)), ('E', '697', 2, 'side-chain clash', (224.936, 186.809, 185.179)), ('E', '1072', 3, 'Dihedral angle:CB:CG:CD:OE1', (219.70399999999998, 189.578, 156.256)), ('E', '1074', 3, 'Bond angle:CA:CB:CG', (225.689, 189.446, 152.646)), ('E', '1307', 3, 'Bond angle:C8:C7:O7\nBond length:C5:O5\nBond length:C3:C4', (228.61499999999998, 187.676, 156.692)), ('E', '200', 4, 'Bond length:CB:CG', (202.526, 179.901, 238.989)), ('E', '230', 4, 'backbone clash', (199.883, 180.978, 245.369)), ('E', '231', 4, 'cablam Outlier', (201.4, 178.1, 244.6)), ('E', '914', 5, 'Bond length:CB:CG', (205.254, 199.95200000000003, 148.512)), ('E', '916', 5, 'Bond length:CG:CD2', (203.67299999999997, 197.721, 153.118)), ('E', '918', 5, 'Dihedral angle:CB:CG:CD:OE1', (202.82100000000003, 194.504, 148.732)), ('E', '994', 6, 'Bond angle:C', (204.708, 213.05800000000002, 226.70299999999997)), ('E', '995', 6, 'Bond angle:N:CA', (207.192, 210.375, 225.889)), ('E', '1146', 7, 'Bond angle:C', (216.36100000000002, 206.083, 119.67199999999998)), ('E', '1147', 7, 'Bond angle:N:CA', (213.106, 203.871, 119.59700000000001)), ('E', '1303', 8, 'Bond length:C5:O5\nBond length:C3:C4', (202.494, 176.21399999999997, 196.001)), ('E', '603', 8, 'Rotamer', (207.411, 176.56000000000003, 196.694)), ('E', '666', 9, 'cablam Outlier', (225.2, 188.0, 195.1)), ('E', '667', 9, 'cablam Outlier', (227.8, 190.6, 194.1)), ('E', '1310', 10, 'Bond angle:C8:C7:N2\nBond length:C5:O5\nBond length:C3:C4', (253.815, 195.465, 236.57899999999998)), ('E', '331', 10, 'Rotamer\nBond angle:CA:CB:CG', (250.431, 194.98700000000002, 240.423)), ('E', '266', 11, 'Bond length:CB:CG', (208.353, 160.74699999999999, 226.93)), ('E', '64', 11, 'C-beta\nBond angle:C:CA:CB\nBond angle:CA:CB:CG', (211.999, 157.47899999999998, 226.007)), ('E', '1109', 12, 'cablam Outlier', (214.8, 196.4, 152.9)), ('E', '1111', 12, 'cablam Outlier', (214.6, 195.5, 146.8)), ('E', '811', 13, 'side-chain clash', (186.679, 191.491, 180.313)), ('E', '820', 13, 'side-chain clash\nBond angle:CA:CB:CG', (190.829, 193.185, 182.231)), ('E', '568', 14, 'side-chain clash\nbackbone clash', (237.844, 207.166, 215.779)), ('E', '569', 14, 'side-chain clash\nbackbone clash', (237.844, 207.166, 215.779)), ('E', '204', 15, 'side-chain clash', (198.01, 177.931, 227.883)), ('E', '225', 15, 'side-chain clash', (198.01, 177.931, 227.883)), ('E', '986', 16, 'Bond angle:CA:C', (198.553, 214.201, 236.002)), ('E', '987', 16, 'Bond angle:N', (201.983, 215.22299999999998, 237.52800000000002)), ('E', '111', 17, 'side-chain clash\ncablam Outlier', (203.742, 204.351, 163.379)), ('E', '905', 17, 'Bond length:CG:CD', (204.681, 205.101, 159.24699999999999)), ('F', '15', 1, 'cablam Outlier', (219.2, 255.0, 291.7)), ('F', '85', 1, 'cablam Outlier', (222.0, 254.1, 289.2)), ('F', '64', 2, 'side-chain clash', (223.009, 251.501, 279.308)), ('F', '68', 2, 'side-chain clash', (223.009, 251.501, 279.308)), ('G', '1', 1, 'Bond angle:C2:N2:C7\nBond angle:C8:C7:N2\nBond length:C3:C4\nBond length:C5:O5\nBond length:C4:C5\nBond length:C4:O4', (242.38200000000003, 230.912, 244.871)), ('G', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4\nBond length:C2:N2', (242.012, 237.797, 246.535)), ('H', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5', (238.974, 225.344, 152.77299999999997)), ('H', '2', 1, 'Bond angle:C8:C7:N2\nBond length:C3:C4\nBond length:C5:O5\nBond length:C2:N2', (244.148, 222.601, 157.52700000000002)), ('I', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5\nBond length:C4:O4', (247.472, 203.91899999999998, 161.911)), ('I', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4', (251.484, 205.942, 167.22299999999998)), ('J', '1', 1, 'Bond length:C5:O5', (232.797, 235.915, 141.755)), ('J', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4', (233.389, 230.98600000000002, 136.01399999999998)), ('K', '1', 1, 'Bond angle:C2:N2:C7\nBond angle:C8:C7:N2\nBond angle:N2:C7:O7\nBond length:C3:C4\nBond length:C5:O5\nBond length:C4:C5\nBond length:C4:O4', (183.667, 230.89800000000002, 243.196)), ('K', '2', 1, 'Bond length:C3:C4\nBond length:C5:O5\nBond length:C2:N2', (178.31, 226.005, 246.52)), ('L', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5', (190.536, 229.605, 152.77399999999997)), ('L', '2', 1, 'Bond angle:C8:C7:N2\nBond length:C3:C4\nBond length:C5:O5\nBond length:C2:N2', (190.227, 235.48000000000002, 157.47)), ('M', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5\nBond length:C4:O4', (204.82500000000002, 247.70999999999998, 161.901)), ('M', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4', (201.068, 250.191, 167.19899999999998)), ('N', '1', 1, 'Bond length:C5:O5\nBond length:C4:C5\nBond length:C3:C4', (184.44899999999998, 219.011, 141.754)), ('N', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4', (188.41899999999998, 221.98700000000002, 136.01299999999998)), ('O', '1', 1, 'Bond angle:C2:N2:C7\nBond angle:C8:C7:N2\nBond length:C5:O5\nBond length:C3:C4\nBond length:C4:C5', (213.66, 178.371, 242.38000000000002)), ('O', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4\nBond length:C2:N2', (220.131, 176.955, 246.48100000000002)), ('P', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5', (211.012, 185.56, 152.772)), ('P', '2', 1, 'Bond angle:C8:C7:N2\nBond length:C5:O5\nBond length:C3:C4\nBond length:C2:N2', (206.065, 182.37, 157.48100000000002)), ('Q', '1', 1, 'Bond length:C3:C4\nBond length:C5:O5', (188.27399999999997, 188.76299999999998, 161.9)), ('Q', '2', 1, 'Bond angle:C8:C7:N2\nBond length:C3:C4\nBond length:C5:O5\nBond length:C2:N2', (188.117, 184.568, 167.64499999999998)), ('R', '1', 1, 'Bond length:C5:O5\nBond length:C3:C4', (223.221, 185.61499999999998, 141.786)), ('R', '2', 1, 'Bond length:C5:O5\nBond length:C3:C4', (218.71899999999997, 187.728, 136.025))]
data['probe'] = [(' F  62  ASP  N  ', ' F  62  ASP  OD1', -0.541, (225.384, 255.435, 272.334)), (' B  62  ASP  N  ', ' B  62  ASP  OD1', -0.535, (171.495, 202.76, 272.439)), (' D  62  ASP  N  ', ' D  62  ASP  OD1', -0.522, (243.887, 182.219, 272.345)), (' C 568  ASP  CG ', ' C 569  ILE  H  ', -0.506, (195.659, 195.483, 215.172)), (' A 568  ASP  CG ', ' A 569  ILE  H  ', -0.505, (206.871, 237.847, 215.185)), (' E 111  ASP  N  ', ' E 111  ASP  OD1', -0.501, (211.981, 165.701, 250.99)), (' A 111  ASP  N  ', ' A 111  ASP  OD1', -0.498, (255.587, 236.049, 250.947)), (' E 905  ARG  HD3', ' E1049  LEU  O  ', -0.495, (203.742, 204.351, 163.379)), (' E 811  LYS  NZ ', ' E 820  ASP  OD2', -0.494, (186.679, 191.491, 180.313)), (' D  64  VAL  HB ', ' D  68  PHE  CD1', -0.492, (241.497, 186.313, 279.734)), (' F  64  VAL  HB ', ' F  68  PHE  CD1', -0.492, (223.009, 251.501, 279.308)), (' E 568  ASP  CG ', ' E 569  ILE  H  ', -0.49, (238.203, 206.613, 215.388)), (' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.489, (223.331, 214.325, 175.91)), (' B  64  VAL  HB ', ' B  68  PHE  CD1', -0.488, (175.952, 202.963, 279.736)), (' C 568  ASP  CG ', ' C 569  ILE  N  ', -0.486, (195.526, 195.925, 215.602)), (' C1028  LYS  NZ ', ' C1042  PHE  O  ', -0.486, (207.581, 221.615, 175.976)), (' A 905  ARG  HD3', ' A1049  LEU  O  ', -0.486, (226.304, 209.151, 163.174)), (' A 908  GLY  O  ', ' A1038  LYS  NZ ', -0.486, (219.475, 214.041, 160.126)), (' C 905  ARG  HD3', ' C1049  LEU  O  ', -0.486, (210.502, 226.644, 163.43)), (' E 138  ASP  N  ', ' E 138  ASP  OD1', -0.483, (209.216, 154.664, 246.323)), (' E 908  GLY  O  ', ' E1038  LYS  NZ ', -0.481, (210.95, 208.136, 160.051)), (' C 908  GLY  O  ', ' C1038  LYS  NZ ', -0.48, (210.45, 218.334, 160.4)), (' C 111  ASP  N  ', ' C 111  ASP  OD1', -0.479, (172.792, 238.607, 250.781)), (' E1028  LYS  NZ ', ' E1042  PHE  O  ', -0.478, (209.345, 204.498, 175.94)), (' E 568  ASP  CG ', ' E 569  ILE  N  ', -0.476, (237.844, 207.166, 215.779)), (' A 568  ASP  CG ', ' A 569  ILE  N  ', -0.465, (206.916, 237.609, 215.671)), (' A 357  ARG  NH2', ' C 230  PRO  O  ', -0.461, (192.11, 241.48, 245.303)), (' A 138  ASP  N  ', ' A 138  ASP  OD1', -0.458, (266.56, 239.452, 246.264)), (' C 357  ARG  NH2', ' E 230  PRO  O  ', -0.453, (199.883, 180.978, 245.369)), (' C 811  LYS  NZ ', ' C 820  ASP  OD2', -0.45, (207.713, 247.688, 180.436)), (' A 230  PRO  O  ', ' E 357  ARG  NH2', -0.448, (248.573, 217.735, 245.286)), (' C1084  ASP  N  ', ' C1084  ASP  OD1', -0.432, (200.769, 200.519, 133.133)), (' C 138  ASP  N  ', ' C 138  ASP  OD1', -0.424, (164.401, 246.484, 246.226)), (' A 811  LYS  NZ ', ' A 820  ASP  OD2', -0.414, (245.979, 201.477, 180.397)), (' E 204  TYR  CE2', ' E 225  PRO  HG3', -0.401, (198.01, 177.931, 227.883)), (' C1092  GLU  OE2', ' C1107  ARG  NH1', -0.4, (204.513, 212.217, 151.465)), (' E 661  GLU  O  ', ' E 697  MET  HB2', -0.4, (224.936, 186.809, 185.179))]
data['cbeta'] = [('A', '  64 ', 'TRP', ' ', 0.2766288704374374, (263.709, 241.092, 225.23799999999997)), ('C', '  64 ', 'TRP', ' ', 0.2715448360397142, (164.50700000000006, 243.184, 225.213)), ('E', '  64 ', 'TRP', ' ', 0.2784949218507751, (212.306, 156.24, 225.156))]
data['cablam'] = [('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (252.2, 235.4, 245.0)), ('A', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'beta bridge\nS-BSS', (257.0, 236.1, 252.0)), ('A', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n-TTSS', (273.9, 222.4, 238.2)), ('A', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (266.1, 236.3, 219.1)), ('A', '231', 'ILE', ' beta sheet', ' \nEE---', (250.2, 220.7, 244.6)), ('A', '385', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTSG', (217.9, 234.5, 245.1)), ('A', '393', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEES-E', (202.2, 241.7, 238.7)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (176.2, 209.5, 266.7)), ('A', '661', 'GLU', 'check CA trace,carbonyls, peptide', ' \n----S', (233.8, 235.9, 183.0)), ('A', '662', 'CYS', 'check CA trace,carbonyls, peptide', ' \n---SE', (233.4, 234.5, 186.6)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (229.8, 236.4, 195.1)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (226.2, 237.3, 194.1)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (237.7, 201.8, 159.3)), ('A', '890', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nGGTSS', (217.2, 197.6, 166.6)), ('A', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (222.7, 203.3, 169.6)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (224.5, 214.6, 172.4)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (230.6, 205.1, 189.3)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (209.1, 232.2, 132.0)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (227.6, 223.2, 152.9)), ('A', '1111', 'GLU', ' beta sheet', ' \nS---E', (228.6, 223.4, 146.8)), ('A', '218', 'GLN', 'check CA trace', ' \n-----', (261.3, 230.0, 213.8)), ('A', '220', 'PHE', 'check CA trace', ' \n-----', (257.1, 224.2, 214.6)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (244.5, 234.5, 214.0)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (219.9, 242.7, 223.2)), ('A', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (230.7, 200.9, 213.9)), ('A', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (204.0, 232.6, 139.5)), ('B', '15', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nESEEE', (174.7, 197.7, 291.7)), ('B', '85', 'SER', 'check CA trace,carbonyls, peptide', 'strand\nEEEE-', (174.1, 200.5, 289.2)), ('B', '111', 'GLN', 'check CA trace,carbonyls, peptide', ' \n----E', (195.8, 200.8, 277.3)), ('B', '100', 'PRO', 'check CA trace', 'bend\nESS--', (185.1, 209.6, 265.2)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (175.2, 236.1, 244.9)), ('C', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'beta bridge\nS-BSS', (172.2, 239.9, 252.0)), ('C', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n-TTSS', (175.6, 261.3, 238.1)), ('C', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (167.5, 247.6, 219.1)), ('C', '231', 'ILE', ' beta sheet', ' \nEE---', (189.0, 241.6, 244.6)), ('C', '385', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTSG', (193.1, 206.8, 245.1)), ('C', '393', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEES-E', (194.8, 189.6, 238.7)), ('C', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (235.6, 183.2, 266.7)), ('C', '661', 'GLU', 'check CA trace,carbonyls, peptide', ' \n----S', (183.9, 219.8, 182.9)), ('C', '662', 'CYS', 'check CA trace,carbonyls, peptide', ' \n---SE', (185.3, 220.2, 186.5)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (185.5, 216.1, 195.1)), ('C', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (186.5, 212.6, 194.1)), ('C', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (211.6, 240.3, 159.3)), ('C', '890', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nGGTSS', (225.4, 224.7, 166.6)), ('C', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (217.7, 226.6, 169.6)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (207.1, 222.5, 172.4)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (212.2, 232.5, 189.3)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (199.5, 200.3, 132.0)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (198.1, 220.9, 152.9)), ('C', '1111', 'GLU', ' beta sheet', ' \nS---E', (197.4, 221.6, 146.8)), ('C', '218', 'GLN', 'check CA trace', ' \n-----', (175.3, 246.6, 213.9)), ('C', '220', 'PHE', 'check CA trace', ' \n-----', (182.4, 245.9, 214.6)), ('C', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (179.9, 229.9, 214.0)), ('C', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (185.0, 204.5, 223.2)), ('C', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (215.8, 234.7, 213.9)), ('C', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (201.7, 195.7, 139.5)), ('D', '15', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nESEEE', (246.6, 187.8, 291.7)), ('D', '85', 'SER', 'check CA trace,carbonyls, peptide', 'strand\nEEEE-', (244.4, 185.9, 289.2)), ('D', '111', 'GLN', 'check CA trace,carbonyls, peptide', ' \n----E', (233.4, 204.6, 277.3)), ('D', '100', 'PRO', 'check CA trace', 'bend\nESS--', (231.1, 190.9, 265.2)), ('E', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (213.1, 168.9, 245.0)), ('E', '111', 'ASP', 'check CA trace,carbonyls, peptide', 'beta bridge\nS-BSS', (211.3, 164.5, 252.1)), ('E', '123', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\n-TTSS', (191.0, 156.8, 238.2)), ('E', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (206.9, 156.7, 219.1)), ('E', '231', 'ILE', ' beta sheet', ' \nEE---', (201.4, 178.1, 244.6)), ('E', '385', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-TTSG', (229.5, 199.2, 245.1)), ('E', '393', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEES-E', (243.6, 209.2, 238.7)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (228.7, 247.8, 266.7)), ('E', '661', 'GLU', 'check CA trace,carbonyls, peptide', ' \n----S', (222.9, 184.7, 182.9)), ('E', '662', 'CYS', 'check CA trace,carbonyls, peptide', ' \n---SE', (221.8, 185.8, 186.5)), ('E', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (225.2, 188.0, 195.1)), ('E', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (227.8, 190.6, 194.1)), ('E', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--STT', (191.2, 198.4, 159.3)), ('E', '890', 'ALA', 'check CA trace,carbonyls, peptide', 'turn\nGGTSS', (197.8, 218.2, 166.6)), ('E', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (200.1, 210.6, 169.6)), ('E', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (208.9, 203.4, 172.3)), ('E', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (197.7, 202.9, 189.3)), ('E', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (231.9, 208.0, 132.0)), ('E', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (214.8, 196.4, 152.9)), ('E', '1111', 'GLU', ' beta sheet', ' \nS---B', (214.6, 195.5, 146.8)), ('E', '34', 'ARG', 'check CA trace', ' \nSS-S-', (205.0, 169.1, 219.1)), ('E', '218', 'GLN', 'check CA trace', ' \n-----', (204.1, 163.9, 213.8)), ('E', '220', 'PHE', 'check CA trace', ' \n-----', (201.0, 170.4, 214.5)), ('E', '293', 'LEU', 'check CA trace', 'bend\nTTSSH', (216.1, 176.2, 214.0)), ('E', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (235.6, 193.3, 223.2)), ('E', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (194.0, 204.9, 213.9)), ('E', '1125', 'ASN', 'check CA trace', 'strand\nEEETT', (234.8, 212.2, 139.5)), ('F', '15', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nESEEE', (219.2, 255.0, 291.7)), ('F', '85', 'SER', 'check CA trace,carbonyls, peptide', 'strand\nEEEE-', (222.0, 254.1, 289.2)), ('F', '111', 'GLN', 'check CA trace,carbonyls, peptide', ' \n----E', (211.3, 235.2, 277.3)), ('F', '100', 'PRO', 'check CA trace', 'bend\nESS--', (224.3, 240.0, 265.2))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22907/7kkk/Model_validation_1/validation_cootdata/molprobity_probe7kkk_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

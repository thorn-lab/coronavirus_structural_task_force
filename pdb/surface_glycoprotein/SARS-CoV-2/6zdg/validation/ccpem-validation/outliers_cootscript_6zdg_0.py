
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
data['smoc'] = []
data['jpred'] = []
data['rota'] = [('E', ' 382 ', 'VAL', 0.003127019590465352, (255.1170000000001, 267.2190000000001, 239.20899999999995)), ('E', ' 398 ', 'ASP', 0.02754972136086107, (241.13000000000005, 269.849, 250.05099999999996)), ('E', ' 452 ', 'LEU', 0.08834883957878031, (231.768, 260.6100000000001, 259.856)), ('H', '  35 ', 'HIS', 0.0006295760537306219, (269.108, 261.58300000000014, 243.52499999999998)), ('H', ' 105 ', 'VAL', 3.802578967184184e-05, (258.693, 265.2980000000001, 236.52199999999996)), ('H', ' 146 ', 'LEU', 0.0030201496408750533, (288.716, 221.086, 234.23999999999995)), ('H', ' 190 ', 'VAL', 0.2051335497172678, (288.65400000000005, 225.843, 231.15499999999994)), ('H', ' 197 ', 'LEU', 0.09605684485359203, (295.47000000000014, 215.557, 230.08599999999998)), ('H', ' 217 ', 'LYS', 0.13280709783455777, (296.229, 224.353, 242.99699999999996)), ('L', '  33 ', 'LEU', 0.08706913708012869, (257.994, 257.178, 231.06899999999993)), ('L', '  45 ', 'LYS', 0.22733502185419327, (272.75, 255.138, 230.515)), ('L', ' 182 ', 'LEU', 0.2789599415220932, (275.183, 219.139, 251.27199999999993)), ('L', ' 215 ', 'CYS', 0.20250725266030803, (285.486, 207.031, 239.58199999999994)), ('A', ' 382 ', 'VAL', 0.003127019590465352, (251.14300000000006, 195.346, 239.57599999999994)), ('A', ' 398 ', 'ASP', 0.027136544006635652, (260.435, 206.066, 250.47499999999994)), ('A', ' 452 ', 'LEU', 0.08811864526154543, (257.15, 218.776, 260.314)), ('B', '  35 ', 'HIS', 0.0006482088330909342, (239.2350000000001, 185.855, 243.269)), ('B', ' 105 ', 'VAL', 3.855599585491074e-05, (247.68000000000006, 193.048, 236.32199999999995)), ('B', ' 146 ', 'LEU', 0.0030007176608138767, (194.37700000000007, 189.256, 233.95299999999995)), ('B', ' 190 ', 'VAL', 0.20398678935834494, (198.527, 186.944, 230.858)), ('B', ' 197 ', 'LEU', 0.0960468685563941, (186.211, 186.212, 229.77)), ('B', ' 217 ', 'LYS', 0.13285442707126244, (193.42600000000004, 181.061, 242.65699999999995)), ('C', '  33 ', 'LEU', 0.08667041352296949, (241.08700000000005, 197.888, 230.59199999999996)), ('C', '  45 ', 'LYS', 0.22620887854585314, (231.93600000000004, 186.13, 230.12999999999997)), ('C', ' 182 ', 'LEU', 0.2793981538054005, (199.55700000000007, 202.194, 250.774)), ('C', ' 215 ', 'CYS', 0.20282371526378187, (183.91500000000008, 199.243, 239.10999999999996)), ('D', ' 382 ', 'VAL', 0.003127019590465352, (190.84900000000013, 234.666, 239.54199999999994)), ('D', ' 398 ', 'ASP', 0.027226917596299124, (195.60600000000008, 221.277, 250.413)), ('D', ' 452 ', 'LEU', 0.08778948471619379, (208.344, 217.804, 260.151)), ('F', '  35 ', 'HIS', 0.0006363689001732466, (188.78500000000014, 249.56300000000002, 243.433)), ('F', ' 105 ', 'VAL', 4.325517705809389e-05, (190.86400000000012, 238.643, 236.52299999999997)), ('F', ' 146 ', 'LEU', 0.003046075572485861, (214.13300000000007, 286.75100000000003, 234.20499999999998)), ('F', ' 190 ', 'VAL', 0.20641960922755678, (210.083, 284.297, 231.088)), ('F', ' 197 ', 'LEU', 0.09610307129832073, (215.588, 295.339, 230.013)), ('F', ' 217 ', 'LYS', 0.13310821888399113, (207.4420000000001, 291.675, 242.85299999999995)), ('G', '  33 ', 'LEU', 0.08679076227183653, (197.95200000000008, 242.207, 231.526)), ('G', '  45 ', 'LYS', 0.22690465752198255, (192.373, 256.0200000000001, 231.003)), ('G', ' 182 ', 'LEU', 0.2780576772635089, (222.51400000000007, 276.0570000000001, 251.56299999999993)), ('G', ' 215 ', 'CYS', 0.20114282366032388, (227.81200000000007, 291.017, 239.83399999999997))]
data['clusters'] = [('A', '350', 1, 'backbone clash', (257.135, 216.435, 254.534)), ('A', '351', 1, 'backbone clash', (257.135, 216.435, 254.534)), ('A', '449', 1, 'side-chain clash', (257.226, 219.421, 265.071)), ('A', '452', 1, 'Rotamer', (257.15, 218.776, 260.314)), ('A', '494', 1, 'side-chain clash', (257.226, 219.421, 265.071)), ('A', '354', 2, 'backbone clash', (265.368, 208.076, 252.63)), ('A', '355', 2, 'backbone clash', (265.368, 208.076, 252.63)), ('A', '398', 2, 'side-chain clash\nRotamer', (260.435, 206.066, 250.47499999999994)), ('A', '511', 2, 'side-chain clash', (257.728, 204.627, 252.611)), ('A', '437', 3, 'backbone clash', (249.773, 206.985, 263.905)), ('A', '438', 3, 'side-chain clash', (255.212, 206.866, 264.524)), ('A', '442', 3, 'side-chain clash', (255.212, 206.866, 264.524)), ('A', '507', 3, 'backbone clash', (249.773, 206.985, 263.905)), ('A', '335', 4, 'side-chain clash', (264.604, 187.369, 250.744)), ('A', '362', 4, 'side-chain clash', (266.678, 187.684, 249.366)), ('A', '364', 4, 'side-chain clash', (264.604, 187.369, 250.744)), ('A', '484', 5, 'cablam CA Geom Outlier', (259.2, 236.8, 259.1)), ('A', '485', 5, 'cablam Outlier', (256.0, 238.7, 259.9)), ('A', '486', 5, 'cablam Outlier', (253.4, 240.1, 257.6)), ('A', '393', 6, 'backbone clash', (264.302, 198.805, 236.804)), ('A', '516', 6, 'backbone clash', (264.302, 198.805, 236.804)), ('A', '498', 7, 'side-chain clash', (249.811, 214.085, 269.464)), ('A', '501', 7, 'side-chain clash', (249.811, 214.085, 269.464)), ('A', '358', 8, 'side-chain clash', (247.349, 197.124, 246.832)), ('A', '395', 8, 'side-chain clash', (247.349, 197.124, 246.832)), ('A', '357', 9, 'backbone clash\nside-chain clash', (250.954, 188.465, 235.611)), ('A', '394', 9, 'side-chain clash', (250.954, 188.465, 235.611)), ('A', '363', 10, 'side-chain clash', (261.308, 191.506, 245.633)), ('A', '365', 10, 'side-chain clash', (261.308, 191.506, 245.633)), ('B', '106', 1, 'side-chain clash', (248.582, 188.592, 242.836)), ('B', '17', 1, 'backbone clash', (229.711, 184.469, 258.145)), ('B', '20', 1, 'side-chain clash', (231.64, 183.23, 249.039)), ('B', '29', 1, 'side-chain clash', (244.235, 177.474, 242.805)), ('B', '33', 1, 'backbone clash', (245.142, 184.211, 244.305)), ('B', '35', 1, 'backbone clash\nRotamer', (239.2350000000001, 185.855, 243.269)), ('B', '36', 1, 'side-chain clash', (234.266, 183.534, 247.226)), ('B', '47', 1, 'side-chain clash', (239.82, 190.701, 247.812)), ('B', '48', 1, 'backbone clash', (238.124, 192.832, 249.249)), ('B', '49', 1, 'side-chain clash', (239.82, 190.701, 247.812)), ('B', '51', 1, 'backbone clash', (245.142, 184.211, 244.305)), ('B', '52', 1, 'side-chain clash', (245.57, 180.805, 244.818)), ('B', '53', 1, 'backbone clash', (248.055, 182.224, 243.047)), ('B', '61', 1, 'backbone clash', (237.278, 194.581, 253.075)), ('B', '65', 1, 'backbone clash', (237.278, 194.581, 253.075)), ('B', '72', 1, 'side-chain clash', (244.235, 177.474, 242.805)), ('B', '81', 1, 'side-chain clash', (231.64, 183.23, 249.039)), ('B', '83', 1, 'side-chain clash\nbackbone clash', (229.711, 184.469, 258.145)), ('B', '86', 1, 'side-chain clash', (229.637, 186.774, 254.276)), ('B', '87', 1, 'side-chain clash', (226.32, 190.98, 255.808)), ('B', '89', 1, 'side-chain clash', (224.165, 194.852, 253.809)), ('B', '90', 1, 'side-chain clash', (226.32, 190.98, 255.808)), ('B', '98', 1, 'backbone clash', (240.701, 185.384, 238.456)), ('B', '99', 1, 'cablam Outlier', (243.7, 184.2, 238.2)), ('B', '132', 2, 'backbone clash', (194.614, 188.985, 238.897)), ('B', '134', 2, 'side-chain clash', (191.985, 189.141, 234.322)), ('B', '146', 2, 'side-chain clash\nRotamer', (194.37700000000007, 189.256, 233.95299999999995)), ('B', '147', 2, 'backbone clash', (194.614, 188.985, 238.897)), ('B', '167', 2, 'side-chain clash', (196.602, 183.047, 230.084)), ('B', '190', 2, 'side-chain clash\nRotamer', (198.527, 186.944, 230.858)), ('B', '124', 3, 'side-chain clash', (211.881, 181.589, 253.903)), ('B', '155', 3, 'side-chain clash', (211.881, 181.589, 253.903)), ('B', '156', 3, 'cablam CA Geom Outlier', (212.9, 183.2, 247.2)), ('B', '21', 4, 'side-chain clash', (231.109, 173.656, 247.288)), ('B', '6', 4, 'side-chain clash', (230.52, 177.194, 241.67)), ('B', '7', 4, 'side-chain clash', (231.109, 173.656, 247.288)), ('B', '200', 5, 'backbone clash', (189.966, 179.161, 232.167)), ('B', '201', 5, 'backbone clash', (189.966, 179.161, 232.167)), ('B', '164', 6, 'side-chain clash', (197.294, 175.738, 236.538)), ('B', '205', 6, 'side-chain clash', (197.294, 175.738, 236.538)), ('B', '129', 7, 'backbone clash', (199.176, 186.532, 245.4)), ('B', '149', 7, 'backbone clash', (199.176, 186.532, 245.4)), ('B', '73', 8, 'side-chain clash', (243.914, 169.299, 249.856)), ('B', '75', 8, 'side-chain clash', (243.914, 169.299, 249.856)), ('B', '103', 9, 'backbone clash', (250.954, 188.465, 235.611)), ('B', '105', 9, 'Rotamer', (247.68000000000006, 193.048, 236.32199999999995)), ('B', '197', 10, 'cablam Outlier\nRotamer', (186.2, 186.2, 229.8)), ('B', '217', 10, 'Rotamer', (193.42600000000004, 181.061, 242.65699999999995)), ('C', '33', 1, 'backbone clash\nside-chain clash\nRotamer', (241.08700000000005, 197.888, 230.59199999999996)), ('C', '34', 1, 'backbone clash\nside-chain clash', (238.804, 196.963, 230.673)), ('C', '50', 1, 'cablam CA Geom Outlier', (244.1, 194.7, 227.9)), ('C', '89', 1, 'backbone clash', (239.53, 196.726, 235.844)), ('C', '90', 1, 'backbone clash', (239.53, 196.726, 235.844)), ('C', '151', 2, 'side-chain clash', (196.669, 212.851, 244.004)), ('C', '154', 2, 'side-chain clash', (196.669, 212.851, 244.004)), ('C', '148', 3, 'side-chain clash', (202.362, 212.17, 237.966)), ('C', '155', 3, 'side-chain clash', (202.362, 212.17, 237.966)), ('C', '61', 4, 'side-chain clash', (228.876, 189.169, 216.952)), ('C', '82', 4, 'side-chain clash', (228.876, 189.169, 216.952)), ('C', '109', 5, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (212.942, 196.977, 215.904)), ('C', '110', 5, 'backbone clash', (208.979, 198.183, 216.852)), ('C', '135', 6, 'side-chain clash', (199.31, 201.76, 238.125)), ('C', '149', 6, 'side-chain clash', (199.31, 201.76, 238.125)), ('C', '37', 7, 'backbone clash', (230.504, 187.205, 230.28)), ('C', '45', 7, 'backbone clash\nRotamer', (231.93600000000004, 186.13, 230.12999999999997)), ('C', '2', 8, 'side-chain clash', (242.568, 201.909, 240.402)), ('C', '93', 8, 'side-chain clash', (242.568, 201.909, 240.402)), ('C', '18', 9, 'backbone clash', (229.861, 196.841, 214.259)), ('C', '75', 9, 'backbone clash', (229.861, 196.841, 214.259)), ('D', '335', 1, 'side-chain clash', (185.253, 238.371, 236.072)), ('D', '350', 1, 'backbone clash\nside-chain clash', (189.961, 236.187, 238.459)), ('D', '351', 1, 'backbone clash\nside-chain clash', (189.961, 236.187, 238.459)), ('D', '364', 1, 'side-chain clash', (185.253, 238.371, 236.072)), ('D', '382', 1, 'Rotamer', (190.84900000000013, 234.666, 239.54199999999994)), ('D', '354', 2, 'backbone clash', (194.828, 215.81, 252.936)), ('D', '355', 2, 'backbone clash', (194.828, 215.81, 252.936)), ('D', '398', 2, 'side-chain clash\nRotamer', (195.60600000000008, 221.277, 250.413)), ('D', '511', 2, 'side-chain clash', (195.662, 224.316, 252.62)), ('D', '449', 3, 'side-chain clash', (208.842, 217.529, 264.917)), ('D', '452', 3, 'Rotamer', (208.344, 217.804, 260.151)), ('D', '494', 3, 'side-chain clash', (208.842, 217.529, 264.917)), ('D', '356', 4, 'backbone clash', (186.029, 215.951, 249.482)), ('D', '358', 4, 'side-chain clash', (186.451, 220.887, 246.192)), ('D', '395', 4, 'side-chain clash', (186.451, 220.887, 246.192)), ('D', '403', 5, 'side-chain clash', (212.041, 231.57, 259.941)), ('D', '405', 5, 'side-chain clash', (208.95, 233.65, 255.016)), ('D', '408', 5, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (205.955, 233.954, 251.895)), ('D', '484', 6, 'cablam CA Geom Outlier', (222.9, 207.1, 258.8)), ('D', '485', 6, 'cablam Outlier', (226.2, 208.9, 259.6)), ('D', '486', 6, 'cablam Outlier', (228.7, 210.5, 257.3)), ('D', '334', 7, 'backbone clash', (176.553, 221.757, 247.262)), ('D', '362', 7, 'side-chain clash\nbackbone clash', (176.553, 221.757, 247.262)), ('D', '393', 8, 'backbone clash', (187.157, 221.624, 236.759)), ('D', '516', 8, 'backbone clash', (187.157, 221.624, 236.759)), ('D', '498', 9, 'side-chain clash', (186.64, 240.751, 242.97)), ('D', '501', 9, 'side-chain clash', (186.64, 240.751, 242.97)), ('D', '357', 10, 'backbone clash\nside-chain clash', (186.523, 215.636, 240.708)), ('D', '394', 10, 'side-chain clash', (186.523, 215.636, 240.708)), ('D', '437', 11, 'backbone clash', (201.79, 230.146, 263.706)), ('D', '507', 11, 'backbone clash', (201.79, 230.146, 263.706)), ('D', '363', 12, 'side-chain clash', (182.499, 227.782, 245.616)), ('D', '365', 12, 'side-chain clash', (182.499, 227.782, 245.616)), ('D', '424', 13, 'backbone clash', (205.99, 225.225, 240.57)), ('D', '425', 13, 'backbone clash', (205.99, 225.225, 240.57)), ('D', '428', 14, 'side-chain clash', (198.356, 233.957, 240.661)), ('D', '519', 14, 'cablam Outlier', (185.6, 220.2, 229.3)), ('E', '382', 1, 'Rotamer', (255.1170000000001, 267.2190000000001, 239.20899999999995)), ('E', '393', 1, 'backbone clash\nside-chain clash', (255.162, 273.396, 235.763)), ('E', '405', 1, 'side-chain clash', (261.282, 270.308, 235.415)), ('E', '422', 1, 'backbone clash', (257.23, 267.139, 239.328)), ('E', '437', 1, 'backbone clash\nside-chain clash', (255.594, 269.665, 238.349)), ('E', '449', 1, 'side-chain clash', (262.286, 268.422, 242.593)), ('E', '454', 1, 'backbone clash', (257.23, 267.139, 239.328)), ('E', '494', 1, 'side-chain clash', (262.286, 268.422, 242.593)), ('E', '507', 1, 'backbone clash\nside-chain clash', (255.594, 269.665, 238.349)), ('E', '516', 1, 'backbone clash\nside-chain clash', (255.162, 273.396, 235.763)), ('E', '334', 2, 'backbone clash', (250.924, 285.755, 246.991)), ('E', '335', 2, 'side-chain clash', (255.495, 282.516, 250.393)), ('E', '362', 2, 'side-chain clash\nbackbone clash', (250.924, 285.755, 246.991)), ('E', '364', 2, 'side-chain clash', (255.495, 282.516, 250.393)), ('E', '354', 3, 'backbone clash', (236.699, 273.085, 252.155)), ('E', '355', 3, 'backbone clash', (236.699, 273.085, 252.155)), ('E', '398', 3, 'side-chain clash\nRotamer', (241.13000000000005, 269.849, 250.05099999999996)), ('E', '511', 3, 'side-chain clash', (243.441, 268.493, 252.044)), ('E', '350', 4, 'backbone clash', (234.059, 261.452, 254.209)), ('E', '351', 4, 'backbone clash', (234.059, 261.452, 254.209)), ('E', '452', 4, 'Rotamer', (231.768, 260.6100000000001, 259.856)), ('E', '356', 5, 'backbone clash', (241.133, 280.547, 249.088)), ('E', '358', 5, 'side-chain clash', (245.9, 277.923, 245.558)), ('E', '395', 5, 'side-chain clash', (245.9, 277.923, 245.558)), ('E', '484', 6, 'cablam CA Geom Outlier', (215.2, 253.3, 258.6)), ('E', '485', 6, 'cablam Outlier', (215.2, 249.6, 259.4)), ('E', '486', 6, 'cablam Outlier', (215.2, 246.6, 257.1)), ('E', '498', 7, 'side-chain clash', (239.573, 256.67, 268.851)), ('E', '501', 7, 'side-chain clash', (239.573, 256.67, 268.851)), ('E', '357', 8, 'backbone clash\nside-chain clash', (241.36, 280.755, 240.126)), ('E', '394', 8, 'side-chain clash', (241.36, 280.755, 240.126)), ('E', '363', 9, 'side-chain clash', (255.532, 262.621, 247.827)), ('E', '365', 9, 'side-chain clash', (255.532, 262.621, 247.827)), ('E', '424', 10, 'backbone clash', (239.371, 258.832, 240.253)), ('E', '425', 10, 'backbone clash', (239.371, 258.832, 240.253)), ('E', '438', 11, 'side-chain clash', (242.999, 264.909, 264.1)), ('E', '442', 11, 'side-chain clash', (242.999, 264.909, 264.1)), ('F', '106', 1, 'side-chain clash', (186.64, 240.751, 242.97)), ('F', '21', 1, 'side-chain clash', (194.445, 246.413, 241.671)), ('F', '29', 1, 'side-chain clash', (178.58, 248.935, 242.67)), ('F', '33', 1, 'backbone clash', (184.44, 245.09, 244.079)), ('F', '35', 1, 'backbone clash\nside-chain clash\nRotamer', (188.78500000000014, 249.56300000000002, 243.433)), ('F', '51', 1, 'backbone clash', (184.44, 245.09, 244.079)), ('F', '52', 1, 'side-chain clash', (181.03, 246.614, 245.005)), ('F', '53', 1, 'backbone clash', (180.934, 243.846, 243.52)), ('F', '7', 1, 'side-chain clash', (194.445, 246.413, 241.671)), ('F', '72', 1, 'side-chain clash', (178.58, 248.935, 242.67)), ('F', '99', 1, 'cablam Outlier', (185.2, 246.5, 238.3)), ('F', '17', 2, 'backbone clash', (192.275, 258.608, 258.25)), ('F', '20', 2, 'side-chain clash', (190.181, 257.924, 249.268)), ('F', '36', 2, 'side-chain clash', (189.175, 255.354, 247.844)), ('F', '81', 2, 'side-chain clash', (190.181, 257.924, 249.268)), ('F', '83', 2, 'side-chain clash\nbackbone clash', (192.275, 258.608, 258.25)), ('F', '86', 2, 'side-chain clash', (194.363, 257.346, 254.46)), ('F', '87', 2, 'side-chain clash', (199.473, 258.396, 256.023)), ('F', '89', 2, 'side-chain clash', (203.968, 258.257, 254.102)), ('F', '90', 2, 'side-chain clash', (199.473, 258.396, 256.023)), ('F', '104', 3, 'backbone clash\nside-chain clash', (198.338, 253.678, 235.533)), ('F', '167', 3, 'side-chain clash', (199.136, 251.678, 238.511)), ('F', '38', 3, 'side-chain clash', (199.178, 251.256, 239.422)), ('F', '47', 3, 'side-chain clash', (199.311, 255.848, 236.327)), ('F', '49', 3, 'side-chain clash', (199.311, 255.848, 236.327)), ('F', '6', 3, 'side-chain clash', (199.547, 253.951, 235.967)), ('F', '94', 3, 'side-chain clash', (199.178, 251.256, 239.422)), ('F', '98', 3, 'backbone clash\nside-chain clash', (194.115, 260.018, 237.493)), ('F', '132', 4, 'backbone clash', (213.767, 286.661, 239.125)), ('F', '134', 4, 'side-chain clash', (215.612, 288.963, 234.435)), ('F', '146', 4, 'side-chain clash\nRotamer', (214.13300000000007, 286.75100000000003, 234.20499999999998)), ('F', '147', 4, 'backbone clash', (213.767, 286.661, 239.125)), ('F', '190', 4, 'side-chain clash\nRotamer', (210.083, 284.297, 231.088)), ('F', '48', 5, 'backbone clash', (195.365, 247.037, 249.353)), ('F', '61', 5, 'backbone clash', (196.994, 246.942, 253.715)), ('F', '65', 5, 'backbone clash', (196.994, 246.942, 253.715)), ('F', '200', 6, 'backbone clash', (207.322, 295.267, 231.919)), ('F', '201', 6, 'backbone clash', (207.322, 295.267, 231.919)), ('F', '124', 7, 'side-chain clash', (198.538, 275.429, 254.019)), ('F', '155', 7, 'side-chain clash', (198.538, 275.429, 254.019)), ('F', '129', 8, 'backbone clash', (209.569, 283.755, 245.371)), ('F', '149', 8, 'backbone clash', (209.569, 283.755, 245.371)), ('F', '73', 9, 'side-chain clash', (172.035, 253.794, 249.93)), ('F', '75', 9, 'side-chain clash', (172.035, 253.794, 249.93)), ('F', '103', 10, 'backbone clash', (185.253, 238.371, 236.072)), ('F', '105', 10, 'Rotamer', (190.86400000000012, 238.643, 236.52299999999997)), ('G', '33', 1, 'backbone clash\nside-chain clash\nRotamer', (197.95200000000008, 242.207, 231.526)), ('G', '34', 1, 'backbone clash\nside-chain clash', (198.327, 244.779, 231.64)), ('G', '50', 1, 'cablam CA Geom Outlier', (193.7, 241.2, 228.9)), ('G', '89', 1, 'backbone clash', (196.864, 243.886, 236.528)), ('G', '90', 1, 'backbone clash', (196.864, 243.886, 236.528)), ('G', '94', 1, 'side-chain clash', (190.959, 241.419, 241.76)), ('G', '97', 1, 'side-chain clash', (194.445, 246.413, 241.671)), ('G', '135', 2, 'side-chain clash', (222.142, 276.313, 238.502)), ('G', '137', 2, 'side-chain clash', (218.581, 275.433, 232.591)), ('G', '149', 2, 'side-chain clash', (222.142, 276.313, 238.502)), ('G', '2', 3, 'side-chain clash', (201.049, 238.91, 241.149)), ('G', '92', 3, 'side-chain clash', (198.356, 233.957, 240.661)), ('G', '93', 3, 'side-chain clash', (201.049, 238.91, 241.149)), ('G', '151', 4, 'side-chain clash', (233.463, 272.76, 244.698)), ('G', '154', 4, 'side-chain clash', (233.463, 272.76, 244.698)), ('G', '148', 5, 'side-chain clash', (229.761, 268.528, 238.729)), ('G', '155', 5, 'side-chain clash', (229.761, 268.528, 238.729)), ('G', '61', 6, 'side-chain clash', (196.526, 257.11, 217.802)), ('G', '82', 6, 'side-chain clash', (196.526, 257.11, 217.802)), ('G', '109', 7, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (211.288, 266.944, 216.731)), ('G', '110', 7, 'backbone clash', (213.771, 270.093, 217.844)), ('G', '87', 8, 'side-chain clash', (198.338, 253.678, 235.533)), ('G', '99', 8, 'side-chain clash', (199.178, 251.256, 239.422)), ('G', '37', 9, 'backbone clash', (193.916, 256.664, 230.964)), ('G', '45', 9, 'backbone clash\nRotamer', (192.373, 256.0200000000001, 231.003)), ('G', '18', 10, 'backbone clash', (202.753, 252.252, 215.143)), ('G', '75', 10, 'backbone clash', (202.753, 252.252, 215.143)), ('H', '17', 1, 'backbone clash', (275.364, 253.993, 258.664)), ('H', '20', 1, 'side-chain clash', (275.215, 256.409, 249.336)), ('H', '36', 1, 'side-chain clash', (273.711, 258.131, 247.891)), ('H', '38', 1, 'side-chain clash', (272.135, 252.765, 246.843)), ('H', '81', 1, 'side-chain clash', (275.215, 256.409, 249.336)), ('H', '83', 1, 'side-chain clash\nbackbone clash', (275.364, 253.993, 258.664)), ('H', '86', 1, 'side-chain clash', (273.169, 252.733, 254.705)), ('H', '87', 1, 'side-chain clash', (271.309, 247.943, 256.171)), ('H', '89', 1, 'side-chain clash', (268.853, 244.083, 254.073)), ('H', '90', 1, 'side-chain clash', (271.309, 247.943, 256.171)), ('H', '94', 1, 'side-chain clash', (272.135, 252.765, 246.843)), ('H', '103', 2, 'backbone clash', (261.282, 270.308, 235.415)), ('H', '104', 2, 'side-chain clash\nbackbone clash', (257.23, 267.139, 239.328)), ('H', '105', 2, 'Rotamer', (258.693, 265.2980000000001, 236.52199999999996)), ('H', '106', 2, 'side-chain clash', (262.286, 268.422, 242.593)), ('H', '29', 2, 'side-chain clash', (273.628, 270.796, 242.917)), ('H', '33', 2, 'backbone clash', (268.072, 271.274, 243.657)), ('H', '52', 2, 'side-chain clash', (270.349, 269.738, 245.11)), ('H', '53', 2, 'backbone clash', (268.072, 271.274, 243.657)), ('H', '72', 2, 'side-chain clash', (273.628, 270.796, 242.917)), ('H', '35', 3, 'backbone clash\nRotamer', (269.108, 261.58300000000014, 243.52499999999998)), ('H', '47', 3, 'side-chain clash', (264.338, 259.754, 247.668)), ('H', '48', 3, 'backbone clash', (263.578, 257.087, 249.41)), ('H', '49', 3, 'side-chain clash', (264.338, 259.754, 247.668)), ('H', '61', 3, 'backbone clash', (262.525, 255.585, 253.261)), ('H', '65', 3, 'backbone clash', (262.525, 255.585, 253.261)), ('H', '98', 3, 'backbone clash', (268.822, 263.248, 238.837)), ('H', '99', 3, 'cablam Outlier', (268.3, 266.3, 238.4)), ('H', '132', 4, 'backbone clash', (288.671, 221.5, 239.34)), ('H', '134', 4, 'side-chain clash', (289.955, 218.698, 234.419)), ('H', '146', 4, 'side-chain clash\nRotamer', (288.716, 221.086, 234.23999999999995)), ('H', '147', 4, 'backbone clash', (288.671, 221.5, 239.34)), ('H', '167', 4, 'side-chain clash', (292.482, 226.068, 230.292)), ('H', '190', 4, 'side-chain clash\nRotamer', (288.65400000000005, 225.843, 231.15499999999994)), ('H', '21', 5, 'side-chain clash', (283.845, 260.169, 247.276)), ('H', '6', 5, 'side-chain clash', (280.956, 258.333, 242.064)), ('H', '7', 5, 'side-chain clash', (283.845, 260.169, 247.276)), ('H', '200', 6, 'backbone clash', (299.591, 222.598, 232.074)), ('H', '201', 6, 'backbone clash', (299.591, 222.598, 232.074)), ('H', '124', 7, 'side-chain clash', (265.617, 251.553, 238.84)), ('H', '155', 7, 'side-chain clash', (265.617, 251.553, 238.84)), ('H', '129', 8, 'backbone clash', (288.256, 226.406, 245.482)), ('H', '149', 8, 'backbone clash', (288.256, 226.406, 245.482)), ('H', '73', 9, 'side-chain clash', (281.06, 273.94, 250.306)), ('H', '75', 9, 'side-chain clash', (281.06, 273.94, 250.306)), ('L', '33', 1, 'backbone clash\nside-chain clash\nRotamer', (257.994, 257.178, 231.06899999999993)), ('L', '34', 1, 'backbone clash\nside-chain clash', (259.806, 255.269, 230.987)), ('L', '50', 1, 'cablam CA Geom Outlier', (259.2, 261.4, 228.4)), ('L', '89', 1, 'backbone clash', (259.978, 257.372, 236.087)), ('L', '90', 1, 'backbone clash', (259.978, 257.372, 236.087)), ('L', '151', 2, 'side-chain clash', (267.302, 211.127, 244.604)), ('L', '154', 2, 'side-chain clash', (267.302, 211.127, 244.604)), ('L', '61', 3, 'side-chain clash', (271.579, 250.946, 217.442)), ('L', '82', 3, 'side-chain clash', (271.579, 250.946, 217.442)), ('L', '109', 4, 'backbone clash\nDihedral angle:CD:NE:CZ:NH1', (272.768, 233.21399999999997, 216.36700000000002)), ('L', '110', 4, 'backbone clash', (274.257, 229.013, 217.447)), ('L', '135', 5, 'side-chain clash', (275.631, 219.161, 238.212)), ('L', '149', 5, 'side-chain clash', (275.631, 219.161, 238.212)), ('L', '37', 6, 'backbone clash', (272.241, 253.526, 230.554)), ('L', '45', 6, 'backbone clash\nRotamer', (272.75, 255.138, 230.515)), ('L', '2', 7, 'side-chain clash', (253.675, 256.195, 240.661)), ('L', '93', 7, 'side-chain clash', (253.675, 256.195, 240.661)), ('L', '18', 8, 'backbone clash', (264.396, 247.996, 214.57)), ('L', '75', 8, 'backbone clash', (264.396, 247.996, 214.57))]
data['probe'] = [(' B   7  SER  OG ', ' B  21  SER  OG ', -0.907, (231.109, 173.656, 247.288)), (' F   7  SER  OG ', ' F  21  SER  OG ', -0.904, (182.715, 262.916, 246.929)), (' H   7  SER  OG ', ' H  21  SER  OG ', -0.898, (283.845, 260.169, 247.276)), (' F  47  TRP  CD1', ' G  97  LEU HD12', -0.822, (194.445, 246.413, 241.671)), (' G  89  GLN  NE2', ' G  90  GLN  O  ', -0.82, (196.864, 243.886, 236.528)), (' G 109  ARG  NH2', ' G 110  THR  O  ', -0.819, (213.771, 270.093, 217.844)), (' L  89  GLN  NE2', ' L  90  GLN  O  ', -0.818, (259.978, 257.372, 236.087)), (' C  89  GLN  NE2', ' C  90  GLN  O  ', -0.813, (239.53, 196.726, 235.844)), (' L 109  ARG  NH2', ' L 110  THR  O  ', -0.812, (274.257, 229.013, 217.447)), (' C 109  ARG  NH2', ' C 110  THR  O  ', -0.796, (208.979, 198.183, 216.852)), (' D 356  LYS  NZ ', ' D 357  ARG  O  ', -0.764, (186.029, 215.951, 249.482)), (' A 356  LYS  NZ ', ' A 357  ARG  O  ', -0.756, (269.725, 200.101, 249.482)), (' D 403  ARG  NH1', ' D 405  ASP  OD2', -0.747, (212.041, 231.57, 259.941)), (' E 356  LYS  NZ ', ' E 357  ARG  O  ', -0.746, (241.133, 280.547, 249.088)), (' A 403  ARG  NH1', ' A 405  ASP  OD2', -0.734, (243.439, 214.279, 260.199)), (' E 498  GLN  N  ', ' E 501  ASN  OD1', -0.731, (239.573, 256.67, 268.851)), (' A 498  GLN  N  ', ' A 501  ASN  OD1', -0.727, (249.811, 214.085, 269.464)), (' E 403  ARG  NH1', ' E 405  ASP  OD2', -0.727, (242.469, 250.81, 259.585)), (' D 498  GLN  N  ', ' D 501  ASN  OD1', -0.722, (208.074, 226.453, 269.25)), (' D 385  THR  HG1', ' F 106  TYR  HH ', -0.709, (186.64, 240.751, 242.97)), (' D 405  ASP  O  ', ' D 408  ARG  NH2', -0.687, (208.95, 233.65, 255.016)), (' A 405  ASP  O  ', ' A 408  ARG  NH2', -0.683, (242.62, 211.272, 255.227)), (' E 405  ASP  O  ', ' E 408  ARG  NH2', -0.681, (245.601, 251.86, 254.819)), (' F 200  GLN  NE2', ' F 201  THR  O  ', -0.681, (207.322, 295.267, 231.919)), (' H 200  GLN  NE2', ' H 201  THR  O  ', -0.674, (299.591, 222.598, 232.074)), (' B 200  GLN  NE2', ' B 201  THR  O  ', -0.674, (189.966, 179.161, 232.167)), (' E 386  LYS  NZ ', ' H 103  LEU  O  ', -0.662, (261.282, 270.308, 235.415)), (' H  33  ASP  OD1', ' H  53  TYR  N  ', -0.66, (268.072, 271.274, 243.657)), (' B  33  ASP  OD1', ' B  53  TYR  N  ', -0.657, (248.055, 182.224, 243.047)), (' B  89  GLU  N  ', ' B  89  GLU  OE1', -0.652, (224.165, 194.852, 253.809)), (' F  33  ASP  OD1', ' F  53  TYR  N  ', -0.651, (180.934, 243.846, 243.52)), (' F  89  GLU  N  ', ' F  89  GLU  OE1', -0.645, (203.968, 258.257, 254.102)), (' H  52  SER  O  ', ' H  72  ARG  NH1', -0.641, (270.349, 269.738, 245.11)), (' F  48  VAL  O  ', ' F  61  ALA  N  ', -0.637, (195.365, 247.037, 249.353)), (' B  52  SER  O  ', ' B  72  ARG  NH1', -0.636, (245.57, 180.805, 244.818)), (' H  89  GLU  N  ', ' H  89  GLU  OE1', -0.636, (268.853, 244.083, 254.073)), (' L 166  GLU  N  ', ' L 166  GLU  OE1', -0.636, (278.528, 236.675, 231.312)), (' C 166  GLU  N  ', ' C 166  GLU  OE1', -0.631, (213.015, 190.458, 230.959)), (' F  52  SER  O  ', ' F  72  ARG  NH1', -0.631, (181.03, 246.614, 245.005)), (' B  48  VAL  O  ', ' B  61  ALA  N  ', -0.628, (238.124, 192.832, 249.249)), (' G 166  GLU  N  ', ' G 166  GLU  OE1', -0.624, (205.525, 270.05, 231.733)), (' F  87  ARG  N  ', ' F  90  ASP  OD2', -0.622, (199.473, 258.396, 256.023)), (' H  48  VAL  O  ', ' H  61  ALA  N  ', -0.617, (263.578, 257.087, 249.41)), (' E 393  THR  OG1', ' E 516  GLU  O  ', -0.617, (245.489, 276.848, 236.413)), (' A 385  THR  OG1', ' B 106  TYR  OH ', -0.611, (248.582, 188.592, 242.836)), (' H  87  ARG  N  ', ' H  90  ASP  OD2', -0.603, (271.309, 247.943, 256.171)), (' A 393  THR  OG1', ' A 516  GLU  O  ', -0.598, (264.302, 198.805, 236.804)), (' H  29  PHE  O  ', ' H  72  ARG  NH2', -0.596, (273.628, 270.796, 242.917)), (' B  29  PHE  O  ', ' B  72  ARG  NH2', -0.593, (244.235, 177.474, 242.805)), (' E 382  VAL HG23', ' H 104  TRP  HB3', -0.593, (256.361, 269.667, 237.974)), (' B  87  ARG  N  ', ' B  90  ASP  OD2', -0.593, (226.32, 190.98, 255.808)), (' F  29  PHE  O  ', ' F  72  ARG  NH2', -0.589, (178.58, 248.935, 242.67)), (' D 357  ARG  NH2', ' D 394  ASN  OD1', -0.589, (186.523, 215.636, 240.708)), (' E 390  LEU HD21', ' H 104  TRP  CE2', -0.586, (255.162, 273.396, 235.763)), (' H  73  ASP  OD2', ' H  75  SER  OG ', -0.584, (281.06, 273.94, 250.306)), (' A 357  ARG  NH2', ' A 394  ASN  OD1', -0.578, (269.754, 200.427, 240.521)), (' D 393  THR  OG1', ' D 516  GLU  O  ', -0.578, (187.157, 221.624, 236.759)), (' B  73  ASP  OD2', ' B  75  SER  OG ', -0.575, (243.914, 169.299, 249.856)), (' E 357  ARG  NH2', ' E 394  ASN  OD1', -0.573, (241.36, 280.755, 240.126)), (' A 386  LYS  NZ ', ' B 103  LEU  O  ', -0.572, (250.954, 188.465, 235.611)), (' A 449  TYR  O  ', ' A 494  SER  OG ', -0.572, (257.226, 219.421, 265.071)), (' D 449  TYR  O  ', ' D 494  SER  OG ', -0.571, (208.842, 217.529, 264.917)), (' F  73  ASP  OD2', ' F  75  SER  OG ', -0.571, (172.035, 253.794, 249.93)), (' E 449  TYR  O  ', ' E 494  SER  OG ', -0.565, (231.084, 260.396, 264.528)), (' G  37  GLN  N  ', ' G  45  LYS  O  ', -0.562, (195.318, 254.168, 229.91)), (' H  83  MET  HB3', ' H  86  LEU HD21', -0.558, (273.169, 252.733, 254.705)), (' B  83  MET  HB3', ' B  86  LEU HD21', -0.558, (229.637, 186.774, 254.276)), (' G 124  GLU  N  ', ' G 124  GLU  OE1', -0.553, (217.482, 290.537, 248.803)), (' B 167  LEU HD21', ' B 190  VAL HG21', -0.551, (196.602, 183.047, 230.084)), (' F 167  LEU HD21', ' F 190  VAL HG21', -0.55, (207.915, 287.506, 230.119)), (' H 167  LEU HD21', ' H 190  VAL HG21', -0.545, (292.482, 226.068, 230.292)), (' F  45  LEU  HB2', ' G  99  PHE  CG ', -0.543, (199.136, 251.678, 238.511)), (' F  83  MET  HB3', ' F  86  LEU HD21', -0.542, (194.363, 257.346, 254.46)), (' C  37  GLN  N  ', ' C  45  LYS  O  ', -0.541, (231.636, 189.372, 229.085)), (' G  33  LEU HD13', ' G  34  ASN  N  ', -0.536, (198.17, 244.539, 230.892)), (' L  33  LEU HD13', ' L  34  ASN  N  ', -0.534, (259.845, 255.334, 230.364)), (' L 124  GLU  N  ', ' L 124  GLU  OE1', -0.533, (290.376, 216.393, 248.626)), (' E 465  GLU  HA ', ' G 155  LEU  HB2', -0.53, (231.948, 266.278, 242.343)), (' C  33  LEU HD13', ' C  34  ASN  N  ', -0.526, (238.548, 197.231, 230.013)), (' A 437  ASN  ND2', ' A 507  PRO  O  ', -0.524, (249.773, 206.985, 263.905)), (' B  35  HIS  NE2', ' B  98  LYS  O  ', -0.523, (240.701, 185.384, 238.456)), (' E 385  THR  OG1', ' H 106  TYR  OH ', -0.521, (262.286, 268.422, 242.593)), (' H  36  TRP  CD2', ' H  81  LEU HD22', -0.521, (273.711, 258.131, 247.891)), (' D 437  ASN  ND2', ' D 507  PRO  O  ', -0.518, (201.79, 230.146, 263.706)), (' L  37  GLN  N  ', ' L  45  LYS  O  ', -0.518, (270.35, 253.22, 229.385)), (' E 335  LEU HD12', ' E 362  VAL  HB ', -0.517, (253.715, 284.66, 248.548)), (' E 437  ASN  ND2', ' E 507  PRO  O  ', -0.517, (245.693, 260.253, 263.493)), (' F 132  LEU  N  ', ' F 147  GLY  O  ', -0.514, (213.767, 286.661, 239.125)), (' C 124  GLU  N  ', ' C 124  GLU  OE1', -0.514, (189.675, 190.528, 248.132)), (' L  37  GLN  O  ', ' L  45  LYS  N  ', -0.514, (272.241, 253.526, 230.554)), (' D 335  LEU HD12', ' D 362  VAL  HB ', -0.514, (176.539, 224.889, 248.998)), (' B 132  LEU  N  ', ' B 147  GLY  O  ', -0.513, (194.614, 188.985, 238.897)), (' C  61  ARG  NH2', ' C  82  ASP  OD1', -0.513, (228.49, 187.568, 217.768)), (' A 335  LEU HD12', ' A 362  VAL  HB ', -0.511, (266.678, 187.684, 249.366)), (' G  37  GLN  O  ', ' G  45  LYS  N  ', -0.51, (193.916, 256.664, 230.964)), (' L  61  ARG  NH2', ' L  82  ASP  OD1', -0.508, (273.108, 251.459, 218.228)), (' F  36  TRP  CD2', ' F  81  LEU HD22', -0.507, (189.175, 255.354, 247.844)), (' B  36  TRP  CD2', ' B  81  LEU HD22', -0.506, (234.266, 183.534, 247.226)), (' F   6  GLU  N  ', ' F   6  GLU  OE1', -0.504, (185.662, 261.376, 241.86)), (' H 132  LEU  N  ', ' H 147  GLY  O  ', -0.503, (288.671, 221.5, 239.34)), (' F  45  LEU  HG ', ' G  87  TYR  CD2', -0.5, (199.547, 253.951, 235.967)), (' A 358  ILE  HB ', ' A 395  VAL  HB ', -0.498, (265.199, 198.458, 246.241)), (' E 382  VAL  CG2', ' H 104  TRP  HB3', -0.496, (255.594, 269.665, 238.349)), (' E 358  ILE  HB ', ' E 395  VAL  HB ', -0.495, (245.9, 277.923, 245.558)), (' C  37  GLN  O  ', ' C  45  LYS  N  ', -0.494, (230.504, 187.205, 230.28)), (' H  35  HIS  NE2', ' H  98  LYS  O  ', -0.493, (268.822, 263.248, 238.837)), (' G  61  ARG  NH2', ' G  82  ASP  OD1', -0.493, (195.271, 258.374, 218.634)), (' D 358  ILE  HB ', ' D 395  VAL  HB ', -0.493, (186.451, 220.887, 246.192)), (' B   6  GLU  N  ', ' B   6  GLU  OE1', -0.492, (230.52, 177.194, 241.67)), (' F  35  HIS  NE2', ' F  98  LYS  O  ', -0.49, (187.717, 248.457, 238.549)), (' A 379  CYS  H  ', ' C  95  LEU HD12', -0.489, (247.349, 197.124, 246.832)), (' F  95  TYR  CZ ', ' G  44  PRO  HD3', -0.488, (194.115, 260.018, 237.493)), (' D 424  LYS  NZ ', ' D 425  LEU  O  ', -0.487, (205.99, 225.225, 240.57)), (' B 124  THR HG22', ' B 155  PRO  HD3', -0.48, (211.881, 181.589, 253.903)), (' H   6  GLU  N  ', ' H   6  GLU  OE1', -0.48, (280.956, 258.333, 242.064)), (' L  18  ARG  HA ', ' L  75  ILE  O  ', -0.479, (264.396, 247.996, 214.57)), (' C  18  ARG  HA ', ' C  75  ILE  O  ', -0.475, (229.861, 196.841, 214.259)), (' G  18  ARG  HA ', ' G  75  ILE  O  ', -0.474, (202.753, 252.252, 215.143)), (' E 424  LYS  NZ ', ' E 425  LEU  O  ', -0.47, (239.371, 258.832, 240.253)), (' H 124  THR HG22', ' H 155  PRO  HD3', -0.469, (286.423, 240.261, 254.187)), (' F 124  THR HG22', ' F 155  PRO  HD3', -0.466, (198.538, 275.429, 254.019)), (' E 363  ALA  HB1', ' E 365  TYR  CZ ', -0.46, (253.625, 277.581, 245.152)), (' E 378  LYS  HA ', ' L  95  LEU HD12', -0.459, (255.532, 262.621, 247.827)), (' H  47  TRP  CD1', ' L  97  LEU HD12', -0.458, (263.901, 258.454, 242.015)), (' D 428  ASP  N  ', ' D 428  ASP  OD1', -0.45, (200.859, 227.243, 235.895)), (' A 363  ALA  HB1', ' A 365  TYR  CZ ', -0.449, (261.308, 191.506, 245.633)), (' B  20  LEU HD12', ' B  81  LEU HD23', -0.448, (231.64, 183.23, 249.039)), (' D 380  TYR  HB3', ' G  92  TYR  CE2', -0.447, (198.356, 233.957, 240.661)), (' D 363  ALA  HB1', ' D 365  TYR  CZ ', -0.447, (182.499, 227.782, 245.616)), (' A 428  ASP  N  ', ' A 428  ASP  OD1', -0.446, (252.522, 207.788, 235.932)), (' E 335  LEU HD11', ' E 364  ASP  HB2', -0.445, (255.495, 282.516, 250.393)), (' H  45  LEU  HB2', ' L  99  PHE  CD1', -0.444, (265.617, 251.553, 238.84)), (' H  20  LEU HD12', ' H  81  LEU HD23', -0.443, (275.215, 256.409, 249.336)), (' F  20  LEU HD12', ' F  81  LEU HD23', -0.443, (190.181, 257.924, 249.268)), (' A 335  LEU HD11', ' A 364  ASP  HB2', -0.441, (264.604, 187.369, 250.744)), (' E 428  ASP  N  ', ' E 428  ASP  OD1', -0.438, (243.605, 262.035, 235.493)), (' E 386  LYS  HD2', ' H 104  TRP  HA ', -0.438, (259.321, 269.857, 237.163)), (' C 151  VAL  O  ', ' C 154  ALA  HB3', -0.436, (196.669, 212.851, 244.004)), (' L 151  VAL  O  ', ' L 154  ALA  HB3', -0.436, (267.302, 211.127, 244.604)), (' H  61  ALA  O  ', ' H  65  LYS  N  ', -0.432, (262.525, 255.585, 253.261)), (' D 335  LEU HD11', ' D 364  ASP  HB2', -0.432, (177.561, 227.321, 250.693)), (' L  33  LEU HD13', ' L  34  ASN  H  ', -0.431, (259.806, 255.269, 230.987)), (' C  33  LEU HD13', ' C  34  ASN  H  ', -0.43, (238.804, 196.963, 230.673)), (' G 151  VAL  O  ', ' G 154  ALA  HB3', -0.429, (233.463, 272.76, 244.698)), (' E 468  ILE HD11', ' G 159  ASN  OD1', -0.427, (225.043, 269.311, 250.666)), (' B  47  TRP  CH2', ' B  49  ALA  HA ', -0.427, (239.82, 190.701, 247.812)), (' B 164  SER  N  ', ' B 205  ASN  OD1', -0.425, (197.294, 175.738, 236.538)), (' G  33  LEU HD13', ' G  34  ASN  H  ', -0.425, (198.327, 244.779, 231.64)), (' E 422  ASN  OD1', ' E 454  ARG  N  ', -0.424, (231.812, 258.467, 254.148)), (' F  47  TRP  CH2', ' F  49  ALA  HA ', -0.424, (192.847, 246.325, 247.8)), (' E 383  SER  N  ', ' H 104  TRP  O  ', -0.423, (257.23, 267.139, 239.328)), (' H 129  VAL  HA ', ' H 149  LEU  O  ', -0.423, (288.256, 226.406, 245.482)), (' E 334  ASN  O  ', ' E 362  VAL  N  ', -0.423, (250.924, 285.755, 246.991)), (' F  45  LEU HD21', ' G  87  TYR  HE2', -0.422, (199.311, 255.848, 236.327)), (' F 129  VAL  HA ', ' F 149  LEU  O  ', -0.422, (209.569, 283.755, 245.371)), (' F  61  ALA  O  ', ' F  65  LYS  N  ', -0.421, (196.994, 246.942, 253.715)), (' B  61  ALA  O  ', ' B  65  LYS  N  ', -0.421, (237.278, 194.581, 253.075)), (' B 134  PRO  HD3', ' B 146  LEU  HB3', -0.42, (191.985, 189.141, 234.322)), (' F 134  PRO  HD3', ' F 146  LEU  HB3', -0.42, (215.612, 288.963, 234.435)), (' F  17  SER  HA ', ' F  83  MET  O  ', -0.42, (192.275, 258.608, 258.25)), (' D 386  LYS  NZ ', ' F 103  LEU  O  ', -0.418, (185.253, 238.371, 236.072)), (' G 135  CYS  HB2', ' G 149  TRP  CH2', -0.418, (222.142, 276.313, 238.502)), (' D 350  VAL HG13', ' D 351  TYR  N  ', -0.416, (206.484, 219.342, 254.381)), (' L 135  CYS  HB2', ' L 149  TRP  CH2', -0.415, (275.631, 219.161, 238.212)), (' A 350  VAL HG13', ' A 351  TYR  N  ', -0.415, (257.135, 216.435, 254.534)), (' G  61  ARG  NE ', ' G  82  ASP  OD2', -0.414, (196.526, 257.11, 217.802)), (' E 398  ASP  O  ', ' E 511  VAL  HA ', -0.414, (243.441, 268.493, 252.044)), (' H  47  TRP  CH2', ' H  49  ALA  HA ', -0.414, (264.338, 259.754, 247.668)), (' D 382  VAL  HA ', ' F 104  TRP  O  ', -0.414, (189.961, 236.187, 238.459)), (' D 398  ASP  O  ', ' D 511  VAL  HA ', -0.414, (195.662, 224.316, 252.62)), (' C  61  ARG  NE ', ' C  82  ASP  OD2', -0.413, (228.876, 189.169, 216.952)), (' B  17  SER  HA ', ' B  83  MET  O  ', -0.413, (229.711, 184.469, 258.145)), (' G   2  ILE HD12', ' G  93  SER  HB2', -0.413, (201.049, 238.91, 241.149)), (' H  17  SER  HA ', ' H  83  MET  O  ', -0.411, (275.364, 253.993, 258.664)), (' C   2  ILE HD12', ' C  93  SER  HB2', -0.411, (242.568, 201.909, 240.402)), (' D 354  ASN  OD1', ' D 355  ARG  N  ', -0.411, (194.828, 215.81, 252.936)), (' A 398  ASP  O  ', ' A 511  VAL  HA ', -0.41, (257.728, 204.627, 252.611)), (' C 135  CYS  HB2', ' C 149  TRP  CH2', -0.41, (199.31, 201.76, 238.125)), (' B 129  VAL  HA ', ' B 149  LEU  O  ', -0.41, (199.176, 186.532, 245.4)), (' F  45  LEU HD11', ' G  87  TYR  HD2', -0.41, (198.338, 253.678, 235.533)), (' L  61  ARG  NE ', ' L  82  ASP  OD2', -0.409, (271.579, 250.946, 217.442)), (' F  33  ASP  HB3', ' F  51  ILE  O  ', -0.408, (184.44, 245.09, 244.079)), (' E 354  ASN  OD1', ' E 355  ARG  N  ', -0.408, (236.699, 273.085, 252.155)), (' F  38  ARG  HB3', ' F  94  TYR  CD2', -0.407, (194.906, 256.662, 246.801)), (' E 438  SER  OG ', ' E 442  ASP  OD2', -0.407, (242.999, 264.909, 264.1)), (' B  33  ASP  HB3', ' B  51  ILE  O  ', -0.407, (245.142, 184.211, 244.305)), (' E 350  VAL HG13', ' E 351  TYR  N  ', -0.406, (234.059, 261.452, 254.209)), (' F 106  TYR  CD2', ' G  94  THR HG23', -0.406, (190.959, 241.419, 241.76)), (' L   2  ILE HD12', ' L  93  SER  HB2', -0.406, (253.675, 256.195, 240.661)), (' G 137  LEU  N  ', ' G 137  LEU HD12', -0.405, (218.581, 275.433, 232.591)), (' C 148  GLN  CG ', ' C 155  LEU HD12', -0.405, (202.362, 212.17, 237.966)), (' L 137  LEU  N  ', ' L 137  LEU HD12', -0.403, (276.483, 222.846, 232.292)), (' G 148  GLN  CG ', ' G 155  LEU HD12', -0.403, (229.761, 268.528, 238.729)), (' H  38  ARG  HB3', ' H  94  TYR  CD2', -0.402, (272.135, 252.765, 246.843)), (' A 438  SER  OG ', ' A 442  ASP  OD2', -0.402, (255.212, 206.866, 264.524)), (' A 354  ASN  OD1', ' A 355  ARG  N  ', -0.402, (265.368, 208.076, 252.63)), (' H 134  PRO  HD3', ' H 146  LEU  HB3', -0.402, (289.955, 218.698, 234.419)), (' F  45  LEU  HB2', ' G  99  PHE  CD1', -0.401, (199.178, 251.256, 239.422)), (' D 334  ASN  O  ', ' D 362  VAL  N  ', -0.4, (176.553, 221.757, 247.262))]
data['omega'] = [('B', ' 155 ', 'PRO', None, (211.51000000000005, 182.95, 251.80299999999994)), ('B', ' 157 ', 'PRO', None, (212.78300000000007, 181.01, 245.96899999999994)), ('C', '   8 ', 'PRO', None, (226.933, 204.12, 225.29699999999994)), ('C', ' 142 ', 'PRO', None, (210.966, 201.509, 222.536)), ('F', ' 155 ', 'PRO', None, (200.01500000000007, 275.07200000000006, 251.98599999999993)), ('F', ' 157 ', 'PRO', None, (197.73700000000005, 274.921, 246.138)), ('G', '   8 ', 'PRO', None, (210.4450000000001, 251.3, 226.19299999999996)), ('G', ' 142 ', 'PRO', None, (216.2, 266.4090000000001, 223.36599999999999)), ('H', ' 155 ', 'PRO', None, (285.47, 239.032, 252.11)), ('H', ' 157 ', 'PRO', None, (286.546, 241.119, 246.288)), ('L', '   8 ', 'PRO', None, (259.646, 241.787, 225.81799999999996)), ('L', ' 142 ', 'PRO', None, (269.878, 229.25900000000001, 223.033))]
data['cablam'] = [('A', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (256.0, 238.7, 259.9)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (253.4, 240.1, 257.6)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (266.3, 198.1, 229.3)), ('A', '484', 'GLU', 'check CA trace', ' \nS--BT', (259.2, 236.8, 259.1)), ('B', '99', 'ASP', ' beta sheet', ' \nEE---', (243.7, 184.2, 238.2)), ('B', '197', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nT-SSS', (186.2, 186.2, 229.8)), ('B', '156', 'GLU', 'check CA trace', 'bend\nBSS--', (212.9, 183.2, 247.2)), ('C', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (241.1, 207.4, 229.9)), ('C', '50', 'ALA', 'check CA trace', 'turn\nEETTT', (244.1, 194.7, 227.9)), ('D', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (226.2, 208.9, 259.6)), ('D', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (228.7, 210.5, 257.3)), ('D', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (185.6, 220.2, 229.3)), ('D', '484', 'GLU', 'check CA trace', ' \nS--BT', (222.9, 207.1, 258.8)), ('E', '485', 'GLY', 'check CA trace,carbonyls, peptide', 'beta bridge\n--BTT', (215.2, 249.6, 259.4)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (215.2, 246.6, 257.1)), ('E', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (245.2, 278.9, 228.9)), ('E', '484', 'GLU', 'check CA trace', ' \nS--BT', (215.2, 253.3, 258.6)), ('F', '99', 'ASP', ' beta sheet', ' \nEE---', (185.2, 246.5, 238.3)), ('F', '197', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nT-SSS', (215.6, 295.3, 230.0)), ('F', '156', 'GLU', 'check CA trace', 'bend\nBSS--', (199.5, 273.7, 247.3)), ('G', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (206.1, 237.4, 230.9)), ('G', '50', 'ALA', 'check CA trace', 'turn\nEETTT', (193.7, 241.2, 228.9)), ('H', '99', 'ASP', ' beta sheet', ' \nEE---', (268.3, 266.3, 238.4)), ('H', '197', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nT-SSS', (295.5, 215.6, 230.1)), ('H', '156', 'GLU', 'check CA trace', 'bend\nBSS--', (284.6, 240.1, 247.5)), ('L', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (249.8, 252.5, 230.4)), ('L', '50', 'ALA', 'check CA trace', 'turn\nEETTT', (259.2, 261.4, 228.4))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11173/6zdg/Model_validation_4/validation_cootdata/molprobity_probe6zdg_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

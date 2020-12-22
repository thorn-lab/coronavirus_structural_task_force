
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
data['rota'] = [('C', '  38 ', 'GLU', 0.2962090014524466, (97.402, 88.98800000000001, 114.354))]
data['clusters'] = [('A', '128', 1, 'side-chain clash', (129.351, 111.77, 120.842)), ('A', '132', 1, 'side-chain clash', (129.351, 111.77, 120.842)), ('A', '133', 1, 'smoc Outlier', (126.069, 105.43400000000001, 122.895)), ('A', '148', 1, 'backbone clash', (122.145, 104.71, 127.834)), ('A', '149', 1, 'side-chain clash', (123.066, 106.008, 133.398)), ('A', '156', 1, 'backbone clash', (122.145, 104.71, 127.834)), ('A', '158', 1, 'side-chain clash', (116.901, 101.498, 127.202)), ('A', '185', 1, 'backbone clash', (111.776, 101.972, 129.122)), ('A', '188', 1, 'smoc Outlier', (107.21100000000001, 103.74400000000001, 127.74000000000001)), ('A', '189', 1, 'backbone clash', (111.776, 101.972, 129.122)), ('A', '191', 1, 'side-chain clash', (116.901, 101.498, 127.202)), ('A', '201', 1, 'side-chain clash', (123.066, 106.008, 133.398)), ('A', '204', 1, 'side-chain clash', (127.2, 110.965, 124.628)), ('A', '147', 2, 'side-chain clash', (117.881, 111.123, 130.865)), ('A', '167', 2, 'side-chain clash', (117.881, 111.123, 130.865)), ('A', '212', 2, 'side-chain clash', (119.775, 111.799, 136.398)), ('A', '233', 2, 'side-chain clash', (119.775, 111.799, 136.398)), ('A', '109', 3, 'smoc Outlier', (117.88499999999999, 119.115, 90.988)), ('A', '112', 3, 'side-chain clash', (116.752, 114.715, 93.153)), ('A', '75', 3, 'side-chain clash', (112.162, 112.243, 95.783)), ('A', '89', 3, 'side-chain clash', (116.752, 114.715, 93.153)), ('A', '216', 4, 'side-chain clash\nsmoc Outlier', (113.511, 109.175, 146.22)), ('A', '218', 4, 'side-chain clash', (110.444, 105.824, 142.556)), ('A', '230', 4, 'side-chain clash', (110.444, 105.824, 142.556)), ('A', '66', 5, 'cablam Outlier', (106.5, 98.5, 118.5)), ('A', '68', 5, 'side-chain clash', (112.831, 97.667, 117.714)), ('A', '71', 5, 'side-chain clash', (112.831, 97.667, 117.714)), ('A', '116', 6, 'smoc Outlier', (120.40700000000001, 114.61999999999999, 100.083)), ('A', '172', 6, 'side-chain clash\nbackbone clash', (117.098, 119.428, 103.202)), ('A', '182', 6, 'side-chain clash\nbackbone clash', (117.098, 119.428, 103.202)), ('A', '173', 7, 'Dihedral angle:CA:CB:CG:OD1', (111.208, 93.15499999999999, 138.346)), ('A', '181', 7, 'smoc Outlier', (110.049, 91.081, 132.335)), ('A', '183', 7, 'smoc Outlier', (113.26100000000001, 96.034, 132.626)), ('A', '102', 8, 'smoc Outlier', (117.531, 120.184, 81.902)), ('A', '103', 8, 'side-chain clash', (119.468, 123.132, 83.63)), ('A', '106', 8, 'side-chain clash', (119.468, 123.132, 83.63)), ('A', '42', 9, 'side-chain clash', (101.245, 98.475, 102.739)), ('A', '45', 9, 'side-chain clash', (101.245, 98.475, 102.739)), ('A', '401', 10, 'backbone clash', (110.782, 107.102, 102.379)), ('A', '57', 10, 'backbone clash', (110.782, 107.102, 102.379)), ('A', '145', 11, 'side-chain clash', (105.798, 105.458, 95.908)), ('A', '205', 11, 'side-chain clash', (105.798, 105.458, 95.908)), ('B', '148', 1, 'backbone clash', (95.409, 113.763, 127.642)), ('B', '149', 1, 'side-chain clash', (94.787, 112.328, 133.163)), ('B', '156', 1, 'backbone clash\nside-chain clash', (98.75, 119.161, 129.132)), ('B', '172', 1, 'side-chain clash', (105.187, 123.914, 136.415)), ('B', '173', 1, 'Dihedral angle:CA:CB:CG:OD1', (106.869, 124.973, 138.315)), ('B', '181', 1, 'smoc Outlier', (108.079, 127.133, 132.38800000000003)), ('B', '182', 1, 'side-chain clash', (105.187, 123.914, 136.415)), ('B', '183', 1, 'smoc Outlier', (104.82499999999999, 122.07, 132.61599999999999)), ('B', '185', 1, 'backbone clash', (106.463, 116.028, 129.14)), ('B', '189', 1, 'backbone clash', (106.463, 116.028, 129.14)), ('B', '191', 1, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (102.65899999999999, 119.925, 127.956)), ('B', '201', 1, 'side-chain clash', (94.787, 112.328, 133.163)), ('B', '128', 2, 'side-chain clash', (89.087, 105.682, 120.218)), ('B', '132', 2, 'side-chain clash', (89.087, 105.682, 120.218)), ('B', '145', 2, 'smoc Outlier', (99.962, 105.796, 122.77499999999999)), ('B', '160', 2, 'smoc Outlier', (103.85199999999999, 107.641, 125.232)), ('B', '204', 2, 'side-chain clash', (90.653, 107.159, 124.264)), ('B', '205', 2, 'side-chain clash', (95.753, 101.192, 122.692)), ('B', '208', 2, 'side-chain clash', (95.753, 101.192, 122.692)), ('B', '212', 2, 'side-chain clash\nbackbone clash', (90.584, 102.257, 119.518)), ('B', '233', 2, 'side-chain clash\nbackbone clash', (90.584, 102.257, 119.518)), ('B', '216', 3, 'side-chain clash', (104.597, 108.907, 146.205)), ('B', '218', 3, 'side-chain clash', (107.653, 112.379, 142.556)), ('B', '223', 3, 'smoc Outlier', (113.147, 113.258, 146.52800000000002)), ('B', '230', 3, 'side-chain clash', (107.653, 112.379, 142.556)), ('B', '112', 4, 'side-chain clash', (101.42, 103.313, 93.21)), ('B', '85', 4, 'side-chain clash', (105.798, 105.458, 95.908)), ('B', '89', 4, 'side-chain clash\nsmoc Outlier', (101.42, 103.313, 93.21)), ('B', '66', 5, 'cablam Outlier', (111.8, 119.6, 118.5)), ('B', '68', 5, 'side-chain clash', (105.52, 120.048, 117.868)), ('B', '71', 5, 'side-chain clash', (105.52, 120.048, 117.868)), ('B', '49', 6, 'smoc Outlier', (106.29700000000001, 115.095, 89.509)), ('B', '50', 6, 'smoc Outlier', (109.389, 113.021, 90.303)), ('B', '54', 6, 'side-chain clash', (112.162, 112.243, 95.783)), ('B', '301', 7, 'side-chain clash', (121.078, 119.548, 108.742)), ('B', '62', 7, 'side-chain clash', (117.098, 119.428, 103.202)), ('B', '130', 8, 'side-chain clash', (95.042, 114.31, 114.822)), ('B', '139', 8, 'side-chain clash', (95.042, 114.31, 114.822)), ('B', '42', 9, 'side-chain clash', (101.809, 116.066, 80.623)), ('B', '45', 9, 'side-chain clash', (101.809, 116.066, 80.623)), ('B', '402', 10, 'backbone clash', (107.325, 110.943, 102.357)), ('B', '57', 10, 'backbone clash\nsmoc Outlier', (107.325, 110.943, 102.357)), ('B', '147', 11, 'side-chain clash', (99.709, 107.126, 130.992)), ('B', '167', 11, 'side-chain clash', (99.709, 107.126, 130.992)), ('B', '103', 12, 'side-chain clash', (98.675, 94.67, 83.46)), ('B', '106', 12, 'side-chain clash', (98.675, 94.67, 83.46)), ('C', '41', 1, 'side-chain clash\nsmoc Outlier', (104.521, 86.284, 115.285)), ('C', '44', 1, 'side-chain clash', (105.68, 87.044, 115.431)), ('C', '45', 1, 'side-chain clash', (105.68, 87.044, 115.431)), ('C', '48', 1, 'side-chain clash\nsmoc Outlier', (110.992, 86.286, 115.231)), ('C', '51', 1, 'side-chain clash\nsmoc Outlier', (110.992, 86.286, 115.231)), ('C', '36', 2, 'smoc Outlier', (96.348, 94.18199999999999, 112.68199999999999)), ('C', '38', 2, 'Rotamer\nDihedral angle:CB:CG:CD:OE1', (97.402, 88.988, 114.354)), ('D', '45', 1, 'side-chain clash', (111.514, 133.896, 115.161)), ('D', '48', 1, 'side-chain clash\nsmoc Outlier', (107.413, 131.828, 115.176)), ('D', '51', 1, 'side-chain clash', (107.413, 131.828, 115.176)), ('D', '29', 2, 'side-chain clash', (127.738, 115.11, 119.333)), ('D', '38', 2, 'Dihedral angle:CB:CG:CD:OE1', (120.664, 129.134, 114.342))]
data['probe'] = [(' A  89  THR HG21', ' A 112  VAL HG11', -0.652, (116.752, 114.715, 93.153)), (' B  57  GLN  NE2', ' B 402  HOH  O  ', -0.63, (107.325, 110.943, 102.357)), (' B  89  THR HG21', ' B 112  VAL HG11', -0.622, (101.42, 103.313, 93.21)), (' A  57  GLN  NE2', ' A 401  HOH  O  ', -0.617, (110.782, 107.102, 102.379)), (' B 103  ALA  HA ', ' B 106  LEU  HG ', -0.61, (98.675, 94.67, 83.46)), (' A 172  GLY  O  ', ' A 182  HIS  HA ', -0.597, (111.592, 94.312, 135.561)), (' A 206  TYR  O  ', ' D  29  ARG  NH1', -0.59, (127.738, 115.11, 119.333)), (' A 148  CYS  HA ', ' A 156  TYR  O  ', -0.577, (122.145, 104.71, 127.834)), (' B 148  CYS  HA ', ' B 156  TYR  O  ', -0.576, (95.409, 113.763, 127.642)), (' A 212  TYR  HB3', ' A 233  TYR  HB3', -0.573, (119.775, 111.799, 136.398)), (' C  41  ASP  O  ', ' C  45  LYS  NZ ', -0.569, (104.521, 86.284, 115.285)), (' B 172  GLY  O  ', ' B 182  HIS  HA ', -0.563, (106.061, 124.126, 135.259)), (' B 212  TYR  HB3', ' B 233  TYR  HB3', -0.55, (98.556, 106.171, 136.236)), (' B 206  TYR  O  ', ' C  29  ARG  NH1', -0.545, (90.584, 102.257, 119.518)), (' B  42  PRO  HG2', ' B  45  TRP  CD1', -0.525, (101.867, 116.764, 80.447)), (' A 185  GLN  HA ', ' A 189  TYR  O  ', -0.52, (111.776, 101.972, 129.122)), (' A 172  GLY  O  ', ' A 182  HIS  ND1', -0.518, (112.908, 94.179, 136.375)), (' B 172  GLY  O  ', ' B 182  HIS  ND1', -0.517, (105.187, 123.914, 136.415)), (' A 115  LEU HD22', ' B  62  ILE HD11', -0.501, (117.098, 119.428, 103.202)), (' A 147  LEU HD13', ' A 167  ILE HD13', -0.5, (117.881, 111.123, 130.865)), (' A 158  ILE HG12', ' A 191  GLU  HG3', -0.5, (116.901, 101.498, 127.202)), (' A  42  PRO  HG2', ' A  45  TRP  CD1', -0.499, (116.272, 101.772, 80.553)), (' B 132  LYS  HD3', ' B 204  HIS  CE1', -0.496, (90.653, 107.159, 124.264)), (' B 238  ASP  N  ', ' B 238  ASP  OD1', -0.492, (91.491, 95.708, 134.61)), (' A 132  LYS  HD3', ' A 204  HIS  CE1', -0.491, (127.2, 110.965, 124.628)), (' B 156  TYR  HD2', ' B 191  GLU  HG2', -0.483, (98.845, 118.916, 129.122)), (' C  51  ARG  HA ', ' C  54  MET  HE3', -0.481, (116.335, 88.127, 110.181)), (' A 128  TRP  CH2', ' A 132  LYS  HE3', -0.48, (129.351, 111.77, 120.842)), (' B 185  GLN  HA ', ' B 189  TYR  O  ', -0.475, (106.463, 116.028, 129.14)), (' A  68  ARG  HA ', ' A  71  LEU HD12', -0.47, (112.831, 97.667, 117.714)), (' B 216  SER  OG ', ' B 218  GLN  OE1', -0.468, (104.597, 108.907, 146.205)), (' B 136  LYS  HB2', ' B 136  LYS  HE2', -0.468, (96.223, 120.335, 118.279)), (' B 128  TRP  CH2', ' B 132  LYS  HE3', -0.467, (89.087, 105.682, 120.218)), (' A 216  SER  OG ', ' A 218  GLN  OE1', -0.461, (113.511, 109.175, 146.22)), (' D  45  LYS  HA ', ' D  45  LYS  HD3', -0.461, (111.514, 133.896, 115.161)), (' A 103  ALA  HA ', ' A 106  LEU HD23', -0.458, (119.468, 123.132, 83.63)), (' B  42  PRO  HG2', ' B  45  TRP  HD1', -0.458, (101.809, 116.066, 80.623)), (' A 218  GLN  HB2', ' A 230  PHE  HB2', -0.448, (110.444, 105.824, 142.556)), (' C  48  GLU  OE1', ' C  51  ARG  NH2', -0.447, (110.992, 86.286, 115.231)), (' B 130  CYS  SG ', ' B 139  LEU  HG ', -0.444, (95.042, 114.31, 114.822)), (' A  42  PRO  HG2', ' A  45  TRP  HD1', -0.442, (116.092, 102.009, 80.642)), (' B 218  GLN  HB2', ' B 230  PHE  HB2', -0.44, (107.653, 112.379, 142.556)), (' C  44  GLU  HB3', ' C  45  LYS  HZ2', -0.439, (105.68, 87.044, 115.431)), (' B 301  PEE  H14', ' B 301  PEE  H49', -0.438, (121.078, 119.548, 108.742)), (' B 205  SER  HG ', ' B 208  THR  HG1', -0.437, (95.753, 101.192, 122.692)), (' A  62  ILE HD11', ' B 115  LEU HD22', -0.437, (101.245, 98.475, 102.739)), (' B  68  ARG  HA ', ' B  71  LEU HD12', -0.435, (105.52, 120.048, 117.868)), (' B 147  LEU HD13', ' B 167  ILE HD13', -0.433, (99.709, 107.126, 130.992)), (' B 156  TYR  CD2', ' B 191  GLU  HG2', -0.433, (98.75, 119.161, 129.132)), (' D  48  GLU  OE1', ' D  51  ARG  NH2', -0.429, (107.413, 131.828, 115.176)), (' A 145  TYR  CD2', ' A 205  SER  HB3', -0.426, (120.42, 115.361, 122.592)), (' A  54  ALA  HA ', ' B  85  LEU HD11', -0.425, (105.798, 105.458, 95.908)), (' A  75  LYS  HA ', ' A  75  LYS  HD3', -0.421, (114.083, 103.169, 108.919)), (' A  85  LEU HD11', ' B  54  ALA  HA ', -0.413, (112.162, 112.243, 95.783)), (' B 149  TRP  HB3', ' B 201  VAL HG12', -0.406, (94.787, 112.328, 133.163)), (' A 149  TRP  HB3', ' A 201  VAL HG12', -0.401, (123.066, 106.008, 133.398))]
data['cablam'] = [('A', '66', 'LYS', 'check CA trace,carbonyls, peptide', ' \n---SH', (106.5, 98.5, 118.5)), ('B', '66', 'LYS', 'check CA trace,carbonyls, peptide', ' \n---SH', (111.8, 119.6, 118.5))]
data['smoc'] = [('A', 102, u'GLU', 0.6537497359767032, (117.531, 120.184, 81.902)), ('A', 109, u'TYR', 0.6237623241699312, (117.88499999999999, 119.115, 90.988)), ('A', 116, u'GLN', 0.599549295439037, (120.40700000000001, 114.61999999999999, 100.083)), ('A', 126, u'ARG', 0.6236535848930589, (123.455, 109.009, 113.557)), ('A', 133, u'CYS', 0.6422160699398757, (126.069, 105.43400000000001, 122.895)), ('A', 142, u'ASP', 0.6265724761781191, (114.15799999999999, 108.697, 115.779)), ('A', 181, u'GLU', 0.6309072646593505, (110.049, 91.081, 132.335)), ('A', 183, u'ASP', 0.599475764149918, (113.26100000000001, 96.034, 132.626)), ('A', 188, u'GLY', 0.5894574781130856, (107.21100000000001, 103.74400000000001, 127.74000000000001)), ('A', 210, u'ASP', 0.6214798142359359, (124.054, 116.39, 129.812)), ('A', 216, u'SER', 0.6762150774754215, (116.44000000000001, 109.453, 145.117)), ('A', 238, u'ASP', 0.6876735177649472, (128.192, 123.418, 136.272)), ('B', 49, u'GLY', 0.5801308741698257, (106.29700000000001, 115.095, 89.509)), ('B', 50, u'VAL', 0.5820885466924737, (109.389, 113.021, 90.303)), ('B', 57, u'GLN', 0.6029122804312383, (110.927, 113.809, 100.393)), ('B', 89, u'THR', 0.6174568553476327, (102.081, 106.384, 90.70700000000001)), ('B', 142, u'ASP', 0.617115107573781, (103.94300000000001, 109.395, 115.785)), ('B', 145, u'TYR', 0.6498345656382742, (99.962, 105.796, 122.77499999999999)), ('B', 160, u'TYR', 0.6391718373598337, (103.85199999999999, 107.641, 125.232)), ('B', 181, u'GLU', 0.5535660851778098, (108.079, 127.133, 132.38800000000003)), ('B', 183, u'ASP', 0.5817645899110436, (104.82499999999999, 122.07, 132.61599999999999)), ('B', 223, u'THR', 0.666664018162975, (113.147, 113.258, 146.52800000000002)), ('B', 238, u'ASP', 0.6982793104390997, (90.083, 94.886, 135.54)), ('C', 25, u'PHE', 0.6927699010329931, (82.615, 103.229, 113.3)), ('C', 36, u'THR', 0.7411497976845559, (96.348, 94.18199999999999, 112.68199999999999)), ('C', 41, u'ASP', 0.6924497425549333, (102.229, 88.345, 115.115)), ('C', 48, u'GLU', 0.7012819569359775, (111.70400000000001, 84.485, 113.085)), ('C', 51, u'ARG', 0.6890490862539076, (115.70400000000001, 87.38799999999999, 111.456)), ('D', 48, u'GLU', 0.7257858068914769, (106.283, 133.782, 112.995))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22898/7kjr/Model_validation_1/validation_cootdata/molprobity_probe7kjr_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

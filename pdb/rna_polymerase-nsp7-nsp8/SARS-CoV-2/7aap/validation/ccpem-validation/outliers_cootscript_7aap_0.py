
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
data['jpred'] = []
data['clusters'] = [('A', '388', 1, 'side-chain clash', (112.721, 119.476, 125.697)), ('A', '395', 1, 'smoc Outlier', (115.458, 113.265, 114.99400000000001)), ('A', '396', 1, 'side-chain clash', (112.795, 117.409, 113.337)), ('A', '397', 1, 'side-chain clash', (113.947, 117.963, 120.845)), ('A', '398', 1, 'smoc Outlier', (112.106, 121.661, 118.44000000000001)), ('A', '400', 1, 'side-chain clash', (112.721, 119.476, 125.697)), ('A', '631', 1, 'side-chain clash', (103.293, 110.497, 104.087)), ('A', '658', 1, 'smoc Outlier', (97.73400000000001, 116.295, 104.96400000000001)), ('A', '659', 1, 'smoc Outlier', (101.478, 116.67599999999999, 104.38)), ('A', '663', 1, 'side-chain clash', (103.293, 110.497, 104.087)), ('A', '672', 1, 'side-chain clash', (111.516, 117.616, 123.325)), ('A', '675', 1, 'side-chain clash', (112.795, 117.409, 113.337)), ('A', '677', 1, 'cablam Outlier', (111.0, 112.9, 109.1)), ('A', '678', 1, 'cablam CA Geom Outlier', (108.2, 111.2, 107.2)), ('A', '679', 1, 'smoc Outlier', (106.40400000000001, 107.867, 106.87599999999999)), ('A', '377', 2, 'smoc Outlier', (98.91900000000001, 125.366, 116.069)), ('A', '378', 2, 'side-chain clash', (101.978, 122.695, 118.615)), ('A', '504', 2, 'cablam Outlier', (97.3, 117.3, 122.0)), ('A', '539', 2, 'side-chain clash', (101.978, 122.695, 118.615)), ('A', '540', 2, 'smoc Outlier', (100.709, 114.381, 116.91600000000001)), ('A', '666', 2, 'smoc Outlier', (105.26400000000001, 117.867, 115.054)), ('A', '667', 2, 'smoc Outlier', (105.508, 114.883, 117.40100000000001)), ('A', '668', 2, 'smoc Outlier', (104.49000000000001, 115.209, 121.062)), ('A', '100', 3, 'side-chain clash\nsmoc Outlier', (143.992, 108.07, 71.195)), ('A', '116', 3, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (138.425, 105.15799999999999, 72.639)), ('A', '117', 3, 'side-chain clash', (143.992, 108.07, 71.195)), ('A', '118', 3, 'smoc Outlier', (141.04299999999998, 105.865, 78.94800000000001)), ('A', '119', 3, 'backbone clash', (139.6, 101.813, 80.434)), ('A', '217', 3, 'side-chain clash', (133.99, 106.128, 73.15)), ('A', '69', 3, 'backbone clash', (139.6, 101.813, 80.434)), ('A', '778', 4, 'smoc Outlier', (108.226, 87.721, 91.22)), ('A', '782', 4, 'smoc Outlier', (109.94100000000002, 92.94400000000002, 94.65799999999999)), ('A', '784', 4, 'smoc Outlier', (114.94000000000001, 94.95100000000001, 93.924)), ('A', '785', 4, 'smoc Outlier', (112.12899999999999, 97.526, 93.91400000000002)), ('A', '789', 4, 'smoc Outlier', (112.408, 102.80799999999999, 96.02499999999999)), ('A', '790', 4, 'smoc Outlier', (111.866, 101.975, 99.71700000000001)), ('A', '1003', 5, 'smoc Outlier', (104.38199999999999, 95.12899999999999, 107.922)), ('A', '623', 5, 'side-chain clash', (105.754, 101.233, 109.261)), ('A', '758', 5, 'side-chain clash\nbackbone clash', (95.274, 95.955, 104.494)), ('A', '759', 5, 'side-chain clash\nbackbone clash\ncablam Outlier\nsmoc Outlier', (95.274, 95.955, 104.494)), ('A', '760', 5, 'cablam Outlier', (99.9, 95.9, 104.1)), ('A', '605', 6, 'smoc Outlier', (92.003, 86.227, 93.49700000000001)), ('A', '607', 6, 'cablam Outlier', (90.1, 84.5, 88.8)), ('A', '754', 6, 'smoc Outlier', (95.648, 89.161, 90.079)), ('A', '755', 6, 'side-chain clash', (99.087, 90.352, 93.64)), ('A', '764', 6, 'side-chain clash', (99.087, 90.352, 93.64)), ('A', '507', 7, 'side-chain clash', (87.767, 89.596, 124.693)), ('A', '541', 7, 'side-chain clash', (87.767, 89.596, 124.693)), ('A', '614', 7, 'side-chain clash', (89.455, 92.157, 126.878)), ('A', '802', 7, 'side-chain clash\nsmoc Outlier', (89.455, 92.157, 126.878)), ('A', '858', 7, 'Dihedral angle:CD:NE:CZ:NH1', (85.392, 87.482, 125.935)), ('A', '340', 8, 'smoc Outlier', (100.49400000000001, 136.282, 119.255)), ('A', '60', 8, 'side-chain clash', (99.14, 135.278, 123.904)), ('A', '61', 8, 'side-chain clash', (99.14, 135.278, 123.904)), ('A', '613', 8, 'side-chain clash', (104.212, 133.195, 119.323)), ('A', '803', 8, 'side-chain clash', (104.212, 133.195, 119.323)), ('A', '916', 9, 'side-chain clash\ncablam Outlier', (75.681, 74.696, 121.235)), ('A', '917', 9, 'side-chain clash\nbackbone clash\ncablam Outlier\nsmoc Outlier', (77.202, 73.928, 117.955)), ('A', '919', 9, 'backbone clash', (77.202, 73.928, 117.955)), ('A', '922', 9, 'smoc Outlier', (79.492, 76.233, 112.519)), ('A', '924', 9, 'smoc Outlier', (79.70700000000001, 81.536, 111.618)), ('A', '833', 10, 'smoc Outlier', (98.034, 80.16499999999999, 115.30199999999999)), ('A', '836', 10, 'Dihedral angle:CD:NE:CZ:NH1', (97.93400000000001, 83.166, 119.62199999999999)), ('A', '837', 10, 'side-chain clash', (93.298, 81.306, 123.891)), ('A', '840', 10, 'smoc Outlier', (94.908, 85.667, 124.609)), ('A', '884', 10, 'side-chain clash', (93.298, 81.306, 123.891)), ('A', '236', 11, 'smoc Outlier', (115.576, 108.3, 79.648)), ('A', '238', 11, 'side-chain clash', (116.316, 110.859, 86.964)), ('A', '239', 11, 'smoc Outlier', (114.84400000000001, 109.599, 84.827)), ('A', '242', 11, 'side-chain clash', (116.316, 110.859, 86.964)), ('A', '465', 11, 'smoc Outlier', (112.021, 107.624, 88.769)), ('A', '717', 12, 'smoc Outlier', (105.224, 85.868, 72.426)), ('A', '718', 12, 'smoc Outlier', (104.556, 88.55499999999999, 69.82199999999999)), ('A', '720', 12, 'side-chain clash', (106.459, 88.452, 78.452)), ('A', '775', 12, 'side-chain clash\nsmoc Outlier', (106.459, 88.452, 78.452)), ('A', '726', 13, 'smoc Outlier', (105.059, 100.166, 74.02199999999999)), ('A', '730', 13, 'smoc Outlier', (104.94100000000002, 105.31, 77.257)), ('A', '734', 13, 'smoc Outlier', (105.473, 110.242, 75.71900000000001)), ('A', '736', 13, 'smoc Outlier', (100.98700000000001, 112.661, 77.989)), ('A', '469', 14, 'side-chain clash', (103.079, 107.242, 88.974)), ('A', '473', 14, 'side-chain clash', (103.079, 107.242, 88.974)), ('A', '474', 14, 'smoc Outlier', (97.823, 105.838, 85.98700000000001)), ('A', '475', 14, 'smoc Outlier', (97.74400000000001, 102.05799999999999, 86.44600000000001)), ('A', '161', 15, 'smoc Outlier', (124.04700000000001, 91.72, 105.99900000000001)), ('A', '164', 15, 'side-chain clash\nsmoc Outlier', (121.243, 94.696, 107.781)), ('A', '167', 15, 'side-chain clash', (121.243, 94.696, 107.781)), ('A', '811', 16, 'side-chain clash\nsmoc Outlier', (99.603, 85.651, 109.78)), ('A', '812', 16, 'smoc Outlier', (97.356, 86.475, 105.192)), ('A', '814', 16, 'side-chain clash', (99.603, 85.651, 109.78)), ('A', '927', 17, 'smoc Outlier', (78.326, 80.17099999999999, 103.113)), ('A', '928', 17, 'smoc Outlier', (74.79700000000001, 81.384, 103.861)), ('A', '929', 17, 'smoc Outlier', (74.46600000000001, 84.315, 106.251)), ('A', '1001', 18, 'smoc Outlier', (104.68799999999999, 121.853, 88.722)), ('A', '298', 18, 'smoc Outlier', (104.05499999999999, 123.309, 94.02499999999999)), ('A', '301', 18, 'smoc Outlier', (101.51100000000001, 123.435, 89.512)), ('A', '522', 19, 'smoc Outlier', (78.049, 125.3, 110.387)), ('A', '525', 19, 'smoc Outlier', (81.777, 123.22, 107.56400000000001)), ('A', '529', 19, 'smoc Outlier', (86.35199999999999, 125.426, 104.04100000000001)), ('A', '506', 20, 'side-chain clash', (89.982, 119.272, 122.467)), ('A', '512', 20, 'smoc Outlier', (86.301, 113.801, 120.84)), ('A', '515', 20, 'side-chain clash', (89.982, 119.272, 122.467)), ('A', '576', 21, 'side-chain clash', (90.216, 104.716, 102.83)), ('A', '686', 21, 'side-chain clash', (90.523, 107.599, 104.659)), ('A', '689', 21, 'side-chain clash', (90.216, 104.716, 102.83)), ('A', '211', 22, 'backbone clash\nsmoc Outlier', (132.55, 105.546, 82.862)), ('A', '212', 22, 'backbone clash\nsmoc Outlier', (132.55, 105.546, 82.862)), ('A', '24', 23, 'smoc Outlier', (143.967, 86.04400000000001, 72.67199999999998)), ('A', '25', 23, 'smoc Outlier', (144.292, 86.745, 68.94600000000001)), ('A', '284', 24, 'smoc Outlier', (119.752, 124.857, 85.93)), ('A', '285', 24, 'Dihedral angle:CD:NE:CZ:NH1', (123.14, 123.482, 87.006)), ('A', '56', 25, 'side-chain clash', (143.321, 99.123, 74.975)), ('A', '70', 25, 'side-chain clash', (143.321, 99.123, 74.975)), ('A', '358', 26, 'side-chain clash', (90.449, 133.688, 102.187)), ('A', '533', 26, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (92.66499999999999, 127.96600000000001, 101.508)), ('A', '308', 27, 'smoc Outlier', (104.432, 114.692, 91.425)), ('A', '312', 27, 'smoc Outlier', (110.332, 114.91600000000001, 93.035)), ('A', '889', 28, 'smoc Outlier', (80.864, 75.254, 130.969)), ('A', '893', 28, 'smoc Outlier', (78.637, 76.37899999999999, 136.24299999999997)), ('A', '88', 29, 'side-chain clash', (136.883, 116.816, 65.371)), ('A', '91', 29, 'side-chain clash', (136.883, 116.816, 65.371)), ('A', '103', 30, 'side-chain clash', (139.018, 101.486, 59.047)), ('A', '112', 30, 'side-chain clash', (139.018, 101.486, 59.047)), ('A', '83', 31, 'Dihedral angle:CB:CG:CD:OE1', (131.56, 109.169, 63.561)), ('A', '84', 31, 'smoc Outlier', (134.252, 111.319, 61.92)), ('A', '530', 32, 'side-chain clash', (91.817, 126.077, 108.888)), ('A', '536', 32, 'side-chain clash', (91.817, 126.077, 108.888)), ('A', '444', 33, 'side-chain clash', (86.489, 95.711, 106.607)), ('A', '448', 33, 'side-chain clash', (86.489, 95.711, 106.607)), ('A', '245', 34, 'smoc Outlier', (121.068, 110.687, 93.088)), ('A', '250', 34, 'smoc Outlier', (125.223, 113.315, 94.94300000000001)), ('A', '517', 35, 'smoc Outlier', (79.033, 118.48100000000001, 120.37499999999999)), ('A', '519', 35, 'side-chain clash', (83.128, 120.666, 118.341)), ('A', '436', 36, 'smoc Outlier', (103.031, 76.119, 123.543)), ('A', '438', 36, 'smoc Outlier', (104.534, 82.17199999999998, 122.40700000000001)), ('A', '1004', 37, 'smoc Outlier', (126.44300000000001, 102.49100000000001, 73.271)), ('A', '1005', 37, 'Dihedral angle:O4:O:P2:P1\nDihedral angle:O2:O:P1:P2', (129.181, 100.603, 71.67499999999998)), ('A', '430', 38, 'smoc Outlier', (103.14999999999999, 69.551, 128.542)), ('A', '431', 38, 'smoc Outlier', (106.67799999999998, 69.024, 127.262)), ('A', '740', 39, 'smoc Outlier', (94.617, 103.232, 75.518)), ('A', '744', 39, 'smoc Outlier', (95.798, 97.35799999999999, 78.09700000000001)), ('A', '452', 40, 'smoc Outlier', (110.546, 103.49700000000001, 119.30799999999999)), ('A', '453', 40, 'smoc Outlier', (110.34, 107.029, 117.905)), ('A', '454', 41, 'side-chain clash', (117.33, 104.949, 116.172)), ('A', '457', 41, 'side-chain clash', (117.33, 104.949, 116.172)), ('A', '856', 42, 'side-chain clash', (100.27, 80.672, 134.389)), ('A', '888', 42, 'side-chain clash', (100.27, 80.672, 134.389)), ('A', '851', 43, 'side-chain clash', (81.273, 90.45, 135.14)), ('A', '853', 43, 'side-chain clash\nsmoc Outlier', (81.273, 90.45, 135.14)), ('A', '746', 44, 'side-chain clash', (90.591, 95.591, 88.158)), ('A', '750', 44, 'side-chain clash', (90.591, 95.591, 88.158)), ('A', '633', 45, 'smoc Outlier', (101.309, 109.94300000000001, 95.65299999999999)), ('A', '634', 45, 'smoc Outlier', (98.807, 107.936, 97.708)), ('A', '865', 46, 'smoc Outlier', (88.236, 82.506, 115.958)), ('A', '866', 46, 'smoc Outlier', (89.518, 79.141, 117.225)), ('A', '274', 47, 'cablam Outlier\nsmoc Outlier', (112.4, 130.9, 100.7)), ('A', '275', 47, 'cablam Outlier', (115.3, 129.2, 98.9)), ('A', '153', 48, 'smoc Outlier', (137.584, 97.74300000000001, 101.3)), ('A', '154', 48, 'smoc Outlier', (137.349, 94.334, 99.65599999999999)), ('A', '553', 49, 'side-chain clash\nsmoc Outlier', (108.322, 95.041, 118.116)), ('A', '555', 49, 'side-chain clash', (108.322, 95.041, 118.116)), ('A', '322', 50, 'side-chain clash', (120.252, 122.37, 107.2)), ('A', '323', 50, 'side-chain clash', (120.252, 122.37, 107.2)), ('B', '132', 1, 'side-chain clash', (126.652, 113.059, 129.373)), ('B', '138', 1, 'side-chain clash', (126.652, 113.059, 129.373)), ('B', '142', 1, 'smoc Outlier', (128.35100000000003, 119.27199999999999, 128.285)), ('B', '143', 1, 'smoc Outlier', (131.904, 118.975, 129.583)), ('B', '155', 2, 'smoc Outlier', (125.71700000000001, 128.001, 132.07299999999998)), ('B', '157', 2, 'smoc Outlier', (122.45, 125.088, 136.575)), ('B', '191', 2, 'smoc Outlier', (124.67199999999998, 133.751, 129.3)), ('B', '87', 3, 'side-chain clash', (89.325, 128.428, 121.37)), ('B', '88', 3, 'smoc Outlier', (91.315, 130.863, 125.718)), ('B', '111', 4, 'Dihedral angle:CD:NE:CZ:NH1\nsmoc Outlier', (112.43900000000001, 141.24499999999998, 105.49600000000001)), ('B', '112', 4, 'smoc Outlier', (108.71300000000001, 140.541, 105.979)), ('B', '128', 5, 'smoc Outlier', (118.01, 124.706, 127.515)), ('B', '129', 5, 'smoc Outlier', (117.39, 121.05, 128.377)), ('B', '165', 6, 'smoc Outlier', (116.59100000000001, 113.43700000000001, 141.61499999999998)), ('B', '166', 6, 'side-chain clash', (117.207, 116.001, 142.921)), ('B', '96', 7, 'side-chain clash', (107.93, 131.679, 129.103)), ('B', '97', 7, 'side-chain clash', (107.93, 131.679, 129.103)), ('C', '18', 1, 'smoc Outlier', (104.55, 97.043, 139.502)), ('C', '23', 1, 'smoc Outlier', (109.396, 101.32499999999999, 138.698)), ('C', '16', 2, 'side-chain clash', (104.557, 79.959, 139.486)), ('C', '19', 2, 'side-chain clash', (104.557, 79.959, 139.486)), ('C', '32', 3, 'smoc Outlier', (113.804, 93.483, 136.176)), ('C', '55', 3, 'smoc Outlier', (114.332, 87.94600000000001, 139.47899999999998)), ('P', '18', 1, 'side-chain clash', (91.855, 88.055, 113.825)), ('P', '19', 1, 'side-chain clash', (91.855, 88.055, 113.825)), ('P', '17', 2, 'backbone clash\nside-chain clash', (87.767, 89.596, 124.693)), ('T', '13', 1, 'side-chain clash', (86.489, 95.711, 106.607)), ('T', '14', 1, 'side-chain clash', (84.795, 95.545, 110.647)), ('T', '11', 2, 'smoc Outlier', (92.755, 105.01100000000001, 113.107)), ('D', '100', 1, 'side-chain clash', (112.742, 77.196, 142.656)), ('D', '101', 1, 'backbone clash', (117.451, 75.091, 143.072)), ('D', '102', 1, 'backbone clash', (117.451, 75.091, 143.072)), ('D', '103', 1, 'side-chain clash\nsmoc Outlier', (114.348, 80.472, 141.839)), ('D', '84', 2, 'smoc Outlier', (97.195, 93.42, 146.90200000000002)), ('D', '85', 2, 'smoc Outlier', (97.029, 90.63799999999999, 149.48800000000003))]
data['probe'] = [(' C  13  LEU HD13', ' D  91  LEU HD21', -0.774, (106.515, 86.087, 142.19)), (' C  13  LEU  HA ', ' D  91  LEU HD11', -0.719, (105.374, 87.602, 140.683)), (' A 758  LEU HD23', ' A 759  SER  H  ', -0.715, (94.963, 95.935, 104.415)), (' C  53  VAL HG12', ' D 103  LEU HD23', -0.682, (114.405, 80.725, 142.105)), (' A 614  LEU  HB2', ' A 802  GLU  HB3', -0.681, (101.027, 79.905, 97.126)), (' A 380  MET  HG3', ' B  94  MET  HE3', -0.665, (100.251, 128.34, 123.125)), (' A 371  LEU  HG ', ' B  87  MET  HE3', -0.654, (89.325, 128.428, 121.37)), (' A 849  LYS  NZ ', ' P  17    U  OP1', -0.644, (89.455, 92.157, 126.878)), (' A 856  ILE HD11', ' A 888  ILE HG23', -0.619, (80.43, 80.158, 127.888)), (' A 415  PHE  CZ ', ' C   8  CYS  SG ', -0.606, (100.27, 80.672, 134.389)), (' C   9  THR HG22', ' D  94  MET  HB3', -0.606, (104.131, 79.895, 139.77)), (' A 576  LEU HD11', ' A 686  THR HG22', -0.584, (90.523, 107.599, 104.659)), (' A 211  ASP  OD1', ' A 212  LEU  N  ', -0.581, (132.55, 105.546, 82.862)), (' D 100  ASN  HB3', ' D 103  LEU  HB2', -0.58, (112.742, 77.196, 142.656)), (' A 103  LYS  HG2', ' A 112  PRO  HA ', -0.563, (139.018, 101.486, 59.047)), (' A 388  LEU HD23', ' A 397  SER  HB3', -0.561, (113.947, 117.963, 120.845)), (' A 758  LEU HD23', ' A 759  SER  N  ', -0.533, (95.274, 95.955, 104.494)), (' A 507  ASN  ND2', ' A 541  GLN  OE1', -0.526, (97.571, 114.14, 123.87)), (' A 858  ARG  HG3', " P  17    U  H5'", -0.522, (87.767, 89.596, 124.693)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.516, (126.652, 113.059, 129.373)), (' A 837  ILE  O  ', ' A 884  TYR  OH ', -0.51, (93.298, 81.306, 123.891)), (' A 720  VAL HG11', ' A 775  LEU  HG ', -0.505, (106.459, 88.452, 78.452)), (" P  18    U  O2'", " P  19    A  H5'", -0.495, (91.855, 88.055, 113.825)), (' A 454  ASP  OD2', ' A 457  ARG  NH1', -0.494, (117.33, 104.949, 116.172)), (' A  56  PHE  HB2', ' A  70  PHE  HB2', -0.494, (143.321, 99.123, 74.975)), (' D 101  ASP  OD1', ' D 102  ALA  N  ', -0.489, (117.451, 75.091, 143.072)), (' C  53  VAL HG12', ' D 103  LEU  CD2', -0.484, (114.348, 80.472, 141.839)), (' A  69  TYR  N  ', ' A 119  LEU  O  ', -0.484, (139.6, 101.813, 80.434)), (' A 824  ASP  N  ', ' A 824  ASP  OD1', -0.482, (77.938, 70.178, 100.993)), (' A  88  ASN  HA ', ' A  91  LYS  HE3', -0.469, (136.883, 116.816, 65.371)), (' A 100  ASP  OD1', ' A 117  GLN  NE2', -0.466, (143.992, 108.07, 71.195)), (' A 916  TRP  O  ', ' A 917  GLU  HG2', -0.466, (75.681, 74.696, 121.235)), (' C  13  LEU  CD1', ' D  91  LEU HD21', -0.462, (106.762, 86.321, 142.578)), (' A 631  ARG  HG2', ' A 663  LEU HD13', -0.46, (103.293, 110.497, 104.087)), (' A 623  ASP  N  ', ' A 623  ASP  OD1', -0.46, (105.754, 101.233, 109.261)), (' A 396  PHE  HB3', ' A 675  VAL  HB ', -0.452, (112.795, 117.409, 113.337)), (' A 358  ASP  OD1', ' A 533  ARG  NH2', -0.452, (90.449, 133.688, 102.187)), (' B  96  ARG  HG3', ' B  97  LYS  HG2', -0.451, (107.93, 131.679, 129.103)), (' A 388  LEU HD22', ' A 672  SER  HB3', -0.45, (111.516, 117.616, 123.325)), (' A 755  MET  HB3', ' A 764  VAL HG22', -0.449, (99.087, 90.352, 93.64)), (' A 116  ARG  HG2', ' A 217  TYR  HB2', -0.448, (133.99, 106.128, 73.15)), (' C  16  VAL  HA ', ' C  19  GLN HE22', -0.447, (102.425, 92.997, 142.463)), (' A 388  LEU HD13', ' A 400  ALA  HB2', -0.443, (112.721, 119.476, 125.697)), (' C  13  LEU HD12', ' D  91  LEU HD11', -0.438, (106.311, 87.379, 141.917)), (' A 545  LYS  HB3', ' A 555  ARG  HB2', -0.437, (101.893, 98.927, 120.865)), (' A 515  TYR  O  ', ' A 519  MET  HG3', -0.434, (83.128, 120.666, 118.341)), (' A 164  ASP  HB3', ' A 167  GLU  HB2', -0.427, (121.243, 94.696, 107.781)), (' A 553  ARG  HB3', ' A 555  ARG HH12', -0.421, (108.322, 95.041, 118.116)), (' C  16  VAL  O  ', ' C  19  GLN  NE2', -0.42, (102.856, 94.165, 143.425)), (' A 917  GLU  O  ', ' A 919  GLU  N  ', -0.418, (77.202, 73.928, 117.955)), (' A 613  HIS  CE1', ' A 803  THR HG23', -0.418, (103.212, 75.666, 91.437)), (' A 341  VAL  HB ', ' B  98  LEU HD11', -0.415, (104.212, 133.195, 119.323)), (' A 530  TYR  HD2', ' A 536  ILE HD11', -0.414, (91.817, 126.077, 108.888)), (' A 851  ASP  OD2', ' A 853  THR  OG1', -0.413, (81.273, 90.45, 135.14)), (' C   9  THR  CG2', ' D  94  MET  HB3', -0.412, (104.557, 79.959, 139.486)), (' A 378  PRO  HA ', ' A 539  ILE HD11', -0.411, (101.978, 122.695, 118.615)), (' A  60  ASP  CG ', ' A  61  GLU  H  ', -0.41, (151.567, 103.623, 86.315)), (' A 340  PHE  HE1', ' B  95  LEU HD21', -0.409, (99.14, 135.278, 123.904)), (" T  13    A  H2'", ' T  14    A  C8 ', -0.408, (84.795, 95.545, 110.647)), (' A 469  LEU  O  ', ' A 473  VAL HG13', -0.407, (103.079, 107.242, 88.974)), (' A 238  TYR  O  ', ' A 242  MET  HG3', -0.406, (116.316, 110.859, 86.964)), (' A 746  TYR  OH ', ' A 750  ARG  NH1', -0.405, (90.591, 95.591, 88.158)), (' A 322  PRO  HA ', ' A 323  PRO  HD3', -0.405, (120.252, 122.37, 107.2)), (' A 811  GLU  OE2', ' A 814  SER  HA ', -0.404, (99.603, 85.651, 109.78)), (' A 506  PHE  HB3', ' A 515  TYR  CZ ', -0.403, (89.982, 119.272, 122.467)), (' A 576  LEU HD22', ' A 689  TYR  CG ', -0.402, (90.216, 104.716, 102.83)), (' A 444  GLN  HB3', ' A 448  ALA  HB2', -0.401, (109.892, 100.308, 126.696)), (' B 166  ILE  H  ', ' B 166  ILE HD12', -0.4, (117.207, 116.001, 142.921)), (' A 590  GLY  HA2', " T  13    A  O2'", -0.4, (86.489, 95.711, 106.607))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (96.60900000000002, 119.68399999999998, 121.91799999999996)), ('B', ' 183 ', 'PRO', None, (119.12500000000004, 108.01599999999998, 131.618))]
data['cablam'] = [('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (112.4, 130.9, 100.7)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (115.3, 129.2, 98.9)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (97.3, 117.3, 122.0)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nHTSS-', (90.1, 84.5, 88.8)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--SS', (111.0, 112.9, 109.1)), ('A', '759', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (96.6, 97.7, 104.1)), ('A', '760', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (99.9, 95.9, 104.1)), ('A', '916', 'TRP', 'check CA trace,carbonyls, peptide', 'bend\nGGSST', (78.4, 75.0, 123.7)), ('A', '917', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nGSSTH', (76.9, 72.5, 121.1)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (134.1, 103.4, 98.6)), ('A', '326', 'PHE', 'check CA trace', 'bend\nGGSEE', (111.5, 123.8, 107.0)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--SS-', (108.2, 111.2, 107.2)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (121.0, 107.3, 133.1))]
data['smoc'] = [('A', 24, u'THR', 0.4336807678184626, (143.967, 86.04400000000001, 72.67199999999998)), ('A', 25, u'GLY', 0.5372584849437595, (144.292, 86.745, 68.94600000000001)), ('A', 32, u'TYR', 0.6980100395725993, (127.62199999999999, 91.221, 80.218)), ('A', 36, u'ASP', 0.762992071785673, (119.37299999999999, 101.37499999999999, 77.78)), ('A', 84, u'GLU', 0.7042128572480769, (134.252, 111.319, 61.92)), ('A', 92, u'ASP', 0.756489098103977, (136.77499999999998, 120.585, 71.86)), ('A', 100, u'ASP', 0.7242639037873361, (141.37, 107.95400000000001, 67.64999999999999)), ('A', 118, u'ARG', 0.7330884065303068, (141.04299999999998, 105.865, 78.94800000000001)), ('A', 138, u'ASN', 0.7759307080396032, (124.642, 87.84400000000001, 92.618)), ('A', 144, u'GLU', 0.762915091854931, (133.672, 95.548, 92.037)), ('A', 151, u'CYS', 0.826385510583878, (134.14299999999997, 103.38499999999999, 98.601)), ('A', 153, u'ASP', 0.7692157762329345, (137.584, 97.74300000000001, 101.3)), ('A', 154, u'ASP', 0.7624942001818407, (137.349, 94.334, 99.65599999999999)), ('A', 161, u'ASP', 0.7428565232855, (124.04700000000001, 91.72, 105.99900000000001)), ('A', 164, u'ASP', 0.7682712454036007, (120.96100000000001, 95.733, 104.691)), ('A', 211, u'ASP', 0.7245193421422402, (131.766, 106.498, 81.29700000000001)), ('A', 212, u'LEU', 0.7751518348922474, (131.929, 106.422, 85.09100000000001)), ('A', 236, u'SER', 0.7794489131848739, (115.576, 108.3, 79.648)), ('A', 239, u'SER', 0.7700419481382104, (114.84400000000001, 109.599, 84.827)), ('A', 245, u'LEU', 0.7952977372794136, (121.068, 110.687, 93.088)), ('A', 250, u'ALA', 0.7608119233377049, (125.223, 113.315, 94.94300000000001)), ('A', 269, u'ASP', 0.7749351894451754, (121.112, 132.901, 107.181)), ('A', 274, u'ASP', 0.7375561346435108, (112.357, 130.894, 100.74300000000001)), ('A', 284, u'ASP', 0.7827202051592235, (119.752, 124.857, 85.93)), ('A', 291, u'ASP', 0.7656776958674365, (112.421, 119.77499999999999, 78.93400000000001)), ('A', 298, u'CYS', 0.8208458172454336, (104.05499999999999, 123.309, 94.02499999999999)), ('A', 301, u'CYS', 0.7945563181226615, (101.51100000000001, 123.435, 89.512)), ('A', 308, u'LEU', 0.8057893496608786, (104.432, 114.692, 91.425)), ('A', 312, u'ASN', 0.7902729577855258, (110.332, 114.91600000000001, 93.035)), ('A', 336, u'ASP', 0.6357314565669853, (92.90400000000001, 142.607, 121.54100000000001)), ('A', 340, u'PHE', 0.7202285545841174, (100.49400000000001, 136.282, 119.255)), ('A', 350, u'GLU', 0.7210612641589368, (108.474, 118.515, 98.745)), ('A', 365, u'ARG', 0.6701993758534345, (87.73, 138.70899999999997, 118.837)), ('A', 369, u'LYS', 0.7364570375119227, (86.51, 128.17499999999998, 114.85199999999999)), ('A', 377, u'ASP', 0.7674590062390265, (98.91900000000001, 125.366, 116.069)), ('A', 395, u'CYS', 0.7743478038822352, (115.458, 113.265, 114.99400000000001)), ('A', 398, u'VAL', 0.7406338934843633, (112.106, 121.661, 118.44000000000001)), ('A', 418, u'ASP', 0.7478333142879442, (91.91600000000001, 79.877, 136.47)), ('A', 426, u'LYS', 0.7736317926291078, (92.91100000000002, 68.886, 130.529)), ('A', 430, u'LYS', 0.7586623199367667, (103.14999999999999, 69.551, 128.542)), ('A', 431, u'GLU', 0.7130820725644209, (106.67799999999998, 69.024, 127.262)), ('A', 436, u'GLU', 0.7110672473772436, (103.031, 76.119, 123.543)), ('A', 438, u'LYS', 0.7888710068452695, (104.534, 82.17199999999998, 122.40700000000001)), ('A', 442, u'PHE', 0.7844799604226668, (106.199, 92.10199999999999, 127.015)), ('A', 445, u'ASP', 0.7831897025935187, (111.41700000000002, 100.369, 130.517)), ('A', 452, u'ASP', 0.7724689743468993, (110.546, 103.49700000000001, 119.30799999999999)), ('A', 453, u'TYR', 0.8158281478583562, (110.34, 107.029, 117.905)), ('A', 465, u'ASP', 0.7770764801883883, (112.021, 107.624, 88.769)), ('A', 474, u'GLU', 0.8007166802852203, (97.823, 105.838, 85.98700000000001)), ('A', 475, u'VAL', 0.8039903788160813, (97.74400000000001, 102.05799999999999, 86.44600000000001)), ('A', 481, u'ASP', 0.7590394238792645, (88.021, 103.54, 89.362)), ('A', 496, u'ASN', 0.7776866188734093, (82.645, 105.359, 114.784)), ('A', 508, u'LYS', 0.8093696230687212, (93.569, 118.184, 128.39800000000002)), ('A', 512, u'ALA', 0.7572803648398319, (86.301, 113.801, 120.84)), ('A', 517, u'ASP', 0.7470594366279328, (79.033, 118.48100000000001, 120.37499999999999)), ('A', 522, u'GLU', 0.7053674327324717, (78.049, 125.3, 110.387)), ('A', 525, u'ASP', 0.7958680564460789, (81.777, 123.22, 107.56400000000001)), ('A', 529, u'ALA', 0.8231559674087111, (86.35199999999999, 125.426, 104.04100000000001)), ('A', 540, u'THR', 0.7821768940196049, (100.709, 114.381, 116.91600000000001)), ('A', 553, u'ARG', 0.7081257011836547, (109.71000000000001, 95.259, 120.383)), ('A', 563, u'CYS', 0.77038126621284, (91.228, 119.45400000000001, 114.13799999999999)), ('A', 605, u'VAL', 0.7814043485591851, (92.003, 86.227, 93.49700000000001)), ('A', 611, u'ASN', 0.7729629178764091, (99.40400000000001, 78.67099999999999, 85.56)), ('A', 615, u'MET', 0.7568240642482487, (102.886, 84.648, 96.54100000000001)), ('A', 633, u'MET', 0.7612329886364477, (101.309, 109.94300000000001, 95.65299999999999)), ('A', 634, u'ALA', 0.7899457079997522, (98.807, 107.936, 97.708)), ('A', 658, u'GLU', 0.7259978397323329, (97.73400000000001, 116.295, 104.96400000000001)), ('A', 659, u'CYS', 0.7588681517051401, (101.478, 116.67599999999999, 104.38)), ('A', 666, u'MET', 0.7368839380515458, (105.26400000000001, 117.867, 115.054)), ('A', 667, u'VAL', 0.7679510886612444, (105.508, 114.883, 117.40100000000001)), ('A', 668, u'MET', 0.7598483776528652, (104.49000000000001, 115.209, 121.062)), ('A', 679, u'GLY', 0.7455405621635804, (106.40400000000001, 107.867, 106.87599999999999)), ('A', 684, u'ASP', 0.745481309710403, (95.38, 108.99700000000001, 110.424)), ('A', 703, u'ASN', 0.7840267354330835, (105.853, 94.29700000000001, 87.14)), ('A', 711, u'ASP', 0.8028124726528933, (115.543, 90.588, 76.932)), ('A', 717, u'ASP', 0.7942885829488366, (105.224, 85.868, 72.426)), ('A', 718, u'LYS', 0.7544524391417351, (104.556, 88.55499999999999, 69.82199999999999)), ('A', 726, u'ARG', 0.7467300537396624, (105.059, 100.166, 74.02199999999999)), ('A', 730, u'CYS', 0.7807445437822798, (104.94100000000002, 105.31, 77.257)), ('A', 734, u'ASN', 0.7526681922038161, (105.473, 110.242, 75.71900000000001)), ('A', 736, u'ASP', 0.7813397990208825, (100.98700000000001, 112.661, 77.989)), ('A', 740, u'ASP', 0.7586018931238777, (94.617, 103.232, 75.518)), ('A', 744, u'GLU', 0.7768009438862521, (95.798, 97.35799999999999, 78.09700000000001)), ('A', 754, u'SER', 0.7539810466174015, (95.648, 89.161, 90.079)), ('A', 759, u'SER', 0.7443174160591767, (96.563, 97.727, 104.083)), ('A', 775, u'LEU', 0.7810627328266802, (107.062, 88.52199999999999, 81.98)), ('A', 778, u'SER', 0.7884759452659397, (108.226, 87.721, 91.22)), ('A', 782, u'PHE', 0.7854099100224888, (109.94100000000002, 92.94400000000002, 94.65799999999999)), ('A', 784, u'SER', 0.7994726713470566, (114.94000000000001, 94.95100000000001, 93.924)), ('A', 785, u'VAL', 0.7896081703802185, (112.12899999999999, 97.526, 93.91400000000002)), ('A', 789, u'GLN', 0.7652948793298869, (112.408, 102.80799999999999, 96.02499999999999)), ('A', 790, u'ASN', 0.7991532652474037, (111.866, 101.975, 99.71700000000001)), ('A', 796, u'GLU', 0.7252930522928648, (113.333, 86.042, 101.118)), ('A', 802, u'GLU', 0.784694177227356, (102.71700000000001, 78.381, 97.43)), ('A', 811, u'GLU', 0.6746916760511342, (99.90700000000001, 83.667, 105.488)), ('A', 812, u'PHE', 0.809858430271793, (97.356, 86.475, 105.192)), ('A', 818, u'MET', 0.7674508957874622, (93.061, 74.922, 104.613)), ('A', 824, u'ASP', 0.7277632952608057, (78.709, 68.736, 100.227)), ('A', 833, u'ASP', 0.7635058518103909, (98.034, 80.16499999999999, 115.30199999999999)), ('A', 840, u'ALA', 0.8023294681743628, (94.908, 85.667, 124.609)), ('A', 853, u'THR', 0.7522874161844316, (80.819, 87.936, 133.664)), ('A', 865, u'ASP', 0.7675984712747895, (88.236, 82.506, 115.958)), ('A', 866, u'ALA', 0.8030849845105689, (89.518, 79.141, 117.225)), ('A', 879, u'ASP', 0.7973988357137743, (91.70400000000001, 70.46300000000001, 121.215)), ('A', 889, u'ARG', 0.7046189609212802, (80.864, 75.254, 130.969)), ('A', 893, u'ASP', 0.596829063796324, (78.637, 76.37899999999999, 136.24299999999997)), ('A', 911, u'ASN', 0.4865489385113176, (69.718, 80.70400000000001, 124.07199999999999)), ('A', 917, u'GLU', 0.685574730425215, (76.91400000000002, 72.539, 121.082)), ('A', 922, u'GLU', 0.7620239640548888, (79.492, 76.233, 112.519)), ('A', 924, u'MET', 0.8231749151984435, (79.70700000000001, 81.536, 111.618)), ('A', 927, u'PRO', 0.7770176768373016, (78.326, 80.17099999999999, 103.113)), ('A', 928, u'HIS', 0.7041073733546315, (74.79700000000001, 81.384, 103.861)), ('A', 929, u'THR', 0.7489500591705844, (74.46600000000001, 84.315, 106.251)), ('A', 1001, u'ZN', 0.7470489693484025, (104.68799999999999, 121.853, 88.722)), ('A', 1002, u'ZN', 0.6664247201155616, (86.25, 117.74700000000001, 97.44300000000001)), ('A', 1003, u'MG', 0.3651794500381051, (104.38199999999999, 95.12899999999999, 107.922)), ('A', 1004, u'MG', 0.6204928112120973, (126.44300000000001, 102.49100000000001, 73.271)), ('B', 79, u'LYS', 0.5931110012032639, (79.886, 122.724, 127.004)), ('B', 88, u'GLN', 0.7933503235864319, (91.315, 130.863, 125.718)), ('B', 101, u'ASP', 0.7267626524782415, (112.846, 141.45700000000002, 124.121)), ('B', 106, u'ILE', 0.7351519526170112, (114.20100000000001, 138.27299999999997, 115.52499999999999)), ('B', 111, u'ARG', 0.5991567036294954, (112.43900000000001, 141.24499999999998, 105.49600000000001)), ('B', 112, u'ASP', 0.6488608190245878, (108.71300000000001, 140.541, 105.979)), ('B', 119, u'ILE', 0.7936656406859862, (114.501, 128.819, 115.026)), ('B', 128, u'LEU', 0.8157171698872226, (118.01, 124.706, 127.515)), ('B', 129, u'MET', 0.7809004562275809, (117.39, 121.05, 128.377)), ('B', 142, u'CYS', 0.7012339072259399, (128.35100000000003, 119.27199999999999, 128.285)), ('B', 143, u'ASP', 0.7273253324405823, (131.904, 118.975, 129.583)), ('B', 155, u'GLU', 0.764518520839793, (125.71700000000001, 128.001, 132.07299999999998)), ('B', 157, u'GLN', 0.7702403387805824, (122.45, 125.088, 136.575)), ('B', 165, u'LYS', 0.7383020042702857, (116.59100000000001, 113.43700000000001, 141.61499999999998)), ('B', 171, u'GLU', 0.7381738313288204, (129.232, 112.831, 140.71099999999998)), ('B', 174, u'MET', 0.6844247852608312, (133.60399999999998, 107.268, 134.25)), ('B', 191, u'ALA', 0.7919631410035475, (124.67199999999998, 133.751, 129.3)), ('C', 11, u'VAL', 0.7547776952397339, (104.729, 87.256, 134.348)), ('C', 18, u'GLN', 0.6957420393007663, (104.55, 97.043, 139.502)), ('C', 23, u'GLU', 0.666889088134033, (109.396, 101.32499999999999, 138.698)), ('C', 32, u'CYS', 0.6918564839392983, (113.804, 93.483, 136.176)), ('C', 55, u'LEU', 0.6017723071523271, (114.332, 87.94600000000001, 139.47899999999998)), ('C', 67, u'ASP', 0.37005719078661864, (105.721, 89.87299999999999, 155.121)), ('T', 11, u'A', 0.8293392695915853, (92.755, 105.01100000000001, 113.107)), ('D', 84, u'THR', 0.5157189131021235, (97.195, 93.42, 146.90200000000002)), ('D', 85, u'SER', 0.5538494160136479, (97.029, 90.63799999999999, 149.48800000000003)), ('D', 90, u'MET', 0.49964807626348506, (98.722, 83.345, 145.012)), ('D', 103, u'LEU', 0.30711664672730904, (114.19, 78.806, 144.295))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11692/7aap/Model_validation_1/validation_cootdata/molprobity_probe7aap_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

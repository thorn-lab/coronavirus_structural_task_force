
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
data['clusters'] = [('A', '586', 1, 'cablam Outlier', (136.6, 141.5, 121.3)), ('A', '601', 1, 'side-chain clash\nsmoc Outlier', (133.37, 148.49, 124.598)), ('A', '602', 1, 'smoc Outlier', (132.089, 150.38000000000002, 126.252)), ('A', '603', 1, 'side-chain clash', (133.09, 154.456, 124.449)), ('A', '605', 1, 'side-chain clash', (132.238, 145.308, 122.984)), ('A', '606', 1, 'Dihedral angle:CA:C', (131.937, 152.096, 120.281)), ('A', '607', 1, 'Dihedral angle:N:CA\ncablam CA Geom Outlier', (135.32100000000003, 152.4, 118.76100000000001)), ('A', '608', 1, 'cablam Outlier', (134.8, 154.2, 115.5)), ('A', '615', 1, 'side-chain clash', (123.702, 144.804, 117.024)), ('A', '695', 1, 'side-chain clash', (127.374, 137.562, 121.532)), ('A', '755', 1, 'side-chain clash', (129.338, 142.159, 117.537)), ('A', '756', 1, 'side-chain clash', (132.238, 145.308, 122.984)), ('A', '761', 1, 'Dihedral angle:CA:CB:CG:OD1', (126.537, 137.153, 125.61999999999999)), ('A', '762', 1, 'side-chain clash', (127.374, 137.562, 121.532)), ('A', '764', 1, 'side-chain clash', (129.338, 142.159, 117.537)), ('A', '312', 2, 'side-chain clash\nsmoc Outlier', (128.109, 120.519, 107.645)), ('A', '462', 2, 'side-chain clash', (123.966, 121.614, 114.575)), ('A', '463', 2, 'smoc Outlier', (125.21600000000001, 119.289, 108.642)), ('A', '464', 2, 'side-chain clash', (128.109, 120.519, 107.645)), ('A', '466', 2, 'side-chain clash', (131.724, 123.606, 106.226)), ('A', '468', 2, 'side-chain clash', (131.809, 129.588, 103.01)), ('A', '472', 2, 'smoc Outlier', (134.156, 131.69, 108.74900000000001)), ('A', '627', 2, 'side-chain clash', (123.966, 121.614, 114.575)), ('A', '697', 2, 'smoc Outlier', (131.23899999999998, 132.21899999999997, 114.49000000000001)), ('A', '698', 2, 'smoc Outlier', (127.49900000000001, 132.847, 114.426)), ('A', '702', 2, 'smoc Outlier', (125.19, 136.295, 109.877)), ('A', '703', 2, 'smoc Outlier', (127.35499999999999, 138.98700000000002, 108.29400000000001)), ('A', '731', 2, 'side-chain clash', (131.809, 129.588, 103.01)), ('A', '749', 2, 'side-chain clash', (132.209, 143.762, 109.299)), ('A', '785', 2, 'smoc Outlier', (121.30799999999999, 131.81, 110.789)), ('A', '502', 3, 'cablam Outlier', (136.4, 115.2, 140.6)), ('A', '504', 3, 'cablam CA Geom Outlier', (132.8, 109.9, 138.7)), ('A', '539', 3, 'smoc Outlier', (132.04299999999998, 109.807, 132.997)), ('A', '540', 3, 'side-chain clash', (128.008, 112.725, 132.22)), ('A', '561', 3, 'smoc Outlier', (136.505, 113.68799999999999, 135.638)), ('A', '562', 3, 'smoc Outlier', (139.781, 114.61999999999999, 137.24499999999998)), ('A', '658', 3, 'side-chain clash', (135.514, 117.506, 125.35)), ('A', '662', 3, 'side-chain clash', (135.514, 117.506, 125.35)), ('A', '665', 3, 'side-chain clash\ncablam Outlier', (129.761, 114.195, 126.732)), ('A', '666', 3, 'smoc Outlier', (128.629, 109.369, 129.23)), ('A', '667', 3, 'side-chain clash', (128.008, 112.725, 132.22)), ('A', '677', 3, 'cablam Outlier', (124.4, 113.7, 122.5)), ('A', '678', 3, 'cablam CA Geom Outlier', (126.1, 117.1, 122.6)), ('A', '26', 4, 'cablam Outlier', (105.8, 138.1, 78.6)), ('A', '28', 4, 'side-chain clash\ncablam Outlier\nsmoc Outlier', (104.757, 132.533, 85.37)), ('A', '35', 4, 'side-chain clash', (114.622, 133.697, 87.324)), ('A', '50', 4, 'side-chain clash', (114.622, 133.697, 87.324)), ('A', '52', 4, 'side-chain clash\ncablam Outlier', (112.774, 134.232, 81.147)), ('A', '53', 4, 'cablam Outlier', (108.9, 133.5, 81.2)), ('A', '55', 4, 'side-chain clash', (104.757, 132.533, 85.37)), ('A', '73', 4, 'side-chain clash', (112.774, 134.232, 81.147)), ('A', '279', 5, 'side-chain clash\nsmoc Outlier', (136.839, 94.076, 136.188)), ('A', '331', 5, 'side-chain clash', (138.077, 94.649, 128.232)), ('A', '340', 5, 'Dihedral angle:CA:C', (139.518, 93.05, 132.311)), ('A', '341', 5, 'side-chain clash\nDihedral angle:N:CA', (137.502, 94.971, 129.782)), ('A', '352', 5, 'side-chain clash\nsmoc Outlier', (136.839, 94.076, 136.188)), ('A', '631', 5, 'side-chain clash', (133.027, 98.627, 126.807)), ('A', '663', 5, 'side-chain clash', (133.027, 98.627, 126.807)), ('A', '493', 6, 'side-chain clash', (146.949, 125.3, 134.712)), ('A', '494', 6, 'side-chain clash', (146.497, 128.516, 137.39)), ('A', '569', 6, 'side-chain clash', (146.465, 124.604, 131.26)), ('A', '572', 6, 'side-chain clash', (143.112, 127.638, 128.361)), ('A', '573', 6, 'side-chain clash', (146.465, 124.604, 131.26)), ('A', '576', 6, 'side-chain clash\nsmoc Outlier', (143.112, 127.638, 128.361)), ('A', '577', 6, 'side-chain clash', (147.057, 131.382, 135.979)), ('A', '610', 7, 'side-chain clash', (127.943, 156.807, 113.662)), ('A', '611', 7, 'side-chain clash\nDihedral angle:CA:C', (126.24900000000001, 155.697, 112.15899999999999)), ('A', '612', 7, 'side-chain clash\nDihedral angle:N:CA', (126.193, 153.636, 115.31700000000001)), ('A', '613', 7, 'side-chain clash\nsmoc Outlier', (122.992, 153.899, 115.823)), ('A', '769', 7, 'side-chain clash', (124.666, 155.841, 107.967)), ('A', '770', 7, 'smoc Outlier', (124.798, 149.671, 106.11999999999999)), ('A', '115', 8, 'side-chain clash', (109.38, 127.253, 76.704)), ('A', '116', 8, 'side-chain clash\nDihedral angle:CA:C\nsmoc Outlier', (110.573, 123.41000000000001, 78.87599999999999)), ('A', '117', 8, 'Dihedral angle:N:CA', (107.95700000000001, 120.96700000000001, 80.04700000000001)), ('A', '119', 8, 'side-chain clash', (111.097, 124.374, 82.35)), ('A', '72', 8, 'side-chain clash', (109.38, 127.253, 76.704)), ('A', '98', 8, 'side-chain clash', (110.541, 117.224, 76.064)), ('A', '274', 9, 'cablam Outlier', (133.6, 100.0, 111.6)), ('A', '275', 9, 'cablam Outlier', (131.2, 101.1, 108.8)), ('A', '324', 9, 'side-chain clash', (122.394, 101.514, 121.983)), ('A', '325', 9, 'smoc Outlier', (127.71900000000001, 101.203, 117.52199999999999)), ('A', '396', 9, 'side-chain clash', (122.394, 101.514, 121.983)), ('A', '426', 9, 'side-chain clash', (131.299, 98.642, 117.721)), ('A', '836', 10, 'Dihedral angle:CD:NE:CZ:NH1', (117.936, 140.61899999999997, 142.198)), ('A', '838', 10, 'side-chain clash', (117.691, 143.673, 148.983)), ('A', '839', 10, 'smoc Outlier', (116.327, 138.82500000000002, 146.696)), ('A', '842', 10, 'smoc Outlier', (116.782, 138.226, 151.90800000000002)), ('A', '877', 10, 'smoc Outlier', (116.789, 152.407, 143.577)), ('A', '880', 10, 'smoc Outlier', (118.251, 150.15200000000002, 148.05200000000002)), ('A', '10', 11, 'Dihedral angle:CD:NE:CZ:NH1', (101.812, 125.184, 69.645)), ('A', '11', 11, 'side-chain clash', (100.306, 127.262, 73.609)), ('A', '12', 11, 'side-chain clash', (99.401, 122.583, 71.022)), ('A', '8', 11, 'side-chain clash', (100.306, 127.262, 73.609)), ('A', '9', 11, 'side-chain clash', (99.401, 122.583, 71.022)), ('A', '36', 12, 'Dihedral angle:CA:CB:CG:OD1', (122.41900000000001, 131.478, 92.651)), ('A', '45', 12, 'cablam Outlier', (122.6, 133.8, 96.4)), ('A', '46', 12, 'smoc Outlier', (119.67099999999999, 136.21299999999997, 96.537)), ('A', '708', 12, 'side-chain clash', (126.818, 138.133, 98.821)), ('A', '724', 12, 'smoc Outlier', (130.657, 140.87, 97.812)), ('A', '105', 13, 'side-chain clash', (106.737, 132.667, 61.545)), ('A', '107', 13, 'cablam Outlier\nsmoc Outlier', (104.8, 140.5, 64.1)), ('A', '108', 13, 'cablam Outlier', (107.1, 139.9, 61.1)), ('A', '109', 13, 'smoc Outlier', (109.921, 137.758, 62.358)), ('A', '110', 13, 'side-chain clash', (106.737, 132.667, 61.545)), ('A', '816', 14, 'side-chain clash', (125.603, 149.098, 134.441)), ('A', '830', 14, 'side-chain clash', (125.603, 149.098, 134.441)), ('A', '865', 14, 'smoc Outlier', (127.364, 145.414, 143.383)), ('A', '868', 14, 'side-chain clash', (126.968, 149.471, 138.605)), ('A', '189', 15, 'smoc Outlier', (121.94100000000002, 115.25, 90.107)), ('A', '192', 15, 'smoc Outlier', (123.04400000000001, 114.397, 85.292)), ('A', '196', 15, 'side-chain clash', (127.778, 118.682, 85.21)), ('A', '232', 15, 'side-chain clash', (127.778, 118.682, 85.21)), ('A', '211', 16, 'smoc Outlier', (112.923, 121.837, 89.806)), ('A', '213', 16, 'cablam Outlier', (110.9, 116.9, 91.1)), ('A', '216', 16, 'smoc Outlier', (117.43, 119.88, 85.13)), ('A', '29', 17, 'side-chain clash', (108.862, 139.839, 85.472)), ('A', '30', 17, 'smoc Outlier', (105.301, 139.534, 89.021)), ('A', '51', 17, 'side-chain clash\ncablam Outlier', (108.862, 139.839, 85.472)), ('A', '414', 18, 'side-chain clash', (119.916, 127.488, 154.179)), ('A', '845', 18, 'cablam Outlier', (122.2, 129.4, 151.8)), ('A', '846', 18, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1', (122.32499999999999, 128.453, 155.55700000000002)), ('A', '80', 19, 'smoc Outlier', (118.87899999999999, 129.093, 71.04100000000001)), ('A', '83', 19, 'smoc Outlier', (121.251, 125.334, 73.886)), ('A', '84', 19, 'smoc Outlier', (119.619, 123.20700000000001, 71.194)), ('A', '795', 20, 'side-chain clash', (112.214, 134.894, 121.257)), ('A', '796', 20, 'smoc Outlier', (112.728, 139.14, 118.46100000000001)), ('A', '798', 20, 'side-chain clash', (112.214, 134.894, 121.257)), ('A', '60', 21, 'side-chain clash', (93.462, 117.279, 88.215)), ('A', '62', 21, 'cablam Outlier', (88.6, 116.4, 85.8)), ('A', '64', 21, 'side-chain clash', (93.462, 117.279, 88.215)), ('A', '180', 22, 'side-chain clash', (113.116, 110.159, 99.872)), ('A', '183', 22, 'smoc Outlier', (117.12799999999999, 112.412, 98.092)), ('A', '184', 22, 'smoc Outlier', (115.593, 111.831, 94.67099999999999)), ('A', '164', 23, 'backbone clash\nside-chain clash', (108.094, 126.899, 120.527)), ('A', '165', 23, 'backbone clash\nsmoc Outlier', (111.131, 126.188, 117.386)), ('A', '167', 23, 'side-chain clash\nsmoc Outlier', (108.094, 126.899, 120.527)), ('A', '131', 24, 'side-chain clash', (115.341, 123.033, 106.414)), ('A', '247', 24, 'side-chain clash', (115.341, 123.033, 106.414)), ('A', '225', 25, 'side-chain clash', (136.542, 118.804, 75.412)), ('A', '226', 25, 'side-chain clash', (136.542, 118.804, 75.412)), ('A', '634', 26, 'side-chain clash', (135.972, 127.675, 117.982)), ('A', '693', 26, 'side-chain clash', (135.972, 127.675, 117.982)), ('A', '258', 27, 'cablam Outlier', (116.6, 98.0, 99.9)), ('A', '260', 27, 'smoc Outlier', (112.801, 102.07799999999999, 100.006)), ('A', '18', 28, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (94.986, 120.54400000000001, 78.648)), ('A', '59', 28, 'side-chain clash', (93.472, 120.727, 81.369)), ('A', '410', 29, 'smoc Outlier', (116.343, 120.533, 146.094)), ('A', '444', 29, 'smoc Outlier', (112.471, 120.783, 143.15800000000002)), ('A', '366', 30, 'side-chain clash', (146.634, 100.225, 138.767)), ('A', '371', 30, 'side-chain clash', (146.634, 100.225, 138.767)), ('A', '361', 31, 'smoc Outlier', (147.46800000000002, 93.17099999999999, 126.614)), ('A', '362', 31, 'smoc Outlier', (148.796, 90.793, 129.28)), ('A', '146', 32, 'smoc Outlier', (105.07799999999999, 122.195, 102.44000000000001)), ('A', '151', 32, 'cablam CA Geom Outlier', (104.1, 117.5, 104.1)), ('A', '388', 33, 'side-chain clash', (119.454, 103.592, 131.182)), ('A', '397', 33, 'side-chain clash', (119.454, 103.592, 131.182)), ('A', '118', 34, 'side-chain clash', (102.904, 116.188, 77.384)), ('A', '15', 34, 'side-chain clash', (102.904, 116.188, 77.384)), ('A', '483', 35, 'side-chain clash', (143.746, 138.545, 124.27)), ('A', '582', 35, 'side-chain clash', (143.746, 138.545, 124.27)), ('A', '642', 36, 'smoc Outlier', (149.92100000000002, 124.55499999999999, 119.252)), ('A', '646', 36, 'smoc Outlier', (152.271, 119.312, 118.98700000000001)), ('A', '431', 37, 'smoc Outlier', (102.337, 147.95000000000002, 147.914)), ('A', '432', 37, 'cablam Outlier', (102.7, 149.7, 144.5)), ('A', '619', 38, 'side-chain clash', (122.534, 130.505, 123.296)), ('A', '622', 38, 'side-chain clash', (122.534, 130.505, 123.296)), ('A', '335', 39, 'side-chain clash', (144.519, 90.091, 136.441)), ('A', '338', 39, 'side-chain clash', (144.519, 90.091, 136.441)), ('A', '722', 40, 'side-chain clash', (136.575, 144.274, 94.791)), ('A', '726', 40, 'side-chain clash', (136.575, 144.274, 94.791)), ('A', '111', 41, 'side-chain clash', (110.623, 136.929, 70.842)), ('A', '74', 41, 'side-chain clash', (110.623, 136.929, 70.842)), ('A', '614', 42, 'side-chain clash', (121.882, 150.092, 121.632)), ('A', '802', 42, 'side-chain clash', (121.882, 150.092, 121.632)), ('A', '684', 43, 'side-chain clash', (133.396, 123.204, 129.19)), ('A', '687', 43, 'side-chain clash', (133.396, 123.204, 129.19)), ('C', '23', 1, 'side-chain clash', (94.922, 130.283, 154.641)), ('C', '29', 1, 'side-chain clash', (94.922, 130.283, 154.641)), ('C', '44', 1, 'side-chain clash', (93.351, 136.926, 143.172)), ('C', '45', 1, 'cablam Outlier', (97.1, 138.3, 146.1)), ('C', '46', 1, 'side-chain clash', (93.137, 132.563, 147.215)), ('C', '47', 1, 'smoc Outlier', (94.938, 132.80800000000002, 144.76899999999998)), ('C', '50', 1, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (94.222, 129.97, 148.441)), ('C', '53', 1, 'side-chain clash', (94.671, 128.018, 150.089)), ('C', '54', 1, 'smoc Outlier', (96.136, 124.44600000000001, 150.86200000000002)), ('C', '57', 1, 'smoc Outlier', (96.806, 122.04700000000001, 155.595)), ('C', '63', 2, 'smoc Outlier', (97.96700000000001, 115.084, 163.971)), ('C', '64', 2, 'cablam Outlier\nsmoc Outlier', (100.7, 116.5, 166.2)), ('C', '65', 2, 'cablam CA Geom Outlier', (103.7, 118.6, 165.2)), ('C', '66', 2, 'side-chain clash\nbackbone clash', (102.569, 123.351, 167.198)), ('C', '67', 2, 'side-chain clash\nbackbone clash', (102.569, 123.351, 167.198)), ('C', '10', 3, 'smoc Outlier', (105.71100000000001, 130.142, 151.875)), ('C', '14', 3, 'side-chain clash', (110.969, 124.768, 149.642)), ('C', '17', 3, 'smoc Outlier', (107.85199999999999, 120.84700000000001, 156.04299999999998)), ('C', '22', 3, 'side-chain clash', (98.544, 117.243, 147.956)), ('C', '30', 3, 'smoc Outlier', (105.68499999999999, 116.8, 144.742)), ('B', '68', 1, 'side-chain clash', (160.11, 114.058, 144.561)), ('B', '70', 1, 'smoc Outlier', (159.072, 116.485, 140.17399999999998)), ('B', '72', 1, 'side-chain clash', (160.11, 114.058, 144.561)), ('B', '73', 1, 'side-chain clash\ncablam Outlier', (155.265, 111.384, 145.316)), ('B', '74', 1, 'cablam Outlier', (154.2, 116.3, 148.2)), ('B', '75', 1, 'smoc Outlier', (151.483, 115.13499999999999, 150.62)), ('B', '76', 1, 'cablam Outlier', (151.8, 111.4, 150.1)), ('B', '77', 1, 'cablam CA Geom Outlier', (151.6, 110.7, 153.8)), ('B', '78', 1, 'smoc Outlier', (149.35100000000003, 107.669, 153.34)), ('B', '81', 1, 'side-chain clash', (147.846, 104.19, 147.982)), ('B', '84', 1, 'side-chain clash', (147.846, 104.19, 147.982)), ('B', '134', 2, 'Dihedral angle:CA:CB:CG:OD1', (102.708, 106.195, 134.07399999999998)), ('B', '136', 2, 'smoc Outlier', (99.66799999999999, 103.94200000000001, 129.695)), ('B', '161', 2, 'side-chain clash', (106.665, 102.375, 141.729)), ('B', '162', 2, 'side-chain clash', (108.882, 107.353, 141.372)), ('B', '174', 2, 'smoc Outlier', (93.709, 101.977, 135.89200000000002)), ('B', '177', 2, 'side-chain clash', (98.87, 104.788, 137.808)), ('B', '181', 2, 'Dihedral angle:CA:C', (104.253, 106.93100000000001, 143.596)), ('B', '182', 2, 'side-chain clash\nBond angle:CA:C\nBond angle:CA:CB:CG\nBond angle:N:CA:C\nDihedral angle:N:CA', (104.65499999999999, 106.952, 139.918)), ('B', '183', 2, 'side-chain clash\nBond angle:N\ncablam CA Geom Outlier', (108.20700000000001, 106.38499999999999, 138.692)), ('B', '184', 2, 'side-chain clash\nsmoc Outlier', (106.665, 102.375, 141.729)), ('B', '83', 3, 'side-chain clash', (142.488, 107.305, 143.443)), ('B', '87', 3, 'side-chain clash', (142.488, 107.305, 143.443)), ('B', '142', 4, 'smoc Outlier', (105.84, 95.589, 130.92800000000003)), ('B', '143', 4, 'smoc Outlier', (102.377, 94.057, 130.795)), ('D', '109', 1, 'smoc Outlier', (90.006, 124.403, 163.989)), ('D', '114', 1, 'backbone clash\nsmoc Outlier', (88.567, 117.63, 163.233)), ('D', '116', 1, 'side-chain clash', (91.629, 121.48, 159.021)), ('D', '117', 1, 'side-chain clash', (90.3, 112.584, 160.064)), ('D', '120', 1, 'side-chain clash', (90.804, 122.343, 155.991)), ('D', '129', 1, 'side-chain clash', (91.273, 113.169, 155.584)), ('D', '131', 1, 'backbone clash\nside-chain clash', (90.3, 112.584, 160.064)), ('D', '132', 1, 'smoc Outlier', (85.829, 116.22, 164.154)), ('D', '135', 1, 'side-chain clash', (80.11, 118.07, 167.596)), ('D', '138', 1, 'side-chain clash', (80.11, 118.07, 167.596)), ('D', '149', 1, 'side-chain clash\nsmoc Outlier', (91.629, 121.48, 159.021)), ('D', '159', 1, 'side-chain clash', (77.589, 110.108, 159.958)), ('D', '160', 1, 'side-chain clash', (80.898, 105.875, 156.629)), ('D', '161', 1, 'side-chain clash', (82.169, 106.35, 165.739)), ('D', '162', 1, 'side-chain clash', (86.544, 107.604, 166.122)), ('D', '164', 1, 'smoc Outlier', (84.24900000000001, 102.548, 160.864)), ('D', '166', 1, 'side-chain clash', (80.898, 105.875, 156.629)), ('D', '167', 1, 'side-chain clash', (77.589, 110.108, 159.958)), ('D', '172', 1, 'side-chain clash', (75.017, 112.37, 166.634)), ('D', '176', 1, 'smoc Outlier', (71.88, 111.092, 173.005)), ('D', '177', 1, 'side-chain clash', (78.714, 111.44, 171.828)), ('D', '180', 1, 'side-chain clash', (75.017, 112.37, 166.634)), ('D', '181', 1, 'side-chain clash\nDihedral angle:CA:C', (81.48400000000001, 107.29100000000001, 168.13)), ('D', '182', 1, 'side-chain clash\nDihedral angle:N:CA\nsmoc Outlier', (82.831, 110.79, 168.472)), ('D', '183', 1, 'side-chain clash\ncablam CA Geom Outlier', (86.544, 107.604, 166.122)), ('D', '184', 1, 'side-chain clash', (83.255, 112.651, 166.342)), ('D', '142', 2, 'smoc Outlier', (78.589, 121.884, 160.7)), ('D', '145', 2, 'cablam Outlier', (74.7, 119.4, 155.8)), ('D', '147', 2, 'side-chain clash', (81.641, 121.546, 153.762)), ('D', '154', 2, 'side-chain clash', (81.641, 121.546, 153.762)), ('D', '155', 2, 'smoc Outlier', (78.40400000000001, 119.68599999999999, 151.20499999999998)), ('D', '157', 2, 'side-chain clash', (81.123, 115.083, 147.712)), ('D', '189', 2, 'side-chain clash', (81.123, 115.083, 147.712)), ('D', '191', 2, 'smoc Outlier', (80.03, 123.936, 146.71599999999998)), ('D', '100', 3, 'side-chain clash', (95.513, 134.11, 155.692)), ('D', '101', 3, 'Dihedral angle:CA:CB:CG:OD1', (90.67799999999998, 134.903, 158.003)), ('D', '102', 3, 'smoc Outlier', (90.84700000000001, 131.608, 156.08100000000002)), ('D', '103', 3, 'side-chain clash', (94.922, 130.283, 154.641)), ('D', '151', 3, 'cablam Outlier', (86.0, 130.1, 155.2)), ('D', '90', 4, 'side-chain clash', (107.423, 133.446, 160.84)), ('D', '94', 4, 'side-chain clash', (107.423, 133.446, 160.84)), ('D', '97', 4, 'side-chain clash', (103.816, 137.57, 159.822)), ('D', '122', 5, 'side-chain clash', (90.1, 124.574, 146.985)), ('D', '190', 5, 'side-chain clash', (90.1, 124.574, 146.985))]
data['probe'] = [(' A  28  THR HG21', ' A  55  ARG  HD3', -0.862, (104.573, 132.349, 85.362)), (' D 161  ASP  HB2', ' D 181  ALA  HB3', -0.818, (82.169, 106.35, 165.739)), (' D 162  ALA  HB2', ' D 183  PRO  HG2', -0.769, (86.544, 107.604, 166.122)), (' A  15  SER  HB3', ' A 118  ARG HH21', -0.722, (102.904, 116.188, 77.384)), (' A  28  THR  O  ', ' A  28  THR HG22', -0.717, (105.416, 134.038, 85.521)), (' C  66  VAL HG13', ' C  67  ASP  H  ', -0.71, (102.653, 123.604, 166.176)), (' A  28  THR  CG2', ' A  55  ARG  HD3', -0.706, (104.757, 132.533, 85.37)), (' A 540  THR  CG2', ' A 667  VAL HG22', -0.7, (127.824, 113.683, 130.882)), (' A 312  ASN HD21', ' A 464  CYS  H  ', -0.695, (128.109, 120.519, 107.645)), (' A 225  THR HG22', ' A 226  THR  H  ', -0.66, (136.542, 118.804, 75.412)), (' B 162  ALA  HB2', ' B 183  PRO  HG2', -0.644, (108.882, 107.353, 141.372)), (' A 684  ASP  HB3', ' A 687  THR HG23', -0.636, (133.396, 123.204, 129.19)), (' A 164  ASP  OD1', ' A 165  PHE  N  ', -0.63, (111.131, 126.188, 117.386)), (' A 279  ARG HH12', ' A 352  GLY  HA2', -0.62, (133.988, 107.3, 111.278)), (' A 380  MET  HE1', ' B  95  LEU  HB3', -0.612, (136.839, 94.076, 136.188)), (' A  35  PHE  HZ ', ' A  50  LYS  HD3', -0.61, (114.622, 133.697, 87.324)), (' C  16  VAL HG11', ' D  91  LEU HD22', -0.609, (106.185, 126.053, 158.983)), (' B 177  SER  HG ', ' B 182  TRP  HZ2', -0.596, (98.87, 104.788, 137.808)), (' D 135  TYR  HB3', ' D 182  TRP  CH2', -0.596, (78.551, 115.275, 168.946)), (' A 540  THR HG21', ' A 667  VAL HG22', -0.592, (128.009, 114.333, 131.089)), (' D 177  SER  HB3', ' D 182  TRP  HZ2', -0.59, (76.954, 113.41, 171.654)), (' A  18  ARG  HB3', ' A  59  LYS  HG3', -0.59, (93.472, 120.727, 81.369)), (' A   8  LEU  HA ', ' A  11  VAL HG12', -0.582, (100.306, 127.262, 73.609)), (' B  83  VAL HG22', ' B  87  MET  HE3', -0.578, (142.488, 107.305, 143.443)), (' A 493  VAL HG13', ' A 573  GLN HE21', -0.578, (146.949, 125.3, 134.712)), (' A 695  ASN HD21', ' A 762  ALA  HB2', -0.572, (127.374, 137.562, 121.532)), (' D 120  ILE HD11', ' D 149  TYR  HE2', -0.57, (90.804, 122.343, 155.991)), (' A   9  ASN  O  ', ' A  12  CYS  SG ', -0.56, (99.401, 122.583, 71.022)), (' A 631  ARG  HG2', ' A 663  LEU HD13', -0.554, (131.216, 119.723, 121.687)), (' C  58  VAL HG22', ' D 119  ILE HG12', -0.553, (99.153, 118.722, 151.521)), (' A 330  VAL HG11', ' B 117  LEU HD13', -0.549, (133.027, 98.627, 126.807)), (' D 182  TRP  O  ', ' D 184  LEU HD12', -0.547, (83.255, 112.651, 166.342)), (' D 172  ILE  HA ', ' D 180  LEU HD21', -0.546, (75.017, 112.37, 166.634)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.54, (133.37, 148.49, 124.598)), (' A 540  THR HG22', ' A 667  VAL  HA ', -0.538, (128.15, 111.86, 131.978)), (' A 196  MET  HE3', ' A 232  PRO  HB3', -0.53, (128.281, 118.635, 85.321)), (' A 795  SER  HB3', ' A 798  LYS  HE2', -0.524, (112.214, 134.894, 121.257)), (' D 147  PHE  HB3', ' D 154  TRP  HB2', -0.512, (81.641, 121.546, 153.762)), (' A 324  THR HG22', ' A 396  PHE  HZ ', -0.511, (122.16, 101.033, 122.339)), (' A 755  MET  HG2', ' A 764  VAL HG22', -0.507, (129.338, 142.159, 117.537)), (' A 468  GLN  HA ', ' A 731  LEU HD22', -0.504, (131.809, 129.588, 103.01)), (' A 335  VAL HG22', ' A 363  SER  HB2', -0.504, (147.442, 94.109, 133.003)), (' C  52  MET  HG3', ' D 103  LEU HD21', -0.501, (97.94, 130.221, 154.003)), (' A 412  PRO  HG3', ' C  14  LEU HD23', -0.499, (110.969, 124.768, 149.642)), (' A 335  VAL  O  ', ' A 338  VAL HG22', -0.499, (144.519, 90.091, 136.441)), (' A 414  ASN  ND2', ' A 846  ASP  HB2', -0.496, (119.916, 127.488, 154.179)), (' A  72  VAL  HA ', ' A 115  SER  HA ', -0.493, (109.38, 127.253, 76.704)), (' A 483  TYR  HE1', ' A 582  THR HG21', -0.489, (143.552, 139.042, 124.085)), (' C  44  ASP  OD1', ' C  46  THR HG22', -0.484, (93.351, 136.926, 143.172)), (' D 135  TYR  HA ', ' D 138  TYR  HB3', -0.483, (80.11, 118.07, 167.596)), (' A 105  ARG  HG2', ' A 110  MET  SD ', -0.476, (106.737, 132.667, 61.545)), (' A 388  LEU HD23', ' A 397  SER  OG ', -0.473, (119.454, 103.592, 131.182)), (' D 114  CYS  HA ', ' D 131  VAL  O  ', -0.472, (88.567, 117.63, 163.233)), (' D 117  LEU  HB2', ' D 129  MET  HG3', -0.47, (91.273, 113.169, 155.584)), (' A 830  PRO  O  ', ' A 868  PRO  HG2', -0.463, (126.968, 149.471, 138.605)), (' A 569  ARG  O  ', ' A 573  GLN  HB2', -0.461, (146.465, 124.604, 131.26)), (' A 572  HIS  O  ', ' A 576  LEU  HG ', -0.459, (143.112, 127.638, 128.361)), (' A 116  ARG  HG3', ' A 119  LEU HD11', -0.455, (111.097, 124.374, 82.35)), (' B  67  MET  HB3', ' B  67  MET  HE2', -0.454, (166.939, 116.716, 140.237)), (' C  66  VAL HG13', ' C  67  ASP  N  ', -0.454, (102.569, 123.351, 167.198)), (' A 612  PRO  O  ', ' A 613  HIS  HD2', -0.453, (122.992, 153.899, 115.823)), (' A 324  THR HG22', ' A 396  PHE  CZ ', -0.453, (122.394, 101.514, 121.983)), (' D  90  MET  O  ', ' D  94  MET  HG3', -0.453, (107.423, 133.446, 160.84)), (' A 722  ASN  HB3', ' A 726  ARG  NH1', -0.45, (136.379, 143.849, 94.745)), (' A 180  GLU  HA ', ' A 180  GLU  OE1', -0.449, (113.116, 110.159, 99.872)), (' A  74  ARG  HD3', ' A 111  VAL HG11', -0.448, (110.623, 136.929, 70.842)), (' A 483  TYR  CE1', ' A 582  THR HG21', -0.448, (143.746, 138.545, 124.27)), (' A  60  ASP  HB3', ' A  64  ASN  OD1', -0.445, (93.462, 117.279, 88.215)), (' A 605  VAL HG22', ' A 756  MET  HB2', -0.444, (132.238, 145.308, 122.984)), (' A 708  LEU  HA ', ' A 708  LEU HD23', -0.444, (126.818, 138.133, 98.821)), (' A 658  GLU  O  ', ' A 662  VAL HG22', -0.444, (135.514, 117.506, 125.35)), (' B  81  ALA  HA ', ' B  84  THR HG22', -0.443, (147.846, 104.19, 147.982)), (' A  52  ASN  HB3', ' A  73  LYS  HE2', -0.442, (112.774, 134.232, 81.147)), (' A 494  ILE HD11', ' A 577  LYS  HE3', -0.44, (147.057, 131.382, 135.979)), (' A  29  ASP  HB3', ' A  51  THR HG22', -0.437, (108.862, 139.839, 85.472)), (' A 611  ASN  ND2', ' A 769  THR  OG1', -0.436, (124.666, 155.841, 107.967)), (' A 603  LYS  HA ', ' A 603  LYS  HD2', -0.435, (133.09, 154.456, 124.449)), (' A 462  THR  CG2', ' A 627  PRO  HB3', -0.435, (124.436, 121.549, 114.789)), (' D 116  PRO  HD3', ' D 149  TYR  OH ', -0.433, (91.629, 121.48, 159.021)), (' C  22  VAL HG23', ' C  29  TRP  HE3', -0.431, (107.944, 117.319, 151.542)), (' A 426  LYS  HA ', ' A 426  LYS  HD3', -0.431, (113.47, 152.197, 157.643)), (' A 273  TYR  HB3', ' B 116  PRO  HG3', -0.43, (131.299, 98.642, 117.721)), (' B 161  ASP  HA ', ' B 184  LEU HD23', -0.43, (106.665, 102.375, 141.729)), (' A 749  LEU  HA ', ' A 749  LEU HD23', -0.427, (132.209, 143.762, 109.299)), (' A 466  ILE  HA ', ' A 466  ILE HD12', -0.427, (131.724, 123.606, 106.226)), (' D 160  VAL HG22', ' D 166  ILE HD13', -0.427, (80.898, 105.875, 156.629)), (' C  31  GLN  NE2', ' D 119  ILE HD12', -0.426, (98.544, 117.243, 147.956)), (' A 171  ILE  HA ', ' A 171  ILE HD12', -0.425, (106.688, 120.782, 111.419)), (' D 100  ASN  HB3', ' D 103  LEU HD12', -0.425, (95.513, 134.11, 155.692)), (' A 614  LEU  HB2', ' A 802  GLU  HB3', -0.425, (121.882, 150.092, 121.632)), (' C  50  GLU  O  ', ' C  53  VAL HG22', -0.424, (94.671, 128.018, 150.089)), (' D 117  LEU HD11', ' D 131  VAL HG23', -0.424, (90.3, 112.584, 160.064)), (' B  73  GLN  CD ', ' B  73  GLN  H  ', -0.423, (155.265, 111.384, 145.316)), (' A 610  GLU  O  ', ' A 612  PRO  HD3', -0.422, (127.943, 156.807, 113.662)), (' D 159  VAL HG13', ' D 167  VAL HG13', -0.421, (77.589, 110.108, 159.958)), (' D 122  LEU  HA ', ' D 190  ARG HH21', -0.419, (90.1, 124.574, 146.985)), (' A 540  THR  CG2', ' A 667  VAL  HA ', -0.418, (128.008, 112.725, 132.22)), (' A 588  VAL  O  ', ' A 588  VAL HG13', -0.418, (134.575, 140.517, 128.136)), (' C  23  GLU  HA ', ' C  29  TRP  HB2', -0.416, (108.854, 115.173, 149.722)), (' A  98  LYS  HB3', ' A  98  LYS  HE2', -0.415, (110.541, 117.224, 76.064)), (' A 366  LEU  HB3', ' A 371  LEU  HG ', -0.413, (146.634, 100.225, 138.767)), (' A 838  LEU  HA ', ' A 838  LEU HD23', -0.411, (117.691, 143.673, 148.983)), (' A 722  ASN  HB3', ' A 726  ARG HH12', -0.409, (136.575, 144.274, 94.791)), (' A 196  MET  CE ', ' A 232  PRO  HB3', -0.409, (127.778, 118.682, 85.21)), (' A 131  LEU  HA ', ' A 131  LEU HD23', -0.409, (113.393, 127.427, 105.595)), (' D 157  GLN  HG3', ' D 189  LEU HD13', -0.409, (81.123, 115.083, 147.712)), (' A 131  LEU HD13', ' A 247  LEU HD23', -0.408, (115.341, 123.033, 106.414)), (' A  89  LEU  HA ', ' A  89  LEU HD23', -0.408, (124.255, 115.177, 71.617)), (' A 634  ALA  HA ', ' A 693  VAL HG11', -0.408, (135.972, 127.675, 117.982)), (' A 665  GLU  H  ', ' A 665  GLU  HG2', -0.408, (129.761, 114.195, 126.732)), (' C  53  VAL HG12', ' D 103  LEU  HG ', -0.407, (94.922, 130.283, 154.641)), (' A 494  ILE  O  ', ' A 494  ILE HG13', -0.406, (146.497, 128.516, 137.39)), (' C  46  THR  O  ', ' C  50  GLU  HG2', -0.406, (93.137, 132.563, 147.215)), (' D 177  SER  O  ', ' D 182  TRP  NE1', -0.405, (78.714, 111.44, 171.828)), (' A 304  ASP  N  ', ' A 304  ASP  OD1', -0.405, (143.586, 122.316, 110.05)), (' A 619  TYR  HB2', ' A 622  CYS  HB2', -0.405, (122.534, 130.505, 123.296)), (' A 462  THR HG21', ' A 627  PRO  HB3', -0.404, (123.966, 121.614, 114.575)), (' B 103  LEU  HA ', ' B 103  LEU HD12', -0.404, (130.459, 89.311, 126.975)), (' A 331  ARG  O  ', ' A 341  VAL  HA ', -0.404, (138.077, 94.649, 128.232)), (' A 615  MET  HB3', ' A 615  MET  HE2', -0.403, (123.702, 144.804, 117.024)), (' D  97  LYS  HB3', ' D  97  LYS  HE2', -0.402, (103.816, 137.57, 159.822)), (' A 816  HIS  O  ', ' A 830  PRO  HA ', -0.402, (125.603, 149.098, 134.441)), (' A 164  ASP  OD2', ' A 167  GLU  HB2', -0.4, (108.094, 126.899, 120.527)), (' B  68  THR  O  ', ' B  72  LYS  HG2', -0.4, (160.11, 114.058, 144.561))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (134.38, 107.98, 138.864))]
data['cablam'] = [('A', '26', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSS-S', (105.8, 138.1, 78.6)), ('A', '28', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nS-S--', (103.8, 135.7, 84.9)), ('A', '45', 'PHE', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (122.6, 133.8, 96.4)), ('A', '51', 'THR', 'check CA trace,carbonyls, peptide', ' \n-----', (110.9, 138.5, 84.2)), ('A', '52', 'ASN', 'check CA trace,carbonyls, peptide', ' \n-----', (111.3, 136.4, 81.1)), ('A', '53', 'CYS', 'check CA trace,carbonyls, peptide', ' \n----E', (108.9, 133.5, 81.2)), ('A', '62', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (88.6, 116.4, 85.8)), ('A', '107', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSS', (104.8, 140.5, 64.1)), ('A', '108', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nSSSSE', (107.1, 139.9, 61.1)), ('A', '213', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\nBTTS-', (110.9, 116.9, 91.1)), ('A', '218', 'ASP', 'check CA trace,carbonyls, peptide', ' \nB---S', (118.8, 125.8, 81.2)), ('A', '258', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nBTTS-', (116.6, 98.0, 99.9)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (133.6, 100.0, 111.6)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (131.2, 101.1, 108.8)), ('A', '363', 'SER', 'check CA trace,carbonyls, peptide', 'beta bridge\nSSB--', (149.8, 93.5, 131.8)), ('A', '432', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n-SS-S', (102.7, 149.7, 144.5)), ('A', '502', 'ALA', 'check CA trace,carbonyls, peptide', ' \nS---B', (136.4, 115.2, 140.6)), ('A', '509', 'TRP', 'check CA trace,carbonyls, peptide', 'turn\nTTT--', (137.2, 109.5, 147.7)), ('A', '586', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSSB-', (136.6, 141.5, 121.3)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTSS-S', (134.8, 154.2, 115.5)), ('A', '665', 'GLU', 'check CA trace,carbonyls, peptide', ' \nTS-EE', (130.5, 111.8, 127.1)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (124.4, 113.7, 122.5)), ('A', '823', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (134.2, 165.0, 138.3)), ('A', '845', 'ASP', 'check CA trace,carbonyls, peptide', ' \nEE-SS', (122.2, 129.4, 151.8)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (104.1, 117.5, 104.1)), ('A', '504', 'PHE', 'check CA trace', 'beta bridge\n--BTT', (132.8, 109.9, 138.7)), ('A', '607', 'SER', 'check CA trace', 'bend\nHTSS-', (135.3, 152.4, 118.8)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (126.1, 117.1, 122.6)), ('A', '733', 'ARG', 'check CA trace', 'bend\nHHS--', (135.4, 129.0, 94.2)), ('C', '45', 'THR', 'check CA trace,carbonyls, peptide', 'turn\n-STTH', (97.1, 138.3, 146.1)), ('C', '64', 'GLY', 'check CA trace,carbonyls, peptide', ' \nSS-SS', (100.7, 116.5, 166.2)), ('C', '65', 'ALA', 'check CA trace', 'bend\nS-SS-', (103.7, 118.6, 165.2)), ('B', '73', 'GLN', 'check CA trace,carbonyls, peptide', ' \nTS-SS', (154.7, 113.7, 145.4)), ('B', '74', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nS-SS-', (154.2, 116.3, 148.2)), ('B', '76', 'SER', 'check CA trace,carbonyls, peptide', ' \nSS-TT', (151.8, 111.4, 150.1)), ('B', '77', 'GLU', 'check CA trace', 'turn\nS-TTT', (151.6, 110.7, 153.8)), ('B', '183', 'PRO', 'check CA trace', 'bend\n-SSEE', (108.2, 106.4, 138.7)), ('D', '145', 'THR', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (74.7, 119.4, 155.8)), ('D', '151', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (86.0, 130.1, 155.2)), ('D', '183', 'PRO', 'check CA trace', 'bend\n-SSEE', (85.9, 111.1, 166.3))]
data['smoc'] = [('A', 4, u'ALA', 0.7581467115380897, (96.96700000000001, 134.373, 70.74100000000001)), ('A', 28, u'THR', 0.7298351234223951, (103.786, 135.671, 84.93700000000001)), ('A', 30, u'VAL', 0.7502494282321945, (105.301, 139.534, 89.021)), ('A', 46, u'ALA', 0.7739245502691106, (119.67099999999999, 136.21299999999997, 96.537)), ('A', 80, u'TYR', 0.8127327394030411, (118.87899999999999, 129.093, 71.04100000000001)), ('A', 83, u'GLU', 0.754349080957333, (121.251, 125.334, 73.886)), ('A', 84, u'GLU', 0.7414809234799772, (119.619, 123.20700000000001, 71.194)), ('A', 107, u'ASP', 0.678773007058761, (104.77499999999999, 140.46, 64.095)), ('A', 109, u'ASP', 0.7750808450078628, (109.921, 137.758, 62.358)), ('A', 116, u'ARG', 0.7271249554673124, (110.573, 123.41000000000001, 78.87599999999999)), ('A', 139, u'CYS', 0.7768335208836997, (107.206, 132.44899999999998, 104.758)), ('A', 146, u'LEU', 0.7792454776825043, (105.07799999999999, 122.195, 102.44000000000001)), ('A', 165, u'PHE', 0.7920366716780953, (111.596, 123.922, 117.076)), ('A', 167, u'GLU', 0.7272257606889662, (107.87899999999999, 124.495, 121.026)), ('A', 171, u'ILE', 0.7894279400783507, (107.809, 120.60499999999999, 112.74700000000001)), ('A', 183, u'ARG', 0.7510840815897196, (117.12799999999999, 112.412, 98.092)), ('A', 184, u'GLN', 0.787855073302166, (115.593, 111.831, 94.67099999999999)), ('A', 189, u'THR', 0.7615556982821331, (121.94100000000002, 115.25, 90.107)), ('A', 192, u'PHE', 0.7891550104421096, (123.04400000000001, 114.397, 85.292)), ('A', 201, u'ILE', 0.7822316547282344, (129.993, 119.142, 78.531)), ('A', 211, u'ASP', 0.6649430286392572, (112.923, 121.837, 89.806)), ('A', 216, u'TRP', 0.778083444839859, (117.43, 119.88, 85.13)), ('A', 260, u'ASP', 0.782001463953933, (112.801, 102.07799999999999, 100.006)), ('A', 279, u'ARG', 0.7530003791551051, (130.423, 105.43100000000001, 104.5)), ('A', 287, u'PHE', 0.7881086557022848, (128.313, 113.061, 96.254)), ('A', 312, u'ASN', 0.743391313283743, (130.93, 117.41300000000001, 108.222)), ('A', 325, u'SER', 0.7755679264977783, (127.71900000000001, 101.203, 117.52199999999999)), ('A', 352, u'GLY', 0.737538014260402, (134.945, 107.887, 112.73700000000001)), ('A', 361, u'LEU', 0.8293390009363087, (147.46800000000002, 93.17099999999999, 126.614)), ('A', 362, u'HIS', 0.7862037068330908, (148.796, 90.793, 129.28)), ('A', 410, u'VAL', 0.8028867077563833, (116.343, 120.533, 146.094)), ('A', 431, u'GLU', 0.7509348222542028, (102.337, 147.95000000000002, 147.914)), ('A', 444, u'GLN', 0.8026054217661318, (112.471, 120.783, 143.15800000000002)), ('A', 463, u'MET', 0.7000430233584081, (125.21600000000001, 119.289, 108.642)), ('A', 472, u'VAL', 0.7292307695074074, (134.156, 131.69, 108.74900000000001)), ('A', 487, u'CYS', 0.7794677834232143, (151.424, 123.268, 126.13199999999999)), ('A', 519, u'MET', 0.789133592649015, (150.0, 112.506, 141.64899999999997)), ('A', 531, u'THR', 0.7113862045256477, (146.348, 111.409, 126.26700000000001)), ('A', 539, u'ILE', 0.7369956591127999, (132.04299999999998, 109.807, 132.997)), ('A', 553, u'ARG', 0.8166212373474004, (113.251, 125.724, 136.151)), ('A', 557, u'VAL', 0.8230658128344588, (125.832, 121.43700000000001, 137.44299999999998)), ('A', 561, u'SER', 0.6695668586817868, (136.505, 113.68799999999999, 135.638)), ('A', 562, u'ILE', 0.7363686787835811, (139.781, 114.61999999999999, 137.24499999999998)), ('A', 576, u'LEU', 0.7627834782537409, (143.078, 130.895, 128.60399999999998)), ('A', 601, u'MET', 0.712176298179887, (134.83700000000002, 148.136, 127.586)), ('A', 602, u'LEU', 0.779176922376068, (132.089, 150.38000000000002, 126.252)), ('A', 613, u'HIS', 0.7501517871040736, (123.36, 151.575, 116.73700000000001)), ('A', 642, u'HIS', 0.7841874801167948, (149.92100000000002, 124.55499999999999, 119.252)), ('A', 646, u'CYS', 0.7622638902268376, (152.271, 119.312, 118.98700000000001)), ('A', 666, u'MET', 0.743235112685567, (128.629, 109.369, 129.23)), ('A', 697, u'CYS', 0.7558043935211056, (131.23899999999998, 132.21899999999997, 114.49000000000001)), ('A', 698, u'GLN', 0.7607928386268498, (127.49900000000001, 132.847, 114.426)), ('A', 702, u'ALA', 0.7502538400509078, (125.19, 136.295, 109.877)), ('A', 703, u'ASN', 0.7666445011556285, (127.35499999999999, 138.98700000000002, 108.29400000000001)), ('A', 715, u'ILE', 0.7888380450933162, (124.619, 148.267, 96.01100000000001)), ('A', 724, u'GLN', 0.7714107475554471, (130.657, 140.87, 97.812)), ('A', 770, u'TYR', 0.804628059498748, (124.798, 149.671, 106.11999999999999)), ('A', 780, u'LYS', 0.7778843369571625, (116.645, 139.071, 111.23400000000001)), ('A', 785, u'VAL', 0.7548160996913242, (121.30799999999999, 131.81, 110.789)), ('A', 796, u'GLU', 0.8086897030089565, (112.728, 139.14, 118.46100000000001)), ('A', 811, u'GLU', 0.7485868244328813, (121.74600000000001, 144.453, 129.016)), ('A', 839, u'GLY', 0.7666194515633893, (116.327, 138.82500000000002, 146.696)), ('A', 842, u'CYS', 0.7719459166472825, (116.782, 138.226, 151.90800000000002)), ('A', 865, u'ASP', 0.6989440386014651, (127.364, 145.414, 143.383)), ('A', 877, u'TYR', 0.7626886469348377, (116.789, 152.407, 143.577)), ('A', 880, u'VAL', 0.7574681720122892, (118.251, 150.15200000000002, 148.05200000000002)), ('A', 885, u'LEU', 0.7788568048222971, (124.66499999999999, 150.277, 154.031)), ('A', 894, u'GLU', 0.7350664376285976, (126.42, 144.036, 166.499)), ('C', 10, u'SER', 0.6638511168754051, (105.71100000000001, 130.142, 151.875)), ('C', 17, u'LEU', 0.7357621070808131, (107.85199999999999, 120.84700000000001, 156.04299999999998)), ('C', 30, u'ALA', 0.7562056748851003, (105.68499999999999, 116.8, 144.742)), ('C', 47, u'GLU', 0.7179154694203221, (94.938, 132.80800000000002, 144.76899999999998)), ('C', 50, u'GLU', 0.7100661903918377, (94.222, 129.97, 148.441)), ('C', 54, u'SER', 0.7011767865559984, (96.136, 124.44600000000001, 150.86200000000002)), ('C', 57, u'SER', 0.7282137770618329, (96.806, 122.04700000000001, 155.595)), ('C', 63, u'GLN', 0.6536492366228964, (97.96700000000001, 115.084, 163.971)), ('C', 64, u'GLY', 0.7328033417512638, (100.722, 116.453, 166.189)), ('B', 67, u'MET', 0.604906068674995, (164.596, 117.87299999999999, 141.11499999999998)), ('B', 70, u'MET', 0.6560165152942798, (159.072, 116.485, 140.17399999999998)), ('B', 75, u'ARG', 0.6751326865951345, (151.483, 115.13499999999999, 150.62)), ('B', 78, u'ASP', 0.7979773762185212, (149.35100000000003, 107.669, 153.34)), ('B', 99, u'ASP', 0.7056509855508165, (134.131, 87.57499999999999, 134.865)), ('B', 111, u'ARG', 0.7661808009663171, (136.395, 90.24700000000001, 114.115)), ('B', 136, u'ASN', 0.7894495642507235, (99.66799999999999, 103.94200000000001, 129.695)), ('B', 142, u'CYS', 0.8077591112987136, (105.84, 95.589, 130.92800000000003)), ('B', 143, u'ASP', 0.8030089764900985, (102.377, 94.057, 130.795)), ('B', 174, u'MET', 0.7597790072644685, (93.709, 101.977, 135.89200000000002)), ('B', 184, u'LEU', 0.767831310231194, (107.979, 102.614, 138.98200000000003)), ('B', 192, u'ASN', 0.7824991281753445, (116.41400000000002, 81.221, 128.909)), ('D', 87, u'MET', 0.699121240449988, (111.91300000000001, 127.73, 162.877)), ('D', 102, u'ALA', 0.7429850398559311, (90.84700000000001, 131.608, 156.08100000000002)), ('D', 109, u'ASN', 0.7217730714125591, (90.006, 124.403, 163.989)), ('D', 114, u'CYS', 0.7567557909353365, (89.13, 119.535, 163.946)), ('D', 132, u'ILE', 0.7234725631386043, (85.829, 116.22, 164.154)), ('D', 142, u'CYS', 0.665339329343377, (78.589, 121.884, 160.7)), ('D', 149, u'TYR', 0.7746047884420643, (85.92, 125.27199999999999, 156.72899999999998)), ('D', 155, u'GLU', 0.6999812455361878, (78.40400000000001, 119.68599999999999, 151.20499999999998)), ('D', 164, u'SER', 0.7590136009676947, (84.24900000000001, 102.548, 160.864)), ('D', 176, u'ASN', 0.6278961437854762, (71.88, 111.092, 173.005)), ('D', 182, u'TRP', 0.6803073450448482, (82.831, 110.79, 168.472)), ('D', 191, u'ALA', 0.7959154965880194, (80.03, 123.936, 146.71599999999998))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30178/7btf/Model_validation_1/validation_cootdata/molprobity_probe7btf_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

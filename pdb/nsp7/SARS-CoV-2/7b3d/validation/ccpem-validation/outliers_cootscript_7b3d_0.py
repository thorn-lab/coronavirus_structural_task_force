
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
data['clusters'] = [('A', '480', 1, 'side-chain clash', (89.685, 103.746, 91.018)), ('A', '626', 1, 'side-chain clash', (98.553, 105.055, 98.72)), ('A', '631', 1, 'side-chain clash', (98.21, 107.413, 99.069)), ('A', '634', 1, 'smoc Outlier', (94.405, 108.45, 92.39)), ('A', '635', 1, 'side-chain clash\nsmoc Outlier', (94.98, 110.722, 96.442)), ('A', '680', 1, 'side-chain clash', (98.553, 105.055, 98.72)), ('A', '691', 1, 'backbone clash', (94.544, 99.235, 98.266)), ('A', '692', 1, 'smoc Outlier', (92.106, 100.255, 94.41700000000002)), ('A', '693', 1, 'side-chain clash', (89.685, 103.746, 91.018)), ('A', '756', 1, 'smoc Outlier', (88.93, 91.724, 90.667)), ('A', '758', 1, 'backbone clash\nDihedral angle:CA:C', (89.765, 95.006, 96.66799999999999)), ('A', '759', 1, 'backbone clash\nDihedral angle:N:CA\nDihedral angle:CA:C\nsmoc Outlier', (92.0, 97.826, 97.831)), ('A', '760', 1, 'backbone clash\nDihedral angle:N:CA', (95.17899999999999, 95.777, 97.95400000000001)), ('A', '761', 1, 'smoc Outlier', (94.21600000000001, 92.35199999999999, 96.65299999999999)), ('A', '238', 2, 'side-chain clash', (111.792, 111.289, 80.825)), ('A', '239', 2, 'side-chain clash\nsmoc Outlier', (106.864, 108.632, 78.8)), ('A', '242', 2, 'side-chain clash', (111.792, 111.289, 80.825)), ('A', '465', 2, 'side-chain clash\nsmoc Outlier', (106.864, 108.632, 78.8)), ('A', '468', 2, 'smoc Outlier', (102.85499999999999, 106.55499999999999, 80.346)), ('A', '470', 2, 'side-chain clash', (96.847, 109.293, 81.826)), ('A', '472', 2, 'side-chain clash\nsmoc Outlier', (94.686, 104.164, 83.677)), ('A', '473', 2, 'side-chain clash', (96.847, 109.293, 81.826)), ('A', '476', 2, 'side-chain clash', (94.686, 104.164, 83.677)), ('A', '729', 2, 'Dihedral angle:CB:CG:CD:OE1', (101.542, 106.513, 68.769)), ('A', '731', 2, 'smoc Outlier', (102.012, 107.233, 74.109)), ('A', '863', 3, 'smoc Outlier', (81.259, 79.432, 113.271)), ('A', '865', 3, 'smoc Outlier', (83.121, 82.136, 109.073)), ('A', '885', 3, 'side-chain clash', (75.392, 75.068, 116.523)), ('A', '892', 3, 'side-chain clash', (69.835, 79.034, 124.583)), ('A', '912', 3, 'side-chain clash', (69.835, 79.034, 124.583)), ('A', '914', 3, 'smoc Outlier', (69.551, 77.505, 115.732)), ('A', '915', 3, 'side-chain clash', (71.345, 80.117, 121.067)), ('A', '916', 3, 'side-chain clash', (75.392, 75.068, 116.523)), ('A', '921', 3, 'side-chain clash', (76.847, 76.132, 114.008)), ('A', '452', 4, 'side-chain clash', (102.465, 101.251, 111.499)), ('A', '544', 4, 'side-chain clash', (102.001, 101.863, 116.231)), ('A', '556', 4, 'side-chain clash', (102.001, 101.863, 116.231)), ('A', '557', 4, 'smoc Outlier', (97.143, 103.29, 112.077)), ('A', '682', 4, 'smoc Outlier', (95.35799999999999, 104.339, 106.61999999999999)), ('A', '683', 4, 'smoc Outlier', (92.79, 106.584, 108.339)), ('A', '755', 4, 'side-chain clash\nbackbone clash', (88.688, 106.526, 105.389)), ('A', '764', 4, 'side-chain clash\nbackbone clash', (88.688, 106.526, 105.389)), ('A', '459', 5, 'smoc Outlier', (109.16999999999999, 106.088, 100.595)), ('A', '462', 5, 'side-chain clash', (109.966, 105.9, 93.885)), ('A', '677', 5, 'cablam Outlier', (108.1, 111.9, 103.7)), ('A', '678', 5, 'cablam CA Geom Outlier', (105.1, 110.5, 101.7)), ('A', '785', 5, 'smoc Outlier', (106.71100000000001, 97.779, 87.235)), ('A', '789', 5, 'smoc Outlier', (107.79, 102.649, 89.795)), ('A', '791', 5, 'side-chain clash', (109.966, 105.9, 93.885)), ('A', '608', 6, 'Dihedral angle:CA:CB:CG:OD1', (84.881, 85.4, 78.361)), ('A', '610', 6, 'Dihedral angle:CB:CG:CD:OE1', (89.79100000000001, 82.27799999999999, 75.705)), ('A', '611', 6, 'backbone clash', (95.024, 82.101, 78.626)), ('A', '612', 6, 'side-chain clash', (89.221, 80.063, 82.075)), ('A', '768', 6, 'side-chain clash\nbackbone clash', (95.024, 82.101, 78.626)), ('A', '805', 6, 'side-chain clash', (89.221, 80.063, 82.075)), ('A', '335', 7, 'side-chain clash', (93.911, 138.257, 119.22)), ('A', '336', 7, 'smoc Outlier', (91.428, 140.671, 118.971)), ('A', '338', 7, 'side-chain clash', (98.026, 138.005, 122.029)), ('A', '339', 7, 'side-chain clash', (98.026, 138.005, 122.029)), ('A', '340', 7, 'smoc Outlier', (98.733, 134.63, 116.94300000000001)), ('A', '811', 8, 'Dihedral angle:CB:CG:CD:OE1', (93.862, 83.23, 98.10799999999999)), ('A', '815', 8, 'smoc Outlier', (90.139, 83.223, 102.07499999999999)), ('A', '816', 8, 'side-chain clash', (90.772, 77.243, 101.292)), ('A', '831', 8, 'side-chain clash', (90.772, 77.243, 101.292)), ('A', '291', 9, 'side-chain clash', (86.921, 126.575, 120.115)), ('A', '368', 9, 'side-chain clash', (85.405, 125.659, 115.355)), ('A', '369', 9, 'smoc Outlier', (84.93400000000001, 127.26400000000001, 112.546)), ('A', '372', 9, 'side-chain clash', (85.405, 125.659, 115.355)), ('A', '836', 10, 'Dihedral angle:CD:NE:CZ:NH1', (93.195, 82.039, 112.238)), ('A', '837', 10, 'side-chain clash', (88.401, 80.065, 116.209)), ('A', '841', 10, 'smoc Outlier', (88.55199999999999, 81.64, 119.535)), ('A', '884', 10, 'side-chain clash', (88.401, 80.065, 116.209)), ('A', '504', 11, 'cablam Outlier', (95.0, 115.6, 117.8)), ('A', '506', 11, 'smoc Outlier', (90.708, 117.304, 119.29)), ('A', '507', 11, 'backbone clash\nside-chain clash\nsmoc Outlier', (92.901, 114.756, 122.312)), ('A', '508', 11, 'backbone clash', (92.901, 114.756, 122.312)), ('A', '206', 12, 'side-chain clash', (118.09, 106.517, 67.782)), ('A', '209', 12, 'side-chain clash', (121.816, 107.939, 67.004)), ('A', '218', 12, 'side-chain clash', (121.816, 107.939, 67.004)), ('A', '699', 13, 'smoc Outlier', (97.985, 96.60499999999999, 86.363)), ('A', '703', 13, 'smoc Outlier', (100.018, 95.533, 80.54)), ('A', '706', 13, 'smoc Outlier', (104.32, 94.008, 78.35199999999999)), ('A', '818', 14, 'side-chain clash\nsmoc Outlier', (83.606, 73.809, 98.132)), ('A', '820', 14, 'side-chain clash', (83.606, 73.809, 98.132)), ('A', '829', 14, 'smoc Outlier', (82.742, 78.657, 98.459)), ('A', '711', 15, 'smoc Outlier', (109.21300000000001, 92.44900000000001, 69.396)), ('A', '712', 15, 'side-chain clash', (104.21, 92.602, 67.953)), ('A', '715', 15, 'side-chain clash', (104.21, 92.602, 67.953)), ('A', '531', 16, 'side-chain clash', (87.562, 121.303, 104.546)), ('A', '563', 16, 'side-chain clash', (87.358, 118.796, 107.225)), ('A', '567', 16, 'side-chain clash', (87.358, 118.796, 107.225)), ('A', '847', 17, 'side-chain clash', (86.714, 88.436, 130.504)), ('A', '850', 17, 'side-chain clash', (86.714, 88.436, 130.504)), ('A', '851', 17, 'cablam CA Geom Outlier', (83.4, 84.6, 129.4)), ('A', '478', 18, 'side-chain clash', (86.305, 104.843, 76.688)), ('A', '740', 18, 'Dihedral angle:CA:CB:CG:OD1', (88.648, 105.809, 70.40100000000001)), ('A', '743', 18, 'side-chain clash', (86.305, 104.843, 76.688)), ('A', '877', 19, 'smoc Outlier', (89.21400000000001, 71.283, 108.94100000000002)), ('A', '878', 19, 'smoc Outlier', (85.621, 70.042, 109.065)), ('A', '879', 19, 'Dihedral angle:CA:CB:CG:OD1', (85.99000000000001, 69.03, 112.71900000000001)), ('A', '613', 20, 'side-chain clash\nsmoc Outlier', (96.553, 77.708, 84.718)), ('A', '802', 20, 'smoc Outlier', (96.548, 78.895, 89.252)), ('A', '803', 20, 'side-chain clash', (96.553, 77.708, 84.718)), ('A', '211', 21, 'backbone clash\nsmoc Outlier', (128.369, 107.704, 76.159)), ('A', '213', 21, 'backbone clash', (128.369, 107.704, 76.159)), ('A', '665', 22, 'cablam Outlier', (101.0, 116.0, 106.7)), ('A', '666', 22, 'smoc Outlier', (102.408, 116.485, 110.22)), ('A', '615', 23, 'side-chain clash', (97.563, 86.535, 84.411)), ('A', '766', 23, 'side-chain clash', (97.563, 86.535, 84.411)), ('A', '329', 24, 'smoc Outlier', (103.81, 128.60299999999998, 105.63)), ('A', '346', 24, 'smoc Outlier', (101.899, 125.666, 102.1)), ('A', '276', 25, 'side-chain clash', (111.023, 129.133, 88.626)), ('A', '280', 25, 'side-chain clash', (111.023, 129.133, 88.626)), ('A', '122', 26, 'side-chain clash', (127.533, 93.077, 78.452)), ('A', '144', 26, 'side-chain clash\nsmoc Outlier', (127.533, 93.077, 78.452)), ('A', '358', 27, 'smoc Outlier', (91.018, 134.313, 102.55799999999999)), ('A', '534', 27, 'smoc Outlier', (92.326, 127.654, 101.46300000000001)), ('A', '299', 28, 'side-chain clash', (97.307, 125.913, 94.385)), ('A', '652', 28, 'side-chain clash', (97.307, 125.913, 94.385)), ('A', '867', 29, 'side-chain clash', (76.037, 73.561, 104.677)), ('A', '922', 29, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (73.90400000000001, 76.393, 105.905)), ('A', '426', 30, 'side-chain clash', (83.109, 68.306, 120.257)), ('A', '886', 30, 'side-chain clash', (83.109, 68.306, 120.257)), ('A', '308', 31, 'smoc Outlier', (100.253, 115.697, 86.827)), ('A', '312', 31, 'smoc Outlier', (106.104, 115.086, 88.013)), ('A', '388', 32, 'smoc Outlier', (113.647, 117.95400000000001, 119.037)), ('A', '390', 32, 'smoc Outlier', (115.51100000000001, 112.137, 117.31400000000001)), ('A', '381', 33, 'smoc Outlier', (101.71000000000001, 123.57199999999999, 118.4)), ('A', '385', 33, 'smoc Outlier', (106.955, 123.17299999999999, 121.13199999999999)), ('A', '151', 34, 'cablam CA Geom Outlier', (129.4, 101.7, 90.6)), ('A', '178', 34, 'smoc Outlier', (125.811, 106.301, 88.17999999999999)), ('A', '451', 35, 'smoc Outlier', (110.22, 101.889, 114.853)), ('A', '454', 35, 'Dihedral angle:CA:CB:CG:OD1', (110.827, 104.356, 110.59400000000001)), ('A', '575', 36, 'smoc Outlier', (81.327, 108.55799999999999, 94.821)), ('A', '576', 36, 'smoc Outlier', (82.46000000000001, 106.23, 97.607)), ('A', '185', 37, 'smoc Outlier', (124.293, 112.818, 79.37199999999999)), ('A', '188', 37, 'smoc Outlier', (125.089, 116.766, 76.37499999999999)), ('A', '254', 38, 'smoc Outlier', (122.617, 120.67199999999998, 92.065)), ('A', '259', 38, 'side-chain clash', (127.279, 120.22, 89.006)), ('A', '726', 39, 'side-chain clash\nsmoc Outlier', (92.299, 100.205, 67.741)), ('A', '744', 39, 'side-chain clash', (92.299, 100.205, 67.741)), ('A', '734', 40, 'backbone clash', (96.41, 112.147, 71.454)), ('A', '736', 40, 'backbone clash', (96.41, 112.147, 71.454)), ('A', '749', 41, 'backbone clash\nsmoc Outlier', (91.853, 91.496, 79.68)), ('A', '753', 41, 'backbone clash\nsmoc Outlier', (91.853, 91.496, 79.68)), ('A', '887', 42, 'side-chain clash', (80.847, 77.2, 124.448)), ('A', '891', 42, 'side-chain clash', (80.847, 77.2, 124.448)), ('A', '155', 43, 'backbone clash', (131.203, 93.162, 95.364)), ('A', '156', 43, 'backbone clash', (131.203, 93.162, 95.364)), ('A', '804', 44, 'side-chain clash', (89.793, 72.315, 88.183)), ('A', '806', 44, 'side-chain clash', (89.793, 72.315, 88.183)), ('B', '157', 1, 'smoc Outlier', (120.84400000000001, 120.49700000000001, 131.836)), ('B', '159', 1, 'side-chain clash', (122.9, 111.091, 129.998)), ('B', '167', 1, 'smoc Outlier', (121.039, 109.542, 134.76399999999998)), ('B', '172', 1, 'side-chain clash\ncablam Outlier', (122.9, 111.091, 129.998)), ('B', '186', 1, 'side-chain clash', (121.322, 115.009, 128.575)), ('B', '79', 2, 'side-chain clash', (81.968, 121.613, 123.832)), ('B', '80', 2, 'side-chain clash\nsmoc Outlier', (82.399, 125.712, 121.433)), ('B', '83', 2, 'side-chain clash', (81.968, 121.613, 123.832)), ('B', '84', 2, 'side-chain clash', (82.399, 125.712, 121.433)), ('B', '87', 2, 'side-chain clash', (86.921, 126.575, 120.115)), ('B', '118', 3, 'smoc Outlier', (109.718, 123.86, 110.616)), ('B', '119', 3, 'smoc Outlier', (112.384, 126.545, 111.057)), ('B', '120', 3, 'side-chain clash', (111.223, 128.84, 117.075)), ('B', '124', 3, 'side-chain clash', (111.223, 128.84, 117.075)), ('B', '125', 3, 'smoc Outlier', (113.284, 127.09700000000001, 120.85)), ('B', '129', 4, 'smoc Outlier', (115.52799999999999, 117.57199999999999, 123.667)), ('B', '131', 4, 'side-chain clash', (114.12, 111.46, 123.983)), ('B', '185', 4, 'side-chain clash', (114.12, 111.46, 123.983)), ('B', '111', 5, 'Dihedral angle:CD:NE:CZ:NH1', (110.67399999999999, 140.441, 103.074)), ('B', '112', 5, 'smoc Outlier', (107.32, 138.73399999999998, 102.473)), ('B', '136', 6, 'side-chain clash', (129.829, 104.064, 119.559)), ('B', '139', 6, 'side-chain clash', (129.829, 104.064, 119.559)), ('B', '134', 7, 'smoc Outlier', (122.789, 104.018, 121.67199999999998)), ('B', '182', 7, 'cablam CA Geom Outlier', (118.2, 103.3, 126.5)), ('B', '101', 8, 'backbone clash', (112.508, 136.132, 120.215)), ('B', '102', 8, 'backbone clash', (112.508, 136.132, 120.215)), ('C', '14', 1, 'side-chain clash', (102.222, 89.077, 126.001)), ('C', '15', 1, 'smoc Outlier', (100.032, 88.63199999999999, 131.054)), ('C', '33', 1, 'smoc Outlier', (108.515, 90.63799999999999, 125.307)), ('C', '34', 1, 'side-chain clash', (111.684, 89.763, 121.331)), ('C', '36', 1, 'side-chain clash', (105.066, 87.667, 125.204)), ('C', '1', 2, 'smoc Outlier', (100.584, 68.87299999999999, 122.753)), ('C', '2', 2, 'side-chain clash', (103.043, 72.689, 125.874)), ('C', '5', 2, 'side-chain clash\nbackbone clash\nsmoc Outlier', (103.043, 72.689, 125.874)), ('C', '6', 2, 'backbone clash', (102.594, 73.443, 126.069)), ('C', '9', 2, 'side-chain clash', (101.296, 76.525, 128.165)), ('C', '17', 3, 'side-chain clash', (104.845, 92.954, 134.129)), ('C', '22', 3, 'side-chain clash\nsmoc Outlier', (104.845, 92.954, 134.129)), ('C', '28', 3, 'side-chain clash', (110.306, 93.258, 134.798)), ('C', '40', 4, 'backbone clash', (104.893, 79.373, 117.9)), ('C', '7', 4, 'backbone clash', (104.893, 79.373, 117.9)), ('C', '50', 5, 'Dihedral angle:CB:CG:CD:OE1', (114.203, 77.01, 127.582)), ('C', '52', 5, 'smoc Outlier', (109.617, 79.55799999999999, 129.1)), ('C', '44', 6, 'smoc Outlier', (111.554, 73.81400000000001, 118.21100000000001)), ('C', '59', 6, 'side-chain clash', (108.084, 85.527, 139.034)), ('T', '9', 1, 'side-chain clash', (88.688, 106.526, 105.389)), ('T', '18', 1, 'Backbone torsion suites: ', (61.842999999999996, 99.49100000000001, 119.513))]
data['probe'] = [(' A 206  THR  OG1', ' A 209  ASN  OD1', -0.879, (118.09, 106.517, 67.782)), (' A 239  SER  OG ', ' A 465  ASP  OD1', -0.835, (106.864, 108.632, 78.8)), (' A 804  ASP  OD2', ' A 806  THR  OG1', -0.829, (89.793, 72.315, 88.183)), (' A 122  TYR  OH ', ' A 144  GLU  OE1', -0.754, (127.533, 93.077, 78.452)), (' A 452  ASP  OD2', ' A 556  THR  OG1', -0.75, (102.465, 101.251, 111.499)), (' A 631  ARG  NH1', ' A 635  SER  OG ', -0.724, (94.98, 110.722, 96.442)), (' B  83  VAL HG12', ' B  87  MET  HE2', -0.719, (85.877, 123.831, 120.21)), (' B 131  VAL HG22', ' B 185  ILE  CD1', -0.692, (114.777, 110.767, 123.746)), (' C   7  LYS  NZ ', ' C  40  LEU  O  ', -0.67, (104.893, 79.373, 117.9)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.657, (105.066, 87.667, 125.204)), (' A 867  TYR  OH ', ' A 922  GLU  OE2', -0.643, (76.037, 73.561, 104.677)), (' A 531  THR HG21', ' A 567  THR HG21', -0.643, (87.562, 121.303, 104.546)), (' A 335  VAL  O  ', ' A 338  VAL HG12', -0.636, (93.911, 138.257, 119.22)), (' A 299  VAL HG22', ' A 652  PHE  CE2', -0.626, (97.198, 126.468, 93.538)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.611, (91.398, 115.075, 119.134)), (' C   5  ASP  O  ', ' C   9  THR HG23', -0.584, (101.296, 76.525, 128.165)), (' B 101  ASP  OD1', ' B 102  ALA  N  ', -0.582, (112.508, 136.132, 120.215)), (' A 412  PRO  HB3', ' C  14  LEU HD23', -0.581, (102.222, 89.077, 126.001)), (' A 478  LYS  NZ ', ' A 743  ASN  OD1', -0.562, (86.305, 104.843, 76.688)), (' A 885  LEU HD21', ' A 921  TYR  CE1', -0.559, (76.847, 76.132, 114.008)), (' A 887  TYR  CZ ', ' A 891  LEU HD11', -0.551, (82.9, 77.868, 125.579)), (' A 912  THR  HG1', ' A 915  TYR  HD2', -0.54, (71.345, 80.117, 121.067)), (' A 726  ARG  NH1', ' A 744  GLU  OE1', -0.534, (92.299, 100.205, 67.741)), (' A 892  HIS  CE1', ' A 912  THR HG21', -0.532, (69.835, 79.034, 124.583)), (' A 612  PRO  CG ', ' A 805  LEU HD11', -0.532, (89.221, 80.063, 82.075)), (' C  59  LEU  O  ', ' C  59  LEU HD23', -0.526, (107.988, 86.238, 139.548)), (' B 131  VAL HG22', ' B 185  ILE HD12', -0.526, (114.12, 111.46, 123.983)), (' C   5  ASP  OD1', ' C   6  VAL  N  ', -0.525, (102.594, 73.443, 126.069)), (' A 472  VAL  O  ', ' A 476  VAL HG23', -0.524, (94.686, 104.164, 83.677)), (' A 885  LEU HD22', ' A 916  TRP  HA ', -0.52, (75.392, 75.068, 116.523)), (' B 120  ILE  O  ', ' B 124  THR  OG1', -0.519, (111.223, 128.84, 117.075)), (' A 749  LEU  O  ', ' A 753  PHE  N  ', -0.518, (91.853, 91.496, 79.68)), (' A 734  ASN  ND2', ' A 736  ASP  O  ', -0.501, (96.41, 112.147, 71.454)), (' A 259  THR  O  ', ' A 259  THR HG22', -0.499, (127.279, 120.22, 89.006)), (' C  22  VAL HG23', ' C  28  LEU HD23', -0.494, (110.306, 93.258, 134.798)), (' A 887  TYR  O  ', ' A 891  LEU HD13', -0.487, (80.847, 77.2, 124.448)), (' A 462  THR  OG1', ' A 791  ASN  OD1', -0.484, (109.966, 105.9, 93.885)), (' A 299  VAL HG22', ' A 652  PHE  HE2', -0.479, (97.307, 125.913, 94.385)), (' B  80  ARG  O  ', ' B  84  THR HG23', -0.477, (82.399, 125.712, 121.433)), (' B 159  VAL HG22', ' B 186  VAL HG23', -0.472, (121.322, 115.009, 128.575)), (' A 615  MET  HE3', ' A 766  PHE  CD1', -0.472, (97.563, 86.535, 84.411)), (' A 155  ASP  OD1', ' A 156  TYR  N  ', -0.47, (131.203, 93.162, 95.364)), (' A 544  LEU HD23', ' A 556  THR HG22', -0.468, (102.001, 101.863, 116.231)), (' A 712  GLY  HA2', ' A 715  ILE HD12', -0.468, (104.21, 92.602, 67.953)), (' C  59  LEU  C  ', ' C  59  LEU HD23', -0.461, (108.084, 85.527, 139.034)), (' A 613  HIS  CD2', ' A 768  SER  OG ', -0.459, (96.523, 79.932, 80.331)), (' A 276  THR  O  ', ' A 280  LEU HD23', -0.455, (111.023, 129.133, 88.626)), (' A 209  ASN  HB3', ' A 218  ASP  HB2', -0.449, (121.816, 107.939, 67.004)), (' B  79  LYS  O  ', ' B  83  VAL HG23', -0.439, (81.968, 121.613, 123.832)), (' C   2  LYS  O  ', ' C   5  ASP  OD1', -0.438, (103.043, 72.689, 125.874)), (' A 470  LEU  O  ', ' A 473  VAL HG12', -0.437, (96.847, 109.293, 81.826)), (' A 837  ILE  O  ', ' A 884  TYR  OH ', -0.436, (88.401, 80.065, 116.209)), (' A 818  MET  HG3', ' A 820  VAL HG13', -0.433, (83.606, 73.809, 98.132)), (' A 211  ASP  OD1', ' A 213  ASN  N  ', -0.431, (128.369, 107.704, 76.159)), (' A 755  MET  HG2', ' A 764  VAL HG22', -0.43, (93.467, 91.949, 86.855)), (' A 684  ASP  O  ', " T   9    C  O2'", -0.43, (88.688, 106.526, 105.389)), (' A 631  ARG  HD3', ' A 680  THR HG22', -0.424, (98.21, 107.413, 99.069)), (' A 847  ILE  O  ', ' A 850  THR HG22', -0.422, (86.714, 88.436, 130.504)), (' B 136  ASN  HA ', ' B 139  LYS  NZ ', -0.422, (129.307, 105.472, 119.62)), (' A 368  PHE  O  ', ' A 372  LEU HD13', -0.421, (85.405, 125.659, 115.355)), (' A 691  ASN  HB3', ' A 759  SER  O  ', -0.42, (94.544, 99.235, 98.266)), (' A 480  PHE  CZ ', ' A 693  VAL HG22', -0.419, (89.685, 103.746, 91.018)), (' A 626  MET  CE ', ' A 680  THR HG21', -0.418, (98.553, 105.055, 98.72)), (' C  17  LEU  O  ', ' C  22  VAL HG12', -0.418, (104.845, 92.954, 134.129)), (' A 238  TYR  O  ', ' A 242  MET  HG3', -0.417, (111.792, 111.289, 80.825)), (' C  34  GLN  HA ', ' C  34  GLN  OE1', -0.417, (111.684, 89.763, 121.331)), (' A 613  HIS  HD1', ' A 803  THR  HA ', -0.417, (96.553, 77.708, 84.718)), (' A 611  ASN  O  ', ' A 768  SER  N  ', -0.415, (95.024, 82.101, 78.626)), (' A 563  CYS  O  ', ' A 567  THR HG23', -0.415, (87.358, 118.796, 107.225)), (' A 507  ASN  OD1', ' A 508  LYS  N  ', -0.409, (92.901, 114.756, 122.312)), (' A 426  LYS  NZ ', ' A 886  GLN  OE1', -0.406, (83.109, 68.306, 120.257)), (' A 758  LEU  O  ', ' A 760  ASP  N  ', -0.406, (92.685, 95.878, 98.091)), (' B 136  ASN  OD1', ' B 139  LYS  NZ ', -0.406, (129.829, 104.064, 119.559)), (' A 816  HIS  HB2', ' A 831  TYR  CZ ', -0.406, (90.772, 77.243, 101.292)), (' A 291  ASP  N  ', ' A 291  ASP  OD1', -0.405, (107.832, 120.224, 74.539)), (' A 371  LEU HD23', ' B  87  MET  HE3', -0.404, (86.921, 126.575, 120.115)), (' A 338  VAL  CG2', ' A 339  PRO  HD2', -0.402, (98.026, 138.005, 122.029)), (' B 159  VAL HG11', ' B 172  ILE HD11', -0.401, (122.9, 111.091, 129.998))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (94.56300000000007, 118.052, 118.05300000000001)), ('B', ' 183 ', 'PRO', None, (116.40700000000004, 104.258, 125.145))]
data['cablam'] = [('A', '220', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (120.0, 109.3, 60.2)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (95.0, 115.6, 117.8)), ('A', '665', 'GLU', 'check CA trace,carbonyls, peptide', ' \nIS-EE', (101.0, 116.0, 106.7)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (108.1, 111.9, 103.7)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (129.4, 101.7, 90.6)), ('A', '326', 'PHE', 'check CA trace', 'bend\nGGSEE', (108.9, 122.6, 102.4)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (105.1, 110.5, 101.7)), ('A', '851', 'ASP', 'check CA trace', 'bend\nGSSST', (83.4, 84.6, 129.4)), ('B', '172', 'ILE', 'check CA trace,carbonyls, peptide', ' \nTT-ST', (127.3, 107.5, 130.7)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (118.2, 103.3, 126.5))]
data['smoc'] = [('A', 32, u'TYR', 0.5722945008048057, (120.21000000000001, 91.306, 71.598)), ('A', 118, u'ARG', 0.5568994485204682, (134.99800000000002, 105.52799999999999, 69.639)), ('A', 144, u'GLU', 0.6129631789247273, (128.22, 94.62499999999999, 83.548)), ('A', 161, u'ASP', 0.6301222589116046, (118.95700000000001, 90.12899999999999, 97.796)), ('A', 171, u'ILE', 0.6048367764294847, (121.765, 99.354, 96.559)), ('A', 178, u'LEU', 0.6124884512185621, (125.811, 106.301, 88.17999999999999)), ('A', 185, u'ALA', 0.5618684997897682, (124.293, 112.818, 79.37199999999999)), ('A', 188, u'LYS', 0.5468241076499766, (125.089, 116.766, 76.37499999999999)), ('A', 193, u'CYS', 0.6287854258980923, (119.568, 119.67699999999999, 70.389)), ('A', 211, u'ASP', 0.4847334600119217, (126.17799999999998, 106.003, 74.51)), ('A', 239, u'SER', 0.5648337865326335, (109.84, 110.17999999999999, 78.905)), ('A', 254, u'GLU', 0.6538764079784228, (122.617, 120.67199999999998, 92.065)), ('A', 308, u'LEU', 0.555921532414849, (100.253, 115.697, 86.827)), ('A', 312, u'ASN', 0.5357629503971201, (106.104, 115.086, 88.013)), ('A', 329, u'LEU', 0.6265285728586291, (103.81, 128.60299999999998, 105.63)), ('A', 331, u'ARG', 0.5753994753153694, (102.57499999999999, 134.335, 109.589)), ('A', 336, u'ASP', 0.6228625602917416, (91.428, 140.671, 118.971)), ('A', 340, u'PHE', 0.6483008662069933, (98.733, 134.63, 116.94300000000001)), ('A', 346, u'TYR', 0.6013751409904141, (101.899, 125.666, 102.1)), ('A', 358, u'ASP', 0.6407597475281004, (91.018, 134.313, 102.55799999999999)), ('A', 369, u'LYS', 0.6200687060002558, (84.93400000000001, 127.26400000000001, 112.546)), ('A', 377, u'ASP', 0.6181661814293322, (96.726, 123.992, 112.4)), ('A', 381, u'HIS', 0.5730000024835376, (101.71000000000001, 123.57199999999999, 118.4)), ('A', 385, u'GLY', 0.45760832676166435, (106.955, 123.17299999999999, 121.13199999999999)), ('A', 388, u'LEU', 0.5821207936629388, (113.647, 117.95400000000001, 119.037)), ('A', 390, u'ASP', 0.6426305525345712, (115.51100000000001, 112.137, 117.31400000000001)), ('A', 402, u'THR', 0.611805371915503, (105.98100000000001, 117.209, 125.959)), ('A', 418, u'ASP', 0.6693533686015278, (87.851, 77.104, 128.756)), ('A', 436, u'GLU', 0.682776452368648, (98.032, 74.252, 114.66)), ('A', 445, u'ASP', 0.6453856182492509, (108.398, 97.16199999999999, 123.59400000000001)), ('A', 451, u'SER', 0.6406497543596591, (110.22, 101.889, 114.853)), ('A', 459, u'ASN', 0.6850124632217767, (109.16999999999999, 106.088, 100.595)), ('A', 465, u'ASP', 0.5848745893140996, (107.086, 108.338, 82.886)), ('A', 468, u'GLN', 0.5658070551383312, (102.85499999999999, 106.55499999999999, 80.346)), ('A', 472, u'VAL', 0.6019632934949961, (97.41700000000002, 104.955, 82.184)), ('A', 506, u'PHE', 0.5506503879484589, (90.708, 117.304, 119.29)), ('A', 507, u'ASN', 0.591660070924124, (91.04400000000001, 113.977, 121.131)), ('A', 534, u'ASN', 0.5229238378399632, (92.326, 127.654, 101.46300000000001)), ('A', 548, u'ILE', 0.6255925847624169, (95.649, 89.08, 115.721)), ('A', 557, u'VAL', 0.681094173961478, (97.143, 103.29, 112.077)), ('A', 575, u'LEU', 0.6309358292586857, (81.327, 108.55799999999999, 94.821)), ('A', 576, u'LEU', 0.5854868100067269, (82.46000000000001, 106.23, 97.607)), ('A', 595, u'TYR', 0.6275959424171845, (74.67899999999999, 84.235, 99.988)), ('A', 602, u'LEU', 0.6226699673956474, (84.339, 84.45100000000001, 90.609)), ('A', 613, u'HIS', 0.6138275665058279, (94.66199999999999, 81.181, 83.955)), ('A', 622, u'CYS', 0.6716576537516865, (102.26700000000001, 99.189, 99.884)), ('A', 634, u'ALA', 0.5679031227487988, (94.405, 108.45, 92.39)), ('A', 635, u'SER', 0.6195845521913234, (93.134, 111.613, 94.082)), ('A', 646, u'CYS', 0.6247304124408602, (83.426, 122.32799999999999, 91.311)), ('A', 658, u'GLU', 0.5215127714120624, (94.286, 116.386, 100.68199999999999)), ('A', 666, u'MET', 0.5813269472541451, (102.408, 116.485, 110.22)), ('A', 682, u'SER', 0.6429558267984972, (95.35799999999999, 104.339, 106.61999999999999)), ('A', 683, u'GLY', 0.5416881319163159, (92.79, 106.584, 108.339)), ('A', 692, u'SER', 0.5372657643431812, (92.106, 100.255, 94.41700000000002)), ('A', 699, u'ALA', 0.5307347265654075, (97.985, 96.60499999999999, 86.363)), ('A', 703, u'ASN', 0.5534994859348797, (100.018, 95.533, 80.54)), ('A', 706, u'ALA', 0.5168192001521644, (104.32, 94.008, 78.35199999999999)), ('A', 711, u'ASP', 0.6182471026429126, (109.21300000000001, 92.44900000000001, 69.396)), ('A', 726, u'ARG', 0.5786654687055119, (98.699, 102.77799999999999, 67.96600000000001)), ('A', 731, u'LEU', 0.6384828649335768, (102.012, 107.233, 74.109)), ('A', 749, u'LEU', 0.6250521428037301, (92.144, 94.553, 78.59100000000001)), ('A', 753, u'PHE', 0.6271729458740417, (92.646, 90.782, 81.37899999999999)), ('A', 756, u'MET', 0.6129362032950108, (88.93, 91.724, 90.667)), ('A', 759, u'SER', 0.5088361279355963, (92.0, 97.826, 97.831)), ('A', 761, u'ASP', 0.591709686448588, (94.21600000000001, 92.35199999999999, 96.65299999999999)), ('A', 785, u'VAL', 0.6100853526884134, (106.71100000000001, 97.779, 87.235)), ('A', 789, u'GLN', 0.594730105439345, (107.79, 102.649, 89.795)), ('A', 802, u'GLU', 0.6155489233471877, (96.548, 78.895, 89.252)), ('A', 815, u'GLN', 0.5823106172856464, (90.139, 83.223, 102.07499999999999)), ('A', 818, u'MET', 0.5804816438193018, (86.619, 75.296, 97.101)), ('A', 829, u'LEU', 0.6268753802308331, (82.742, 78.657, 98.459)), ('A', 841, u'GLY', 0.6237408270645443, (88.55199999999999, 81.64, 119.535)), ('A', 863, u'ALA', 0.5731101391118874, (81.259, 79.432, 113.271)), ('A', 865, u'ASP', 0.5678089258357608, (83.121, 82.136, 109.073)), ('A', 877, u'TYR', 0.642019839527166, (89.21400000000001, 71.283, 108.94100000000002)), ('A', 878, u'ALA', 0.5338228298093627, (85.621, 70.042, 109.065)), ('A', 896, u'THR', 0.6663469887697199, (71.456, 78.15899999999999, 131.64399999999998)), ('A', 914, u'ARG', 0.6493494057663018, (69.551, 77.505, 115.732)), ('B', 77, u'GLU', 0.4286692313399415, (75.16199999999999, 123.927, 122.85199999999999)), ('B', 80, u'ARG', 0.5416740204222953, (79.877, 123.5, 122.16)), ('B', 90, u'MET', 0.5271494532042732, (94.756, 126.133, 124.962)), ('B', 97, u'LYS', 0.4411659050664601, (104.46600000000001, 129.67, 126.233)), ('B', 112, u'ASP', 0.5098981341089076, (107.32, 138.73399999999998, 102.473)), ('B', 118, u'ASN', 0.6217302292235601, (109.718, 123.86, 110.616)), ('B', 119, u'ILE', 0.628459722174563, (112.384, 126.545, 111.057)), ('B', 125, u'ALA', 0.5799136030446006, (113.284, 127.09700000000001, 120.85)), ('B', 129, u'MET', 0.6670381346578634, (115.52799999999999, 117.57199999999999, 123.667)), ('B', 134, u'ASP', 0.6938791082462012, (122.789, 104.018, 121.67199999999998)), ('B', 141, u'THR', 0.7130552629722963, (126.266, 114.003, 118.706)), ('B', 154, u'TRP', 0.6739017913496167, (123.56, 123.94000000000001, 123.648)), ('B', 157, u'GLN', 0.6536819648447423, (120.84400000000001, 120.49700000000001, 131.836)), ('B', 167, u'VAL', 0.692118593350913, (121.039, 109.542, 134.76399999999998)), ('B', 175, u'ASP', 0.739482379896571, (131.689, 100.31700000000001, 130.48000000000002)), ('C', 1, u'SER', 0.5927692772685191, (100.584, 68.87299999999999, 122.753)), ('C', 5, u'ASP', 0.6727214031171546, (100.40700000000001, 74.403, 126.006)), ('C', 15, u'SER', 0.6524372609004893, (100.032, 88.63199999999999, 131.054)), ('C', 22, u'VAL', 0.6712044270257689, (106.96000000000001, 94.891, 135.045)), ('C', 33, u'VAL', 0.6650405549849424, (108.515, 90.63799999999999, 125.307)), ('C', 44, u'ASP', 0.6723513031165942, (111.554, 73.81400000000001, 118.21100000000001)), ('C', 52, u'MET', 0.6335391346889576, (109.617, 79.55799999999999, 129.1))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11995/7b3d/Model_validation_1/validation_cootdata/molprobity_probe7b3d_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

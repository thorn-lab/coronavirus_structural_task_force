
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
data['smoc'] = []
data['jpred'] = []
data['clusters'] = [('A', '323', 1, 'side-chain clash', (144.311, 95.156, 149.743)), ('A', '324', 1, 'side-chain clash', (144.311, 95.156, 149.743)), ('A', '325', 1, 'side-chain clash', (145.373, 100.321, 152.631)), ('A', '537', 1, 'side-chain clash', (145.595, 94.215, 145.912)), ('A', '540', 1, 'side-chain clash', (145.373, 100.321, 152.631)), ('A', '533', 2, 'side-chain clash', (156.899, 99.211, 149.365)), ('A', '535', 2, 'side-chain clash', (159.076, 95.017, 144.434)), ('A', '554', 2, 'side-chain clash', (159.076, 95.017, 144.434)), ('A', '578', 2, 'side-chain clash', (160.598, 102.54, 152.105)), ('A', '585', 2, 'side-chain clash', (156.899, 99.211, 149.365)), ('A', '565', 3, 'Dihedral angle:CA:C', (160.416, 110.693, 147.048)), ('A', '566', 3, 'Dihedral angle:N:CA', (159.996, 111.389, 143.42000000000002)), ('A', '575', 3, 'side-chain clash', (160.718, 105.7, 144.303)), ('A', '584', 3, 'side-chain clash', (160.718, 105.7, 144.303)), ('A', '586', 3, 'side-chain clash', (157.006, 105.441, 143.353)), ('A', '854', 4, 'side-chain clash', (108.461, 131.25, 136.311)), ('A', '855', 4, 'side-chain clash', (108.461, 131.25, 136.311)), ('A', '856', 4, 'cablam CA Geom Outlier', (110.8, 134.4, 138.4)), ('A', '880', 4, 'side-chain clash', (105.222, 126.385, 137.593)), ('A', '884', 4, 'side-chain clash', (105.222, 126.385, 137.593)), ('A', '767', 5, 'side-chain clash', (117.792, 131.84, 146.78)), ('A', '770', 5, 'side-chain clash', (117.792, 131.84, 146.78)), ('A', '932', 5, 'side-chain clash', (119.806, 132.985, 140.233)), ('A', '935', 5, 'side-chain clash', (119.806, 132.985, 140.233)), ('A', '720', 6, 'side-chain clash', (115.616, 119.071, 84.353)), ('A', '923', 6, 'side-chain clash', (115.616, 119.071, 84.353)), ('A', '980', 6, 'side-chain clash', (119.351, 122.922, 84.218)), ('A', '984', 6, 'side-chain clash', (119.351, 122.922, 84.218)), ('A', '191', 7, 'side-chain clash', (101.326, 93.766, 143.669)), ('A', '33', 7, 'cablam Outlier', (107.5, 94.9, 140.1)), ('A', '34', 7, 'cablam CA Geom Outlier\nside-chain clash', (105.1, 95.1, 143.0)), ('A', '557', 8, 'side-chain clash', (106.349, 144.541, 101.851)), ('A', '785', 8, 'cablam Outlier', (113.9, 142.9, 98.1)), ('A', '786', 8, 'cablam Outlier', (112.2, 146.2, 99.3)), ('A', '560', 9, 'backbone clash\nDihedral angle:CA:C', (170.471, 109.533, 146.485)), ('A', '561', 9, 'cablam Outlier\nDihedral angle:N:CA', (171.5, 108.5, 150.0)), ('A', '562', 9, 'backbone clash', (169.59, 109.979, 149.509)), ('A', '215', 10, 'cablam Outlier\nside-chain clash', (101.8, 82.8, 143.1)), ('A', '29', 10, 'side-chain clash', (106.659, 83.097, 142.573)), ('A', '186', 11, 'backbone clash', (93.596, 82.085, 143.711)), ('A', '212', 11, 'backbone clash', (93.596, 82.085, 143.711)), ('A', '661', 12, 'side-chain clash', (128.325, 99.875, 109.472)), ('A', '695', 12, 'side-chain clash', (128.325, 99.875, 109.472)), ('A', '189', 13, 'side-chain clash', (98.092, 88.108, 146.615)), ('A', '95', 13, 'side-chain clash', (98.092, 88.108, 146.615)), ('A', '930', 14, 'side-chain clash', (111.382, 116.903, 95.773)), ('A', '934', 14, 'side-chain clash', (111.382, 116.903, 95.773)), ('A', '37', 15, 'side-chain clash', (106.624, 102.564, 146.233)), ('A', '55', 15, 'side-chain clash', (106.624, 102.564, 146.233)), ('A', '327', 16, 'backbone clash', (152.29, 98.438, 158.564)), ('A', '531', 16, 'backbone clash', (152.29, 98.438, 158.564)), ('A', '295', 17, 'side-chain clash', (123.009, 97.407, 128.979)), ('A', '608', 17, 'side-chain clash', (123.009, 97.407, 128.979)), ('A', '708', 18, 'backbone clash', (145.171, 105.956, 77.244)), ('A', '709', 18, 'backbone clash', (145.171, 105.956, 77.244)), ('A', '193', 19, 'side-chain clash', (134.355, 112.888, 73.593)), ('A', '195', 19, 'side-chain clash', (134.355, 112.888, 73.593)), ('A', '309', 20, 'Dihedral angle:CB:CG:CD:OE1', (116.899, 106.248, 120.362)), ('A', '310', 20, 'cablam CA Geom Outlier', (119.8, 104.5, 118.6)), ('A', '276', 21, 'side-chain clash', (114.392, 109.224, 132.981)), ('A', '304', 21, 'side-chain clash', (114.392, 109.224, 132.981)), ('A', '239', 22, 'side-chain clash', (106.182, 82.544, 163.783)), ('A', '81', 22, 'side-chain clash', (106.182, 82.544, 163.783)), ('A', '204', 23, 'side-chain clash', (115.213, 123.441, 105.526)), ('A', '223', 23, 'side-chain clash', (115.213, 123.441, 105.526)), ('A', '577', 24, 'side-chain clash', (118.751, 140.502, 93.507)), ('A', '582', 24, 'side-chain clash', (118.751, 140.502, 93.507)), ('A', '106', 25, 'side-chain clash\nbackbone clash', (121.391, 114.17, 85.267)), ('A', '235', 25, 'side-chain clash\nbackbone clash', (121.391, 114.17, 85.267)), ('A', '170', 26, 'side-chain clash', (103.024, 136.574, 84.957)), ('A', '172', 26, 'side-chain clash', (103.024, 136.574, 84.957)), ('A', '976', 27, 'side-chain clash', (137.036, 104.627, 102.243)), ('A', '979', 27, 'side-chain clash', (137.036, 104.627, 102.243)), ('A', '733', 28, 'side-chain clash', (113.014, 141.989, 118.65)), ('A', '775', 28, 'side-chain clash', (113.014, 141.989, 118.65)), ('A', '960', 29, 'side-chain clash', (115.79, 123.834, 135.209)), ('A', '964', 29, 'side-chain clash', (115.79, 123.834, 135.209)), ('A', '1109', 30, 'cablam Outlier', (126.8, 116.4, 77.0)), ('A', '1111', 30, 'Dihedral angle:CB:CG:CD:OE1', (126.456, 115.721, 70.68299999999999)), ('A', '605', 31, 'backbone clash', (116.544, 94.817, 122.201)), ('A', '606', 31, 'backbone clash', (116.544, 94.817, 122.201)), ('A', '231', 32, 'side-chain clash', (107.257, 130.431, 105.613)), ('A', '233', 32, 'side-chain clash', (107.257, 130.431, 105.613)), ('A', '1042', 33, 'cablam Outlier', (128.0, 125.8, 97.7)), ('A', '1043', 33, 'cablam Outlier', (124.5, 125.8, 96.2)), ('A', '802', 34, 'side-chain clash', (108.136, 126.36, 92.082)), ('A', '805', 34, 'side-chain clash', (108.136, 126.36, 92.082)), ('B', '189', 1, 'side-chain clash', (189.311, 125.181, 146.467)), ('B', '191', 1, 'side-chain clash', (183.97, 124.962, 143.679)), ('B', '215', 1, 'cablam Outlier\nBond angle:C', (192.4, 131.0, 143.1)), ('B', '216', 1, 'Bond angle:N:CA', (188.984, 129.185, 142.904)), ('B', '33', 1, 'cablam Outlier', (179.1, 129.9, 140.1)), ('B', '34', 1, 'cablam CA Geom Outlier\nside-chain clash', (180.0, 127.9, 143.2)), ('B', '95', 1, 'side-chain clash', (189.311, 125.181, 146.467)), ('B', '661', 2, 'side-chain clash', (145.819, 131.998, 86.78)), ('B', '695', 2, 'side-chain clash', (145.819, 131.998, 86.78)), ('B', '906', 2, 'side-chain clash', (144.185, 129.289, 81.307)), ('B', '909', 2, 'side-chain clash', (144.185, 129.289, 81.307)), ('B', '922', 2, 'side-chain clash', (148.864, 126.329, 84.133)), ('B', '926', 2, 'side-chain clash', (148.864, 126.329, 84.133)), ('B', '645', 3, 'side-chain clash', (160.699, 153.434, 119.785)), ('B', '647', 3, 'side-chain clash', (158.134, 154.791, 121.143)), ('B', '666', 3, 'cablam Outlier', (159.3, 147.5, 118.9)), ('B', '670', 3, 'side-chain clash', (160.699, 153.434, 119.785)), ('B', '930', 4, 'side-chain clash', (158.045, 122.337, 95.764)), ('B', '931', 4, 'side-chain clash', (159.783, 118.237, 97.144)), ('B', '934', 4, 'side-chain clash', (158.045, 122.337, 95.764)), ('B', '935', 4, 'side-chain clash', (159.783, 118.237, 97.144)), ('B', '959', 5, 'side-chain clash', (146.714, 120.253, 133.513)), ('B', '960', 5, 'side-chain clash', (149.988, 122.683, 135.164)), ('B', '963', 5, 'side-chain clash', (146.714, 120.253, 133.513)), ('B', '964', 5, 'side-chain clash', (149.988, 122.683, 135.164)), ('B', '327', 6, 'backbone clash', (153.503, 167.984, 158.553)), ('B', '328', 6, 'backbone clash', (153.594, 171.158, 157.072)), ('B', '531', 6, 'backbone clash', (153.594, 171.158, 157.072)), ('B', '296', 7, 'side-chain clash', (167.52, 137.495, 128.139)), ('B', '308', 7, 'side-chain clash', (168.54, 133.008, 123.851)), ('B', '602', 7, 'side-chain clash', (168.54, 133.008, 123.851)), ('B', '776', 8, 'side-chain clash', (132.273, 117.391, 109.586)), ('B', '780', 8, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (133.21599999999998, 117.46400000000001, 106.88499999999999)), ('B', '784', 8, 'side-chain clash', (133.618, 117.868, 103.657)), ('B', '976', 9, 'side-chain clash', (144.491, 115.23, 151.338)), ('B', '978', 9, 'side-chain clash', (144.491, 115.23, 151.338)), ('B', '979', 9, 'Dihedral angle:CA:CB:CG:OD1', (145.686, 116.166, 155.448)), ('B', '186', 10, 'backbone clash', (196.717, 124.515, 143.377)), ('B', '212', 10, 'backbone clash', (196.717, 124.515, 143.377)), ('B', '767', 11, 'side-chain clash', (133.779, 120.599, 125.592)), ('B', '770', 11, 'side-chain clash', (133.779, 120.599, 125.592)), ('B', '229', 12, 'side-chain clash', (148.507, 112.219, 105.611)), ('B', '819', 12, 'Dihedral angle:CB:CG:CD:OE1', (153.24599999999998, 113.252, 104.819)), ('B', '708', 13, 'backbone clash', (150.902, 157.106, 77.356)), ('B', '709', 13, 'backbone clash', (150.902, 157.106, 77.356)), ('B', '239', 14, 'side-chain clash', (190.758, 135.478, 163.159)), ('B', '81', 14, 'side-chain clash', (190.758, 135.478, 163.159)), ('B', '204', 15, 'side-chain clash', (175.931, 121.027, 149.9)), ('B', '223', 15, 'side-chain clash', (175.931, 121.027, 149.9)), ('B', '903', 16, 'side-chain clash', (144.78, 123.009, 76.507)), ('B', '913', 16, 'side-chain clash', (144.78, 123.009, 76.507)), ('B', '554', 17, 'side-chain clash', (148.976, 171.355, 143.538)), ('B', '585', 17, 'side-chain clash', (148.976, 171.355, 143.538)), ('B', '620', 18, 'side-chain clash', (147.781, 157.67, 137.923)), ('B', '651', 18, 'side-chain clash', (147.781, 157.67, 137.923)), ('B', '170', 19, 'side-chain clash', (180.721, 110.837, 161.089)), ('B', '172', 19, 'side-chain clash', (180.721, 110.837, 161.089)), ('B', '744', 20, 'side-chain clash', (152.502, 116.563, 113.519)), ('B', '977', 20, 'side-chain clash', (152.502, 116.563, 113.519)), ('B', '880', 21, 'side-chain clash', (139.278, 112.008, 89.115)), ('B', '884', 21, 'side-chain clash', (139.278, 112.008, 89.115)), ('B', '733', 22, 'side-chain clash', (150.401, 122.827, 105.915)), ('B', '775', 22, 'side-chain clash', (150.401, 122.827, 105.915)), ('B', '90', 23, 'Dihedral angle:CA:C', (178.539, 131.161, 154.712)), ('B', '91', 23, 'Dihedral angle:N:CA', (179.863, 129.73399999999998, 151.5)), ('B', '1109', 24, 'cablam Outlier', (150.9, 135.9, 76.9)), ('B', '1111', 24, 'Dihedral angle:CB:CG:CD:OE1', (151.39800000000002, 136.047, 70.67299999999999)), ('B', '740', 25, 'side-chain clash', (138.307, 109.267, 143.552)), ('B', '745', 25, 'side-chain clash', (138.307, 109.267, 143.552)), ('B', '231', 26, 'side-chain clash', (174.13, 125.481, 168.117)), ('B', '233', 26, 'side-chain clash', (174.13, 125.481, 168.117)), ('B', '1042', 27, 'cablam Outlier', (142.0, 132.4, 97.8)), ('B', '1043', 27, 'cablam Outlier', (143.8, 129.4, 96.4)), ('B', '802', 28, 'side-chain clash', (151.645, 114.684, 92.512)), ('B', '805', 28, 'side-chain clash', (151.645, 114.684, 92.512)), ('C', '815', 1, 'side-chain clash', (146.61, 158.289, 109.969)), ('C', '819', 1, 'Dihedral angle:CB:CG:CD:OE1', (140.197, 160.48600000000002, 104.71300000000001)), ('C', '867', 1, 'side-chain clash', (146.61, 158.289, 109.969)), ('C', '868', 1, 'Dihedral angle:CB:CG:CD:OE1', (151.059, 157.71399999999997, 107.789)), ('C', '880', 1, 'side-chain clash', (143.376, 156.995, 105.344)), ('C', '744', 2, 'side-chain clash', (145.785, 147.663, 146.936)), ('C', '776', 2, 'side-chain clash', (139.565, 146.748, 147.271)), ('C', '901', 2, 'side-chain clash', (141.547, 144.87, 142.753)), ('C', '905', 2, 'side-chain clash', (141.547, 144.87, 142.753)), ('C', '977', 2, 'side-chain clash', (145.785, 147.663, 146.936)), ('C', '738', 3, 'backbone clash', (148.354, 141.119, 139.015)), ('C', '739', 3, 'backbone clash', (148.354, 141.119, 139.015)), ('C', '760', 3, 'side-chain clash', (148.659, 138.213, 134.188)), ('C', '764', 3, 'side-chain clash', (148.659, 138.213, 134.188)), ('C', '1042', 4, 'cablam Outlier', (129.2, 141.2, 97.8)), ('C', '1043', 4, 'cablam Outlier', (131.0, 144.3, 96.4)), ('C', '318', 4, 'backbone clash\nside-chain clash', (131.619, 147.148, 100.093)), ('C', '593', 4, 'backbone clash\nside-chain clash', (131.619, 147.148, 100.093)), ('C', '661', 5, 'side-chain clash', (106.761, 154.002, 108.789)), ('C', '663', 5, 'Dihedral angle:CA:CB:CG:OD1', (110.596, 154.314, 112.018)), ('C', '695', 5, 'side-chain clash', (106.761, 154.002, 108.789)), ('C', '659', 6, 'side-chain clash', (102.45, 149.721, 104.64)), ('C', '698', 6, 'side-chain clash', (102.45, 149.721, 104.64)), ('C', '699', 6, 'cablam Outlier\nside-chain clash', (107.0, 146.0, 104.2)), ('C', '549', 7, 'cablam CA Geom Outlier', (102.4, 136.3, 146.3)), ('C', '550', 7, 'side-chain clash', (100.778, 135.726, 141.902)), ('C', '589', 7, 'side-chain clash', (100.778, 135.726, 141.902)), ('C', '327', 8, 'backbone clash', (93.015, 133.783, 158.612)), ('C', '328', 8, 'backbone clash', (89.263, 132.966, 157.147)), ('C', '531', 8, 'backbone clash', (93.015, 133.783, 158.612)), ('C', '903', 9, 'side-chain clash', (136.171, 147.733, 75.914)), ('C', '912', 9, 'cablam Outlier', (130.3, 145.2, 75.5)), ('C', '913', 9, 'side-chain clash', (136.171, 147.733, 75.914)), ('C', '229', 10, 'side-chain clash', (124.158, 172.778, 165.627)), ('C', '231', 10, 'side-chain clash', (119.338, 172.444, 167.643)), ('C', '233', 10, 'side-chain clash', (119.338, 172.444, 167.643)), ('C', '882', 11, 'side-chain clash', (143.16, 153.366, 87.996)), ('C', '884', 11, 'cablam Outlier\nside-chain clash', (147.9, 148.8, 86.4)), ('C', '898', 11, 'side-chain clash', (143.16, 153.366, 87.996)), ('C', '186', 12, 'backbone clash', (108.692, 192.851, 143.614)), ('C', '212', 12, 'backbone clash', (108.692, 192.851, 143.614)), ('C', '666', 13, 'cablam Outlier\nside-chain clash', (107.6, 148.6, 118.9)), ('C', '672', 13, 'side-chain clash', (105.182, 152.698, 118.098)), ('C', '767', 14, 'side-chain clash', (143.987, 140.426, 125.887)), ('C', '770', 14, 'side-chain clash', (143.987, 140.426, 125.887)), ('C', '189', 15, 'side-chain clash', (111.875, 185.696, 146.354)), ('C', '95', 15, 'side-chain clash', (111.875, 185.696, 146.354)), ('C', '931', 16, 'side-chain clash\nbackbone clash', (136.812, 144.046, 133.129)), ('C', '935', 16, 'side-chain clash\nbackbone clash', (136.812, 144.046, 133.129)), ('C', '930', 17, 'side-chain clash', (129.616, 160.004, 95.646)), ('C', '934', 17, 'side-chain clash', (129.616, 160.004, 95.646)), ('C', '265', 18, 'side-chain clash', (146.558, 141.585, 93.489)), ('C', '80', 18, 'side-chain clash', (146.558, 141.585, 93.489)), ('C', '293', 19, 'cablam Outlier', (108.9, 163.4, 137.5)), ('C', '294', 19, 'side-chain clash', (109.337, 163.557, 134.21)), ('C', '720', 20, 'side-chain clash', (129.724, 155.257, 84.343)), ('C', '923', 20, 'side-chain clash', (129.724, 155.257, 84.343)), ('C', '708', 21, 'backbone clash', (103.571, 136.091, 77.36)), ('C', '709', 21, 'backbone clash', (103.571, 136.091, 77.36)), ('C', '239', 22, 'side-chain clash', (102.72, 181.813, 163.445)), ('C', '81', 22, 'side-chain clash', (102.72, 181.813, 163.445)), ('C', '204', 23, 'side-chain clash', (133.861, 153.552, 105.846)), ('C', '223', 23, 'side-chain clash', (133.861, 153.552, 105.846)), ('C', '554', 24, 'side-chain clash', (91.969, 127.417, 143.541)), ('C', '585', 24, 'side-chain clash', (91.969, 127.417, 143.541)), ('C', '976', 25, 'side-chain clash', (140.104, 153.111, 152.66)), ('C', '979', 25, 'side-chain clash', (140.104, 153.111, 152.66)), ('C', '780', 26, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (146.532, 140.98800000000003, 106.91000000000001)), ('C', '784', 26, 'side-chain clash', (145.217, 141.712, 103.497)), ('C', '33', 27, 'cablam Outlier', (113.0, 174.6, 140.1)), ('C', '34', 27, 'cablam CA Geom Outlier\nside-chain clash\nbackbone clash', (114.2, 176.3, 143.2)), ('C', '645', 28, 'side-chain clash', (136.366, 146.857, 87.466)), ('C', '647', 28, 'side-chain clash', (136.366, 146.857, 87.466)), ('C', '656', 29, 'side-chain clash', (97.284, 155.008, 109.183)), ('C', '658', 29, 'side-chain clash', (97.284, 155.008, 109.183)), ('C', '90', 30, 'Dihedral angle:CA:C', (112.07799999999999, 173.39100000000002, 154.73999999999998)), ('C', '91', 30, 'Dihedral angle:N:CA', (112.67999999999999, 175.26, 151.539)), ('C', '950', 31, 'side-chain clash', (130.683, 150.129, 120.919)), ('C', '954', 31, 'side-chain clash', (130.683, 150.129, 120.919)), ('C', '323', 32, 'side-chain clash', (94.378, 142.107, 149.609)), ('C', '324', 32, 'side-chain clash', (94.378, 142.107, 149.609)), ('C', '802', 33, 'side-chain clash', (139.551, 158.216, 92.571)), ('C', '805', 33, 'side-chain clash', (139.551, 158.216, 92.571))]
data['probe'] = [(' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.658, (125.921, 126.579, 99.889)), (' A 276  LEU HD11', ' A 304  LYS  HA ', -0.652, (114.392, 109.224, 132.981)), (' C 903  ALA  HB1', ' C 913  GLN  HG2', -0.646, (136.171, 147.733, 75.914)), (' C 659  SER  HB2', ' C 698  SER  HB2', -0.643, (102.45, 149.721, 104.64)), (' B1123  SER  OG ', ' C 914  ASN  ND2', -0.641, (129.836, 148.327, 68.899)), (' C1102  TRP  HB2', ' C1135  ASN HD22', -0.639, (112.572, 138.561, 62.03)), (' A1123  SER  OG ', ' B 914  ASN  ND2', -0.628, (148.197, 128.424, 68.993)), (' B1028  LYS  NZ ', ' B1042  PHE  O  ', -0.628, (142.264, 130.107, 99.363)), (' C 738  CYS  SG ', ' C 739  THR  N  ', -0.614, (148.354, 141.119, 139.015)), (' A 204  TYR  HB3', ' A 223  LEU  HB3', -0.609, (101.458, 102.036, 149.422)), (' B 308  VAL HG12', ' B 602  THR HG23', -0.608, (168.54, 133.008, 123.851)), (' B 554  GLU  HA ', ' B 585  LEU  HA ', -0.6, (148.976, 171.355, 143.538)), (' B1091  ARG  NH1', ' B1118  ASP  O  ', -0.597, (136.73, 136.81, 64.467)), (' B 170  TYR  HH ', ' B 172  SER  HG ', -0.595, (180.721, 110.837, 161.089)), (' A 726  ILE HG12', ' A1061  VAL HG22', -0.595, (115.213, 123.441, 105.526)), (' B 204  TYR  HB3', ' B 223  LEU  HB3', -0.592, (175.931, 121.027, 149.9)), (' A1091  ARG  NH1', ' A1118  ASP  O  ', -0.589, (134.339, 128.391, 64.262)), (' B 767  LEU  HA ', ' B 770  ILE HD12', -0.588, (133.779, 120.599, 125.592)), (' C 554  GLU  HA ', ' C 585  LEU  HA ', -0.588, (91.969, 127.417, 143.541)), (' C 328  ARG  NH2', ' C 531  THR  O  ', -0.583, (89.263, 132.966, 157.147)), (' C 767  LEU  HA ', ' C 770  ILE HD12', -0.582, (143.987, 140.426, 125.887)), (' A  81  ASN  O  ', ' A 239  GLN  NE2', -0.58, (106.182, 82.544, 163.783)), (' C 204  TYR  HB3', ' C 223  LEU  HB3', -0.576, (121.853, 176.171, 149.347)), (' B 733  LYS  NZ ', ' B 775  ASP  OD2', -0.573, (136.069, 112.369, 118.107)), (' B 726  ILE HG12', ' B1061  VAL HG22', -0.569, (150.401, 122.827, 105.915)), (' C 726  ILE HG12', ' C1061  VAL HG22', -0.565, (133.861, 153.552, 105.846)), (' C  81  ASN  O  ', ' C 239  GLN  NE2', -0.562, (102.72, 181.813, 163.445)), (' A 767  LEU  HA ', ' A 770  ILE HD12', -0.561, (121.441, 138.919, 125.926)), (' B  81  ASN  O  ', ' B 239  GLN  NE2', -0.561, (190.758, 135.478, 163.159)), (' B 620  VAL HG11', ' B 651  ILE HD11', -0.56, (166.655, 153.047, 131.302)), (' A 996  LEU HD23', ' A1000  ARG HH21', -0.557, (117.792, 131.84, 146.78)), (' C 976  VAL HG23', ' C 979  ASP  HB2', -0.55, (140.104, 153.111, 152.66)), (' A 170  TYR  HH ', ' A 172  SER  HG ', -0.548, (89.876, 103.046, 161.194)), (' B 589  PRO  HG3', ' C 855  PHE  HB3', -0.544, (147.781, 157.67, 137.923)), (' A 792  PRO  HG2', ' C 707  TYR  HB3', -0.544, (103.024, 136.574, 84.957)), (' A 720  ILE HG13', ' A 923  ILE HG23', -0.543, (115.616, 119.071, 84.353)), (' A  34  ARG  NE ', ' A 191  GLU  OE2', -0.537, (101.326, 93.766, 143.669)), (' B 740  MET  HE1', ' B 745  ASP  HB3', -0.536, (138.307, 109.267, 143.552)), (' B 327  VAL  O  ', ' B 531  THR  N  ', -0.529, (153.503, 167.984, 158.553)), (' C 327  VAL  O  ', ' C 531  THR  N  ', -0.527, (93.015, 133.783, 158.612)), (' B 328  ARG  NH1', ' B 531  THR  O  ', -0.516, (153.594, 171.158, 157.072)), (' B 802  PHE  HD2', ' B 805  ILE HD11', -0.515, (151.645, 114.684, 92.512)), (' A 802  PHE  HD2', ' A 805  ILE HD11', -0.512, (108.136, 126.36, 92.082)), (' B 780  GLU  O  ', ' B 784  GLN  NE2', -0.512, (133.618, 117.868, 103.657)), (' C 323  THR HG23', ' C 324  GLU  HG2', -0.511, (94.378, 142.107, 149.609)), (' A 976  VAL HG23', ' A 979  ASP  HB2', -0.508, (112.012, 129.203, 153.227)), (' A 699  LEU  HB2', ' B 788  ILE HD11', -0.508, (137.036, 104.627, 102.243)), (' C 780  GLU  O  ', ' C 784  GLN  NE2', -0.506, (145.217, 141.712, 103.497)), (' A 578  ASP  N  ', ' A 578  ASP  OD1', -0.505, (160.598, 102.54, 152.105)), (' C 720  ILE HG13', ' C 923  ILE HG23', -0.503, (129.724, 155.257, 84.343)), (' A 323  THR HG23', ' A 324  GLU  HG2', -0.5, (144.311, 95.156, 149.743)), (' A 327  VAL  O  ', ' A 531  THR  N  ', -0.5, (152.29, 98.438, 158.564)), (' A 708  SER  OG ', ' A 709  ASN  N  ', -0.495, (145.171, 105.956, 77.244)), (' C 661  GLU  O  ', ' C 695  TYR  OH ', -0.495, (106.761, 154.002, 108.789)), (' B 661  GLU  O  ', ' B 695  TYR  OH ', -0.494, (164.324, 145.806, 109.37)), (' C 666  ILE HD11', ' C 672  ALA  HB2', -0.493, (105.182, 152.698, 118.098)), (' A 535  LYS  HE3', ' A 554  GLU  HG2', -0.493, (159.076, 95.017, 144.434)), (' C 294  ASP  N  ', ' C 294  ASP  OD1', -0.492, (109.337, 163.557, 134.21)), (' A 577  ARG HH12', ' A 582  LEU  HB2', -0.489, (166.669, 102.034, 151.206)), (' A 889  GLY  HA3', ' A1034  LEU HD23', -0.487, (118.751, 140.502, 93.507)), (' C1111  GLU  OE1', ' C1113  GLN  NE2', -0.486, (124.481, 145.76, 68.568)), (' A 325  SER  HA ', ' A 540  ASN  HB3', -0.485, (145.373, 100.321, 152.631)), (' B 889  GLY  HA3', ' B1034  LEU HD23', -0.485, (133.775, 117.213, 93.47)), (' A1102  TRP  HB2', ' A1135  ASN HD22', -0.485, (138.599, 112.285, 62.581)), (' A 557  LYS  HB3', ' A 584  ILE HG12', -0.482, (163.364, 104.853, 142.955)), (' C 815  ARG HH12', ' C 867  ASP  HB3', -0.479, (146.61, 158.289, 109.969)), (' B 909  ILE HD11', ' B1047  TYR  HB3', -0.478, (145.819, 131.998, 86.78)), (' C 776  LYS  O  ', ' C 780  GLU  HG3', -0.478, (146.949, 140.287, 109.604)), (' B 776  LYS  O  ', ' B 780  GLU  HG3', -0.477, (132.273, 117.391, 109.586)), (' C 996  LEU HD23', ' C1000  ARG HH21', -0.475, (139.565, 146.748, 147.271)), (' A 788  ILE HD11', ' C 699  LEU  HB2', -0.475, (106.349, 144.541, 101.851)), (' B 229  LEU  HB3', ' B 231  ILE HG23', -0.473, (172.234, 121.118, 165.215)), (' C 802  PHE  HD2', ' C 805  ILE HD11', -0.472, (139.551, 158.216, 92.571)), (' A 229  LEU  HB3', ' A 231  ILE HG23', -0.472, (103.185, 105.488, 165.685)), (' C 880  GLY  O  ', ' C 884  SER  OG ', -0.472, (148.273, 148.757, 89.348)), (' B 819  GLU  OE2', ' B1055  SER  OG ', -0.472, (148.507, 112.219, 105.611)), (' A 733  LYS  NZ ', ' A 775  ASP  OD2', -0.465, (113.014, 141.989, 118.65)), (' C 819  GLU  OE2', ' C1055  SER  OG ', -0.465, (143.376, 156.995, 105.344)), (' B  34  ARG  NE ', ' B 191  GLU  OE2', -0.464, (183.97, 124.962, 143.679)), (' C 318  PHE  N  ', ' C 593  GLY  O  ', -0.464, (108.02, 146.424, 134.971)), (' A 575  ALA  HA ', ' A 586  ASP  HA ', -0.462, (157.006, 105.441, 143.353)), (' A 980  ILE HG23', ' A 984  LEU HD12', -0.462, (118.042, 132.873, 156.823)), (' C 718  PHE  HA ', ' C1069  PRO  HA ', -0.461, (121.181, 151.82, 83.52)), (' A 911  VAL  HA ', ' A1106  GLN  NE2', -0.459, (126.045, 121.96, 77.386)), (' B 880  GLY  O  ', ' B 884  SER  OG ', -0.458, (139.278, 112.008, 89.115)), (' B 708  SER  OG ', ' B 709  ASN  N  ', -0.457, (150.902, 157.106, 77.356)), (' A 906  PHE  HE1', ' A1049  LEU HD11', -0.455, (119.351, 122.922, 84.218)), (' B1111  GLU  O  ', ' B1113  GLN  NE2', -0.454, (148.584, 136.503, 69.051)), (' B 645  THR HG23', ' B 647  ALA  H  ', -0.453, (158.134, 154.791, 121.143)), (' C 725  GLU  OE1', ' C1064  HIS  NE2', -0.452, (131.619, 147.148, 100.093)), (' C 645  THR HG23', ' C 647  ALA  H  ', -0.452, (101.622, 144.385, 120.994)), (' C 905  ARG  HD3', ' C1049  LEU  O  ', -0.452, (136.366, 146.857, 87.466)), (' B 960  ASN  O  ', ' B 964  LYS  HG3', -0.451, (149.988, 122.683, 135.164)), (' C 950  ASP  O  ', ' C 954  GLN  HG3', -0.45, (130.683, 150.129, 120.919)), (' A 880  GLY  O  ', ' A 884  SER  OG ', -0.45, (112.22, 138.371, 89.443)), (' C 708  SER  OG ', ' C 709  ASN  N  ', -0.448, (103.571, 136.091, 77.36)), (' B1105  THR  OG1', ' B1106  GLN  N  ', -0.447, (147.837, 138.614, 72.669)), (' C 229  LEU  HB3', ' C 231  ILE HG23', -0.447, (124.158, 172.778, 165.627)), (' A 854  LYS  NZ ', ' C 568  ASP  OD2', -0.446, (105.222, 126.385, 137.593)), (' C 760  CYS  O  ', ' C 764  ASN  ND2', -0.446, (148.659, 138.213, 134.188)), (' C  95  THR HG22', ' C 189  LEU HD13', -0.445, (111.875, 185.696, 146.354)), (' C  80  ASP  O  ', ' C 265  TYR  OH ', -0.445, (103.597, 183.78, 158.37)), (' C 889  GLY  HA3', ' C1034  LEU HD23', -0.445, (146.558, 141.585, 93.489)), (' B 186  PHE  N  ', ' B 212  LEU  O  ', -0.444, (196.717, 124.515, 143.377)), (' C1047  TYR  HE2', ' C1108  ASN HD21', -0.444, (123.215, 143.544, 84.108)), (' A1095  PHE  HE1', ' A1115  ILE HD11', -0.442, (137.958, 115.414, 64.908)), (' B 906  PHE  O  ', ' B 909  ILE HG22', -0.441, (144.185, 129.289, 81.307)), (' A 960  ASN  O  ', ' A 964  LYS  HG3', -0.441, (115.79, 123.834, 135.209)), (' B 922  LEU  O  ', ' B 926  GLN  HG3', -0.439, (159.041, 124.219, 83.772)), (' C  34  ARG  NE ', ' C 191  GLU  OE2', -0.439, (114.634, 181.201, 143.829)), (' A 193  VAL HG12', ' A 195  LYS  HB3', -0.439, (107.408, 100.574, 153.709)), (' C 719  THR  N  ', ' C1068  VAL  O  ', -0.436, (122.591, 152.835, 85.371)), (' A 714  ILE HD11', ' A1096  VAL HG11', -0.436, (134.355, 112.888, 73.593)), (' C 231  ILE HD12', ' C 233  ILE HD12', -0.433, (119.338, 172.444, 167.643)), (' B 906  PHE  HE1', ' B1049  LEU HD11', -0.432, (148.864, 126.329, 84.133)), (' A  37  TYR  H  ', ' A  55  PHE  HE1', -0.43, (106.624, 102.564, 146.233)), (' B 931  ILE  O  ', ' B 935  GLN  HG3', -0.429, (159.783, 118.237, 97.144)), (' A 231  ILE HD12', ' A 233  ILE HD12', -0.428, (106.012, 101.587, 167.686)), (' C1111  GLU  O  ', ' C1113  GLN  NE2', -0.426, (122.598, 145.057, 69.005)), (' A1047  TYR  HE2', ' A1108  ASN HD21', -0.426, (128.926, 119.458, 83.571)), (' B 959  LEU  O  ', ' B 963  VAL HG23', -0.426, (146.714, 120.253, 133.513)), (' B 569  ILE  H  ', ' B 569  ILE HD12', -0.425, (136.106, 162.426, 136.124)), (' A 819  GLU  OE2', ' A1055  SER  OG ', -0.424, (107.257, 130.431, 105.613)), (' A  95  THR HG22', ' A 189  LEU HD13', -0.423, (98.092, 88.108, 146.615)), (' A 661  GLU  O  ', ' A 695  TYR  OH ', -0.423, (128.325, 99.875, 109.472)), (' C 931  ILE  O  ', ' C 935  GLN  HG3', -0.423, (132.749, 163.58, 96.958)), (' C 905  ARG  O  ', ' C1036  GLN  NE2', -0.422, (133.891, 144.809, 84.994)), (' B 231  ILE HD12', ' B 233  ILE HD12', -0.422, (174.13, 125.481, 168.117)), (' A1029  MET  O  ', ' A1033  VAL  HB ', -0.421, (119.376, 134.348, 97.131)), (' C 962  LEU HD21', ' C1007  TYR  HB2', -0.421, (136.812, 144.046, 133.129)), (' C 186  PHE  N  ', ' C 212  LEU  O  ', -0.42, (108.692, 192.851, 143.614)), (' A 106  PHE  HD2', ' A 235  ILE HD13', -0.419, (107.528, 97.295, 163.672)), (' B 903  ALA  HB1', ' B 913  GLN  HB2', -0.418, (144.78, 123.009, 76.507)), (' C 550  GLY  HA2', ' C 589  PRO  HA ', -0.417, (100.778, 135.726, 141.902)), (' A 718  PHE  HA ', ' A1069  PRO  HA ', -0.416, (123.364, 113.721, 83.569)), (' A 719  THR  N  ', ' A1068  VAL  O  ', -0.416, (121.391, 114.17, 85.267)), (' A 932  GLY  HA2', ' A 935  GLN  HG3', -0.416, (105.995, 116.108, 96.304)), (' B  95  THR HG22', ' B 189  LEU HD13', -0.416, (189.311, 125.181, 146.467)), (' A 741  TYR  HE1', ' A1000  ARG  HB3', -0.415, (119.806, 132.985, 140.233)), (' B1013  ILE  O  ', ' B1017  GLU  HG3', -0.415, (137.976, 130.186, 119.283)), (' C 882  ILE  HA ', ' C 898  PHE  HE1', -0.414, (143.16, 153.366, 87.996)), (' C 656  VAL HG12', ' C 658  ASN  H  ', -0.413, (97.284, 155.008, 109.183)), (' A 930  ALA  O  ', ' A 934  ILE HG12', -0.412, (111.382, 116.903, 95.773)), (' B 930  ALA  O  ', ' B 934  ILE HG12', -0.412, (158.045, 122.337, 95.764)), (' A 295  PRO  HB2', ' A 608  VAL HG21', -0.41, (123.009, 97.407, 128.979)), (' A 533  LEU HD11', ' A 585  LEU HD21', -0.409, (156.899, 99.211, 149.365)), (' A  29  THR  OG1', ' A 215  ASP  OD2', -0.409, (106.659, 83.097, 142.573)), (' A 186  PHE  N  ', ' A 212  LEU  O  ', -0.407, (93.596, 82.085, 143.711)), (' A 605  SER  OG ', ' A 606  ASN  N  ', -0.407, (116.544, 94.817, 122.201)), (' A 854  LYS  HB3', ' A 855  PHE  H  ', -0.407, (108.461, 131.25, 136.311)), (' A 560  LEU  O  ', ' A 562  PHE  N  ', -0.406, (169.59, 109.979, 149.509)), (' B 976  VAL HG12', ' B 978  ASN  H  ', -0.406, (144.491, 115.23, 151.338)), (' B 296  LEU  HA ', ' B 296  LEU HD12', -0.405, (167.52, 137.495, 128.139)), (' C 930  ALA  O  ', ' C 934  ILE HG12', -0.404, (129.616, 160.004, 95.646)), (' C 901  GLN  O  ', ' C 905  ARG  HG3', -0.404, (138.232, 147.376, 83.627)), (' A1080  ALA  HB3', ' A1132  ILE HG12', -0.404, (147.939, 117.589, 67.222)), (' C 742  ILE  HA ', ' C1000  ARG  HD2', -0.403, (141.547, 144.87, 142.753)), (' A 575  ALA  HB1', ' A 584  ILE HD11', -0.403, (160.718, 105.7, 144.303)), (' B 744  GLY  H  ', ' B 977  LEU HD22', -0.402, (139.445, 115.42, 147.509)), (' B 826  VAL  HB ', ' B1057  PRO  HG2', -0.402, (152.502, 116.563, 113.519)), (' A 537  LYS  HB3', ' A 537  LYS  HE2', -0.402, (145.595, 94.215, 145.912)), (' B 645  THR HG21', ' B 670  ILE HD11', -0.401, (160.699, 153.434, 119.785)), (' C 744  GLY  H  ', ' C 977  LEU HD22', -0.401, (145.785, 147.663, 146.936))]
data['omega'] = [('A', ' 566 ', 'GLY', None, (160.158, 110.664, 144.65800000000004))]
data['cablam'] = [('A', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (107.5, 94.9, 140.1)), ('A', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (102.2, 114.1, 148.9)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (114.6, 98.0, 156.7)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (112.0, 93.6, 169.5)), ('A', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (101.8, 82.8, 143.1)), ('A', '293', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nTTSSH', (119.0, 97.0, 137.5)), ('A', '556', 'ASN', ' beta sheet', ' \nB----', (164.9, 101.3, 140.1)), ('A', '561', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\n--TT-', (171.5, 108.5, 150.0)), ('A', '657', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (135.6, 90.2, 110.3)), ('A', '785', 'VAL', ' alpha helix', ' \n---SE', (113.9, 142.9, 98.1)), ('A', '786', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (112.2, 146.2, 99.3)), ('A', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nGTSS-', (118.2, 147.2, 90.0)), ('A', '1042', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (128.0, 125.8, 97.7)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (124.5, 125.8, 96.2)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (113.6, 130.2, 113.5)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (148.3, 119.9, 55.9)), ('A', '1098', 'ASN', 'check CA trace,carbonyls, peptide', ' \nEE-SS', (133.7, 106.3, 68.0)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (126.8, 116.4, 77.0)), ('A', '34', 'ARG', 'check CA trace', ' \n-S---', (105.1, 95.1, 143.0)), ('A', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (119.8, 104.5, 118.6)), ('A', '549', 'THR', 'check CA trace', ' \n---BB', (145.8, 104.8, 146.4)), ('A', '856', 'ASN', 'check CA trace', 'bend\n--SSE', (110.8, 134.4, 138.4)), ('B', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nE-STT', (179.1, 129.9, 140.1)), ('B', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSEE', (165.0, 115.8, 149.2)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (172.8, 134.6, 156.8)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (177.9, 134.6, 169.5)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nSBSSS', (181.7, 130.7, 177.4)), ('B', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (192.4, 131.0, 143.1)), ('B', '293', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nTTSSH', (171.4, 139.0, 137.4)), ('B', '544', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (145.1, 163.9, 158.8)), ('B', '565', 'PHE', 'check CA trace,carbonyls, peptide', ' \n-S---', (139.6, 167.7, 148.8)), ('B', '657', 'ASN', ' beta sheet', ' \n-----', (169.3, 155.8, 110.9)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (159.3, 147.5, 118.9)), ('B', '856', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (143.3, 113.0, 138.6)), ('B', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nHHSS-', (128.8, 113.1, 89.6)), ('B', '1042', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (142.0, 132.4, 97.8)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (143.8, 129.4, 96.4)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (145.5, 117.7, 113.5)), ('B', '1072', 'GLU', 'check CA trace,carbonyls, peptide', ' \nE----', (157.5, 141.9, 80.6)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (137.1, 152.9, 56.0)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (150.9, 135.9, 76.9)), ('B', '34', 'ARG', 'check CA trace', 'turn\n-STT-', (180.0, 127.9, 143.2)), ('B', '53', 'ASP', 'check CA trace', 'bend\nEES-B', (165.6, 130.3, 149.2)), ('B', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (164.5, 135.6, 118.6)), ('B', '549', 'THR', 'check CA trace', 'strand\n--EEE', (151.2, 158.2, 146.3)), ('C', '33', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nE-STT', (113.0, 174.6, 140.1)), ('C', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SS-E', (111.9, 166.7, 156.8)), ('C', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESSS', (109.5, 171.2, 169.5)), ('C', '215', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (105.2, 185.4, 143.1)), ('C', '293', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nTTS-H', (108.9, 163.4, 137.5)), ('C', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (107.6, 148.6, 118.9)), ('C', '699', 'LEU', 'check CA trace,carbonyls, peptide', ' \n----E', (107.0, 146.0, 104.2)), ('C', '884', 'SER', 'check CA trace,carbonyls, peptide', 'helix\nHHH-S', (147.9, 148.8, 86.4)), ('C', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nHHSS-', (152.7, 139.5, 89.7)), ('C', '912', 'THR', 'check CA trace,carbonyls, peptide', ' \nT--SH', (130.3, 145.2, 75.5)), ('C', '1042', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\nTTTSS', (129.2, 141.2, 97.8)), ('C', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSS', (131.0, 144.3, 96.4)), ('C', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (140.3, 151.5, 113.5)), ('C', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSS-', (114.1, 126.8, 56.1)), ('C', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (121.8, 147.0, 76.9)), ('C', '34', 'ARG', 'check CA trace', 'turn\n-STT-', (114.2, 176.3, 143.2)), ('C', '53', 'ASP', 'check CA trace', 'bend\nEES-B', (119.2, 162.5, 149.3)), ('C', '310', 'LYS', 'check CA trace', 'bend\n--SEE', (115.1, 159.2, 119.1)), ('C', '549', 'THR', 'check CA trace', ' \n---EE', (102.4, 136.3, 146.3))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22301/6xs6/Model_validation_3/validation_cootdata/molprobity_probe6xs6_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

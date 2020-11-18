
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
data['clusters'] = [('A', '476', 1, 'side-chain clash', (90.905, 94.911, 84.507)), ('A', '480', 1, 'side-chain clash', (86.65, 97.561, 89.263)), ('A', '633', 1, 'side-chain clash', (90.056, 103.399, 87.303)), ('A', '634', 1, 'smoc Outlier', (90.7490005493164, 102.32499694824219, 90.5739974975586)), ('A', '637', 1, 'side-chain clash', (90.056, 103.399, 87.303)), ('A', '689', 1, 'side-chain clash', (87.493, 97.362, 92.369)), ('A', '693', 1, 'side-chain clash', (86.65, 97.561, 89.263)), ('A', '696', 1, 'side-chain clash', (92.512, 93.07, 83.779)), ('A', '700', 1, 'side-chain clash', (92.512, 93.07, 83.779)), ('A', '658', 2, 'side-chain clash\nsmoc Outlier', (91.224, 108.057, 99.667)), ('A', '662', 2, 'side-chain clash', (91.224, 108.057, 99.667)), ('A', '665', 2, 'side-chain clash\nsmoc Outlier', (96.663, 108.946, 103.951)), ('A', '677', 2, 'cablam Outlier', (103.3, 106.6, 102.0)), ('A', '678', 2, 'cablam CA Geom Outlier', (100.5, 105.0, 100.1)), ('A', '679', 2, 'smoc Outlier', (98.59500122070312, 101.71900177001953, 99.71700286865234)), ('A', '684', 2, 'backbone clash\nsmoc Outlier', (86.357, 103.428, 101.458)), ('A', '685', 2, 'backbone clash\nsmoc Outlier', (86.357, 103.428, 101.458)), ('A', '196', 3, 'smoc Outlier', (116.96900177001953, 115.7300033569336, 64.24400329589844)), ('A', '197', 3, 'smoc Outlier', (114.70099639892578, 118.78099822998047, 64.51699829101562)), ('A', '201', 3, 'side-chain clash', (115.537, 110.692, 59.622)), ('A', '222', 3, 'side-chain clash', (115.537, 110.692, 59.622)), ('A', '223', 3, 'smoc Outlier', (113.1989974975586, 110.5770034790039, 56.119998931884766)), ('A', '224', 3, 'side-chain clash', (119.095, 111.984, 54.169)), ('A', '84', 3, 'Dihedral angle:CB:CG:CD:OE1', (122.387, 106.253, 54.955999999999996)), ('A', '86', 3, 'side-chain clash', (119.095, 111.984, 54.169)), ('A', '611', 4, 'Dihedral angle:CA:C', (91.3, 73.783, 76.503)), ('A', '612', 4, 'Dihedral angle:CA:C\nDihedral angle:N:CA', (90.63499999999999, 74.61, 80.131)), ('A', '613', 4, 'Dihedral angle:N:CA', (93.124, 74.648, 82.96900000000001)), ('A', '614', 4, 'smoc Outlier', (92.70899963378906, 76.56900024414062, 86.21600341796875)), ('A', '615', 4, 'smoc Outlier', (95.15899658203125, 78.9990005493164, 87.78800201416016)), ('A', '768', 4, 'smoc Outlier', (95.97000122070312, 75.86900329589844, 77.73600006103516)), ('A', '802', 4, 'smoc Outlier', (95.05000305175781, 72.50700378417969, 88.17400360107422)), ('A', '706', 5, 'smoc Outlier', (102.20999908447266, 88.16899871826172, 77.13899993896484)), ('A', '707', 5, 'side-chain clash\nsmoc Outlier', (102.573, 88.633, 71.564)), ('A', '710', 5, 'side-chain clash', (102.573, 88.633, 71.564)), ('A', '712', 5, 'side-chain clash', (103.111, 87.233, 66.345)), ('A', '715', 5, 'side-chain clash', (103.111, 87.233, 66.345)), ('A', '720', 5, 'side-chain clash', (97.585, 84.393, 69.69)), ('A', '775', 5, 'side-chain clash', (97.585, 84.393, 69.69)), ('A', '311', 6, 'side-chain clash', (101.953, 110.457, 88.795)), ('A', '314', 6, 'smoc Outlier', (103.98500061035156, 114.11599731445312, 88.81099700927734)), ('A', '315', 6, 'side-chain clash', (101.953, 110.457, 88.795)), ('A', '350', 6, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (100.398, 112.974, 92.147)), ('A', '462', 6, 'smoc Outlier', (106.2239990234375, 103.63899993896484, 90.7979965209961)), ('A', '463', 6, 'smoc Outlier', (105.9800033569336, 105.21700286865234, 87.36000061035156)), ('A', '629', 6, 'smoc Outlier', (98.9219970703125, 105.16300201416016, 90.24600219726562)), ('A', '413', 7, 'side-chain clash', (92.912, 82.821, 121.776)), ('A', '441', 7, 'side-chain clash', (92.912, 82.821, 121.776)), ('A', '546', 7, 'side-chain clash', (90.077, 87.745, 121.258)), ('A', '845', 7, 'side-chain clash\nsmoc Outlier', (90.077, 87.745, 121.258)), ('A', '846', 7, 'side-chain clash\nsmoc Outlier', (84.31, 86.055, 123.011)), ('A', '849', 7, 'side-chain clash', (84.31, 86.055, 123.011)), ('A', '452', 8, 'smoc Outlier', (103.2760009765625, 96.4540023803711, 111.53600311279297)), ('A', '453', 8, 'smoc Outlier', (102.87100219726562, 100.0530014038086, 110.35299682617188)), ('A', '454', 8, 'side-chain clash', (107.817, 98.943, 106.311)), ('A', '457', 8, 'side-chain clash', (107.817, 98.943, 106.311)), ('A', '458', 8, 'smoc Outlier', (107.37799835205078, 98.3290023803711, 100.71700286865234)), ('A', '376', 9, 'side-chain clash', (88.171, 114.948, 108.906)), ('A', '377', 9, 'smoc Outlier', (91.04399871826172, 118.66200256347656, 109.89199829101562)), ('A', '378', 9, 'side-chain clash', (92.83, 118.132, 107.106)), ('A', '537', 9, 'side-chain clash', (92.83, 118.132, 107.106)), ('A', '538', 9, 'side-chain clash', (88.171, 114.948, 108.906)), ('A', '238', 10, 'side-chain clash', (108.188, 106.305, 79.162)), ('A', '239', 10, 'side-chain clash', (103.703, 103.449, 77.461)), ('A', '242', 10, 'side-chain clash', (108.188, 106.305, 79.162)), ('A', '465', 10, 'side-chain clash', (103.703, 103.449, 77.461)), ('A', '468', 10, 'smoc Outlier', (99.75199890136719, 100.7239990234375, 78.30699920654297)), ('A', '854', 11, 'side-chain clash', (75.038, 82.606, 121.853)), ('A', '856', 11, 'side-chain clash', (75.113, 75.962, 117.393)), ('A', '857', 11, 'Dihedral angle:CB:CG:CD:OE1', (74.94300000000001, 79.212, 118.3)), ('A', '858', 11, 'Dihedral angle:CD:NE:CZ:NH1', (78.70700000000001, 79.389, 117.633)), ('A', '860', 11, 'side-chain clash', (75.113, 75.962, 117.393)), ('A', '402', 12, 'side-chain clash', (106.532, 117.841, 124.211)), ('A', '404', 12, 'side-chain clash\nsmoc Outlier', (106.532, 117.841, 124.211)), ('A', '507', 12, 'backbone clash\nside-chain clash', (105.443, 117.846, 124.62)), ('A', '541', 12, 'side-chain clash', (105.443, 117.846, 124.62)), ('A', '420', 13, 'side-chain clash', (90.467, 66.752, 123.463)), ('A', '423', 13, 'side-chain clash', (85.712, 65.525, 119.833)), ('A', '424', 13, 'side-chain clash', (90.467, 66.752, 123.463)), ('A', '883', 13, 'side-chain clash', (85.712, 65.525, 119.833)), ('A', '49', 14, 'side-chain clash', (96.877, 86.432, 95.904)), ('A', '50', 14, 'side-chain clash', (96.877, 86.432, 95.904)), ('A', '761', 14, 'smoc Outlier', (91.61499786376953, 86.56600189208984, 95.21800231933594)), ('A', '754', 15, 'smoc Outlier', (87.71800231933594, 84.0790023803711, 81.91300201416016)), ('A', '755', 15, 'side-chain clash', (91.056, 85.335, 85.529)), ('A', '764', 15, 'side-chain clash', (91.056, 85.335, 85.529)), ('A', '219', 16, 'side-chain clash', (124.322, 109.255, 64.88)), ('A', '96', 16, 'side-chain clash', (124.322, 109.255, 64.88)), ('A', '97', 16, 'smoc Outlier', (128.1510009765625, 106.98200225830078, 67.6520004272461)), ('A', '136', 17, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (114.824, 84.112, 88.193)), ('A', '139', 17, 'side-chain clash', (119.813, 86.096, 87.531)), ('A', '143', 17, 'side-chain clash', (119.813, 86.096, 87.531)), ('A', '494', 18, 'side-chain clash', (74.283, 101.88, 102.759)), ('A', '569', 18, 'side-chain clash', (76.795, 105.633, 99.231)), ('A', '573', 18, 'side-chain clash', (76.795, 105.633, 99.231)), ('A', '128', 19, 'side-chain clash', (114.098, 98.44, 80.902)), ('A', '129', 19, 'smoc Outlier', (113.33499908447266, 93.83699798583984, 78.52999877929688)), ('A', '244', 19, 'side-chain clash', (114.098, 98.44, 80.902)), ('A', '885', 20, 'side-chain clash\nsmoc Outlier', (75.126, 66.036, 118.612)), ('A', '889', 20, 'side-chain clash', (75.126, 66.036, 118.612)), ('A', '916', 20, 'side-chain clash', (70.675, 66.601, 118.021)), ('A', '864', 21, 'smoc Outlier', (77.22899627685547, 74.75199890136719, 108.94000244140625)), ('A', '865', 21, 'smoc Outlier', (80.77899932861328, 75.52300262451172, 107.83399963378906)), ('A', '921', 21, 'side-chain clash', (74.843, 69.617, 112.368)), ('A', '443', 22, 'smoc Outlier', (100.22899627685547, 87.17400360107422, 121.31999969482422)), ('A', '444', 22, 'side-chain clash\nsmoc Outlier', (102.472, 92.897, 118.597)), ('A', '448', 22, 'side-chain clash', (102.472, 92.897, 118.597)), ('A', '571', 23, 'side-chain clash', (81.994, 112.643, 93.42)), ('A', '651', 23, 'smoc Outlier', (84.66699981689453, 114.89199829101562, 90.14800262451172)), ('A', '654', 23, 'side-chain clash', (81.994, 112.643, 93.42)), ('A', '606', 24, 'Dihedral angle:CA:C', (84.306, 77.55, 83.459)), ('A', '607', 24, 'cablam CA Geom Outlier\nDihedral angle:N:CA', (82.0, 79.3, 81.0)), ('A', '608', 24, 'cablam Outlier\nsmoc Outlier', (83.2, 78.0, 77.6)), ('A', '622', 25, 'smoc Outlier', (99.02200317382812, 93.62699890136719, 98.6500015258789)), ('A', '790', 25, 'side-chain clash', (103.547, 95.734, 93.912)), ('A', '161', 26, 'smoc Outlier', (116.72200012207031, 85.73600006103516, 97.0250015258789)), ('A', '167', 26, 'Dihedral angle:CB:CG:CD:OE1', (113.569, 89.40700000000001, 101.51400000000001)), ('A', '333', 27, 'side-chain clash\nsmoc Outlier', (90.657, 129.294, 112.307)), ('A', '340', 27, 'side-chain clash', (90.657, 129.294, 112.307)), ('A', '811', 28, 'smoc Outlier', (92.26000213623047, 77.41200256347656, 96.76300048828125)), ('A', '815', 28, 'smoc Outlier', (87.94599914550781, 77.0260009765625, 100.66000366210938)), ('A', '911', 29, 'side-chain clash', (62.854, 68.854, 113.214)), ('A', '914', 29, 'side-chain clash', (62.854, 68.854, 113.214)), ('A', '531', 30, 'side-chain clash', (84.481, 117.609, 102.161)), ('A', '536', 30, 'side-chain clash', (84.481, 117.609, 102.161)), ('A', '416', 31, 'smoc Outlier', (87.73600006103516, 75.91300201416016, 125.59500122070312)), ('A', '842', 31, 'smoc Outlier', (89.0770034790039, 75.21099853515625, 120.83999633789062)), ('A', '366', 32, 'side-chain clash', (98.438, 126.271, 101.876)), ('A', '374', 32, 'side-chain clash', (98.438, 126.271, 101.876)), ('A', '274', 33, 'cablam Outlier', (104.3, 125.2, 94.9)), ('A', '275', 33, 'cablam Outlier', (107.2, 123.8, 92.8)), ('A', '836', 34, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (90.67099999999999, 76.08, 110.98700000000001)), ('A', '840', 34, 'side-chain clash', (87.731, 79.314, 113.122)), ('A', '427', 35, 'side-chain clash', (91.627, 59.915, 120.087)), ('A', '430', 35, 'side-chain clash', (91.627, 59.915, 120.087)), ('A', '581', 36, 'smoc Outlier', (73.45600128173828, 92.5510025024414, 93.8030014038086)), ('A', '583', 36, 'Dihedral angle:CD:NE:CZ:NH1', (75.039, 87.48, 89.705)), ('A', '303', 37, 'smoc Outlier', (89.28299713134766, 114.33799743652344, 81.79299926757812)), ('A', '306', 37, 'smoc Outlier', (94.43599700927734, 113.47200012207031, 81.23600006103516)), ('A', '382', 38, 'smoc Outlier', (99.35099792480469, 118.80699920654297, 114.22000122070312)), ('A', '503', 38, 'backbone clash\nside-chain clash', (98.338, 122.678, 108.695)), ('A', '388', 39, 'side-chain clash', (106.365, 111.363, 114.201)), ('A', '397', 39, 'side-chain clash', (106.365, 111.363, 114.201)), ('A', '575', 40, 'side-chain clash', (79.074, 102.566, 88.221)), ('A', '641', 40, 'side-chain clash', (79.074, 102.566, 88.221)), ('A', '151', 41, 'cablam CA Geom Outlier', (126.5, 97.9, 90.2)), ('A', '153', 41, 'side-chain clash\nsmoc Outlier', (129.124, 92.483, 93.183)), ('A', '855', 42, 'side-chain clash', (78.275, 74.878, 124.328)), ('A', '891', 42, 'side-chain clash', (78.275, 74.878, 124.328)), ('A', '555', 43, 'smoc Outlier', (97.14399719238281, 92.43499755859375, 111.88899993896484)), ('A', '557', 43, 'smoc Outlier', (92.81999969482422, 97.6760025024414, 110.86399841308594)), ('A', '504', 44, 'cablam Outlier', (89.7, 110.2, 115.5)), ('A', '506', 44, 'smoc Outlier', (85.15899658203125, 111.7969970703125, 116.76300048828125)), ('A', '600', 45, 'smoc Outlier', (77.03199768066406, 78.35099792480469, 89.96499633789062)), ('A', '601', 45, 'smoc Outlier', (80.21099853515625, 80.39600372314453, 90.43599700927734)), ('A', '747', 46, 'smoc Outlier', (85.62899780273438, 89.63700103759766, 73.94499969482422)), ('A', '750', 46, 'side-chain clash', (83.273, 89.279, 78.161)), ('A', '872', 47, 'side-chain clash', (89.272, 66.37, 103.237)), ('A', '877', 47, 'side-chain clash', (89.272, 66.37, 103.237)), ('A', '40', 48, 'smoc Outlier', (103.43599700927734, 96.23600006103516, 58.15299987792969)), ('A', '41', 48, 'side-chain clash', (105.081, 89.836, 57.649)), ('A', '144', 49, 'side-chain clash\nsmoc Outlier', (128.17, 93.231, 82.865)), ('A', '148', 49, 'side-chain clash', (128.17, 93.231, 82.865)), ('A', '806', 50, 'Dihedral angle:CA:C', (86.539, 67.763, 87.557)), ('A', '807', 50, 'Dihedral angle:N:CA', (88.742, 68.861, 90.406)), ('B', '127', 1, 'side-chain clash', (105.443, 117.846, 124.62)), ('B', '129', 1, 'smoc Outlier', (110.04100036621094, 113.6969985961914, 121.68299865722656)), ('B', '130', 1, 'smoc Outlier', (112.60900115966797, 111.1510009765625, 120.4800033569336)), ('B', '141', 1, 'side-chain clash', (118.676, 111.682, 119.483)), ('B', '142', 1, 'side-chain clash', (118.676, 111.682, 119.483)), ('B', '187', 1, 'smoc Outlier', (111.94300079345703, 114.63999938964844, 125.71499633789062)), ('B', '135', 2, 'side-chain clash', (127.073, 104.267, 122.498)), ('B', '139', 2, 'side-chain clash', (127.073, 104.267, 122.498)), ('B', '172', 2, 'side-chain clash', (123.038, 104.726, 126.347)), ('B', '174', 2, 'smoc Outlier', (126.98500061035156, 99.85299682617188, 126.0989990234375)), ('B', '145', 3, 'side-chain clash', (123.835, 119.21, 127.09)), ('B', '146', 3, 'side-chain clash', (123.835, 119.21, 127.09)), ('B', '155', 3, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (118.357, 120.13, 125.65499999999999)), ('B', '96', 4, 'Dihedral angle:CD:NE:CZ:NH1', (96.474, 127.568, 124.48)), ('B', '98', 4, 'cablam CA Geom Outlier\nsmoc Outlier', (98.6, 128.2, 119.1)), ('B', '99', 4, 'smoc Outlier', (98.8239974975586, 131.86199951171875, 118.20999908447266)), ('B', '161', 5, 'smoc Outlier', (111.84500122070312, 103.54499816894531, 128.8699951171875)), ('B', '162', 5, 'smoc Outlier', (108.9540023803711, 101.52799987792969, 127.44300079345703)), ('B', '167', 5, 'smoc Outlier', (116.15399932861328, 106.53399658203125, 133.15499877929688)), ('C', '13', 1, 'side-chain clash', (99.177, 80.015, 132.193)), ('C', '14', 1, 'side-chain clash', (101.469, 83.243, 124.847)), ('C', '15', 1, 'smoc Outlier', (96.7490005493164, 83.69000244140625, 129.80299377441406)), ('C', '16', 1, 'side-chain clash', (99.177, 80.015, 132.193)), ('C', '19', 1, 'side-chain clash', (96.782, 83.234, 135.789)), ('C', '36', 1, 'side-chain clash', (101.469, 83.243, 124.847)), ('C', '40', 1, 'side-chain clash', (99.945, 81.413, 120.901)), ('C', '23', 2, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (102.534, 92.458, 130.539)), ('C', '26', 2, 'smoc Outlier', (107.57499694824219, 94.78900146484375, 128.7760009765625)), ('C', '27', 2, 'smoc Outlier', (111.05599975585938, 93.27100372314453, 129.10000610351562)), ('C', '29', 2, 'side-chain clash', (103.984, 91.869, 129.76)), ('C', '33', 2, 'side-chain clash', (105.523, 88.866, 125.846)), ('C', '3', 3, 'smoc Outlier', (102.38300323486328, 68.15699768066406, 121.302001953125)), ('C', '47', 3, 'Dihedral angle:CB:CG:CD:OE1', (111.821, 71.908, 121.738)), ('C', '48', 3, 'side-chain clash', (105.468, 71.972, 123.582)), ('C', '6', 3, 'side-chain clash', (105.468, 71.972, 123.582)), ('C', '8', 4, 'smoc Outlier', (97.02899932861328, 74.0260009765625, 124.81500244140625)), ('C', '38', 4, 'smoc Outlier', (107.72000122070312, 79.48799896240234, 119.48899841308594)), ('C', '60', 4, 'smoc Outlier', (107.14800262451172, 79.625, 139.26600646972656))]
data['probe'] = [(' P  12    U  O4 ', ' T  19    A  N1 ', -0.982, (63.174, 91.362, 112.464)), (' P  11    A  H61', ' T  20    U  H3 ', -0.775, (59.282, 90.251, 112.733)), (' A 402  THR HG22', ' A 404  ASN  H  ', -0.736, (101.454, 110.919, 125.226)), (' A 386  ASN  ND2', ' B 127  LYS  HD2', -0.714, (106.532, 117.841, 124.211)), (' P  12    U  O4 ', ' T  19    A  C6 ', -0.665, (63.369, 90.514, 112.869)), (' A 790  ASN  O  ', ' A 790  ASN  OD1', -0.645, (103.547, 95.734, 93.912)), (' A 846  ASP  HB3', ' A 849  LYS  HD2', -0.634, (84.31, 86.055, 123.011)), (' A 494  ILE  O  ', ' A 573  GLN  NE2', -0.631, (74.283, 101.88, 102.759)), (' A 911  ASN  HA ', ' A 914  ARG  HD2', -0.628, (62.854, 68.854, 113.214)), (' A 755  MET  HG2', ' A 764  VAL HG22', -0.627, (91.056, 85.335, 85.529)), (' P  12    U  O4 ', ' T  19    A  N6 ', -0.62, (62.486, 90.288, 112.398)), (' C  16  VAL HG23', ' C  19  GLN HE21', -0.61, (96.782, 83.234, 135.789)), (' A 856  ILE  O  ', ' A 860  VAL HG23', -0.608, (75.113, 75.962, 117.393)), (' A  86  ILE HD11', ' A 219  PHE  HB3', -0.606, (119.892, 108.272, 59.675)), (' B 145  THR HG23', ' B 146  THR HG23', -0.585, (123.835, 119.21, 127.09)), (' A 128  VAL  HA ', ' A 244  ILE HD11', -0.558, (114.098, 98.44, 80.902)), (' A 238  TYR  O  ', ' A 242  MET  HG3', -0.555, (108.188, 106.305, 79.162)), (' A 575  LEU HD13', ' A 641  LYS  HG3', -0.554, (79.074, 102.566, 88.221)), (' A 531  THR HG22', ' A 536  ILE HD12', -0.547, (84.481, 117.609, 102.161)), (' A 427  GLY  HA2', ' A 430  LYS  HE3', -0.544, (91.627, 59.915, 120.087)), (' A 311  ALA  O  ', ' A 315  VAL HG23', -0.543, (101.953, 110.457, 88.795)), (' P  12    U  C4 ', ' T  19    A  N1 ', -0.536, (62.6, 92.237, 112.808)), (' A 750  ARG  HG3', ' A 750  ARG HH11', -0.536, (83.273, 89.279, 78.161)), (' B 135  TYR  HE1', ' B 139  LYS  HZ3', -0.532, (126.815, 103.811, 122.244)), (' A 712  GLY  HA2', ' A 715  ILE HD12', -0.528, (103.111, 87.233, 66.345)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.523, (86.083, 109.12, 116.741)), (' A 330  VAL HG11', ' B 117  LEU HD13', -0.523, (98.338, 122.678, 108.695)), (' A  96  VAL HG13', ' A 219  PHE  HZ ', -0.516, (124.322, 109.255, 64.88)), (' A 546  TYR  CE2', ' A 845  ASP  HB2', -0.515, (90.077, 87.745, 121.258)), (' A 872  HIS  CD2', ' A 877  TYR  HD2', -0.513, (89.272, 66.37, 103.237)), (' A 836  ARG HH22', ' A 840  ALA  HB2', -0.511, (87.282, 79.378, 113.542)), (' A 571  PHE  CE1', ' A 654  ARG  HG3', -0.511, (81.994, 112.643, 93.42)), (' A 889  ARG  CZ ', ' A 916  TRP  HB2', -0.504, (70.675, 66.601, 118.021)), (' P  11    A  N6 ', ' T  20    U  H3 ', -0.503, (59.35, 90.614, 112.319)), (' A 836  ARG  NH2', ' A 840  ALA  HB2', -0.497, (87.731, 79.314, 113.122)), (' B 135  TYR  CE2', ' B 172  ILE HG22', -0.49, (123.159, 104.578, 125.759)), (' A 366  LEU HD11', ' A 374  TYR  HE2', -0.49, (84.591, 127.209, 111.246)), (' B 135  TYR  HE2', ' B 172  ILE HG22', -0.485, (123.038, 104.726, 126.347)), (' B 135  TYR  HE1', ' B 139  LYS  NZ ', -0.481, (127.073, 104.267, 122.498)), (' C  29  TRP  O  ', ' C  33  VAL HG23', -0.481, (105.523, 88.866, 125.846)), (' A 423  ALA  HA ', ' A 883  LEU HD11', -0.48, (85.712, 65.525, 119.833)), (" P  14    A  H2'", ' P  15    A  C8 ', -0.48, (72.898, 91.383, 117.48)), (' A 201  ILE HG23', ' A 222  PHE  HB3', -0.48, (115.537, 110.692, 59.622)), (' A 720  VAL HG11', ' A 775  LEU  HG ', -0.479, (97.585, 84.393, 69.69)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.475, (87.493, 97.362, 92.369)), (' A 239  SER  OG ', ' A 465  ASP  OD1', -0.475, (103.703, 103.449, 77.461)), (' A 454  ASP  O  ', ' A 457  ARG  HG2', -0.47, (107.817, 98.943, 106.311)), (' A 665  GLU  N  ', ' A 665  GLU  OE1', -0.464, (96.663, 108.946, 103.951)), (' A 476  VAL HG22', ' A 696  ILE HG22', -0.463, (90.905, 94.911, 84.507)), (' A 507  ASN  ND2', ' A 541  GLN  OE1', -0.462, (90.244, 106.509, 117.163)), (' A 386  ASN HD21', ' B 127  LYS  HD2', -0.462, (105.443, 117.846, 124.62)), (' A 413  GLY  HA3', ' A 441  PHE  CD2', -0.462, (93.084, 83.141, 121.704)), (' A 569  ARG  O  ', ' A 573  GLN  HB2', -0.459, (76.795, 105.633, 99.231)), (' A  49  LEU  O  ', ' A  50  LYS  HD2', -0.459, (117.979, 88.29, 64.139)), (' A 618  ASP  HA ', ' A1102  HOH  O  ', -0.459, (96.877, 86.432, 95.904)), (' A 366  LEU HD11', ' A 374  TYR  CE2', -0.457, (84.916, 126.786, 111.098)), (' A 329  LEU  HB3', ' B 114  CYS  SG ', -0.456, (98.438, 126.271, 101.876)), (' C  13  LEU  HA ', ' C  16  VAL HG12', -0.456, (99.177, 80.015, 132.193)), (' A 388  LEU HD23', ' A 397  SER  HB3', -0.454, (106.365, 111.363, 114.201)), (' A 153  ASP  N  ', ' A 153  ASP  OD1', -0.452, (129.124, 92.483, 93.183)), (' C   6  VAL HG11', ' C  48  ALA  HB1', -0.45, (105.468, 71.972, 123.582)), (' P  10    G  H1 ', ' T  21    C  N4 ', -0.448, (55.742, 90.073, 112.048)), (' A 658  GLU  O  ', ' A 662  VAL HG22', -0.448, (91.224, 108.057, 99.667)), (' A 885  LEU HD11', ' A 921  TYR  CE2', -0.444, (74.843, 69.617, 112.368)), (' A  41  LYS  HB3', ' A  41  LYS  HE3', -0.441, (105.081, 89.836, 57.649)), (' A 136  GLU  N  ', ' A 136  GLU  OE2', -0.44, (113.036, 83.811, 88.022)), (' C  23  GLU  HA ', ' C  29  TRP  HB2', -0.439, (103.984, 91.869, 129.76)), (' A 885  LEU  O  ', ' A 889  ARG  HG2', -0.439, (75.126, 66.036, 118.612)), (' A 855  MET  HE3', ' A 891  LEU HD21', -0.437, (78.275, 74.878, 124.328)), (' A 333  ILE HG22', ' A 340  PHE  HB2', -0.437, (90.657, 129.294, 112.307)), (' A 633  MET  O  ', ' A 637  VAL HG23', -0.435, (90.056, 103.399, 87.303)), (' C  36  HIS  NE2', ' C  40  LEU HD11', -0.432, (100.0, 81.07, 121.576)), (' A 684  ASP  OD1', ' A 685  ALA  N  ', -0.43, (86.357, 103.428, 101.458)), (' A 420  TYR  O  ', ' A 424  VAL HG23', -0.428, (90.467, 66.752, 123.463)), (' A 144  GLU  O  ', ' A 148  THR  OG1', -0.423, (128.17, 93.231, 82.865)), (' A 378  PRO  HD2', ' A 537  PRO  HG2', -0.422, (92.83, 118.132, 107.106)), (' B  90  MET  HB3', ' B  90  MET  HE2', -0.421, (87.107, 119.594, 120.08)), (' A 696  ILE  O  ', ' A 700  VAL HG23', -0.42, (92.512, 93.07, 83.779)), (' B 141  THR HG22', ' B 142  CYS  SG ', -0.413, (118.676, 111.682, 119.483)), (' A  86  ILE HG22', ' A 224  GLN  NE2', -0.413, (119.095, 111.984, 54.169)), (' A 444  GLN  HB3', ' A 448  ALA  HB2', -0.413, (102.472, 92.897, 118.597)), (' A 480  PHE  CZ ', ' A 693  VAL HG22', -0.412, (86.65, 97.561, 89.263)), (' A 413  GLY  HA3', ' A 441  PHE  HD2', -0.412, (92.912, 82.821, 121.776)), (' A 139  CYS  SG ', ' A 143  LYS  HE3', -0.407, (119.813, 86.096, 87.531)), (' A 566  MET  HB2', ' A 566  MET  HE3', -0.405, (78.826, 110.527, 108.04)), (' A 376  ALA  HB1', ' A 538  THR HG22', -0.403, (88.171, 114.948, 108.906)), (' A1003  POP  O3 ', ' A1003  POP  O6 ', -0.403, (98.101, 90.663, 104.478)), (' A 854  LEU  HA ', ' A 854  LEU HD23', -0.403, (75.038, 82.606, 121.853)), (' A 707  LEU  O  ', ' A 710  THR HG22', -0.402, (102.573, 88.633, 71.564)), (' C  36  HIS  HE2', ' C  40  LEU HD11', -0.4, (99.945, 81.413, 120.901)), (' C  14  LEU HD22', ' C  36  HIS  ND1', -0.4, (101.469, 83.243, 124.847))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (89.03799999999995, 112.62199999999997, 115.596)), ('A', ' 607 ', 'SER', None, (83.15, 79.049, 81.895)), ('B', ' 183 ', 'PRO', None, (111.87800000000003, 100.49799999999999, 123.702))]
data['cablam'] = [('A', '45', 'PHE', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (108.6, 94.2, 71.9)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (104.3, 125.2, 94.9)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (107.2, 123.8, 92.8)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (89.7, 110.2, 115.5)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nTTT-S', (83.2, 78.0, 77.6)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (103.3, 106.6, 102.0)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (126.5, 97.9, 90.2)), ('A', '607', 'SER', 'check CA trace', 'turn\nHTTT-', (82.0, 79.3, 81.0)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (100.5, 105.0, 100.1)), ('B', '98', 'LEU', 'check CA trace', 'turn\nGTTT-', (98.6, 128.2, 119.1))]
data['smoc'] = [('A', 40, 'ASP', 0.5842950001254855, (103.43599700927734, 96.23600006103516, 58.15299987792969)), ('A', 45, 'PHE', 0.6291596181746305, (108.59400177001953, 94.19400024414062, 71.9209976196289)), ('A', 93, 'CYS', 0.3630612541137444, (125.73699951171875, 115.72000122070312, 67.4739990234375)), ('A', 97, 'ALA', 0.5106694686265538, (128.1510009765625, 106.98200225830078, 67.6520004272461)), ('A', 100, 'ASP', 0.47423617556459424, (133.33799743652344, 104.4489974975586, 59.5989990234375)), ('A', 129, 'TYR', 0.5909152603340773, (113.33499908447266, 93.83699798583984, 78.52999877929688)), ('A', 144, 'GLU', 0.619416631530002, (125.90899658203125, 90.53800201416016, 83.18800354003906)), ('A', 153, 'ASP', 0.5913929411954223, (129.927001953125, 91.84700012207031, 91.6500015258789)), ('A', 161, 'ASP', 0.45626163157892946, (116.72200012207031, 85.73600006103516, 97.0250015258789)), ('A', 196, 'MET', 0.5688132302756873, (116.96900177001953, 115.7300033569336, 64.24400329589844)), ('A', 197, 'ARG', 0.5824871447840512, (114.70099639892578, 118.78099822998047, 64.51699829101562)), ('A', 211, 'ASP', 0.5568134581339783, (123.68699645996094, 102.03399658203125, 73.56900024414062)), ('A', 223, 'ILE', 0.5728592490498022, (113.1989974975586, 110.5770034790039, 56.119998931884766)), ('A', 266, 'ILE', 0.6469353031030951, (119.84600067138672, 121.5770034790039, 97.36699676513672)), ('A', 270, 'LEU', 0.5781926502820502, (110.7040023803711, 125.11000061035156, 104.25800323486328)), ('A', 291, 'ASP', 0.5810081027041804, (103.94300079345703, 115.24500274658203, 72.33699798583984)), ('A', 303, 'ASP', 0.5478983100001015, (89.28299713134766, 114.33799743652344, 81.79299926757812)), ('A', 306, 'CYS', 0.5582622006262005, (94.43599700927734, 113.47200012207031, 81.23600006103516)), ('A', 314, 'ASN', 0.5736529241447219, (103.98500061035156, 114.11599731445312, 88.81099700927734)), ('A', 333, 'ILE', 0.5864608397368486, (91.59300231933594, 132.1510009765625, 110.11199951171875)), ('A', 350, 'GLU', 0.5469259817533468, (100.39800262451172, 112.9739990234375, 92.14700317382812)), ('A', 354, 'VAL', 0.5905616848952399, (94.73500061035156, 122.06900024414062, 94.99600219726562)), ('A', 377, 'ASP', 0.5837872590909879, (91.04399871826172, 118.66200256347656, 109.89199829101562)), ('A', 382, 'ALA', 0.536107554356439, (99.35099792480469, 118.80699920654297, 114.22000122070312)), ('A', 404, 'ASN', 0.6069516443263019, (103.55899810791016, 109.59500122070312, 126.35399627685547)), ('A', 416, 'ASN', 0.5192344923433996, (87.73600006103516, 75.91300201416016, 125.59500122070312)), ('A', 443, 'ALA', 0.535329608335752, (100.22899627685547, 87.17400360107422, 121.31999969482422)), ('A', 444, 'GLN', 0.5668794825951807, (102.01100158691406, 90.43299865722656, 120.43599700927734)), ('A', 452, 'ASP', 0.5565203081992713, (103.2760009765625, 96.4540023803711, 111.53600311279297)), ('A', 453, 'TYR', 0.5785866716147536, (102.87100219726562, 100.0530014038086, 110.35299682617188)), ('A', 458, 'TYR', 0.5939543916835757, (107.37799835205078, 98.3290023803711, 100.71700286865234)), ('A', 462, 'THR', 0.5578392078628207, (106.2239990234375, 103.63899993896484, 90.7979965209961)), ('A', 463, 'MET', 0.5400436502480873, (105.9800033569336, 105.21700286865234, 87.36000061035156)), ('A', 468, 'GLN', 0.5626536434481689, (99.75199890136719, 100.7239990234375, 78.30699920654297)), ('A', 482, 'CYS', 0.6114319947838681, (76.6760025024414, 96.33899688720703, 83.60700225830078)), ('A', 487, 'CYS', 0.6170334726889538, (75.16999816894531, 110.18699645996094, 93.5)), ('A', 506, 'PHE', 0.5815362882019836, (85.15899658203125, 111.7969970703125, 116.76300048828125)), ('A', 555, 'ARG', 0.46149877604232703, (97.14399719238281, 92.43499755859375, 111.88899993896484)), ('A', 557, 'VAL', 0.4580537657870166, (92.81999969482422, 97.6760025024414, 110.86399841308594)), ('A', 560, 'VAL', 0.5587607893928056, (88.56600189208984, 106.17400360107422, 109.01699829101562)), ('A', 581, 'ALA', 0.62952636514681, (73.45600128173828, 92.5510025024414, 93.8030014038086)), ('A', 600, 'ASN', 0.6196111863300666, (77.03199768066406, 78.35099792480469, 89.96499633789062)), ('A', 601, 'MET', 0.5855009693026827, (80.21099853515625, 80.39600372314453, 90.43599700927734)), ('A', 608, 'ASP', 0.5322468423798552, (83.22599792480469, 78.03199768066406, 77.58499908447266)), ('A', 614, 'LEU', 0.6148219194871699, (92.70899963378906, 76.56900024414062, 86.21600341796875)), ('A', 615, 'MET', 0.6124820462236701, (95.15899658203125, 78.9990005493164, 87.78800201416016)), ('A', 622, 'CYS', 0.5433282035584738, (99.02200317382812, 93.62699890136719, 98.6500015258789)), ('A', 629, 'MET', 0.5573916399886664, (98.9219970703125, 105.16300201416016, 90.24600219726562)), ('A', 634, 'ALA', 0.4654984533725355, (90.7490005493164, 102.32499694824219, 90.5739974975586)), ('A', 651, 'ARG', 0.5670102603995777, (84.66699981689453, 114.89199829101562, 90.14800262451172)), ('A', 658, 'GLU', 0.5151270071920709, (89.54299926757812, 110.4020004272461, 98.21900177001953)), ('A', 665, 'GLU', 0.523981663010248, (96.34600067138672, 110.67900085449219, 104.78099822998047)), ('A', 679, 'GLY', 0.5298052308650318, (98.59500122070312, 101.71900177001953, 99.71700286865234)), ('A', 684, 'ASP', 0.4487696969210178, (87.76499938964844, 102.6240005493164, 103.31600189208984)), ('A', 685, 'ALA', 0.528027249049114, (84.21800231933594, 102.04299926757812, 102.07599639892578)), ('A', 706, 'ALA', 0.5888338109729753, (102.20999908447266, 88.16899871826172, 77.13899993896484)), ('A', 707, 'LEU', 0.6099428745479116, (100.65799713134766, 88.97899627685547, 73.76899719238281)), ('A', 718, 'LYS', 0.6145966174302044, (96.0479965209961, 84.8290023803711, 61.23400115966797)), ('A', 729, 'GLU', 0.5465585654458132, (99.10800170898438, 100.06099700927734, 67.20899963378906)), ('A', 740, 'ASP', 0.6042369828958082, (85.97599792480469, 98.73100280761719, 68.53500366210938)), ('A', 747, 'ALA', 0.5409857897370902, (85.62899780273438, 89.63700103759766, 73.94499969482422)), ('A', 754, 'SER', 0.5271469616810309, (87.71800231933594, 84.0790023803711, 81.91300201416016)), ('A', 761, 'ASP', 0.5545968335005242, (91.61499786376953, 86.56600189208984, 95.21800231933594)), ('A', 768, 'SER', 0.6520116120088867, (95.97000122070312, 75.86900329589844, 77.73600006103516)), ('A', 796, 'GLU', 0.6069747566479222, (105.625, 80.15899658203125, 92.41699981689453)), ('A', 802, 'GLU', 0.5210754185485095, (95.05000305175781, 72.50700378417969, 88.17400360107422)), ('A', 811, 'GLU', 0.555716547870558, (92.26000213623047, 77.41200256347656, 96.76300048828125)), ('A', 815, 'GLN', 0.6049936044523347, (87.94599914550781, 77.0260009765625, 100.66000366210938)), ('A', 825, 'ASP', 0.621831434325992, (73.72599792480469, 64.91000366210938, 89.75499725341797)), ('A', 842, 'CYS', 0.5645178553576623, (89.0770034790039, 75.21099853515625, 120.83999633789062)), ('A', 845, 'ASP', 0.5686473783060101, (88.65499877929688, 85.68699645996094, 122.21399688720703)), ('A', 846, 'ASP', 0.5016156968122567, (86.18399810791016, 86.20899963378906, 125.11299896240234)), ('A', 864, 'ILE', 0.6140129699663365, (77.22899627685547, 74.75199890136719, 108.94000244140625)), ('A', 865, 'ASP', 0.6110270374043236, (80.77899932861328, 75.52300262451172, 107.83399963378906)), ('A', 885, 'LEU', 0.5649338407219887, (77.02100372314453, 67.48999786376953, 115.97000122070312)), ('A', 922, 'GLU', 0.6306752115662875, (72.36399841308594, 69.27100372314453, 104.28700256347656)), ('B', 83, 'VAL', 0.49239082538730017, (78.53800201416016, 117.12000274658203, 120.9229965209961)), ('B', 90, 'MET', 0.5206557673021703, (88.20099639892578, 120.9020004272461, 122.26499938964844)), ('B', 98, 'LEU', 0.4456113012332028, (98.64199829101562, 128.1529998779297, 119.08999633789062)), ('B', 99, 'ASP', 0.4822202999207243, (98.8239974975586, 131.86199951171875, 118.20999908447266)), ('B', 106, 'ILE', 0.568164685439981, (106.322998046875, 131.6790008544922, 110.11000061035156)), ('B', 125, 'ALA', 0.5869487455310979, (107.1729965209961, 123.31600189208984, 118.53299713134766)), ('B', 129, 'MET', 0.6100936330780626, (110.04100036621094, 113.6969985961914, 121.68299865722656)), ('B', 130, 'VAL', 0.6249814779952365, (112.60900115966797, 111.1510009765625, 120.4800033569336)), ('B', 134, 'ASP', 0.5983134904003988, (118.54499816894531, 100.59600067138672, 120.57499694824219)), ('B', 155, 'GLU', 0.6541592323624376, (118.35700225830078, 120.12999725341797, 125.65499877929688)), ('B', 161, 'ASP', 0.5962657563282341, (111.84500122070312, 103.54499816894531, 128.8699951171875)), ('B', 162, 'ALA', 0.6105667410061094, (108.9540023803711, 101.52799987792969, 127.44300079345703)), ('B', 167, 'VAL', 0.6038155464158138, (116.15399932861328, 106.53399658203125, 133.15499877929688)), ('B', 174, 'MET', 0.5513652233782382, (126.98500061035156, 99.85299682617188, 126.0989990234375)), ('B', 178, 'PRO', 0.639910313571768, (120.73200225830078, 95.08100128173828, 127.88600158691406)), ('B', 187, 'THR', 0.5932740434880728, (111.94300079345703, 114.63999938964844, 125.71499633789062)), ('C', 3, 'MET', 0.4829013658200967, (102.38300323486328, 68.15699768066406, 121.302001953125)), ('C', 8, 'CYS', 0.5451676439906663, (97.02899932861328, 74.0260009765625, 124.81500244140625)), ('C', 15, 'SER', 0.573122095521028, (96.7490005493164, 83.69000244140625, 129.80299377441406)), ('C', 26, 'SER', 0.5419789952860226, (107.57499694824219, 94.78900146484375, 128.7760009765625)), ('C', 27, 'LYS', 0.6118138431340674, (111.05599975585938, 93.27100372314453, 129.10000610351562)), ('C', 38, 'ASP', 0.39573546289942146, (107.72000122070312, 79.48799896240234, 119.48899841308594)), ('C', 60, 'LEU', 0.4758907027389859, (107.14800262451172, 79.625, 139.26600646972656))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30210/7bv2/Model_validation_9/validation_cootdata/molprobity_probe7bv2_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)


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
data['clusters'] = [('A', '476', 1, 'side-chain clash', (90.905, 94.911, 84.507)), ('A', '480', 1, 'side-chain clash', (86.65, 97.561, 89.263)), ('A', '633', 1, 'side-chain clash\nsmoc Outlier', (90.056, 103.399, 87.303)), ('A', '634', 1, 'smoc Outlier', (90.74900000000001, 102.32499999999999, 90.574)), ('A', '637', 1, 'side-chain clash', (90.056, 103.399, 87.303)), ('A', '689', 1, 'side-chain clash', (87.493, 97.362, 92.369)), ('A', '693', 1, 'side-chain clash', (86.65, 97.561, 89.263)), ('A', '696', 1, 'side-chain clash', (92.512, 93.07, 83.779)), ('A', '699', 1, 'smoc Outlier', (95.456, 90.512, 84.893)), ('A', '700', 1, 'side-chain clash', (92.512, 93.07, 83.779)), ('A', '754', 1, 'smoc Outlier', (87.718, 84.079, 81.91300000000001)), ('A', '755', 1, 'side-chain clash', (91.056, 85.335, 85.529)), ('A', '764', 1, 'side-chain clash\nsmoc Outlier', (91.056, 85.335, 85.529)), ('A', '330', 2, 'smoc Outlier', (97.296, 125.726, 106.25)), ('A', '366', 2, 'side-chain clash\nsmoc Outlier', (98.438, 126.271, 101.876)), ('A', '374', 2, 'side-chain clash', (98.438, 126.271, 101.876)), ('A', '382', 2, 'smoc Outlier', (99.351, 118.807, 114.22)), ('A', '385', 2, 'smoc Outlier', (101.32799999999999, 118.80799999999999, 119.127)), ('A', '402', 2, 'side-chain clash', (106.532, 117.841, 124.211)), ('A', '404', 2, 'side-chain clash', (106.532, 117.841, 124.211)), ('A', '503', 2, 'backbone clash\nside-chain clash', (98.338, 122.678, 108.695)), ('A', '507', 2, 'backbone clash\nside-chain clash\nsmoc Outlier', (105.443, 117.846, 124.62)), ('A', '541', 2, 'side-chain clash', (105.443, 117.846, 124.62)), ('A', '658', 3, 'side-chain clash', (91.224, 108.057, 99.667)), ('A', '662', 3, 'side-chain clash', (91.224, 108.057, 99.667)), ('A', '665', 3, 'side-chain clash\nsmoc Outlier', (96.663, 108.946, 103.951)), ('A', '677', 3, 'cablam Outlier', (103.3, 106.6, 102.0)), ('A', '678', 3, 'cablam CA Geom Outlier', (100.5, 105.0, 100.1)), ('A', '684', 3, 'backbone clash', (86.357, 103.428, 101.458)), ('A', '685', 3, 'backbone clash', (86.357, 103.428, 101.458)), ('A', '196', 4, 'smoc Outlier', (116.96900000000001, 115.73, 64.24400000000001)), ('A', '197', 4, 'smoc Outlier', (114.70100000000001, 118.781, 64.51700000000001)), ('A', '201', 4, 'side-chain clash', (115.537, 110.692, 59.622)), ('A', '222', 4, 'side-chain clash', (115.537, 110.692, 59.622)), ('A', '224', 4, 'side-chain clash', (119.095, 111.984, 54.169)), ('A', '84', 4, 'Dihedral angle:CB:CG:CD:OE1', (122.387, 106.253, 54.955999999999996)), ('A', '86', 4, 'side-chain clash', (119.095, 111.984, 54.169)), ('A', '707', 5, 'side-chain clash', (102.573, 88.633, 71.564)), ('A', '710', 5, 'side-chain clash', (102.573, 88.633, 71.564)), ('A', '712', 5, 'side-chain clash', (103.111, 87.233, 66.345)), ('A', '715', 5, 'side-chain clash', (103.111, 87.233, 66.345)), ('A', '720', 5, 'side-chain clash', (97.585, 84.393, 69.69)), ('A', '775', 5, 'side-chain clash', (97.585, 84.393, 69.69)), ('A', '522', 6, 'Dihedral angle:CB:CG:CD:OE1', (70.051, 118.842, 104.829)), ('A', '524', 6, 'smoc Outlier', (74.52799999999999, 115.864, 105.428)), ('A', '525', 6, 'smoc Outlier', (73.691, 117.09400000000001, 101.923)), ('A', '528', 6, 'smoc Outlier', (78.51, 116.35499999999999, 100.695)), ('A', '531', 6, 'side-chain clash', (84.481, 117.609, 102.161)), ('A', '536', 6, 'side-chain clash', (84.481, 117.609, 102.161)), ('A', '413', 7, 'side-chain clash', (92.912, 82.821, 121.776)), ('A', '441', 7, 'side-chain clash', (92.912, 82.821, 121.776)), ('A', '546', 7, 'side-chain clash', (90.077, 87.745, 121.258)), ('A', '845', 7, 'side-chain clash', (90.077, 87.745, 121.258)), ('A', '846', 7, 'side-chain clash', (84.31, 86.055, 123.011)), ('A', '849', 7, 'side-chain clash', (84.31, 86.055, 123.011)), ('A', '854', 8, 'side-chain clash', (75.038, 82.606, 121.853)), ('A', '856', 8, 'side-chain clash', (75.113, 75.962, 117.393)), ('A', '857', 8, 'Dihedral angle:CB:CG:CD:OE1', (74.94300000000001, 79.212, 118.3)), ('A', '858', 8, 'Dihedral angle:CD:NE:CZ:NH1', (78.70700000000001, 79.389, 117.633)), ('A', '859', 8, 'smoc Outlier', (78.9, 75.614, 117.15799999999999)), ('A', '860', 8, 'side-chain clash\nsmoc Outlier', (75.113, 75.962, 117.393)), ('A', '144', 9, 'side-chain clash', (128.17, 93.231, 82.865)), ('A', '146', 9, 'smoc Outlier', (124.809, 94.526, 86.74100000000001)), ('A', '148', 9, 'side-chain clash', (128.17, 93.231, 82.865)), ('A', '151', 9, 'cablam CA Geom Outlier', (126.5, 97.9, 90.2)), ('A', '153', 9, 'side-chain clash', (129.124, 92.483, 93.183)), ('A', '125', 10, 'smoc Outlier', (116.262, 97.62299999999999, 75.073)), ('A', '128', 10, 'side-chain clash', (114.098, 98.44, 80.902)), ('A', '129', 10, 'smoc Outlier', (113.335, 93.837, 78.53)), ('A', '208', 10, 'smoc Outlier', (117.296, 99.04700000000001, 70.699)), ('A', '244', 10, 'side-chain clash', (114.098, 98.44, 80.902)), ('A', '376', 11, 'side-chain clash\nsmoc Outlier', (88.171, 114.948, 108.906)), ('A', '377', 11, 'smoc Outlier', (91.04400000000001, 118.66199999999999, 109.892)), ('A', '378', 11, 'side-chain clash', (92.83, 118.132, 107.106)), ('A', '537', 11, 'side-chain clash', (92.83, 118.132, 107.106)), ('A', '538', 11, 'side-chain clash', (88.171, 114.948, 108.906)), ('A', '219', 12, 'side-chain clash\nsmoc Outlier', (124.322, 109.255, 64.88)), ('A', '93', 12, 'smoc Outlier', (125.73700000000001, 115.72, 67.474)), ('A', '95', 12, 'smoc Outlier', (124.972, 111.753, 71.077)), ('A', '96', 12, 'side-chain clash', (124.322, 109.255, 64.88)), ('A', '504', 13, 'cablam Outlier', (89.7, 110.2, 115.5)), ('A', '506', 13, 'smoc Outlier', (85.15899999999999, 111.79700000000001, 116.763)), ('A', '540', 13, 'smoc Outlier', (92.96300000000001, 107.592, 110.104)), ('A', '560', 13, 'smoc Outlier', (88.566, 106.17399999999999, 109.01700000000001)), ('A', '420', 14, 'side-chain clash', (90.467, 66.752, 123.463)), ('A', '423', 14, 'side-chain clash', (85.712, 65.525, 119.833)), ('A', '424', 14, 'side-chain clash', (90.467, 66.752, 123.463)), ('A', '883', 14, 'side-chain clash', (85.712, 65.525, 119.833)), ('A', '311', 15, 'side-chain clash', (101.953, 110.457, 88.795)), ('A', '312', 15, 'smoc Outlier', (102.151, 109.755, 86.166)), ('A', '315', 15, 'side-chain clash', (101.953, 110.457, 88.795)), ('A', '350', 15, 'Dihedral angle:CB:CG:CD:OE1', (100.398, 112.974, 92.147)), ('A', '442', 16, 'smoc Outlier', (99.24600000000001, 84.66999999999999, 118.641)), ('A', '443', 16, 'smoc Outlier', (100.229, 87.17399999999999, 121.32)), ('A', '444', 16, 'side-chain clash', (102.472, 92.897, 118.597)), ('A', '448', 16, 'side-chain clash\nsmoc Outlier', (102.472, 92.897, 118.597)), ('A', '238', 17, 'side-chain clash', (108.188, 106.305, 79.162)), ('A', '239', 17, 'side-chain clash', (103.703, 103.449, 77.461)), ('A', '242', 17, 'side-chain clash', (108.188, 106.305, 79.162)), ('A', '465', 17, 'side-chain clash', (103.703, 103.449, 77.461)), ('A', '602', 18, 'smoc Outlier', (82.4, 77.548, 89.198)), ('A', '606', 18, 'Dihedral angle:CA:C', (84.306, 77.55, 83.459)), ('A', '607', 18, 'Dihedral angle:N:CA\ncablam CA Geom Outlier', (82.021, 79.336, 80.986)), ('A', '608', 18, 'cablam Outlier', (83.2, 78.0, 77.6)), ('A', '49', 19, 'side-chain clash', (96.877, 86.432, 95.904)), ('A', '50', 19, 'side-chain clash', (96.877, 86.432, 95.904)), ('A', '761', 19, 'smoc Outlier', (91.615, 86.566, 95.218)), ('A', '136', 20, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (114.824, 84.112, 88.193)), ('A', '139', 20, 'side-chain clash', (119.813, 86.096, 87.531)), ('A', '143', 20, 'side-chain clash', (119.813, 86.096, 87.531)), ('A', '494', 21, 'side-chain clash', (74.283, 101.88, 102.759)), ('A', '569', 21, 'side-chain clash', (76.795, 105.633, 99.231)), ('A', '573', 21, 'side-chain clash', (76.795, 105.633, 99.231)), ('A', '911', 22, 'side-chain clash', (62.854, 68.854, 113.214)), ('A', '912', 22, 'smoc Outlier', (64.364, 70.842, 108.59400000000001)), ('A', '914', 22, 'side-chain clash', (62.854, 68.854, 113.214)), ('A', '885', 23, 'side-chain clash\nsmoc Outlier', (75.126, 66.036, 118.612)), ('A', '889', 23, 'side-chain clash', (75.126, 66.036, 118.612)), ('A', '916', 23, 'side-chain clash', (70.675, 66.601, 118.021)), ('A', '512', 24, 'smoc Outlier', (78.62799999999999, 106.756, 114.24000000000001)), ('A', '515', 24, 'smoc Outlier', (76.742, 111.816, 114.21300000000001)), ('A', '566', 24, 'side-chain clash', (78.826, 110.527, 108.04)), ('A', '611', 25, 'Dihedral angle:CA:C', (91.3, 73.783, 76.503)), ('A', '612', 25, 'Dihedral angle:CA:C\nDihedral angle:N:CA', (90.63499999999999, 74.61, 80.131)), ('A', '613', 25, 'Dihedral angle:N:CA', (93.124, 74.648, 82.96900000000001)), ('A', '161', 26, 'smoc Outlier', (116.722, 85.736, 97.02499999999999)), ('A', '167', 26, 'Dihedral angle:CB:CG:CD:OE1', (113.569, 89.40700000000001, 101.51400000000001)), ('A', '333', 27, 'side-chain clash', (90.657, 129.294, 112.307)), ('A', '340', 27, 'side-chain clash', (90.657, 129.294, 112.307)), ('A', '811', 28, 'smoc Outlier', (92.26, 77.412, 96.763)), ('A', '815', 28, 'smoc Outlier', (87.94600000000001, 77.026, 100.66)), ('A', '864', 29, 'smoc Outlier', (77.229, 74.752, 108.94000000000001)), ('A', '921', 29, 'side-chain clash', (74.843, 69.617, 112.368)), ('A', '388', 30, 'side-chain clash', (106.365, 111.363, 114.201)), ('A', '397', 30, 'side-chain clash', (106.365, 111.363, 114.201)), ('A', '274', 31, 'cablam Outlier', (104.3, 125.2, 94.9)), ('A', '275', 31, 'cablam Outlier', (107.2, 123.8, 92.8)), ('A', '836', 32, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (90.67099999999999, 76.08, 110.98700000000001)), ('A', '840', 32, 'side-chain clash', (87.731, 79.314, 113.122)), ('A', '625', 33, 'smoc Outlier', (102.899, 97.56700000000001, 98.17899999999999)), ('A', '790', 33, 'side-chain clash', (103.547, 95.734, 93.912)), ('A', '427', 34, 'side-chain clash', (91.627, 59.915, 120.087)), ('A', '430', 34, 'side-chain clash', (91.627, 59.915, 120.087)), ('A', '575', 35, 'side-chain clash', (79.074, 102.566, 88.221)), ('A', '641', 35, 'side-chain clash', (79.074, 102.566, 88.221)), ('A', '571', 36, 'side-chain clash', (81.994, 112.643, 93.42)), ('A', '654', 36, 'side-chain clash', (81.994, 112.643, 93.42)), ('A', '454', 37, 'side-chain clash', (107.817, 98.943, 106.311)), ('A', '457', 37, 'side-chain clash', (107.817, 98.943, 106.311)), ('A', '855', 38, 'side-chain clash', (78.275, 74.878, 124.328)), ('A', '891', 38, 'side-chain clash', (78.275, 74.878, 124.328)), ('A', '727', 39, 'smoc Outlier', (97.024, 95.897, 69.99000000000001)), ('A', '729', 39, 'Dihedral angle:CB:CG:CD:OE1', (99.10799999999999, 100.061, 67.209)), ('A', '872', 40, 'side-chain clash', (89.272, 66.37, 103.237)), ('A', '877', 40, 'side-chain clash', (89.272, 66.37, 103.237)), ('A', '806', 41, 'Dihedral angle:CA:C', (86.539, 67.763, 87.557)), ('A', '807', 41, 'Dihedral angle:N:CA', (88.742, 68.861, 90.406)), ('B', '145', 1, 'side-chain clash', (123.835, 119.21, 127.09)), ('B', '146', 1, 'side-chain clash', (123.835, 119.21, 127.09)), ('B', '155', 1, 'Dihedral angle:CB:CG:CD:OE1', (118.357, 120.13, 125.65499999999999)), ('B', '96', 2, 'Dihedral angle:CD:NE:CZ:NH1', (96.474, 127.568, 124.48)), ('B', '98', 2, 'cablam CA Geom Outlier\nsmoc Outlier', (98.6, 128.2, 119.1)), ('B', '99', 2, 'smoc Outlier', (98.824, 131.86200000000002, 118.21000000000001)), ('B', '135', 3, 'side-chain clash', (127.073, 104.267, 122.498)), ('B', '139', 3, 'side-chain clash', (127.073, 104.267, 122.498)), ('B', '172', 3, 'side-chain clash\nsmoc Outlier', (123.038, 104.726, 126.347)), ('B', '141', 4, 'side-chain clash', (118.676, 111.682, 119.483)), ('B', '142', 4, 'side-chain clash\nsmoc Outlier', (118.676, 111.682, 119.483)), ('C', '13', 1, 'side-chain clash', (99.177, 80.015, 132.193)), ('C', '14', 1, 'side-chain clash', (101.469, 83.243, 124.847)), ('C', '15', 1, 'smoc Outlier', (96.74900000000001, 83.69, 129.803)), ('C', '16', 1, 'side-chain clash', (99.177, 80.015, 132.193)), ('C', '19', 1, 'side-chain clash', (96.782, 83.234, 135.789)), ('C', '36', 1, 'side-chain clash', (101.469, 83.243, 124.847)), ('C', '40', 1, 'side-chain clash', (99.945, 81.413, 120.901)), ('C', '47', 2, 'Dihedral angle:CB:CG:CD:OE1', (111.821, 71.908, 121.738)), ('C', '48', 2, 'side-chain clash', (105.468, 71.972, 123.582)), ('C', '6', 2, 'side-chain clash', (105.468, 71.972, 123.582)), ('C', '23', 3, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (102.534, 92.458, 130.539)), ('C', '29', 3, 'side-chain clash', (103.984, 91.869, 129.76)), ('C', '33', 3, 'side-chain clash', (105.523, 88.866, 125.846)), ('C', '8', 4, 'smoc Outlier', (97.029, 74.026, 124.815)), ('C', '38', 4, 'smoc Outlier', (107.72, 79.488, 119.489)), ('C', '60', 4, 'smoc Outlier', (107.148, 79.62499999999999, 139.266)), ('P', '14', 1, 'side-chain clash', (55.742, 90.073, 112.048)), ('P', '15', 1, 'side-chain clash', (55.742, 90.073, 112.048)), ('P', '11', 2, 'Backbone torsion suites: ', (60.281, 94.459, 106.513)), ('P', '20', 2, "Bond length:P:O5'", (87.99400000000001, 89.409, 102.065)), ('T', '19', 1, 'side-chain clash', (62.6, 92.237, 112.808)), ('T', '20', 1, 'side-chain clash', (59.35, 90.614, 112.319)), ('T', '21', 1, 'side-chain clash', (55.742, 90.073, 112.048)), ('T', '13', 2, 'smoc Outlier', (79.574, 90.412, 101.866))]
data['probe'] = [(' P  12    U  O4 ', ' T  19    A  N1 ', -0.982, (63.174, 91.362, 112.464)), (' P  11    A  H61', ' T  20    U  H3 ', -0.775, (59.282, 90.251, 112.733)), (' A 402  THR HG22', ' A 404  ASN  H  ', -0.736, (101.454, 110.919, 125.226)), (' A 386  ASN  ND2', ' B 127  LYS  HD2', -0.714, (106.532, 117.841, 124.211)), (' P  12    U  O4 ', ' T  19    A  C6 ', -0.665, (63.369, 90.514, 112.869)), (' A 790  ASN  O  ', ' A 790  ASN  OD1', -0.645, (103.547, 95.734, 93.912)), (' A 846  ASP  HB3', ' A 849  LYS  HD2', -0.634, (84.31, 86.055, 123.011)), (' A 494  ILE  O  ', ' A 573  GLN  NE2', -0.631, (74.283, 101.88, 102.759)), (' A 911  ASN  HA ', ' A 914  ARG  HD2', -0.628, (62.854, 68.854, 113.214)), (' A 755  MET  HG2', ' A 764  VAL HG22', -0.627, (91.056, 85.335, 85.529)), (' P  12    U  O4 ', ' T  19    A  N6 ', -0.62, (62.486, 90.288, 112.398)), (' C  16  VAL HG23', ' C  19  GLN HE21', -0.61, (96.782, 83.234, 135.789)), (' A 856  ILE  O  ', ' A 860  VAL HG23', -0.608, (75.113, 75.962, 117.393)), (' A  86  ILE HD11', ' A 219  PHE  HB3', -0.606, (119.892, 108.272, 59.675)), (' B 145  THR HG23', ' B 146  THR HG23', -0.585, (123.835, 119.21, 127.09)), (' A 128  VAL  HA ', ' A 244  ILE HD11', -0.558, (114.098, 98.44, 80.902)), (' A 238  TYR  O  ', ' A 242  MET  HG3', -0.555, (108.188, 106.305, 79.162)), (' A 575  LEU HD13', ' A 641  LYS  HG3', -0.554, (79.074, 102.566, 88.221)), (' A 531  THR HG22', ' A 536  ILE HD12', -0.547, (84.481, 117.609, 102.161)), (' A 427  GLY  HA2', ' A 430  LYS  HE3', -0.544, (91.627, 59.915, 120.087)), (' A 311  ALA  O  ', ' A 315  VAL HG23', -0.543, (101.953, 110.457, 88.795)), (' P  12    U  C4 ', ' T  19    A  N1 ', -0.536, (62.6, 92.237, 112.808)), (' A 750  ARG  HG3', ' A 750  ARG HH11', -0.536, (83.273, 89.279, 78.161)), (' B 135  TYR  HE1', ' B 139  LYS  HZ3', -0.532, (126.815, 103.811, 122.244)), (' A 712  GLY  HA2', ' A 715  ILE HD12', -0.528, (103.111, 87.233, 66.345)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.523, (86.083, 109.12, 116.741)), (' A 330  VAL HG11', ' B 117  LEU HD13', -0.523, (98.338, 122.678, 108.695)), (' A  96  VAL HG13', ' A 219  PHE  HZ ', -0.516, (124.322, 109.255, 64.88)), (' A 546  TYR  CE2', ' A 845  ASP  HB2', -0.515, (90.077, 87.745, 121.258)), (' A 872  HIS  CD2', ' A 877  TYR  HD2', -0.513, (89.272, 66.37, 103.237)), (' A 836  ARG HH22', ' A 840  ALA  HB2', -0.511, (87.282, 79.378, 113.542)), (' A 571  PHE  CE1', ' A 654  ARG  HG3', -0.511, (81.994, 112.643, 93.42)), (' A 889  ARG  CZ ', ' A 916  TRP  HB2', -0.504, (70.675, 66.601, 118.021)), (' P  11    A  N6 ', ' T  20    U  H3 ', -0.503, (59.35, 90.614, 112.319)), (' A 836  ARG  NH2', ' A 840  ALA  HB2', -0.497, (87.731, 79.314, 113.122)), (' B 135  TYR  CE2', ' B 172  ILE HG22', -0.49, (123.159, 104.578, 125.759)), (' A 366  LEU HD11', ' A 374  TYR  HE2', -0.49, (84.591, 127.209, 111.246)), (' B 135  TYR  HE2', ' B 172  ILE HG22', -0.485, (123.038, 104.726, 126.347)), (' B 135  TYR  HE1', ' B 139  LYS  NZ ', -0.481, (127.073, 104.267, 122.498)), (' C  29  TRP  O  ', ' C  33  VAL HG23', -0.481, (105.523, 88.866, 125.846)), (' A 423  ALA  HA ', ' A 883  LEU HD11', -0.48, (85.712, 65.525, 119.833)), (" P  14    A  H2'", ' P  15    A  C8 ', -0.48, (72.898, 91.383, 117.48)), (' A 201  ILE HG23', ' A 222  PHE  HB3', -0.48, (115.537, 110.692, 59.622)), (' A 720  VAL HG11', ' A 775  LEU  HG ', -0.479, (97.585, 84.393, 69.69)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.475, (87.493, 97.362, 92.369)), (' A 239  SER  OG ', ' A 465  ASP  OD1', -0.475, (103.703, 103.449, 77.461)), (' A 454  ASP  O  ', ' A 457  ARG  HG2', -0.47, (107.817, 98.943, 106.311)), (' A 665  GLU  N  ', ' A 665  GLU  OE1', -0.464, (96.663, 108.946, 103.951)), (' A 476  VAL HG22', ' A 696  ILE HG22', -0.463, (90.905, 94.911, 84.507)), (' A 507  ASN  ND2', ' A 541  GLN  OE1', -0.462, (90.244, 106.509, 117.163)), (' A 386  ASN HD21', ' B 127  LYS  HD2', -0.462, (105.443, 117.846, 124.62)), (' A 413  GLY  HA3', ' A 441  PHE  CD2', -0.462, (93.084, 83.141, 121.704)), (' A 569  ARG  O  ', ' A 573  GLN  HB2', -0.459, (76.795, 105.633, 99.231)), (' A  49  LEU  O  ', ' A  50  LYS  HD2', -0.459, (117.979, 88.29, 64.139)), (' A 618  ASP  HA ', ' A1102  HOH  O  ', -0.459, (96.877, 86.432, 95.904)), (' A 366  LEU HD11', ' A 374  TYR  CE2', -0.457, (84.916, 126.786, 111.098)), (' A 329  LEU  HB3', ' B 114  CYS  SG ', -0.456, (98.438, 126.271, 101.876)), (' C  13  LEU  HA ', ' C  16  VAL HG12', -0.456, (99.177, 80.015, 132.193)), (' A 388  LEU HD23', ' A 397  SER  HB3', -0.454, (106.365, 111.363, 114.201)), (' A 153  ASP  N  ', ' A 153  ASP  OD1', -0.452, (129.124, 92.483, 93.183)), (' C   6  VAL HG11', ' C  48  ALA  HB1', -0.45, (105.468, 71.972, 123.582)), (' P  10    G  H1 ', ' T  21    C  N4 ', -0.448, (55.742, 90.073, 112.048)), (' A 658  GLU  O  ', ' A 662  VAL HG22', -0.448, (91.224, 108.057, 99.667)), (' A 885  LEU HD11', ' A 921  TYR  CE2', -0.444, (74.843, 69.617, 112.368)), (' A  41  LYS  HB3', ' A  41  LYS  HE3', -0.441, (105.081, 89.836, 57.649)), (' A 136  GLU  N  ', ' A 136  GLU  OE2', -0.44, (113.036, 83.811, 88.022)), (' C  23  GLU  HA ', ' C  29  TRP  HB2', -0.439, (103.984, 91.869, 129.76)), (' A 885  LEU  O  ', ' A 889  ARG  HG2', -0.439, (75.126, 66.036, 118.612)), (' A 855  MET  HE3', ' A 891  LEU HD21', -0.437, (78.275, 74.878, 124.328)), (' A 333  ILE HG22', ' A 340  PHE  HB2', -0.437, (90.657, 129.294, 112.307)), (' A 633  MET  O  ', ' A 637  VAL HG23', -0.435, (90.056, 103.399, 87.303)), (' C  36  HIS  NE2', ' C  40  LEU HD11', -0.432, (100.0, 81.07, 121.576)), (' A 684  ASP  OD1', ' A 685  ALA  N  ', -0.43, (86.357, 103.428, 101.458)), (' A 420  TYR  O  ', ' A 424  VAL HG23', -0.428, (90.467, 66.752, 123.463)), (' A 144  GLU  O  ', ' A 148  THR  OG1', -0.423, (128.17, 93.231, 82.865)), (' A 378  PRO  HD2', ' A 537  PRO  HG2', -0.422, (92.83, 118.132, 107.106)), (' B  90  MET  HB3', ' B  90  MET  HE2', -0.421, (87.107, 119.594, 120.08)), (' A 696  ILE  O  ', ' A 700  VAL HG23', -0.42, (92.512, 93.07, 83.779)), (' B 141  THR HG22', ' B 142  CYS  SG ', -0.413, (118.676, 111.682, 119.483)), (' A  86  ILE HG22', ' A 224  GLN  NE2', -0.413, (119.095, 111.984, 54.169)), (' A 444  GLN  HB3', ' A 448  ALA  HB2', -0.413, (102.472, 92.897, 118.597)), (' A 480  PHE  CZ ', ' A 693  VAL HG22', -0.412, (86.65, 97.561, 89.263)), (' A 413  GLY  HA3', ' A 441  PHE  HD2', -0.412, (92.912, 82.821, 121.776)), (' A 139  CYS  SG ', ' A 143  LYS  HE3', -0.407, (119.813, 86.096, 87.531)), (' A 566  MET  HB2', ' A 566  MET  HE3', -0.405, (78.826, 110.527, 108.04)), (' A 376  ALA  HB1', ' A 538  THR HG22', -0.403, (88.171, 114.948, 108.906)), (' A1003  POP  O3 ', ' A1003  POP  O6 ', -0.403, (98.101, 90.663, 104.478)), (' A 854  LEU  HA ', ' A 854  LEU HD23', -0.403, (75.038, 82.606, 121.853)), (' A 707  LEU  O  ', ' A 710  THR HG22', -0.402, (102.573, 88.633, 71.564)), (' C  36  HIS  HE2', ' C  40  LEU HD11', -0.4, (99.945, 81.413, 120.901)), (' C  14  LEU HD22', ' C  36  HIS  ND1', -0.4, (101.469, 83.243, 124.847))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (89.03799999999995, 112.62199999999997, 115.596)), ('A', ' 607 ', 'SER', None, (83.15, 79.049, 81.895)), ('B', ' 183 ', 'PRO', None, (111.87800000000003, 100.49799999999999, 123.702))]
data['cablam'] = [('A', '45', 'PHE', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (108.6, 94.2, 71.9)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (104.3, 125.2, 94.9)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (107.2, 123.8, 92.8)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (89.7, 110.2, 115.5)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nTTT-S', (83.2, 78.0, 77.6)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (103.3, 106.6, 102.0)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (126.5, 97.9, 90.2)), ('A', '607', 'SER', 'check CA trace', 'turn\nHTTT-', (82.0, 79.3, 81.0)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (100.5, 105.0, 100.1)), ('B', '98', 'LEU', 'check CA trace', 'turn\nGTTT-', (98.6, 128.2, 119.1))]
data['smoc'] = [('A', 33, u'ARG', 0.541822270531087, (118.283, 90.538, 71.538)), ('A', 93, u'CYS', 0.31658849551493906, (125.73700000000001, 115.72, 67.474)), ('A', 95, u'ALA', 0.419193721989676, (124.972, 111.753, 71.077)), ('A', 125, u'ALA', 0.46221472500250654, (116.262, 97.62299999999999, 75.073)), ('A', 129, u'TYR', 0.4839968301557163, (113.335, 93.837, 78.53)), ('A', 146, u'LEU', 0.584985406767071, (124.809, 94.526, 86.74100000000001)), ('A', 157, u'PHE', 0.6288246790603145, (123.983, 86.51400000000001, 93.34400000000001)), ('A', 161, u'ASP', 0.4844042025270493, (116.722, 85.736, 97.02499999999999)), ('A', 171, u'ILE', 0.44069913546857803, (118.583, 95.19, 95.84100000000001)), ('A', 196, u'MET', 0.5697699159353437, (116.96900000000001, 115.73, 64.24400000000001)), ('A', 197, u'ARG', 0.598012571348457, (114.70100000000001, 118.781, 64.51700000000001)), ('A', 208, u'ASP', 0.5169023528939066, (117.296, 99.04700000000001, 70.699)), ('A', 219, u'PHE', 0.6243353167440915, (119.357, 105.96100000000001, 61.083)), ('A', 233, u'VAL', 0.5449841570066946, (108.367, 110.362, 67.346)), ('A', 250, u'ALA', 0.4865871855451196, (117.306, 108.12899999999999, 87.57199999999999)), ('A', 270, u'LEU', 0.5589732202313504, (110.70400000000001, 125.11, 104.258)), ('A', 312, u'ASN', 0.40488345315875474, (102.151, 109.755, 86.166)), ('A', 330, u'VAL', 0.5300316938658836, (97.296, 125.726, 106.25)), ('A', 366, u'LEU', 0.45599837967689794, (80.762, 128.38600000000002, 113.64999999999999)), ('A', 369, u'LYS', 0.5420863023257518, (79.082, 121.542, 109.758)), ('A', 376, u'ALA', 0.43347949544534675, (88.331, 116.368, 111.27)), ('A', 377, u'ASP', 0.4794482667736748, (91.04400000000001, 118.66199999999999, 109.892)), ('A', 382, u'ALA', 0.3921266666542006, (99.351, 118.807, 114.22)), ('A', 385, u'GLY', 0.5157604166468124, (101.32799999999999, 118.80799999999999, 119.127)), ('A', 393, u'THR', 0.5670694488843963, (110.12199999999999, 103.468, 111.76700000000001)), ('A', 405, u'VAL', 0.6353923306650566, (103.953, 106.91600000000001, 123.691)), ('A', 431, u'GLU', 0.777844637134308, (99.82499999999999, 61.004, 116.86)), ('A', 442, u'PHE', 0.49849257869428476, (99.24600000000001, 84.66999999999999, 118.641)), ('A', 443, u'ALA', 0.4403135383405702, (100.229, 87.17399999999999, 121.32)), ('A', 448, u'ALA', 0.5748338446752884, (103.455, 95.276, 117.43)), ('A', 452, u'ASP', 0.5473844125228151, (103.276, 96.45400000000001, 111.536)), ('A', 506, u'PHE', 0.45119472007114764, (85.15899999999999, 111.79700000000001, 116.763)), ('A', 507, u'ASN', 0.47697056773028823, (85.609, 108.51100000000001, 118.64)), ('A', 512, u'ALA', 0.49201963274077776, (78.62799999999999, 106.756, 114.24000000000001)), ('A', 515, u'TYR', 0.5427152545404712, (76.742, 111.816, 114.21300000000001)), ('A', 524, u'GLN', 0.5202877075206812, (74.52799999999999, 115.864, 105.428)), ('A', 525, u'ASP', 0.5312103473339854, (73.691, 117.09400000000001, 101.923)), ('A', 528, u'PHE', 0.45242053908322793, (78.51, 116.35499999999999, 100.695)), ('A', 540, u'THR', 0.4571778592309935, (92.96300000000001, 107.592, 110.104)), ('A', 555, u'ARG', 0.44774231784904306, (97.144, 92.435, 111.889)), ('A', 560, u'VAL', 0.4631466331169644, (88.566, 106.17399999999999, 109.01700000000001)), ('A', 590, u'GLY', 0.5419075012690577, (77.962, 89.57499999999999, 97.346)), ('A', 593, u'LYS', 0.5464531901711938, (78.321, 80.148, 98.527)), ('A', 602, u'LEU', 0.4868854164203961, (82.4, 77.548, 89.198)), ('A', 625, u'ALA', 0.4616313158961567, (102.899, 97.56700000000001, 98.17899999999999)), ('A', 633, u'MET', 0.38828723618266725, (93.141, 104.44200000000001, 88.504)), ('A', 634, u'ALA', 0.33146824301242933, (90.74900000000001, 102.32499999999999, 90.574)), ('A', 656, u'ALA', 0.419545233449632, (91.269, 114.833, 95.63199999999999)), ('A', 665, u'GLU', 0.4119756492148771, (96.346, 110.67899999999999, 104.781)), ('A', 699, u'ALA', 0.3830129261162779, (95.456, 90.512, 84.893)), ('A', 727, u'LEU', 0.48201868314480834, (97.024, 95.897, 69.99000000000001)), ('A', 754, u'SER', 0.48883930838256545, (87.718, 84.079, 81.91300000000001)), ('A', 761, u'ASP', 0.37854333476861957, (91.615, 86.566, 95.218)), ('A', 764, u'VAL', 0.4686088326862406, (91.11999999999999, 81.898, 86.01)), ('A', 785, u'VAL', 0.38698170004268795, (104.21400000000001, 92.268, 85.798)), ('A', 811, u'GLU', 0.4953816148275134, (92.26, 77.412, 96.763)), ('A', 815, u'GLN', 0.5117719101325555, (87.94600000000001, 77.026, 100.66)), ('A', 859, u'PHE', 0.5349083727730497, (78.9, 75.614, 117.15799999999999)), ('A', 860, u'VAL', 0.4490112026915079, (75.827, 75.69, 114.9)), ('A', 864, u'ILE', 0.5357445926034875, (77.229, 74.752, 108.94000000000001)), ('A', 878, u'ALA', 0.6244311074644672, (84.646, 63.443, 107.93400000000001)), ('A', 885, u'LEU', 0.5261691837808717, (77.021, 67.49000000000001, 115.97)), ('A', 912, u'THR', 0.5632426378216457, (64.364, 70.842, 108.59400000000001)), ('B', 83, u'VAL', 0.43239403935604864, (78.538, 117.11999999999999, 120.923)), ('B', 90, u'MET', 0.501675576005544, (88.20100000000001, 120.902, 122.265)), ('B', 98, u'LEU', 0.5039362687152457, (98.642, 128.153, 119.09)), ('B', 99, u'ASP', 0.636120111012185, (98.824, 131.86200000000002, 118.21000000000001)), ('B', 114, u'CYS', 0.5188320020512763, (99.839, 129.666, 103.191)), ('B', 117, u'LEU', 0.5514192478117366, (101.343, 121.681, 107.63799999999999)), ('B', 125, u'ALA', 0.5290369053248952, (107.17299999999999, 123.316, 118.533)), ('B', 142, u'CYS', 0.6434054971135363, (121.2, 111.96600000000001, 121.455)), ('B', 172, u'ILE', 0.6538468018043662, (122.529, 104.54700000000001, 129.20999999999998)), ('C', 8, u'CYS', 0.5044743561337006, (97.029, 74.026, 124.815)), ('C', 15, u'SER', 0.5654106400611573, (96.74900000000001, 83.69, 129.803)), ('C', 38, u'ASP', 0.4541680705293884, (107.72, 79.488, 119.489)), ('C', 60, u'LEU', 0.6213519928760227, (107.148, 79.62499999999999, 139.266)), ('T', 13, u'A', 0.5138983307324827, (79.574, 90.412, 101.866))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30210/7bv2/Model_validation_1/validation_cootdata/molprobity_probe7bv2_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

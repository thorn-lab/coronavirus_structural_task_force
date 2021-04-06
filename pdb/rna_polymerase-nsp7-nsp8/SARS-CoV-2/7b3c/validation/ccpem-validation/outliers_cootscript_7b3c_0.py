
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
data['clusters'] = [('A', '598', 1, 'side-chain clash', (83.983, 82.424, 92.997)), ('A', '601', 1, 'side-chain clash', (86.106, 87.802, 93.828)), ('A', '602', 1, 'side-chain clash', (83.983, 82.424, 92.997)), ('A', '605', 1, 'side-chain clash', (87.391, 86.499, 90.144)), ('A', '755', 1, 'Dihedral angle:CA:C', (90.531, 90.62799999999999, 86.884)), ('A', '756', 1, 'side-chain clash\nDihedral angle:N:CA', (89.224, 90.357, 90.41900000000001)), ('A', '764', 1, 'smoc Outlier', (93.745, 87.34700000000001, 87.01100000000001)), ('A', '819', 1, 'side-chain clash', (85.164, 74.185, 90.417)), ('A', '820', 1, 'side-chain clash', (81.365, 73.116, 97.033)), ('A', '827', 1, 'side-chain clash', (80.57, 74.457, 95.746)), ('A', '828', 1, 'side-chain clash', (82.216, 76.429, 95.841)), ('A', '829', 1, 'side-chain clash', (82.216, 76.429, 95.841)), ('A', '480', 2, 'side-chain clash', (89.076, 102.414, 90.852)), ('A', '630', 2, 'smoc Outlier', (99.51100000000001, 107.049, 92.12599999999999)), ('A', '634', 2, 'smoc Outlier', (93.392, 107.384, 92.41100000000002)), ('A', '687', 2, 'side-chain clash', (93.641, 101.294, 99.884)), ('A', '691', 2, 'side-chain clash', (93.641, 101.294, 99.884)), ('A', '692', 2, 'smoc Outlier', (91.735, 98.971, 94.073)), ('A', '693', 2, 'side-chain clash', (89.076, 102.414, 90.852)), ('A', '695', 2, 'backbone clash', (95.964, 94.056, 94.261)), ('A', '759', 2, 'smoc Outlier', (92.166, 96.633, 97.689)), ('A', '760', 2, 'backbone clash\ncablam Outlier', (95.964, 94.056, 94.261)), ('A', '531', 3, 'side-chain clash', (85.901, 119.435, 104.984)), ('A', '564', 3, 'side-chain clash', (87.751, 113.295, 104.865)), ('A', '567', 3, 'side-chain clash\nsmoc Outlier', (85.901, 119.435, 104.984)), ('A', '568', 3, 'side-chain clash', (87.751, 113.295, 104.865)), ('A', '631', 3, 'side-chain clash', (92.081, 108.63, 100.398)), ('A', '658', 3, 'smoc Outlier', (92.798, 114.965, 100.712)), ('A', '684', 3, 'side-chain clash\nbackbone clash', (89.249, 107.602, 102.787)), ('A', '685', 3, 'backbone clash', (89.249, 107.602, 102.787)), ('A', '367', 4, 'side-chain clash', (83.209, 131.014, 116.35)), ('A', '368', 4, 'side-chain clash', (81.494, 121.592, 115.835)), ('A', '370', 4, 'side-chain clash', (83.209, 131.014, 116.35)), ('A', '371', 4, 'smoc Outlier', (86.262, 125.70400000000001, 116.883)), ('A', '372', 4, 'side-chain clash', (81.494, 121.592, 115.835)), ('A', '504', 4, 'side-chain clash\ncablam Outlier', (81.132, 124.016, 119.881)), ('A', '668', 4, 'side-chain clash', (81.132, 124.016, 119.881)), ('A', '239', 5, 'smoc Outlier', (108.697, 110.425, 79.157)), ('A', '242', 5, 'side-chain clash', (109.049, 112.919, 83.841)), ('A', '312', 5, 'smoc Outlier', (104.63, 114.835, 88.39)), ('A', '318', 5, 'backbone clash', (107.261, 119.453, 95.281)), ('A', '349', 5, 'backbone clash', (107.261, 119.453, 95.281)), ('A', '350', 5, 'smoc Outlier', (103.43400000000001, 118.154, 94.408)), ('A', '463', 5, 'side-chain clash', (109.049, 112.919, 83.841)), ('A', '665', 6, 'side-chain clash\nsmoc Outlier', (99.732, 113.026, 105.864)), ('A', '676', 6, 'side-chain clash', (97.889, 108.318, 105.78)), ('A', '677', 6, 'cablam Outlier', (106.8, 111.2, 103.9)), ('A', '678', 6, 'cablam CA Geom Outlier', (103.9, 110.1, 101.9)), ('A', '679', 6, 'smoc Outlier', (101.768, 107.05499999999999, 101.027)), ('A', '681', 6, 'side-chain clash', (97.889, 108.318, 105.78)), ('A', '143', 7, 'side-chain clash', (128.146, 96.295, 87.251)), ('A', '144', 7, 'side-chain clash\nsmoc Outlier', (129.944, 98.449, 83.159)), ('A', '147', 7, 'side-chain clash', (128.146, 96.295, 87.251)), ('A', '148', 7, 'side-chain clash', (129.944, 98.449, 83.159)), ('A', '151', 7, 'cablam Outlier', (128.8, 102.8, 91.1)), ('A', '152', 7, 'smoc Outlier', (129.575, 99.44200000000001, 92.87799999999999)), ('A', '867', 8, 'side-chain clash', (82.637, 71.352, 104.947)), ('A', '870', 8, 'side-chain clash', (82.637, 71.352, 104.947)), ('A', '876', 8, 'side-chain clash', (90.435, 69.291, 110.25)), ('A', '878', 8, 'side-chain clash\nsmoc Outlier', (84.884, 66.417, 108.287)), ('A', '880', 8, 'side-chain clash', (90.435, 69.291, 110.25)), ('A', '882', 8, 'side-chain clash', (84.884, 66.417, 108.287)), ('A', '388', 9, 'side-chain clash', (108.654, 115.985, 121.205)), ('A', '400', 9, 'side-chain clash', (108.654, 115.985, 121.205)), ('A', '401', 9, 'side-chain clash', (100.293, 115.763, 119.682)), ('A', '672', 9, 'smoc Outlier', (105.24000000000001, 113.527, 119.387)), ('A', '673', 9, 'smoc Outlier', (104.423, 115.053, 116.003)), ('A', '185', 10, 'smoc Outlier', (123.07799999999999, 113.982, 79.909)), ('A', '189', 10, 'smoc Outlier', (120.232, 117.13499999999999, 75.52499999999999)), ('A', '211', 10, 'backbone clash\nsmoc Outlier', (126.609, 111.316, 74.499)), ('A', '215', 10, 'backbone clash', (126.609, 111.316, 74.499)), ('A', '503', 11, 'backbone clash', (89.814, 112.816, 119.276)), ('A', '506', 11, 'smoc Outlier', (89.037, 115.161, 119.303)), ('A', '507', 11, 'backbone clash\nside-chain clash\nsmoc Outlier', (94.247, 110.561, 119.503)), ('A', '541', 11, 'side-chain clash', (94.247, 110.561, 119.503)), ('A', '836', 12, 'Dihedral angle:CD:NE:CZ:NH1', (93.91400000000002, 80.34400000000001, 111.53)), ('A', '837', 12, 'smoc Outlier', (90.537, 79.024, 112.693)), ('A', '840', 12, 'smoc Outlier', (91.06, 82.024, 116.748)), ('A', '841', 12, 'smoc Outlier', (89.324, 79.339, 118.79100000000001)), ('A', '845', 13, 'side-chain clash\nbackbone clash', (90.196, 90.107, 123.927)), ('A', '846', 13, 'backbone clash', (90.196, 90.107, 123.927)), ('A', '847', 13, 'backbone clash', (89.318, 89.501, 127.854)), ('A', '849', 13, 'side-chain clash', (88.347, 89.501, 120.441)), ('A', '487', 14, 'side-chain clash', (80.543, 115.956, 95.089)), ('A', '642', 14, 'side-chain clash', (80.543, 115.956, 95.089)), ('A', '646', 14, 'smoc Outlier', (81.65199999999999, 120.409, 91.596)), ('A', '452', 15, 'side-chain clash\nDihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (106.87199999999999, 100.577, 112.508)), ('A', '556', 15, 'side-chain clash', (102.557, 99.803, 112.028)), ('A', '557', 15, 'smoc Outlier', (96.056, 101.642, 112.46000000000001)), ('A', '39', 16, 'smoc Outlier', (107.813, 103.393, 61.641)), ('A', '40', 16, 'backbone clash', (106.021, 100.322, 58.334)), ('A', '41', 16, 'backbone clash', (106.021, 100.322, 58.334)), ('A', '167', 17, 'Dihedral angle:CB:CG:CD:OE1', (116.392, 94.049, 102.18599999999999)), ('A', '168', 17, 'smoc Outlier', (119.336, 96.16499999999999, 100.952)), ('A', '171', 17, 'smoc Outlier', (121.356, 99.98100000000001, 96.663)), ('A', '200', 18, 'backbone clash\nsmoc Outlier', (114.961, 122.727, 58.795)), ('A', '223', 18, 'side-chain clash', (113.467, 119.072, 59.091)), ('A', '225', 18, 'backbone clash', (114.961, 122.727, 58.795)), ('A', '470', 19, 'side-chain clash', (95.7, 108.619, 82.413)), ('A', '472', 19, 'smoc Outlier', (96.751, 104.30199999999999, 82.092)), ('A', '473', 19, 'side-chain clash', (95.7, 108.619, 82.413)), ('A', '499', 20, 'side-chain clash', (99.657, 135.284, 104.631)), ('A', '513', 20, 'side-chain clash\nsmoc Outlier', (99.657, 135.284, 104.631)), ('A', '260', 21, 'side-chain clash', (130.005, 123.626, 93.708)), ('A', '263', 21, 'side-chain clash\nsmoc Outlier', (130.005, 123.626, 93.708)), ('A', '128', 22, 'side-chain clash', (116.481, 106.127, 78.707)), ('A', '207', 22, 'side-chain clash', (116.481, 106.127, 78.707)), ('A', '416', 23, 'smoc Outlier', (91.393, 79.38799999999999, 126.36)), ('A', '418', 23, 'Dihedral angle:CA:CB:CG:OD1', (88.95400000000001, 74.63799999999999, 127.881)), ('A', '358', 24, 'Dihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (88.263, 132.69899999999998, 103.10799999999999)), ('A', '534', 24, 'smoc Outlier', (89.96300000000001, 126.235, 101.978)), ('A', '369', 25, 'side-chain clash', (86.294, 126.093, 109.47)), ('A', '373', 25, 'side-chain clash', (86.294, 126.093, 109.47)), ('A', '911', 26, 'backbone clash\nside-chain clash', (81.908, 116.8, 123.316)), ('A', '914', 26, 'side-chain clash', (81.908, 116.8, 123.316)), ('A', '483', 27, 'side-chain clash', (80.522, 98.492, 90.306)), ('A', '582', 27, 'side-chain clash', (80.522, 98.492, 90.306)), ('A', '304', 28, 'side-chain clash', (88.563, 115.892, 87.379)), ('A', '651', 28, 'side-chain clash', (88.563, 115.892, 87.379)), ('A', '245', 29, 'smoc Outlier', (115.77799999999999, 110.853, 87.319)), ('A', '248', 29, 'smoc Outlier', (119.096, 107.912, 90.43400000000001)), ('A', '38', 30, 'side-chain clash', (101.897, 106.408, 65.517)), ('A', '729', 30, 'side-chain clash', (101.897, 106.408, 65.517)), ('A', '785', 31, 'smoc Outlier', (106.483, 97.613, 87.05199999999999)), ('A', '788', 31, 'smoc Outlier', (110.48400000000001, 101.086, 88.516)), ('A', '431', 32, 'backbone clash', (104.568, 65.283, 114.779)), ('A', '432', 32, 'backbone clash', (104.568, 65.283, 114.779)), ('A', '333', 33, 'smoc Outlier', (95.67399999999999, 136.864, 113.74000000000001)), ('A', '340', 33, 'smoc Outlier', (95.706, 133.055, 117.5)), ('A', '607', 34, 'cablam CA Geom Outlier', (84.1, 84.8, 81.1)), ('A', '608', 34, 'cablam Outlier', (85.4, 83.9, 77.6)), ('A', '484', 35, 'backbone clash\nDihedral angle:CA:CB:CG:OD1\nsmoc Outlier', (77.571, 106.758, 89.792)), ('A', '485', 35, 'backbone clash', (77.132, 108.901, 90.577)), ('B', '132', 1, 'side-chain clash', (123.005, 108.803, 123.425)), ('B', '137', 1, 'smoc Outlier', (124.006, 108.21700000000001, 119.093)), ('B', '138', 1, 'side-chain clash', (123.005, 108.803, 123.425)), ('B', '141', 1, 'backbone clash', (123.821, 114.197, 120.823)), ('B', '142', 1, 'backbone clash', (123.821, 114.197, 120.823)), ('B', '158', 1, 'smoc Outlier', (117.60499999999999, 116.40700000000001, 132.71899999999997)), ('B', '159', 1, 'side-chain clash', (119.666, 112.132, 128.63)), ('B', '182', 1, 'cablam CA Geom Outlier', (117.4, 102.9, 126.6)), ('B', '184', 1, 'smoc Outlier', (117.161, 108.01400000000001, 126.96300000000001)), ('B', '186', 1, 'side-chain clash', (119.666, 112.132, 128.63)), ('B', '187', 1, 'smoc Outlier', (115.557, 117.66199999999999, 128.236)), ('B', '83', 2, 'side-chain clash', (83.693, 121.808, 120.836)), ('B', '84', 2, 'side-chain clash', (81.132, 124.016, 119.881)), ('B', '87', 2, 'side-chain clash', (83.693, 121.808, 120.836)), ('B', '171', 3, 'smoc Outlier', (126.124, 107.16199999999999, 134.785)), ('B', '172', 3, 'cablam Outlier', (126.0, 107.5, 131.0)), ('B', '103', 4, 'side-chain clash', (105.844, 135.905, 114.257)), ('B', '107', 4, 'side-chain clash', (105.844, 135.905, 114.257)), ('C', '38', 1, 'side-chain clash', (115.072, 81.726, 120.754)), ('C', '46', 1, 'smoc Outlier', (114.65499999999999, 71.871, 122.691)), ('C', '47', 1, 'Dihedral angle:CB:CG:CD:OE1', (115.037, 75.60799999999999, 122.07199999999999)), ('C', '51', 1, 'side-chain clash', (115.072, 81.726, 120.754)), ('C', '3', 2, 'side-chain clash', (104.136, 74.628, 121.27)), ('C', '5', 2, 'backbone clash\nsmoc Outlier', (103.761, 72.48, 125.296)), ('C', '6', 2, 'side-chain clash\nbackbone clash', (103.761, 72.48, 125.296)), ('C', '7', 2, 'side-chain clash', (104.136, 74.628, 121.27)), ('C', '14', 3, 'side-chain clash', (105.514, 86.41, 125.029)), ('C', '36', 3, 'side-chain clash', (106.434, 83.649, 122.089)), ('C', '40', 3, 'side-chain clash', (101.476, 83.112, 119.089)), ('C', '20', 4, 'backbone clash', (104.777, 91.977, 138.449)), ('C', '52', 4, 'smoc Outlier', (110.36999999999999, 78.537, 128.476)), ('P', '14', 1, 'Backbone torsion suites: ', (91.708, 94.3, 102.85799999999999)), ('P', '15', 1, 'side-chain clash', (91.867, 101.758, 107.341)), ('T', '19', 1, 'Backbone torsion suites: ', (61.612, 97.644, 118.838))]
data['probe'] = [(' B  83  VAL HG12', ' B  87  MET  HE2', -0.8, (83.934, 121.697, 120.831)), (' A 682  SER  O  ', ' P  15    G  N2 ', -0.725, (91.867, 101.758, 107.341)), (' A 676  LYS  NZ ', ' A 681  SER  OG ', -0.724, (97.889, 108.318, 105.78)), (' A 631  ARG  NH2', ' A 684  ASP  OD2', -0.713, (92.081, 108.63, 100.398)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.707, (89.814, 112.816, 119.276)), (' A 684  ASP  OD1', ' A 685  ALA  N  ', -0.676, (89.249, 107.602, 102.787)), (' A 368  PHE  O  ', ' A 372  LEU HD12', -0.676, (83.261, 123.677, 115.32)), (' B  77  GLU  N  ', ' B  77  GLU  OE1', -0.675, (71.877, 119.115, 122.727)), (' A 368  PHE  CE2', ' A 372  LEU HD11', -0.667, (81.484, 121.186, 116.067)), (' A 388  LEU HD12', ' A 400  ALA  HB2', -0.639, (108.654, 115.985, 121.205)), (' A 242  MET  SD ', ' A 463  MET  HE2', -0.625, (109.049, 112.919, 83.841)), (' A 452  ASP  OD1', ' A 556  THR HG23', -0.625, (102.557, 99.803, 112.028)), (' A 820  VAL HG22', ' A 829  LEU HD13', -0.622, (81.519, 73.758, 96.812)), (' A 846  ASP  OD1', ' A 847  ILE  N  ', -0.595, (89.318, 89.501, 127.854)), (' A 878  ALA  O  ', ' A 882  HIS  ND1', -0.58, (85.142, 67.011, 110.485)), (' A 876  GLU  O  ', ' A 880  VAL HG23', -0.577, (90.435, 69.291, 110.25)), (' A 431  GLU  OE2', ' A 432  GLY  N  ', -0.576, (104.568, 65.283, 114.779)), (' A 128  VAL HG21', ' A 207  LEU  CD2', -0.573, (116.051, 105.884, 78.591)), (' A 318  SER  OG ', ' A 349  ARG  O  ', -0.573, (107.261, 119.453, 95.281)), (' A 144  GLU  O  ', ' A 148  THR HG23', -0.564, (129.944, 98.449, 83.159)), (' A 483  TYR  HE1', ' A 582  THR HG21', -0.561, (80.522, 98.492, 90.306)), (' A 910  ASP  OD1', ' A 911  ASN  N  ', -0.554, (64.75, 75.303, 120.037)), (' C  38  ASP  OD2', ' C  51  LYS  NZ ', -0.554, (115.072, 81.726, 120.754)), (' A 687  THR  O  ', ' A 691  ASN  ND2', -0.551, (93.641, 101.294, 99.884)), (' A 827  VAL HG13', ' A 829  LEU  CD1', -0.531, (80.57, 74.457, 95.746)), (' A 368  PHE  CD2', ' A 372  LEU HD11', -0.53, (81.494, 121.592, 115.835)), (' A 507  ASN  ND2', ' A 541  GLN  OE1', -0.519, (94.247, 110.561, 119.503)), (' A 531  THR HG21', ' A 567  THR HG21', -0.519, (85.901, 119.435, 104.984)), (' A 845  ASP  OD2', ' A 849  LYS  NZ ', -0.515, (88.347, 89.501, 120.441)), (' A 304  ASP  OD2', ' A 651  ARG  NH2', -0.514, (88.563, 115.892, 87.379)), (' B 159  VAL HG13', ' B 186  VAL HG22', -0.504, (119.666, 112.132, 128.63)), (' A 211  ASP  OD1', ' A 215  ASN  N  ', -0.503, (126.609, 111.316, 74.499)), (' A 564  SER  O  ', ' A 568  ASN  ND2', -0.501, (87.751, 113.295, 104.865)), (' A 487  CYS  SG ', ' A 642  HIS  CE1', -0.493, (80.543, 115.956, 95.089)), (' A 499  ASP  OD1', ' A 513  ARG  NH1', -0.482, (78.629, 104.725, 120.649)), (' A 331  ARG  NH2', ' B 114  CYS  SG ', -0.481, (99.657, 135.284, 104.631)), (' A 267  LYS  HA ', ' A 267  LYS  HE2', -0.479, (121.234, 126.309, 104.372)), (' C   3  MET  O  ', ' C   6  VAL HG12', -0.474, (105.341, 73.609, 122.54)), (' A 665  GLU  N  ', ' A 665  GLU  OE1', -0.466, (99.732, 113.026, 105.864)), (' B 141  THR  OG1', ' B 142  CYS  N  ', -0.465, (123.821, 114.197, 120.823)), (' C  14  LEU HD22', ' C  36  HIS  CG ', -0.461, (105.514, 86.41, 125.029)), (' A 601  MET  HE3', ' A 756  MET  HE3', -0.46, (86.106, 87.802, 93.828)), (' A 401  LEU HD12', ' A 668  MET  HE2', -0.456, (100.293, 115.763, 119.682)), (' A 845  ASP  OD1', ' A 846  ASP  N  ', -0.455, (90.196, 90.107, 123.927)), (' C   3  MET  O  ', ' C   7  LYS  HG3', -0.454, (104.136, 74.628, 121.27)), (' A 820  VAL  CG2', ' A 829  LEU HD13', -0.454, (81.365, 73.116, 97.033)), (' C   5  ASP  OD1', ' C   6  VAL  N  ', -0.454, (103.761, 72.48, 125.296)), (' A 867  TYR  O  ', ' A 870  THR HG22', -0.454, (82.637, 71.352, 104.947)), (' C  36  HIS  O  ', ' C  40  LEU HD13', -0.442, (106.434, 83.649, 122.089)), (' A 695  ASN  ND2', ' A 760  ASP  O  ', -0.435, (95.964, 94.056, 94.261)), (' A  40  ASP  OD1', ' A  41  LYS  N  ', -0.435, (106.021, 100.322, 58.334)), (' A 911  ASN  OD1', ' A 914  ARG  NH2', -0.433, (67.551, 78.664, 115.803)), (' A 514  LEU HD21', ' B  83  VAL  CG2', -0.433, (81.908, 116.8, 123.316)), (' C  20  LEU  HG ', ' C  20  LEU  O  ', -0.432, (104.777, 91.977, 138.449)), (' A 819  LEU HD13', ' A 828  TYR  CE1', -0.432, (85.164, 74.185, 90.417)), (' A 598  TRP  O  ', ' A 602  LEU HD23', -0.43, (83.983, 82.424, 92.997)), (' A 260  ASP  HB3', ' A 263  LYS  HZ2', -0.429, (130.005, 123.626, 93.708)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.429, (123.005, 108.803, 123.425)), (' A 796  GLU  N  ', ' A 796  GLU  OE1', -0.429, (109.625, 86.57, 92.744)), (' B  83  VAL HG12', ' B  87  MET  CE ', -0.428, (83.693, 121.808, 120.836)), (' A 440  PHE  CB ', ' C  40  LEU HD23', -0.424, (101.476, 83.112, 119.089)), (' A 367  SER  N  ', ' A 370  GLU  OE2', -0.424, (83.209, 131.014, 116.35)), (' A 504  PHE  CE1', ' A 668  MET  HE1', -0.423, (97.91, 115.717, 120.057)), (' A 368  PHE  HD1', ' B  84  THR HG22', -0.422, (81.132, 124.016, 119.881)), (' A 828  TYR  C  ', ' A 829  LEU HD12', -0.421, (82.216, 76.429, 95.841)), (' A 200  GLY  O  ', ' A 225  THR  N  ', -0.419, (114.961, 122.727, 58.795)), (' B 103  LEU  O  ', ' B 107  ILE HG12', -0.417, (105.844, 135.905, 114.257)), (' B 101  ASP  N  ', ' B 101  ASP  OD1', -0.415, (108.374, 135.679, 122.707)), (' A 605  VAL HG21', ' A 756  MET  SD ', -0.415, (87.391, 86.499, 90.144)), (' A 369  LYS  HZ3', ' A 373  VAL HG21', -0.415, (86.294, 126.093, 109.47)), (' A 480  PHE  CZ ', ' A 693  VAL HG22', -0.413, (89.076, 102.414, 90.852)), (' A 470  LEU  O  ', ' A 473  VAL HG12', -0.412, (95.7, 108.619, 82.413)), (' A 223  ILE  O  ', ' A 223  ILE HG13', -0.411, (113.467, 119.072, 59.091)), (' A 143  LYS  O  ', ' A 147  VAL HG23', -0.408, (128.146, 96.295, 87.251)), (' B 123  THR  O  ', ' B 123  THR HG22', -0.408, (113.493, 131.294, 116.703)), (' A 128  VAL HG21', ' A 207  LEU HD23', -0.406, (116.481, 106.127, 78.707)), (' A 484  ASP  OD2', ' A 485  GLY  N  ', -0.405, (77.132, 108.901, 90.577)), (' A 878  ALA  HB1', ' A 882  HIS  HE1', -0.402, (84.884, 66.417, 108.287)), (' A  38  TYR  OH ', ' A 729  GLU  HG2', -0.401, (101.897, 106.408, 65.517))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (92.81600000000006, 116.51899999999998, 118.493)), ('B', ' 183 ', 'PRO', None, (115.54700000000003, 103.691, 125.24800000000002))]
data['cablam'] = [('A', '151', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSS-', (128.8, 102.8, 91.1)), ('A', '326', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nGGSEE', (107.0, 122.1, 103.0)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTH', (93.4, 114.1, 118.2)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTSS-S', (85.4, 83.9, 77.6)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--SS', (106.8, 111.2, 103.9)), ('A', '732', 'TYR', ' alpha helix', 'helix\nHHHT-', (104.2, 109.1, 72.8)), ('A', '760', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (95.6, 95.1, 96.8)), ('A', '607', 'SER', 'check CA trace', 'bend\nHTSS-', (84.1, 84.8, 81.1)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--SS-', (103.9, 110.1, 101.9)), ('B', '172', 'ILE', 'check CA trace,carbonyls, peptide', ' \nTT-ST', (126.0, 107.5, 131.0)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (117.4, 102.9, 126.6))]
data['smoc'] = [('A', 39, u'ASN', 0.6544640400334963, (107.813, 103.393, 61.641)), ('A', 46, u'ALA', 0.5383816025845584, (111.98400000000001, 96.82799999999999, 73.103)), ('A', 121, u'LYS', 0.5408862121438295, (129.26299999999998, 100.49700000000001, 74.20400000000001)), ('A', 144, u'GLU', 0.5913076926789526, (127.84, 95.977, 83.909)), ('A', 152, u'CYS', 0.6588353525559907, (129.575, 99.44200000000001, 92.87799999999999)), ('A', 168, u'ASN', 0.6007281854677391, (119.336, 96.16499999999999, 100.952)), ('A', 171, u'ILE', 0.6524287433469543, (121.356, 99.98100000000001, 96.663)), ('A', 185, u'ALA', 0.4955981822055373, (123.07799999999999, 113.982, 79.909)), ('A', 189, u'THR', 0.5288353536255871, (120.232, 117.13499999999999, 75.52499999999999)), ('A', 200, u'GLY', 0.5869447055549376, (116.339, 124.74300000000001, 61.392)), ('A', 211, u'ASP', 0.5261946863793756, (125.569, 107.52199999999999, 74.771)), ('A', 219, u'PHE', 0.5636421622477306, (121.286, 112.932, 62.672000000000004)), ('A', 239, u'SER', 0.5607378420451814, (108.697, 110.425, 79.157)), ('A', 245, u'LEU', 0.5376886014007306, (115.77799999999999, 110.853, 87.319)), ('A', 248, u'THR', 0.5602279306013006, (119.096, 107.912, 90.43400000000001)), ('A', 254, u'GLU', 0.722963939254702, (120.94000000000001, 121.329, 92.571)), ('A', 263, u'LYS', 0.7326312832574076, (130.88200000000003, 122.76, 97.489)), ('A', 312, u'ASN', 0.4819255296399355, (104.63, 114.835, 88.39)), ('A', 329, u'LEU', 0.6122344426375572, (101.45400000000001, 127.694, 106.353)), ('A', 333, u'ILE', 0.6786473324090132, (95.67399999999999, 136.864, 113.74000000000001)), ('A', 336, u'ASP', 0.6222764937175422, (88.363, 138.632, 120.202)), ('A', 340, u'PHE', 0.6554096902969534, (95.706, 133.055, 117.5)), ('A', 350, u'GLU', 0.5572512275778795, (103.43400000000001, 118.154, 94.408)), ('A', 358, u'ASP', 0.6430521487781012, (88.263, 132.69899999999998, 103.10799999999999)), ('A', 371, u'LEU', 0.6085477687679088, (86.262, 125.70400000000001, 116.883)), ('A', 377, u'ASP', 0.6414800804339161, (94.698, 122.588, 112.79700000000001)), ('A', 385, u'GLY', 0.4900908558628817, (104.86, 122.13199999999999, 121.63799999999999)), ('A', 395, u'CYS', 0.6593022376945891, (111.68199999999999, 110.98400000000001, 109.252)), ('A', 416, u'ASN', 0.5471708230095121, (91.393, 79.38799999999999, 126.36)), ('A', 426, u'LYS', 0.6485985685348735, (89.67299999999999, 64.479, 120.723)), ('A', 445, u'ASP', 0.5807337712888352, (107.94000000000001, 96.12499999999999, 123.49900000000001)), ('A', 452, u'ASP', 0.7009124358678835, (106.87199999999999, 100.577, 112.508)), ('A', 472, u'VAL', 0.6091057450857551, (96.751, 104.30199999999999, 82.092)), ('A', 484, u'ASP', 0.6746415284843379, (77.571, 106.758, 89.792)), ('A', 490, u'ALA', 0.67627546782139, (74.71300000000001, 115.609, 105.634)), ('A', 506, u'PHE', 0.5521133052466339, (89.037, 115.161, 119.303)), ('A', 507, u'ASN', 0.5685146594795534, (89.62799999999999, 111.898, 121.191)), ('A', 512, u'ALA', 0.5290521171224842, (81.909, 110.483, 117.096)), ('A', 513, u'ARG', 0.5979988215693501, (78.398, 110.483, 118.588)), ('A', 534, u'ASN', 0.5225037222135605, (89.96300000000001, 126.235, 101.978)), ('A', 546, u'TYR', 0.6157529911349174, (95.599, 93.785, 118.67899999999999)), ('A', 557, u'VAL', 0.6891504611876587, (96.056, 101.642, 112.46000000000001)), ('A', 567, u'THR', 0.6015424158777225, (84.032, 115.753, 104.739)), ('A', 576, u'LEU', 0.6522652156528429, (81.68199999999999, 104.196, 97.55)), ('A', 611, u'ASN', 0.658311436975231, (93.422, 79.65599999999999, 76.96100000000001)), ('A', 622, u'CYS', 0.6666958813812436, (101.736, 98.331, 99.703)), ('A', 630, u'LEU', 0.6406051033595793, (99.51100000000001, 107.049, 92.12599999999999)), ('A', 634, u'ALA', 0.6635968705018855, (93.392, 107.384, 92.41100000000002)), ('A', 646, u'CYS', 0.6144156487574748, (81.65199999999999, 120.409, 91.596)), ('A', 658, u'GLU', 0.46327626086700174, (92.798, 114.965, 100.712)), ('A', 665, u'GLU', 0.5715216072945913, (99.809, 115.042, 107.209)), ('A', 672, u'SER', 0.5928942993023597, (105.24000000000001, 113.527, 119.387)), ('A', 673, u'LEU', 0.590469225292236, (104.423, 115.053, 116.003)), ('A', 679, u'GLY', 0.543904215534957, (101.768, 107.05499999999999, 101.027)), ('A', 692, u'SER', 0.5550154372796332, (91.735, 98.971, 94.073)), ('A', 749, u'LEU', 0.6516396099512637, (92.17199999999998, 93.71100000000001, 78.306)), ('A', 759, u'SER', 0.6067579029464918, (92.166, 96.633, 97.689)), ('A', 764, u'VAL', 0.5591827750805285, (93.745, 87.34700000000001, 87.01100000000001)), ('A', 778, u'SER', 0.6058590915833187, (103.002, 88.14, 83.054)), ('A', 785, u'VAL', 0.539613570086185, (106.483, 97.613, 87.05199999999999)), ('A', 788, u'TYR', 0.6123712729837512, (110.48400000000001, 101.086, 88.516)), ('A', 817, u'THR', 0.639740688752386, (89.15199999999999, 77.645, 96.483)), ('A', 837, u'ILE', 0.5978766904824512, (90.537, 79.024, 112.693)), ('A', 840, u'ALA', 0.5507458904805467, (91.06, 82.024, 116.748)), ('A', 841, u'GLY', 0.5187873730611761, (89.324, 79.339, 118.79100000000001)), ('A', 863, u'ALA', 0.5874460349199092, (82.17999999999999, 77.013, 112.069)), ('A', 878, u'ALA', 0.6089020501678095, (86.898, 68.085, 108.298)), ('A', 889, u'ARG', 0.5852428596175109, (77.364, 71.18299999999999, 121.87799999999999)), ('A', 917, u'GLU', 0.5587502530167906, (73.423, 70.518, 113.58)), ('B', 90, u'MET', 0.5657505215434537, (92.41300000000001, 124.21400000000001, 125.40700000000001)), ('B', 97, u'LYS', 0.44078756059889534, (101.94000000000001, 128.20999999999998, 126.79100000000001)), ('B', 101, u'ASP', 0.6704092305704781, (108.783, 137.559, 122.01700000000001)), ('B', 111, u'ARG', 0.6615256298797125, (107.54400000000001, 139.875, 104.15299999999999)), ('B', 125, u'ALA', 0.5617048534884337, (110.77799999999999, 126.476, 121.486)), ('B', 137, u'THR', 0.6692167207069247, (124.006, 108.21700000000001, 119.093)), ('B', 155, u'GLU', 0.6269358518437991, (122.35499999999999, 123.233, 127.976)), ('B', 158, u'GLN', 0.5778947097261095, (117.60499999999999, 116.40700000000001, 132.71899999999997)), ('B', 163, u'ASP', 0.6777809669077016, (111.335, 104.115, 133.02800000000002)), ('B', 171, u'GLU', 0.6955452880622582, (126.124, 107.16199999999999, 134.785)), ('B', 184, u'LEU', 0.6842779318029265, (117.161, 108.01400000000001, 126.96300000000001)), ('B', 187, u'THR', 0.58856775814683, (115.557, 117.66199999999999, 128.236)), ('C', 5, u'ASP', 0.42048563802116634, (101.534, 72.81400000000001, 125.26700000000001)), ('C', 46, u'THR', 0.5760733817503121, (114.65499999999999, 71.871, 122.691)), ('C', 52, u'MET', 0.3997895986229659, (110.36999999999999, 78.537, 128.476))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11994/7b3c/Model_validation_1/validation_cootdata/molprobity_probe7b3c_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

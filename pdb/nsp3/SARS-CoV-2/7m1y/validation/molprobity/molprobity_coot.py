# script auto-generated by phenix.molprobity


from __future__ import absolute_import, division, print_function
from six.moves import cPickle as pickle
from six.moves import range
try :
  import gobject
except ImportError :
  gobject = None
import sys

class coot_extension_gui(object):
  def __init__(self, title):
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

  def finish_window(self):
    import gtk
    self.outside_vbox.set_border_width(2)
    ok_button = gtk.Button("  Close  ")
    self.outside_vbox.pack_end(ok_button, False, False, 0)
    ok_button.connect("clicked", lambda b: self.destroy_window())
    self.window.connect("delete_event", lambda a, b: self.destroy_window())
    self.window.show_all()

  def destroy_window(self, *args):
    self.window.destroy()
    self.window = None

  def confirm_data(self, data):
    for data_key in self.data_keys :
      outlier_list = data.get(data_key)
      if outlier_list is not None and len(outlier_list) > 0 :
        return True
    return False

  def create_property_lists(self, data):
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

# Molprobity result viewer
class coot_molprobity_todo_list_gui(coot_extension_gui):
  data_keys = [ "rama", "rota", "cbeta", "probe" ]
  data_titles = { "rama"  : "Ramachandran outliers",
                  "rota"  : "Rotamer outliers",
                  "cbeta" : "C-beta outliers",
                  "probe" : "Severe clashes" }
  data_names = { "rama"  : ["Chain", "Residue", "Name", "Score"],
                 "rota"  : ["Chain", "Residue", "Name", "Score"],
                 "cbeta" : ["Chain", "Residue", "Name", "Conf.", "Deviation"],
                 "probe" : ["Atom 1", "Atom 2", "Overlap"] }
  if (gobject is not None):
    data_types = { "rama" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "rota" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cbeta" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "probe" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT] }
  else :
    data_types = dict([ (s, []) for s in ["rama","rota","cbeta","probe"] ])

  def __init__(self, data_file=None, data=None):
    assert ([data, data_file].count(None) == 1)
    if (data is None):
      data = load_pkl(data_file)
    if not self.confirm_data(data):
      return
    coot_extension_gui.__init__(self, "MolProbity to-do list")
    self.dots_btn = None
    self.dots2_btn = None
    self._overlaps_only = True
    self.window.set_default_size(420, 600)
    self.create_property_lists(data)
    self.finish_window()

  def add_top_widgets(self, data_key, box):
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

  def toggle_probe_dots(self, *args):
    if self.dots_btn is not None :
      show_dots = self.dots_btn.get_active()
      overlaps_only = self.dots2_btn.get_active()
      if show_dots :
        self.dots2_btn.set_sensitive(True)
      else :
        self.dots2_btn.set_sensitive(False)
      show_probe_dots(show_dots, overlaps_only)

  def toggle_all_probe_dots(self, *args):
    if self.dots2_btn is not None :
      self._overlaps_only = self.dots2_btn.get_active()
      self.toggle_probe_dots()

class rsc_todo_list_gui(coot_extension_gui):
  data_keys = ["by_res", "by_atom"]
  data_titles = ["Real-space correlation by residue",
                 "Real-space correlation by atom"]
  data_names = {}
  data_types = {}

class residue_properties_list(object):
  def __init__(self, columns, column_types, rows, box,
      default_size=(380,200)):
    assert len(columns) == (len(column_types) - 1)
    if (len(rows) > 0) and (len(rows[0]) != len(column_types)):
      raise RuntimeError("Wrong number of rows:\n%s" % str(rows[0]))
    import gtk
    self.liststore = gtk.ListStore(*column_types)
    self.listmodel = gtk.TreeModelSort(self.liststore)
    self.listctrl = gtk.TreeView(self.listmodel)
    self.listctrl.column = [None]*len(columns)
    self.listctrl.cell = [None]*len(columns)
    for i, column_label in enumerate(columns):
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn(column_label)
      self.listctrl.append_column(column)
      column.set_sort_column_id(i)
      column.pack_start(cell, True)
      column.set_attributes(cell, text=i)
    self.listctrl.get_selection().set_mode(gtk.SELECTION_SINGLE)
    for row in rows :
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

  def OnChange(self, treeview):
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

def show_probe_dots(show_dots, overlaps_only):
  import coot # import dependency
  n_objects = number_of_generic_objects()
  sys.stdout.flush()
  if show_dots :
    for object_number in range(n_objects):
      obj_name = generic_object_name(object_number)
      if overlaps_only and not obj_name in ["small overlap", "bad overlap"] :
        sys.stdout.flush()
        set_display_generic_object(object_number, 0)
      else :
        set_display_generic_object(object_number, 1)
  else :
    sys.stdout.flush()
    for object_number in range(n_objects):
      set_display_generic_object(object_number, 0)

def load_pkl(file_name):
  pkl = open(file_name, "rb")
  data = pickle.load(pkl)
  pkl.close()
  return data

data = {}
data['rama'] = []
data['omega'] = []
data['rota'] = [('A', ' 170 ', 'SER', 0.17425617313484099, (56.53699999999994, 33.352, 44.457)), ('A', ' 186 ', 'ASN', 0.2520329417311908, (70.82500000000002, 47.73099999999997, 56.058)), ('A', ' 191 ', 'THR', 0.07661214249794003, (72.74199999999996, 62.052999999999955, 55.86)), ('A', ' 194 ', 'GLN', 0.0, (71.31699999999996, 53.66499999999999, 58.918)), ('A', ' 210 ', 'THR', 0.038846715853974194, (69.88000000000001, 42.86099999999999, 41.053)), ('A', ' 269 ', 'GLN', 0.007642863665347845, (52.80200000000001, 39.278, 24.043)), ('A', ' 269 ', 'GLN', 0.07530378099948384, (52.768, 39.242, 24.118)), ('A', ' 295 ', 'GLU', 0.005147310179676004, (80.79100000000005, 31.179999999999982, 29.006)), ('A', ' 315 ', 'LYS', 0.07501769633637344, (81.47999999999999, 47.58799999999997, 59.875)), ('B', '   6 ', 'LYS', 0.26097771686449306, (23.559999999999995, -0.6329999999999998, 14.905)), ('B', '  18 ', 'THR', 0.02249523170701286, (24.749000000000006, 1.1179999999999997, 8.498)), ('B', '  44 ', 'ILE', 0.023558821924204373, (34.473, 6.836999999999999, 24.005)), ('B', '  51 ', 'GLU', 0.16672690055292927, (21.517, 2.987, 18.906)), ('B', '  80 ', 'LEU', 0.008445779936798408, (35.916, 16.788999999999998, 7.252)), ('B', ' 162 ', 'LEU', 0.02260045966204033, (41.93100000000001, 36.35799999999999, 14.286000000000007)), ('B', ' 190 ', 'LYS', 0.0034024770302186367, (49.057, 61.65699999999999, -19.871)), ('B', ' 269 ', 'GLN', 0.16430445151702552, (47.89400000000001, 41.011999999999986, 17.084000000000014)), ('B', ' 269 ', 'GLN', 0.24804852559242868, (47.885999999999996, 40.92999999999999, 17.026))]
data['cbeta'] = []
data['probe'] = [(' B 284  CYS  SG ', ' B 403  9JT SE1 ', -0.672, (29.043, 50.904, 14.765)), (' A 501  9JT  O09', ' A 501  9JT SE1 ', -0.665, (72.286, 30.655, 24.711)), (' A 263  GLU  OE2', ' A 296  TYR  OH ', -0.651, (70.647, 34.053, 27.774)), (' B 403  9JT  O09', ' B 403  9JT SE1 ', -0.628, (30.387, 53.287, 15.063)), (' B 296  TYR  C  ', ' B 296  TYR  CD1', -0.618, (30.072, 56.529, 10.223)), (' A 164  ASP  OD2', ' A 504  GOL  H2 ', -0.545, (57.369, 37.648, 34.2)), (' A  89  HIS  HB2', ' A 159  VAL HG21', -0.529, (46.652, 21.912, 29.714)), (' A 105  LYS  HD2', ' A 510  IOD  I  ', -0.519, (59.993, 15.64, 23.225)), (' A 296  TYR  C  ', ' A 296  TYR  CD1', -0.518, (75.861, 33.755, 28.914)), (' A 166  ARG  HA ', ' A 243  MET  HE1', -0.516, (61.127, 33.895, 40.157)), (' B 301 BTHR HG23', ' B 302  ASP  OD2', -0.514, (36.902, 45.341, 5.635)), (' A  95  TYR  CD1', ' A 144  ALA  HB3', -0.498, (56.668, 16.471, 33.23)), (' A 207  TYR  HE2', ' A 210 BTHR HG23', -0.497, (68.98, 44.395, 43.666)), (' B  61  ASP  C  ', ' B  61  ASP  OD1', -0.491, (35.785, 5.378, 0.23)), (' A 501  9JT  H1 ', ' A 501  9JT  O09', -0.477, (74.241, 32.518, 24.279)), (' B  13  ASN  HB2', ' B  56  TYR  OH ', -0.47, (25.718, 15.529, 8.014)), (' B 263  GLU  OE2', ' B 296  TYR  OH ', -0.464, (33.342, 51.914, 12.213)), (' A 140  ARG  HD2', ' A 605  HOH  O  ', -0.459, (63.869, 17.425, 43.963)), (' A 268  TYR  CD2', ' A 269 BGLN  HG2', -0.442, (52.224, 42.366, 24.969)), (' A 268  TYR  CE2', ' A 269 BGLN  HG2', -0.44, (51.869, 42.379, 24.245)), (' A 301 ATHR HG23', ' A 302  ASP  OD2', -0.438, (63.663, 35.253, 35.471)), (' B  63  THR  O  ', ' B  66  VAL HG12', -0.436, (31.876, 8.206, -2.422)), (' A 203  GLU  O  ', ' A 601  HOH  O  ', -0.434, (62.397, 39.292, 50.074)), (' B  40  ASP  OD1', ' B  42  THR  OG1', -0.431, (37.027, 11.206, 17.772)), (' A 284  CYS  SG ', ' A 501  9JT SE1 ', -0.419, (70.705, 28.831, 26.134)), (' A 263  GLU  O  ', ' A 273  TYR  HA ', -0.408, (63.973, 32.416, 29.296)), (' B  95  TYR  CD1', ' B 144  ALA  HB3', -0.407, (24.897, 31.421, 13.797))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

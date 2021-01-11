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
data['rama'] = [('A', ' 154 ', 'TYR', 0.020234232227171713, (-14.772000000000002, -10.310999999999996, 31.822)), ('A', ' 169 ', 'THR', 0.030812001592223928, (-14.148000000000003, 13.751, 5.662))]
data['omega'] = []
data['rota'] = [('A', ' 147 ', 'SER', 0.17309787703304924, (-12.178999999999998, -5.252999999999998, 10.916))]
data['cbeta'] = []
data['probe'] = [(' A 278  GLY  O  ', ' A 501  HOH  O  ', -0.91, (-0.617, 25.881, 26.534)), (' A 170  GLY  O  ', ' A 502  HOH  O  ', -0.894, (-11.593, 10.582, 9.491)), (' A  69  GLN  HG3', ' A  74  GLN  HG2', -0.821, (-6.562, -20.403, 3.534)), (' A 240  GLU  OE2', ' A 504  HOH  O  ', -0.765, (-23.816, 11.531, 21.773)), (' A  27  LEU HD13', ' A  39  PRO  HD2', -0.712, (-15.314, -8.182, 4.215)), (' A  46 BSER  OG ', ' A 503  HOH  O  ', -0.71, (-10.843, -2.871, -7.45)), (' A 198  THR HG22', ' A 238  ASN  OD1', -0.692, (-23.612, 19.113, 17.484)), (' A 401  VHV  O9 ', ' A 505  HOH  O  ', -0.657, (-11.213, -2.967, 2.043)), (' A 144  SER  O  ', ' A 147 BSER  OG ', -0.606, (-11.745, -3.502, 8.967)), (' A  17  MET  HG3', ' A 117  CYS  SG ', -0.589, (-8.484, -8.976, 12.254)), (' A 115  LEU HD11', ' A 122  PRO  HB3', -0.583, (-5.114, -7.312, 15.47)), (' A 221  ASN  ND2', ' A 223  PHE  HD2', -0.542, (-16.714, 29.13, 37.061)), (' A 228  ASN  O  ', ' A 232  LEU HD23', -0.52, (-30.367, 26.579, 29.309)), (' A 222  ARG  NH1', ' A 514  HOH  O  ', -0.518, (-20.407, 31.528, 46.014)), (' A 169  THR  HB ', ' A 171  VAL HG22', -0.517, (-16.002, 12.327, 7.135)), (' A 221  ASN HD22', ' A 270  GLU  HG3', -0.517, (-16.028, 28.695, 35.569)), (' A 294  PHE  CE1', ' A 298  ARG  HD2', -0.516, (-15.159, -0.498, 30.891)), (' A   4  ARG  NH2', ' A 510  HOH  O  ', -0.513, (-0.698, 6.641, 24.613)), (' A  72  ASN  O  ', ' A  74  GLN  HG3', -0.502, (-4.773, -22.852, 5.26)), (' A 100  LYS  HE3', ' A 654  HOH  O  ', -0.502, (-22.064, -14.078, 27.437)), (' A 225  THR  OG1', ' A 229  ASP  OD2', -0.5, (-25.492, 27.355, 34.437)), (' A 102  LYS  HE3', ' A 654  HOH  O  ', -0.49, (-22.853, -12.496, 27.164)), (' A 189  GLN  HA ', ' A 401  VHV  O29', -0.473, (-18.239, 5.413, -2.105)), (' A  26  THR HG21', ' A 119  ASN  ND2', -0.469, (-6.118, -10.602, 1.521)), (' A  69  GLN  HG3', ' A  74  GLN  CG ', -0.463, (-6.179, -21.053, 3.696)), (' A  31  TRP  CE2', ' A  75  LEU HD21', -0.456, (-13.216, -21.225, 10.204)), (' A 132  PRO  HG3', ' A 240  GLU  OE2', -0.443, (-23.25, 12.72, 20.763)), (' A  27  LEU  CD1', ' A  39  PRO  HD2', -0.436, (-15.301, -8.418, 4.411)), (' A  95  ASN  HB3', ' A  98  THR  OG1', -0.42, (-15.147, -20.066, 16.965)), (' A 127  GLN  HG2', ' A 620  HOH  O  ', -0.414, (-11.795, 4.49, 25.207)), (' A 109  GLY  HA2', ' A 200  ILE HD13', -0.413, (-20.252, 9.423, 22.473)), (' A 190  THR  O  ', ' A 192  GLN  HG3', -0.408, (-22.191, 8.3, -0.656)), (' A 222  ARG  NH2', ' A 222  ARG  O  ', -0.404, (-18.756, 28.675, 44.305)), (' A 167  LEU  O  ', ' A 169  THR  N  ', -0.401, (-14.736, 11.882, 4.221))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

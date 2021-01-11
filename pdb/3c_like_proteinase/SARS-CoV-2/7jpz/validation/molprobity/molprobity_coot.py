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
data['rama'] = [('A', '  71 ', 'GLY', 0.02752184059785356, (-3.7490000000000014, -18.576, 8.789))]
data['omega'] = [('A', ' 306 ', 'GLN', None, (-10.888000000000002, -12.141999999999996, 31.226999999999997))]
data['rota'] = [('A', ' 240 ', 'GLU', 0.21351250406891698, (-24.991999999999997, 17.045999999999996, 22.875))]
data['cbeta'] = [('A', '  74 ', 'GLN', ' ', 0.2502452062989793, (-9.262000000000004, -24.481999999999992, 3.205))]
data['probe'] = [(' A 165  MET  HB3', ' A 632  HOH  O  ', -0.833, (-17.747, 1.086, 1.497)), (' A   4  ARG  NH2', ' A 505  HOH  O  ', -0.781, (1.671, 7.91, 25.934)), (' A  40  ARG  HA ', ' A  87  LEU HD13', -0.765, (-21.682, -9.805, 0.734)), (' A 165  MET  SD ', ' A 632  HOH  O  ', -0.729, (-18.911, 1.895, 1.411)), (' A  74  GLN  OE1', ' A 501  HOH  O  ', -0.708, (-11.956, -22.789, 0.873)), (' A   2  GLY  O  ', ' A 503  HOH  O  ', -0.698, (-4.23, 5.601, 35.519)), (' A 290  GLU  OE1', ' A 502  HOH  O  ', -0.695, (-11.172, 8.006, 19.848)), (' A  40  ARG  CB ', ' A  87  LEU HD13', -0.65, (-22.49, -9.772, 1.015)), (' A 168  PRO  HA ', ' A 401  GHX  H28', -0.625, (-14.134, 9.792, -0.643)), (' A  40  ARG  CA ', ' A  87  LEU HD13', -0.614, (-21.82, -9.154, 0.904)), (' A  60  ARG  HG3', ' A  60  ARG HH21', -0.608, (-25.955, -13.423, -11.178)), (' A 189  GLN  HG2', ' A 189  GLN  O  ', -0.604, (-18.37, 5.594, -5.569)), (' A 190  THR  OG1', ' A 504  HOH  O  ', -0.597, (-23.725, 9.583, -5.128)), (' A 188  ARG  NE ', ' A 514  HOH  O  ', -0.589, (-25.823, 4.132, -5.987)), (' A 298  ARG  HG3', ' A 303  VAL  HB ', -0.575, (-12.263, -2.302, 33.897)), (' A 269  LYS  HE3', ' A 273  GLN HE22', -0.574, (-21.658, 30.275, 30.104)), (' A 190  THR  O  ', ' A 506  HOH  O  ', -0.539, (-19.405, 7.121, -1.031)), (' A 401  GHX  H21', ' A 401  GHX  H22', -0.529, (-16.876, 1.061, -0.736)), (' A 156  CYS  O  ', ' A 507  HOH  O  ', -0.516, (-18.12, -9.266, 26.013)), (' A  49  MET  HG2', ' A 401  GHX  C22', -0.498, (-17.357, -1.641, -4.171)), (' A  40  ARG  CB ', ' A  87  LEU  CD1', -0.497, (-22.749, -9.762, 1.016)), (' A  60  ARG  HG3', ' A  60  ARG  NH2', -0.496, (-25.959, -13.419, -11.433)), (' A  95  ASN  HB3', ' A  98  THR  OG1', -0.479, (-15.133, -20.249, 16.68)), (' A  56  ASP  O  ', ' A  60  ARG  NH2', -0.477, (-26.43, -11.998, -10.614)), (' A 168  PRO  CA ', ' A 401  GHX  H28', -0.469, (-14.733, 9.649, -0.382)), (' A 269  LYS  HE3', ' A 273  GLN  NE2', -0.468, (-21.4, 30.459, 29.685)), (' A 401  GHX  H21', ' A 401  GHX  N13', -0.464, (-16.358, 1.233, -0.15)), (' A 154  TYR  H  ', ' A 305  PHE  HD1', -0.452, (-14.498, -8.515, 31.104)), (' A 115  LEU HD11', ' A 122  PRO  HB3', -0.448, (-5.091, -7.909, 15.438)), (' A  40  ARG  HB2', ' A  87  LEU  CD1', -0.448, (-22.839, -9.369, 0.685)), (' A 113  SER  O  ', ' A 149  GLY  HA2', -0.425, (-13.269, -2.988, 18.128)), (' A  40  ARG  HB2', ' A  87  LEU HD13', -0.424, (-22.535, -9.323, 0.663)), (' A 109  GLY  HA2', ' A 200  ILE HD13', -0.416, (-19.696, 9.394, 22.239)), (' A 221  ASN  ND2', ' A 223  PHE  HB2', -0.411, (-17.707, 28.034, 37.329)), (' A   6  MET  HB2', ' A   6  MET  HE3', -0.407, (-6.385, 2.8, 29.219)), (' A  17  MET  HG3', ' A 117  CYS  SG ', -0.406, (-8.31, -9.515, 12.748))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

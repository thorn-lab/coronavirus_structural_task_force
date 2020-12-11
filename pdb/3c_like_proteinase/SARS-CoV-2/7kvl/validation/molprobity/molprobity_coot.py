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
data['rama'] = [('A', ' 141 ', 'LEU', 0.027660186544883066, (-14.238, 5.261, 21.228)), ('B', '   3 ', 'PHE', 0.008261774567166355, (-5.669999999999998, 7.176999999999998, 22.204))]
data['omega'] = []
data['rota'] = [('A', ' 165 ', 'MET', 0.01777431087087024, (-18.328999999999994, 0.881, 29.532)), ('B', '  49 ', 'MET', 0.290039520981517, (21.172, -14.261999999999999, -5.449))]
data['cbeta'] = [('B', '  49 ', 'MET', ' ', 0.2904871058380342, (20.39699999999999, -14.489000000000003, -4.142))]
data['probe'] = [(' B 287  LEU  H  ', ' B 705  PEG  H12', -0.903, (8.741, 11.011, 21.867)), (' A 233  VAL HG21', ' A 269  LYS  HD3', -0.72, (15.255, -2.843, 44.333)), (' A 224  THR  H  ', ' A 506  PEG  H32', -0.718, (23.515, -10.727, 42.834)), (' A 286  LEU  HG ', ' B 286  LEU HD11', -0.709, (9.151, 4.226, 25.34)), (' A 509  DMS  H22', ' B 127  GLN  H  ', -0.702, (0.466, -2.621, 14.527)), (' B 102  LYS  HE2', ' B 869  HOH  O  ', -0.687, (-8.576, 2.265, -3.416)), (' A 140  PHE  HE1', ' B 214  ASN HD21', -0.654, (-8.49, 12.013, 21.836)), (' A 141  LEU HD12', ' A 172  HIS  CE1', -0.634, (-11.966, 3.236, 24.703)), (' B  86  VAL HG13', ' B 179  GLY  HA2', -0.631, (7.329, -4.691, -7.429)), (' A 137  LYS  HE3', ' B 701  PEG  H41', -0.611, (-2.869, 2.062, 27.427)), (' A 141  LEU HD12', ' A 172  HIS  NE2', -0.602, (-12.713, 3.049, 24.543)), (' A   4  ARG  NH2', ' A 603  HOH  O  ', -0.599, (3.556, 1.658, 14.285)), (' B  45  THR  OG1', ' B  48  ASP  OD2', -0.596, (20.567, -20.029, -8.87)), (' B  21  THR  HB ', ' B  67  LEU  HB3', -0.595, (6.006, -24.112, -5.032)), (' A 118  TYR  HE2', ' A 142  ASN  H  ', -0.565, (-16.742, 4.772, 19.114)), (' B   1  SER  HB3', ' B 283  GLY  HA3', -0.552, (-1.881, 7.91, 28.536)), (' A  86  VAL HG23', ' A 179  GLY  HA2', -0.539, (-21.515, -10.765, 29.488)), (' A 118  TYR  OH ', ' A 141  LEU  HA ', -0.535, (-14.598, 4.715, 19.7)), (' A  71  GLY  HA2', ' A 511  DMS  H12', -0.529, (-24.19, -4.528, 6.814)), (' A 269  LYS  HG2', ' A 503  X4P  C3 ', -0.527, (15.709, -1.155, 42.346)), (' B  49  MET  HG3', ' B  49  MET  O  ', -0.52, (20.755, -12.514, -4.584)), (' A 115  LEU HD11', ' A 122  PRO  HB3', -0.519, (-12.938, -5.209, 12.651)), (' B  49  MET  CG ', ' B 189  GLN  H  ', -0.514, (20.788, -12.318, -3.38)), (' B  49  MET  HG2', ' B 189  GLN  HG2', -0.503, (20.189, -13.105, -1.999)), (' A 273  GLN  HB2', ' A 503  X4P  N2 ', -0.494, (16.65, 1.896, 41.263)), (' B 228  ASN  O  ', ' B 232  LEU HD12', -0.494, (15.175, 26.862, 10.289)), (' A 118  TYR  OH ', ' A 141  LEU HD23', -0.492, (-13.936, 3.441, 19.03)), (' B  57  LEU  O  ', ' B  61  LYS  HG3', -0.482, (13.592, -18.358, -15.279)), (' A   0  MET  HG2', ' B 141  LEU HD12', -0.479, (11.059, -11.909, 17.437)), (' B  49  MET  HG2', ' B 189  GLN  H  ', -0.475, (20.836, -12.432, -2.886)), (' A  15  GLY  HA2', ' A 505  PEG  H41', -0.465, (-17.968, -11.087, 9.048)), (' A 109  GLY  HA2', ' A 200  ILE HD13', -0.464, (-0.67, -8.113, 32.158)), (' A 140  PHE  HE1', ' B 214  ASN  ND2', -0.46, (-8.682, 12.484, 22.102)), (' A 165 BMET  HE3', ' A 167  LEU HD21', -0.459, (-16.623, 0.82, 34.518)), (' A 163  HIS  CE1', ' A 172  HIS  HB3', -0.459, (-14.479, -0.306, 27.132)), (' A  56  ASP  O  ', ' A  59  ILE HG22', -0.458, (-39.218, -5.991, 32.828)), (' B  59  ILE HG13', ' B  60  ARG  HG3', -0.457, (14.935, -17.105, -20.18)), (' B 113  SER  O  ', ' B 149  GLY  HA2', -0.455, (-0.303, -3.274, 5.464)), (' B 156  CYS  SG ', ' B 869  HOH  O  ', -0.454, (-9.974, 1.792, -2.329)), (' A 141  LEU HD22', ' A 144  SER  OG ', -0.454, (-15.419, 1.464, 21.26)), (' B  40  ARG  O  ', ' B  43  ILE HG12', -0.451, (12.863, -14.415, -8.823)), (' A 502  PEG  H21', ' A 502  PEG  H42', -0.45, (-30.21, 2.827, 11.115)), (' A   0  MET  HB2', ' A 214  ASN  ND2', -0.449, (14.709, -11.365, 19.792)), (' A 139  SER  HB3', ' A 141  LEU  CD2', -0.446, (-12.371, 2.469, 20.593)), (' B  86  VAL HG13', ' B 179  GLY  CA ', -0.445, (7.144, -4.719, -7.663)), (' B 287  LEU  N  ', ' B 705  PEG  H12', -0.445, (8.154, 11.138, 22.03)), (' B 108  PRO  HA ', ' B 130  MET  CG ', -0.44, (7.69, 6.181, 4.147)), (' B  62  SER  H  ', ' B  65  ASN HD22', -0.437, (10.377, -23.475, -15.206)), (' B  62  SER  N  ', ' B  65  ASN HD22', -0.436, (9.962, -22.993, -15.497)), (' B 246  HIS  HA ', ' B 249  ILE HD12', -0.434, (2.191, 17.936, 4.92)), (' A  63  ASN  HB3', ' A  77  VAL  O  ', -0.43, (-37.575, -12.657, 18.134)), (' A 113  SER  O  ', ' A 149  GLY  HA2', -0.428, (-10.33, -8.748, 21.5)), (' B  15  GLY  HA2', ' B 703  PEG  H12', -0.425, (-9.345, -14.882, 2.861)), (' A 286  LEU  HG ', ' B 286  LEU  CD1', -0.421, (8.429, 4.887, 25.016)), (' A 141  LEU HD22', ' A 144  SER  CB ', -0.417, (-15.078, 1.656, 20.764)), (' B 109  GLY  HA2', ' B 200  ILE HD13', -0.412, (6.449, 8.94, 8.808)), (' A 165 AMET  HB3', ' A 165 AMET  HE3', -0.407, (-19.898, 2.371, 31.215)), (' A 165 BMET  HE1', ' A 192  GLN  NE2', -0.407, (-18.917, 0.544, 35.839)), (' A  90  LYS  HB2', ' A 504  PEG  H41', -0.407, (-31.683, -17.469, 22.162)), (' B  49  MET  HG2', ' B 189  GLN  CB ', -0.403, (21.332, -12.82, -1.86)), (' A 153  ASP  HB2', ' A 622  HOH  O  ', -0.401, (-6.925, -21.438, 20.432))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

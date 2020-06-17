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
data['rota'] = [('A', '  62 ', 'SER', 0.26948805685219823, (-23.597, -21.749, 22.589000000000006)), ('A', ' 189 ', 'GLN', 0.0, (-22.478, 2.982, 19.965000000000003)), ('A', ' 222 ', 'ARG', 0.0, (22.299999999999997, 27.393, 7.954)), ('A', ' 224 ', 'THR', 0.008159601566148922, (21.431999999999995, 25.592000000000006, 14.716000000000003)), ('A', ' 235 ', 'MET', 0.027060036190183885, (4.357, 22.658, 21.221000000000007))]
data['cbeta'] = []
data['probe'] = [(' A 276  MET  CE ', ' A 281  ILE HG13', -0.693, (7.805, 20.431, 0.89)), (' A 256  GLN  HG3', ' A 540  HOH  O  ', -0.683, (24.86, 6.94, 3.436)), (' A 188  ARG  HG3', ' A 190  THR HG22', -0.675, (-20.468, 3.434, 23.411)), (' A 154  TYR  O  ', ' A 305  PHE  HB3', -0.597, (9.755, -11.95, 5.919)), (' A 186  VAL HG23', ' A 188  ARG  HG2', -0.591, (-18.869, 2.012, 24.228)), (' A 276  MET  HE3', ' A 281  ILE HG13', -0.576, (8.507, 20.974, 1.652)), (' A 176  ASP  HB2', ' A 516  HOH  O  ', -0.56, (-2.345, -6.567, 20.324)), (' A 225  THR HG22', ' A 266  ALA  HB2', -0.553, (17.606, 24.481, 14.489)), (' A 155  ASP  HB2', ' A 306  GLN  NE2', -0.531, (9.25, -17.103, 6.851)), (' A  60  ARG  HD2', ' A  60  ARG  N  ', -0.523, (-27.118, -15.569, 26.771)), (' A  55  GLU  O  ', ' A  59  ILE HG12', -0.515, (-23.625, -13.742, 29.434)), (' A  40  ARG  CB ', ' A  87  LEU HD13', -0.514, (-16.856, -11.107, 21.652)), (' A 225  THR  OG1', ' A 226  THR  N  ', -0.502, (17.265, 25.095, 18.96)), (' A  33  ASP  O  ', ' A  94  ALA  HA ', -0.49, (-5.385, -24.416, 13.869)), (' A 105  ARG  NH1', ' A 176  ASP  OD2', -0.48, (-3.985, -3.303, 23.599)), (' A 113  SER  O  ', ' A 149  GLY  HA2', -0.479, (-2.273, -4.089, 9.338)), (' A 276  MET  HE1', ' A 281  ILE HG13', -0.479, (7.797, 20.021, 1.377)), (' A 109  GLY  HA2', ' A 200  ILE HD13', -0.473, (3.031, 8.404, 14.966)), (' A   6  MET  O  ', ' A 403  DMS  H22', -0.468, (5.209, 0.302, 3.601)), (' A  95  ASN  HB3', ' A  98  THR  OG1', -0.466, (-2.938, -21.628, 11.269)), (' A 249  ILE  CG2', ' A 293  PRO  HG2', -0.449, (13.962, 6.615, 14.992)), (' A 201  THR HG22', ' A 242  LEU HD13', -0.436, (10.555, 15.677, 16.566)), (' A 108  PRO  HG3', ' A 134  PHE  CE1', -0.433, (-0.935, 5.654, 21.978)), (' A 121  SER  HA ', ' A 122  PRO  HD3', -0.433, (-10.655, -13.169, 2.04)), (' A 247  VAL HG22', ' A 261  VAL HG11', -0.431, (17.598, 14.529, 18.02)), (' A 262  LEU  HA ', ' A 262  LEU HD23', -0.427, (18.177, 19.572, 16.882)), (' A 271  LEU HD22', ' A 276  MET  HG2', -0.425, (7.999, 23.36, 4.013)), (' A   6  MET  HB2', ' A   6  MET  HE3', -0.419, (7.5, 1.986, 0.401)), (' A  78  ILE HD11', ' A  92  ASP  HB3', -0.417, (-13.134, -29.133, 16.865)), (' A 306  GLN  HG2', ' A 306  GLN  O  ', -0.415, (9.005, -16.476, 3.12)), (' A 294  PHE  O  ', ' A 298  ARG  HG3', -0.413, (12.815, 0.704, 8.283)), (' A   1  SER  HA ', ' A 545  HOH  O  ', -0.41, (15.137, 4.563, -3.957)), (' A  40  ARG  HD3', ' A  85  CYS  HA ', -0.409, (-14.772, -7.545, 24.231)), (' A  92  ASP  N  ', ' A  92  ASP  OD1', -0.409, (-12.28, -27.26, 14.528)), (' A  41  HIS  HB2', ' A  49  MET  SD ', -0.406, (-21.446, -4.555, 18.684)), (' A 233  VAL HG21', ' A 269  LYS  HE2', -0.406, (11.809, 28.042, 17.31))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

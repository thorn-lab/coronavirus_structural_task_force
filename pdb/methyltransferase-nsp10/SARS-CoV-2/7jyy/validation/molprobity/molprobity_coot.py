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
data['rota'] = []
data['cbeta'] = []
data['probe'] = [(' B4270  CYS  HA ', ' B4274  VAL HG12', -0.734, (58.586, -3.451, -15.637)), (' A6940 AGLU  N  ', ' A6940 AGLU  OE1', -0.636, (91.242, 16.9, 24.159)), (' C6820  LEU HD11', ' C7027 BILE HD12', -0.615, (94.647, -28.164, -30.845)), (' A6841  ASN  ND2', " E   2    U  H4'", -0.603, (76.409, 20.739, 1.797)), (' C6930  TYR  CD1', ' F   1    A  C4 ', -0.564, (81.98, -19.283, -25.801)), (' A6884  ARG  HB3', ' B4349  TYR  OH ', -0.562, (78.589, 20.651, -14.643)), (' C6971  GLU  OE1', ' F   0  M7G  H82', -0.561, (86.807, -27.551, -32.746)), (' C6820  LEU  CD1', ' C7027 BILE HD12', -0.553, (94.472, -29.019, -31.047)), (' B4273  ALA  HB1', ' D4279  ALA  HB1', -0.542, (54.051, -3.86, -12.116)), (' A6894  VAL HG11', ' A7088 AILE HD12', -0.516, (87.834, 7.942, -10.152)), (' B4274  VAL  O  ', ' B4274  VAL HG13', -0.482, (59.002, -1.062, -15.698)), (' A6797  SER  HB3', ' A7036  GLN  HB2', -0.48, (80.988, 42.323, 7.51)), (' C6961  LEU  HB2', ' C7080  ILE  HB ', -0.469, (101.978, -21.248, 0.245)), (' A6892  LEU HD21', ' C7094  VAL HG11', -0.463, (88.133, 10.496, -14.965)), (' A6823  CYS  HB2', ' A7027 AILE HD12', -0.461, (89.367, 28.399, 15.104)), (' C7009  TYR  CZ ', ' C7011  GLY  HA2', -0.46, (103.243, -20.59, -7.595)), (' A7009  TYR  CZ ', ' A7011  GLY  HA2', -0.459, (105.527, 17.233, -4.409)), (' A6930  TYR  CD1', ' E   1    A  C4 ', -0.459, (80.775, 17.834, 8.534)), (' C6915  THR  HB ', ' C7091  ASP  HB2', -0.457, (89.377, -2.28, -14.271)), (' A7101  SAM  CE ', " E   1    A  O2'", -0.454, (80.044, 19.483, 4.396)), (' C6847  GLN  HG3', ' C7042  LEU HD21', -0.452, (77.157, -33.578, -13.394)), (' A6841  ASN HD21', " E   2    U  H4'", -0.446, (77.232, 20.949, 1.866)), (' C6898 BLEU  HG ', ' C7101  SAM  C2 ', -0.441, (84.71, -10.277, -19.177)), (' C6823  CYS  HB3', ' F   0  M7G HM73', -0.441, (87.157, -29.613, -31.504)), (' C6841  ASN  ND2', " F   2    U  H4'", -0.441, (76.648, -22.225, -19.059)), (' C6894  VAL HG11', ' C7088 AILE  CD1', -0.429, (85.613, -9.851, -5.368)), (' C6997  ALA  HB1', ' C7035  ILE  HB ', -0.428, (82.974, -37.638, -23.57)), (' B4354  THR HG21', ' B4502  HOH  O  ', -0.425, (62.29, 32.918, -15.285)), (' C6909  LEU HD11', ' C7088 AILE HD12', -0.421, (86.235, -8.285, -6.761)), (' A6961  LEU  HB2', ' A7080  ILE  HB ', -0.42, (105.686, 18.017, -12.706)), (' C6818  MET  HE3', ' C7028  PHE  CE2', -0.418, (98.303, -39.478, -29.805)), (' A6820  LEU HD11', ' A7027 BILE HD12', -0.414, (93.027, 26.364, 16.638)), (' C6863  MET  HB3', ' C6891  THR HG23', -0.413, (86.271, -21.013, 1.19)), (' A7092  VAL HG22', ' C7088 AILE HG13', -0.41, (85.64, -5.991, -4.18)), (' A6803 BTRP  HA ', ' A7040 BTYR  CD2', -0.408, (80.459, 41.791, -3.782)), (' C7000  SER  HB3', ' F   0  M7G  CM7', -0.408, (86.049, -29.723, -29.852)), (' A6894  VAL HG11', ' A7088 AILE  CD1', -0.401, (87.651, 8.03, -10.381)), (' A6820  LEU  CD1', ' A7027 BILE HD12', -0.4, (93.823, 26.677, 16.35))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

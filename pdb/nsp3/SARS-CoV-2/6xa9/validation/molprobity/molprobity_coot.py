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
data['rota'] = [('B', '  82 ', 'LEU', 0.09713442099721063, (-39.03, 13.049, -68.816)), ('D', ' 114 ', 'LEU', 0.20544188469374952, (-37.818, -0.218, -4.456))]
data['cbeta'] = []
data['probe'] = [(' E 162  LEU HD23', ' F 155  ARG  HB3', -0.766, (-34.423, 9.616, 0.104)), (' C 263  GLU  OE2', ' C 296  TYR  OH ', -0.727, (-53.749, -11.412, -34.547)), (' E 140  ARG  NH1', ' E 601  HOH  O  ', -0.676, (-8.097, -6.115, -1.953)), (' C 162  LEU HD23', ' D 155  ARG  HB3', -0.67, (-44.345, 1.821, -27.011)), (' F 136  PRO  HG2', ' F 139  GLU  HG3', -0.661, (-26.578, 6.03, 27.024)), (' A  49  SER  HB3', ' A 402  GOL  H11', -0.638, (-24.026, 33.541, -15.052)), (' E 157  LYS  HE3', ' E 163  GLY  HA2', -0.62, (-29.987, 5.431, 3.779)), (' A 157  LYS  HE3', ' A 163  GLY  HA2', -0.599, (-36.746, 5.918, -38.832)), (' D  82  LEU HD11', ' D 144  PRO  HG3', -0.594, (-52.746, 6.627, 6.989)), (' A 263  GLU  OE2', ' A 296  TYR  OH ', -0.582, (-33.531, -11.931, -32.022)), (' A 121  GLN  OE1', ' A 140  ARG  NH2', -0.575, (-17.832, 0.677, -30.308)), (' F 123  TRP  HD1', ' F 153  ARG  HB2', -0.56, (-28.938, 12.57, 7.172)), (' B 105  ALA  HB2', ' B 133  ASP  HB3', -0.553, (-40.448, 15.495, -50.178)), (' B 123  TRP  HD1', ' B 153  ARG  HB2', -0.552, (-38.916, 3.239, -45.64)), (' C 157  LYS  HE3', ' C 163  GLY  HA2', -0.546, (-50.272, 5.678, -24.605)), (' B 123  TRP  CD1', ' B 153  ARG  HB2', -0.538, (-38.746, 3.1, -45.594)), (' C  13  ASN  HB2', ' C  56  TYR  OH ', -0.536, (-66.912, 23.119, -29.323)), (' F  82  LEU HD22', ' F 100  LEU HD11', -0.515, (-24.58, 16.36, 29.53)), (' D  86  VAL HG22', ' D 148  VAL  HB ', -0.509, (-49.164, 1.623, -4.309)), (' D  86  VAL  HB ', ' D  96  TYR  CE1', -0.507, (-45.456, 0.333, -3.21)), (' C  89  HIS  HB2', ' C 159  VAL HG21', -0.505, (-52.908, 15.052, -32.786)), (' A  13  ASN  HB2', ' A  56  TYR  OH ', -0.505, (-19.27, 21.974, -31.87)), (' D 103  THR  HA ', ' D 136  PRO  HA ', -0.502, (-48.293, 14.873, -4.965)), (' C 263  GLU  O  ', ' C 273  TYR  HA ', -0.501, (-52.175, -5.286, -31.035)), (' E  13  ASN  HB2', ' E  56  TYR  OH ', -0.5, (-23.219, -17.345, 10.399)), (' E 166  ARG  NH2', ' F 151  ASN  HB3', -0.484, (-23.979, 15.506, 6.719)), (' D 102  GLN  OE1', ' D 106  HIS  ND1', -0.483, (-42.878, 11.297, -1.856)), (' F 104  VAL HG22', ' F 137  LEU HD23', -0.476, (-28.337, 11.965, 22.411)), (' A  47  HIS  HB3', ' A 402  GOL  H32', -0.46, (-26.765, 35.289, -16.863)), (' C 283  TYR  HB3', ' C 290  LEU HD11', -0.46, (-62.972, -7.629, -39.88)), (' A 263  GLU  O  ', ' A 273  TYR  HA ', -0.459, (-35.31, -5.104, -33.802)), (' D  99  ARG  H  ', ' D 102  GLN  NE2', -0.457, (-45.109, 11.666, 1.614)), (' B  86  VAL HG22', ' B 148  VAL  HB ', -0.455, (-38.131, 5.833, -58.865)), (' A  96  PRO  HB3', ' E 289  LEU HD11', -0.454, (-26.277, 0.887, -19.457)), (' A 121  GLN  HA ', ' A 136  TYR  OH ', -0.452, (-17.579, 1.387, -34.642)), (' A 147  PHE  CE2', ' A 151  ILE HD11', -0.452, (-23.205, 6.778, -35.295)), (' F 123  TRP  CD1', ' F 153  ARG  HB2', -0.451, (-28.57, 12.651, 7.458)), (' D  87  ARG  HA ', ' D  93  SER  HA ', -0.45, (-47.6, -4.908, -3.502)), (' E 253  LEU  HB2', ' E 296  TYR  HB3', -0.449, (-15.83, 13.155, -13.6)), (' C 120  LEU  O  ', ' C 136  TYR  OH ', -0.442, (-69.193, 2.179, -27.517)), (' A   4  THR HG22', ' A  22  ASP  HA ', -0.442, (-23.717, 44.62, -25.33)), (' D  99  ARG  O  ', ' D 102  GLN  HG2', -0.441, (-46.73, 12.825, -0.07)), (' D 123  TRP  CD1', ' D 153  ARG  HB3', -0.438, (-49.18, 1.569, -17.64)), (' B  85  LEU  HB2', ' B 147  THR HG22', -0.438, (-36.367, 2.328, -64.071)), (' E  80  LEU  HA ', ' E  80  LEU HD23', -0.436, (-27.266, -10.563, 13.861)), (' A  49  SER  CB ', ' A 402  GOL  H11', -0.434, (-24.295, 33.338, -15.294)), (' B 137  LEU  HB3', ' B 142  LEU HD12', -0.434, (-35.314, 13.477, -60.047)), (' B  81  PRO  HD3', ' B  99  ARG  CZ ', -0.433, (-42.153, 19.541, -69.432)), (' E 219  GLY  HA2', ' E 232  LYS  O  ', -0.43, (-8.08, 26.309, 4.087)), (' A  89  HIS  HB2', ' A 159  VAL HG21', -0.429, (-32.804, 14.144, -28.941)), (' E 147  PHE  CE2', ' E 151  ILE HD11', -0.427, (-20.305, -3.258, 2.951)), (' C  80  LEU  HA ', ' C  80  LEU HD23', -0.423, (-59.813, 21.949, -23.909)), (' B 106  HIS  O  ', ' B 110  GLN  HG3', -0.42, (-45.688, 12.681, -57.617)), (' C 301  THR HG23', ' C 302  ASP  OD2', -0.416, (-54.915, -5.592, -24.232)), (' C 147  PHE  O  ', ' C 151  ILE HG13', -0.415, (-61.73, 10.275, -27.133)), (' A 164  ASP  HB2', ' B 154  LEU  O  ', -0.414, (-38.143, 1.891, -40.409)), (' A  95  TYR  OH ', ' A 145  ALA  HA ', -0.413, (-25.825, 10.55, -27.121)), (' A  95  TYR  CD1', ' A 144  ALA  HB3', -0.413, (-24.014, 6.995, -26.743)), (' F  82  LEU  HA ', ' F  82  LEU HD12', -0.411, (-25.633, 21.0, 31.41)), (' B 120  ASP  HB3', ' B 155  ARG HH21', -0.411, (-44.813, 7.351, -42.365)), (' E 224  CYS  SG ', ' E 225  THR  N  ', -0.411, (-13.821, 33.229, 14.939)), (' C 112  TYR  CD2', ' C 163  GLY  HA3', -0.408, (-51.865, 4.413, -26.351)), (' E 132  LEU  HA ', ' E 132  LEU HD23', -0.406, (-18.357, -7.087, 7.701)), (' E 247  PRO  HB3', ' E 268  TYR  OH ', -0.406, (-26.3, 19.984, -0.138)), (' E 252  GLU  HA ', ' E 296  TYR  O  ', -0.406, (-16.539, 17.161, -13.86)), (' A 224  CYS  SG ', ' A 225  THR  N  ', -0.406, (-36.087, -10.543, -67.84)), (' C 112  TYR  CE2', ' C 163  GLY  HA3', -0.402, (-51.822, 4.75, -26.332))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

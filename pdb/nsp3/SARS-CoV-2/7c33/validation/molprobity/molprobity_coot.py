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
data['probe'] = [(' A  10  LEU  CB ', ' B 169  LEU HD13', -1.461, (15.633, 27.223, -8.447)), (' B  12  LEU HD11', ' B  18  ILE  CD1', -1.346, (21.524, 31.97, 0.56)), (' B  12  LEU  CD1', ' B  18  ILE HD12', -1.324, (21.544, 31.06, 0.261)), (' A  18  ILE  CD1', ' A 153  LEU  HB2', -1.249, (9.941, 21.301, -9.504)), (' A  10  LEU  HB2', ' B 169  LEU  CD1', -1.201, (15.919, 27.446, -7.317)), (' A 169  LEU HD13', ' B  10  LEU  CB ', -1.178, (16.177, 28.41, 2.411)), (' A  10  LEU  O  ', ' A  10  LEU HD12', -1.148, (14.632, 23.525, -9.054)), (' A  18  ILE HD11', ' A 153  LEU  CD1', -1.117, (10.01, 18.861, -9.004)), (' B  10  LEU  O  ', ' B  10  LEU HD12', -1.113, (19.538, 27.663, 3.8)), (' A  10  LEU HD23', ' A 161  TYR  OH ', -1.112, (11.646, 27.881, -7.35)), (' A  18  ILE HD13', ' A 153  LEU  HB2', -1.101, (10.409, 20.661, -9.781)), (' B  10  LEU HD23', ' B 161  TYR  OH ', -1.072, (14.627, 30.214, 2.668)), (' A 169  LEU HD13', ' B  10  LEU  HB2', -1.053, (16.803, 27.083, 2.353)), (' A  18  ILE  CD1', ' A 153  LEU HD12', -1.015, (9.979, 19.532, -9.111)), (' A  10  LEU  CB ', ' B 169  LEU  CD1', -0.996, (15.572, 27.858, -7.816)), (' A  10  LEU  HB3', ' B 169  LEU HD13', -0.967, (14.87, 27.695, -8.022)), (' A  18  ILE HD11', ' A 153  LEU HD12', -0.957, (10.238, 19.951, -8.232)), (' B  12  LEU  CD1', ' B  18  ILE  CD1', -0.954, (22.131, 31.275, 0.511)), (' B  10  LEU HD11', ' B  18  ILE  HB ', -0.938, (19.306, 31.254, 2.67)), (' A  18  ILE  CD1', ' A 153  LEU  CB ', -0.912, (9.567, 19.631, -9.795)), (' A  10  LEU HD11', ' A  18  ILE  HB ', -0.892, (12.882, 23.528, -7.634)), (' A  10  LEU  HB2', ' B 169  LEU HD13', -0.839, (15.958, 25.996, -7.152)), (' A  10  LEU HD23', ' A 161  TYR  CZ ', -0.806, (11.599, 27.277, -7.583)), (' A  18  ILE HD12', ' A 153  LEU  HB2', -0.805, (8.792, 20.935, -8.909)), (' A 107  GLN  HA ', ' C  70  ALA  O  ', -0.803, (3.449, 6.245, 0.634)), (' A 169  LEU  CD1', ' B  10  LEU  HB2', -0.803, (16.027, 27.305, 1.773)), (' A  18  ILE HD13', ' A 153  LEU  CB ', -0.77, (9.684, 19.965, -10.294)), (' A  18  ILE  CD1', ' A 153  LEU  CD1', -0.768, (9.878, 19.549, -9.178)), (' B 107  GLN  HA ', ' D  70  ALA  O  ', -0.765, (37.412, 39.903, -5.76)), (' A  10  LEU HD23', ' A 161  TYR  HH ', -0.761, (12.564, 28.322, -7.33)), (' B  10  LEU HD23', ' B 161  TYR  CZ ', -0.76, (15.033, 31.419, 1.966)), (' A  10  LEU  HG ', ' A  18  ILE  O  ', -0.747, (12.924, 25.682, -9.622)), (' B 107  GLN  CB ', ' D  71  THR  HA ', -0.745, (39.195, 40.451, -6.191)), (' B  10  LEU  HG ', ' B  18  ILE  O  ', -0.74, (17.484, 30.944, 4.794)), (' A 107  GLN  CB ', ' C  71  THR  HA ', -0.738, (3.269, 3.24, 1.074)), (' A 169  LEU HD13', ' B  10  LEU  HB3', -0.707, (15.418, 28.34, 3.146)), (' A  12  LEU HD11', ' A  18  ILE HG13', -0.666, (11.513, 21.195, -6.577)), (' A 168  PHE  O  ', ' A 171  MET  HG2', -0.655, (15.33, 20.6, 1.866)), (' B  10  LEU  CD1', ' B  18  ILE  HB ', -0.645, (19.4, 30.071, 3.115)), (' A  17  TYR  O  ', ' A  18  ILE HD13', -0.642, (10.555, 20.373, -10.083)), (' A  10  LEU  CD2', ' A 161  TYR  OH ', -0.614, (12.728, 27.063, -7.422)), (' B  10  LEU  CD1', ' B  10  LEU  O  ', -0.614, (19.036, 28.128, 3.231)), (' A  10  LEU  HB3', ' B 169  LEU  CD1', -0.596, (15.434, 28.01, -7.769)), (' A  10  LEU  CD1', ' A  18  ILE  HB ', -0.595, (12.767, 24.056, -7.866)), (' A  10  LEU  CD1', ' A  10  LEU  O  ', -0.587, (14.421, 24.296, -8.102)), (' B  12  LEU  CD1', ' B  18  ILE HD11', -0.582, (22.885, 31.653, 1.45)), (' A  80  SER  HA ', ' A  94  HIS  O  ', -0.563, (0.718, 5.871, -16.399)), (' A  10  LEU  C  ', ' A  10  LEU HD12', -0.559, (15.124, 24.267, -8.517)), (' D  80  SER  HA ', ' D  94  HIS  O  ', -0.552, (33.68, 36.495, -22.048)), (' C  80  SER  HA ', ' C  94  HIS  O  ', -0.551, (6.588, 9.266, 17.055)), (' B  80  SER  HA ', ' B  94  HIS  O  ', -0.549, (36.864, 42.399, 11.454)), (' B  12  LEU HD12', ' B  18  ILE  CD1', -0.547, (22.596, 30.902, 2.12)), (' A 100  VAL HG22', ' A 132  PHE  O  ', -0.539, (-5.848, 12.485, -2.539)), (' A  18  ILE HD12', ' A 153  LEU  CB ', -0.538, (8.547, 20.597, -9.387)), (' D 100  VAL HG22', ' D 132  PHE  O  ', -0.537, (16.879, 34.401, -24.245)), (' C 100  VAL HG22', ' C 132  PHE  O  ', -0.533, (8.094, 25.912, 19.433)), (' B 100  VAL HG22', ' B 132  PHE  O  ', -0.532, (29.952, 48.939, -2.078)), (' A  10  LEU  CD2', ' A 161  TYR  CZ ', -0.525, (11.854, 26.917, -7.041)), (' B  18  ILE HG22', ' B 161  TYR  HE1', -0.511, (17.568, 32.932, 3.425)), (' B  10  LEU  C  ', ' B  10  LEU HD12', -0.508, (18.776, 27.744, 3.804)), (' B  10  LEU  CD1', ' B  12  LEU  HG ', -0.508, (19.84, 28.886, 2.124)), (' A  10  LEU  CD1', ' A  12  LEU  HG ', -0.506, (13.789, 22.932, -7.011)), (' B  18  ILE HG22', ' B 161  TYR  CE1', -0.502, (17.594, 33.08, 3.229)), (' A  18  ILE  CD1', ' A 153  LEU  CG ', -0.499, (9.5, 19.17, -9.189)), (' B 138  HIS  HE1', ' D  69  ILE HG22', -0.496, (33.032, 37.091, -7.663)), (' A  12  LEU HD11', ' A  18  ILE  CG1', -0.493, (11.864, 21.58, -6.767)), (' B  18  ILE HD11', ' B 140  LEU HD11', -0.478, (23.433, 32.66, 0.79)), (' A 138  HIS  HE1', ' C  69  ILE HG22', -0.462, (6.101, 10.251, 3.199)), (' B  12  LEU HD11', ' B  18  ILE HD12', -0.451, (20.585, 31.717, 1.287)), (' A  10  LEU  HA ', ' B 169  LEU  HB3', -0.437, (17.281, 26.935, -8.65)), (' C  20  ASN  HA ', ' C 155  VAL  O  ', -0.429, (22.731, 17.076, 30.44)), (' D  20  ASN  HA ', ' D 155  VAL  O  ', -0.426, (25.988, 20.196, -34.847)), (' A  10  LEU HD13', ' A  12  LEU  CD2', -0.426, (14.452, 23.447, -5.476)), (' A 169  LEU  HB3', ' B  10  LEU  HA ', -0.425, (16.102, 25.716, 4.17)), (' B  20  ASN  HA ', ' B 155  VAL  O  ', -0.422, (15.527, 37.459, 5.872)), (' A  20  ASN  HA ', ' A 155  VAL  O  ', -0.421, (5.589, 27.356, -10.368)), (' B  10  LEU HD13', ' B  12  LEU  CD2', -0.421, (19.514, 28.67, 0.988)), (' D  46  GLY  O  ', ' D  51  GLY  HA3', -0.415, (26.434, 23.279, -17.225)), (' C 132  PHE  CZ ', ' C 201  APR H5R1', -0.414, (10.356, 19.533, 15.746)), (' A  46  GLY  O  ', ' A  51  GLY  HA3', -0.413, (-9.17, 18.712, -16.729)), (' B  46  GLY  O  ', ' B  51  GLY  HA3', -0.413, (23.987, 52.024, 12.572)), (' A  12  LEU  CD1', ' A  18  ILE  CG1', -0.409, (12.174, 21.256, -6.515)), (' D  15  ASN  HB2', ' D 149  THR  O  ', -0.409, (35.925, 34.771, -39.362)), (' C  15  ASN  HB2', ' C 149  THR  O  ', -0.402, (8.209, 7.086, 34.938)), (' A  12  LEU  CD1', ' A  18  ILE HG13', -0.401, (11.767, 21.011, -6.214)), (' C  46  GLY  O  ', ' C  51  GLY  HA3', -0.401, (19.691, 16.557, 12.861))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

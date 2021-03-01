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
data['rota'] = [('A', '  37 ', 'ASP', 0.08201013194493018, (-7.457000000000001, -18.64, 26.406)), ('A', '  61 ', 'ASP', 0.26059964345470926, (12.097000000000014, -28.743, 26.928)), ('A', ' 189 ', 'CYS', 0.11722643498399518, (27.069000000000003, 28.313, 25.264)), ('A', ' 236 ', 'GLN', 0.0, (18.974000000000004, 16.949, 11.782000000000004)), ('B', '   0 ', 'SER', 0.10945618453587067, (-2.319, -8.903, -9.807000000000002)), ('B', '  85 ', 'SER', 0.09563956811030312, (2.956, -42.615, -2.768)), ('B', ' 104 ', 'ILE', 0.11796762108217218, (-7.649000000000001, -56.183, 3.279)), ('B', ' 168 ', 'THR', 0.2727815259823199, (8.099, -58.677, 4.966000000000002)), ('B', ' 187 ', 'VAL', 0.17957316606954635, (24.02000000000002, -79.668, 16.138)), ('B', ' 210 ', 'THR', 0.18514232256622876, (11.060000000000002, -76.914, 8.439000000000002)), ('B', ' 294 ', 'SER', 0.1102674888800275, (-11.916, -78.949, 10.969))]
data['cbeta'] = []
data['probe'] = [(' A 283  TYR  HD2', ' A 290  LEU HD11', -0.597, (-13.425, 11.682, 16.861)), (' A 170  SER  O  ', ' A 174  GLN  HG2', -0.568, (11.119, 1.075, 24.03)), (' A 165  VAL  O  ', ' A 169  MET  HG2', -0.556, (3.243, 5.765, 25.741)), (' A  26  THR  OG1', ' A  29  GLN  HG3', -0.542, (-2.364, -32.187, 38.013)), (' B 224  CYS  SG ', ' B 225  THR  N  ', -0.506, (29.925, -81.101, 7.8)), (' B 147  PHE  CE2', ' B 151  ILE HD11', -0.493, (1.369, -53.869, 9.083)), (' A 158  THR HG22', ' A 159  VAL  O  ', -0.487, (-4.065, -5.176, 37.32)), (' B 117  LEU  O  ', ' B 121  GLN  HG3', -0.481, (-2.854, -58.055, 11.818)), (' A 147  PHE  CE2', ' A 151  ILE HD11', -0.447, (-0.254, -2.501, 21.57)), (' A 128  ASN  HB2', ' A 129  PRO  HD3', -0.447, (11.394, -6.905, 17.919)), (' B 185  LEU HD21', ' B 216  PHE  CZ ', -0.429, (16.516, -74.263, 15.713)), (' B 186  ASN  HB2', ' B 235  VAL  CG2', -0.428, (20.972, -77.828, 21.656)), (' B  13  ASN  HB2', ' B  56  TYR  OH ', -0.427, (0.96, -37.399, 9.243)), (' A 243  MET  HE3', ' A 304  PHE  CZ ', -0.424, (4.029, 9.395, 23.02)), (' A 276  ILE  N  ', ' A 276  ILE HD12', -0.422, (-6.446, 13.568, 22.584)), (' A 268  TYR  CD2', ' A 269  GLN  HG3', -0.417, (3.211, 9.418, 40.089)), (' B 207  TYR  HE2', ' B 210  THR HG22', -0.417, (14.043, -76.418, 9.74)), (' B  95  TYR  CD1', ' B 144  ALA  HB3', -0.413, (-6.357, -51.8, 6.444)), (' B 128  ASN  HB2', ' B 129  PRO  HD3', -0.407, (11.401, -49.456, 15.758)), (' B  89  HIS  HB2', ' B 159  VAL HG21', -0.404, (-0.428, -47.813, -3.09)), (' B 210  THR HG21', ' B 220  VAL HG11', -0.401, (13.34, -79.098, 11.063))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

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
data['probe'] = [(' D  98  THR  HB ', ' D 100E HIS  O  ', -0.987, (302.28, 314.918, 289.494)), (' D  83  LYS  HE2', ' D  85  GLU  HB2', -0.715, (321.986, 310.568, 267.385)), (' D  54  ASP  OD1', ' D  56  ARG  NH1', -0.666, (297.766, 318.684, 281.138)), (' D  90  TYR  O  ', ' D 106  GLY  HA3', -0.665, (310.043, 298.703, 273.336)), (' A 472  ILE HD12', ' A 488  CYS  HB3', -0.657, (313.58, 322.791, 287.959)), (' A 433  VAL HG12', ' A 512  VAL HG22', -0.615, (308.306, 303.938, 312.877)), (' A 393  THR  OG1', ' A 516  GLU  O  ', -0.578, (312.657, 311.02, 328.752)), (' D   7  THR  OG1', ' D  21  SER  OG ', -0.574, (301.19, 299.897, 267.691)), (' A 342  PHE  HZ ', ' A 513  LEU HD11', -0.555, (303.118, 303.065, 320.437)), (' A 365  TYR  HD2', ' A 387  LEU  HB3', -0.548, (305.805, 299.645, 327.999)), (' D  68  THR  HB ', ' D  81  GLN  HG3', -0.536, (304.065, 313.206, 264.522)), (' A 333  THR  N  ', ' A 362  VAL  O  ', -0.534, (298.072, 304.936, 333.576)), (' D  87  THR  HB ', ' D 110  THR  HA ', -0.534, (318.475, 302.037, 264.981)), (' D  38  ARG HH12', ' D  43  LYS  NZ ', -0.513, (321.371, 306.816, 272.273)), (' D  18  LEU HD12', ' D  82  MET  HE2', -0.498, (312.392, 306.54, 263.311)), (' A 344  ALA  HB3', ' A 347  PHE  HE1', -0.497, (294.642, 308.912, 313.783)), (' A 426  PRO  HD2', ' A 429  PHE  HB2', -0.495, (316.99, 306.367, 315.707)), (' D  34  ILE HG21', ' D  78  VAL HG21', -0.488, (301.668, 306.474, 276.288)), (' D  63  VAL HG23', ' D  67  PHE  HB2', -0.481, (310.025, 315.042, 269.259)), (' D  39  GLN  HB2', ' D  45  ARG  HE ', -0.475, (317.107, 301.369, 277.904)), (' D 100K ASP  N  ', ' D 100K ASP  OD1', -0.473, (312.341, 306.543, 288.572)), (' A 455  LEU HD12', ' D 100G THR HG21', -0.464, (309.064, 311.006, 290.976)), (' A 401  VAL HG22', ' A 509  ARG  HG2', -0.46, (298.318, 305.087, 307.981)), (' A 501  ASN  HB3', ' A 505  TYR  HB2', -0.46, (298.989, 297.077, 295.613)), (' A 393  THR HG22', ' A 522  ALA  HA ', -0.459, (311.89, 310.881, 333.379)), (' A 360  ASN  H  ', ' A 523  THR  HB ', -0.453, (305.508, 312.206, 332.752)), (' A 461  LEU  H  ', ' A 461  LEU HD23', -0.451, (318.385, 311.877, 305.046)), (' D 100I SER  OG ', ' D 100K ASP  OD1', -0.451, (311.104, 307.792, 288.81)), (' A 409  GLN  NE2', ' A 416  GLY  HA3', -0.45, (316.165, 301.216, 303.007)), (' D  38  ARG HH12', ' D  43  LYS  HZ3', -0.449, (321.279, 306.58, 272.016)), (' A 455  LEU HD11', ' A 493  GLN  HG2', -0.445, (307.887, 309.547, 292.224)), (' D  67  PHE  HD2', ' D  80  LEU HD11', -0.442, (308.745, 311.255, 268.635)), (' A 393  THR  O  ', ' A 523  THR  OG1', -0.441, (307.82, 311.504, 331.132)), (' D  90  TYR  O  ', ' D 106  GLY  CA ', -0.437, (309.549, 298.84, 273.342)), (' A 424  LYS  HB3', ' A 463  PRO  HA ', -0.435, (317.64, 310.321, 310.053)), (' D  53  SER  OG ', ' D  56  ARG  NH1', -0.433, (297.51, 318.001, 282.727)), (' D  63  VAL  O  ', ' D  66  ARG  HG2', -0.422, (312.648, 316.277, 266.661)), (' D  39  GLN  HB2', ' D  45  ARG  NE ', -0.419, (316.87, 301.46, 277.903)), (' A 376  THR  OG1', ' A 378  LYS  NZ ', -0.414, (307.567, 292.093, 312.454)), (' D  66  ARG  HD2', ' D  82A ASN  O  ', -0.413, (313.139, 313.637, 262.947)), (' A 392  PHE  HA ', ' A 517  LEU HD21', -0.406, (312.619, 306.781, 330.693)), (' D  98  THR  CB ', ' D 100E HIS  O  ', -0.406, (301.673, 314.5, 290.296))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

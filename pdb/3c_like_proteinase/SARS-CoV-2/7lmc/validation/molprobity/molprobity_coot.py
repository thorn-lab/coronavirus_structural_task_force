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
data['rama'] = [('A', '   2 ', 'GLY', 0.05155167824786864, (-4.912, -12.654, -5.510999999999998)), ('A', '  11 ', 'GLY', 0.07407565607180241, (7.228000000000001, 7.938999999999998, -8.434)), ('A', '  50 ', 'LEU', 0.04081097302891819, (-7.135999999999998, 29.544, 18.153)), ('A', ' 154 ', 'TYR', 0.0026829496880483522, (-1.6099999999999999, 7.107, -18.202)), ('A', ' 155 ', 'ASP', 0.027000209353411908, (1.108, 9.788, -17.41)), ('B', '  43 ', 'ILE', 0.034970744890217426, (13.112000000000002, -18.187, -22.994)), ('B', '  47 ', 'GLU', 0.0029413627347231693, (4.167000000000001, -25.33, -24.558999999999997)), ('B', '  52 ', 'PRO', 0.06703010404924725, (11.091000000000001, -27.238, -19.274999999999995)), ('B', '  63 ', 'ASN', 0.015564274440637274, (21.951, -12.069000000000003, -27.162)), ('C', ' 134 ', 'PHE', 0.0402721091262106, (-5.7770000000000055, 0.8289999999999962, 46.966)), ('C', ' 154 ', 'TYR', 0.01376238883584062, (-18.944000000000013, 0.3820000000000019, 24.167)), ('C', ' 283 ', 'GLY', 0.029734418674491284, (-12.363000000000007, 26.723000000000013, 38.521)), ('D', ' 240 ', 'GLU', 0.04387958914163248, (-27.721000000000007, 35.356, 46.379999999999995))]
data['omega'] = []
data['rota'] = [('E', '  -5 ', 'THR', 0.2580932140307716, (-4.335999999999997, -28.351, -11.033)), ('E', '   0 ', 'GLN', 0.08636624568292796, (3.4770000000000016, -15.918, -14.909999999999997)), ('A', '   1 ', 'SER', 0.05725627628304957, (-5.012999999999997, -14.579999999999993, -8.883999999999999)), ('A', '   4 ', 'ARG', 0.1736743184470682, (-4.967, -6.746, -2.408)), ('A', '   5 ', 'LYS', 0.0, (-5.097999999999996, -2.951999999999999, -1.7949999999999993)), ('A', '  25 ', 'THR', 0.19560977933884127, (6.208999999999999, 25.551999999999985, 11.546)), ('A', '  44 ', 'CYS', 0.1776050463298242, (0.6120000000000001, 30.038, 12.322)), ('A', '  45 ', 'THR', 0.013070097871576626, (1.7780000000000014, 28.841999999999995, 15.754999999999999)), ('A', '  55 ', 'GLU', 0.09086699276682475, (-5.743000000000006, 37.499, 5.737999999999998)), ('A', '  64 ', 'HIS', 0.28020027276104525, (11.797000000000002, 35.81799999999997, 2.764)), ('A', '  67 ', 'LEU', 0.2709239962434211, (12.143000000000006, 28.767, 3.579)), ('A', '  87 ', 'LEU', 0.003976399474969191, (-0.9930000000000125, 28.882, 0.30599999999999994)), ('A', ' 102 ', 'LYS', 0.022796881168348104, (-4.7769999999999975, 17.753, -12.835)), ('A', ' 106 ', 'ILE', 0.21925585306909412, (-13.269, 13.312, -5.8329999999999975)), ('A', ' 155 ', 'ASP', 0.005208615364730805, (1.108, 9.788, -17.41)), ('A', ' 169 ', 'THR', 0.013749134954561443, (-11.453, 10.116, 16.569)), ('A', ' 188 ', 'ARG', 0.23653064300826432, (-9.245000000000003, 26.488, 13.196999999999996)), ('A', ' 190 ', 'THR', 0.18367443562801333, (-12.681999999999997, 25.043, 17.098)), ('A', ' 192 ', 'GLN', 0.05864642379306489, (-14.974000000000004, 20.055, 15.197999999999999)), ('A', ' 197 ', 'ASP', 0.16871056770245318, (-19.745000000000015, 7.146, 9.391)), ('A', ' 227 ', 'LEU', 0.10639580764477925, (-33.68599999999999, -2.130999999999999, -5.283999999999998)), ('A', ' 228 ', 'ASN', 0.16662100759842555, (-35.78, -0.29000000000000004, -2.687)), ('A', ' 288 ', 'GLU', 0.23190536092457542, (-14.595, -4.027, 3.242)), ('A', ' 297 ', 'VAL', 0.13590549085779802, (-11.905, -4.789000000000002, -12.502999999999998)), ('A', ' 299 ', 'GLN', 0.0856087885280164, (-7.307999999999999, -6.9030000000000005, -10.613999999999999)), ('B', '  35 ', 'VAL', 0.2232030646291719, (22.725, -5.714, -15.936999999999998)), ('B', '  47 ', 'GLU', 0.044284621553479966, (4.167000000000001, -25.33, -24.558999999999997)), ('B', '  49 ', 'MET', 0.00043569197108975883, (6.211000000000001, -24.339, -19.409)), ('B', '  55 ', 'GLU', 0.2667923623660431, (19.919, -25.59, -18.791)), ('B', '  58 ', 'LEU', 0.0276943235108542, (19.733000000000015, -20.804, -22.74599999999999)), ('B', '  67 ', 'LEU', 0.11317611076935959, (14.147000000000014, -7.645, -26.747)), ('B', '  69 ', 'GLN', 0.04117953069802352, (12.825000000000006, -1.9230000000000023, -23.792999999999992)), ('B', '  73 ', 'VAL', 0.003150532575091347, (14.122, 2.979, -26.385)), ('B', '  74 ', 'GLN', 0.0021078482327957964, (15.194000000000008, -0.6300000000000017, -27.051999999999992)), ('B', '  87 ', 'LEU', 0.085042333658733, (18.555, -14.372999999999992, -16.546)), ('B', ' 107 ', 'GLN', 0.016275308777423524, (13.567999999999996, -15.042000000000002, 6.338)), ('B', ' 128 ', 'CYS', 0.07322877645492554, (3.804000000000004, -8.242, 1.391)), ('B', ' 154 ', 'TYR', 0.1503925967110398, (18.148000000000014, 5.143, 4.25)), ('B', ' 158 ', 'SER', 0.26202993945052744, (17.429999999999986, -3.6230000000000007, -0.806)), ('B', ' 216 ', 'ASP', 0.21630030970920402, (-6.536000000000002, 0.6420000000000026, 21.288)), ('B', ' 224 ', 'THR', 0.06656628266222261, (1.9899999999999995, -12.696, 32.909)), ('B', ' 227 ', 'LEU', 0.10896966802504617, (8.202999999999998, -17.506999999999998, 27.47)), ('B', ' 228 ', 'ASN', 0.04811200411684064, (7.849000000000005, -21.310999999999993, 27.192999999999994)), ('B', ' 232 ', 'LEU', 0.16051486150922897, (2.625000000000006, -23.846, 24.978999999999992)), ('F', '   0 ', 'GLN', 0.06409609685375493, (-25.772000000000006, 22.028000000000013, 18.978)), ('C', '   1 ', 'SER', 0.11112351175995891, (-16.877000000000013, 22.576, 25.149999999999995)), ('C', '   4 ', 'ARG', 0.18420033346129447, (-17.285, 17.915, 33.99)), ('C', '  16 ', 'CYS', 0.20238733799945244, (-29.067, -6.618000000000002, 37.916999999999994)), ('C', '  19 ', 'GLN', 0.09432480093994745, (-30.937000000000012, -7.349999999999989, 48.024)), ('C', '  22 ', 'CYS', 0.16712690641038735, (-28.66200000000001, -13.509000000000004, 56.24899999999998)), ('C', '  35 ', 'VAL', 0.2766927795006133, (-25.788000000000004, -16.28199999999999, 40.00599999999999)), ('C', '  48 ', 'ASP', 0.22430925670234753, (-18.611000000000004, -12.104, 65.199)), ('C', '  58 ', 'LEU', 0.05825127586542499, (-20.851, -20.921, 55.54499999999998)), ('C', '  60 ', 'ARG', 0.13549609289823766, (-23.736000000000015, -23.609000000000005, 59.37099999999999)), ('C', '  62 ', 'SER', 0.19909188898445726, (-28.541, -23.036, 54.902)), ('C', '  64 ', 'HIS', 0.0, (-33.223, -20.552, 53.725)), ('C', '  73 ', 'VAL', 0.10210730061180379, (-40.065000000000005, -10.701, 43.84)), ('C', '  80 ', 'HIS', 0.1348140422705707, (-24.27, -21.155, 47.685)), ('C', '  84 ', 'ASN', 0.05430535339159351, (-12.403, -15.52399999999999, 48.45599999999999)), ('C', '  87 ', 'LEU', 0.05940383004241459, (-20.648, -15.248, 48.153)), ('C', '  89 ', 'LEU', 0.07916702945135788, (-25.561000000000003, -17.793, 45.245)), ('C', '  90 ', 'LYS', 0.25563489793630684, (-27.176000000000002, -19.857999999999997, 42.472)), ('C', ' 106 ', 'ILE', 0.009662060793965529, (-8.657999999999998, -1.967999999999999, 38.048)), ('C', ' 110 ', 'GLN', 0.252213035799255, (-7.954, 4.189000000000002, 36.656)), ('C', ' 114 ', 'VAL', 0.02961037995197722, (-19.950000000000014, 3.7720000000000016, 41.223)), ('C', ' 128 ', 'CYS', 0.06666950271502389, (-14.285000000000007, 8.107, 41.55399999999999)), ('C', ' 162 ', 'MET', 0.24717433562456828, (-17.396000000000004, -4.500999999999992, 44.715)), ('C', ' 177 ', 'LEU', 0.22679384726758053, (-15.593000000000002, -8.904000000000002, 40.976)), ('C', ' 192 ', 'GLN', 0.0019004257092778978, (-6.382000000000002, -1.610000000000003, 59.39899999999999)), ('C', ' 217 ', 'ARG', 0.0945359838083648, (-2.375, 29.487, 30.141)), ('C', ' 225 ', 'THR', 0.2431530965656071, (12.63, 18.925, 31.873999999999995)), ('C', ' 248 ', 'ASP', 0.09720596185658673, (2.241999999999998, 7.623, 25.411)), ('C', ' 269 ', 'LYS', 0.07460497740392462, (7.131, 21.344, 38.484)), ('C', ' 280 ', 'THR', 0.010776753596461857, (-7.848000000000004, 28.984000000000005, 39.563)), ('C', ' 286 ', 'LEU', 0.17873764386924532, (-6.357000000000008, 22.836, 43.73499999999999)), ('C', ' 288 ', 'GLU', 0.22163357519152854, (-7.6270000000000024, 17.744, 40.19599999999999)), ('C', ' 289 ', 'ASP', 0.10452524969078994, (-5.910000000000005, 14.355999999999998, 40.40899999999999)), ('C', ' 291 ', 'PHE', 0.15728436538297563, (-9.294000000000002, 13.559, 35.51499999999999)), ('C', ' 292 ', 'THR', 0.149422253999703, (-7.828, 10.722000000000001, 33.342)), ('C', ' 297 ', 'VAL', 0.22908336678439914, (-9.922000000000002, 13.384, 25.33)), ('D', '   6 ', 'MET', 0.22581158918307723, (-24.026, 12.442999999999998, 43.029)), ('D', '  10 ', 'SER', 0.0891556690252667, (-30.13500000000003, 7.185, 34.523)), ('D', '  12 ', 'LYS', 0.14110909604778366, (-35.549, 5.488000000000004, 33.455)), ('D', '  35 ', 'VAL', 0.15026096637034658, (-44.64600000000005, 11.239, 21.334)), ('D', '  48 ', 'ASP', 0.27597349268577503, (-30.254000000000005, 28.269, 8.381)), ('D', '  50 ', 'LEU', 0.20271301465799632, (-28.06800000000003, 32.461, 11.413)), ('D', '  56 ', 'ASP', 0.06308699018862808, (-41.46100000000002, 28.853999999999985, 7.997999999999999)), ('D', '  73 ', 'VAL', 0.14005025309262387, (-36.363, 0.07300000000000173, 15.319)), ('D', '  78 ', 'ILE', 0.06707832900734789, (-47.655, 10.137, 12.207)), ('D', '  87 ', 'LEU', 0.11115861103657443, (-40.79299999999999, 19.967, 18.344999999999995)), ('D', ' 104 ', 'VAL', 0.16910966825064158, (-41.62200000000003, 20.708999999999996, 35.87199999999999)), ('D', ' 107 ', 'GLN', 0.031011311962489945, (-36.403999999999975, 27.811, 39.838)), ('D', ' 121 ', 'SER', 0.03196377093000234, (-27.210000000000015, 7.019999999999996, 22.508)), ('D', ' 128 ', 'CYS', 0.21845483909350294, (-25.976000000000006, 20.395999999999987, 37.132)), ('D', ' 142 ', 'ASN', 0.05186178827168732, (-22.398000000000003, 19.713, 18.724)), ('D', ' 158 ', 'SER', 0.23439371280623214, (-39.40900000000003, 14.882, 36.717)), ('D', ' 165 ', 'MET', 0.011409456196723244, (-26.848000000000024, 25.563000000000002, 22.525)), ('D', ' 186 ', 'VAL', 0.00206597036489774, (-33.011, 31.958, 21.959999999999997)), ('D', ' 188 ', 'ARG', 0.2429099152400351, (-30.57600000000002, 32.09299999999999, 16.919999999999998)), ('D', ' 200 ', 'ILE', 0.040787821276519684, (-26.55, 30.638, 45.476)), ('D', ' 204 ', 'VAL', 0.19992909386132418, (-23.628, 26.759, 50.128999999999984)), ('D', ' 222 ', 'ARG', 0.0, (-19.879000000000005, 30.985999999999997, 69.082)), ('D', ' 224 ', 'THR', 0.0013599335943581536, (-25.54700000000002, 33.753, 66.09599999999999)), ('D', ' 225 ', 'THR', 0.022978595025785743, (-26.663999999999998, 36.193, 63.34999999999999)), ('D', ' 227 ', 'LEU', 0.09647888464540828, (-31.301, 37.922, 58.035)), ('D', ' 233 ', 'VAL', 0.008634153141715556, (-20.626, 40.447, 52.901)), ('D', ' 242 ', 'LEU', 0.013341534170034197, (-30.810999999999996, 35.067000000000014, 52.103)), ('D', ' 243 ', 'THR', 0.16320843987561157, (-34.613, 34.675, 51.577)), ('D', ' 245 ', 'ASP', 0.15592901598351291, (-38.160000000000025, 30.692999999999998, 52.74999999999999)), ('D', ' 263 ', 'ASP', 0.014121808348039269, (-25.974000000000032, 29.874999999999986, 63.728)), ('D', ' 271 ', 'LEU', 0.07511929362960312, (-15.178, 32.06, 56.298)), ('D', ' 284 ', 'SER', 0.09602768272861262, (-12.358, 21.572, 48.746)), ('D', ' 286 ', 'LEU', 0.008442200114921231, (-13.720000000000006, 26.61199999999999, 47.21499999999998)), ('D', ' 304 ', 'THR', 0.0241826141868183, (-32.798999999999985, 5.048, 47.322))]
data['cbeta'] = [('A', '  27 ', 'LEU', ' ', 0.2565141835150243, (3.502999999999996, 21.437, 6.744999999999998)), ('D', ' 186 ', 'VAL', ' ', 0.2594479548491002, (-33.99699999999999, 32.91, 21.227)), ('D', ' 224 ', 'THR', ' ', 0.2607390780592646, (-26.60299999999999, 33.07600000000001, 67.035)), ('D', ' 233 ', 'VAL', ' ', 0.25338351352769417, (-19.46800000000001, 39.70700000000001, 53.61599999999999))]
data['probe'] = [(' D  51  ASN  HB2', ' D 188  ARG  HE ', -0.816, (-31.19, 36.042, 12.423)), (' B  84  ASN  ND2', ' B 180  ASN  ND2', -0.808, (19.797, -19.672, -6.7)), (' B  58  LEU HD13', ' B  82  MET  HB2', -0.805, (21.096, -18.829, -18.868)), (' C  40  ARG  HD3', ' C  85  CYS  HA ', -0.735, (-15.222, -13.342, 50.684)), (' C 285  ALA  H  ', ' D 286  LEU HD11', -0.727, (-10.758, 26.119, 43.801)), (' D  51  ASN  CB ', ' D 188  ARG  HE ', -0.726, (-31.19, 35.197, 12.386)), (' A 166  GLU  OE2', ' B   1  SER  HB3', -0.721, (-3.959, 10.227, 14.971)), (' C 146  GLY  HA2', ' C 162  MET  HE2', -0.716, (-21.464, -5.728, 45.76)), (' C 213  ILE HG21', ' C 300  CYS  HB3', -0.714, (-10.206, 19.816, 24.69)), (' A 188  ARG  HB3', ' A 190  THR HG22', -0.692, (-12.003, 26.507, 13.66)), (' B  41  HIS  CG ', ' E  -1  LEU HD12', -0.685, (7.775, -19.034, -16.267)), (' D 100  LYS  O  ', ' D 156  CYS  HA ', -0.676, (-41.637, 8.836, 37.405)), (' A  58  LEU HD11', ' A  80  HIS  HD2', -0.672, (1.358, 34.413, 1.852)), (' B  21  THR  HB ', ' B  67  LEU  HB3', -0.666, (11.222, -8.425, -26.844)), (' C 109  GLY  HA2', ' C 200  ILE HD13', -0.65, (-5.571, 7.525, 39.52)), (' D  41  HIS  CG ', ' F  -1  LEU HD12', -0.65, (-30.38, 24.15, 17.454)), (' B  84  ASN  ND2', ' B 180  ASN HD21', -0.649, (21.058, -19.781, -6.225)), (' A  87  LEU HD13', ' A  89  LEU HD21', -0.634, (3.142, 30.249, 0.799)), (' C 163  HIS  HE1', ' C 172  HIS  HB3', -0.621, (-16.174, 1.562, 50.285)), (' D  45  THR  H  ', ' D  48  ASP  HB2', -0.613, (-30.141, 25.047, 8.483)), (' C  58  LEU HD13', ' C  82  MET  HE2', -0.602, (-18.342, -20.269, 51.584)), (' B 243  THR HG23', ' B 246  HIS  CE1', -0.597, (12.043, -17.129, 16.953)), (' B 111  THR HG22', ' B 129  ALA  HB2', -0.592, (5.097, -9.172, 5.272)), (' C 233  VAL HG21', ' C 269  LYS  HD3', -0.585, (11.352, 19.156, 39.524)), (' B 108  PRO  HB2', ' B 132  PRO  HA ', -0.584, (7.968, -17.802, 7.215)), (' D  40  ARG  HD3', ' D  85  CYS  HA ', -0.58, (-38.789, 26.245, 18.892)), (' B  57  LEU  O  ', ' B  61  LYS  HG2', -0.578, (17.614, -21.183, -26.088)), (' B  84  ASN HD22', ' B 180  ASN  ND2', -0.576, (19.873, -19.219, -7.064)), (' B   9  PRO  HD2', ' B 152  ILE HD12', -0.575, (10.254, 3.347, -0.211)), (' A 113  SER  O  ', ' A 149  GLY  HA2', -0.574, (-3.125, 10.204, -2.802)), (' B  36  VAL  HB ', ' B  89  LEU  HB2', -0.574, (18.911, -7.562, -19.209)), (' C 166  GLU  OE2', ' D   1  SER  HB3', -0.573, (-16.802, 7.854, 55.582)), (' A 161  TYR  OH ', ' A 163  HIS  ND1', -0.569, (-5.365, 14.09, 5.412)), (' B  40  ARG  HD3', ' B  85  CYS  HA ', -0.564, (16.115, -19.708, -13.997)), (' D  51  ASN  HB2', ' D 188  ARG  NE ', -0.557, (-30.848, 36.043, 13.04)), (' C  20  VAL HG22', ' C  68  VAL HG22', -0.557, (-28.977, -11.891, 47.874)), (' D 142  ASN  HA ', ' F   0  GLN  HB3', -0.556, (-23.274, 21.039, 19.066)), (' A 111  THR HG22', ' A 129  ALA  HB2', -0.555, (-11.744, 4.257, -0.916)), (' C  20  VAL HG12', ' C  42  VAL HG21', -0.554, (-26.605, -11.073, 52.328)), (' D 222  ARG  H  ', ' D 222  ARG  HE ', -0.553, (-17.729, 30.546, 67.803)), (' D  41  HIS  CD2', ' F  -1  LEU HD12', -0.551, (-30.466, 24.918, 17.891)), (' A  44  CYS  HB3', ' A  48  ASP  HB2', -0.547, (-1.495, 30.976, 14.044)), (' D 168  PRO  HB3', ' F  -5  THR  HB ', -0.547, (-19.309, 34.235, 21.827)), (' C 207  TRP  NE1', ' C 282  LEU HD12', -0.544, (-9.557, 20.88, 35.082)), (' B 175  THR  HA ', ' B 181  PHE  HA ', -0.539, (13.214, -17.933, -5.591)), (' A  58  LEU HD11', ' A  80  HIS  CD2', -0.537, (1.898, 34.721, 1.644)), (' B 243  THR HG23', ' B 246  HIS  ND1', -0.536, (11.497, -16.507, 17.198)), (' D 142  ASN  HA ', ' F   0  GLN  CB ', -0.536, (-23.968, 21.177, 19.136)), (' C 118  TYR  CE1', ' C 144  SER  HB3', -0.534, (-25.178, 2.444, 50.996)), (' B  64  HIS  CD2', ' B  65  ASN  ND2', -0.531, (18.409, -14.333, -32.031)), (' C 102  LYS  HG2', ' C 104  VAL HG23', -0.529, (-13.612, -7.241, 31.853)), (' C 201  THR HG22', ' C 242  LEU HD13', -0.528, (2.787, 12.085, 35.227)), (' D 186  VAL  H  ', ' D 192  GLN  NE2', -0.524, (-31.122, 33.0, 22.429)), (' C  70  ALA  HB2', ' C  75  LEU HD11', -0.524, (-33.95, -11.415, 42.009)), (' B  40  ARG  O  ', ' B  43  ILE HG12', -0.522, (13.944, -18.368, -19.861)), (' D 188  ARG  HB3', ' D 190  THR HG22', -0.521, (-30.122, 34.34, 17.653)), (' D  43  ILE HG22', ' D  66  PHE  HE1', -0.519, (-37.834, 19.282, 11.315)), (' D 271  LEU HD11', ' D 281  ILE HD11', -0.517, (-15.534, 26.74, 55.084)), (' B  14  GLU  HG2', ' B 122  PRO  HG2', -0.515, (7.084, 2.565, -11.607)), (' B 279  ARG HH22', ' C 102  LYS  NZ ', -0.514, (-15.154, -7.772, 25.693)), (' B  85  CYS  HB2', ' B 175  THR HG21', -0.514, (14.172, -18.474, -9.546)), (' D 276  MET  CE ', ' D 281  ILE HG13', -0.513, (-13.506, 24.535, 53.589)), (' B 165  MET  HE1', ' B 185  PHE  HB3', -0.513, (8.047, -23.482, -7.011)), (' B  41  HIS  CD2', ' E  -1  LEU HD12', -0.508, (8.016, -18.024, -15.607)), (' C  85  CYS  HB2', ' C 175  THR HG21', -0.506, (-13.853, -9.584, 48.625)), (' C  10  SER  HB2', ' C 115  LEU HD13', -0.503, (-26.05, 3.514, 38.453)), (' D 276  MET  HE3', ' D 281  ILE HG13', -0.498, (-13.488, 24.842, 53.99)), (' D 164  HIS  CD2', ' D 175  THR HG23', -0.494, (-34.49, 24.883, 24.392)), (' A 126  TYR  CE1', ' B   6  MET  HE2', -0.491, (0.868, 6.237, 5.278)), (' C   2  GLY  HA3', ' D 139  SER  HA ', -0.491, (-18.962, 21.515, 28.902)), (' C   3  PHE  HE1', ' C 300  CYS  HG ', -0.491, (-11.644, 17.816, 28.719)), (' B 206  ALA  HB2', ' B 293  PRO  HG3', -0.49, (6.944, -6.662, 16.103)), (' B 222  ARG  HG2', ' C 107  GLN HE21', -0.489, (-3.08, -4.563, 35.96)), (' C  21  THR  HB ', ' C  67  LEU  HB2', -0.489, (-32.846, -12.503, 53.373)), (' C 100  LYS  HB2', ' C 156  CYS  HA ', -0.488, (-21.444, -6.126, 27.477)), (' A 245  ASP  O  ', ' A 249  ILE HG13', -0.488, (-23.02, 2.898, -11.838)), (' D 205  LEU HD23', ' D 208  LEU HD12', -0.488, (-24.181, 28.077, 55.336)), (' D 204  VAL HG22', ' D 289  ASP  HB3', -0.483, (-22.686, 28.212, 46.774)), (' D 222  ARG  H  ', ' D 222  ARG  NE ', -0.482, (-17.222, 31.059, 68.195)), (' D 131  ARG  HG2', ' D 135  THR  O  ', -0.482, (-26.347, 28.103, 34.82)), (' C  53  ASN  OD1', ' C  55  GLU  OE1', -0.48, (-13.374, -20.106, 58.424)), (' D 152  ILE HG22', ' D 153  ASP  N  ', -0.48, (-37.951, 9.792, 41.95)), (' D 205  LEU  O  ', ' D 208  LEU  HB2', -0.479, (-24.243, 24.646, 54.854)), (' B  44  CYS  HB3', ' B  48  ASP  HB2', -0.479, (8.758, -22.358, -22.875)), (' C 132  PRO  HG2', ' C 198  THR  O  ', -0.474, (-1.888, 8.728, 44.897)), (' C  44  CYS  SG ', ' C  54  TYR  CE2', -0.474, (-18.445, -12.506, 57.506)), (' B  84  ASN HD21', ' B 180  ASN HD21', -0.473, (21.45, -19.638, -6.741)), (' C 207  TRP  HZ3', ' C 287  LEU HD23', -0.473, (-4.022, 21.632, 38.537)), (' C 106  ILE HG12', ' C 160  CYS  HB2', -0.471, (-11.476, -2.315, 38.933)), (' B 108  PRO  CB ', ' B 132  PRO  HA ', -0.471, (8.307, -18.128, 6.696)), (' A  95  ASN  HB3', ' A  98  THR  OG1', -0.467, (7.437, 20.737, -11.894)), (' D 168  PRO  CB ', ' F  -5  THR  HB ', -0.465, (-19.223, 34.349, 22.038)), (' D 111  THR HG23', ' D 292  THR HG23', -0.462, (-29.722, 21.792, 43.94)), (' B 167  LEU  HB3', ' B 168  PRO  HD2', -0.462, (0.195, -23.277, -5.761)), (' B  60  ARG  HG3', ' B  61  LYS  HE3', -0.461, (17.29, -22.691, -27.799)), (' C  27  LEU HD13', ' C  39  PRO  HD2', -0.46, (-23.469, -7.74, 49.945)), (' A 163  HIS  HE1', ' A 172  HIS  HB3', -0.46, (-5.884, 13.675, 7.892)), (' D 138  GLY  O  ', ' D 172  HIS  HE1', -0.458, (-20.985, 22.616, 29.498)), (' B  81  SER  HB3', ' B  88  LYS  HB2', -0.458, (23.434, -13.269, -16.645)), (' C 105  ARG HH11', ' C 176  ASP  HB3', -0.455, (-9.453, -7.512, 42.327)), (' B 217  ARG  HB3', ' B 220  LEU HD12', -0.453, (-4.46, -0.689, 26.536)), (' D  30  LEU HD22', ' D 148  VAL HG11', -0.451, (-36.383, 14.459, 27.823)), (' D  39  PRO  HG2', ' D 145  ALA  HB1', -0.451, (-31.115, 20.318, 20.718)), (' A 166  GLU  OE1', ' A 172  HIS  NE2', -0.45, (-4.772, 11.545, 11.817)), (' D  41  HIS  CD2', ' F  -1  LEU  CD1', -0.446, (-30.616, 25.091, 18.149)), (' A 164  HIS  O  ', ' C 305  PHE  O  ', -0.446, (-2.719, 19.323, 10.199)), (' C   3  PHE  CE1', ' C 300  CYS  SG ', -0.445, (-11.813, 18.798, 28.479)), (' C  40  ARG  CD ', ' C  85  CYS  HA ', -0.444, (-14.919, -13.479, 51.689)), (' A  84  ASN  HB2', ' A 179  GLY  HA3', -0.444, (-8.553, 26.511, -1.146)), (' B 210  ALA  HB2', ' B 296  VAL HG13', -0.442, (3.222, -0.564, 15.24)), (' B 270  GLU  OE1', ' B 273  GLN  OE1', -0.441, (-5.862, -17.638, 27.923)), (' B 163  HIS  HE1', ' B 172  HIS  HB3', -0.44, (3.605, -15.054, -6.843)), (' A 163  HIS  CE1', ' A 172  HIS  HB3', -0.439, (-5.534, 13.975, 7.717)), (' A  91  VAL HG23', ' A  93  THR  H  ', -0.438, (10.484, 28.437, -8.719)), (' D 269  LYS  HA ', ' D 272  LEU HD12', -0.437, (-19.69, 35.295, 55.512)), (' D  17  MET  HG3', ' D 117  CYS  SG ', -0.437, (-30.379, 10.175, 26.453)), (' D  51  ASN  HB2', ' D 188  ARG HH21', -0.437, (-30.123, 36.386, 12.067)), (' D 249  ILE HG22', ' D 293  PRO  HG2', -0.436, (-33.741, 23.652, 51.171)), (' D 165  MET  HE2', ' D 173  ALA  HB3', -0.434, (-28.877, 29.193, 24.804)), (' D  53  ASN  HB3', ' D  56  ASP  HB2', -0.433, (-39.665, 30.933, 8.559)), (' D 212  VAL HG21', ' D 264  MET  HE1', -0.433, (-22.865, 22.901, 60.302)), (' D 163  HIS  HE1', ' D 172  HIS  HB3', -0.432, (-25.787, 24.304, 26.942)), (' B 198  THR  HA ', ' B 238  ASN  OD1', -0.432, (0.023, -21.051, 11.083)), (' B 249  ILE HG22', ' B 293  PRO  HG2', -0.431, (10.44, -7.306, 16.235)), (' D  12  LYS  NZ ', ' D  99  PRO  HB3', -0.431, (-39.559, 5.234, 34.851)), (' C 185  PHE  HD1', ' C 192  GLN  HG2', -0.427, (-7.05, -2.414, 55.729)), (' D 294  PHE  O  ', ' D 298  ARG  HB2', -0.426, (-31.171, 14.897, 48.699)), (' B  52  PRO  HD3', ' B 188  ARG  HG3', -0.426, (8.371, -27.806, -16.449)), (' A 164  HIS  CD2', ' A 175  THR HG23', -0.426, (-7.073, 21.151, 3.575)), (' C 234  ALA  O  ', ' C 239  TYR  HB2', -0.425, (5.419, 13.441, 43.489)), (' A   8  PHE  HB3', ' A 152  ILE HD12', -0.425, (0.231, 6.135, -9.578)), (' B  95  ASN  HB3', ' B  98  THR  OG1', -0.424, (20.704, 1.589, -13.803)), (' A 262  LEU  HA ', ' A 265  CYS  HB2', -0.424, (-29.252, -7.139, -5.638)), (' C 117  CYS  HA ', ' C 122  PRO  HA ', -0.424, (-28.601, 1.993, 45.083)), (' B  84  ASN  ND2', ' B 180  ASN HD22', -0.424, (19.858, -19.929, -6.711)), (' D  54  TYR  HA ', ' D  57  LEU HD12', -0.421, (-37.713, 27.388, 11.253)), (' B 279  ARG  NH2', ' C 102  LYS  NZ ', -0.418, (-14.838, -7.749, 25.757)), (' B  31  TRP  CD2', ' B  95  ASN  HB2', -0.418, (19.185, 0.828, -16.444)), (' C 101  TYR  O  ', ' C 156  CYS  SG ', -0.418, (-18.635, -8.258, 29.773)), (' D  10  SER  O  ', ' D  14  GLU  HG3', -0.417, (-30.672, 6.315, 31.724)), (' C 111  THR HG22', ' C 129  ALA  HB2', -0.417, (-9.853, 8.392, 39.281)), (' C 140  PHE  HB2', ' C 172  HIS  CD2', -0.416, (-17.985, 4.304, 51.607)), (' A 109  GLY  HA2', ' A 200  ILE HD13', -0.415, (-16.672, 5.036, -0.462)), (' D 188  ARG HH11', ' D 190  THR  HB ', -0.414, (-29.197, 37.068, 16.637)), (' C 294  PHE  O  ', ' C 298  ARG  HB2', -0.414, (-12.401, 10.483, 27.389)), (' B 209  TYR  HB3', ' B 253  LEU HD22', -0.413, (5.286, -1.366, 19.522)), (' B 165  MET  CE ', ' B 185  PHE  HB3', -0.413, (7.488, -22.962, -7.051)), (' D 299  GLN  HB2', ' D 299  GLN HE21', -0.412, (-26.173, 13.308, 47.861)), (' B 140  PHE  HB3', ' B 144  SER  OG ', -0.412, (1.975, -11.573, -11.343)), (' D  27  LEU HD13', ' D  39  PRO  HD2', -0.411, (-32.814, 17.848, 19.355)), (' A 167  LEU  HB3', ' A 168  PRO  HD2', -0.41, (-12.053, 14.941, 14.955)), (' D 186  VAL  H  ', ' D 192  GLN HE22', -0.409, (-31.31, 33.261, 22.526)), (' C  52  PRO  HD3', ' C 188  ARG  HG3', -0.409, (-11.498, -10.876, 61.916)), (' A  27  LEU  HB2', ' A 145  ALA  O  ', -0.408, (2.522, 19.781, 5.759)), (' B 189  GLN  HG3', ' E  -1  LEU HD23', -0.407, (4.822, -23.305, -15.711)), (' A 216  ASP  O  ', ' A 217  ARG  HG3', -0.407, (-17.173, -17.299, -4.102)), (' D 161  TYR  CE1', ' D 174  GLY  HA3', -0.406, (-31.235, 23.884, 28.813)), (' B 233  VAL HG21', ' B 269  LYS  HD3', -0.402, (-1.609, -19.808, 27.482)), (' D  47  GLU  HG2', ' D  50  LEU HD12', -0.401, (-25.84, 31.614, 7.359))]
handle_read_draw_probe_dots_unformatted("molprobity_probe.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

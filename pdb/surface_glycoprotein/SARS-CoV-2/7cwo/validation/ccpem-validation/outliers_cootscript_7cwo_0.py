
from __future__ import division
import cPickle
try :
  import gobject
except ImportError :
  gobject = None
import sys

dict_residue_prop_objects = {}
class coot_extension_gui (object) :
  def __init__ (self, title) :
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

  def finish_window (self) :
    import gtk
    self.outside_vbox.set_border_width(2)
    ok_button = gtk.Button("  Close  ")
    self.outside_vbox.pack_end(ok_button, False, False, 0)
    ok_button.connect("clicked", lambda b: self.destroy_window())
    self.window.connect("delete_event", lambda a, b: self.destroy_window())
    self.window.show_all()

  def destroy_window (self, *args) :
    self.window.destroy()
    self.window = None

  def confirm_data (self, data) :
    for data_key in self.data_keys :
      outlier_list = data.get(data_key)
      if outlier_list is not None and len(outlier_list) > 0 :
        return True
    return False

  def create_property_lists (self, data) :
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
        ##save property list frame object
        dict_residue_prop_objects[data_key] = list_obj
# Molprobity result viewer
class coot_molprobity_todo_list_gui (coot_extension_gui) :
  data_keys = [ "clusters","rama", "rota", "cbeta", "probe", "smoc", "cablam",
               "jpred"]
  data_titles = { "clusters"  : "Outlier residue clusters",
                  "rama"  : "Ramachandran outliers",
                  "rota"  : "Rotamer outliers",
                  "cbeta" : "C-beta outliers",
                  "probe" : "Severe clashes",
                  "smoc"  : "Local density fit (SMOC)",
                  "cablam": "Ca geometry (CaBLAM)",
                  "jpred":"SS prediction"}
  data_names = { "clusters"  : ["Chain","Residue","Cluster","Outlier types"],
                 "rama"  : ["Chain", "Residue", "Name", "Score"],
                 "rota"  : ["Chain", "Residue", "Name", "Score"],
                 "cbeta" : ["Chain", "Residue", "Name", "Conf.", "Deviation"],
                 "probe" : ["Atom 1", "Atom 2", "Overlap"],
                 "smoc" : ["Chain", "Residue", "Name", "Score"],
                 "cablam" : ["Chain", "Residue","Name","recommendation","DSSP"],
                 "jpred" : ["Chain", "Residue","Name","predicted SS","current SS"]}
  if (gobject is not None) :
    data_types = {  "clusters" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_INT, gobject.TYPE_STRING,
                             gobject.TYPE_PYOBJECT],
                    "rama" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "rota" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                             gobject.TYPE_STRING, gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cbeta" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "probe" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_FLOAT, gobject.TYPE_PYOBJECT],
                   "smoc" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_FLOAT,
                             gobject.TYPE_PYOBJECT],
                   "cablam" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT],
                   "jpred" : [gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING,gobject.TYPE_STRING,
                             gobject.TYPE_STRING,gobject.TYPE_PYOBJECT]}
  else :
    data_types = dict([ (s, []) for s in ["clusters","rama","rota","cbeta","probe","smoc",
                                          "cablam","jpred"] ])

  def __init__ (self, data_file=None, data=None) :
    assert ([data, data_file].count(None) == 1)
    if (data is None) :
      data = load_pkl(data_file)
    if not self.confirm_data(data) :
      return
    coot_extension_gui.__init__(self, "MolProbity to-do list")
    self.dots_btn = None
    self.dots2_btn = None
    self._overlaps_only = True
    self.window.set_default_size(420, 600)
    self.create_property_lists(data)
    self.finish_window()

  def add_top_widgets (self, data_key, box) :
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

  def toggle_probe_dots (self, *args) :
    if self.dots_btn is not None :
      show_dots = self.dots_btn.get_active()
      overlaps_only = self.dots2_btn.get_active()
      if show_dots :
        self.dots2_btn.set_sensitive(True)
      else :
        self.dots2_btn.set_sensitive(False)
      show_probe_dots(show_dots, overlaps_only)

  def toggle_all_probe_dots (self, *args) :
    if self.dots2_btn is not None :
      self._overlaps_only = self.dots2_btn.get_active()
      self.toggle_probe_dots()

class rsc_todo_list_gui (coot_extension_gui) :
  data_keys = ["by_res", "by_atom"]
  data_titles = ["Real-space correlation by residue",
                 "Real-space correlation by atom"]
  data_names = {}
  data_types = {}

class residue_properties_list (object) :
  def __init__ (self, columns, column_types, rows, box,
      default_size=(380,200)) :
    assert len(columns) == (len(column_types) - 1)
    if (len(rows) > 0) and (len(rows[0]) != len(column_types)) :
      raise RuntimeError("Wrong number of rows:\n%s" % str(rows[0]))
    import gtk
    ##adding a column type for checkbox (bool) before atom coordinate
    if gobject is not None:
        column_types = column_types[:-1]+[bool]+[column_types[-1]]
    
    self.liststore = gtk.ListStore(*column_types)
    self.listmodel = gtk.TreeModelSort(self.liststore)
    self.listctrl = gtk.TreeView(self.listmodel)
    self.listctrl.column = [None]*len(columns)
    self.listctrl.cell = [None]*len(columns)
    for i, column_label in enumerate(columns) :
      cell = gtk.CellRendererText()
      column = gtk.TreeViewColumn(column_label)
      self.listctrl.append_column(column)
      column.set_sort_column_id(i)
      column.pack_start(cell, True)
      column.set_attributes(cell, text=i)
    ##add a cell for checkbox
    cell1 = gtk.CellRendererToggle()
    cell1.connect ("toggled", self.on_selected_toggled)
    column = gtk.TreeViewColumn('Dealt with',cell1,active=i+1)
    self.listctrl.append_column(column)
    #column.set_sort_column_id(i+1)
    #column.pack_start(cell1, True)
    
    self.listctrl.get_selection().set_mode(gtk.SELECTION_SINGLE)
    for row in rows :
      row = row[:-1] + (False,)+(row[-1],)
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

  def OnChange (self, treeview) :
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
  ##check box toggle
  def on_selected_toggled(self,renderer,path):
    if path is not None:
      model = self.listmodel.get_model()
      it = model.get_iter(path)
      #set toggle
      model[it][-2] = not model[it][-2]
      #set checkboxes for same residues in other lists
      try:
        chain = model[it][0]
        residue = model[it][1]
        for data_key in dict_residue_prop_objects:
          prop_obj = dict_residue_prop_objects[data_key]
          for row in prop_obj.listmodel.get_model():
            if data_key == 'probe':
              atom1_split = row[0].split()
              atom2_split = row[1].split()
              if atom1_split[0] == chain and atom1_split[1] == residue:
                row[-2] = model[it][-2]
              elif atom2_split[0] == chain and atom2_split[1] == residue:
                row[-2] = model[it][-2]
            elif row[0] == chain and row[1] == residue:
              row[-2] = model[it][-2]
      except IndexError: pass

  def check_chain_residue(self,chain,residue):
      pass
  
def show_probe_dots (show_dots, overlaps_only) :
  import coot # import dependency
  n_objects = number_of_generic_objects()
  sys.stdout.flush()
  if show_dots :
    for object_number in range(n_objects) :
      obj_name = generic_object_name(object_number)
      if overlaps_only and not obj_name in ["small overlap", "bad overlap"] :
        sys.stdout.flush()
        set_display_generic_object(object_number, 0)
      else :
        set_display_generic_object(object_number, 1)
  else :
    sys.stdout.flush()
    for object_number in range(n_objects) :
      set_display_generic_object(object_number, 0)

def load_pkl (file_name) :
  pkl = open(file_name, "rb")
  data = cPickle.load(pkl)
  pkl.close()
  return data
data = {}
data['rama'] = []
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' H  17  SER  HA ', ' H  83  MET  O  ', -0.971, (100.675, 135.803, 83.973)), (' L  33  LEU  HA ', ' L  89  GLN  O  ', -0.88, (102.366, 106.492, 88.319)), (' L  63  SER  O  ', ' L  74  THR  HB ', -0.766, (100.602, 94.954, 81.609)), (' H  69  THR  O  ', ' H  81  LEU  HA ', -0.744, (96.72, 130.782, 89.82)), (' A 431  GLY  HA3', ' A 513  LEU  O  ', -0.667, (63.951, 102.073, 113.334)), (' H   6  GLU  H  ', ' H 111  GLN HE22', -0.633, (87.367, 125.194, 78.641)), (' H  20  LEU  O  ', ' H  80  TYR  HA ', -0.618, (91.718, 129.945, 86.836)), (' A 455  LEU HD23', ' H 103  MET  HE1', -0.612, (90.002, 103.138, 100.202)), (' H   7  SER  HB3', ' H  21  SER  HB3', -0.59, (88.763, 130.567, 82.704)), (' H  19  ARG  HA ', ' H  82  GLN  HA ', -0.578, (96.04, 133.545, 86.214)), (' L  86  TYR  O  ', ' L 101  GLY  HA2', -0.576, (104.859, 108.304, 77.062)), (' H 104  ASN  HB3', ' H 106  LYS  HG2', -0.567, (88.039, 108.882, 91.561)), (' H  47  TRP  HZ2', ' H  50  VAL HG13', -0.561, (100.484, 119.648, 92.75)), (' H   2  GLN  N  ', ' H  25  SER  O  ', -0.554, (81.657, 116.579, 84.863)), (' H  91  THR HG23', ' H 116  THR  HA ', -0.553, (102.992, 130.372, 73.652)), (' A 367  VAL  HA ', ' A 370  ASN  HB2', -0.543, (50.544, 96.788, 102.628)), (' A 437  ASN  ND2', ' A 506  GLN  OE1', -0.541, (69.388, 92.399, 92.957)), (' A 417  LYS  HE2', ' A 455  LEU HD12', -0.541, (86.805, 99.799, 104.202)), (' H  62  ASP  HA ', ' H  65  LYS  HB2', -0.534, (109.648, 126.274, 91.596)), (' A 334  ASN  HB2', ' A 361  CYS  HA ', -0.533, (50.296, 113.756, 110.355)), (' A 457  ARG  NH1', ' A 459  SER  OG ', -0.532, (86.669, 108.112, 114.44)), (' H  11  VAL  HA ', ' H 116  THR  HB ', -0.522, (100.305, 134.031, 73.129)), (' L  63  SER  O  ', ' L  74  THR  CB ', -0.521, (101.553, 94.874, 81.372)), (' H  37  VAL HG12', ' H  47  TRP  HA ', -0.519, (101.171, 118.163, 85.535)), (' H  70  ILE  HB ', ' H  81  LEU HD12', -0.519, (97.206, 127.122, 90.378)), (' A 365  TYR  HA ', ' A 368  LEU HD13', -0.518, (53.21, 100.933, 107.418)), (' L  94  THR  OG1', ' L  96  ARG  NH1', -0.512, (102.612, 116.273, 96.236)), (' H  35  HIS  HB2', ' H  97  ALA  HB3', -0.499, (96.14, 118.051, 87.185)), (' H  40  ALA  HB3', ' H  43  LYS  HB2', -0.498, (107.063, 120.823, 75.606)), (' H  11  VAL HG11', ' H 121  SER  HA ', -0.494, (101.392, 137.344, 69.837)), (' L   5  THR  HB ', ' L  24  ARG  HB2', -0.491, (113.934, 103.929, 85.296)), (' A 401  VAL HG22', ' A 509  ARG  HG2', -0.489, (69.341, 103.091, 97.439)), (' A 393  THR  O  ', ' A 523  THR  OG1', -0.482, (55.928, 113.152, 117.559)), (' A 337  PRO  HB2', ' A 340  GLU  HB2', -0.482, (56.925, 111.866, 101.856)), (' H  68  PHE  HB3', ' H  81  LEU HD21', -0.479, (100.233, 128.707, 87.532)), (' A 448  ASN  HB3', ' A 497  PHE  HB2', -0.479, (76.205, 100.881, 89.939)), (' L  93  SER  OG ', ' L  94  THR  N  ', -0.475, (106.335, 114.718, 96.975)), (' H  24  ALA  HB3', ' H  77  ASN  HB3', -0.474, (82.968, 121.982, 88.847)), (' A 418  ILE  HA ', ' A 422  ASN  HB2', -0.474, (79.602, 102.07, 106.323)), (' H  60  TYR  HE1', ' H  70  ILE HG22', -0.465, (99.345, 127.136, 93.45)), (' A 486  PHE  HA ', ' L  32  TYR  HE2', -0.464, (101.953, 107.542, 99.211)), (' L  35  TRP  HA ', ' L  87  TYR  O  ', -0.463, (101.214, 106.081, 81.771)), (' A 393  THR HG21', ' A 518  LEU  H  ', -0.454, (58.388, 110.631, 123.625)), (' L  34  ASN  HB2', ' L  89  GLN  HB3', -0.452, (100.193, 107.457, 86.48)), (' H   5  VAL  O  ', ' H  22  CYS  HA ', -0.451, (87.991, 125.204, 82.745)), (' H  38  ARG  NH2', ' H  46  GLU  OE1', -0.446, (107.29, 121.941, 82.622)), (' A 497  PHE  HA ', ' A 501  ASN HD21', -0.444, (77.325, 97.126, 90.261)), (' A 356  LYS  HE3', ' A 358  ILE HD11', -0.443, (59.469, 113.395, 106.311)), (' L  35  TRP  HD1', ' L  48  ILE  HB ', -0.443, (99.556, 101.654, 84.424)), (' L   6  GLN  O  ', ' L 100  GLN  NE2', -0.44, (112.309, 106.744, 79.161)), (' A 436  TRP  O  ', ' A 508  TYR  HA ', -0.434, (68.42, 97.371, 98.05)), (' H  99  HIS  CG ', ' L  89  GLN HE22', -0.432, (98.453, 111.763, 88.849)), (' L  21  ILE HD12', ' L  73  LEU HD23', -0.432, (103.62, 101.107, 77.432)), (' H  22  CYS  O  ', ' H  78  THR  HA ', -0.421, (86.953, 125.571, 87.258)), (' A 501  ASN  HB3', ' A 505  TYR  HB2', -0.421, (77.102, 92.422, 91.522)), (' A 394  ASN  N  ', ' A 394  ASN  OD1', -0.409, (59.593, 111.278, 118.879)), (' H   9  GLY  HA3', ' H 114  LEU  O  ', -0.406, (96.052, 129.848, 75.114)), (' H   7  SER  N  ', ' H  21  SER  O  ', -0.406, (89.519, 128.247, 81.6)), (' A 424  LYS  HB3', ' A 463  PRO  HA ', -0.404, (76.911, 105.563, 114.673)), (' A 498  GLN  H  ', ' A 501  ASN  ND2', -0.403, (76.802, 96.104, 89.262)), (' A 406  GLU  O  ', ' A 409  GLN  HB2', -0.401, (76.729, 95.693, 106.114)), (' L   3  GLN  HB2', ' L  26  SER  HB3', -0.4, (115.486, 108.971, 89.514))]
data['smoc'] = [('A', 334, u'ASN', 0.8166944653001184, (47.791000000000004, 114.455, 108.66)), ('A', 343, u'ASN', 0.8462044869214868, (58.774, 105.681, 96.854)), ('A', 346, u'ARG', 0.8828533787574053, (66.94500000000001, 109.51400000000001, 94.663)), ('A', 364, u'ASP', 0.8370006326428366, (50.407, 103.829, 107.569)), ('A', 382, u'VAL', 0.77128947401261, (58.713, 95.259, 120.452)), ('A', 398, u'ASP', 0.8582659552516528, (67.195, 108.12899999999999, 107.35499999999999)), ('A', 401, u'VAL', 0.8811792546421008, (72.115, 102.8, 99.384)), ('A', 408, u'ARG', 0.8047748790484353, (74.304, 92.223, 107.245)), ('A', 415, u'THR', 0.8663090056637635, (81.21100000000001, 95.576, 112.706)), ('A', 423, u'TYR', 0.8623907132756634, (76.777, 104.86, 109.353)), ('A', 432, u'CYS', 0.828984833074225, (63.336999999999996, 98.862, 111.96900000000001)), ('A', 447, u'GLY', 0.8506922702014389, (78.533, 101.55799999999999, 84.812)), ('A', 458, u'LYS', 0.8644027674435558, (91.07799999999999, 107.503, 112.303)), ('A', 464, u'PHE', 0.8518201034173761, (73.96100000000001, 108.295, 113.853)), ('A', 467, u'ASP', 0.8657401334199458, (80.926, 112.037, 107.936)), ('A', 480, u'CYS', 0.8501936381101091, (100.298, 114.895, 103.27499999999999)), ('A', 484, u'GLU', 0.8474583434109078, (97.17599999999999, 113.16199999999999, 98.425)), ('A', 485, u'GLY', 0.8346959040894586, (100.49400000000001, 111.381, 98.745)), ('A', 499, u'PRO', 0.8190780745950973, (73.319, 94.669, 86.095)), ('A', 501, u'ASN', 0.8414785069924164, (76.78, 91.983, 88.899)), ('A', 519, u'HIS', 0.7225984532553196, (58.28, 114.274, 127.71300000000001)), ('A', 525, u'CYS', 0.8237135782934324, (50.72200000000001, 107.93900000000001, 115.846)), ('H', 10, u'GLY', 0.7003696577355432, (96.313, 133.547, 73.823)), ('H', 11, u'VAL', 0.7653411983085809, (99.527, 135.415, 73.117)), ('H', 19, u'ARG', 0.8567507557477839, (94.301, 134.195, 85.195)), ('H', 22, u'CYS', 0.8346256978261015, (88.627, 125.96000000000001, 84.531)), ('H', 28, u'THR', 0.8165092111456936, (81.80799999999999, 118.91100000000002, 91.614)), ('H', 41, u'PRO', 0.8687067037442746, (104.869, 120.709, 71.661)), ('H', 51, u'ILE', 0.8555561325802302, (94.924, 122.607, 94.613)), ('H', 53, u'TYR', 0.7062727254396722, (90.085, 122.263, 98.68599999999999)), ('H', 54, u'ASP', 0.809427209806239, (89.33, 119.70400000000001, 101.418)), ('H', 63, u'SER', 0.8379089820241103, (111.04, 123.41700000000002, 88.482)), ('H', 66, u'GLY', 0.8432556665130793, (106.956, 131.491, 89.277)), ('H', 67, u'ARG', 0.7840988521234724, (104.276, 132.004, 91.974)), ('H', 96, u'CYS', 0.8176293559464853, (93.147, 120.562, 84.242)), ('H', 116, u'THR', 0.8290663329251411, (101.788, 131.771, 74.579)), ('H', 121, u'SER', 0.723385256583866, (101.561, 138.499, 68.621)), ('L', 1, u'ASP', 0.6157386400759234, (113.04, 115.573, 93.531)), ('L', 11, u'LEU', 0.8647764422840294, (109.37299999999999, 101.79, 70.301)), ('L', 18, u'ARG', 0.8194722723211777, (103.535, 92.32, 73.49000000000001)), ('L', 23, u'CYS', 0.8216832668575207, (109.116, 103.061, 83.99700000000001)), ('L', 24, u'ARG', 0.8768421802346195, (111.91600000000001, 102.94200000000001, 86.54400000000001)), ('L', 29, u'ILE', 0.8557797422931985, (107.59, 103.906, 95.5)), ('L', 33, u'LEU', 0.8459866312225064, (102.37199999999999, 104.81700000000001, 89.363)), ('L', 57, u'GLY', 0.8261012819240253, (86.838, 100.789, 78.975)), ('L', 70, u'ASP', 0.8634779772407744, (110.617, 98.972, 88.94300000000001)), ('L', 88, u'CYS', 0.7863125597180147, (103.952, 106.74000000000001, 83.35199999999999)), ('L', 106, u'ILE', 0.8183530862840593, (103.41900000000001, 101.29400000000001, 63.297000000000004))]
data['rota'] = [('A', ' 524 ', 'VAL', 0.2294790327849565, (53.241, 110.653, 115.17400000000002))]
data['clusters'] = [('A', '334', 1, 'side-chain clash\nsmoc Outlier', (50.296, 113.756, 110.355)), ('A', '337', 1, 'side-chain clash', (56.925, 111.866, 101.856)), ('A', '340', 1, 'side-chain clash', (56.925, 111.866, 101.856)), ('A', '356', 1, 'side-chain clash', (59.469, 113.395, 106.311)), ('A', '357', 1, 'Dihedral angle:CD:NE:CZ:NH1', (62.809999999999995, 114.11999999999999, 111.059)), ('A', '358', 1, 'side-chain clash', (59.469, 113.395, 106.311)), ('A', '359', 1, 'cablam CA Geom Outlier', (56.4, 113.9, 113.5)), ('A', '360', 1, 'cablam Outlier', (52.9, 115.3, 113.6)), ('A', '361', 1, 'side-chain clash', (50.296, 113.756, 110.355)), ('A', '390', 1, 'Dihedral angle:CA:C', (52.23500000000001, 101.429, 119.827)), ('A', '391', 1, 'Dihedral angle:CA:C\nDihedral angle:N:CA', (53.329, 104.843, 118.694)), ('A', '392', 1, 'Dihedral angle:N:CA', (56.043, 107.39, 118.796)), ('A', '393', 1, 'side-chain clash', (58.388, 110.631, 123.625)), ('A', '394', 1, 'side-chain clash', (59.593, 111.278, 118.879)), ('A', '518', 1, 'side-chain clash', (58.388, 110.631, 123.625)), ('A', '519', 1, 'smoc Outlier', (58.28, 114.274, 127.71300000000001)), ('A', '523', 1, 'side-chain clash', (55.928, 113.152, 117.559)), ('A', '524', 1, 'Rotamer', (53.241, 110.653, 115.17400000000002)), ('A', '525', 1, 'smoc Outlier', (50.72200000000001, 107.93900000000001, 115.846)), ('A', '406', 2, 'side-chain clash', (76.729, 95.693, 106.114)), ('A', '408', 2, 'smoc Outlier', (74.304, 92.223, 107.245)), ('A', '409', 2, 'side-chain clash', (76.729, 95.693, 106.114)), ('A', '410', 2, 'cablam Outlier', (73.7, 96.9, 109.1)), ('A', '411', 2, 'cablam Outlier', (72.5, 95.5, 112.4)), ('A', '413', 2, 'cablam Outlier', (75.9, 96.5, 117.3)), ('A', '415', 2, 'cablam CA Geom Outlier\nsmoc Outlier', (81.2, 95.6, 112.7)), ('A', '416', 2, 'Dihedral angle:CA:C', (82.24300000000001, 95.924, 109.098)), ('A', '417', 2, 'side-chain clash\nDihedral angle:N:CA', (82.849, 98.94900000000001, 106.94400000000002)), ('A', '431', 2, 'backbone clash\nside-chain clash', (90.002, 103.138, 100.202)), ('A', '455', 2, 'side-chain clash', (86.805, 99.799, 104.202)), ('A', '513', 2, 'backbone clash\nside-chain clash', (90.002, 103.138, 100.202)), ('A', '447', 3, 'smoc Outlier', (78.533, 101.55799999999999, 84.812)), ('A', '448', 3, 'side-chain clash', (76.205, 100.881, 89.939)), ('A', '494', 3, 'Dihedral angle:CA:C', (82.71700000000001, 104.396, 94.821)), ('A', '495', 3, 'Dihedral angle:N:CA', (80.81700000000001, 101.169, 94.41900000000001)), ('A', '497', 3, 'side-chain clash', (77.325, 97.126, 90.261)), ('A', '498', 3, 'side-chain clash', (76.802, 96.104, 89.262)), ('A', '499', 3, 'smoc Outlier', (73.319, 94.669, 86.095)), ('A', '501', 3, 'side-chain clash\nsmoc Outlier', (76.802, 96.104, 89.262)), ('A', '505', 3, 'side-chain clash', (77.102, 92.422, 91.522)), ('A', '418', 4, 'side-chain clash', (101.953, 107.542, 99.211)), ('A', '422', 4, 'side-chain clash', (101.953, 107.542, 99.211)), ('A', '480', 4, 'smoc Outlier', (100.298, 114.895, 103.27499999999999)), ('A', '481', 4, 'cablam Outlier', (98.3, 118.0, 104.5)), ('A', '482', 4, 'cablam Outlier', (95.2, 118.1, 102.3)), ('A', '484', 4, 'smoc Outlier', (97.17599999999999, 113.16199999999999, 98.425)), ('A', '485', 4, 'smoc Outlier', (100.49400000000001, 111.381, 98.745)), ('A', '486', 4, 'Bond angle:C\ncablam Outlier', (102.397, 108.553, 100.429)), ('A', '487', 4, 'Bond angle:N:CA', (101.21600000000001, 106.757, 103.612)), ('A', '364', 5, 'smoc Outlier', (50.407, 103.829, 107.569)), ('A', '365', 5, 'side-chain clash', (53.21, 100.933, 107.418)), ('A', '367', 5, 'side-chain clash', (50.544, 96.788, 102.628)), ('A', '368', 5, 'side-chain clash', (53.21, 100.933, 107.418)), ('A', '370', 5, 'side-chain clash', (50.544, 96.788, 102.628)), ('A', '371', 5, 'cablam Outlier', (54.4, 95.5, 100.5)), ('A', '372', 5, 'cablam Outlier', (56.2, 92.1, 100.6)), ('A', '423', 6, 'smoc Outlier', (76.777, 104.86, 109.353)), ('A', '424', 6, 'side-chain clash', (76.911, 105.563, 114.673)), ('A', '463', 6, 'side-chain clash', (76.911, 105.563, 114.673)), ('A', '464', 6, 'smoc Outlier', (73.96100000000001, 108.295, 113.853)), ('A', '401', 7, 'side-chain clash\nsmoc Outlier', (69.341, 103.091, 97.439)), ('A', '436', 7, 'side-chain clash', (68.42, 97.371, 98.05)), ('A', '508', 7, 'side-chain clash', (68.42, 97.371, 98.05)), ('A', '509', 7, 'side-chain clash', (69.341, 103.091, 97.439)), ('A', '457', 8, 'side-chain clash', (86.669, 108.112, 114.44)), ('A', '458', 8, 'cablam Outlier\nsmoc Outlier', (91.1, 107.5, 112.3)), ('A', '459', 8, 'side-chain clash', (86.669, 108.112, 114.44)), ('A', '437', 9, 'side-chain clash', (69.388, 92.399, 92.957)), ('A', '506', 9, 'side-chain clash', (69.388, 92.399, 92.957)), ('A', '382', 10, 'smoc Outlier', (58.713, 95.259, 120.452)), ('A', '383', 10, 'cablam Outlier', (57.2, 93.0, 117.8)), ('H', '111', 1, 'side-chain clash\ncablam Outlier', (87.367, 125.194, 78.641)), ('H', '17', 1, 'backbone clash', (100.675, 135.803, 83.973)), ('H', '19', 1, 'side-chain clash\nsmoc Outlier', (96.04, 133.545, 86.214)), ('H', '2', 1, 'backbone clash', (81.657, 116.579, 84.863)), ('H', '20', 1, 'side-chain clash', (91.718, 129.945, 86.836)), ('H', '21', 1, 'side-chain clash\nbackbone clash', (89.519, 128.247, 81.6)), ('H', '22', 1, 'side-chain clash\nsmoc Outlier', (86.953, 125.571, 87.258)), ('H', '24', 1, 'side-chain clash', (82.968, 121.982, 88.847)), ('H', '25', 1, 'backbone clash', (81.657, 116.579, 84.863)), ('H', '28', 1, 'Dihedral angle:CA:C\nsmoc Outlier', (81.80799999999999, 118.91100000000002, 91.614)), ('H', '29', 1, 'Dihedral angle:CA:C\nDihedral angle:N:CA', (85.318, 120.13799999999999, 92.073)), ('H', '30', 1, 'Dihedral angle:N:CA', (84.44400000000002, 120.48700000000001, 95.74300000000001)), ('H', '35', 1, 'side-chain clash', (96.14, 118.051, 87.185)), ('H', '37', 1, 'side-chain clash', (101.171, 118.163, 85.535)), ('H', '38', 1, 'side-chain clash', (98.453, 111.763, 88.849)), ('H', '46', 1, 'side-chain clash', (98.453, 111.763, 88.849)), ('H', '47', 1, 'side-chain clash', (101.171, 118.163, 85.535)), ('H', '5', 1, 'side-chain clash', (87.991, 125.204, 82.745)), ('H', '50', 1, 'side-chain clash\nDihedral angle:CA:C', (97.95700000000001, 121.253, 92.866)), ('H', '51', 1, 'Dihedral angle:N:CA\nsmoc Outlier', (94.924, 122.607, 94.613)), ('H', '53', 1, 'smoc Outlier', (90.085, 122.263, 98.68599999999999)), ('H', '54', 1, 'Dihedral angle:CA:C\ncablam Outlier\nsmoc Outlier', (89.33, 119.70400000000001, 101.418)), ('H', '55', 1, 'Dihedral angle:CA:C\nDihedral angle:N:CA', (91.57799999999999, 121.65299999999999, 103.71300000000001)), ('H', '56', 1, 'Dihedral angle:N:CA', (93.40700000000001, 124.5, 102.09)), ('H', '6', 1, 'side-chain clash', (87.367, 125.194, 78.641)), ('H', '60', 1, 'side-chain clash', (99.345, 127.136, 93.45)), ('H', '62', 1, 'side-chain clash', (109.648, 126.274, 91.596)), ('H', '63', 1, 'smoc Outlier', (111.04, 123.41700000000002, 88.482)), ('H', '65', 1, 'side-chain clash', (109.648, 126.274, 91.596)), ('H', '66', 1, 'smoc Outlier', (106.956, 131.491, 89.277)), ('H', '67', 1, 'smoc Outlier', (104.276, 132.004, 91.974)), ('H', '68', 1, 'side-chain clash', (100.233, 128.707, 87.532)), ('H', '69', 1, 'side-chain clash', (96.72, 130.782, 89.82)), ('H', '7', 1, 'side-chain clash\nbackbone clash', (89.519, 128.247, 81.6)), ('H', '70', 1, 'side-chain clash', (99.345, 127.136, 93.45)), ('H', '72', 1, 'Dihedral angle:CA:C\ncablam CA Geom Outlier', (89.059, 128.26, 93.827)), ('H', '73', 1, 'Dihedral angle:N:CA', (85.62499999999999, 129.184, 92.861)), ('H', '77', 1, 'side-chain clash', (82.968, 121.982, 88.847)), ('H', '78', 1, 'side-chain clash', (86.953, 125.571, 87.258)), ('H', '80', 1, 'side-chain clash', (91.718, 129.945, 86.836)), ('H', '81', 1, 'side-chain clash', (100.233, 128.707, 87.532)), ('H', '82', 1, 'side-chain clash', (96.04, 133.545, 86.214)), ('H', '83', 1, 'backbone clash', (100.675, 135.803, 83.973)), ('H', '96', 1, 'smoc Outlier', (93.147, 120.562, 84.242)), ('H', '97', 1, 'side-chain clash', (96.14, 118.051, 87.185)), ('H', '98', 1, 'Dihedral angle:CD:NE:CZ:NH1', (93.223, 114.62799999999999, 88.507)), ('H', '10', 2, 'smoc Outlier', (96.313, 133.547, 73.823)), ('H', '11', 2, 'side-chain clash\nsmoc Outlier', (101.392, 137.344, 69.837)), ('H', '114', 2, 'backbone clash', (96.052, 129.848, 75.114)), ('H', '116', 2, 'side-chain clash\nsmoc Outlier', (100.305, 134.031, 73.129)), ('H', '121', 2, 'side-chain clash\nsmoc Outlier', (101.392, 137.344, 69.837)), ('H', '87', 2, 'Dihedral angle:CA:C', (108.959, 133.43800000000002, 80.274)), ('H', '88', 2, 'Dihedral angle:N:CA', (108.821, 132.189, 76.73400000000001)), ('H', '9', 2, 'backbone clash', (96.052, 129.848, 75.114)), ('H', '91', 2, 'side-chain clash', (102.992, 130.372, 73.652)), ('H', '40', 3, 'side-chain clash', (107.063, 120.823, 75.606)), ('H', '41', 3, 'smoc Outlier', (104.869, 120.709, 71.661)), ('H', '43', 3, 'side-chain clash', (107.063, 120.823, 75.606)), ('H', '104', 4, 'side-chain clash\nDihedral angle:CA:C\ncablam Outlier', (89.512, 106.68599999999999, 93.076)), ('H', '105', 4, 'Dihedral angle:N:CA', (89.242, 106.557, 89.331)), ('H', '106', 4, 'side-chain clash', (88.039, 108.882, 91.561)), ('H', '103', 5, 'side-chain clash', (90.002, 103.138, 100.202)), ('L', '100', 1, 'side-chain clash', (112.309, 106.744, 79.161)), ('L', '101', 1, 'side-chain clash', (104.859, 108.304, 77.062)), ('L', '23', 1, 'smoc Outlier', (109.116, 103.061, 83.99700000000001)), ('L', '24', 1, 'side-chain clash\nsmoc Outlier', (113.934, 103.929, 85.296)), ('L', '26', 1, 'side-chain clash', (115.486, 108.971, 89.514)), ('L', '29', 1, 'smoc Outlier', (107.59, 103.906, 95.5)), ('L', '3', 1, 'side-chain clash', (115.486, 108.971, 89.514)), ('L', '31', 1, 'Dihedral angle:CA:C\ncablam Outlier', (102.669, 101.199, 93.887)), ('L', '32', 1, 'side-chain clash\nDihedral angle:N:CA', (101.929, 104.836, 93.12899999999999)), ('L', '33', 1, 'backbone clash\nsmoc Outlier', (102.366, 106.492, 88.319)), ('L', '34', 1, 'side-chain clash', (100.193, 107.457, 86.48)), ('L', '35', 1, 'backbone clash\nside-chain clash', (99.556, 101.654, 84.424)), ('L', '48', 1, 'side-chain clash', (99.556, 101.654, 84.424)), ('L', '5', 1, 'side-chain clash', (113.934, 103.929, 85.296)), ('L', '6', 1, 'side-chain clash', (112.309, 106.744, 79.161)), ('L', '69', 1, 'cablam Outlier', (111.6, 101.2, 91.8)), ('L', '70', 1, 'smoc Outlier', (110.617, 98.972, 88.94300000000001)), ('L', '86', 1, 'side-chain clash', (104.859, 108.304, 77.062)), ('L', '87', 1, 'backbone clash', (101.214, 106.081, 81.771)), ('L', '88', 1, 'smoc Outlier', (103.952, 106.74000000000001, 83.35199999999999)), ('L', '89', 1, 'backbone clash\nside-chain clash', (98.453, 111.763, 88.849)), ('L', '93', 2, 'backbone clash\ncablam Outlier', (106.335, 114.718, 96.975)), ('L', '94', 2, 'side-chain clash\nbackbone clash\ncablam Outlier', (106.335, 114.718, 96.975)), ('L', '96', 2, 'side-chain clash', (102.612, 116.273, 96.236)), ('L', '63', 3, 'side-chain clash', (101.553, 94.874, 81.372)), ('L', '74', 3, 'side-chain clash', (101.553, 94.874, 81.372)), ('L', '21', 4, 'side-chain clash', (103.62, 101.107, 77.432)), ('L', '73', 4, 'side-chain clash', (103.62, 101.107, 77.432)), ('L', '18', 5, 'smoc Outlier', (103.535, 92.32, 73.49000000000001)), ('L', '77', 5, 'cablam Outlier', (98.2, 91.6, 71.6)), ('L', '38', 6, 'Dihedral angle:CA:C', (97.669, 110.112, 74.418)), ('L', '39', 6, 'Dihedral angle:N:CA', (97.269, 110.37299999999999, 70.74100000000001))]
data['omega'] = [('A', ' 392 ', 'PHE', None, (54.715, 106.808, 118.677)), ('H', '  73 ', 'ASP', None, (87.00400000000005, 128.736, 92.714)), ('L', '   8 ', 'PRO', None, (111.848, 101.977, 76.93000000000002)), ('L', '  95 ', 'PRO', None, (106.99500000000003, 117.133, 94.492))]
data['cablam'] = [('A', '360', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nE-SB-', (52.9, 115.3, 113.6)), ('A', '371', 'SER', 'check CA trace,carbonyls, peptide', 'helix\nHHH--', (54.4, 95.5, 100.5)), ('A', '372', 'ALA', 'check CA trace,carbonyls, peptide', ' \nHH---', (56.2, 92.1, 100.6)), ('A', '383', 'SER', 'check CA trace,carbonyls, peptide', ' \nSS-TT', (57.2, 93.0, 117.8)), ('A', '410', 'ILE', 'check CA trace,carbonyls, peptide', ' \nGT-ST', (73.7, 96.9, 109.1)), ('A', '411', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nT-STT', (72.5, 95.5, 112.4)), ('A', '413', 'GLY', 'check CA trace,carbonyls, peptide', 'turn\nSTT--', (75.9, 96.5, 117.3)), ('A', '458', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (91.1, 107.5, 112.3)), ('A', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n--TTS', (98.3, 118.0, 104.5)), ('A', '482', 'GLY', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (95.2, 118.1, 102.3)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (102.4, 108.6, 100.4)), ('A', '359', 'SER', 'check CA trace', ' \nEE-SB', (56.4, 113.9, 113.5)), ('A', '415', 'THR', 'check CA trace', ' \nT--SH', (81.2, 95.6, 112.7)), ('H', '54', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nETTTT', (89.3, 119.7, 101.4)), ('H', '104', 'ASN', 'check CA trace,carbonyls, peptide', ' \nSS---', (89.5, 106.7, 93.1)), ('H', '111', 'GLN', 'check CA trace,carbonyls, peptide', ' \n----E', (90.3, 120.2, 76.5)), ('H', '72', 'ARG', 'check CA trace', 'strand\nEEEEG', (89.1, 128.3, 93.8)), ('L', '31', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nESS-E', (102.7, 101.2, 93.9)), ('L', '60', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nB-TTE', (93.4, 93.4, 79.7)), ('L', '69', 'THR', 'check CA trace,carbonyls, peptide', 'strand\nEEEEE', (111.6, 101.2, 91.8)), ('L', '77', 'SER', 'check CA trace,carbonyls, peptide', 'bend\nE-S--', (98.2, 91.6, 71.6)), ('L', '93', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (105.5, 112.7, 96.9)), ('L', '94', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nSSSS-', (105.2, 116.2, 95.9))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-30485/7cwo/Model_validation_1/validation_cootdata/molprobity_probe7cwo_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

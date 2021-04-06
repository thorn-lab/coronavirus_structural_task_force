
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
data['rota'] = []
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' B 380  HIS  HB3', ' B 393  TYR  HB2', -0.783, (76.509, 62.719, 76.421)), (' A 363  TYR  HE2', ' A 631  MET  HE1', -0.702, (72.873, 91.484, 94.119)), (' A 363  TYR  CE2', ' A 631  MET  HE1', -0.699, (73.422, 91.655, 93.622)), (' A 564  ARG  O  ', ' A 568  ASN  HB2', -0.671, (107.246, 72.204, 94.05)), (' A 261  LYS  NZ ', ' A 321  LEU  O  ', -0.664, (75.613, 122.476, 93.371)), (' B 548  HIS  HB2', ' B 555  LEU HD21', -0.649, (87.89, 68.7, 50.007)), (' A 355  ASP  OD1', ' A 356  TYR  N  ', -0.64, (71.128, 95.408, 76.778)), (' B 496  ARG  HG3', ' B 500  MET  HE3', -0.638, (83.271, 87.057, 40.91)), (' A 564  ARG  HA ', ' A 567  ILE HG22', -0.614, (104.408, 73.5, 93.71)), (' A 255  LYS  HE2', ' A 334  PRO  HG3', -0.602, (93.669, 115.028, 105.007)), (' A 514  THR HG22', ' A 516  ARG  H  ', -0.602, (109.775, 93.304, 105.129)), (' B 498  ARG  NH1', ' B 649  ASP  OD1', -0.599, (73.744, 96.447, 36.561)), (' A 583  LYS  NZ ', ' A 638  TYR  OH ', -0.599, (86.285, 86.002, 86.637)), (' B 483  ILE HG22', ' B 575  LEU  HB2', -0.595, (86.166, 85.22, 49.665)), (' B 472  TYR  OH ', ' B 591  LYS  NZ ', -0.592, (97.034, 94.013, 58.485)), (' A 518  ARG HH21', ' A 523  VAL  HA ', -0.582, (117.176, 84.728, 111.339)), (' A 318  PHE  HB2', ' C  73  LEU HD21', -0.573, (71.066, 115.275, 96.712)), (' B 514  THR HG22', ' B 516  ARG  H  ', -0.573, (91.086, 67.18, 39.158)), (' B 483  ILE HD11', ' B 594  ILE HG12', -0.571, (84.866, 86.855, 55.49)), (' B 624  ILE  O  ', ' B 628  THR HG23', -0.571, (60.327, 84.332, 51.808)), (' B 497  GLN  O  ', ' B 501  ASN  HB2', -0.566, (82.33, 89.896, 35.738)), (' A 464  LEU HD22', ' B 462  GLU  HG3', -0.565, (83.4, 81.427, 73.616)), (' B 600  PRO  HG2', ' B 605  LEU  HB2', -0.562, (62.346, 89.97, 47.205)), (' B 548  HIS  HA ', ' B 556  TYR  O  ', -0.541, (86.839, 71.457, 48.866)), (' B 536  PHE  HE2', ' B 555  LEU  HB3', -0.539, (89.279, 66.12, 47.067)), (' A 312  LYS  HB3', ' A 316  GLU  OE2', -0.534, (70.365, 116.554, 106.331)), (' B 355  ASP  OD1', ' B 356  TYR  N  ', -0.533, (67.347, 77.048, 80.356)), (' B 637  HIS  ND1', ' B 637  HIS  O  ', -0.53, (78.367, 88.834, 65.169)), (' A 399  ASP  OD1', ' A 400  ASN  N  ', -0.523, (80.389, 115.385, 72.937)), (' B 358  PRO  O  ', ' B 367  ARG  NH2', -0.523, (59.775, 72.784, 72.679)), (' B 498  ARG  HD2', ' B 652  TYR  OH ', -0.515, (77.467, 94.454, 37.897)), (' B 410  LYS  NZ ', ' B 635  ASN  HA ', -0.509, (73.201, 81.827, 65.666)), (' A 303  GLU  HA ', ' A 309  ILE HG12', -0.508, (78.722, 120.825, 106.284)), (' B 563  VAL HG11', ' B 590  LEU HD21', -0.507, (93.02, 84.043, 52.225)), (' A 368  GLU  N  ', ' A 368  GLU  OE1', -0.503, (71.005, 108.289, 88.75)), (' B 656  LEU  HA ', ' B 659  ILE HG22', -0.5, (83.364, 98.668, 46.18)), (' A 589  ASP  N  ', ' A 589  ASP  OD1', -0.499, (100.579, 77.136, 86.06)), (' A 313  ASP  N  ', ' A 316  GLU  OE2', -0.498, (69.846, 114.831, 105.761)), (' C  68  SER  C  ', ' C  69  ARG  HD2', -0.489, (70.701, 99.119, 101.927)), (' A 277  SER  OG ', ' A 310  ARG  NH2', -0.489, (80.69, 112.216, 111.39)), (' B 523  VAL  H  ', ' B 526  ARG  NH1', -0.488, (95.764, 76.271, 30.555)), (' A 388  ASN  OD1', ' A 635  ASN  ND2', -0.488, (80.809, 91.272, 90.76)), (' A 351  LYS  HD3', ' B 469  MET  HE2', -0.487, (83.566, 93.626, 68.314)), (' B 516  ARG  HG2', ' B 517  SER  H  ', -0.48, (89.705, 64.866, 35.412)), (' B 493  ASN  OD1', ' B 496  ARG  NH1', -0.476, (79.612, 82.169, 41.617)), (' A 641  THR HG21', ' A 658  LEU HD11', -0.475, (82.465, 70.123, 98.9)), (' A 269  ALA  O  ', ' C  75  VAL HG22', -0.469, (78.484, 114.136, 93.64)), (' B 559  SER  OG ', ' B 560  ILE  N  ', -0.468, (96.153, 77.336, 50.86)), (' A 533  ARG  HG2', ' A 537  GLU  OE1', -0.467, (110.653, 98.502, 95.664)), (' B 623  GLU  O  ', ' B 627  LYS  HG2', -0.466, (61.754, 80.771, 49.104)), (' A 305  ASN  HA ', ' A 329  THR  OG1', -0.466, (82.55, 126.956, 102.293)), (' B 461  GLU  CD ', ' B 462  GLU  H  ', -0.466, (81.505, 77.483, 69.836)), (' A 654  GLU  OE2', ' A 657  ARG  NH2', -0.463, (80.074, 65.814, 101.82)), (' A 464  LEU  HA ', ' A 464  LEU HD23', -0.463, (82.061, 82.745, 76.217)), (' B 386  ASP  OD1', ' B 387  PRO  HD2', -0.462, (73.501, 69.384, 60.248)), (' B 523  VAL HG12', ' B 525  GLY  H  ', -0.456, (99.385, 76.189, 33.93)), (' B 384  GLN  HG3', ' B 390  TRP  NE1', -0.456, (78.062, 70.326, 66.925)), (' A 640  ASP  O  ', ' A 641  THR  OG1', -0.455, (82.973, 71.434, 94.797)), (' A 469  MET  HE2', ' B 351  LYS  HD2', -0.453, (82.503, 72.494, 83.536)), (' B 367  ARG  NE ', ' B 367  ARG  O  ', -0.452, (58.063, 70.699, 70.416)), (' B 532  SER  OG ', ' B 534  GLN  OE1', -0.449, (97.627, 60.437, 44.188)), (' B 366  CYS  SG ', ' B 369  LEU  HB2', -0.444, (63.281, 66.892, 68.316)), (' B 405  GLY  O  ', ' B 406  LEU HD23', -0.444, (69.978, 65.263, 69.522)), (' B 593  TYR  CD2', ' B 662  LEU HD11', -0.444, (86.098, 95.344, 53.765)), (' B 527  ASP  OD1', ' B 528  TYR  N  ', -0.443, (94.429, 76.03, 36.481)), (' B 582  LEU  HA ', ' B 582  LEU HD23', -0.442, (84.21, 81.111, 57.115)), (' B 516  ARG  NH2', ' B 519  ARG HH21', -0.441, (88.945, 70.097, 33.806)), (' B 358  PRO  HG3', ' B 370  GLY  HA3', -0.44, (63.952, 69.942, 74.554)), (' B 477  ASN  HB2', ' B 478  ARG HH11', -0.437, (103.213, 96.245, 50.546)), (' A 470  SER  OG ', ' A 671  SER  OG ', -0.433, (89.755, 68.15, 78.063)), (' A 351  LYS  HD3', ' B 469  MET  CE ', -0.432, (83.678, 94.049, 68.082)), (' A 469  MET  HE2', ' B 351  LYS  CD ', -0.43, (83.054, 72.623, 83.319)), (' B 581  SER  O  ', ' B 581  SER  OG ', -0.43, (85.079, 77.802, 55.977)), (' B 358  PRO  HD2', ' B 372  SER  HB3', -0.429, (64.123, 71.633, 78.053)), (' A 570  GLY  O  ', ' A 571  LYS  HD3', -0.428, (103.114, 66.211, 102.135)), (' A 387  PRO  HG3', ' A 580  GLN  OE1', -0.427, (88.678, 93.826, 92.319)), (' B 388  ASN  HB2', ' B 389  TRP  CD1', -0.425, (70.573, 72.598, 63.687)), (' B 362  PRO  HG2', ' B 363  TYR  CE1', -0.424, (61.942, 80.254, 65.133)), (' B 465  THR  O  ', ' B 466  TYR  HD1', -0.422, (80.858, 91.628, 76.659)), (' A 300  GLU  OE1', ' A 301  VAL  N  ', -0.42, (83.05, 114.52, 106.665)), (' A 249  TYR  HB3', ' A 302  LEU HD23', -0.418, (84.252, 120.32, 112.008)), (' B 637  HIS  CG ', ' B 637  HIS  O  ', -0.418, (77.793, 88.616, 65.298)), (' B 508  ALA  O  ', ' B 573  CYS  HA ', -0.414, (90.536, 88.26, 44.242)), (' B 367  ARG  O  ', ' B 368  GLU  HG3', -0.413, (57.833, 69.072, 71.041)), (' B 540  ILE  H  ', ' B 540  ILE HD12', -0.411, (93.415, 66.361, 53.662)), (' B 361  ASP  O  ', ' B 364  VAL HG22', -0.409, (61.779, 74.586, 68.314)), (' B 563  VAL  O  ', ' B 567  ILE HG13', -0.408, (95.98, 86.511, 49.51)), (' A 275  MET  O  ', ' A 277  SER  N  ', -0.407, (77.308, 109.365, 110.018)), (' A 263  ARG  O  ', ' A 265  ILE HG12', -0.405, (75.929, 124.734, 85.932)), (' B 656  LEU  HA ', ' B 656  LEU HD23', -0.403, (83.06, 98.827, 45.219)), (' B 577  LEU  HA ', ' B 577  LEU HD23', -0.4, (83.553, 80.0, 50.205))]
data['cablam'] = [('A', '276', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nBTTB-', (75.8, 109.8, 111.6)), ('A', '294', 'LEU', 'check CA trace,carbonyls, peptide', ' \nHT---', (92.0, 116.7, 95.4)), ('A', '299', 'ASP', 'check CA trace,carbonyls, peptide', ' \nTT---', (86.6, 110.8, 103.4)), ('A', '352', 'ALA', 'check CA trace,carbonyls, peptide', ' \nEE--S', (79.6, 94.1, 74.0)), ('A', '362', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nG-TT-', (67.5, 96.4, 91.1)), ('A', '363', 'TYR', 'check CA trace,carbonyls, peptide', 'turn\n-TT-S', (71.3, 96.2, 91.8)), ('A', '365', 'PRO', 'check CA trace,carbonyls, peptide', 'bend\nT-S-S', (74.8, 101.6, 92.9)), ('A', '400', 'ASN', 'check CA trace,carbonyls, peptide', 'turn\n-TTS-', (78.7, 115.6, 75.0)), ('A', '401', 'GLN', 'check CA trace,carbonyls, peptide', 'bend\nTTS-S', (78.0, 113.1, 77.7)), ('A', '403', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nS-S-E', (80.2, 112.8, 82.7)), ('A', '464', 'LEU', 'check CA trace,carbonyls, peptide', ' \n---S-', (81.7, 81.6, 77.4)), ('A', '490', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nTTSSH', (81.9, 83.4, 108.9)), ('A', '520', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\n--TT-', (116.2, 88.6, 115.9)), ('A', '524', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (116.5, 83.0, 106.9)), ('A', '527', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (109.5, 82.3, 108.3)), ('A', '529', 'HIS', 'check CA trace,carbonyls, peptide', ' \nS----', (112.1, 85.8, 102.4)), ('A', '530', 'PHE', 'check CA trace,carbonyls, peptide', ' \n-----', (113.6, 89.2, 103.3)), ('A', '553', 'LYS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (105.1, 101.3, 105.3)), ('A', '558', 'THR', ' beta sheet', 'beta bridge\n--B-S', (102.8, 85.7, 98.2)), ('A', '601', 'SER', 'check CA trace,carbonyls, peptide', ' \n---HH', (69.8, 82.5, 106.5)), ('A', '634', 'ASN', ' alpha helix', 'bend\nHSSS-', (76.0, 85.9, 90.6)), ('A', '639', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---S-', (84.4, 77.4, 92.4)), ('A', '649', 'ASP', ' alpha helix', 'helix\nSHHHH', (81.9, 70.3, 114.1)), ('A', '650', 'LYS', ' alpha helix', 'helix\nHHHHH', (79.8, 69.3, 111.2)), ('A', '250', 'GLY', 'check CA trace', 'helix-3\n-GGGS', (85.4, 117.6, 116.1)), ('A', '275', 'MET', 'check CA trace', 'turn\n-BTTB', (76.0, 106.1, 110.5)), ('A', '633', 'GLN', 'check CA trace', 'bend\nHHSSS', (77.8, 84.9, 93.9)), ('B', '352', 'ALA', ' beta sheet', ' \nE---S', (77.0, 74.5, 79.5)), ('B', '358', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nB-TTS', (62.8, 73.8, 74.6)), ('B', '365', 'PRO', 'check CA trace,carbonyls, peptide', 'turn\nT-TTS', (62.4, 70.6, 63.4)), ('B', '366', 'CYS', ' alpha helix', 'turn\n-TTS-', (60.5, 68.1, 65.5)), ('B', '369', 'LEU', 'check CA trace,carbonyls, peptide', ' \nS----', (63.1, 66.1, 71.2)), ('B', '372', 'SER', ' beta sheet', ' \n---B-', (66.4, 70.7, 78.7)), ('B', '403', 'LEU', ' beta sheet', ' \nS---E', (69.4, 60.0, 75.2)), ('B', '404', 'ALA', ' beta sheet', ' \n---EE', (70.0, 60.8, 71.5)), ('B', '464', 'LEU', 'check CA trace,carbonyls, peptide', ' \n---SS', (81.8, 86.0, 74.3)), ('B', '465', 'THR', 'check CA trace,carbonyls, peptide', 'bend\n--SSE', (80.5, 88.7, 76.6)), ('B', '489', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n-SSSS', (69.4, 82.3, 45.5)), ('B', '490', 'CYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSSH', (69.7, 86.0, 45.9)), ('B', '529', 'HIS', 'check CA trace,carbonyls, peptide', ' \nT----', (96.6, 73.0, 40.9)), ('B', '559', 'SER', 'check CA trace,carbonyls, peptide', ' \nEE-SH', (94.4, 76.5, 50.0)), ('B', '571', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSEE', (94.4, 92.7, 42.9)), ('B', '590', 'LEU', 'check CA trace,carbonyls, peptide', 'turn\nSTT--', (94.5, 86.1, 57.2)), ('B', '637', 'HIS', 'check CA trace,carbonyls, peptide', ' \nT----', (77.0, 87.4, 63.7)), ('B', '649', 'ASP', ' alpha helix', 'helix-3\nSGGGT', (71.8, 98.1, 39.3)), ('B', '360', 'ASP', 'check CA trace', 'bend\nTTS-T', (59.0, 76.9, 72.8)), ('C', '71', 'PRO', 'check CA trace,carbonyls, peptide', ' \nSS--E', (71.3, 103.3, 96.9)), ('C', '69', 'ARG', 'check CA trace', 'bend\n--SS-', (69.4, 101.1, 101.2)), ('C', '70', 'VAL', 'check CA trace', 'bend\n-SS--', (68.3, 104.0, 99.1))]
data['clusters'] = [('A', '514', 1, 'side-chain clash', (109.775, 93.304, 105.129)), ('A', '516', 1, 'side-chain clash', (109.775, 93.304, 105.129)), ('A', '520', 1, 'cablam Outlier', (116.2, 88.6, 115.9)), ('A', '521', 1, 'smoc Outlier', (113.476, 85.84700000000001, 116.012)), ('A', '522', 1, 'Dihedral angle:CA:C', (113.115, 84.691, 112.37199999999999)), ('A', '523', 1, 'side-chain clash\nDihedral angle:N:CA', (116.238, 83.6, 110.62899999999999)), ('A', '524', 1, 'cablam Outlier', (116.5, 83.0, 106.9)), ('A', '527', 1, 'cablam Outlier', (109.5, 82.3, 108.3)), ('A', '529', 1, 'cablam Outlier', (112.1, 85.8, 102.4)), ('A', '530', 1, 'cablam Outlier', (113.6, 89.2, 103.3)), ('A', '531', 1, 'smoc Outlier', (114.568, 91.119, 100.181)), ('A', '363', 2, 'side-chain clash\ncablam Outlier', (73.422, 91.655, 93.622)), ('A', '583', 2, 'side-chain clash', (86.285, 86.002, 86.637)), ('A', '594', 2, 'smoc Outlier', (88.337, 76.486, 95.039)), ('A', '630', 2, 'Dihedral angle:CB:CG:CD:OE1', (74.859, 87.664, 97.67999999999999)), ('A', '631', 2, 'side-chain clash\nsmoc Outlier', (73.422, 91.655, 93.622)), ('A', '633', 2, 'cablam CA Geom Outlier', (77.8, 84.9, 93.9)), ('A', '634', 2, 'cablam Outlier', (76.0, 85.9, 90.6)), ('A', '636', 2, 'smoc Outlier', (81.554, 84.147, 90.651)), ('A', '638', 2, 'side-chain clash\nDihedral angle:CA:C', (84.721, 79.41600000000001, 89.23)), ('A', '639', 2, 'Dihedral angle:N:CA\ncablam Outlier', (84.44700000000002, 77.43400000000001, 92.40700000000001)), ('A', '384', 3, 'smoc Outlier', (88.738, 99.143, 85.933)), ('A', '385', 3, 'smoc Outlier', (89.582, 100.11999999999999, 89.51400000000001)), ('A', '387', 3, 'side-chain clash', (88.678, 93.826, 92.319)), ('A', '547', 3, 'smoc Outlier', (98.18499999999999, 88.73100000000001, 96.1)), ('A', '558', 3, 'cablam Outlier', (102.8, 85.7, 98.2)), ('A', '580', 3, 'side-chain clash\nDihedral angle:CA:C', (90.15599999999999, 89.76, 93.254)), ('A', '581', 3, 'Dihedral angle:N:CA', (93.074, 87.415, 92.68799999999999)), ('A', '275', 4, 'backbone clash\ncablam CA Geom Outlier', (77.308, 109.365, 110.018)), ('A', '276', 4, 'Ramachandran\ncablam Outlier', (75.779, 109.79999999999998, 111.62099999999998)), ('A', '277', 4, 'side-chain clash\nbackbone clash\nsmoc Outlier', (77.308, 109.365, 110.018)), ('A', '299', 4, 'cablam Outlier\nsmoc Outlier', (86.6, 110.8, 103.4)), ('A', '300', 4, 'backbone clash', (83.05, 114.52, 106.665)), ('A', '301', 4, 'backbone clash', (83.05, 114.52, 106.665)), ('A', '310', 4, 'side-chain clash', (80.69, 112.216, 111.39)), ('A', '352', 5, 'cablam Outlier', (79.6, 94.1, 74.0)), ('A', '355', 5, 'backbone clash', (71.128, 95.408, 76.778)), ('A', '356', 5, 'backbone clash', (71.128, 95.408, 76.778)), ('A', '357', 5, 'smoc Outlier', (69.051, 98.44400000000002, 80.604)), ('A', '375', 5, 'smoc Outlier', (74.116, 94.543, 71.315)), ('A', '388', 5, 'side-chain clash', (83.566, 93.626, 68.314)), ('A', '635', 5, 'side-chain clash', (83.566, 93.626, 68.314)), ('A', '398', 6, 'Dihedral angle:CB:CG:CD:OE1', (82.335, 111.038, 73.696)), ('A', '399', 6, 'backbone clash', (80.389, 115.385, 72.937)), ('A', '400', 6, 'backbone clash\ncablam Outlier\nsmoc Outlier', (80.389, 115.385, 72.937)), ('A', '401', 6, 'cablam Outlier', (78.0, 113.1, 77.7)), ('A', '403', 6, 'cablam Outlier', (80.2, 112.8, 82.7)), ('A', '470', 7, 'side-chain clash', (83.054, 72.623, 83.319)), ('A', '640', 7, 'side-chain clash', (82.503, 72.494, 83.536)), ('A', '641', 7, 'side-chain clash\nbackbone clash', (82.503, 72.494, 83.536)), ('A', '671', 7, 'side-chain clash', (83.054, 72.623, 83.319)), ('A', '249', 8, 'side-chain clash', (84.252, 120.32, 112.008)), ('A', '250', 8, 'cablam CA Geom Outlier', (85.4, 117.6, 116.1)), ('A', '252', 8, 'smoc Outlier', (90.479, 116.31700000000001, 114.426)), ('A', '302', 8, 'side-chain clash', (84.252, 120.32, 112.008)), ('A', '464', 9, 'side-chain clash\ncablam Outlier', (82.061, 82.745, 76.217)), ('A', '465', 9, 'Bond angle:C\nDihedral angle:CA:C', (78.604, 79.62899999999999, 76.24600000000001)), ('A', '466', 9, 'Bond angle:N:CA\nDihedral angle:N:CA', (80.402, 76.258, 76.003)), ('A', '518', 9, 'side-chain clash', (83.4, 81.427, 73.616)), ('A', '282', 10, 'Dihedral angle:CD:NE:CZ:NH1', (83.036, 107.59, 94.17699999999999)), ('A', '284', 10, 'smoc Outlier', (83.335, 110.329, 88.561)), ('A', '290', 10, 'Dihedral angle:CB:CG:CD:OE1', (88.533, 114.807, 89.147)), ('A', '261', 11, 'backbone clash', (75.613, 122.476, 93.371)), ('A', '321', 11, 'backbone clash', (75.613, 122.476, 93.371)), ('A', '324', 11, 'smoc Outlier', (74.94600000000001, 127.61, 95.281)), ('A', '533', 12, 'side-chain clash', (110.653, 98.502, 95.664)), ('A', '534', 12, 'smoc Outlier', (113.79400000000001, 97.223, 94.295)), ('A', '537', 12, 'side-chain clash', (110.653, 98.502, 95.664)), ('A', '586', 13, 'smoc Outlier', (93.705, 80.271, 87.015)), ('A', '587', 13, 'smoc Outlier', (95.926, 81.24900000000001, 84.086)), ('A', '589', 13, 'side-chain clash', (100.579, 77.136, 86.06)), ('A', '312', 14, 'side-chain clash', (70.365, 116.554, 106.331)), ('A', '313', 14, 'side-chain clash', (69.846, 114.831, 105.761)), ('A', '316', 14, 'side-chain clash', (69.846, 114.831, 105.761)), ('A', '305', 15, 'side-chain clash', (82.55, 126.956, 102.293)), ('A', '328', 15, 'smoc Outlier', (83.35, 126.399, 97.359)), ('A', '329', 15, 'side-chain clash', (82.55, 126.956, 102.293)), ('A', '564', 16, 'side-chain clash\nsmoc Outlier', (104.408, 73.5, 93.71)), ('A', '567', 16, 'side-chain clash', (104.408, 73.5, 93.71)), ('A', '568', 16, 'side-chain clash', (107.246, 72.204, 94.05)), ('A', '494', 17, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (88.923, 78.806, 113.15799999999999)), ('A', '496', 17, 'Dihedral angle:CD:NE:CZ:NH1', (92.11999999999999, 76.784, 109.255)), ('A', '263', 18, 'side-chain clash', (75.929, 124.734, 85.932)), ('A', '265', 18, 'side-chain clash', (75.929, 124.734, 85.932)), ('A', '379', 19, 'Dihedral angle:CA:C', (82.765, 101.326, 74.458)), ('A', '380', 19, 'Dihedral angle:N:CA', (85.67499999999998, 103.369, 75.681)), ('A', '303', 20, 'side-chain clash\nsmoc Outlier', (78.722, 120.825, 106.284)), ('A', '309', 20, 'side-chain clash', (78.722, 120.825, 106.284)), ('A', '649', 21, 'Dihedral angle:CA:C\ncablam Outlier', (81.864, 70.31700000000001, 114.12299999999999)), ('A', '650', 21, 'Dihedral angle:N:CA\ncablam Outlier', (79.751, 69.251, 111.197)), ('A', '601', 22, 'cablam Outlier', (69.8, 82.5, 106.5)), ('A', '604', 22, 'smoc Outlier', (69.67799999999998, 80.65499999999999, 112.242)), ('A', '255', 23, 'side-chain clash', (93.669, 115.028, 105.007)), ('A', '334', 23, 'side-chain clash', (93.669, 115.028, 105.007)), ('A', '570', 24, 'side-chain clash', (103.114, 66.211, 102.135)), ('A', '571', 24, 'side-chain clash', (103.114, 66.211, 102.135)), ('A', '654', 25, 'side-chain clash\nsmoc Outlier', (80.074, 65.814, 101.82)), ('A', '657', 25, 'side-chain clash', (80.074, 65.814, 101.82)), ('A', '550', 26, 'smoc Outlier', (101.106, 97.368, 101.459)), ('A', '553', 26, 'cablam Outlier', (105.1, 101.3, 105.3)), ('B', '355', 1, 'backbone clash', (67.347, 77.048, 80.356)), ('B', '356', 1, 'backbone clash', (67.347, 77.048, 80.356)), ('B', '358', 1, 'side-chain clash\ncablam Outlier', (64.123, 71.633, 78.053)), ('B', '360', 1, 'cablam CA Geom Outlier', (59.0, 76.9, 72.8)), ('B', '361', 1, 'side-chain clash', (61.779, 74.586, 68.314)), ('B', '362', 1, 'side-chain clash', (61.942, 80.254, 65.133)), ('B', '363', 1, 'side-chain clash\nsmoc Outlier', (61.942, 80.254, 65.133)), ('B', '364', 1, 'side-chain clash', (61.779, 74.586, 68.314)), ('B', '365', 1, 'cablam Outlier', (62.4, 70.6, 63.4)), ('B', '366', 1, 'side-chain clash\ncablam Outlier\nsmoc Outlier', (63.281, 66.892, 68.316)), ('B', '367', 1, 'side-chain clash\nbackbone clash', (57.833, 69.072, 71.041)), ('B', '368', 1, 'side-chain clash\nDihedral angle:CA:C', (59.56, 67.318, 70.783)), ('B', '369', 1, 'side-chain clash\nDihedral angle:N:CA\ncablam Outlier', (63.134, 66.124, 71.163)), ('B', '370', 1, 'side-chain clash', (63.952, 69.942, 74.554)), ('B', '372', 1, 'side-chain clash\ncablam Outlier', (64.123, 71.633, 78.053)), ('B', '380', 1, 'side-chain clash', (76.509, 62.719, 76.421)), ('B', '393', 1, 'side-chain clash\nDihedral angle:CA:C', (73.532, 62.682, 76.295)), ('B', '394', 1, 'Dihedral angle:N:CA', (73.24000000000001, 64.141, 79.73400000000001)), ('B', '398', 1, 'smoc Outlier', (69.44200000000001, 60.471, 82.059)), ('B', '403', 1, 'cablam Outlier', (69.4, 60.0, 75.2)), ('B', '404', 1, 'cablam Outlier', (70.0, 60.8, 71.5)), ('B', '405', 1, 'side-chain clash\nsmoc Outlier', (69.978, 65.263, 69.522)), ('B', '406', 1, 'side-chain clash', (69.978, 65.263, 69.522)), ('B', '514', 2, 'side-chain clash', (91.086, 67.18, 39.158)), ('B', '516', 2, 'side-chain clash\nsmoc Outlier', (88.945, 70.097, 33.806)), ('B', '517', 2, 'side-chain clash', (89.705, 64.866, 35.412)), ('B', '519', 2, 'side-chain clash\nsmoc Outlier', (88.945, 70.097, 33.806)), ('B', '522', 2, 'smoc Outlier', (93.96300000000001, 73.953, 31.354000000000003)), ('B', '523', 2, 'side-chain clash', (99.385, 76.189, 33.93)), ('B', '524', 2, 'smoc Outlier', (98.44500000000001, 73.51400000000001, 35.599000000000004)), ('B', '525', 2, 'side-chain clash', (99.385, 76.189, 33.93)), ('B', '526', 2, 'side-chain clash', (95.764, 76.271, 30.555)), ('B', '527', 2, 'backbone clash', (94.429, 76.03, 36.481)), ('B', '528', 2, 'backbone clash', (94.429, 76.03, 36.481)), ('B', '529', 2, 'cablam Outlier', (96.6, 73.0, 40.9)), ('B', '536', 3, 'side-chain clash', (89.279, 66.12, 47.067)), ('B', '537', 3, 'smoc Outlier', (93.759, 63.474, 51.218)), ('B', '540', 3, 'side-chain clash', (93.415, 66.361, 53.662)), ('B', '548', 3, 'side-chain clash\nbackbone clash', (86.839, 71.457, 48.866)), ('B', '555', 3, 'side-chain clash\nsmoc Outlier', (89.279, 66.12, 47.067)), ('B', '556', 3, 'backbone clash', (86.839, 71.457, 48.866)), ('B', '483', 4, 'side-chain clash', (84.866, 86.855, 55.49)), ('B', '575', 4, 'side-chain clash', (86.166, 85.22, 49.665)), ('B', '577', 4, 'side-chain clash', (83.553, 80.0, 50.205)), ('B', '581', 4, 'side-chain clash', (85.079, 77.802, 55.977)), ('B', '582', 4, 'side-chain clash', (84.21, 81.111, 57.115)), ('B', '594', 4, 'side-chain clash', (84.866, 86.855, 55.49)), ('B', '493', 5, 'side-chain clash', (79.612, 82.169, 41.617)), ('B', '496', 5, 'side-chain clash\nDihedral angle:CD:NE:CZ:NH1', (80.68799999999999, 88.513, 41.56)), ('B', '497', 5, 'side-chain clash', (82.33, 89.896, 35.738)), ('B', '500', 5, 'side-chain clash', (83.271, 87.057, 40.91)), ('B', '501', 5, 'side-chain clash', (82.33, 89.896, 35.738)), ('B', '622', 6, 'smoc Outlier', (55.998000000000005, 78.192, 49.398)), ('B', '623', 6, 'side-chain clash', (61.754, 80.771, 49.104)), ('B', '624', 6, 'side-chain clash', (60.327, 84.332, 51.808)), ('B', '627', 6, 'side-chain clash', (61.754, 80.771, 49.104)), ('B', '628', 6, 'side-chain clash', (60.327, 84.332, 51.808)), ('B', '464', 7, 'Dihedral angle:CA:C\ncablam Outlier', (81.80199999999999, 85.958, 74.327)), ('B', '465', 7, 'side-chain clash\nDihedral angle:N:CA\ncablam Outlier', (80.51400000000001, 88.67899999999999, 76.615)), ('B', '466', 7, 'side-chain clash', (80.858, 91.628, 76.659)), ('B', '467', 7, 'Dihedral angle:CB:CG:CD:OE1', (86.088, 91.412, 73.84700000000001)), ('B', '469', 7, 'side-chain clash', (83.678, 94.049, 68.082)), ('B', '386', 8, 'side-chain clash', (73.501, 69.384, 60.248)), ('B', '387', 8, 'side-chain clash', (73.501, 69.384, 60.248)), ('B', '388', 8, 'side-chain clash', (70.573, 72.598, 63.687)), ('B', '389', 8, 'side-chain clash', (70.573, 72.598, 63.687)), ('B', '498', 9, 'side-chain clash', (77.467, 94.454, 37.897)), ('B', '649', 9, 'side-chain clash\ncablam Outlier', (73.744, 96.447, 36.561)), ('B', '652', 9, 'side-chain clash', (77.467, 94.454, 37.897)), ('B', '563', 10, 'side-chain clash', (95.98, 86.511, 49.51)), ('B', '567', 10, 'side-chain clash', (95.98, 86.511, 49.51)), ('B', '590', 10, 'side-chain clash\ncablam Outlier', (93.02, 84.043, 52.225)), ('B', '383', 11, 'smoc Outlier', (77.563, 63.685, 66.99700000000001)), ('B', '384', 11, 'side-chain clash', (78.062, 70.326, 66.925)), ('B', '390', 11, 'side-chain clash', (78.062, 70.326, 66.925)), ('B', '508', 12, 'side-chain clash', (90.536, 88.26, 44.242)), ('B', '571', 12, 'cablam Outlier', (94.4, 92.7, 42.9)), ('B', '573', 12, 'side-chain clash', (90.536, 88.26, 44.242)), ('B', '593', 13, 'side-chain clash', (86.098, 95.344, 53.765)), ('B', '662', 13, 'side-chain clash', (86.098, 95.344, 53.765)), ('B', '489', 14, 'cablam Outlier', (69.4, 82.3, 45.5)), ('B', '490', 14, 'cablam Outlier\nsmoc Outlier', (69.7, 86.0, 45.9)), ('B', '532', 15, 'side-chain clash', (97.627, 60.437, 44.188)), ('B', '534', 15, 'side-chain clash\nsmoc Outlier', (97.627, 60.437, 44.188)), ('B', '410', 16, 'side-chain clash', (73.201, 81.827, 65.666)), ('B', '635', 16, 'side-chain clash', (73.201, 81.827, 65.666)), ('B', '472', 17, 'side-chain clash', (97.034, 94.013, 58.485)), ('B', '591', 17, 'side-chain clash', (97.034, 94.013, 58.485)), ('B', '656', 18, 'side-chain clash', (83.06, 98.827, 45.219)), ('B', '659', 18, 'side-chain clash', (83.364, 98.668, 46.18)), ('B', '503', 19, 'Dihedral angle:CB:CG:CD:OE1', (87.299, 96.363, 36.506)), ('B', '504', 19, 'smoc Outlier', (90.10499999999999, 95.181, 34.247)), ('B', '631', 20, 'smoc Outlier', (67.29700000000001, 84.17699999999999, 55.88699999999999)), ('B', '632', 20, 'Dihedral angle:CB:CG:CD:OE1', (66.86, 83.742, 59.639)), ('B', '559', 21, 'backbone clash\ncablam Outlier', (96.153, 77.336, 50.86)), ('B', '560', 21, 'backbone clash', (96.153, 77.336, 50.86)), ('B', '461', 22, 'side-chain clash\nsmoc Outlier', (81.505, 77.483, 69.836)), ('B', '462', 22, 'side-chain clash', (81.505, 77.483, 69.836)), ('B', '600', 23, 'side-chain clash', (62.346, 89.97, 47.205)), ('B', '605', 23, 'side-chain clash', (62.346, 89.97, 47.205)), ('B', '477', 24, 'side-chain clash', (103.213, 96.245, 50.546)), ('B', '478', 24, 'side-chain clash', (103.213, 96.245, 50.546)), ('C', '68', 1, 'side-chain clash', (70.701, 99.119, 101.927)), ('C', '69', 1, 'side-chain clash\nDihedral angle:CA:C\ncablam CA Geom Outlier', (69.435, 101.077, 101.238)), ('C', '70', 1, 'Dihedral angle:N:CA\nDihedral angle:CA:C\ncablam CA Geom Outlier', (68.32499999999999, 103.97, 99.148)), ('C', '71', 1, 'Dihedral angle:N:CA\ncablam Outlier', (71.30199999999999, 103.26700000000001, 96.898)), ('C', '73', 2, 'side-chain clash', (71.066, 115.275, 96.712)), ('C', '75', 2, 'side-chain clash\nsmoc Outlier', (78.484, 114.136, 93.64))]
data['omega'] = [('A', ' 402 ', 'PRO', None, (78.095, 114.72299999999998, 79.565))]
data['rama'] = [('A', ' 276 ', 'ASP', 0.001565037521759401, (75.779, 109.79999999999998, 111.62099999999998))]
data['smoc'] = [('A', 252, u'GLU', 0.6842072370480395, (90.479, 116.31700000000001, 114.426)), ('A', 277, u'SER', 0.7090819788320434, (78.06400000000001, 111.17499999999998, 108.89)), ('A', 284, u'VAL', 0.7331032664634252, (83.335, 110.329, 88.561)), ('A', 294, u'LEU', 0.7569187821411199, (91.96300000000001, 116.65499999999999, 95.41400000000002)), ('A', 299, u'ASP', 0.7385589131140864, (86.62299999999999, 110.833, 103.421)), ('A', 303, u'GLU', 0.6816997945519632, (80.46900000000001, 121.793, 106.88799999999999)), ('A', 318, u'PHE', 0.7319341793390489, (71.516, 117.859, 97.44500000000001)), ('A', 324, u'MET', 0.6986097211182315, (74.94600000000001, 127.61, 95.281)), ('A', 328, u'LEU', 0.7100398515253886, (83.35, 126.399, 97.359)), ('A', 336, u'GLN', 0.6570311074962426, (92.94900000000001, 106.083, 106.634)), ('A', 345, u'GLU', 0.6576245496411536, (95.289, 103.418, 83.17699999999999)), ('A', 357, u'ASP', 0.7579881718250793, (69.051, 98.44400000000002, 80.604)), ('A', 375, u'LYS', 0.7751896160016867, (74.116, 94.543, 71.315)), ('A', 384, u'GLN', 0.7573607115757431, (88.738, 99.143, 85.933)), ('A', 385, u'GLU', 0.7788966652355798, (89.582, 100.11999999999999, 89.51400000000001)), ('A', 400, u'ASN', 0.6857476716141907, (78.74600000000001, 115.63, 75.0)), ('A', 406, u'LEU', 0.7782970731449622, (78.804, 102.695, 84.91000000000001)), ('A', 473, u'HIS', 0.6768382872767604, (93.35, 61.985, 88.11)), ('A', 478, u'ARG', 0.7467436396688932, (101.871, 65.91600000000001, 93.958)), ('A', 494, u'GLU', 0.6893360955658484, (88.923, 78.806, 113.15799999999999)), ('A', 503, u'GLU', 0.6930751414097716, (96.533, 67.298, 111.806)), ('A', 510, u'ALA', 0.766403783067155, (103.402, 79.32199999999999, 101.815)), ('A', 521, u'GLN', 0.6563597285573934, (113.476, 85.84700000000001, 116.012)), ('A', 531, u'VAL', 0.7299867313905604, (114.568, 91.119, 100.181)), ('A', 534, u'GLN', 0.7121927405395954, (113.79400000000001, 97.223, 94.295)), ('A', 542, u'ALA', 0.7368256738555045, (106.959, 90.915, 86.141)), ('A', 547, u'GLU', 0.7750030294516375, (98.18499999999999, 88.73100000000001, 96.1)), ('A', 550, u'GLU', 0.67885498121144, (101.106, 97.368, 101.459)), ('A', 561, u'ASP', 0.7290428974329768, (107.573, 79.782, 93.233)), ('A', 564, u'ARG', 0.7292948656583361, (105.59, 75.23100000000001, 93.84400000000001)), ('A', 573, u'CYS', 0.7664674707428798, (99.029, 73.584, 100.504)), ('A', 586, u'ARG', 0.7795117327644707, (93.705, 80.271, 87.015)), ('A', 587, u'ASN', 0.7783349139760832, (95.926, 81.24900000000001, 84.086)), ('A', 594, u'ILE', 0.7711654662283801, (88.337, 76.486, 95.039)), ('A', 604, u'ARG', 0.7138003271975899, (69.67799999999998, 80.65499999999999, 112.242)), ('A', 609, u'LEU', 0.7056261616965609, (75.49100000000001, 84.703, 117.059)), ('A', 631, u'MET', 0.6857067423133223, (77.342, 89.765, 95.699)), ('A', 636, u'GLY', 0.7184880873561518, (81.554, 84.147, 90.651)), ('A', 654, u'GLU', 0.7180390317072092, (82.252, 67.92, 105.69)), ('A', 663, u'ASP', 0.7533598997924597, (92.273, 60.615, 96.21100000000001)), ('A', 675, u'ARG', 0.6891989925474925, (97.63199999999999, 71.003, 76.40400000000001)), ('B', 346, u'THR', 0.7109179187941728, (85.034, 60.088, 69.15799999999999)), ('B', 363, u'TYR', 0.7159622934493014, (63.336, 76.329, 64.854)), ('B', 366, u'CYS', 0.6164592761372675, (60.509, 68.05199999999999, 65.524)), ('B', 383, u'SER', 0.7035292603501746, (77.563, 63.685, 66.99700000000001)), ('B', 398, u'GLU', 0.6708898199395987, (69.44200000000001, 60.471, 82.059)), ('B', 405, u'GLY', 0.6794805499611944, (68.49000000000001, 64.263, 71.807)), ('B', 461, u'GLU', 0.7574091872822284, (79.04700000000001, 77.87299999999999, 69.18199999999999)), ('B', 473, u'HIS', 0.7352321644041662, (94.62499999999999, 101.282, 59.142)), ('B', 490, u'CYS', 0.67884783313373, (69.709, 86.023, 45.926)), ('B', 504, u'LYS', 0.689550857269709, (90.10499999999999, 95.181, 34.247)), ('B', 516, u'ARG', 0.6670002023611219, (90.303, 65.392, 38.009)), ('B', 519, u'ARG', 0.685934145822834, (94.35799999999999, 67.95100000000001, 30.341)), ('B', 522, u'GLU', 0.6556324290816626, (93.96300000000001, 73.953, 31.354000000000003)), ('B', 524, u'ALA', 0.682681092324372, (98.44500000000001, 73.51400000000001, 35.599000000000004)), ('B', 534, u'GLN', 0.6725055487744219, (96.71400000000001, 60.537, 48.31699999999999)), ('B', 537, u'GLU', 0.6897384920912959, (93.759, 63.474, 51.218)), ('B', 552, u'GLU', 0.7049412937965274, (81.55, 62.94, 41.529)), ('B', 555, u'LEU', 0.7203056842159896, (87.109, 66.526, 46.241)), ('B', 587, u'ASN', 0.7547946589953575, (91.12799999999999, 82.03, 63.368)), ('B', 609, u'LEU', 0.6264574657623265, (60.226000000000006, 86.52199999999999, 39.561)), ('B', 622, u'ARG', 0.6909372701369928, (55.998000000000005, 78.192, 49.398)), ('B', 631, u'MET', 0.7168457956934284, (67.29700000000001, 84.17699999999999, 55.88699999999999)), ('B', 653, u'GLN', 0.6695600983918698, (76.26100000000001, 102.55199999999999, 45.293000000000006)), ('B', 675, u'ARG', 0.7350745070402399, (99.956, 90.757, 68.02499999999999)), ('C', 75, u'VAL', 0.7220883245767878, (75.831, 115.589, 94.428))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-23665/7m4r/Model_validation_1/validation_cootdata/molprobity_probe7m4r_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

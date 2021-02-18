
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
data['clusters'] = []
data['rama'] = []
data['rota'] = []
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' F 261  CYS  HB2', ' F 488  VAL HG23', -0.685, (264.016, 263.211, 316.351)), (' F 503  LEU HD23', ' F 505  HIS  H  ', -0.64, (249.576, 269.6, 300.304)), (' F 482  ARG  HD3', ' F 609  ASP  H  ', -0.582, (261.952, 260.415, 320.098)), (' F 284  PRO  HG3', ' F 440  LEU HD13', -0.571, (274.259, 258.061, 298.409)), (' F 144  LEU  HA ', ' F 148  LEU HD23', -0.57, (256.982, 281.839, 299.59)), (' F 108  LEU HD23', ' F 112  LYS  HB3', -0.569, (226.268, 271.877, 305.66)), (' F 574  VAL HG23', ' F 576  ALA  H  ', -0.563, (249.939, 241.735, 289.63)), (' G 433  VAL HG12', ' G 512  VAL HG22', -0.537, (228.454, 257.777, 251.609)), (' F 445  THR HG23', ' F 446  ILE HG13', -0.526, (262.181, 259.799, 293.518)), (' F  19  SER  N  ', ' F  23  GLU  OE2', -0.524, (211.642, 247.457, 279.232)), (' F 177  ARG  HD3', ' F 498  CYS  HB2', -0.522, (245.4, 274.49, 314.242)), (' F 183  TYR  OH ', ' F 187  LYS  NZ ', -0.521, (236.462, 269.053, 301.992)), (' G 452  LEU HD23', ' G 492  LEU  HB3', -0.517, (217.634, 267.888, 267.27)), (' G 393  THR  HB ', ' G 523  THR  HA ', -0.509, (220.689, 256.313, 233.016)), (' F 174  LYS  NZ ', ' F 496  THR  OG1', -0.507, (247.393, 279.124, 318.585)), (' F 303  ASP  N  ', ' F 303  ASP  OD1', -0.505, (265.602, 273.245, 270.714)), (' G 418  ILE  HA ', ' G 422  ASN HD22', -0.502, (223.211, 258.634, 263.788)), (' F 107  VAL HG23', ' F 108  LEU HD12', -0.501, (225.738, 267.216, 303.084)), (' G 376  THR  HB ', ' G 435  ALA  HB3', -0.501, (235.62, 259.779, 254.293)), (' F 501  ALA  O  ', ' F 507  SER  OG ', -0.5, (246.789, 273.928, 304.967)), (' F 481  LYS  HG2', ' F 487  VAL  HB ', -0.496, (258.986, 263.828, 312.132)), (' F 374  HIS  ND1', ' F 405  GLY  O  ', -0.496, (255.453, 261.702, 285.134)), (' F 544  ILE  O  ', ' F 547  SER  OG ', -0.494, (260.203, 248.653, 275.358)), (' F 349  TRP  HE1', ' F 359  LEU HD22', -0.494, (247.347, 274.488, 282.767)), (' F 177  ARG  NH2', ' F 181  GLU  OE1', -0.493, (240.944, 272.602, 317.038)), (' G 341  VAL HG13', ' G 342  PHE  HD2', -0.49, (228.175, 266.939, 245.302)), (' F  47  SER  O  ', ' F  51  ASN  ND2', -0.489, (243.261, 277.171, 283.852)), (' F  21  ILE HG21', ' F  84  PRO  HD2', -0.488, (215.535, 251.097, 288.527)), (' F 155  SER  O  ', ' F 161  ARG  NH1', -0.483, (269.787, 275.514, 303.716)), (' F  42  GLN  OE1', ' G 498  GLN  NE2', -0.478, (232.501, 275.002, 273.553)), (' G 360  ASN  HA ', ' G 524  VAL HG11', -0.474, (221.215, 261.949, 231.477)), (' F 481  LYS  O  ', ' F 486  GLY  N  ', -0.471, (259.703, 260.439, 312.487)), (' G 405  ASP  N  ', ' G 504  GLY  O  ', -0.46, (235.65, 261.462, 264.958)), (' F 394  ASN  HB3', ' F 562  LYS  HE2', -0.459, (237.976, 257.331, 287.034)), (' G 361  CYS  H  ', ' G 524  VAL HG21', -0.447, (223.018, 262.345, 233.109)), (' F  31  LYS  O  ', ' F  35  GLU  HG2', -0.446, (222.897, 264.57, 277.384)), (' F 469  PRO  HD2', ' F 472  GLN  HB2', -0.444, (243.315, 263.968, 321.544)), (' F 118  THR  O  ', ' F 122  THR  OG1', -0.436, (237.037, 281.286, 303.264)), (' F 528  ALA  HB2', ' F 574  VAL HG12', -0.433, (253.775, 243.989, 286.854)), (' F 398  GLU  HB2', ' F 514  ARG  HE ', -0.433, (244.204, 260.436, 293.621)), (' F  41  TYR  OH ', ' G 500  THR  OG1', -0.429, (239.133, 273.165, 271.469)), (' F 371  THR  HA ', ' F 374  HIS  HB3', -0.422, (257.998, 264.871, 284.107)), (' F 313  LYS  HA ', ' F 316  VAL HG12', -0.419, (258.504, 258.614, 268.759)), (' F 152  MET  O  ', ' F 161  ARG  NH2', -0.419, (266.601, 273.652, 303.548)), (' F 586  ASN  HA ', ' F 589  GLU  HG2', -0.411, (266.16, 244.743, 295.257)), (' G 395  VAL HG13', ' G 515  PHE  HE2', -0.411, (226.223, 258.668, 240.965)), (' G 444  LYS  HB2', ' G 444  LYS  HE2', -0.411, (231.461, 281.206, 265.426)), (' G 393  THR  OG1', ' G 394  ASN  N  ', -0.407, (219.763, 256.915, 236.832)), (' F 538  PRO  HB2', ' F 540  HIS  CD2', -0.4, (270.376, 247.716, 288.058))]
data['cablam'] = [('F', '197', 'GLU', 'check CA trace,carbonyls, peptide', 'bend\nT-S-H', (231.8, 255.8, 308.1)), ('F', '267', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nGGSSS', (264.9, 268.0, 305.1)), ('F', '334', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nB-S--', (257.9, 278.6, 277.0)), ('F', '338', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (255.5, 290.0, 279.0)), ('F', '467', 'GLU', 'check CA trace,carbonyls, peptide', ' \nHT-S-', (239.0, 259.5, 318.0)), ('F', '486', 'GLY', 'check CA trace,carbonyls, peptide', ' \nII-EE', (261.7, 259.9, 312.8)), ('F', '545', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (261.8, 251.9, 274.7)), ('F', '583', 'PRO', ' three-ten', 'helix\n-HHHH', (259.0, 244.9, 293.4)), ('F', '139', 'GLN', 'check CA trace', ' \nB----', (263.0, 294.9, 305.2)), ('F', '353', 'LYS', 'check CA trace', 'turn\nEETTE', (236.7, 265.8, 272.7)), ('G', '394', 'ASN', 'check CA trace,carbonyls, peptide', ' \n-S---', (219.6, 257.0, 239.3)), ('G', '415', 'THR', ' beta sheet', ' \nT--SS', (225.9, 249.4, 262.8)), ('G', '417', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\n-SSHH', (224.5, 255.1, 266.6)), ('G', '442', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (232.0, 274.0, 259.7)), ('G', '477', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (206.0, 253.1, 280.8)), ('G', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (202.6, 264.8, 277.1)), ('G', '488', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nTTT--', (210.8, 261.4, 278.1)), ('G', '489', 'TYR', 'check CA trace,carbonyls, peptide', ' \nTT--S', (214.3, 262.3, 276.7)), ('G', '393', 'THR', 'check CA trace', 'bend\n--S--', (221.4, 256.1, 236.0))]
data['smoc'] = [('F', 20, u'THR', 0.769270353330356, (213.07899999999998, 247.20999999999998, 282.67400000000004)), ('F', 56, u'GLU', 0.8643354584044073, (240.309, 290.472, 285.59299999999996)), ('F', 64, u'ASN', 0.8880111913509116, (230.814, 281.374, 285.047)), ('F', 67, u'ASP', 0.8669578432104067, (229.371, 277.139, 288.183)), ('F', 86, u'GLN', 0.7173694350639661, (219.153, 246.252, 293.274)), ('F', 87, u'GLU', 0.7378023641927561, (218.342, 244.92700000000002, 289.78499999999997)), ('F', 101, u'GLN', 0.8413253585049107, (224.629, 259.377, 292.445)), ('F', 108, u'LEU', 0.891452033767042, (223.844, 269.553, 303.635)), ('F', 116, u'LEU', 0.8571493214992126, (232.107, 274.83299999999997, 302.134)), ('F', 117, u'ASN', 0.8005728823751941, (232.865, 277.61400000000003, 299.65000000000003)), ('F', 118, u'THR', 0.8632297910755903, (233.71699999999998, 280.172, 302.355)), ('F', 123, u'MET', 0.863168136264712, (242.32200000000003, 278.14500000000004, 302.637)), ('F', 136, u'ASP', 0.7428216696705353, (260.582, 293.869, 314.27799999999996)), ('F', 141, u'CYS', 0.7316785535430688, (259.54, 289.69599999999997, 301.582)), ('F', 142, u'LEU', 0.7099099631230579, (258.52299999999997, 287.89799999999997, 298.38599999999997)), ('F', 172, u'VAL', 0.8534889764316925, (250.227, 281.062, 308.394)), ('F', 178, u'PRO', 0.8240304966708085, (239.82000000000002, 277.621, 314.455)), ('F', 188, u'ASN', 0.8400444417511609, (232.847, 264.5, 308.811)), ('F', 207, u'TYR', 0.8048288763531951, (239.874, 252.12800000000001, 296.22099999999995)), ('F', 216, u'ASP', 0.7608133950699173, (236.123, 242.883, 295.974)), ('F', 221, u'GLN', 0.8301433065877969, (241.15, 246.731, 303.729)), ('F', 224, u'GLU', 0.8192465079676365, (245.371, 247.018, 306.632)), ('F', 229, u'THR', 0.8114996027898237, (253.25, 246.97899999999998, 303.191)), ('F', 232, u'GLU', 0.7790896522846652, (259.15200000000004, 246.117, 304.399)), ('F', 248, u'LEU', 0.8266986583138055, (273.98599999999993, 265.92199999999997, 307.846)), ('F', 256, u'ILE', 0.7510323288380182, (272.35, 267.73299999999995, 316.127)), ('F', 261, u'CYS', 0.8504093406326794, (266.284, 261.634, 314.99799999999993)), ('F', 267, u'LEU', 0.7467081446350997, (264.892, 267.97499999999997, 305.115)), ('F', 292, u'ASP', 0.8445787676960375, (274.33099999999996, 265.78799999999995, 284.241)), ('F', 296, u'ALA', 0.8706469853081565, (275.325, 269.222, 277.03)), ('F', 329, u'GLU', 0.845141179282686, (250.49, 274.28, 267.624)), ('F', 332, u'MET', 0.8472359522645984, (252.24599999999998, 276.514, 275.08299999999997)), ('F', 342, u'ALA', 0.8232047704857929, (249.971, 283.312, 284.40999999999997)), ('F', 351, u'LEU', 0.875301229402298, (239.873, 268.989, 277.9309999999999)), ('F', 355, u'ASP', 0.8791010608411935, (241.758, 268.037, 272.957)), ('F', 375, u'GLU', 0.8801971040969528, (253.853, 265.137, 281.97799999999995)), ('F', 384, u'ALA', 0.8718870307493115, (243.92200000000003, 255.518, 276.166)), ('F', 392, u'LEU', 0.8639712335686592, (234.375, 256.26099999999997, 283.22599999999994)), ('F', 404, u'VAL', 0.7800772052550367, (251.537, 255.984, 285.08099999999996)), ('F', 408, u'MET', 0.8010557657969004, (258.507, 256.895, 282.019)), ('F', 421, u'ILE', 0.8606972523687042, (269.628, 259.95599999999996, 272.163)), ('F', 426, u'PRO', 0.8684840649885968, (279.452, 258.116, 274.328)), ('F', 433, u'GLU', 0.7949894130771994, (279.949, 254.72899999999998, 292.442)), ('F', 446, u'ILE', 0.7973222884789185, (260.98499999999996, 258.234, 296.376)), ('F', 453, u'THR', 0.7899280762603395, (253.046, 260.302, 303.168)), ('F', 460, u'ARG', 0.8180645323749897, (244.283, 262.67900000000003, 308.83)), ('F', 480, u'MET', 0.8300783535317356, (254.02200000000002, 259.697, 315.23599999999993)), ('F', 487, u'VAL', 0.8272752989829494, (261.866, 263.656, 313.23499999999996)), ('F', 493, u'HIS', 0.8209061639235914, (254.622, 273.372, 320.133)), ('F', 498, u'CYS', 0.8148340950359683, (247.996, 273.93899999999996, 313.48199999999997)), ('F', 511, u'SER', 0.8587785236960064, (243.637, 263.066, 299.241)), ('F', 525, u'PHE', 0.8189226228722101, (254.70299999999997, 248.414, 286.61400000000003)), ('F', 530, u'CYS', 0.805906269239114, (261.10200000000003, 245.23499999999999, 282.175)), ('F', 536, u'GLU', 0.8744327641924509, (269.14000000000004, 241.38100000000003, 281.21599999999995)), ('F', 542, u'CYS', 0.7850875479954682, (266.44599999999997, 248.95100000000002, 282.592)), ('F', 552, u'GLN', 0.893947619921362, (251.125, 246.281, 274.33299999999997)), ('F', 557, u'MET', 0.8796362899033755, (245.624, 248.26399999999998, 281.141)), ('F', 575, u'GLY', 0.8067558311108388, (249.403, 239.132, 287.962)), ('F', 589, u'GLU', 0.8329077068224922, (269.019, 246.224, 296.224)), ('F', 597, u'ASP', 0.8499167854912364, (277.767, 247.74099999999999, 304.93499999999995)), ('F', 608, u'THR', 0.8648146134159287, (261.34900000000005, 257.455, 320.834)), ('F', 610, u'TRP', 0.8031729005263879, (263.302, 263.452, 323.355)), ('F', 702, u'NAG', 0.7407139672363904, (282.90299999999996, 248.196, 288.512)), ('G', 521, u'PRO', 0.7755336246255424, (215.88400000000001, 253.809, 231.076)), ('G', 340, u'GLU', 0.8339740374027944, (226.51299999999998, 272.811, 244.191)), ('G', 365, u'TYR', 0.8294756442002625, (234.646, 261.202, 238.535)), ('G', 379, u'CYS', 0.8751304817351134, (233.80700000000002, 252.61499999999998, 247.206)), ('G', 390, u'LEU', 0.7879389045802876, (230.324, 251.49, 232.369)), ('G', 392, u'PHE', 0.7874528837354053, (224.232, 253.59, 235.712)), ('G', 400, u'PHE', 0.8603968494091139, (225.066, 265.33599999999996, 255.80200000000002)), ('G', 402, u'ILE', 0.7867069576829641, (229.225, 263.58, 260.65200000000004)), ('G', 406, u'GLU', 0.8746114832761698, (231.79299999999998, 258.173, 263.78599999999994)), ('G', 413, u'GLY', 0.8621118046720538, (226.583, 246.008, 257.148)), ('G', 428, u'ASP', 0.7614434044187045, (225.056, 245.415, 249.012)), ('G', 440, u'ASN', 0.8974576242307369, (237.997, 275.772, 259.05400000000003)), ('G', 442, u'ASP', 0.8852252135538996, (232.02, 274.03, 259.71)), ('G', 453, u'TYR', 0.8475048106874931, (221.2, 264.262, 265.23799999999994)), ('G', 464, u'PHE', 0.9000862209632878, (217.45600000000002, 254.875, 253.07399999999998)), ('G', 476, u'GLY', 0.7544532634994158, (209.707, 253.404, 280.28599999999994)), ('G', 485, u'GLY', 0.7510959695208493, (210.74399999999997, 264.191, 282.507)), ('G', 495, u'TYR', 0.8818927402127056, (226.612, 268.69599999999997, 267.83799999999997)), ('G', 497, u'PHE', 0.8905658893683859, (232.11599999999999, 271.768, 266.887)), ('G', 507, u'PRO', 0.8777274531176096, (233.287, 267.83, 261.893)), ('G', 508, u'TYR', 0.8597098009091366, (233.92600000000002, 265.697, 258.807))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22922/7kmb/Model_validation_1/validation_cootdata/molprobity_probe7kmb_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

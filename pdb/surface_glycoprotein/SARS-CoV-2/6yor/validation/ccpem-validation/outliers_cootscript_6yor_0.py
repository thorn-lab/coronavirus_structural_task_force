
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
data['cbeta'] = []
data['jpred'] = []
data['probe'] = [(' A 378  LYS  NZ ', ' B  57  GLU  OE2', -0.698, (225.869, 214.954, 220.631)), (' E 378  LYS  NZ ', ' H  57  GLU  OE2', -0.697, (225.268, 233.162, 244.808)), (' B 123  PRO  HB3', ' B 149  TYR  HB3', -0.62, (230.2, 260.915, 206.94)), (' H 123  PRO  HB3', ' H 149  TYR  HB3', -0.618, (229.898, 187.016, 258.789)), (' A 383  SER  OG ', ' B 104  THR  OG1', -0.577, (225.761, 215.882, 205.783)), (' E 383  SER  OG ', ' H 104  THR  OG1', -0.568, (223.377, 232.506, 259.564)), (' C 190  ALA  O  ', ' C 194  LYS  HG3', -0.499, (250.255, 276.398, 203.248)), (' L 190  ALA  O  ', ' L 194  LYS  HG3', -0.497, (250.598, 172.407, 263.658)), (' A 485  GLY  O  ', ' H 119  SER  OG ', -0.496, (232.275, 189.889, 246.568)), (' A 517  LEU  HB2', ' C  34  ILE HG22', -0.472, (229.618, 203.699, 202.146)), (' C  67  ARG  HB2', ' C  82  SER  O  ', -0.465, (233.589, 224.567, 183.594)), (' C  34  ILE  O  ', ' C  36  LYS  N  ', -0.464, (234.616, 207.03, 201.898)), (' E 517  LEU  HB2', ' L  34  ILE HG22', -0.462, (227.225, 244.646, 264.114)), (' L  34  ILE  O  ', ' L  36  LYS  N  ', -0.46, (231.75, 240.909, 264.598)), (' L  67  ARG  HB2', ' L  82  SER  O  ', -0.456, (229.05, 222.972, 283.193)), (' E 447  GLY  HA2', ' E 498  GLN  HG2', -0.44, (212.261, 248.396, 225.332)), (' A 489  TYR  HH ', ' H 119  SER  N  ', -0.437, (232.421, 193.774, 246.477)), (' A 447  GLY  HA2', ' A 498  GLN  HG2', -0.436, (210.639, 199.8, 239.101)), (' H 105  PRO  HG3', ' L  97  TYR  CZ ', -0.43, (228.332, 230.756, 262.945)), (' B 105  PRO  HG3', ' C  97  TYR  CZ ', -0.428, (230.62, 217.468, 203.315)), (' A 497  PHE  CE2', ' A 507  PRO  HB3', -0.427, (214.926, 201.387, 231.198)), (' A 379  CYS  HA ', ' A 432  CYS  HA ', -0.426, (223.421, 209.435, 213.099)), (' E 379  CYS  HA ', ' E 432  CYS  HA ', -0.425, (221.906, 238.672, 252.506)), (' A 393  THR  HA ', ' A 522  ALA  HA ', -0.424, (224.994, 197.544, 198.361)), (' E 497  PHE  CE2', ' E 507  PRO  HB3', -0.42, (215.51, 247.058, 233.794)), (' E 393  THR  HA ', ' E 522  ALA  HA ', -0.415, (222.193, 250.489, 267.718)), (' A 393  THR HG21', ' A 518  LEU  H  ', -0.415, (229.757, 198.151, 199.919)), (' E 401  VAL HG22', ' E 509  ARG  HG2', -0.409, (213.955, 247.663, 240.23)), (' H 213  LYS  HA ', ' H 213  LYS  HD2', -0.408, (224.505, 177.253, 266.112)), (' E 347  PHE  HB3', ' E 348  ALA  H  ', -0.408, (215.424, 251.506, 241.453)), (' E 393  THR HG21', ' E 518  LEU  H  ', -0.407, (226.919, 249.856, 266.54)), (' A 360  ASN  H  ', ' A 523  THR  HB ', -0.407, (219.402, 194.668, 199.729)), (' B 188  VAL HG11', ' B 198  TYR  CE1', -0.406, (224.718, 265.686, 185.635)), (' H 188  VAL HG11', ' H 198  TYR  CE1', -0.401, (223.147, 182.618, 280.071)), (' A 412  PRO  HB3', ' A 426  PRO  O  ', -0.4, (233.027, 206.946, 215.963)), (' H 150  PHE  HA ', ' H 151  PRO  HA ', -0.4, (231.528, 193.699, 255.249))]
data['smoc'] = [('E', 338, u'PHE', 0.5783110914578379, (210.571, 248.282, 254.84)), ('E', 344, u'ALA', 0.7093754384271452, (208.51399999999998, 252.14899999999997, 246.141)), ('E', 355, u'ARG', 0.6438253581133887, (220.14499999999998, 254.284, 250.41299999999998)), ('E', 398, u'ASP', 0.6088865086126523, (220.10299999999998, 250.072, 249.33)), ('E', 414, u'GLN', 0.4875370979594858, (232.547, 239.907, 242.442)), ('E', 432, u'CYS', 0.5545926861407242, (221.218, 240.251, 252.54299999999998)), ('E', 439, u'ASN', 0.5830407802578079, (209.51, 243.268, 234.02100000000002)), ('E', 481, u'ASN', 0.5521975827996335, (237.39600000000002, 268.953, 226.833)), ('E', 505, u'TYR', 0.6844010641340127, (217.883, 241.183, 230.147)), ('E', 506, u'GLN', 0.7074147502352425, (214.55700000000002, 241.98600000000002, 231.815)), ('E', 515, u'PHE', 0.5493476745574719, (223.90800000000002, 245.73999999999998, 259.29799999999994)), ('E', 517, u'LEU', 0.5245906550050331, (227.153, 247.266, 265.14700000000005)), ('H', 21, u'SER', 0.5101578283125009, (218.46, 213.971, 248.232)), ('H', 41, u'PRO', 0.2852424297803812, (233.147, 205.141, 259.59)), ('H', 45, u'LEU', 0.47816016649678805, (233.494, 215.444, 259.84400000000005)), ('H', 53, u'PRO', 0.6436510361585275, (219.08, 226.611, 245.698)), ('H', 54, u'GLY', 0.6808820328578358, (217.71899999999997, 230.038, 244.73)), ('H', 64, u'PHE', 0.5482429395686049, (235.748, 217.055, 246.728)), ('H', 71, u'SER', 0.6928773461224151, (222.768, 220.14499999999998, 242.465)), ('H', 86, u'LEU', 0.48182224362486376, (231.218, 205.035, 243.142)), ('H', 94, u'TYR', 0.5586852432056446, (226.39800000000002, 211.811, 254.485)), ('H', 97, u'ALA', 0.5188007529835891, (223.19, 220.748, 256.848)), ('H', 111, u'GLN', 0.5514623439854626, (219.656, 212.36800000000002, 260.327)), ('H', 117, u'VAL', 0.4452803347294981, (229.60299999999998, 200.68, 248.106)), ('H', 118, u'ALA', 0.47221851091405787, (230.091, 196.9, 248.38100000000003)), ('H', 132, u'SER', 0.5189679148161821, (234.55200000000002, 174.36200000000002, 283.92599999999993)), ('H', 137, u'GLY', 0.39455098812170025, (230.701, 178.446, 292.173)), ('H', 138, u'GLY', 0.6524444650665132, (230.701, 181.934, 290.69599999999997)), ('H', 149, u'TYR', 0.5975175653067357, (231.623, 188.70899999999997, 256.694)), ('H', 150, u'PHE', 0.5662950202749002, (231.289, 191.854, 254.608)), ('H', 152, u'GLU', 0.5263097757473288, (229.02100000000002, 195.797, 258.335)), ('H', 157, u'SER', 0.6215069206531484, (221.04899999999998, 188.912, 270.23699999999997)), ('H', 181, u'SER', 0.4728943791192151, (235.439, 189.471, 262.49499999999995)), ('H', 187, u'THR', 0.5472186610306193, (228.32100000000003, 186.277, 281.459)), ('H', 192, u'SER', 0.749320099697813, (222.70899999999997, 177.907, 284.578)), ('H', 193, u'LEU', 0.6735844579150585, (224.904, 175.89100000000002, 282.192)), ('H', 202, u'VAL', 0.5879921002276068, (223.278, 186.425, 264.094)), ('H', 209, u'THR', 0.6940579034450295, (221.79399999999998, 185.165, 256.26599999999996)), ('L', 11, u'LEU', 0.18172296671433708, (240.04299999999998, 214.668, 277.792)), ('L', 16, u'GLY', 0.3086948211218526, (231.102, 218.197, 288.337)), ('L', 21, u'ILE', 0.48997430522963603, (238.815, 222.38600000000002, 274.884)), ('L', 25, u'SER', 0.46781797420234256, (242.829, 228.691, 263.709)), ('L', 31, u'TYR', 0.6288778262074255, (234.36100000000002, 240.26399999999998, 260.99399999999997)), ('L', 39, u'LEU', 0.45249805347106536, (233.708, 230.20999999999998, 265.055)), ('L', 40, u'ALA', 0.13866362557170794, (231.23999999999998, 227.502, 266.09099999999995)), ('L', 44, u'GLN', 0.5196083820447944, (228.24899999999997, 214.65200000000002, 268.14700000000005)), ('L', 50, u'PRO', 0.4541793418408107, (226.11599999999999, 216.95200000000003, 264.96)), ('L', 68, u'PHE', 0.4603170500241638, (228.399, 225.248, 278.018)), ('L', 88, u'ASP', 0.4000005041963228, (228.129, 215.364, 278.132)), ('L', 101, u'PRO', 0.6692543886408051, (235.51399999999998, 226.207, 252.313)), ('L', 112, u'ILE', 0.18230456147425886, (234.268, 211.069, 282.612)), ('L', 119, u'PRO', 0.5727820686798427, (239.36, 192.805, 284.509)), ('L', 120, u'SER', 0.618517411547968, (237.819, 189.36800000000002, 284.78099999999995)), ('L', 127, u'SER', 0.7164867770378707, (235.412, 175.24499999999998, 268.194)), ('L', 128, u'ASP', 0.6866143536995968, (235.61499999999998, 171.83700000000002, 266.545)), ('L', 132, u'LYS', 0.5966921505365432, (237.253, 171.501, 259.962)), ('L', 133, u'SER', 0.5388431459754246, (237.509, 174.657, 257.825)), ('L', 137, u'SER', 0.5681068000649346, (240.64299999999997, 181.394, 266.45099999999996)), ('L', 148, u'ARG', 0.414151422931894, (241.255, 201.112, 279.006)), ('L', 149, u'GLU', 0.6099281756907647, (245.018, 200.52800000000002, 278.806)), ('L', 161, u'GLN', 0.6641121395568322, (253.135, 185.69299999999998, 269.83799999999997)), ('L', 171, u'GLU', 0.4661887135436381, (231.941, 201.29, 274.41099999999994)), ('L', 200, u'CYS', 0.4343611032991183, (246.611, 184.70399999999998, 277.605)), ('L', 213, u'LYS', 0.25970555805515816, (244.48100000000002, 182.171, 281.759)), ('L', 214, u'SER', 0.24755358685908735, (245.315, 179.126, 279.665)), ('A', 519, u'HIS', 0.6914314533485512, (233.32600000000002, 197.031, 196.568)), ('A', 338, u'PHE', 0.6501872694838949, (212.197, 200.0, 209.83800000000002)), ('A', 356, u'LYS', 0.6825433987028398, (218.82800000000003, 193.92600000000002, 212.324)), ('A', 358, u'ILE', 0.7254064189638022, (218.71099999999998, 195.702, 206.24599999999998)), ('A', 363, u'ALA', 0.6383474824229122, (214.577, 202.641, 202.541)), ('A', 387, u'LEU', 0.5136092595856439, (220.578, 209.784, 201.344)), ('A', 427, u'ASP', 0.614842149025271, (235.70999999999998, 206.842, 215.98100000000002)), ('A', 432, u'CYS', 0.47312386948351853, (222.624, 207.942, 213.206)), ('A', 443, u'SER', 0.648610540226106, (208.58800000000002, 200.725, 233.517)), ('A', 447, u'GLY', 0.7214921985857522, (210.32500000000002, 198.287, 239.048)), ('A', 448, u'ASN', 0.6413957126851868, (211.304, 196.817, 235.689)), ('A', 461, u'LEU', 0.6076524804967413, (234.816, 196.483, 224.023)), ('A', 487, u'ASN', 0.571411248401998, (236.12, 190.592, 245.194)), ('A', 492, u'LEU', 0.6992319131165281, (225.42700000000002, 192.089, 235.02)), ('A', 505, u'TYR', 0.652650452974776, (216.875, 207.26399999999998, 235.11599999999999)), ('A', 510, u'VAL', 0.4706336280490028, (217.83200000000002, 203.576, 221.142)), ('B', 8, u'GLY', 0.46186477320527863, (218.841, 241.847, 212.407)), ('B', 18, u'LEU', 0.5386435862037082, (224.782, 240.889, 222.77499999999998)), ('B', 41, u'PRO', 0.5629957876796643, (235.64399999999998, 242.85700000000003, 207.19)), ('B', 64, u'PHE', 0.6966675154842169, (236.70299999999997, 231.04299999999998, 220.36)), ('B', 65, u'GLN', 0.6428504803536226, (236.653, 228.74299999999997, 223.411)), ('B', 97, u'ALA', 0.5184650473922711, (225.272, 227.38100000000003, 208.972)), ('B', 110, u'GLY', 0.26199653880660206, (221.667, 232.39200000000002, 206.671)), ('B', 111, u'GLN', 0.3292648683057146, (222.231, 235.76299999999998, 205.05800000000002)), ('B', 112, u'GLY', 0.5954497510717818, (224.42200000000003, 236.781, 208.008)), ('B', 132, u'SER', 0.6630052983686481, (236.045, 274.239, 182.393)), ('B', 137, u'GLY', 0.6906520222144222, (232.796, 270.046, 173.944)), ('B', 138, u'GLY', 0.7197515307556716, (232.805, 266.56, 175.425)), ('B', 152, u'GLU', 0.6483690797768089, (229.624, 252.671, 207.66299999999998)), ('B', 163, u'LEU', 0.7430109234743781, (220.364, 260.257, 188.121)), ('B', 171, u'PRO', 0.6055649028402607, (233.995, 252.24499999999998, 198.621)), ('B', 174, u'LEU', 0.6151553309365841, (239.39200000000002, 254.309, 206.86200000000002)), ('B', 200, u'CYS', 0.6945603640342732, (223.89800000000002, 264.809, 195.859)), ('B', 211, u'VAL', 0.6974222993461031, (222.503, 266.335, 203.62)), ('B', 217, u'PRO', 0.6655831892247639, (231.005, 275.183, 188.69899999999998)), ('B', 218, u'LYS', 0.6639090905671077, (233.067, 277.638, 190.737)), ('C', 13, u'VAL', 0.016717350308243895, (242.292, 232.64499999999998, 183.781)), ('C', 18, u'ARG', 0.5761787927948859, (240.496, 225.814, 182.85600000000002)), ('C', 28, u'SER', 0.5254498032030063, (244.125, 212.635, 205.92700000000002)), ('C', 38, u'TYR', 0.5430378335652455, (235.47899999999998, 214.585, 203.903)), ('C', 40, u'ALA', 0.2682388269804062, (234.19899999999998, 220.454, 200.71299999999997)), ('C', 45, u'LYS', 0.5666490196920018, (230.76999999999998, 236.631, 196.569)), ('C', 54, u'ILE', 0.560329410568311, (231.347, 220.32000000000002, 196.096)), ('C', 63, u'GLY', 0.2932870738583101, (222.453, 224.278, 191.637)), ('C', 79, u'LEU', 0.5422105985378249, (238.795, 222.278, 192.484)), ('C', 81, u'ILE', 0.6364083269512624, (236.506, 225.20999999999998, 186.9)), ('C', 88, u'ASP', 0.4510688581539987, (232.547, 232.504, 188.30200000000002)), ('C', 95, u'GLN', 0.5095495545901008, (236.67299999999997, 223.21099999999998, 204.129)), ('C', 127, u'SER', 0.6195532483360395, (236.011, 273.38599999999997, 198.15)), ('C', 132, u'LYS', 0.6752980722751106, (237.265, 277.183, 206.46800000000002)), ('C', 140, u'CYS', 0.6144481730707431, (241.944, 262.73299999999995, 191.466)), ('C', 151, u'LYS', 0.5410485132174269, (250.35000000000002, 254.21699999999998, 189.47)), ('C', 158, u'ASN', 0.5449092583875625, (256.53599999999994, 269.48699999999997, 191.185)), ('C', 161, u'GLN', 0.4682462001964751, (254.07899999999998, 263.42999999999995, 197.564)), ('C', 166, u'GLN', 0.6525141969373476, (244.529, 257.146, 199.953)), ('C', 171, u'GLU', 0.48575155710334933, (233.626, 247.252, 191.796)), ('C', 199, u'ALA', 0.308390528476822, (249.14, 267.84900000000005, 189.77499999999998)), ('C', 207, u'LEU', 0.681243179604034, (248.467, 255.13299999999998, 178.192)), ('C', 208, u'SER', 0.7191773989843105, (251.568, 255.17399999999998, 175.996))]
data['rota'] = [('E', ' 368 ', 'LEU', 0.0, (210.78300000000004, 239.646, 254.18799999999996)), ('E', ' 376 ', 'THR', 0.026958901435136795, (216.89700000000005, 235.697, 245.267)), ('E', ' 387 ', 'LEU', 0.23728738194087884, (217.88, 238.33099999999993, 264.095)), ('E', ' 390 ', 'LEU', 0.18972274031531605, (218.81400000000005, 240.916, 267.857)), ('E', ' 480 ', 'CYS', 0.02232224352802614, (238.59800000000007, 265.488, 225.823)), ('E', ' 483 ', 'VAL', 0.025922069295810545, (233.29900000000006, 266.779, 224.414)), ('E', ' 506 ', 'GLN', 0.015708858779972, (214.557, 241.986, 231.815)), ('H', '   5 ', 'VAL', 0.1050819473832211, (214.67300000000006, 215.103, 255.56099999999998)), ('H', ' 192 ', 'SER', 0.102077545529868, (222.70900000000006, 177.907, 284.57799999999986)), ('H', ' 203 ', 'ASN', 0.29814686419572584, (221.54900000000006, 188.462, 261.3869999999999)), ('L', '   1 ', 'ASP', 0.0851910271072826, (241.94300000000007, 228.487, 253.261)), ('A', ' 368 ', 'LEU', 0.0, (212.43600000000006, 208.639, 210.435)), ('A', ' 376 ', 'THR', 0.026958901435136795, (217.59400000000005, 212.612, 219.931)), ('A', ' 387 ', 'LEU', 0.23199634854242243, (220.57800000000006, 209.784, 201.34399999999994)), ('A', ' 390 ', 'LEU', 0.19119460981400507, (221.88600000000005, 207.152, 197.727)), ('A', ' 480 ', 'CYS', 0.02251363632287639, (236.723, 182.79, 241.86799999999994)), ('A', ' 483 ', 'VAL', 0.025861551615577846, (231.28700000000006, 181.568, 242.70499999999996)), ('A', ' 506 ', 'GLN', 0.015819367649333917, (213.74100000000007, 206.48, 233.104)), ('B', '   5 ', 'VAL', 0.10427751936027821, (216.73000000000005, 233.127, 209.27899999999997)), ('B', ' 192 ', 'SER', 0.1018941928457269, (224.36200000000005, 270.367, 181.059)), ('B', ' 203 ', 'ASN', 0.29752982603826106, (222.14300000000006, 259.795, 204.166)), ('C', '   1 ', 'ASP', 0.08338670517103486, (243.43800000000005, 219.484, 214.63499999999993))]
data['clusters'] = [('E', '393', 1, 'side-chain clash', (226.919, 249.856, 266.54)), ('E', '506', 1, 'Rotamer\nside-chain clash\nsmoc Outlier', (227.225, 244.646, 264.114)), ('E', '515', 1, 'smoc Outlier', (223.90800000000002, 245.73999999999998, 259.29799999999994)), ('E', '517', 1, 'smoc Outlier', (227.153, 247.266, 265.14700000000005)), ('E', '518', 1, 'side-chain clash', (226.919, 249.856, 266.54)), ('E', '519', 1, 'cablam Outlier', (230.2, 250.9, 270.3)), ('E', '522', 1, 'side-chain clash', (222.193, 250.489, 267.718)), ('E', '347', 2, 'side-chain clash', (215.424, 251.506, 241.453)), ('E', '348', 2, 'side-chain clash', (215.424, 251.506, 241.453)), ('E', '401', 2, 'side-chain clash', (213.955, 247.663, 240.23)), ('E', '497', 2, 'side-chain clash', (215.51, 247.058, 233.794)), ('E', '507', 2, 'side-chain clash', (215.51, 247.058, 233.794)), ('E', '509', 2, 'side-chain clash', (213.955, 247.663, 240.23)), ('E', '480', 3, 'Rotamer', (238.59800000000007, 265.488, 225.823)), ('E', '481', 3, 'cablam Outlier\nsmoc Outlier', (237.4, 269.0, 226.8)), ('E', '483', 3, 'Rotamer', (233.29900000000006, 266.779, 224.414)), ('E', '484', 3, 'Dihedral angle:CB:CG:CD:OE1', (232.187, 263.33799999999997, 223.24099999999999)), ('E', '387', 4, 'Rotamer', (217.88, 238.33099999999993, 264.095)), ('E', '390', 4, 'Rotamer', (218.81400000000005, 240.916, 267.857)), ('E', '447', 5, 'side-chain clash', (212.261, 248.396, 225.332)), ('E', '498', 5, 'side-chain clash', (212.261, 248.396, 225.332)), ('E', '355', 6, 'smoc Outlier', (220.14499999999998, 254.284, 250.41299999999998)), ('E', '398', 6, 'smoc Outlier', (220.10299999999998, 250.072, 249.33)), ('E', '379', 7, 'side-chain clash', (221.906, 238.672, 252.506)), ('E', '432', 7, 'side-chain clash\nsmoc Outlier', (221.906, 238.672, 252.506)), ('H', '187', 1, 'smoc Outlier', (228.32100000000003, 186.277, 281.459)), ('H', '188', 1, 'side-chain clash', (223.147, 182.618, 280.071)), ('H', '192', 1, 'Rotamer\nsmoc Outlier', (222.70900000000006, 177.907, 284.57799999999986)), ('H', '193', 1, 'smoc Outlier', (224.904, 175.89100000000002, 282.192)), ('H', '198', 1, 'side-chain clash', (223.147, 182.618, 280.071)), ('H', '157', 2, 'smoc Outlier', (221.04899999999998, 188.912, 270.23699999999997)), ('H', '202', 2, 'smoc Outlier', (223.278, 186.425, 264.094)), ('H', '203', 2, 'Rotamer', (221.54900000000006, 188.462, 261.3869999999999)), ('H', '209', 2, 'smoc Outlier', (221.79399999999998, 185.165, 256.26599999999996)), ('H', '150', 3, 'side-chain clash\nsmoc Outlier', (231.528, 193.699, 255.249)), ('H', '151', 3, 'side-chain clash', (231.528, 193.699, 255.249)), ('H', '152', 3, 'smoc Outlier', (229.02100000000002, 195.797, 258.335)), ('H', '117', 4, 'smoc Outlier', (229.60299999999998, 200.68, 248.106)), ('H', '118', 4, 'smoc Outlier', (230.091, 196.9, 248.38100000000003)), ('H', '86', 4, 'smoc Outlier', (231.218, 205.035, 243.142)), ('H', '137', 5, 'smoc Outlier', (230.701, 178.446, 292.173)), ('H', '138', 5, 'smoc Outlier', (230.701, 181.934, 290.69599999999997)), ('H', '104', 6, 'side-chain clash', (223.377, 232.506, 259.564)), ('H', '119', 6, 'side-chain clash\nbackbone clash', (228.332, 230.756, 262.945)), ('H', '123', 7, 'side-chain clash', (229.898, 187.016, 258.789)), ('H', '149', 7, 'side-chain clash\nsmoc Outlier', (229.898, 187.016, 258.789)), ('H', '57', 8, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (225.52200000000002, 228.899, 243.30700000000002)), ('H', '59', 8, 'Dihedral angle:CD:NE:CZ:NH1', (231.059, 226.01, 246.23)), ('H', '53', 9, 'smoc Outlier', (219.08, 226.611, 245.698)), ('H', '54', 9, 'smoc Outlier', (217.71899999999997, 230.038, 244.73)), ('L', '127', 1, 'smoc Outlier', (235.412, 175.24499999999998, 268.194)), ('L', '128', 1, 'smoc Outlier', (235.61499999999998, 171.83700000000002, 266.545)), ('L', '132', 1, 'smoc Outlier', (237.253, 171.501, 259.962)), ('L', '133', 1, 'smoc Outlier', (237.509, 174.657, 257.825)), ('L', '31', 2, 'smoc Outlier', (234.36100000000002, 240.26399999999998, 260.99399999999997)), ('L', '34', 2, 'side-chain clash\nbackbone clash', (231.75, 240.909, 264.598)), ('L', '35', 2, 'Ramachandran', (232.74900000000005, 242.662, 266.0619999999999)), ('L', '36', 2, 'backbone clash', (231.75, 240.909, 264.598)), ('L', '200', 3, 'smoc Outlier', (246.611, 184.70399999999998, 277.605)), ('L', '213', 3, 'smoc Outlier', (244.48100000000002, 182.171, 281.759)), ('L', '214', 3, 'smoc Outlier', (245.315, 179.126, 279.665)), ('L', '67', 4, 'backbone clash', (229.05, 222.972, 283.193)), ('L', '68', 4, 'smoc Outlier', (228.399, 225.248, 278.018)), ('L', '82', 4, 'backbone clash', (229.05, 222.972, 283.193)), ('L', '39', 5, 'smoc Outlier', (233.708, 230.20999999999998, 265.055)), ('L', '40', 5, 'smoc Outlier', (231.23999999999998, 227.502, 266.09099999999995)), ('L', '97', 5, 'side-chain clash', (228.332, 230.756, 262.945)), ('L', '1', 6, 'Rotamer', (241.94300000000007, 228.487, 253.261)), ('L', '100', 6, 'cablam CA Geom Outlier', (234.3, 228.9, 252.3)), ('L', '101', 6, 'smoc Outlier', (235.51399999999998, 226.207, 252.313)), ('L', '190', 7, 'side-chain clash', (250.598, 172.407, 263.658)), ('L', '194', 7, 'side-chain clash', (250.598, 172.407, 263.658)), ('L', '44', 8, 'smoc Outlier', (228.24899999999997, 214.65200000000002, 268.14700000000005)), ('L', '50', 8, 'smoc Outlier', (226.11599999999999, 216.95200000000003, 264.96)), ('L', '119', 9, 'smoc Outlier', (239.36, 192.805, 284.509)), ('L', '120', 9, 'smoc Outlier', (237.819, 189.36800000000002, 284.78099999999995)), ('L', '148', 10, 'smoc Outlier', (241.255, 201.112, 279.006)), ('L', '149', 10, 'smoc Outlier', (245.018, 200.52800000000002, 278.806)), ('A', '356', 1, 'smoc Outlier', (218.82800000000003, 193.92600000000002, 212.324)), ('A', '358', 1, 'smoc Outlier', (218.71099999999998, 195.702, 206.24599999999998)), ('A', '360', 1, 'side-chain clash', (219.402, 194.668, 199.729)), ('A', '393', 1, 'side-chain clash', (229.757, 198.151, 199.919)), ('A', '518', 1, 'side-chain clash', (229.757, 198.151, 199.919)), ('A', '519', 1, 'cablam Outlier\nsmoc Outlier', (233.3, 197.0, 196.6)), ('A', '522', 1, 'side-chain clash', (224.994, 197.544, 198.361)), ('A', '523', 1, 'side-chain clash', (219.402, 194.668, 199.729)), ('A', '443', 2, 'smoc Outlier', (208.58800000000002, 200.725, 233.517)), ('A', '447', 2, 'side-chain clash\nsmoc Outlier', (210.639, 199.8, 239.101)), ('A', '448', 2, 'smoc Outlier', (211.304, 196.817, 235.689)), ('A', '497', 2, 'side-chain clash', (214.926, 201.387, 231.198)), ('A', '498', 2, 'side-chain clash', (210.639, 199.8, 239.101)), ('A', '507', 2, 'side-chain clash', (214.926, 201.387, 231.198)), ('A', '480', 3, 'Rotamer', (236.723, 182.79, 241.86799999999994)), ('A', '481', 3, 'cablam Outlier', (235.6, 179.3, 240.8)), ('A', '483', 3, 'Rotamer', (231.28700000000006, 181.568, 242.70499999999996)), ('A', '484', 3, 'Dihedral angle:CB:CG:CD:OE1', (230.095, 185.031, 243.722)), ('A', '486', 4, 'cablam Outlier', (234.7, 188.6, 248.1)), ('A', '487', 4, 'smoc Outlier', (236.12, 190.592, 245.194)), ('A', '506', 4, 'Rotamer\nside-chain clash\nbackbone clash', (232.421, 193.774, 246.477)), ('A', '412', 5, 'backbone clash', (233.027, 206.946, 215.963)), ('A', '426', 5, 'backbone clash', (233.027, 206.946, 215.963)), ('A', '427', 5, 'smoc Outlier', (235.70999999999998, 206.842, 215.98100000000002)), ('A', '387', 6, 'Rotamer\nsmoc Outlier', (220.57800000000006, 209.784, 201.34399999999994)), ('A', '390', 6, 'Rotamer', (221.88600000000005, 207.152, 197.727)), ('A', '363', 7, 'smoc Outlier', (214.577, 202.641, 202.541)), ('A', '364', 7, 'Dihedral angle:CA:CB:CG:OD1', (212.463, 205.795, 202.923)), ('A', '379', 8, 'side-chain clash', (223.421, 209.435, 213.099)), ('A', '432', 8, 'side-chain clash\nsmoc Outlier', (223.421, 209.435, 213.099)), ('B', '110', 1, 'smoc Outlier', (221.667, 232.39200000000002, 206.671)), ('B', '111', 1, 'cablam Outlier\nsmoc Outlier', (222.2, 235.8, 205.1)), ('B', '112', 1, 'smoc Outlier', (224.42200000000003, 236.781, 208.008)), ('B', '5', 1, 'Rotamer', (216.73000000000005, 233.127, 209.27899999999997)), ('B', '97', 1, 'smoc Outlier', (225.272, 227.38100000000003, 208.972)), ('B', '188', 2, 'side-chain clash', (224.718, 265.686, 185.635)), ('B', '192', 2, 'Rotamer', (224.36200000000005, 270.367, 181.059)), ('B', '198', 2, 'side-chain clash', (224.718, 265.686, 185.635)), ('B', '217', 3, 'smoc Outlier', (231.005, 275.183, 188.69899999999998)), ('B', '218', 3, 'smoc Outlier', (233.067, 277.638, 190.737)), ('B', '203', 4, 'Rotamer', (222.14300000000006, 259.795, 204.166)), ('B', '211', 4, 'smoc Outlier', (222.503, 266.335, 203.62)), ('B', '137', 5, 'smoc Outlier', (232.796, 270.046, 173.944)), ('B', '138', 5, 'smoc Outlier', (232.805, 266.56, 175.425)), ('B', '64', 6, 'smoc Outlier', (236.70299999999997, 231.04299999999998, 220.36)), ('B', '65', 6, 'smoc Outlier', (236.653, 228.74299999999997, 223.411)), ('B', '123', 7, 'side-chain clash', (230.2, 260.915, 206.94)), ('B', '149', 7, 'side-chain clash', (230.2, 260.915, 206.94)), ('B', '57', 8, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (226.032, 219.339, 222.755)), ('B', '59', 8, 'Dihedral angle:CD:NE:CZ:NH1', (231.88500000000002, 222.142, 220.425)), ('C', '38', 1, 'smoc Outlier', (235.47899999999998, 214.585, 203.903)), ('C', '40', 1, 'smoc Outlier', (234.19899999999998, 220.454, 200.71299999999997)), ('C', '54', 1, 'smoc Outlier', (231.347, 220.32000000000002, 196.096)), ('C', '61', 1, 'Dihedral angle:CB:CG:CD:OE1', (225.894, 220.15200000000002, 195.224)), ('C', '63', 1, 'smoc Outlier', (222.453, 224.278, 191.637)), ('C', '95', 1, 'smoc Outlier', (236.67299999999997, 223.21099999999998, 204.129)), ('C', '97', 1, 'side-chain clash', (230.62, 217.468, 203.315)), ('C', '18', 2, 'smoc Outlier', (240.496, 225.814, 182.85600000000002)), ('C', '67', 2, 'backbone clash', (233.589, 224.567, 183.594)), ('C', '79', 2, 'smoc Outlier', (238.795, 222.278, 192.484)), ('C', '81', 2, 'smoc Outlier', (236.506, 225.20999999999998, 186.9)), ('C', '82', 2, 'backbone clash', (233.589, 224.567, 183.594)), ('C', '34', 3, 'side-chain clash\nbackbone clash', (234.616, 207.03, 201.898)), ('C', '35', 3, 'Ramachandran', (235.52300000000005, 205.28, 201.03599999999994)), ('C', '36', 3, 'backbone clash', (234.616, 207.03, 201.898)), ('C', '190', 4, 'side-chain clash', (250.255, 276.398, 203.248)), ('C', '194', 4, 'side-chain clash', (250.255, 276.398, 203.248)), ('C', '207', 5, 'smoc Outlier', (248.467, 255.13299999999998, 178.192)), ('C', '208', 5, 'smoc Outlier', (251.568, 255.17399999999998, 175.996))]
data['omega'] = [('B', ' 151 ', 'PRO', None, (229.737, 255.07099999999997, 211.921)), ('B', ' 153 ', 'PRO', None, (227.278, 252.36599999999993, 206.96999999999994)), ('C', '   8 ', 'PRO', None, (246.79400000000007, 228.495, 194.27799999999993)), ('C', ' 101 ', 'PRO', None, (237.55900000000005, 220.623, 215.437)), ('C', ' 147 ', 'PRO', None, (243.553, 247.296, 182.837)), ('H', ' 151 ', 'PRO', None, (229.448, 193.409, 254.09)), ('H', ' 153 ', 'PRO', None, (226.63100000000006, 196.03499999999994, 258.891)), ('L', '   8 ', 'PRO', None, (242.98000000000005, 219.263, 273.772)), ('L', ' 101 ', 'PRO', None, (236.17500000000007, 227.422, 251.81699999999995)), ('L', ' 147 ', 'PRO', None, (241.32600000000005, 201.501, 283.933))]
data['rama'] = [('C', '  35 ', 'ASN', 0.011132473178877016, (235.52300000000005, 205.28, 201.03599999999994)), ('L', '  35 ', 'ASN', 0.011294462423406579, (232.74900000000005, 242.662, 266.0619999999999))]
data['cablam'] = [('E', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (237.4, 269.0, 226.8)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (237.2, 259.8, 219.3)), ('E', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\nB-SS-', (230.2, 250.9, 270.3)), ('H', '111', 'GLN', ' beta sheet', ' \nE---E', (219.7, 212.4, 260.3)), ('L', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (234.3, 228.9, 252.3)), ('A', '481', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\n--SS-', (235.6, 179.3, 240.8)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (234.7, 188.6, 248.1)), ('A', '519', 'HIS', 'check CA trace,carbonyls, peptide', 'bend\nB-SS-', (233.3, 197.0, 196.6)), ('B', '111', 'GLN', ' beta sheet', ' \nE---E', (222.2, 235.8, 205.1)), ('C', '100', 'THR', 'check CA trace', 'bend\nSSSS-', (235.7, 219.2, 214.7))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-10863/6yor/Model_validation_1/validation_cootdata/molprobity_probe6yor_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

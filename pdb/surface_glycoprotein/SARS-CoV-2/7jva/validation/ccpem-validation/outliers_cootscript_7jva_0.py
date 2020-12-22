
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
data['probe'] = [(' A 378  LYS  NZ ', ' L  52  ASP  OD2', -0.542, (215.322, 216.532, 213.171)), (' A 342  PHE  HB2', ' B   1  NAG  H82', -0.479, (215.24, 197.178, 203.57)), (' A 465  GLU  HG3', ' A 466  ARG  N  ', -0.424, (236.13, 202.018, 216.524)), (' H   6  GLU  OE2', ' H 111  GLN  N  ', -0.406, (190.118, 223.46, 201.086))]
data['cablam'] = [('H', '111', 'GLN', 'check CA trace,carbonyls, peptide', ' \nE---E', (190.0, 225.4, 202.1))]
data['rota'] = [('H', '  86 ', 'LEU', 0.09546073233462396, (178.89, 209.728, 211.951))]
data['clusters'] = [('H', '111', 1, 'backbone clash\ncablam Outlier', (190.118, 223.46, 201.086)), ('H', '22', 1, 'smoc Outlier', (188.667, 216.758, 196.80700000000002)), ('H', '37', 1, 'smoc Outlier', (192.78, 216.49800000000002, 208.372)), ('H', '6', 1, 'backbone clash', (190.118, 223.46, 201.086)), ('H', '96', 1, 'smoc Outlier', (192.42000000000002, 217.43800000000002, 202.098)), ('H', '1', 2, 'Dihedral angle:CB:CG:CD:OE1\nsmoc Outlier', (200.105, 226.859, 190.95200000000003)), ('H', '2', 2, 'Bond angle:CG1:CB:CG2\nBond angle:CA:CB:CG1', (198.316, 223.961, 192.73399999999998)), ('H', '75', 3, 'smoc Outlier', (192.942, 209.155, 186.565)), ('H', '76', 3, 'smoc Outlier', (190.222, 211.516, 187.71899999999997)), ('L', '22', 1, 'smoc Outlier', (205.905, 221.859, 221.82200000000003)), ('L', '91', 1, 'smoc Outlier', (203.37800000000001, 221.472, 215.829)), ('L', '92', 1, 'smoc Outlier', (203.277, 218.15800000000002, 214.015)), ('L', '93', 1, 'smoc Outlier', (205.26299999999998, 214.955, 213.971)), ('L', '106', 2, 'smoc Outlier', (198.978, 227.847, 220.465)), ('L', '107', 2, 'smoc Outlier', (196.967, 230.995, 220.125)), ('L', '88', 2, 'smoc Outlier', (197.05100000000002, 229.526, 215.73499999999999)), ('A', '479', 1, 'smoc Outlier', (245.45000000000002, 195.60399999999998, 238.55800000000002)), ('A', '480', 1, 'smoc Outlier', (243.05, 193.136, 236.91899999999998)), ('A', '488', 1, 'smoc Outlier', (237.506, 194.795, 237.07299999999998)), ('A', '465', 2, 'backbone clash\nsmoc Outlier', (236.13, 202.018, 216.524)), ('A', '466', 2, 'backbone clash', (236.13, 202.018, 216.524)), ('A', '425', 3, 'smoc Outlier', (228.344, 209.76999999999998, 215.16899999999998)), ('A', '427', 3, 'Dihedral angle:CA:CB:CG:OD1', (228.806, 216.39600000000002, 214.92700000000002)), ('A', '391', 4, 'smoc Outlier', (224.804, 211.424, 193.575)), ('A', '525', 4, 'smoc Outlier', (222.77399999999997, 208.033, 192.042)), ('A', '349', 5, 'smoc Outlier', (225.48600000000002, 193.70499999999998, 218.42800000000003)), ('A', '401', 5, 'smoc Outlier', (220.57399999999998, 196.258, 217.751)), ('A', '432', 6, 'smoc Outlier', (219.90800000000002, 209.07299999999998, 207.859)), ('A', '513', 6, 'smoc Outlier', (223.108, 205.383, 206.197)), ('B', '1', 1, 'side-chain clash\nBond angle:C8:C7:N2', (214.068, 197.925, 202.54))]
data['rama'] = [('L', '  99 ', 'HIS', 0.034534792403705675, (200.497, 208.104, 212.423))]
data['smoc'] = [('H', 1, u'GLU', 0.7671273194663972, (200.105, 226.859, 190.95200000000003)), ('H', 8, u'GLY', 0.7040630748176958, (180.26, 216.848, 199.21299999999997)), ('H', 22, u'CYS', 0.765486798685405, (188.667, 216.758, 196.80700000000002)), ('H', 30, u'SER', 0.7911123199506398, (201.159, 209.636, 191.395)), ('H', 37, u'VAL', 0.7019150295164228, (192.78, 216.49800000000002, 208.372)), ('H', 66, u'GLY', 0.7330552420400531, (185.508, 200.65800000000002, 210.414)), ('H', 70, u'ILE', 0.7676095237461706, (189.762, 206.518, 202.01399999999998)), ('H', 75, u'ALA', 0.7785821488063922, (192.942, 209.155, 186.565)), ('H', 76, u'LYS', 0.7858591487347338, (190.222, 211.516, 187.71899999999997)), ('H', 96, u'CYS', 0.6912571993686113, (192.42000000000002, 217.43800000000002, 202.098)), ('L', 22, u'CYS', 0.7117916956582195, (205.905, 221.859, 221.82200000000003)), ('L', 65, u'GLY', 0.7642647420759054, (213.202, 226.864, 215.341)), ('L', 85, u'ASP', 0.7182699576314521, (201.71099999999998, 237.256, 212.759)), ('L', 88, u'ASP', 0.7634565015743628, (197.05100000000002, 229.526, 215.73499999999999)), ('L', 91, u'CYS', 0.6916629877479588, (203.37800000000001, 221.472, 215.829)), ('L', 92, u'GLN', 0.7271434575924993, (203.277, 218.15800000000002, 214.015)), ('L', 93, u'SER', 0.7677678769349298, (205.26299999999998, 214.955, 213.971)), ('L', 106, u'THR', 0.7462775434237099, (198.978, 227.847, 220.465)), ('L', 107, u'LYS', 0.7622274096751308, (196.967, 230.995, 220.125)), ('L', 110, u'VAL', 0.7643534464836346, (200.899, 240.478, 219.017)), ('A', 513, u'LEU', 0.6911517780382206, (223.108, 205.383, 206.197)), ('A', 519, u'HIS', 0.8121345928912513, (236.88600000000002, 214.09, 194.948)), ('A', 525, u'CYS', 0.8238882200301346, (222.77399999999997, 208.033, 192.042)), ('A', 349, u'SER', 0.7465791396225944, (225.48600000000002, 193.70499999999998, 218.42800000000003)), ('A', 370, u'ASN', 0.7660852290436215, (207.53, 205.98700000000002, 202.112)), ('A', 387, u'LEU', 0.8456490226683164, (218.689, 212.73399999999998, 198.69)), ('A', 391, u'CYS', 0.8217848310076825, (224.804, 211.424, 193.575)), ('A', 401, u'VAL', 0.7026309333888243, (220.57399999999998, 196.258, 217.751)), ('A', 425, u'LEU', 0.7809461275881107, (228.344, 209.76999999999998, 215.16899999999998)), ('A', 432, u'CYS', 0.6572645987433582, (219.90800000000002, 209.07299999999998, 207.859)), ('A', 448, u'ASN', 0.8492979000965774, (217.85100000000003, 186.785, 224.446)), ('A', 465, u'GLU', 0.8703939058643032, (235.253, 203.85800000000003, 215.287)), ('A', 479, u'PRO', 0.6301148646628619, (245.45000000000002, 195.60399999999998, 238.55800000000002)), ('A', 480, u'CYS', 0.5143017701874179, (243.05, 193.136, 236.91899999999998)), ('A', 488, u'CYS', 0.6122445088885337, (237.506, 194.795, 237.07299999999998)), ('A', 493, u'GLN', 0.7922614901826966, (227.18200000000002, 193.23499999999999, 228.88000000000002)), ('A', 500, u'THR', 0.8722969390590962, (207.224, 191.29299999999998, 227.817))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22497/7jva/Model_validation_1/validation_cootdata/molprobity_probe7jva_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

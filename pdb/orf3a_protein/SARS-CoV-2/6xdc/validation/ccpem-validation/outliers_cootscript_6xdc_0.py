
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
data['rota'] = [('A', '  97 ', 'VAL', 0.24340818393744829, (149.674, 132.459, 118.79900000000002)), ('A', ' 215 ', 'TYR', 0.0019587103452067822, (146.02, 134.468, 183.33600000000004)), ('B', '  97 ', 'VAL', 0.21867958564224238, (141.418, 158.626, 118.86700000000002)), ('B', ' 215 ', 'TYR', 0.0019587103452067822, (145.032, 156.609, 183.322))]
data['clusters'] = [('A', '126', 1, 'backbone clash', (141.435, 136.456, 155.018)), ('A', '138', 1, 'backbone clash', (141.435, 136.456, 155.018)), ('A', '140', 1, 'Dihedral angle:CA:C', (137.076, 139.89600000000002, 154.597)), ('A', '141', 1, 'Dihedral angle:N:CA', (139.71599999999998, 141.304, 156.88100000000003)), ('A', '68', 1, 'Dihedral angle:CD:NE:CZ:NH1', (131.70299999999997, 145.32000000000002, 157.13)), ('A', '72', 1, 'smoc Outlier', (132.791, 142.74599999999998, 151.415)), ('A', '170', 2, 'side-chain clash', (141.63, 146.141, 177.552)), ('A', '218', 2, 'side-chain clash\nsmoc Outlier', (142.164, 144.644, 182.16)), ('A', '230', 2, 'side-chain clash', (141.63, 146.141, 177.552)), ('A', '119', 3, 'side-chain clash', (145.373, 135.282, 145.557)), ('A', '120', 3, 'smoc Outlier', (144.92000000000002, 130.17499999999998, 143.35600000000002)), ('A', '122', 3, 'side-chain clash', (145.373, 135.282, 145.557)), ('A', '103', 4, 'side-chain clash', (159.157, 130.94, 122.954)), ('A', '104', 4, 'smoc Outlier', (161.1, 135.64299999999997, 125.3)), ('A', '106', 4, 'side-chain clash', (159.157, 130.94, 122.954)), ('A', '150', 5, 'side-chain clash', (133.046, 128.541, 174.211)), ('A', '198', 5, 'side-chain clash', (133.046, 128.541, 174.211)), ('A', '153', 6, 'smoc Outlier', (125.724, 131.668, 170.19299999999998)), ('A', '195', 6, 'cablam Outlier', (127.7, 134.7, 175.3)), ('A', '63', 7, 'side-chain clash\nsmoc Outlier', (152.542, 140.558, 171.725)), ('A', '74', 7, 'side-chain clash', (152.542, 140.558, 171.725)), ('A', '127', 8, 'side-chain clash\nsmoc Outlier', (136.991, 131.645, 151.421)), ('A', '139', 8, 'side-chain clash\nsmoc Outlier', (136.991, 131.645, 151.421)), ('A', '173', 9, 'Dihedral angle:CA:CB:CG:OD1', (130.259, 147.782, 179.298)), ('A', '183', 9, 'side-chain clash', (131.57, 146.06, 173.165)), ('B', '126', 1, 'backbone clash', (149.686, 154.406, 155.179)), ('B', '138', 1, 'backbone clash', (149.686, 154.406, 155.179)), ('B', '140', 1, 'Dihedral angle:CA:C', (153.98100000000002, 151.15200000000002, 154.576)), ('B', '141', 1, 'Dihedral angle:N:CA', (151.33700000000002, 149.757, 156.863)), ('B', '63', 1, 'side-chain clash', (154.771, 143.13, 149.24)), ('B', '74', 1, 'side-chain clash', (154.771, 143.13, 149.24)), ('B', '75', 1, 'side-chain clash', (152.642, 149.385, 148.144)), ('B', '170', 2, 'side-chain clash\nsmoc Outlier', (149.543, 144.852, 178.033)), ('B', '218', 2, 'side-chain clash', (148.907, 146.534, 182.172)), ('B', '230', 2, 'side-chain clash\nsmoc Outlier', (149.543, 144.852, 178.033)), ('B', '50', 3, 'smoc Outlier', (149.34, 144.318, 129.134)), ('B', '54', 3, 'smoc Outlier', (149.98000000000002, 141.034, 134.342)), ('B', '57', 3, 'side-chain clash', (146.389, 141.371, 137.948)), ('B', '41', 4, 'smoc Outlier', (150.314, 154.33200000000002, 116.269)), ('B', '42', 4, 'side-chain clash', (153.769, 151.008, 119.118)), ('B', '45', 4, 'side-chain clash', (153.769, 151.008, 119.118)), ('B', '150', 5, 'side-chain clash', (158.333, 162.426, 174.131)), ('B', '198', 5, 'side-chain clash', (158.333, 162.426, 174.131)), ('B', '119', 6, 'side-chain clash', (145.748, 155.703, 145.552)), ('B', '122', 6, 'side-chain clash', (145.748, 155.703, 145.552)), ('B', '100', 7, 'smoc Outlier', (137.32500000000002, 157.20499999999998, 115.908)), ('B', '97', 7, 'Rotamer', (141.418, 158.626, 118.86700000000002)), ('B', '173', 8, 'Dihedral angle:CA:CB:CG:OD1', (160.82800000000003, 143.285, 179.306)), ('B', '183', 8, 'side-chain clash', (159.721, 145.537, 173.008))]
data['probe'] = [(' B 218  GLN  HB2', ' B 230  PHE  HB2', -0.627, (148.907, 146.534, 182.172)), (' A 218  GLN  HB2', ' A 230  PHE  HB2', -0.621, (142.164, 144.644, 182.16)), (' B 238  ASP  N  ', ' B 238  ASP  OD1', -0.553, (137.75, 166.918, 177.952)), (' B 183  ASP  N  ', ' B 183  ASP  OD1', -0.549, (159.721, 145.537, 173.008)), (' A 127  LEU HD23', ' A 139  LEU HD21', -0.543, (136.991, 131.645, 151.421)), (' A 238  ASP  N  ', ' A 238  ASP  OD1', -0.542, (153.445, 124.339, 178.075)), (' A 183  ASP  N  ', ' A 183  ASP  OD1', -0.538, (131.57, 146.06, 173.165)), (' A 126  ARG  NH1', ' A 138  PRO  O  ', -0.527, (141.435, 136.456, 155.018)), (' B 119  ASN  OD1', ' B 122  ARG  NH1', -0.524, (145.748, 155.703, 145.552)), (' A 119  ASN  OD1', ' A 122  ARG  NH1', -0.503, (145.373, 135.282, 145.557)), (' B 126  ARG  NH1', ' B 138  PRO  O  ', -0.483, (149.686, 154.406, 155.179)), (' B 150  HIS  O  ', ' B 198  LYS  NZ ', -0.465, (158.333, 162.426, 174.131)), (' A 170  THR HG22', ' A 230  PHE  HD1', -0.464, (141.63, 146.141, 177.552)), (' A 103  ALA  HA ', ' A 106  LEU HD12', -0.454, (159.157, 130.94, 122.954)), (' B 170  THR HG22', ' B 230  PHE  HD1', -0.448, (149.543, 144.852, 178.033)), (' A 215  TYR  HA ', ' A 215  TYR  HD2', -0.429, (146.36, 132.805, 183.667)), (' A  63  ILE HG21', ' A  74  SER  HB3', -0.428, (136.385, 147.933, 149.381)), (' A 164  THR  HB ', ' B 185  GLN HE22', -0.422, (152.542, 140.558, 171.725)), (' A  75  LYS  HA ', ' A  75  LYS  HD3', -0.421, (138.426, 141.765, 148.208)), (' A 161  ASN  HB3', ' B 188  GLY  HA3', -0.418, (150.006, 142.255, 165.362)), (' B  75  LYS  HA ', ' B  75  LYS  HD3', -0.415, (152.642, 149.385, 148.144)), (' A 150  HIS  O  ', ' A 198  LYS  NZ ', -0.412, (133.046, 128.541, 174.211)), (' A  83  LEU  HA ', ' A  83  LEU HD23', -0.41, (139.354, 136.047, 136.419)), (' A 188  GLY  HA3', ' B 161  ASN  HB3', -0.41, (141.013, 148.947, 164.962)), (' B  42  PRO  HG2', ' B  45  TRP  HD1', -0.408, (153.769, 151.008, 119.118)), (' A  85  LEU HD22', ' B  57  GLN  HG2', -0.405, (146.389, 141.371, 137.948)), (' B  63  ILE HG21', ' B  74  SER  HB3', -0.405, (154.771, 143.13, 149.24)), (' A 215  TYR  HD1', ' B 225  VAL HG22', -0.402, (149.974, 135.848, 182.896)), (' A 225  VAL HG22', ' B 215  TYR  HD1', -0.401, (140.995, 154.838, 182.719))]
data['cablam'] = [('A', '195', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (127.7, 134.7, 175.3)), ('A', '206', 'TYR', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (147.6, 128.8, 157.5)), ('B', '195', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (163.4, 156.4, 175.3)), ('B', '206', 'TYR', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (143.5, 162.3, 157.5))]
data['smoc'] = [('A', 63, u'ILE', 0.5916210230562496, (137.40800000000002, 151.88400000000001, 148.974)), ('A', 65, u'LEU', 0.6528448024729246, (137.54899999999998, 149.83700000000002, 154.26299999999998)), ('A', 72, u'ALA', 0.6671460117498987, (132.791, 142.74599999999998, 151.415)), ('A', 80, u'VAL', 0.6531977822709427, (136.32800000000003, 140.967, 139.35700000000003)), ('A', 87, u'PHE', 0.5975164949182892, (140.94, 137.15200000000002, 130.61399999999998)), ('A', 104, u'PRO', 0.6633628990655822, (161.1, 135.64299999999997, 125.3)), ('A', 120, u'PHE', 0.679142634472237, (144.92000000000002, 130.17499999999998, 143.35600000000002)), ('A', 127, u'LEU', 0.6448304216995362, (138.76, 129.111, 152.363)), ('A', 136, u'LYS', 0.5983070017976301, (133.58, 134.454, 157.54)), ('A', 139, u'LEU', 0.5697489947505313, (137.691, 136.291, 153.547)), ('A', 153, u'CYS', 0.7298585013278899, (125.724, 131.668, 170.19299999999998)), ('A', 206, u'TYR', 0.6108319643993053, (147.56, 128.809, 157.539)), ('A', 218, u'GLN', 0.5747070143761339, (141.505, 143.629, 185.07399999999998)), ('A', 238, u'ASP', 0.4479756795285924, (154.944, 123.66999999999999, 179.24499999999998)), ('B', 41, u'LEU', 0.682079781803964, (150.314, 154.33200000000002, 116.269)), ('B', 50, u'VAL', 0.5384094781830033, (149.34, 144.318, 129.134)), ('B', 54, u'ALA', 0.5944106519910558, (149.98000000000002, 141.034, 134.342)), ('B', 85, u'LEU', 0.5555490766476341, (147.81, 150.664, 134.24299999999997)), ('B', 92, u'SER', 0.6826963907107257, (144.252, 152.515, 124.258)), ('B', 100, u'GLY', 0.6892725072086043, (137.32500000000002, 157.20499999999998, 115.908)), ('B', 103, u'ALA', 0.5341536514314997, (130.69299999999998, 158.47299999999998, 123.092)), ('B', 147, u'LEU', 0.5324762022658693, (148.86, 156.08700000000002, 167.444)), ('B', 161, u'ASN', 0.594556436135228, (141.98800000000003, 150.476, 163.207)), ('B', 164, u'THR', 0.5325730263029456, (138.127, 152.796, 170.60399999999998)), ('B', 170, u'THR', 0.5811625034301721, (152.066, 146.415, 176.194)), ('B', 185, u'GLN', 0.5115274671041584, (152.971, 146.74599999999998, 170.537)), ('B', 230, u'PHE', 0.5125904725619187, (150.571, 147.159, 180.39600000000002)), ('B', 238, u'ASP', 0.5094769061829141, (136.313, 167.416, 179.253))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22136/6xdc/Model_validation_1/validation_cootdata/molprobity_probe6xdc_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

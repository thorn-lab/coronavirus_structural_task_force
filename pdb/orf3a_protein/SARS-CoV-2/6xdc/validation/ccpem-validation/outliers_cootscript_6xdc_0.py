
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
data['jpred'] = [('A', '231', 'F', 'H', 'E', (141.2, 140.2, 179.9)), ('A', '232', 'I', 'H', 'E', (144.9, 139.4, 179.9)), ('B', '231', 'F', 'H', 'E', (149.9, 150.9, 179.9)), ('B', '232', 'I', 'H', 'E', (146.2, 151.7, 179.9))]
data['probe'] = [(' B 218  GLN  HB2', ' B 230  PHE  HB2', -0.627, (148.907, 146.534, 182.172)), (' A 218  GLN  HB2', ' A 230  PHE  HB2', -0.621, (142.164, 144.644, 182.16)), (' B 238  ASP  N  ', ' B 238  ASP  OD1', -0.553, (137.75, 166.918, 177.952)), (' B 183  ASP  N  ', ' B 183  ASP  OD1', -0.549, (159.721, 145.537, 173.008)), (' A 127  LEU HD23', ' A 139  LEU HD21', -0.543, (136.991, 131.645, 151.421)), (' A 238  ASP  N  ', ' A 238  ASP  OD1', -0.542, (153.445, 124.339, 178.075)), (' A 183  ASP  N  ', ' A 183  ASP  OD1', -0.538, (131.57, 146.06, 173.165)), (' A 126  ARG  NH1', ' A 138  PRO  O  ', -0.527, (141.435, 136.456, 155.018)), (' B 119  ASN  OD1', ' B 122  ARG  NH1', -0.524, (145.748, 155.703, 145.552)), (' A 119  ASN  OD1', ' A 122  ARG  NH1', -0.503, (145.373, 135.282, 145.557)), (' B 126  ARG  NH1', ' B 138  PRO  O  ', -0.483, (149.686, 154.406, 155.179)), (' B 150  HIS  O  ', ' B 198  LYS  NZ ', -0.465, (158.333, 162.426, 174.131)), (' A 170  THR HG22', ' A 230  PHE  HD1', -0.464, (141.63, 146.141, 177.552)), (' A 103  ALA  HA ', ' A 106  LEU HD12', -0.454, (159.157, 130.94, 122.954)), (' B 170  THR HG22', ' B 230  PHE  HD1', -0.448, (149.543, 144.852, 178.033)), (' A 215  TYR  HA ', ' A 215  TYR  HD2', -0.429, (146.36, 132.805, 183.667)), (' A  63  ILE HG21', ' A  74  SER  HB3', -0.428, (136.385, 147.933, 149.381)), (' A 164  THR  HB ', ' B 185  GLN HE22', -0.422, (152.542, 140.558, 171.725)), (' A  75  LYS  HA ', ' A  75  LYS  HD3', -0.421, (138.426, 141.765, 148.208)), (' A 161  ASN  HB3', ' B 188  GLY  HA3', -0.418, (150.006, 142.255, 165.362)), (' B  75  LYS  HA ', ' B  75  LYS  HD3', -0.415, (152.642, 149.385, 148.144)), (' A 150  HIS  O  ', ' A 198  LYS  NZ ', -0.412, (133.046, 128.541, 174.211)), (' A  83  LEU  HA ', ' A  83  LEU HD23', -0.41, (139.354, 136.047, 136.419)), (' A 188  GLY  HA3', ' B 161  ASN  HB3', -0.41, (141.013, 148.947, 164.962)), (' B  42  PRO  HG2', ' B  45  TRP  HD1', -0.408, (153.769, 151.008, 119.118)), (' A  85  LEU HD22', ' B  57  GLN  HG2', -0.405, (146.389, 141.371, 137.948)), (' B  63  ILE HG21', ' B  74  SER  HB3', -0.405, (154.771, 143.13, 149.24)), (' A 215  TYR  HD1', ' B 225  VAL HG22', -0.402, (149.974, 135.848, 182.896)), (' A 225  VAL HG22', ' B 215  TYR  HD1', -0.401, (140.995, 154.838, 182.719))]
data['smoc'] = [('A', 52, 'LEU', 0.5974542489950024, (136.99600219726562, 147.68800354003906, 131.88499450683594)), ('A', 72, 'ALA', 0.6113270721938304, (132.79100036621094, 142.74600219726562, 151.4149932861328)), ('A', 80, 'VAL', 0.6346170290867903, (136.3280029296875, 140.9669952392578, 139.35699462890625)), ('A', 87, 'PHE', 0.5640904349993702, (140.94000244140625, 137.15199279785156, 130.61399841308594)), ('A', 94, 'LEU', 0.6509942685747181, (145.98199462890625, 133.81500244140625, 121.75299835205078)), ('A', 98, 'ALA', 0.5934226453129905, (147.92799377441406, 133.52999877929688, 115.58100128173828)), ('A', 108, 'LEU', 0.6053378129485809, (156.88600158691406, 135.7519989013672, 130.16000366210938)), ('A', 117, 'SER', 0.6565369595194883, (148.593994140625, 129.24600219726562, 140.1820068359375)), ('A', 120, 'PHE', 0.6005410006430804, (144.9199981689453, 130.1750030517578, 143.3560028076172)), ('A', 127, 'LEU', 0.6265840462644157, (138.75999450683594, 129.11099243164062, 152.36300659179688)), ('A', 136, 'LYS', 0.4988958930682475, (133.5800018310547, 134.45399475097656, 157.5399932861328)), ('A', 139, 'LEU', 0.5633662929731839, (137.6909942626953, 136.29100036621094, 153.5469970703125)), ('A', 153, 'CYS', 0.6172430874064523, (125.7239990234375, 131.66799926757812, 170.1929931640625)), ('A', 155, 'ASP', 0.635759185469763, (132.2220001220703, 131.37100219726562, 167.03700256347656)), ('A', 185, 'GLN', 0.5234715416424065, (138.09500122070312, 144.33099365234375, 170.53599548339844)), ('A', 206, 'TYR', 0.6367054498018054, (147.55999755859375, 128.8090057373047, 157.53900146484375)), ('A', 218, 'GLN', 0.5552642464284011, (141.5050048828125, 143.62899780273438, 185.07400512695312)), ('A', 236, 'ILE', 0.5808576466988474, (151.0709991455078, 128.39199829101562, 177.38600158691406)), ('B', 41, 'LEU', 0.6276507878476237, (150.31399536132812, 154.33200073242188, 116.26899719238281)), ('B', 50, 'VAL', 0.562292412369486, (149.33999633789062, 144.3179931640625, 129.13400268554688)), ('B', 51, 'ALA', 0.5608890757862427, (151.73399353027344, 141.38800048828125, 129.63600158691406)), ('B', 85, 'LEU', 0.6073142888965806, (147.80999755859375, 150.66400146484375, 134.2429962158203)), ('B', 87, 'PHE', 0.615619320859549, (150.13600158691406, 153.91900634765625, 130.60899353027344)), ('B', 129, 'LEU', 0.6257635932191619, (149.91900634765625, 162.1959991455078, 157.0970001220703)), ('B', 147, 'LEU', 0.583866469158485, (148.86000061035156, 156.08700561523438, 167.44400024414062)), ('B', 153, 'CYS', 0.6534469813444715, (165.35000610351562, 159.4199981689453, 170.197998046875)), ('B', 161, 'ASN', 0.6047919374961457, (141.98800659179688, 150.4759979248047, 163.20700073242188)), ('B', 164, 'THR', 0.5719317453497443, (138.1269989013672, 152.79600524902344, 170.60400390625)), ('B', 170, 'THR', 0.6023696256592377, (152.0659942626953, 146.4149932861328, 176.19400024414062)), ('B', 181, 'GLU', 0.606111515968779, (163.89500427246094, 143.29100036621094, 173.8280029296875)), ('B', 185, 'GLN', 0.5300466013258931, (152.9709930419922, 146.74600219726562, 170.53700256347656)), ('B', 191, 'GLU', 0.5534446938588456, (158.01699829101562, 149.14599609375, 167.32200622558594)), ('B', 205, 'SER', 0.6345740580316412, (144.2030029296875, 160.1929931640625, 160.66400146484375)), ('B', 220, 'SER', 0.552929525531433, (153.43600463867188, 142.06199645996094, 186.69700622558594)), ('B', 225, 'VAL', 0.5619440201199349, (152.21200561523438, 137.7030029296875, 183.45399475097656)), ('B', 230, 'PHE', 0.5508909497783172, (150.5709991455078, 147.15899658203125, 180.39599609375)), ('B', 232, 'ILE', 0.5458283658714709, (146.1959991455078, 151.68800354003906, 179.8699951171875)), ('B', 238, 'ASP', 0.5364705159451453, (136.31300354003906, 167.41600036621094, 179.2530059814453))]
data['rota'] = [('A', '  97 ', 'VAL', 0.24340818393744829, (149.674, 132.459, 118.79900000000002)), ('A', ' 215 ', 'TYR', 0.0019587103452067822, (146.02, 134.468, 183.33600000000004)), ('B', '  97 ', 'VAL', 0.21867958564224238, (141.418, 158.626, 118.86700000000002)), ('B', ' 215 ', 'TYR', 0.0019587103452067822, (145.032, 156.609, 183.322))]
data['clusters'] = [('A', '170', 1, 'side-chain clash\n', (141.63, 146.141, 177.552)), ('A', '215', 1, 'side-chain clash\nRotamer\n', (146.02, 134.468, 183.33600000000004)), ('A', '218', 1, 'side-chain clash\nsmoc Outlier', (142.164, 144.644, 182.16)), ('A', '230', 1, 'side-chain clash\n', (141.63, 146.141, 177.552)), ('A', '231', 1, 'jpred outlier', (141.2, 140.2, 179.9)), ('A', '232', 1, 'jpred outlier', (144.9, 139.4, 179.9)), ('A', '126', 2, 'backbone clash\n', (141.435, 136.456, 155.018)), ('A', '138', 2, 'backbone clash\n', (141.435, 136.456, 155.018)), ('A', '140', 2, 'Dihedral angle:CA:C\n', (137.076, 139.89600000000002, 154.597)), ('A', '141', 2, 'Dihedral angle:N:CA\n', (139.71599999999998, 141.304, 156.88100000000003)), ('A', '68', 2, 'Dihedral angle:CD:NE:CZ:NH1\n', (131.70299999999997, 145.32000000000002, 157.13)), ('A', '72', 2, 'smoc Outlier\n', (132.79100036621094, 142.74600219726562, 151.4149932861328)), ('A', '117', 3, 'smoc Outlier\n', (148.593994140625, 129.24600219726562, 140.1820068359375)), ('A', '119', 3, 'side-chain clash\n', (145.373, 135.282, 145.557)), ('A', '120', 3, 'smoc Outlier\n', (144.9199981689453, 130.1750030517578, 143.3560028076172)), ('A', '122', 3, 'side-chain clash\n', (145.373, 135.282, 145.557)), ('A', '94', 4, 'smoc Outlier\n', (145.98199462890625, 133.81500244140625, 121.75299835205078)), ('A', '97', 4, 'Rotamer\n', (149.674, 132.459, 118.79900000000002)), ('A', '98', 4, 'smoc Outlier\n', (147.92799377441406, 133.52999877929688, 115.58100128173828)), ('A', '150', 5, 'side-chain clash\n', (133.046, 128.541, 174.211)), ('A', '198', 5, 'side-chain clash\n', (133.046, 128.541, 174.211)), ('A', '153', 6, 'smoc Outlier\n', (125.7239990234375, 131.66799926757812, 170.1929931640625)), ('A', '195', 6, 'cablam Outlier\n', (127.7, 134.7, 175.3)), ('A', '134', 7, 'Dihedral angle:CD:NE:CZ:NH1\n', (134.232, 128.732, 161.54399999999998)), ('A', '155', 7, 'smoc Outlier\n', (132.2220001220703, 131.37100219726562, 167.03700256347656)), ('A', '63', 8, 'side-chain clash\n', (152.542, 140.558, 171.725)), ('A', '74', 8, 'side-chain clash\n', (152.542, 140.558, 171.725)), ('A', '236', 9, 'smoc Outlier\n', (151.0709991455078, 128.39199829101562, 177.38600158691406)), ('A', '238', 9, 'side-chain clash\n', (153.445, 124.339, 178.075)), ('A', '127', 10, 'side-chain clash\nsmoc Outlier', (136.991, 131.645, 151.421)), ('A', '139', 10, 'side-chain clash\nsmoc Outlier', (136.991, 131.645, 151.421)), ('A', '173', 11, 'Dihedral angle:CA:CB:CG:OD1\n', (130.259, 147.782, 179.298)), ('A', '183', 11, 'side-chain clash\n', (131.57, 146.06, 173.165)), ('A', '103', 12, 'side-chain clash\n', (159.157, 130.94, 122.954)), ('A', '106', 12, 'side-chain clash\n', (159.157, 130.94, 122.954)), ('B', '126', 1, 'backbone clash\n', (149.686, 154.406, 155.179)), ('B', '138', 1, 'backbone clash\n', (149.686, 154.406, 155.179)), ('B', '140', 1, 'Dihedral angle:CA:C\n', (153.98100000000002, 151.15200000000002, 154.576)), ('B', '141', 1, 'Dihedral angle:N:CA\n', (151.33700000000002, 149.757, 156.863)), ('B', '63', 1, 'side-chain clash\n', (154.771, 143.13, 149.24)), ('B', '74', 1, 'side-chain clash\n', (154.771, 143.13, 149.24)), ('B', '75', 1, 'side-chain clash\n', (152.642, 149.385, 148.144)), ('B', '170', 2, 'side-chain clash\nsmoc Outlier', (149.543, 144.852, 178.033)), ('B', '215', 2, 'side-chain clash\nRotamer\n', (145.032, 156.609, 183.322)), ('B', '218', 2, 'side-chain clash\n', (148.907, 146.534, 182.172)), ('B', '230', 2, 'side-chain clash\nsmoc Outlier', (149.543, 144.852, 178.033)), ('B', '231', 2, 'jpred outlier', (149.9, 150.9, 179.9)), ('B', '232', 2, 'smoc Outlier\njpred outlier', (146.1959991455078, 151.68800354003906, 179.8699951171875)), ('B', '173', 3, 'Dihedral angle:CA:CB:CG:OD1\n', (160.82800000000003, 143.285, 179.306)), ('B', '181', 3, 'smoc Outlier\n', (163.89500427246094, 143.29100036621094, 173.8280029296875)), ('B', '183', 3, 'side-chain clash\n', (159.721, 145.537, 173.008)), ('B', '191', 3, 'smoc Outlier\n', (158.01699829101562, 149.14599609375, 167.32200622558594)), ('B', '41', 4, 'smoc Outlier\n', (150.31399536132812, 154.33200073242188, 116.26899719238281)), ('B', '42', 4, 'side-chain clash\n', (153.769, 151.008, 119.118)), ('B', '45', 4, 'side-chain clash\n', (153.769, 151.008, 119.118)), ('B', '129', 5, 'smoc Outlier\n', (149.91900634765625, 162.1959991455078, 157.0970001220703)), ('B', '205', 5, 'smoc Outlier\n', (144.2030029296875, 160.1929931640625, 160.66400146484375)), ('B', '206', 5, 'cablam Outlier\n', (143.5, 162.3, 157.5)), ('B', '150', 6, 'side-chain clash\n', (158.333, 162.426, 174.131)), ('B', '198', 6, 'side-chain clash\n', (158.333, 162.426, 174.131)), ('B', '153', 7, 'smoc Outlier\n', (165.35000610351562, 159.4199981689453, 170.197998046875)), ('B', '195', 7, 'cablam Outlier\n', (163.4, 156.4, 175.3)), ('B', '50', 8, 'smoc Outlier\n', (149.33999633789062, 144.3179931640625, 129.13400268554688)), ('B', '51', 8, 'smoc Outlier\n', (151.73399353027344, 141.38800048828125, 129.63600158691406)), ('B', '119', 9, 'side-chain clash\n', (145.748, 155.703, 145.552)), ('B', '122', 9, 'side-chain clash\n', (145.748, 155.703, 145.552)), ('B', '85', 10, 'smoc Outlier\n', (147.80999755859375, 150.66400146484375, 134.2429962158203)), ('B', '87', 10, 'smoc Outlier\n', (150.13600158691406, 153.91900634765625, 130.60899353027344))]
data['cablam'] = [('A', '195', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (127.7, 134.7, 175.3)), ('A', '206', 'TYR', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (147.6, 128.8, 157.5)), ('B', '195', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-SS--', (163.4, 156.4, 175.3)), ('B', '206', 'TYR', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (143.5, 162.3, 157.5))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22136/6xdc/Model_validation_5/validation_cootdata/molprobity_probe6xdc_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

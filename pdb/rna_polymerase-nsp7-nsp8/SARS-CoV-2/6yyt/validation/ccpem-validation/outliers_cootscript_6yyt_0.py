
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
data['probe'] = [(' B  44  VAL HG22', " U  15    G  H4'", -0.692, (28.541, 99.956, 112.107)), (' C  58  VAL HG22', ' D 119  ILE HG12', -0.635, (115.541, 87.85, 131.658)), (' B  40  LYS  O  ', ' B  44  VAL HG23', -0.599, (26.898, 98.951, 115.012)), (" P   5    C  H2'", ' P   6    A  C8 ', -0.599, (57.198, 86.94, 107.279)), (' D 157  GLN  HG3', ' D 189  LEU HD23', -0.579, (132.308, 83.393, 134.786)), (' A 605  VAL HG21', ' A 756  MET  HE2', -0.575, (88.764, 86.786, 89.416)), (' D 131  VAL HG12', ' D 185  ILE HG13', -0.555, (122.325, 86.484, 145.418)), (' C  71  LEU HD21', ' D  88  GLN  HB3', -0.553, (100.023, 82.1, 139.43)), (' C   2  LYS  O  ', ' C   6  VAL HG23', -0.529, (105.952, 73.116, 124.037)), (' D 109  ASN  O  ', ' D 114  CYS  N  ', -0.516, (115.958, 79.034, 144.901)), (' A 606  TYR  HE1', ' A 614  LEU HD21', -0.514, (90.527, 82.14, 86.043)), (' A 491  ASN  N  ', ' A 491  ASN  OD1', -0.512, (72.249, 116.811, 104.104)), (' D 101  ASP  OD1', ' D 102  ALA  N  ', -0.51, (115.842, 70.475, 131.708)), (' A 335  VAL  O  ', ' A 338  VAL HG12', -0.501, (92.614, 138.083, 119.596)), (' D 117  LEU HD11', ' D 131  VAL HG13', -0.501, (120.621, 86.829, 143.735)), (' A 531  THR HG21', ' A 567  THR HG21', -0.501, (87.257, 120.013, 103.92)), (' A 330  VAL HG11', ' B 117  LEU HD13', -0.493, (102.948, 127.547, 110.563)), (' A 726  ARG  NH2', ' A 744  GLU  OE2', -0.488, (92.598, 100.016, 66.845)), (' A 900  LEU  O  ', ' A 900  LEU HD23', -0.487, (69.215, 76.264, 137.996)), (' A 303  ASP  N  ', ' A 303  ASP  OD1', -0.484, (93.719, 121.175, 81.751)), (' A 254  GLU  OE1', ' A 286  TYR  OH ', -0.484, (121.494, 120.999, 86.81)), (' C  13  LEU HD23', ' C  55  LEU  HB3', -0.482, (108.737, 82.699, 129.484)), (' A 242  MET  SD ', ' A 312  ASN  ND2', -0.482, (107.856, 113.389, 83.004)), (' A 628  ASN  HB3', ' A 663  LEU HD21', -0.479, (102.279, 113.195, 95.889)), (' A 503  GLY  O  ', ' A 507  ASN  N  ', -0.476, (90.984, 113.776, 118.373)), (' A 676  LYS  NZ ', ' A 681  SER  OG ', -0.474, (99.388, 109.311, 104.732)), (' A 647  SER  OG ', ' A 648  LEU  N  ', -0.472, (85.843, 125.087, 87.814)), (' A 859  PHE  HA ', ' A 862  LEU HD12', -0.462, (84.48, 81.369, 116.257)), (' C  71  LEU HD23', ' D  92  PHE  HE2', -0.459, (102.928, 81.194, 140.578)), (' A 340  PHE  CD2', ' A 380  MET  HE1', -0.458, (94.143, 131.041, 116.467)), (' B 132  ILE HG21', ' B 138  TYR  HB2', -0.456, (123.924, 109.762, 122.314)), (' B  58  LYS  HG2', ' B  62  MET  HE3', -0.455, (50.38, 110.483, 115.998)), (' D 127  LYS  HD2', ' D 189  LEU HD21', -0.454, (130.917, 85.674, 133.408)), (' A 689  TYR  O  ', ' A 693  VAL HG23', -0.442, (90.996, 103.21, 93.309)), (' A 340  PHE  HD2', ' A 380  MET  HE1', -0.442, (94.305, 130.697, 115.972)), (' A 852  GLY  O  ', ' A 853  THR  OG1', -0.441, (79.369, 85.106, 128.971)), (' B 141  THR  OG1', ' B 142  CYS  N  ', -0.437, (124.818, 114.67, 119.837)), (' A 633  MET  O  ', ' A 637  VAL HG23', -0.433, (93.446, 109.385, 88.202)), (' A 601  MET  O  ', ' A 605  VAL HG23', -0.432, (85.524, 86.607, 88.387)), (' A 631  ARG  HD3', ' A 680  THR HG22', -0.432, (98.187, 107.17, 97.871)), (" P   5    C  H2'", ' P   6    A  H8 ', -0.432, (57.569, 87.267, 107.757)), (' C  36  HIS  CE1', ' C  40  LEU HD11', -0.432, (103.749, 85.885, 121.196)), (' B  59  LEU  HA ', ' B  62  MET  HG2', -0.425, (51.184, 111.954, 118.471)), (' A 626  MET  HE3', ' A 680  THR HG21', -0.424, (98.935, 104.598, 97.223)), (' B  56  GLN  O  ', ' B  59  LEU  HG ', -0.423, (47.249, 110.164, 121.312)), (' A 711  ASP  OD1', ' A 713  ASN  ND2', -0.423, (111.288, 94.087, 64.513)), (' D 159  VAL HG22', ' D 186  VAL HG22', -0.421, (129.619, 81.793, 145.08)), (' A 374  TYR  HB3', ' A 380  MET  HE3', -0.42, (93.941, 128.254, 115.131)), (' A 278  GLU  N  ', ' A 278  GLU  OE1', -0.419, (113.898, 130.459, 91.405)), (' C  71  LEU HD23', ' D  92  PHE  CE2', -0.416, (102.774, 80.978, 140.568)), (' A 540  THR HG21', ' A 665  GLU  OE1', -0.413, (97.39, 112.398, 107.197)), (' A 155  ASP  N  ', ' A 155  ASP  OD1', -0.412, (133.421, 93.514, 93.407)), (' A 575  LEU HD22', ' A 641  LYS  HG3', -0.408, (83.884, 109.163, 90.7)), (" P   6    A  H2'", ' P   7    U  C6 ', -0.408, (60.323, 90.132, 105.139)), (' A 209  ASN  ND2', ' A 218  ASP  OD2', -0.408, (119.747, 108.174, 65.142)), (' C  54  SER  O  ', ' C  58  VAL HG23', -0.408, (114.095, 84.907, 131.383)), (' B 177  SER  N  ', ' B 178  PRO  CD ', -0.406, (127.06, 100.522, 128.625)), (' B  52  ASP  HA ', ' B  55  MET  HG3', -0.405, (41.401, 108.421, 117.826)), (' A 707  LEU  O  ', ' A 724  GLN  NE2', -0.405, (104.757, 95.628, 70.845)), (' A 715  ILE  O  ', ' A 721  ARG  NH2', -0.404, (103.21, 89.796, 62.038)), (' B 126  ALA  O  ', ' B 190  ARG  N  ', -0.404, (117.036, 126.754, 124.607)), (' A 623  ASP  N  ', ' A 623  ASP  OD1', -0.4, (101.833, 100.254, 102.085))]
data['smoc'] = [('A', 32, u'TYR', 0.3216026487539567, (120.96600000000001, 92.59100000000001, 71.12499999999999)), ('A', 38, u'TYR', 0.4381776342271525, (109.38199999999999, 104.093, 64.32)), ('A', 92, u'ASP', -0.15730058512845504, (131.066, 123.363, 65.285)), ('A', 133, u'HIS', 0.2647465244204901, (113.05199999999999, 96.389, 81.863)), ('A', 158, u'ASN', 0.18695747119651074, (128.30700000000002, 89.10499999999999, 94.903)), ('A', 163, u'TYR', 0.366737334205922, (119.327, 94.843, 93.198)), ('A', 168, u'ASN', 0.25519131035295567, (120.502, 96.806, 101.021)), ('A', 169, u'PRO', 0.21696567951579276, (119.532, 100.41600000000001, 100.191)), ('A', 228, u'GLY', -0.3530887947862462, (116.65499999999999, 129.364, 62.021)), ('A', 235, u'ASP', 0.18869888620132746, (108.99900000000001, 114.002, 73.137)), ('A', 260, u'ASP', 0.06509621540617525, (129.80700000000002, 121.804, 91.12299999999999)), ('A', 275, u'PHE', 0.19503621947700514, (111.037, 129.108, 94.05199999999999)), ('A', 283, u'PHE', 0.1625984046942059, (113.07, 124.056, 82.99400000000001)), ('A', 291, u'ASP', 0.3466048302807601, (106.96000000000001, 122.697, 73.56400000000001)), ('A', 306, u'CYS', 0.08371882005047085, (97.99700000000001, 119.71000000000001, 82.663)), ('A', 323, u'PRO', -0.01572351637614799, (112.81700000000001, 120.512, 102.639)), ('A', 353, u'VAL', 0.1557607207124827, (102.556, 127.46300000000001, 96.089)), ('A', 387, u'LEU', 0.13612883313231575, (112.194, 122.057, 118.726)), ('A', 393, u'THR', 0.3426799616385735, (114.386, 108.073, 112.026)), ('A', 400, u'ALA', -0.048635479617589336, (107.65199999999999, 118.046, 120.282)), ('A', 401, u'LEU', 0.049221064694735084, (104.228, 118.927, 121.68299999999999)), ('A', 404, u'ASN', -0.16914599200938366, (108.17099999999999, 113.792, 127.792)), ('A', 421, u'ASP', -0.3752337857421581, (91.956, 71.765, 125.834)), ('A', 430, u'LYS', -0.398719637734189, (99.657, 66.42, 117.44300000000001)), ('A', 445, u'ASP', 0.02721098797782009, (108.55199999999999, 97.149, 122.582)), ('A', 484, u'ASP', 0.26594923789812963, (78.304, 107.67399999999999, 88.781)), ('A', 523, u'ASP', 0.2154559826686681, (77.836, 124.17899999999999, 109.098)), ('A', 537, u'PRO', 0.1409700507452037, (96.59400000000001, 121.24100000000001, 106.712)), ('A', 561, u'SER', 0.18346063571014515, (91.205, 114.276, 111.624)), ('A', 570, u'GLN', 0.1069097882809323, (81.01700000000001, 114.783, 101.069)), ('A', 580, u'ALA', 0.06819683451063042, (80.303, 99.24900000000001, 96.04100000000001)), ('A', 581, u'ALA', 0.0021986319059234412, (76.819, 98.62899999999999, 94.584)), ('A', 599, u'HIS', 0.2213963764822909, (81.37499999999999, 81.62299999999999, 91.956)), ('A', 608, u'ASP', 0.2560866080908453, (85.48700000000001, 84.46600000000001, 77.15599999999999)), ('A', 633, u'MET', -0.007157074511176797, (96.51700000000001, 110.452, 89.43100000000001)), ('A', 634, u'ALA', 0.17141406503208254, (94.12299999999999, 108.26400000000001, 91.428)), ('A', 658, u'GLU', 0.1336378582612515, (93.585, 115.795, 99.585)), ('A', 705, u'ASN', 0.30725355230708745, (105.304, 98.004, 78.52)), ('A', 719, u'TYR', 0.1422417653339676, (95.702, 93.46600000000001, 64.151)), ('A', 726, u'ARG', -0.007795729088739923, (98.842, 103.256, 66.94000000000001)), ('A', 740, u'ASP', -0.16297140685098463, (88.721, 105.465, 69.43900000000001)), ('A', 751, u'LYS', 0.1699737058850933, (89.35799999999999, 90.27, 75.989)), ('A', 754, u'SER', 0.10276000633133246, (90.436, 89.91400000000002, 82.52199999999999)), ('A', 759, u'SER', 0.3228219055537503, (92.329, 97.101, 96.774)), ('A', 763, u'VAL', 0.19901437885123843, (93.732, 87.992, 90.023)), ('A', 803, u'THR', 0.24514681193520554, (97.338, 76.766, 84.475)), ('A', 817, u'THR', 0.24744690621236287, (89.316, 78.276, 96.096)), ('A', 874, u'ASN', -0.2613108223498769, (92.478, 66.489, 103.843)), ('A', 878, u'ALA', -0.27371549552090485, (87.475, 69.016, 107.593)), ('A', 882, u'HIS', -0.3412131595210397, (83.16799999999999, 69.559, 113.425)), ('A', 888, u'ILE', -0.3178460414097566, (79.684, 75.57, 120.37199999999999)), ('A', 889, u'ARG', -0.3036472498832747, (77.422, 72.806, 121.68199999999999)), ('A', 898, u'HIS', -0.3151379990457145, (75.16499999999999, 78.21300000000001, 134.706)), ('A', 909, u'ASN', -0.25271865437988106, (66.492, 77.495, 124.37599999999999)), ('A', 917, u'GLU', -0.31569377460272435, (73.498, 71.94100000000002, 112.952)), ('A', 929, u'THR', 0.3387415584581578, (69.62499999999999, 84.233, 98.77)), ('B', 19, u'GLN', -0.2730098711722847, (26.552, 99.559, 126.397)), ('B', 43, u'ASN', -0.2556599886690248, (29.517000000000003, 97.70100000000001, 117.508)), ('B', 44, u'VAL', -0.27126602236252906, (29.618000000000002, 100.94800000000001, 115.52499999999999)), ('B', 58, u'LYS', 0.22669400469138995, (49.458, 107.94900000000001, 118.197)), ('B', 63, u'ALA', 0.26802846302583583, (54.52, 113.785, 121.835)), ('B', 75, u'ARG', 0.27928955407644024, (72.17099999999999, 117.722, 125.098)), ('B', 80, u'ARG', 0.2181803151500414, (78.63, 122.049, 121.646)), ('B', 81, u'ALA', 0.22549842619231522, (79.087, 124.79, 124.245)), ('B', 91, u'LEU', 0.3011101701615905, (93.846, 127.755, 121.516)), ('B', 92, u'PHE', 0.2576611616795927, (94.51100000000001, 130.636, 123.912)), ('B', 98, u'LEU', 0.27313993928117825, (104.634, 130.537, 121.861)), ('B', 111, u'ARG', 0.46648961749512524, (108.935, 140.77399999999997, 102.838)), ('B', 129, u'MET', 0.1963771815399912, (114.577, 117.795, 122.845)), ('B', 130, u'VAL', 0.21613729926505962, (117.001, 115.368, 121.17699999999999)), ('B', 143, u'ASP', 0.17619935532835157, (129.094, 115.932, 122.83)), ('B', 149, u'TYR', 0.29833711825559756, (122.427, 122.702, 116.12899999999999)), ('B', 150, u'ALA', 0.1461915979065442, (120.47, 124.82199999999999, 113.645)), ('B', 162, u'ALA', 0.3259570351711683, (113.49900000000001, 105.577, 128.461)), ('C', 25, u'SER', -0.3565548135638216, (111.462, 98.83, 132.281)), ('C', 30, u'ALA', -0.3806844380638186, (112.062, 94.609, 125.002)), ('C', 40, u'LEU', -0.3269142399042864, (106.319, 82.007, 118.51700000000001)), ('C', 69, u'ASN', -0.4413953953864798, (105.556, 78.423, 147.394)), ('D', 6, u'PHE', -0.3617558165447266, (48.805, 77.70100000000001, 128.80700000000002)), ('D', 13, u'ALA', -0.2806997973121866, (38.873999999999995, 76.95, 129.55100000000002)), ('D', 15, u'PHE', -0.3210506776058193, (38.713, 78.096, 124.17999999999999)), ('D', 37, u'LYS', -0.28286402517248094, (27.833000000000002, 80.508, 115.287)), ('D', 75, u'ARG', -0.23295335264874725, (80.44600000000001, 87.10199999999999, 134.138)), ('D', 85, u'SER', -0.40090883398706756, (95.40700000000001, 84.697, 140.33100000000002)), ('D', 112, u'ASP', -0.5355600852325585, (113.516, 76.26400000000001, 148.02800000000002)), ('D', 117, u'LEU', -0.49588329540336684, (119.266, 87.91100000000002, 139.766)), ('D', 179, u'ASN', -0.6011349481201007, (130.66, 82.501, 160.07899999999998)), ('D', 184, u'LEU', -0.5329494785165468, (125.534, 84.07, 149.056)), ('T', 9, u'C', 0.32661581909897736, (88.787, 104.006, 106.483))]
data['rota'] = [('A', ' 246 ', 'THR', 0.2556067653575468, (114.83, 110.63699999999997, 89.62599999999999)), ('A', ' 371 ', 'LEU', 0.028224641648028216, (87.456, 126.81699999999996, 115.475)), ('A', ' 440 ', 'PHE', 0.24708157751684706, (99.29900000000004, 84.587, 117.302)), ('A', ' 491 ', 'ASN', 0.0, (71.847, 115.325, 104.854))]
data['clusters'] = [('A', '540', 1, 'side-chain clash', (97.39, 112.398, 107.197)), ('A', '628', 1, 'side-chain clash', (102.279, 113.195, 95.889)), ('A', '663', 1, 'side-chain clash', (102.279, 113.195, 95.889)), ('A', '665', 1, 'side-chain clash', (97.39, 112.398, 107.197)), ('A', '676', 1, 'side-chain clash', (99.388, 109.311, 104.732)), ('A', '677', 1, 'cablam Outlier', (107.6, 112.3, 102.7)), ('A', '678', 1, 'cablam CA Geom Outlier', (104.7, 110.6, 100.9)), ('A', '681', 1, 'side-chain clash', (99.388, 109.311, 104.732)), ('A', '601', 2, 'side-chain clash', (85.524, 86.607, 88.387)), ('A', '605', 2, 'side-chain clash', (85.524, 86.607, 88.387)), ('A', '606', 2, 'side-chain clash', (90.527, 82.14, 86.043)), ('A', '614', 2, 'side-chain clash', (90.527, 82.14, 86.043)), ('A', '756', 2, 'side-chain clash', (88.764, 86.786, 89.416)), ('A', '763', 2, 'smoc Outlier', (93.732, 87.992, 90.023)), ('A', '209', 3, 'side-chain clash', (119.747, 108.174, 65.142)), ('A', '218', 3, 'side-chain clash', (119.747, 108.174, 65.142)), ('A', '220', 3, 'cablam Outlier', (119.7, 110.8, 59.5)), ('A', '83', 3, 'Dihedral angle:CB:CG:CD:OE1', (124.657, 112.087, 56.598000000000006)), ('A', '84', 3, 'Dihedral angle:CB:CG:CD:OE1', (127.985, 113.73700000000001, 55.761)), ('A', '633', 4, 'side-chain clash\nsmoc Outlier', (93.446, 109.385, 88.202)), ('A', '634', 4, 'smoc Outlier', (94.12299999999999, 108.26400000000001, 91.428)), ('A', '637', 4, 'side-chain clash', (93.446, 109.385, 88.202)), ('A', '689', 4, 'side-chain clash', (90.996, 103.21, 93.309)), ('A', '693', 4, 'side-chain clash', (90.996, 103.21, 93.309)), ('A', '340', 5, 'side-chain clash', (94.305, 130.697, 115.972)), ('A', '370', 5, 'Dihedral angle:CB:CG:CD:OE1', (86.786, 128.399, 112.074)), ('A', '371', 5, 'Rotamer', (87.456, 126.81699999999996, 115.475)), ('A', '374', 5, 'side-chain clash', (93.941, 128.254, 115.131)), ('A', '380', 5, 'side-chain clash', (93.941, 128.254, 115.131)), ('A', '503', 6, 'backbone clash', (90.984, 113.776, 118.373)), ('A', '504', 6, 'cablam Outlier', (94.4, 115.0, 116.8)), ('A', '507', 6, 'backbone clash', (90.984, 113.776, 118.373)), ('A', '509', 6, 'cablam Outlier', (87.4, 116.3, 123.7)), ('A', '561', 6, 'smoc Outlier', (91.205, 114.276, 111.624)), ('A', '254', 7, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (121.91400000000002, 121.81700000000001, 91.23700000000001)), ('A', '259', 7, 'cablam Outlier', (126.8, 123.8, 90.0)), ('A', '260', 7, 'smoc Outlier', (129.80700000000002, 121.804, 91.12299999999999)), ('A', '286', 7, 'side-chain clash', (121.494, 120.999, 86.81)), ('A', '626', 8, 'side-chain clash', (98.935, 104.598, 97.223)), ('A', '631', 8, 'side-chain clash', (98.187, 107.17, 97.871)), ('A', '680', 8, 'side-chain clash', (98.935, 104.598, 97.223)), ('A', '387', 9, 'smoc Outlier', (112.194, 122.057, 118.726)), ('A', '400', 9, 'smoc Outlier', (107.65199999999999, 118.046, 120.282)), ('A', '401', 9, 'smoc Outlier', (104.228, 118.927, 121.68299999999999)), ('A', '275', 10, 'smoc Outlier', (111.037, 129.108, 94.05199999999999)), ('A', '277', 10, 'Dihedral angle:CB:CG:CD:OE1', (111.903, 131.592, 89.16799999999999)), ('A', '278', 10, 'side-chain clash', (113.898, 130.459, 91.405)), ('A', '484', 11, 'smoc Outlier', (78.304, 107.67399999999999, 88.781)), ('A', '575', 11, 'side-chain clash', (83.884, 109.163, 90.7)), ('A', '641', 11, 'side-chain clash', (83.884, 109.163, 90.7)), ('A', '726', 12, 'side-chain clash\nsmoc Outlier', (92.598, 100.016, 66.845)), ('A', '740', 12, 'smoc Outlier', (88.721, 105.465, 69.43900000000001)), ('A', '744', 12, 'side-chain clash\nDihedral angle:CB:CG:CD:OE1', (90.099, 99.549, 71.14)), ('A', '851', 13, 'cablam Outlier', (85.2, 83.1, 128.9)), ('A', '852', 13, 'side-chain clash', (79.369, 85.106, 128.971)), ('A', '853', 13, 'side-chain clash', (79.369, 85.106, 128.971)), ('A', '607', 14, 'cablam CA Geom Outlier', (84.5, 86.0, 80.5)), ('A', '608', 14, 'cablam Outlier\nsmoc Outlier', (85.5, 84.5, 77.2)), ('A', '610', 14, 'Dihedral angle:CB:CG:CD:OE1', (90.923, 81.667, 74.52799999999999)), ('A', '711', 15, 'side-chain clash', (111.288, 94.087, 64.513)), ('A', '713', 15, 'side-chain clash', (111.288, 94.087, 64.513)), ('A', '531', 16, 'side-chain clash', (102.948, 127.547, 110.563)), ('A', '567', 16, 'side-chain clash', (102.948, 127.547, 110.563)), ('A', '242', 17, 'side-chain clash', (107.856, 113.389, 83.004)), ('A', '312', 17, 'side-chain clash', (107.856, 113.389, 83.004)), ('A', '707', 18, 'side-chain clash', (104.757, 95.628, 70.845)), ('A', '724', 18, 'side-chain clash', (104.757, 95.628, 70.845)), ('A', '303', 19, 'side-chain clash', (93.719, 121.175, 81.751)), ('A', '306', 19, 'smoc Outlier', (97.99700000000001, 119.71000000000001, 82.663)), ('A', '580', 20, 'smoc Outlier', (80.303, 99.24900000000001, 96.04100000000001)), ('A', '581', 20, 'smoc Outlier', (76.819, 98.62899999999999, 94.584)), ('A', '900', 21, 'side-chain clash', (69.215, 76.264, 137.996)), ('A', '903', 21, 'cablam CA Geom Outlier', (68.2, 81.1, 138.5)), ('A', '647', 22, 'backbone clash', (85.843, 125.087, 87.814)), ('A', '648', 22, 'backbone clash', (85.843, 125.087, 87.814)), ('A', '335', 23, 'side-chain clash', (92.614, 138.083, 119.596)), ('A', '338', 23, 'side-chain clash', (92.614, 138.083, 119.596)), ('A', '859', 24, 'side-chain clash', (84.48, 81.369, 116.257)), ('A', '862', 24, 'side-chain clash', (84.48, 81.369, 116.257)), ('A', '751', 25, 'smoc Outlier', (89.35799999999999, 90.27, 75.989)), ('A', '754', 25, 'smoc Outlier', (90.436, 89.91400000000002, 82.52199999999999)), ('A', '168', 26, 'smoc Outlier', (120.502, 96.806, 101.021)), ('A', '169', 26, 'smoc Outlier', (119.532, 100.41600000000001, 100.191)), ('A', '715', 27, 'side-chain clash', (103.21, 89.796, 62.038)), ('A', '721', 27, 'side-chain clash', (103.21, 89.796, 62.038)), ('A', '155', 28, 'side-chain clash', (133.421, 93.514, 93.407)), ('A', '158', 28, 'smoc Outlier', (128.30700000000002, 89.10499999999999, 94.903)), ('A', '888', 29, 'smoc Outlier', (79.684, 75.57, 120.37199999999999)), ('A', '889', 29, 'smoc Outlier', (77.422, 72.806, 121.68199999999999)), ('A', '874', 30, 'smoc Outlier', (92.478, 66.489, 103.843)), ('A', '878', 30, 'smoc Outlier', (87.475, 69.016, 107.593)), ('A', '323', 31, 'smoc Outlier', (112.81700000000001, 120.512, 102.639)), ('A', '326', 31, 'cablam CA Geom Outlier', (107.9, 123.1, 102.0)), ('A', '802', 32, 'Dihedral angle:CB:CG:CD:OE1', (97.799, 78.71400000000001, 87.712)), ('A', '803', 32, 'smoc Outlier', (97.338, 76.766, 84.475)), ('B', '132', 1, 'side-chain clash', (123.924, 109.762, 122.314)), ('B', '138', 1, 'side-chain clash', (123.924, 109.762, 122.314)), ('B', '141', 1, 'backbone clash', (124.818, 114.67, 119.837)), ('B', '142', 1, 'backbone clash', (124.818, 114.67, 119.837)), ('B', '143', 1, 'smoc Outlier', (129.094, 115.932, 122.83)), ('B', '56', 2, 'side-chain clash', (47.249, 110.164, 121.312)), ('B', '58', 2, 'side-chain clash\nsmoc Outlier', (50.38, 110.483, 115.998)), ('B', '59', 2, 'side-chain clash', (47.249, 110.164, 121.312)), ('B', '62', 2, 'side-chain clash', (51.184, 111.954, 118.471)), ('B', '63', 2, 'smoc Outlier', (54.52, 113.785, 121.835)), ('B', '40', 3, 'side-chain clash', (26.898, 98.951, 115.012)), ('B', '43', 3, 'smoc Outlier', (29.517000000000003, 97.70100000000001, 117.508)), ('B', '44', 3, 'side-chain clash\nsmoc Outlier', (26.898, 98.951, 115.012)), ('B', '149', 4, 'smoc Outlier', (122.427, 122.702, 116.12899999999999)), ('B', '150', 4, 'smoc Outlier', (120.47, 124.82199999999999, 113.645)), ('B', '126', 5, 'backbone clash', (117.036, 126.754, 124.607)), ('B', '190', 5, 'backbone clash', (117.036, 126.754, 124.607)), ('B', '129', 6, 'smoc Outlier', (114.577, 117.795, 122.845)), ('B', '130', 6, 'smoc Outlier', (117.001, 115.368, 121.17699999999999)), ('B', '177', 7, 'side-chain clash', (127.06, 100.522, 128.625)), ('B', '178', 7, 'side-chain clash', (127.06, 100.522, 128.625)), ('B', '80', 8, 'smoc Outlier', (78.63, 122.049, 121.646)), ('B', '81', 8, 'smoc Outlier', (79.087, 124.79, 124.245)), ('B', '162', 9, 'smoc Outlier', (113.49900000000001, 105.577, 128.461)), ('B', '182', 9, 'cablam CA Geom Outlier', (118.3, 103.8, 125.6)), ('B', '91', 10, 'smoc Outlier', (93.846, 127.755, 121.516)), ('B', '92', 10, 'smoc Outlier', (94.51100000000001, 130.636, 123.912)), ('B', '52', 11, 'side-chain clash', (41.401, 108.421, 117.826)), ('B', '55', 11, 'side-chain clash', (41.401, 108.421, 117.826)), ('C', '13', 1, 'side-chain clash', (102.928, 81.194, 140.578)), ('C', '36', 1, 'side-chain clash', (102.774, 80.978, 140.568)), ('C', '40', 1, 'side-chain clash\nsmoc Outlier', (102.774, 80.978, 140.568)), ('C', '55', 1, 'side-chain clash', (102.928, 81.194, 140.578)), ('C', '23', 2, 'Dihedral angle:CB:CG:CD:OE1', (106.726, 96.992, 130.853)), ('C', '25', 2, 'smoc Outlier', (111.462, 98.83, 132.281)), ('C', '54', 3, 'side-chain clash', (114.095, 84.907, 131.383)), ('C', '58', 3, 'side-chain clash', (114.095, 84.907, 131.383)), ('C', '2', 4, 'side-chain clash', (105.952, 73.116, 124.037)), ('C', '6', 4, 'side-chain clash', (105.952, 73.116, 124.037)), ('D', '117', 1, 'side-chain clash\nsmoc Outlier', (120.621, 86.829, 143.735)), ('D', '131', 1, 'side-chain clash', (120.621, 86.829, 143.735)), ('D', '159', 1, 'side-chain clash', (129.619, 81.793, 145.08)), ('D', '182', 1, 'cablam CA Geom Outlier', (124.1, 83.9, 154.0)), ('D', '184', 1, 'smoc Outlier', (125.534, 84.07, 149.056)), ('D', '185', 1, 'side-chain clash', (122.325, 86.484, 145.418)), ('D', '186', 1, 'side-chain clash', (129.619, 81.793, 145.08)), ('D', '80', 2, 'Dihedral angle:CD:NE:CZ:NH1', (87.68599999999999, 91.35199999999999, 135.342)), ('D', '83', 2, 'cablam Outlier', (92.4, 87.7, 136.4)), ('D', '85', 2, 'smoc Outlier', (95.40700000000001, 84.697, 140.33100000000002)), ('D', '88', 2, 'side-chain clash', (100.023, 82.1, 139.43)), ('D', '92', 2, 'side-chain clash', (102.774, 80.978, 140.568)), ('D', '127', 3, 'side-chain clash', (130.917, 85.674, 133.408)), ('D', '155', 3, 'Dihedral angle:CB:CG:CD:OE1', (131.914, 76.979, 135.85500000000002)), ('D', '157', 3, 'side-chain clash', (132.308, 83.393, 134.786)), ('D', '189', 3, 'side-chain clash', (130.917, 85.674, 133.408)), ('D', '109', 4, 'backbone clash', (115.958, 79.034, 144.901)), ('D', '112', 4, 'smoc Outlier', (113.516, 76.26400000000001, 148.02800000000002)), ('D', '114', 4, 'backbone clash', (115.958, 79.034, 144.901)), ('D', '118', 5, 'cablam Outlier', (119.0, 88.2, 136.0)), ('D', '119', 5, 'side-chain clash', (115.541, 87.85, 131.658)), ('D', '96', 6, 'Dihedral angle:CD:NE:CZ:NH1', (103.94500000000001, 71.563, 135.412)), ('D', '99', 6, 'cablam Outlier', (107.4, 68.5, 132.4)), ('D', '101', 7, 'backbone clash', (115.842, 70.475, 131.708)), ('D', '102', 7, 'backbone clash', (115.842, 70.475, 131.708)), ('D', '13', 8, 'smoc Outlier', (38.873999999999995, 76.95, 129.55100000000002)), ('D', '15', 8, 'smoc Outlier', (38.713, 78.096, 124.17999999999999)), ('P', '5', 1, 'side-chain clash', (57.569, 87.267, 107.757)), ('P', '6', 1, 'side-chain clash', (60.323, 90.132, 105.139)), ('P', '7', 1, 'side-chain clash', (60.323, 90.132, 105.139)), ('P', '18', 2, 'Sugar pucker:-\nBackbone torsion suites: ', (91.983, 94.799, 102.197)), ('T', '9', 1, 'smoc Outlier', (88.787, 104.006, 106.483)), ('T', '18', 1, 'Backbone torsion suites: ', (62.766000000000005, 98.111, 118.181)), ('U', '15', 1, 'side-chain clash', (28.541, 99.956, 112.107))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (93.77700000000006, 117.38099999999999, 117.106)), ('B', ' 183 ', 'PRO', None, (116.458, 104.639, 124.23999999999998)), ('D', ' 183 ', 'PRO', None, (122.311, 84.952, 152.684))]
data['cablam'] = [('A', '220', 'GLY', 'check CA trace,carbonyls, peptide', ' \n---S-', (119.7, 110.8, 59.5)), ('A', '259', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nTTS-S', (126.8, 123.8, 90.0)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (94.4, 115.0, 116.8)), ('A', '509', 'TRP', 'check CA trace,carbonyls, peptide', 'turn\nGGT-B', (87.4, 116.3, 123.7)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nTSS-S', (85.5, 84.5, 77.2)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (107.6, 112.3, 102.7)), ('A', '851', 'ASP', 'check CA trace,carbonyls, peptide', 'helix\nHHHSS', (85.2, 83.1, 128.9)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (129.9, 103.3, 89.8)), ('A', '326', 'PHE', 'check CA trace', ' \nTT-EE', (107.9, 123.1, 102.0)), ('A', '607', 'SER', 'check CA trace', 'bend\nHTSS-', (84.5, 86.0, 80.5)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (104.7, 110.6, 100.9)), ('A', '903', 'TYR', 'check CA trace', 'bend\nHHS--', (68.2, 81.1, 138.5)), ('B', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (118.3, 103.8, 125.6)), ('D', '83', 'VAL', ' alpha helix', 'bend\nHSSHH', (92.4, 87.7, 136.4)), ('D', '99', 'ASP', 'check CA trace,carbonyls, peptide', ' \nHH--H', (107.4, 68.5, 132.4)), ('D', '118', 'ASN', 'check CA trace,carbonyls, peptide', 'bend\nBSS--', (119.0, 88.2, 136.0)), ('D', '182', 'TRP', 'check CA trace', 'bend\nS-SSE', (124.1, 83.9, 154.0))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-11007/6yyt/Model_validation_1/validation_cootdata/molprobity_probe6yyt_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

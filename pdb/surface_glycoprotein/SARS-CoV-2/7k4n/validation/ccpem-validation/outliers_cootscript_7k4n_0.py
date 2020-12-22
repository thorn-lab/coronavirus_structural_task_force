
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
data['rota'] = []
data['cbeta'] = []
data['smoc'] = []
data['jpred'] = []
data['clusters'] = [('A', '108', 1, 'cablam Outlier', (308.0, 283.8, 282.0)), ('A', '110', 1, 'cablam Outlier', (312.9, 283.4, 284.9)), ('A', '112', 1, 'cablam Outlier', (312.6, 281.1, 290.4)), ('A', '797', 2, 'cablam Outlier', (292.0, 254.9, 197.0)), ('A', '898', 2, 'side-chain clash', (287.849, 255.924, 194.662)), ('A', '899', 2, 'side-chain clash', (287.849, 255.924, 194.662)), ('A', '666', 3, 'cablam Outlier', (287.3, 290.4, 232.5)), ('A', '667', 3, 'cablam Outlier', (283.8, 291.4, 231.6)), ('A', '792', 4, 'side-chain clash', (291.23, 244.016, 201.839)), ('A', '793', 4, 'side-chain clash', (291.23, 244.016, 201.839)), ('A', '1109', 5, 'cablam Outlier', (283.5, 277.1, 191.1)), ('A', '1111', 5, 'cablam Outlier', (284.7, 277.3, 185.0)), ('A', '521', 6, 'cablam Outlier', (255.6, 297.1, 279.1)), ('A', '522', 6, 'cablam Outlier', (258.1, 298.3, 281.8)), ('A', '891', 7, 'cablam Outlier', (271.4, 249.4, 204.0)), ('A', '892', 7, 'cablam CA Geom Outlier', (273.8, 246.9, 202.2)), ('H', '108', 1, 'cablam Outlier', (248.5, 292.9, 334.8)), ('L', '96', 1, 'cablam CA Geom Outlier', (250.0, 309.5, 338.0)), ('L', '102', 1, 'cablam Outlier', (249.0, 302.3, 355.1)), ('B', '108', 1, 'cablam Outlier', (236.3, 295.2, 282.0)), ('B', '110', 1, 'cablam Outlier', (234.1, 299.7, 284.9)), ('B', '112', 1, 'cablam Outlier', (236.3, 300.6, 290.4)), ('B', '797', 2, 'cablam Outlier', (269.2, 295.8, 197.0)), ('B', '898', 2, 'side-chain clash', (270.84, 291.684, 194.792)), ('B', '899', 2, 'side-chain clash', (270.84, 291.684, 194.792)), ('B', '666', 3, 'cablam Outlier', (240.8, 274.0, 232.5)), ('B', '667', 3, 'cablam Outlier', (241.7, 270.4, 231.6)), ('B', '792', 4, 'side-chain clash', (279.047, 300.58, 202.004)), ('B', '793', 4, 'side-chain clash', (279.047, 300.58, 202.004)), ('B', '1109', 5, 'cablam Outlier', (254.2, 277.4, 191.1)), ('B', '1111', 5, 'cablam Outlier', (253.5, 278.3, 185.0)), ('B', '521', 6, 'cablam Outlier', (250.9, 243.2, 279.1)), ('B', '522', 6, 'cablam Outlier', (248.6, 244.8, 281.8)), ('B', '891', 7, 'cablam Outlier', (284.3, 280.8, 204.0)), ('B', '892', 7, 'cablam CA Geom Outlier', (285.2, 284.1, 202.2)), ('C', '108', 1, 'cablam Outlier', (258.1, 239.2, 334.8)), ('D', '96', 1, 'cablam CA Geom Outlier', (242.9, 232.1, 338.0)), ('D', '102', 1, 'cablam Outlier', (249.7, 234.9, 355.1)), ('E', '108', 1, 'cablam Outlier', (262.2, 227.4, 282.0)), ('E', '110', 1, 'cablam Outlier', (259.3, 223.3, 284.9)), ('E', '112', 1, 'cablam Outlier', (257.5, 224.7, 290.4)), ('E', '797', 2, 'cablam Outlier', (245.2, 255.6, 197.0)), ('E', '898', 2, 'side-chain clash', (247.93, 259.068, 194.864)), ('E', '899', 2, 'side-chain clash', (247.93, 259.068, 194.864)), ('E', '666', 3, 'cablam Outlier', (278.3, 242.0, 232.5)), ('E', '667', 3, 'cablam Outlier', (280.9, 244.5, 231.6)), ('E', '1109', 4, 'cablam Outlier', (268.6, 251.9, 191.1)), ('E', '1111', 4, 'cablam Outlier', (268.2, 250.8, 185.0)), ('E', '521', 5, 'cablam Outlier', (299.9, 266.1, 279.1)), ('E', '522', 5, 'cablam Outlier', (299.7, 263.3, 281.8)), ('E', '891', 6, 'cablam Outlier', (250.7, 276.3, 204.0)), ('E', '892', 6, 'cablam CA Geom Outlier', (247.4, 275.4, 202.2)), ('F', '108', 1, 'cablam Outlier', (299.8, 274.4, 334.8)), ('G', '96', 1, 'cablam CA Geom Outlier', (313.5, 264.7, 338.0)), ('G', '102', 1, 'cablam Outlier', (307.7, 269.2, 355.1)), ('I', '1', 1, 'Bond angle:C8:C7:N2', (294.28999999999996, 277.078, 189.316)), ('K', '2', 1, 'Bond angle:C8:C7:N2', (265.879, 297.648, 166.87800000000001)), ('M', '1', 1, 'side-chain clash\nBond angle:C8:C7:N2', (267.907, 313.262, 293.42799999999994)), ('N', '1', 1, 'Bond angle:C8:C7:N2', (299.58, 254.88100000000003, 200.40200000000002)), ('O', '1', 1, 'Bond angle:C8:C7:N2', (248.88600000000002, 286.73599999999993, 189.316)), ('Q', '2', 1, 'Bond angle:C8:C7:N2', (245.277, 251.847, 166.87800000000001)), ('R', '1', 1, 'side-chain clash\nBond angle:C8:C7:N2', (230.74099999999999, 245.795, 293.42799999999994)), ('S', '1', 1, 'Bond angle:C8:C7:N2', (265.464, 302.41499999999996, 200.40200000000002)), ('T', '1', 1, 'Bond angle:C8:C7:N2', (263.224, 242.586, 189.316)), ('V', '2', 1, 'Bond angle:C8:C7:N2', (295.244, 256.905, 166.87800000000001)), ('W', '1', 1, 'side-chain clash\nBond angle:C8:C7:N2', (307.752, 247.342, 293.42799999999994)), ('X', '1', 1, 'Bond angle:C8:C7:N2', (241.35600000000002, 249.10299999999998, 200.40200000000002))]
data['probe'] = [(' B1028  LYS  NZ ', ' B1042  PHE  O  ', -0.496, (263.682, 277.153, 213.296)), (' E 342  PHE  HB2', ' W   1  NAG  H82', -0.494, (308.418, 248.167, 294.769)), (' A1028  LYS  NZ ', ' A1042  PHE  O  ', -0.494, (278.689, 268.83, 213.692)), (' E1028  LYS  NZ ', ' E1042  PHE  O  ', -0.489, (264.176, 260.281, 213.306)), (' A 342  PHE  HB2', ' M   1  NAG  H82', -0.489, (266.836, 313.253, 294.777)), (' B 342  PHE  HB2', ' R   1  NAG  H82', -0.482, (231.08, 244.879, 294.806)), (' E1142  GLN  HB2', ' E1143  PRO  HD3', -0.449, (273.659, 260.463, 164.592)), (' B1142  GLN  HB2', ' B1143  PRO  HD3', -0.436, (259.15, 268.797, 164.427)), (' A1142  GLN  HB2', ' A1143  PRO  HD3', -0.435, (273.173, 277.229, 164.415)), (' A 898  PHE  N  ', ' A 899  PRO  CD ', -0.422, (287.849, 255.924, 194.662)), (' B 898  PHE  N  ', ' B 899  PRO  CD ', -0.417, (270.84, 291.684, 194.792)), (' E 898  PHE  N  ', ' E 899  PRO  CD ', -0.417, (247.93, 259.068, 194.864)), (' B 792  PRO  HA ', ' B 793  PRO  HD3', -0.411, (279.047, 300.58, 202.004)), (' A 792  PRO  HA ', ' A 793  PRO  HD3', -0.404, (291.23, 244.016, 201.839))]
data['omega'] = [('D', '   8 ', 'PRO', None, (258.19600000000014, 231.89599999999993, 358.596)), ('G', '   8 ', 'PRO', None, (306.0620000000001, 278.0689999999999, 358.596)), ('L', '   8 ', 'PRO', None, (242.14200000000005, 296.435, 358.596))]
data['cablam'] = [('A', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSEE', (304.6, 263.0, 261.4)), ('A', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (302.9, 282.2, 269.2)), ('A', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (308.0, 283.8, 282.0)), ('A', '110', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS-BS', (312.9, 283.4, 284.9)), ('A', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (312.6, 281.1, 290.4)), ('A', '214', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (327.0, 287.4, 257.3)), ('A', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (247.0, 305.7, 329.2)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (249.9, 300.9, 333.6)), ('A', '521', 'PRO', ' beta sheet', ' \nSS---', (255.6, 297.1, 279.1)), ('A', '522', 'ALA', ' beta sheet', ' \nS---B', (258.1, 298.3, 281.8)), ('A', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (287.3, 290.4, 232.5)), ('A', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (283.8, 291.4, 231.6)), ('A', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (292.0, 254.9, 197.0)), ('A', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nTSSS-', (271.4, 249.4, 204.0)), ('A', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (277.0, 257.8, 207.3)), ('A', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (279.9, 269.1, 210.3)), ('A', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (285.1, 258.8, 227.2)), ('A', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (265.7, 287.5, 170.2)), ('A', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (283.5, 277.1, 191.1)), ('A', '1111', 'GLU', ' beta sheet', ' \nS---E', (284.7, 277.3, 185.0)), ('A', '34', 'ARG', 'check CA trace', ' \nTT---', (313.1, 279.7, 255.5)), ('A', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (302.3, 286.7, 250.5)), ('A', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (276.6, 297.8, 259.2)), ('A', '892', 'PRO', 'check CA trace', 'bend\nSSS--', (273.8, 246.9, 202.2)), ('H', '108', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (248.5, 292.9, 334.8)), ('L', '102', 'GLN', 'check CA trace,carbonyls, peptide', ' \nE----', (249.0, 302.3, 355.1)), ('L', '96', 'THR', 'check CA trace', 'bend\nSSS--', (250.0, 309.5, 338.0)), ('B', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSEE', (255.9, 302.7, 261.4)), ('B', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (240.1, 291.6, 269.2)), ('B', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (236.3, 295.2, 282.0)), ('B', '110', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS-BS', (234.1, 299.7, 284.9)), ('B', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (236.3, 300.6, 290.4)), ('B', '214', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (223.6, 309.9, 257.3)), ('B', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (247.7, 231.5, 329.2)), ('B', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (250.5, 236.4, 333.6)), ('B', '521', 'PRO', ' beta sheet', ' \nSS---', (250.9, 243.2, 279.1)), ('B', '522', 'ALA', ' beta sheet', ' \nS---B', (248.6, 244.8, 281.8)), ('B', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (240.8, 274.0, 232.5)), ('B', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (241.7, 270.4, 231.6)), ('B', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (269.2, 295.8, 197.0)), ('B', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nTSSS-', (284.3, 280.8, 204.0)), ('B', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (274.2, 281.4, 207.3)), ('B', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (263.0, 278.2, 210.3)), ('B', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (269.3, 287.9, 227.2)), ('B', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (254.2, 256.8, 170.2)), ('B', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (254.2, 277.4, 191.1)), ('B', '1111', 'GLU', ' beta sheet', ' \nS---E', (253.5, 278.3, 185.0)), ('B', '34', 'ARG', 'check CA trace', ' \nTT---', (237.2, 301.7, 255.5)), ('B', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (236.6, 288.9, 250.5)), ('B', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (239.8, 261.1, 259.2)), ('B', '892', 'PRO', 'check CA trace', 'bend\nSSS--', (285.2, 284.1, 202.2)), ('C', '108', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (258.1, 239.2, 334.8)), ('D', '102', 'GLN', 'check CA trace,carbonyls, peptide', ' \nE----', (249.7, 234.9, 355.1)), ('D', '96', 'THR', 'check CA trace', 'bend\nSSS--', (242.9, 232.1, 338.0)), ('E', '41', 'LYS', 'check CA trace,carbonyls, peptide', 'bend\nSSSEE', (245.8, 240.7, 261.4)), ('E', '88', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n--SEE', (263.4, 232.6, 269.2)), ('E', '108', 'THR', 'check CA trace,carbonyls, peptide', 'bend\nEESS-', (262.2, 227.4, 282.0)), ('E', '110', 'LEU', 'check CA trace,carbonyls, peptide', ' \nSS-BS', (259.3, 223.3, 284.9)), ('E', '112', 'SER', 'check CA trace,carbonyls, peptide', 'bend\n-BSSS', (257.5, 224.7, 290.4)), ('E', '214', 'ARG', 'check CA trace,carbonyls, peptide', 'bend\n-SSS-', (255.8, 209.1, 257.3)), ('E', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nT--BT', (311.7, 269.2, 329.2)), ('E', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (306.0, 269.2, 333.6)), ('E', '521', 'PRO', ' beta sheet', ' \nSS---', (299.9, 266.1, 279.1)), ('E', '522', 'ALA', ' beta sheet', ' \nS---B', (299.7, 263.3, 281.8)), ('E', '666', 'ILE', 'check CA trace,carbonyls, peptide', 'strand\nEEEET', (278.3, 242.0, 232.5)), ('E', '667', 'GLY', 'check CA trace,carbonyls, peptide', 'strand\nEEETT', (280.9, 244.5, 231.6)), ('E', '797', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\n--SSS', (245.2, 255.6, 197.0)), ('E', '891', 'GLY', 'check CA trace,carbonyls, peptide', 'bend\nTSSS-', (250.7, 276.3, 204.0)), ('E', '1034', 'LEU', 'check CA trace,carbonyls, peptide', 'bend\nIISS-', (255.2, 267.2, 207.3)), ('E', '1043', 'CYS', 'check CA trace,carbonyls, peptide', 'turn\nBTTBS', (263.5, 259.1, 210.3)), ('E', '1058', 'HIS', 'check CA trace,carbonyls, peptide', 'turn\nETTEE', (252.0, 259.7, 227.2)), ('E', '1084', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nESSSE', (286.5, 262.2, 170.2)), ('E', '1109', 'PHE', 'check CA trace,carbonyls, peptide', 'bend\nTTS--', (268.6, 251.9, 191.1)), ('E', '1111', 'GLU', ' beta sheet', ' \nS---E', (268.2, 250.8, 185.0)), ('E', '34', 'ARG', 'check CA trace', ' \nTT---', (256.1, 225.0, 255.5)), ('E', '293', 'LEU', 'check CA trace', 'bend\nTTS-H', (267.5, 230.9, 250.5)), ('E', '549', 'THR', 'check CA trace', 'strand\nEEEEE', (290.0, 247.6, 259.2)), ('E', '892', 'PRO', 'check CA trace', 'bend\nSSS--', (247.4, 275.4, 202.2)), ('F', '108', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nE-SS-', (299.8, 274.4, 334.8)), ('G', '102', 'GLN', 'check CA trace,carbonyls, peptide', ' \nE----', (307.7, 269.2, 355.1)), ('G', '96', 'THR', 'check CA trace', 'bend\nSSS--', (313.5, 264.7, 338.0))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22668/7k4n/Model_validation_1/validation_cootdata/molprobity_probe7k4n_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

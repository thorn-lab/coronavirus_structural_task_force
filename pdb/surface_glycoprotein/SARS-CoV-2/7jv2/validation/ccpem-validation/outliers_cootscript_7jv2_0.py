
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
data['probe'] = []
data['jpred'] = []
data['rota'] = [('H', '   6 ', 'GLU', 0.2534431871999097, (191.841, 190.339, 201.28100000000006)), ('H', '  59 ', 'TYR', 0.15591234289390327, (181.97300000000007, 207.22299999999998, 201.929)), ('A', ' 483 ', 'VAL', 0.06358273094519973, (199.567, 199.829, 214.712))]
data['clusters'] = [('H', '20', 1, 'smoc Outlier', (185.035, 191.085, 198.306)), ('H', '4', 1, 'smoc Outlier', (195.189, 192.629, 206.32800000000003)), ('H', '6', 1, 'Rotamer', (191.841, 190.339, 201.28100000000006)), ('H', '7', 1, 'cablam CA Geom Outlier', (190.2, 187.8, 199.0)), ('H', '95', 1, 'smoc Outlier', (193.35600000000002, 196.466, 198.291)), ('H', '89', 2, 'smoc Outlier', (186.04299999999998, 198.45800000000003, 182.61499999999998)), ('H', '90', 2, 'Dihedral angle:CA:CB:CG:OD1', (186.509, 197.94, 186.35000000000002)), ('L', '105', 1, 'smoc Outlier', (205.538, 209.85000000000002, 189.16)), ('L', '34', 1, 'cablam Outlier', (196.6, 215.6, 205.2)), ('L', '36', 1, 'smoc Outlier', (200.029, 210.931, 201.9)), ('L', '49', 1, 'smoc Outlier', (205.933, 206.348, 203.39600000000002)), ('L', '50', 1, 'smoc Outlier', (204.474, 209.641, 204.526)), ('L', '53', 1, 'cablam Outlier', (201.8, 215.8, 205.5)), ('L', '7', 1, 'smoc Outlier', (205.83800000000002, 215.306, 187.05100000000002)), ('L', '89', 1, 'smoc Outlier', (201.85800000000003, 208.197, 194.258)), ('L', '91', 1, 'smoc Outlier', (197.105, 211.285, 197.817)), ('L', '109', 2, 'smoc Outlier', (217.993, 205.71499999999997, 189.339)), ('L', '11', 2, 'smoc Outlier', (215.798, 210.32100000000003, 186.636)), ('L', '13', 2, 'smoc Outlier', (222.04899999999998, 209.52700000000002, 189.73999999999998)), ('L', '18', 2, 'smoc Outlier', (215.23899999999998, 213.79299999999998, 194.17)), ('L', '80', 2, 'smoc Outlier', (218.91, 208.13, 195.727)), ('L', '69', 3, 'cablam Outlier\nsmoc Outlier', (207.0, 223.7, 198.5)), ('L', '74', 3, 'smoc Outlier', (206.685, 217.089, 197.803)), ('L', '75', 3, 'smoc Outlier', (208.585, 213.95600000000002, 198.646)), ('L', '94', 4, 'cablam Outlier', (189.5, 217.5, 200.2)), ('L', '95', 4, 'cablam CA Geom Outlier', (186.1, 218.6, 201.7)), ('L', '26', 5, 'cablam CA Geom Outlier', (192.2, 224.1, 193.4)), ('L', '97', 5, 'cablam Outlier', (186.9, 211.5, 202.9)), ('A', '483', 1, 'Rotamer', (199.567, 199.829, 214.712)), ('A', '484', 1, 'cablam Outlier', (201.5, 203.1, 214.4))]
data['cablam'] = [('H', '30', 'SER', ' three-ten', 'turn\n-STTS', (187.3, 198.5, 216.3)), ('H', '7', 'SER', 'check CA trace', 'strand\nEEE--', (190.2, 187.8, 199.0)), ('L', '34', 'TYR', 'check CA trace,carbonyls, peptide', ' \nGG--E', (196.6, 215.6, 205.2)), ('L', '53', 'THR', 'check CA trace,carbonyls, peptide', 'turn\nETTTE', (201.8, 215.8, 205.5)), ('L', '69', 'LEU', 'check CA trace,carbonyls, peptide', ' \n-B-SS', (207.0, 223.7, 198.5)), ('L', '94', 'TYR', 'check CA trace,carbonyls, peptide', ' \nE--SS', (189.5, 217.5, 200.2)), ('L', '97', 'ALA', 'check CA trace,carbonyls, peptide', 'bend\nSSS--', (186.9, 211.5, 202.9)), ('L', '26', 'THR', 'check CA trace', 'bend\nESSS-', (192.2, 224.1, 193.4)), ('L', '95', 'SER', 'check CA trace', 'bend\n--SSS', (186.1, 218.6, 201.7)), ('A', '484', 'GLU', 'check CA trace,carbonyls, peptide', ' \nS--BT', (201.5, 203.1, 214.4)), ('A', '486', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n-BTTE', (198.2, 209.4, 214.7))]
data['smoc'] = [('H', 4, u'LEU', 0.6475699915733981, (195.189, 192.629, 206.32800000000003)), ('H', 20, u'LEU', 0.6877835690497492, (185.035, 191.085, 198.306)), ('H', 45, u'LEU', 0.7150274470978021, (196.222, 203.757, 192.38500000000002)), ('H', 48, u'VAL', 0.6652298792002203, (187.38500000000002, 203.839, 195.99200000000002)), ('H', 63, u'SER', 0.6980322082784468, (182.567, 206.812, 190.129)), ('H', 73, u'ASP', 0.6023411561943849, (181.297, 192.971, 211.18200000000002)), ('H', 85, u'SER', 0.5789031435576452, (176.423, 195.918, 187.894)), ('H', 89, u'GLU', 0.5903237262490936, (186.04299999999998, 198.45800000000003, 182.61499999999998)), ('H', 95, u'TYR', 0.695357756899538, (193.35600000000002, 196.466, 198.291)), ('H', 117, u'THR', 0.5515341632708979, (188.805, 190.318, 186.61299999999997)), ('L', 7, u'GLU', 0.655930057922493, (205.83800000000002, 215.306, 187.05100000000002)), ('L', 11, u'THR', 0.7265238807714858, (215.798, 210.32100000000003, 186.636)), ('L', 13, u'SER', 0.6235692910343642, (222.04899999999998, 209.52700000000002, 189.73999999999998)), ('L', 18, u'VAL', 0.6894960993748961, (215.23899999999998, 213.79299999999998, 194.17)), ('L', 36, u'TYR', 0.6884008554075334, (200.029, 210.931, 201.9)), ('L', 49, u'LEU', 0.661030567845849, (205.933, 206.348, 203.39600000000002)), ('L', 50, u'ILE', 0.6609576824816723, (204.474, 209.641, 204.526)), ('L', 69, u'LEU', 0.6727669436491052, (206.95600000000002, 223.659, 198.507)), ('L', 74, u'ALA', 0.7336827461908443, (206.685, 217.089, 197.803)), ('L', 75, u'LEU', 0.652970010216976, (208.585, 213.95600000000002, 198.646)), ('L', 80, u'ALA', 0.6680810670940589, (218.91, 208.13, 195.727)), ('L', 89, u'TYR', 0.7056176368889384, (201.85800000000003, 208.197, 194.258)), ('L', 91, u'LEU', 0.6537801825690742, (197.105, 211.285, 197.817)), ('L', 105, u'THR', 0.7111669804630176, (205.538, 209.85000000000002, 189.16)), ('L', 109, u'VAL', 0.7126051177560325, (217.993, 205.71499999999997, 189.339)), ('A', 443, u'SER', 0.6457549235445895, (228.65800000000002, 211.535, 207.418)), ('A', 446, u'GLY', 0.5732321755903093, (223.99200000000002, 210.83, 200.259)), ('A', 454, u'ARG', 0.6351736299229652, (215.126, 208.13899999999998, 221.094)), ('A', 460, u'ASN', 0.5985281016004277, (213.05, 210.094, 231.997)), ('A', 474, u'GLN', 0.6196189087037611, (201.21699999999998, 206.341, 223.017)), ('A', 495, u'TYR', 0.6951825947461732, (219.77299999999997, 211.64399999999998, 212.42600000000002))]
gui = coot_molprobity_todo_list_gui(data=data)

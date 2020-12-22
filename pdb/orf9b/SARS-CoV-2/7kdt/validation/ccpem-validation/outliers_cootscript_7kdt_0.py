
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
data['rota'] = [('A', ' 132 ', 'GLN', 0.1505045612277894, (95.001, 121.681, 153.514)), ('A', ' 520 ', 'GLN', 0.117888432354712, (115.29700000000001, 88.158, 106.91199999999998))]
data['clusters'] = [('A', '340', 1, 'smoc Outlier', (109.908, 117.70400000000001, 92.846)), ('A', '341', 1, 'smoc Outlier', (112.702, 115.045, 92.279)), ('A', '348', 1, 'smoc Outlier', (107.609, 123.44500000000001, 92.17099999999999)), ('A', '349', 1, 'Bond angle:CA:C\nBond angle:CA:C:O', (104.113, 124.897, 93.05799999999999)), ('A', '350', 1, 'Bond angle:N', (104.363, 128.23999999999998, 91.004)), ('A', '351', 1, 'Dihedral angle:CA:CB:CG:OD1', (105.654, 126.392, 87.87199999999999)), ('A', '352', 1, 'smoc Outlier', (102.691, 123.95100000000001, 88.139)), ('A', '355', 1, 'smoc Outlier', (100.868, 125.532, 83.516)), ('A', '366', 1, 'Planar group:CD:NE:CZ:NH1:NH2', (97.55799999999999, 120.351, 81.881)), ('A', '367', 1, 'smoc Outlier', (96.68199999999999, 116.77499999999999, 82.887)), ('A', '371', 1, 'smoc Outlier', (99.251, 114.644, 88.57799999999999)), ('A', '373', 1, 'Planar group:CD:NE:CZ:NH1:NH2', (100.169, 119.079, 91.974)), ('A', '298', 2, 'Planar group:CB:CG:CD1:CD2:CE1:CE2:CZ:OH\nsmoc Outlier', (112.551, 122.17499999999998, 77.18199999999999)), ('A', '320', 2, 'Dihedral angle:CA:C', (113.455, 128.535, 77.906)), ('A', '321', 2, 'Dihedral angle:N:CA\ncablam Outlier', (110.93100000000001, 130.296, 80.16999999999999)), ('A', '322', 2, 'cablam Outlier', (111.0, 134.1, 79.4)), ('A', '323', 2, 'cablam CA Geom Outlier', (110.5, 133.1, 75.7)), ('A', '334', 2, 'smoc Outlier', (110.104, 119.927, 83.071)), ('A', '335', 2, 'Planar group:CD:NE:CZ:NH1:NH2', (111.51700000000001, 122.41000000000001, 85.691)), ('A', '419', 3, 'Dihedral angle:CB:CG:CD:OE1', (88.982, 103.221, 93.141)), ('A', '421', 3, 'smoc Outlier', (91.34100000000001, 98.78, 90.651)), ('A', '424', 3, 'smoc Outlier', (94.38799999999999, 100.513, 86.88199999999999)), ('A', '437', 3, 'smoc Outlier', (99.76100000000001, 97.633, 83.972)), ('A', '438', 3, 'smoc Outlier', (98.745, 93.926, 84.281)), ('A', '176', 4, 'smoc Outlier', (108.037, 113.70100000000001, 141.82800000000003)), ('A', '179', 4, 'smoc Outlier', (110.012, 110.40100000000001, 145.077)), ('A', '180', 4, 'smoc Outlier', (112.23, 109.118, 142.172)), ('A', '186', 4, 'Planar group:CB:CG:CD1:CD2:CE1:CE2:CZ:OH', (108.309, 103.992, 140.894)), ('A', '447', 5, 'Planar group:CD:NE:CZ:NH1:NH2', (95.059, 94.143, 98.08)), ('A', '451', 5, 'Dihedral angle:CA:C', (91.63, 94.021, 102.923)), ('A', '452', 5, 'Dihedral angle:N:CA', (88.77499999999999, 91.51700000000001, 102.82799999999999)), ('A', '109', 6, 'smoc Outlier', (103.399, 105.928, 167.016)), ('A', '112', 6, 'smoc Outlier', (101.32, 105.485, 162.55200000000002)), ('A', '115', 6, 'Bond length:C:O', (100.362, 106.958, 157.80200000000002)), ('A', '481', 7, 'smoc Outlier', (105.019, 92.633, 93.771)), ('A', '483', 7, 'side-chain clash', (109.859, 89.463, 97.14)), ('A', '499', 7, 'side-chain clash', (109.859, 89.463, 97.14)), ('A', '520', 8, 'Rotamer', (115.29700000000001, 88.158, 106.91199999999998)), ('A', '523', 8, 'cablam CA Geom Outlier', (111.8, 85.1, 108.2)), ('A', '524', 8, 'cablam CA Geom Outlier', (112.5, 83.9, 111.8)), ('A', '568', 9, 'smoc Outlier', (119.34, 107.127, 110.554)), ('A', '584', 9, 'smoc Outlier', (113.601, 109.81400000000001, 110.955)), ('A', '587', 9, 'smoc Outlier', (113.71000000000001, 107.29400000000001, 115.474)), ('A', '409', 10, 'smoc Outlier', (99.073, 103.985, 92.64)), ('A', '413', 10, 'smoc Outlier', (98.43900000000001, 103.553, 99.20400000000001)), ('B', '46', 1, 'Dihedral angle:CA:C\nsmoc Outlier', (104.798, 108.986, 99.095)), ('B', '47', 1, 'Dihedral angle:N:CA', (108.02499999999999, 108.44400000000002, 97.194))]
data['probe'] = [(' A 483  ALA  HB1', ' A 499  TYR  CZ ', -0.482, (109.859, 89.463, 97.14))]
data['cablam'] = [('A', '321', 'ILE', ' three-ten', 'bend\nHHSSS', (110.9, 130.3, 80.2)), ('A', '322', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\nHSSS-', (111.0, 134.1, 79.4)), ('A', '323', 'ALA', 'check CA trace', 'bend\nSSS-H', (110.5, 133.1, 75.7)), ('A', '523', 'TRP', 'check CA trace', 'bend\nTTSS-', (111.8, 85.1, 108.2)), ('A', '524', 'LYS', 'check CA trace', 'bend\nTSS--', (112.5, 83.9, 111.8))]
data['smoc'] = [('A', 109, u'ASN', 0.5991004254716743, (103.399, 105.928, 167.016)), ('A', 112, u'ASP', 0.665862957140392, (101.32, 105.485, 162.55200000000002)), ('A', 148, u'LYS', 0.5821365459226332, (113.137, 102.70700000000001, 159.864)), ('A', 164, u'GLU', 0.7148653465399393, (98.501, 119.256, 139.36700000000002)), ('A', 176, u'CYS', 0.5948242614826518, (108.037, 113.70100000000001, 141.82800000000003)), ('A', 179, u'ALA', 0.6509425563367371, (110.012, 110.40100000000001, 145.077)), ('A', 180, u'VAL', 0.6755461640531404, (112.23, 109.118, 142.172)), ('A', 215, u'ILE', 0.6063063228374749, (110.16999999999999, 99.953, 129.447)), ('A', 257, u'ILE', 0.6757612594112105, (115.40400000000001, 109.038, 87.62499999999999)), ('A', 264, u'PHE', 0.7008583844538206, (104.95100000000001, 108.58, 82.37599999999999)), ('A', 298, u'TYR', 0.5990283994681551, (112.551, 122.17499999999998, 77.18199999999999)), ('A', 305, u'MET', 0.7112321957257324, (117.871, 114.131, 79.952)), ('A', 334, u'LEU', 0.4634840136134513, (110.104, 119.927, 83.071)), ('A', 340, u'LEU', 0.5984837986577208, (109.908, 117.70400000000001, 92.846)), ('A', 341, u'LEU', 0.6109202860789735, (112.702, 115.045, 92.279)), ('A', 348, u'ALA', 0.4823283362065648, (107.609, 123.44500000000001, 92.17099999999999)), ('A', 352, u'LEU', 0.5363939408228989, (102.691, 123.95100000000001, 88.139)), ('A', 355, u'VAL', 0.4808932154062348, (100.868, 125.532, 83.516)), ('A', 367, u'ALA', 0.6057932230042693, (96.68199999999999, 116.77499999999999, 82.887)), ('A', 371, u'ILE', 0.5885993798691195, (99.251, 114.644, 88.57799999999999)), ('A', 409, u'GLN', 0.597159360445823, (99.073, 103.985, 92.64)), ('A', 413, u'LEU', 0.6544046572528573, (98.43900000000001, 103.553, 99.20400000000001)), ('A', 421, u'VAL', 0.6777106156289491, (91.34100000000001, 98.78, 90.651)), ('A', 424, u'PHE', 0.6726507019437008, (94.38799999999999, 100.513, 86.88199999999999)), ('A', 437, u'ALA', 0.6981472623021663, (99.76100000000001, 97.633, 83.972)), ('A', 438, u'GLN', 0.7134920704630174, (98.745, 93.926, 84.281)), ('A', 481, u'LEU', 0.5637999405776544, (105.019, 92.633, 93.771)), ('A', 505, u'LEU', 0.6992580737000155, (116.863, 90.005, 85.765)), ('A', 547, u'ALA', 0.5462958362991842, (118.691, 100.589, 102.824)), ('A', 568, u'PHE', 0.515919402989661, (119.34, 107.127, 110.554)), ('A', 584, u'LEU', 0.6008591578040339, (113.601, 109.81400000000001, 110.955)), ('A', 587, u'LEU', 0.5434366366317522, (113.71000000000001, 107.29400000000001, 115.474)), ('B', 46, u'LEU', 0.47997841334431907, (104.798, 108.986, 99.095)), ('B', 52, u'LEU', 0.47970239093250605, (104.536, 100.35499999999999, 93.79700000000001)), ('B', 67, u'LYS', 0.606592081751827, (109.068, 96.762, 117.161))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-22829/7kdt/Model_validation_1/validation_cootdata/molprobity_probe7kdt_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)


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
data['probe'] = [(' A 571  PHE  CZ ', ' A 642  HIS  CD2', -0.671, (133.473, 160.242, 141.78)), (' A 487  CYS  SG ', ' A 642  HIS  ND1', -0.554, (129.682, 160.794, 141.834)), (' A 593  LYS  HE2', ' A 594  PHE  CZ ', -0.477, (128.095, 131.61, 157.252)), (' B 177  SER  N  ', ' B 178  PRO  CD ', -0.446, (173.794, 149.784, 181.726)), (' A 487  CYS  SG ', ' A 642  HIS  CE1', -0.446, (129.683, 160.598, 142.318)), (' A 393  THR  OG1', ' A 394  THR  N  ', -0.443, (160.874, 154.725, 161.647)), (' A 480  PHE  HA ', ' A 483  TYR  HE1', -0.443, (132.318, 145.64, 138.531)), (' B 112  ASP  N  ', ' B 112  ASP  OD1', -0.42, (154.288, 182.564, 148.955)), (' A 402  THR  OG1', ' A 403  ASN  N  ', -0.414, (152.907, 166.108, 175.856)), (' A 258  ASP  N  ', ' A 258  ASP  OD1', -0.408, (176.282, 168.361, 141.268)), (' B 120  ILE  N  ', ' B 121  PRO  CD ', -0.407, (156.764, 173.244, 160.441))]
data['smoc'] = [('A', 125, 'ALA', 0.526977935036654, (166.093994140625, 143.99200439453125, 127.9280014038086)), ('A', 133, 'HIS', 0.5222966459680073, (159.7259979248047, 138.0489959716797, 134.9810028076172)), ('A', 141, 'THR', 0.5266101022013526, (170.20799255371094, 136.28599548339844, 134.64300537109375)), ('A', 157, 'PHE', 0.5851754364995021, (173.00999450683594, 134.64599609375, 146.98300170898438)), ('A', 161, 'ASP', 0.5275899819875574, (165.4510040283203, 134.3179931640625, 150.79800415039062)), ('A', 171, 'ILE', 0.35190383600350744, (168.20399475097656, 143.6750030517578, 148.59800720214844)), ('A', 185, 'SER', 0.3745245772809246, (171.25399780273438, 154.42100524902344, 129.94700622558594)), ('A', 205, 'LEU', 0.4602381442778484, (164.00799560546875, 152.09800720214844, 120.12999725341797)), ('A', 222, 'PHE', 0.3634093337283652, (165.1719970703125, 152.76100158691406, 111.13300323486328)), ('A', 235, 'ASP', 0.3736425821001216, (156.75799560546875, 154.06399536132812, 123.88800048828125)), ('A', 240, 'LEU', 0.34880884452101596, (159.49899291992188, 148.47799682617188, 129.61399841308594)), ('A', 250, 'ALA', 0.37038923246604777, (167.6840057373047, 155.59800720214844, 138.81100463867188)), ('A', 257, 'MET', 0.5314621633680554, (174.3419952392578, 169.4429931640625, 143.36900329589844)), ('A', 259, 'ALA', 0.38703359972433143, (173.45599365234375, 165.28500366210938, 139.63999938964844)), ('A', 261, 'LEU', 0.4082926856545634, (176.79800415039062, 160.927001953125, 143.5469970703125)), ('A', 274, 'ASP', 0.5002366458469567, (156.29200744628906, 173.48699951171875, 144.19700622558594)), ('A', 279, 'ARG', 0.6092783300873404, (160.06500244140625, 167.89100646972656, 137.56300354003906)), ('A', 286, 'TYR', 0.410307758282659, (165.4429931640625, 161.58999633789062, 130.91099548339844)), ('A', 287, 'PHE', 0.47663084398702, (162.1020050048828, 161.31900024414062, 129.0050048828125)), ('A', 291, 'ASP', 0.5101821580518369, (155.85899353027344, 162.3470001220703, 123.22200012207031)), ('A', 298, 'CYS', 0.43670381540143005, (147.73599243164062, 166.51199340820312, 137.8300018310547)), ('A', 312, 'ASN', 0.366696038871036, (153.62100219726562, 157.75100708007812, 137.20700073242188)), ('A', 325, 'SER', 0.45387820339913826, (158.46600341796875, 169.5970001220703, 150.97300720214844)), ('A', 340, 'PHE', 0.4976294818810063, (145.57699584960938, 180.68800354003906, 162.23500061035156)), ('A', 346, 'TYR', 0.4649472824465851, (148.5229949951172, 170.03799438476562, 149.5290069580078)), ('A', 350, 'GLU', 0.36383837121889634, (152.03700256347656, 161.5489959716797, 142.91700744628906)), ('A', 351, 'LEU', 0.3253108669167447, (149.67999267578125, 164.42599487304688, 142.0679931640625)), ('A', 383, 'ALA', 0.19480156272749524, (152.58200073242188, 174.13699340820312, 163.88600158691406)), ('A', 395, 'CYS', 0.4209668123502697, (159.30799865722656, 156.8489990234375, 159.26699829101562)), ('A', 396, 'PHE', 0.22571991717702802, (159.0850067138672, 160.61500549316406, 158.8560028076172)), ('A', 401, 'LEU', 0.3549382608200627, (151.28399658203125, 167.20199584960938, 170.3780059814453)), ('A', 463, 'MET', 0.3399076304928484, (156.73199462890625, 153.4010009765625, 138.98300170898438)), ('A', 465, 'ASP', 0.45811340384387783, (154.63900756835938, 150.39300537109375, 133.00399780273438)), ('A', 482, 'CYS', 0.591841457709241, (127.61699676513672, 145.30999755859375, 135.68899536132812)), ('A', 493, 'VAL', 0.5541297710802233, (123.56999969482422, 157.98899841308594, 152.95700073242188)), ('A', 501, 'SER', 0.47704754870488764, (135.2270050048828, 156.62899780273438, 166.76300048828125)), ('A', 513, 'ARG', 0.5236424595875135, (126.74400329589844, 159.51800537109375, 165.9340057373047)), ('A', 535, 'VAL', 0.38381798616881835, (141.47300720214844, 169.41299438476562, 149.76800537109375)), ('A', 538, 'THR', 0.2615796313822382, (142.6300048828125, 164.9949951171875, 157.81500244140625)), ('A', 542, 'MET', 0.4268248325844542, (146.88499450683594, 154.23800659179688, 164.88400268554688)), ('A', 560, 'VAL', 0.1692185742661522, (139.7729949951172, 157.572998046875, 159.1959991455078)), ('A', 607, 'SER', 0.561625473355289, (131.3979949951172, 128.2519989013672, 134.83200073242188)), ('A', 617, 'TRP', 0.4850706314705071, (147.2899932861328, 132.98399353027344, 146.427001953125)), ('A', 622, 'CYS', 0.17666085469143997, (148.64500427246094, 143.8419952392578, 151.10800170898438)), ('A', 646, 'CYS', 0.6786309710445662, (130.6439971923828, 165.40899658203125, 138.28500366210938)), ('A', 673, 'LEU', 0.36819447352172857, (151.7530059814453, 163.1020050048828, 164.43099975585938)), ('A', 678, 'GLY', 0.013279060716704216, (151.08799743652344, 154.81300354003906, 151.5)), ('A', 679, 'GLY', 0.07273663383896749, (149.17799377441406, 151.4969940185547, 151.74899291992188)), ('A', 727, 'LEU', 0.504423341013987, (147.375, 142.76600646972656, 122.447998046875)), ('A', 740, 'GLU', 0.5779838171959356, (136.4409942626953, 146.3769989013672, 120.5999984741211)), ('A', 756, 'MET', 0.3872441471498059, (135.91600036621094, 135.01499938964844, 142.07200622558594)), ('A', 764, 'VAL', 0.4539262766823213, (140.6020050048828, 131.3159942626953, 139.9029998779297)), ('A', 777, 'ALA', 0.38140250471131093, (148.302001953125, 133.2449951171875, 133.68299865722656)), ('A', 782, 'PHE', 0.4016318386042068, (151.33999633789062, 136.15899658203125, 139.89599609375)), ('A', 785, 'VAL', 0.3327739608685112, (153.89300537109375, 140.38600158691406, 138.94000244140625)), ('A', 789, 'GLN', 0.30734420083681663, (154.2429962158203, 145.6179962158203, 141.125)), ('A', 817, 'THR', 0.3491191601470198, (135.6219940185547, 123.552001953125, 150.89599609375)), ('A', 818, 'MET', 0.309974286479876, (134.1739959716797, 120.05000305175781, 150.55499267578125)), ('A', 819, 'LEU', 0.5036129660923514, (131.51600646972656, 118.41400146484375, 148.36399841308594)), ('A', 824, 'ASP', 0.5714406325484587, (119.78099822998047, 113.40599822998047, 147.25399780273438)), ('A', 832, 'PRO', 0.3808851979818312, (136.80099487304688, 126.81400299072266, 159.0570068359375)), ('A', 834, 'PRO', 0.2344540491620286, (138.33599853515625, 123.00599670410156, 163.79200744628906)), ('A', 859, 'PHE', 0.4171764837627322, (128.57899475097656, 131.0959930419922, 170.67999267578125)), ('A', 871, 'LYS', 0.5448443958487776, (129.35400390625, 116.45099639892578, 157.38400268554688)), ('A', 878, 'ALA', 0.532635337185709, (132.10699462890625, 116.94100189208984, 164.09500122070312)), ('A', 885, 'LEU', 0.11890760575044691, (125.75299835205078, 123.02100372314453, 171.3730010986328)), ('A', 910, 'ASN', 0.500099767029945, (120.48400115966797, 120.57499694824219, 164.9459991455078)), ('A', 916, 'TYR', 0.5042372720504311, (121.46800231933594, 127.58100128173828, 157.29200744628906)), ('B', 95, 'LEU', 0.3898899709019068, (146.24200439453125, 179.69500732421875, 168.79400634765625)), ('B', 103, 'LEU', 0.0968106132033089, (155.50999450683594, 181.83099365234375, 162.927001953125)), ('B', 111, 'ARG', 0.5399430196134068, (157.6719970703125, 183.7790069580078, 148.40499877929688)), ('B', 118, 'ASN', 0.3270830683312649, (156.10299682617188, 169.906005859375, 157.78799438476562)), ('B', 124, 'THR', 0.23069678548772757, (158.0970001220703, 177.51100158691406, 165.79200744628906)), ('B', 129, 'MET', 0.3261468631262719, (161.17799377441406, 165.84100341796875, 172.30099487304688)), ('B', 133, 'PRO', 0.4132533918000914, (165.70599365234375, 153.3679962158203, 172.1020050048828)), ('B', 156, 'ILE', 0.28894024524070927, (168.5850067138672, 169.52200317382812, 177.63800048828125)), ('B', 160, 'VAL', 0.25395526437038474, (162.3939971923828, 160.89700317382812, 181.63400268554688)), ('B', 169, 'LEU', 0.3087892564025393, (172.42300415039062, 162.98699951171875, 182.41299438476562)), ('B', 174, 'MET', 0.32863747052894293, (177.51100158691406, 152.2729949951172, 179.40499877929688)), ('B', 175, 'ASP', 0.4347490625070568, (177.80999755859375, 150.81700134277344, 182.9199981689453)), ('B', 179, 'ASN', 0.5517974294820841, (169.47799682617188, 149.79100036621094, 184.62899780273438)), ('B', 180, 'LEU', 0.6012426629841912, (167.7570037841797, 152.3260040283203, 182.38699340820312))]
data['rota'] = [('A', ' 483 ', 'TYR', 0.009501776017991952, (126.91000000000005, 147.30600000000004, 138.859))]
data['clusters'] = [('A', '477', 1, 'Bond angle:CA:CB:CG', (136.806, 148.638, 134.123)), ('A', '480', 1, 'side-chain clash', (132.318, 145.64, 138.531)), ('A', '481', 1, 'cablam Outlier', (130.6, 147.0, 134.0)), ('A', '482', 1, 'smoc Outlier', (127.61699676513672, 145.30999755859375, 135.68899536132812)), ('A', '483', 1, 'side-chain clash\nRotamer', (126.91000000000005, 147.30600000000004, 138.859)), ('A', '257', 2, 'smoc Outlier', (174.3419952392578, 169.4429931640625, 143.36900329589844)), ('A', '258', 2, 'side-chain clash', (176.282, 168.361, 141.268)), ('A', '259', 2, 'smoc Outlier', (173.45599365234375, 165.28500366210938, 139.63999938964844)), ('A', '261', 2, 'smoc Outlier', (176.79800415039062, 160.927001953125, 143.5469970703125)), ('A', '295', 3, 'Bond angle:CA:CB:CG', (151.242, 167.758, 133.515)), ('A', '298', 3, 'smoc Outlier', (147.73599243164062, 166.51199340820312, 137.8300018310547)), ('A', '350', 3, 'smoc Outlier', (152.03700256347656, 161.5489959716797, 142.91700744628906)), ('A', '351', 3, 'smoc Outlier', (149.67999267578125, 164.42599487304688, 142.0679931640625)), ('A', '393', 4, 'backbone clash', (160.874, 154.725, 161.647)), ('A', '394', 4, 'backbone clash', (160.874, 154.725, 161.647)), ('A', '395', 4, 'smoc Outlier', (159.30799865722656, 156.8489990234375, 159.26699829101562)), ('A', '396', 4, 'smoc Outlier', (159.0850067138672, 160.61500549316406, 158.8560028076172)), ('A', '487', 5, 'side-chain clash', (129.683, 160.598, 142.318)), ('A', '571', 5, 'side-chain clash', (133.473, 160.242, 141.78)), ('A', '642', 5, 'side-chain clash', (129.683, 160.598, 142.318)), ('A', '646', 5, 'smoc Outlier', (130.6439971923828, 165.40899658203125, 138.28500366210938)), ('A', '817', 6, 'smoc Outlier', (135.6219940185547, 123.552001953125, 150.89599609375)), ('A', '818', 6, 'smoc Outlier', (134.1739959716797, 120.05000305175781, 150.55499267578125)), ('A', '819', 6, 'smoc Outlier', (131.51600646972656, 118.41400146484375, 148.36399841308594)), ('A', '401', 7, 'smoc Outlier', (151.28399658203125, 167.20199584960938, 170.3780059814453)), ('A', '402', 7, 'backbone clash', (152.907, 166.108, 175.856)), ('A', '403', 7, 'backbone clash', (152.907, 166.108, 175.856)), ('A', '677', 8, 'cablam Outlier', (154.0, 156.8, 153.2)), ('A', '678', 8, 'cablam CA Geom Outlier\nsmoc Outlier', (151.1, 154.8, 151.5)), ('A', '679', 8, 'smoc Outlier', (149.17799377441406, 151.4969940185547, 151.74899291992188)), ('A', '740', 9, 'smoc Outlier', (136.4409942626953, 146.3769989013672, 120.5999984741211)), ('A', '741', 9, 'Bond angle:CA:CB:CG', (139.81, 144.83, 121.36999999999999)), ('A', '743', 9, 'Bond angle:CA:CB:CG', (135.87, 143.70899999999997, 124.955)), ('A', '274', 10, 'cablam Outlier\nsmoc Outlier', (156.3, 173.5, 144.2)), ('A', '275', 10, 'cablam Outlier', (159.1, 171.7, 142.3)), ('A', '279', 10, 'smoc Outlier', (160.06500244140625, 167.89100646972656, 137.56300354003906)), ('A', '782', 11, 'smoc Outlier', (151.33999633789062, 136.15899658203125, 139.89599609375)), ('A', '785', 11, 'smoc Outlier', (153.89300537109375, 140.38600158691406, 138.94000244140625)), ('A', '789', 11, 'smoc Outlier', (154.2429962158203, 145.6179962158203, 141.125)), ('A', '756', 12, 'smoc Outlier', (135.91600036621094, 135.01499938964844, 142.07200622558594)), ('A', '764', 12, 'smoc Outlier', (140.6020050048828, 131.3159942626953, 139.9029998779297)), ('A', '286', 13, 'smoc Outlier', (165.4429931640625, 161.58999633789062, 130.91099548339844)), ('A', '287', 13, 'smoc Outlier', (162.1020050048828, 161.31900024414062, 129.0050048828125)), ('A', '824', 14, 'cablam Outlier\nBond angle:C\nsmoc Outlier', (119.8, 113.4, 147.3)), ('A', '825', 14, 'Bond angle:N:CA', (122.038, 115.74700000000001, 145.32700000000003)), ('A', '593', 15, 'side-chain clash', (128.095, 131.61, 157.252)), ('A', '594', 15, 'side-chain clash', (128.095, 131.61, 157.252)), ('A', '194', 16, 'Bond angle:CA:CB:CG', (168.684, 163.789, 119.41400000000002)), ('A', '198', 16, 'Bond angle:CA:CB:CG', (169.134, 165.641, 113.518)), ('A', '832', 17, 'smoc Outlier', (136.80099487304688, 126.81400299072266, 159.0570068359375)), ('A', '834', 17, 'smoc Outlier', (138.33599853515625, 123.00599670410156, 163.79200744628906)), ('A', '312', 18, 'smoc Outlier', (153.62100219726562, 157.75100708007812, 137.20700073242188)), ('A', '463', 18, 'smoc Outlier', (156.73199462890625, 153.4010009765625, 138.98300170898438)), ('A', '240', 19, 'smoc Outlier', (159.49899291992188, 148.47799682617188, 129.61399841308594)), ('A', '465', 19, 'smoc Outlier', (154.63900756835938, 150.39300537109375, 133.00399780273438)), ('A', '161', 20, 'smoc Outlier', (165.4510040283203, 134.3179931640625, 150.79800415039062)), ('A', '167', 20, 'cablam Outlier', (163.1, 139.6, 154.7)), ('A', '607', 21, 'cablam Outlier\nsmoc Outlier', (131.4, 128.3, 134.8)), ('A', '608', 21, 'cablam Outlier', (132.1, 126.5, 131.6)), ('A', '325', 22, 'smoc Outlier', (158.46600341796875, 169.5970001220703, 150.97300720214844)), ('A', '326', 22, 'cablam CA Geom Outlier', (155.5, 167.3, 150.6)), ('B', '103', 1, 'smoc Outlier', (155.50999450683594, 181.83099365234375, 162.927001953125)), ('B', '118', 1, 'smoc Outlier', (156.10299682617188, 169.906005859375, 157.78799438476562)), ('B', '120', 1, 'side-chain clash', (156.764, 173.244, 160.441)), ('B', '121', 1, 'side-chain clash', (156.764, 173.244, 160.441)), ('B', '124', 1, 'smoc Outlier', (158.0970001220703, 177.51100158691406, 165.79200744628906)), ('B', '92', 1, 'Bond angle:CA:CB:CG', (141.95700000000002, 178.82200000000003, 170.68)), ('B', '95', 1, 'smoc Outlier', (146.24200439453125, 179.69500732421875, 168.79400634765625)), ('B', '99', 1, 'cablam Outlier', (150.7, 182.9, 167.5)), ('B', '174', 2, 'smoc Outlier', (177.51100158691406, 152.2729949951172, 179.40499877929688)), ('B', '175', 2, 'smoc Outlier', (177.80999755859375, 150.81700134277344, 182.9199981689453)), ('B', '177', 2, 'side-chain clash', (173.794, 149.784, 181.726)), ('B', '178', 2, 'side-chain clash', (173.794, 149.784, 181.726)), ('B', '179', 2, 'smoc Outlier', (169.47799682617188, 149.79100036621094, 184.62899780273438)), ('B', '180', 2, 'smoc Outlier', (167.7570037841797, 152.3260040283203, 182.38699340820312)), ('B', '111', 3, 'smoc Outlier', (157.6719970703125, 183.7790069580078, 148.40499877929688)), ('B', '112', 3, 'side-chain clash\nBond angle:CA:CB:CG', (153.88100000000003, 184.164, 148.445))]
data['omega'] = [('A', ' 505 ', 'PRO', None, (140.68499999999995, 165.00300000000001, 166.117)), ('B', ' 183 ', 'PRO', None, (163.055, 152.92100000000002, 176.0))]
data['cablam'] = [('A', '167', 'GLU', ' alpha helix', 'bend\nSSSST', (163.1, 139.6, 154.7)), ('A', '226', 'ALA', 'check CA trace,carbonyls, peptide', ' \nE--TT', (165.1, 164.1, 105.7)), ('A', '274', 'ASP', 'check CA trace,carbonyls, peptide', ' \n----H', (156.3, 173.5, 144.2)), ('A', '275', 'PHE', 'check CA trace,carbonyls, peptide', ' \n---HH', (159.1, 171.7, 142.3)), ('A', '481', 'ASP', ' alpha helix', ' \nTT-SS', (130.6, 147.0, 134.0)), ('A', '504', 'PHE', 'check CA trace,carbonyls, peptide', 'turn\n--TTG', (141.3, 162.6, 166.2)), ('A', '509', 'TRP', 'check CA trace,carbonyls, peptide', 'turn\nGGT-B', (134.5, 164.6, 172.1)), ('A', '607', 'SER', 'check CA trace,carbonyls, peptide', 'turn\nHHTT-', (131.4, 128.3, 134.8)), ('A', '608', 'ASP', 'check CA trace,carbonyls, peptide', 'turn\nHTT-S', (132.1, 126.5, 131.6)), ('A', '677', 'PRO', 'check CA trace,carbonyls, peptide', ' \nE--S-', (154.0, 156.8, 153.2)), ('A', '824', 'ASP', 'check CA trace,carbonyls, peptide', 'bend\n-SSSE', (119.8, 113.4, 147.3)), ('A', '151', 'CYS', 'check CA trace', 'bend\nTTSS-', (176.1, 145.4, 143.2)), ('A', '326', 'PHE', 'check CA trace', 'bend\nTSSEE', (155.5, 167.3, 150.6)), ('A', '678', 'GLY', 'check CA trace', 'bend\n--S--', (151.1, 154.8, 151.5)), ('A', '733', 'ARG', 'check CA trace', 'bend\nTSS--', (150.9, 151.3, 119.8)), ('B', '99', 'ASP', 'check CA trace,carbonyls, peptide', ' \nHH-SH', (150.7, 182.9, 167.5))]
handle_read_draw_probe_dots_unformatted("/home/ccpem/agnel/gisaid/countries_seq/structure_data/emdb/EMD-0521/6nus/Model_validation_1/validation_cootdata/molprobity_probe6nus_0.txt", 0, 0)
show_probe_dots(True, True)
gui = coot_molprobity_todo_list_gui(data=data)

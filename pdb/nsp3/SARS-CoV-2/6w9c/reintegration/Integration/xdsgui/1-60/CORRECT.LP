
 ***** CORRECT ***** (VERSION Jan 31, 2020  BUILT=20200417)  12-May-2020

 INPUT PARAMETER VALUES
 ----------------------
 SPACE_GROUP_NUMBER=    5 as used in the INTEGRATE step
 UNIT_CELL_CONSTANTS=   190.814   110.204    64.234  90.000  96.141  90.000 as used by INTEGRATE
 FRIEDEL'S_LAW=TRUE 
 PROFILE_FITTING= TRUE 
 OVERLOAD=   1267439     MINPK=  75.00000    WFAC1=   1.0
 INCLUDE_RESOLUTION_RANGE=    50.000     2.500
 NAME_TEMPLATE_OF_DATA_FRAMES=/home/dale/Structures/sars-2/nsp3/6w9c/images/IDP51000_6w9c/data/y3_b07_?????.cbf CBF
 DATA_RANGE=       1      50
 ROTATION_AXIS= -0.999990 -0.000850  0.004511
 OSCILLATION_RANGE=  0.500000
 STARTING_ANGLE=   -90.000     STARTING_FRAME=       1
 X-RAY_WAVELENGTH=  0.979180
 INCIDENT_BEAM_DIRECTION=  0.000922 -0.001585  0.999998
 FRACTION_OF_POLARIZATION=   0.980
 POLARIZATION_PLANE_NORMAL=  0.000000  1.000000  0.000000
 AIR=   0.00032
 DETECTOR=PILATUS
 SILICON=  3.703301 SENSOR_THICKNESS=  1.000000
 NUMBER OF DETECTOR SEGMENTS   1
 NX=  2463  NY=  2527    QX=  0.172000  QY=  0.172000
 ORGX=   1243.98  ORGY=   1266.74
 DETECTOR_DISTANCE=   517.623
 DIRECTION_OF_DETECTOR_X-AXIS=   1.00000   0.00000   0.00000
 DIRECTION_OF_DETECTOR_Y-AXIS=   0.00000   1.00000   0.00000
 BEAM_DIVERGENCE_E.S.D.=   0.015
 REFLECTING_RANGE_E.S.D.=   0.119
 MINIMUM_ZETA=     0.050
 MAXIMUM_ERROR_OF_SPOT_POSITION=   3.0
 MAXIMUM_ERROR_OF_SPINDLE_POSITION=   2.0
 MINIMUM_I/SIGMA=   3.0
 REFLECTIONS/CORRECTION_FACTOR=      50
 SNRC= 50.00 I/sigma for use in scaling factor determination
 STRICT_ABSORPTION_CORRECTION=FALSE 
 CORRECTIONS= DECAY MODULATION ABSORPTION                      
 REFERENCE_DATA_SET=../2-140/XDS_ASCII.HKL                            
 FIT_B-FACTOR_TO_REFERENCE_DATA_SET=FALSE 

   21982 REFLECTIONS ON FILE "INTEGRATE.HKL"
       0 CORRUPTED REFLECTION RECORDS (IGNORED)
       0 MATCHING REFLECTIONS SPECIFIED IN FILE "FILTER.HKL"
       0 REFLECTIONS INCOMPLETE OR OUTSIDE IMAGE RANGE       1 ...      50
       0 OVERLOADED REFLECTIONS (IGNORED)
       1 REFLECTIONS OUTSIDE ACCEPTED RESOLUTION RANGES
                OR TOO CLOSE TO ROTATION AXIS (IGNORED)
   21981 REFLECTIONS ACCEPTED


   43454 REFLECTIONS ACCEPTED FROM REFERENCE DATA SET
         TYPE OF FILE=XDS_ASCII 



 ******************************************************************************
                      AUTOMATIC SPACE GROUP ASSIGNMENT
 ******************************************************************************

 XDS adopts the following approach.
 (1) it looks for possible symmetries of the crystal lattice
 (2) it computes a redundancy independent R-factor for all enantiomorphous
     point groups compatible with the observed lattice symmetry.
 (3) it selects the group which explains the intensity data at an acceptable,
     redundancy-independent R-factor (Rmeas, Rrim) using a minimum number of
     unique reflections.

 This approach does not test for the presence of screw axes. Consequently,
 orthorhombic cell axes will be specified in increasing length (following
 conventions), despite the possibility that different assignments for the
 cell axes could become necessary for space groups P222(1) and P2(1)2(1)2
 containing one or two screw axes, respectively.

 The user can always override the automatic decisions by specifying the
 correct space group number and unit cell constants in XDS.INP and repeating
 the CORRECT step of XDS. This provides a simple way to rename orthorhombic
 cell constants if screw axes are present.

 In addition, the user has the option to specify in XDS.INP
 (a) a reference data set or
 (b) a reindexing transformation or
 (c) the three basis vectors (if known from processing a previous data set
 taken at the same crystal orientation in a multi-wavelength experiment).
 These features of XDS are useful for resolving the issue of alternative
 settings of polar or rhombohedral cells (like P4, P6, R3).

 =====> Specifications provided by the user in XDS.INP:
 SPACE_GROUP_NUMBER=    5 (0: unknown symmetry and unit cell)
 UNIT_CELL_CONSTANTS=   190.81   110.20    64.23  90.000  96.142  90.000
 UNIT_CELL_A-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 UNIT_CELL_B-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 UNIT_CELL_C-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 REIDX=  0  0  0  0  0  0  0  0  0  0  0  0 (all 0 : not specified)
 TEST_RESOLUTION_RANGE=   10.00    5.00 (Angstrom) for space group determination
 NUMBER OF ACCEPTED REFLECTIONS FOR CALCULATING Rmeas             2453
 NUMBER OF ACCEPTED UNIQUE REFLECTIONS FROM REFERENCE DATA SET    4862


 *********** DETERMINATION OF LATTICE CHARACTER AND BRAVAIS LATTICE ***********

 The CHARACTER OF A LATTICE is defined by the metrical parameters of its
 reduced cell as described in the INTERNATIONAL TABLES FOR CRYSTALLOGRAPHY
 Volume A, p. 746 (KLUWER ACADEMIC PUBLISHERS, DORDRECHT/BOSTON/LONDON, 1989).
 Note that more than one lattice character may have the same BRAVAIS LATTICE.

 A lattice character is marked "*" to indicate a lattice consistent with the
 observed locations of the diffraction spots. These marked lattices must have
 low values for the QUALITY OF FIT and their implicated UNIT CELL CONSTANTS
 should not violate the ideal values by more than
 MAX_CELL_AXIS_ERROR=  0.03
 MAX_CELL_ANGLE_ERROR=           2.0 (Degrees)

 The REINDEXING TRANSFORMATION REIDX() consists of 12 integers that relate
 the original indices H,K,L from file INTEGRATE.HKL to the indices H',K',L'
 with respect to the new cell.
    H'=(REIDX(1)*H+REIDX( 2)*K+REIDX( 3)*L)/IDXV+REIDX( 4)
    K'=(REIDX(5)*H+REIDX( 6)*K+REIDX( 7)*L)/IDXV+REIDX( 8)
    L'=(REIDX(9)*H+REIDX(10)*K+REIDX(11)*L)/IDXV+REIDX(12)
 The value of the integer IDXV depends on the lattice type used for
 specifying reflections on file INTEGRATE.HKL; IDXV is
 1 for a primitive,
 2 for a face or body centred,
 3 for a rhombohedral,
 4 for a lattice centred on all faces.
 IDXV is set by XDS and cannot be input by the user.

  LATTICE-  BRAVAIS-   QUALITY  UNIT CELL CONSTANTS (ANGSTROEM & DEGREES)    REINDEXING TRANSFORMATION
 CHARACTER  LATTICE     OF FIT      a      b      c   alpha  beta gamma

 *  31        aP          0.0      64.2  110.2  110.2  60.0  84.7  84.7    0  0 -2  0  1  1  0  0  1 -1  0  0
 *  20        mC          0.0     190.8  110.2   64.2  90.0  96.1  90.0    2  0  0  0  0  2  0  0  0  0  2  0
 *  44        aP          0.8      64.2  110.2  110.2 120.0  90.0  95.3    0  0 -2  0 -1 -1  0  0  0  2  0  0
 *  41        mC          0.8     190.8  110.2   64.2  90.0  96.1  90.0   -2  0  0  0  0  2  0  0  0  0 -2  0
    30        mC         40.2     110.2  190.9   64.2  86.9  95.3  90.0    1  1  0  0 -1  3  0  0  0  0  2  0
    35        mP         80.3     110.2   64.2  110.2  90.0 120.0  95.3    1  1  0  0  0  0  2  0  0 -2  0  0
    40        oC         80.3     110.2  190.8   64.2  83.9  90.0  90.0    0  2  0  0  2  0  0  0  0  0 -2  0
    25        mC         81.2     110.2  190.9   64.2  93.1  95.3  90.0   -1 -1  0  0 -1  3  0  0  0  0 -2  0
    23        oC         81.2     110.2  190.9   64.2  86.9  95.3  90.0   -1  1  0  0  1  3  0  0  0  0 -2  0
    22        hP         81.2     110.2  110.2   64.2  95.3  90.0 120.0    0 -2  0  0 -1  1  0  0  0  0 -2  0
    39        mC        171.4     223.7   64.2  110.2  90.0 119.5  78.7    2  2  2  0  0  0  2  0  0 -2  0  0
    37        mC        171.4     223.7   64.2  110.2  90.0 119.5  78.7    2  2  2  0  0  0  2  0  0 -2  0  0
    42        oI        171.4      64.2  110.2  194.7  90.0 103.0  90.0    0  0 -2  0  0  2  0  0  2  0  2  0
    27        mC        341.1     223.7   64.2  110.2  90.0 119.5  78.7    2  2  2  0  0  0  2  0  0 -2  0  0
    19        oI        341.1      64.2  110.2  194.7  90.0  77.0  90.0    0  0  2  0  0 -2  0  0  2  0  2  0
    24        hR        509.4     198.1  190.9   64.2  93.1  74.2 120.0   -1 -3 -2  0 -1  3  0  0  0  0 -2  0
    43        mI        683.0     127.6  194.7  110.2  90.0 149.8  83.5    0 -2 -2  0 -2  0 -2  0  0  2  0  0
    34        mP        736.9      64.2  110.2  110.2 120.0  95.3  90.0    0  0  2  0  0 -2  0  0  1  1  0  0
    33        mP        736.9      64.2  110.2  110.2 120.0  95.3  90.0    0  0  2  0  0 -2  0  0  1  1  0  0
    32        oP        816.4      64.2  110.2  110.2 120.0  90.0  95.3    0  0 -2  0 -1 -1  0  0  0  2  0  0
    21        tP        817.2     110.2  110.2   64.2  90.0  95.3 120.0   -1 -1  0  0  0  2  0  0  0  0 -2  0
    28        mC        866.0      64.2  223.7  110.2  62.3  95.3  78.7    0  0  2  0  2 -2  2  0  1  1  0  0
    29        mC        866.0      64.2  223.7  110.2  62.3  95.3  78.7    0  0 -2  0 -2 -2 -2  0 -1  1  0  0
    38        oC        907.4      64.2  223.7  110.2  60.5  90.0 101.3    0  0  2  0 -2 -2 -2  0  0 -2  0  0
    36        oC        907.4      64.2  223.7  110.2  60.5  90.0 101.3    0  0  2  0 -2 -2 -2  0  0 -2  0  0
    26        oF        951.3      64.2  223.7  223.7  59.0 101.3 101.3    0  0 -2  0  2  2  2  0  2 -2  2  0
    18        tI        951.3     110.2  194.7   64.2  77.0  90.0  90.0    0 -2  0  0 -2  0 -2  0  0  0 -2  0
     1        cF        999.0     127.6  127.6  194.7  96.5  96.5 119.5    0 -2 -2  0  0  2 -2  0  2  0  2  0
     2        hR        999.0     122.3  122.3  207.7 121.9  58.1 126.4   -1 -1 -2  0  1 -1  2  0 -2  0  2  0
     3        cP        999.0      64.2  110.2  110.2 120.0  95.3  90.0    0  0  2  0  0 -2  0  0  1  1  0  0
     5        cI        999.0     122.3  127.6  110.2  67.3  66.3  99.6    1  1  2  0  0 -2  2  0  1 -1  0  0
     4        hR        999.0     127.6  132.6  122.3  96.9  80.4  85.6    0  2 -2  0 -1  1  2  0  1  1  2  0
     6        tI        999.0     110.2  122.3  127.6  99.6  67.3  66.3   -1 -1  0  0 -1  1 -2  0  0 -2 -2  0
     7        tI        999.0     122.3  127.6  110.2  67.3  66.3  99.6   -1  1 -2  0  0 -2 -2  0 -1 -1  0  0
     8        oI        999.0     127.6  122.3  110.2  66.3  67.3  99.6    0  2  2  0  1 -1  2  0  1  1  0  0
     9        hR        999.0      64.2  122.3  294.1  76.8  98.6 116.2    0  0 -2  0  1  1  2  0  2 -4  2  0
    10        mC        999.0     132.6  122.3  110.2  66.3 117.4 119.6    1  1 -2  0 -1 -1 -2  0 -1  1  0  0
    11        tP        999.0      64.2  110.2  110.2 120.0  90.0  95.3    0  0 -2  0 -1 -1  0  0  0  2  0  0
    12        hP        999.0      64.2  110.2  110.2 120.0  90.0  95.3    0  0 -2  0 -1 -1  0  0  0  2  0  0
    13        oC        999.0     122.3  132.6  110.2 114.6 116.8  60.4   -1 -1 -2  0 -1 -1  2  0  0  2  0  0
    15        tI        999.0      64.2  110.2  194.7  90.0  77.0  90.0    0  0  2  0  0 -2  0  0  2  0  2  0
    16        oF        999.0     127.6  127.6  194.7  83.5  96.5  60.5    0  2  2  0  0  2 -2  0 -2  0 -2  0
    14        mC        999.0     127.6  127.6  110.2 112.7 118.6  60.5    0 -2  2  0  0 -2 -2  0  1  1  0  0
    17        mC        999.0     127.6  127.6  122.3  99.6 127.7  60.5    0  2 -2  0  0  2  2  0  1 -1  2  0

 ****** LATTICE SYMMETRY IMPLICATED BY SPACE GROUP SYMMETRY ******

BRAVAIS-            POSSIBLE SPACE-GROUPS FOR PROTEIN CRYSTALS
  TYPE                     [SPACE GROUP NUMBER,SYMBOL]
  aP      [1,P1]
  mP      [3,P2] [4,P2(1)]
 mC,mI    [5,C2]
  oP      [16,P222] [17,P222(1)] [18,P2(1)2(1)2] [19,P2(1)2(1)2(1)]
  oC      [21,C222] [20,C222(1)]
  oF      [22,F222]
  oI      [23,I222] [24,I2(1)2(1)2(1)]
  tP      [75,P4] [76,P4(1)] [77,P4(2)] [78,P4(3)] [89,P422] [90,P42(1)2]
          [91,P4(1)22] [92,P4(1)2(1)2] [93,P4(2)22] [94,P4(2)2(1)2]
          [95,P4(3)22] [96,P4(3)2(1)2]
  tI      [79,I4] [80,I4(1)] [97,I422] [98,I4(1)22]
  hP      [143,P3] [144,P3(1)] [145,P3(2)] [149,P312] [150,P321] [151,P3(1)12]
          [152,P3(1)21] [153,P3(2)12] [154,P3(2)21] [168,P6] [169,P6(1)]
          [170,P6(5)] [171,P6(2)] [172,P6(4)] [173,P6(3)] [177,P622]
          [178,P6(1)22] [179,P6(5)22] [180,P6(2)22] [181,P6(4)22] [182,P6(3)22]
  hR      [146,R3] [155,R32]
  cP      [195,P23] [198,P2(1)3] [207,P432] [208,P4(2)32] [212,P4(3)32]
          [213,P4(1)32]
  cF      [196,F23] [209,F432] [210,F4(1)32]
  cI      [197,I23] [199,I2(1)3] [211,I432] [214,I4(1)32]


 Several solutions exist for the given space group that explain the data. The
 selected solution (marked "*") correlates best with the given reference data set.
 The independent settings of the cell can be obtained by application of the
 REINDEXING TRANSFORMATION to the original indices H,K,L from file INTEGRATE.HKL

 CORRELATION = correlation factor with the reference data set
 NPAIR       = number of unique reflection pairs correlated 
 Rmeas=Rrim  = redundancy independent R-factor (intensities)
               For definition see:
               Rmeas : Diederichs & Karplus,
                       Nature Struct. Biol. 4, 269-275 (1997);
               Rrim  : Weiss & Hilgenfeld,
                       J.Appl.Cryst. 30,203-205 (1997).
 COMPARED    = number of reflections used for calculating Rmeas
 ESD         = Agreement with given unit cell geometry

 CORRELATION  NPAIR  Rmeas  COMPARED  ESD       REINDEX TRANSFORMATION

  *   0.95     1750   27.7     675    0.00  2  0  0  0  0  2  0  0  0  0  2  0

 ************ SELECTED SPACE GROUP AND UNIT CELL FOR THIS DATA SET ************

 SPACE_GROUP_NUMBER=    5
 UNIT_CELL_CONSTANTS=   190.81   110.20    64.23  90.000  96.142  90.000
 UNIT_CELL_A-AXIS=   162.988     5.358   -99.077
 UNIT_CELL_B-AXIS=    49.339    51.602    83.957
 UNIT_CELL_C-AXIS=    11.021   -56.592    28.306
 REFLECTIONS H,K,L FROM "INTEGRATE.HKL" WILL BE REINDEXED BY
 H' = (  2*H +  0*K +  0*L)/ 2 +  0
 K' = (  0*H +  2*K +  0*L)/ 2 +  0
 L' = (  0*H +  0*K +  2*L)/ 2 +  0

 *****  4 EQUIVALENT POSITIONS IN SPACE GROUP #  5 *****

    If x',y',z' is an equivalent position to x,y,z, then
        x'=x*ML(1)+y*ML( 2)+z*ML( 3)+ML( 4)/12.0
        y'=x*ML(5)+y*ML( 6)+z*ML( 7)+ML( 8)/12.0
        z'=x*ML(9)+y*ML(10)+z*ML(11)+ML(12)/12.0

    #    1  2  3  4    5  6  7  8    9 10 11 12 
    1    1  0  0  0    0  1  0  0    0  0  1  0
    2   -1  0  0  0    0  1  0  0    0  0 -1  0
    3    1  0  0  6    0  1  0  6    0  0  1  0
    4   -1  0  0  6    0  1  0  6    0  0 -1  0

 ******************************************************************************
      MEAN DISCREPANCIES BETWEEN OBSERVED AND CALCULATED SPOT LOCATIONS
 ******************************************************************************

 The discrepancies in X- and Y-coordinates of the spots are depicted in the
 two images DX-CORRECTIONS.cbf and DY-CORRECTIONS.cbf for inspection with
 the XDS-Viewer.



 ******************************************************************************
  REFINEMENT OF DIFFRACTION PARAMETERS USING ALL IMAGES
 ******************************************************************************


 REFINED VALUES OF DIFFRACTION PARAMETERS DERIVED FROM      6391 INDEXED SPOTS
 REFINED PARAMETERS:   POSITION BEAM AXIS ORIENTATION CELL
 STANDARD DEVIATION OF SPOT    POSITION (PIXELS)     0.51
 STANDARD DEVIATION OF SPINDLE POSITION (DEGREES)    0.07
 SPACE GROUP NUMBER      5
 UNIT CELL PARAMETERS    190.836   110.227    64.226  90.000  96.145  90.000
 E.S.D. OF CELL PARAMETERS  2.7E-01 1.8E-01 1.2E-01 0.0E+00 4.0E-02 0.0E+00
 REC. CELL PARAMETERS   0.005270  0.009072  0.015660  90.000  83.855  90.000
 COORDINATES OF UNIT CELL A-AXIS   163.029     5.447   -99.047
 COORDINATES OF UNIT CELL B-AXIS    49.305    51.616    83.993
 COORDINATES OF UNIT CELL C-AXIS    11.035   -56.590    28.298
 CRYSTAL MOSAICITY (DEGREES)     0.119
 LAB COORDINATES OF ROTATION AXIS -0.999988 -0.001204  0.004681
 DIRECT BEAM COORDINATES (REC. ANGSTROEM)   0.000950 -0.001569  1.021261
 DETECTOR COORDINATES (PIXELS) OF DIRECT BEAM    1246.75   1261.97
 DETECTOR ORIGIN (PIXELS) AT                     1243.95   1266.60
 CRYSTAL TO DETECTOR DISTANCE (mm)       517.71
 LAB COORDINATES OF DETECTOR X-AXIS  1.000000  0.000000  0.000000
 LAB COORDINATES OF DETECTOR Y-AXIS  0.000000  1.000000  0.000000


 THE DATA COLLECTION STATISTICS REPORTED BELOW ASSUMES:
 SPACE_GROUP_NUMBER=    5
 UNIT_CELL_CONSTANTS=   190.84   110.23    64.23  90.000  96.145  90.000


 ******************************************************************************
        MEAN INTENSITY AS FUNCTION OF SPINDLE POSITION WITHIN DATA IMAGE
 ******************************************************************************

 This statistics could serve as a diagnostic tool for detecting
 shutter problems (suggested by Kay Diederichs).
 Data are corrected for this effect if PATCH_SHUTTER_PROBLEM=TRUE in XDS.INP.
 ===> Selected : PATCH_SHUTTER_PROBLEM=FALSE

 INTERVAL = Angular interval in units of the oscillation range
            covered by a data image.
 NUMBER   = Number of reflections in each interval
 INTENSITY= Mean intensity of the reflections in each interval
 FACTOR   = Correction factor applied to intensities;
            INTENSITY(overall)/INTENSITY(interval)

   INTERVAL     NUMBER      INTENSITY      FACTOR
 -0.05  0.05      2210         47.862       1.013
  0.05  0.15      2181         51.776       0.936
  0.15  0.25      2165         47.869       1.012
  0.25  0.35      2164         50.695       0.956
  0.35  0.45      2270         46.727       1.037
  0.45  0.55      2174         47.034       1.030
  0.55  0.65      2286         50.135       0.967
  0.65  0.75      2191         46.384       1.045
  0.75  0.85      2181         48.340       1.003
  0.85  0.95      2159         47.837       1.013
 
 -0.05  0.95     21981         48.465       1.000
 
  no common reflections with data set            2


 ******************************************************************************
                OVERALL SCALING AND CRYSTAL DISORDER CORRECTION
 ******************************************************************************

      CORRELATIONS BETWEEN INPUT DATA SETS AFTER CORRECTIONS

 DATA SETS  NUMBER OF COMMON  CORRELATION   RATIO OF COMMON   B-FACTOR
  #i   #j     REFLECTIONS     BETWEEN i,j  INTENSITIES (i/j)  BETWEEN i,j



 K*EXP(B*SS) = Factor applied to intensities
    SS       = (2sin(theta)/lambda)^2

      K        B           DATA SET NAME
  1.000E+00   0.000    INTEGRATE.HKL
  1.000E+00   0.000    ../2-140/XDS_ASCII.HKL

 ******************************************************************************
    CORRECTION PARAMETERS FOR THE STANDARD ERROR OF REFLECTION INTENSITIES
 ******************************************************************************

 The variance v0(I) of the intensity I obtained from counting statistics is
 replaced by v(I)=a*(v0(I)+b*I^2). The model parameters a, b are chosen to
 minimize the discrepancies between v(I) and the variance estimated from
 sample statistics of symmetry related reflections. This model implicates
 an asymptotic limit ISa=1/SQRT(a*b) for the highest I/Sigma(I) that the
 experimental setup can produce (Diederichs (2010) Acta Cryst D66, 733-740).

     a        b          ISa
 4.000E+00  1.000E-04   50.00


 ******************************************************************************
      STANDARD ERROR OF REFLECTION INTENSITIES AS FUNCTION OF RESOLUTION
      FOR DATA SET  XDS_ASCII.HKL                                     
 ******************************************************************************

  I/Sigma  = mean intensity/Sigma of a reflection in shell
  Chi^2    = goodness of fit between sample variances of
             symmetry-related intensities and their errors
             (Chi^2 = 1 for perfect agreement)
  R-FACTOR
  observed = (SUM(ABS(I(h,i)-I(h))))/(SUM(I(h,i)))
  expected = expected R-FACTOR derived from Sigma(I)

   NUMBER  = number of reflections in resolution shell
             used for calculation of R-FACTOR
  ACCEPTED = number of accepted reflections
  REJECTED = number of rejected reflections (MISFITS),
             recognized by comparison with symmetry-related
             reflections.

 RESOLUTION RANGE  I/Sigma  Chi^2  R-FACTOR  R-FACTOR  NUMBER ACCEPTED REJECTED
                                   observed  expected

   43.663  21.725    31.26 144.48      9.65      1.49      24      30       0
   21.725  16.411    22.77  44.74     12.07      2.05      41      47       0
   16.411  13.727    20.28  71.88     12.79      2.09      53      63       0
   13.727  12.038    22.47  27.32      9.87      1.89      38      50       0
   12.038  10.850    22.15  38.03     15.06      2.23      51      70       0
   10.850   9.956    17.28  16.46     12.53      2.84      54      76       0
    9.956   9.251    16.94  38.02     20.11      2.55      58      96       0
    9.251   8.678    13.52  18.01     15.39      3.98      61      92       0
    8.678   8.200    11.82  17.36     16.33      3.99      73     111       0
    8.200   7.793    14.63  32.64     17.94      3.40      62     102       0
    7.793   7.441    10.67  11.19     17.15      4.91      62     111       0
    7.441   7.133     9.80  14.71     17.17      4.84      70     115       0
    7.133   6.860     8.67  12.16     16.75      5.17      58     111       0
    6.860   6.616     8.64  10.56     22.66      6.66      38      94       0
    6.616   6.397     8.09   6.09     17.05      6.71      71     126       0
    6.397   6.198     7.70   9.79     20.99      6.93      70     133       0
    6.198   6.017     7.58  10.36     21.00      7.20      71     131       0
    6.017   5.850     6.75   8.57     19.84      6.89      79     144       0
    5.850   5.697     6.98   7.60     24.13      8.28      90     163       0
    5.697   5.555     6.52   4.91     17.74      7.45      57     133       0
    5.555   5.423     7.07  10.06     24.04      7.50      92     173       0
    5.423   5.300     6.40  11.98     27.42      8.01      69     132       0
    5.300   5.185     6.42   4.70     19.85      7.79      98     192       0
    5.185   5.078     7.30  21.66     25.78      5.46      68     156       0
    5.078   4.977     6.94   9.46     26.45      8.05      82     181       0
    4.977   4.881     8.29  17.44     26.45      6.04      72     164       0
    4.881   4.791     7.60  10.00     23.23      6.65      84     190       0
    4.791   4.706     7.83  19.39     32.61      7.32      58     143       0
    4.706   4.625     8.56  14.05     27.85      6.67      55     152       0
    4.625   4.548     8.09  29.95     31.45      5.11      66     160       0
    4.548   4.475     7.68  18.67     30.26      6.93      95     209       0
    4.475   4.405     7.03  10.42     30.38      8.50      68     165       0
    4.405   4.338     6.50  15.91     33.46      7.44      74     190       0
    4.338   4.275     7.63  20.32     31.50      6.70      77     193       0
    4.275   4.214     6.66  14.11     30.18      7.53      78     189       0
    4.214   4.155     6.52  10.31     28.29      8.52      84     209       0
    4.155   4.099     6.99  12.22     29.68      7.60      83     210       0
    4.099   4.045     6.04   9.47     25.65      7.64      80     204       0
    4.045   3.994     5.86   6.23     33.32     13.09      69     195       0
    3.994   3.944     5.36   8.89     31.83     10.34     102     227       0
    3.944   3.896     5.19   7.75     30.04      9.86      72     215       0
    3.896   3.850     5.18  11.10     29.97      9.25      81     221       0
    3.850   3.805     4.18   5.61     23.78     11.27      78     223       0
    3.805   3.762     4.69   6.79     28.07     10.56      93     233       0
    3.762   3.720     3.55   4.65     33.44     16.91      69     235       0
    3.720   3.680     4.15   4.26     30.30     14.50      81     211       0
    3.680   3.641     3.80   5.16     32.51     14.26      92     254       0
    3.641   3.603     3.57   4.06     27.16     14.87      71     237       0
    3.603   3.566     3.65   3.73     28.33     15.97      75     214       0
    3.566   3.530     3.67   4.12     24.32     12.19      51     188       0
    3.530   3.496     3.33   3.41     31.58     19.87      56     222       0
    3.496   3.462     3.11   3.22     38.72     23.77      75     227       0
    3.462   3.430     2.82   5.02     38.83     19.37      59     234       0
    3.430   3.398     2.54   1.64     35.32     27.88      61     232       0
    3.398   3.367     2.26   0.75     32.44     34.66      84     247       0
    3.367   3.337     2.48   2.66     35.13     22.59      62     238       0
    3.337   3.308     2.54   2.59     34.23     21.88      66     238       0
    3.308   3.279     2.04   1.07     41.93     41.14      60     249       0
    3.279   3.252     1.87   1.06     35.93     39.62      81     251       0
    3.252   3.225     1.74   1.57     45.34     41.03      69     260       0
    3.225   3.198     1.78   1.44     34.32     31.99      66     265       0
    3.198   3.172     1.69   0.88     28.44     31.89      64     257       0
    3.172   3.147     1.65   2.69     34.14     26.47      52     251       0
    3.147   3.123     1.40   1.08     43.48     49.15      84     289       0
    3.123   3.099     1.36   1.44     44.49     49.79      50     249       0
    3.099   3.075     1.43   0.70     19.98     26.01      84     293       0
    3.075   3.052     1.24   1.02     37.69     40.61      70     269       0
    3.052   3.030     1.04   0.45     43.38     65.55      62     287       0
    3.030   3.008     1.06   0.61     30.52     40.50      68     276       0
    3.008   2.987     1.16   0.47     25.12     40.55      66     293       0
    2.987   2.966     0.97   0.41     38.58     66.14      60     271       0
    2.966   2.945     1.10   1.92     51.85     51.98      60     300       0
    2.945   2.925     0.81   0.62     54.28     74.03      62     279       0
    2.925   2.905     0.75   0.35     39.83     70.83      50     248       0
    2.905   2.886     0.86   0.30     37.81     75.88      42     249       0
    2.886   2.867     0.64   0.37     33.92     62.34      58     281       0
    2.867   2.848     0.74   0.84     79.43    117.28      52     252       0
    2.848   2.830     0.74   0.70     47.11     65.88      54     271       0
    2.830   2.812     0.71   0.41     57.55     95.78      54     289       0
    2.812   2.794     0.65   0.40     57.30     89.00      50     307       0
    2.794   2.777     0.66   0.21     69.27    163.83      52     259       0
    2.777   2.760     0.65   0.32     60.47    111.45      52     301       0
    2.760   2.744     0.55   0.24     42.71     93.63      46     324       0
    2.744   2.727     0.50   0.19     58.59    136.10      64     287       0
    2.727   2.711     0.48   0.19     43.44     95.33      48     307       0
    2.711   2.696     0.48   0.31     63.00    124.85      60     306       0
    2.696   2.680     0.47   0.21     57.45    121.86      60     315       0
    2.680   2.665     0.48   0.25     58.88    112.81      40     317       0
    2.665   2.650     0.43   0.22     79.66    196.78      48     310       0
    2.650   2.635     0.47   0.34     60.92    124.75      56     333       0
    2.635   2.621     0.33   0.14    169.48    443.86      38     299       0
    2.621   2.607     0.37   0.27     62.70    132.40      56     312       0
    2.607   2.593     0.27   0.23    119.47    251.39      56     332       0
    2.593   2.579     0.27   0.16     92.46    224.36      58     338       0
    2.579   2.565     0.33   0.49     92.34    144.30      42     297       0
    2.565   2.552     0.24   0.17     79.60    235.40      60     335       0
    2.552   2.539     0.31   0.20     74.27    155.58      50     353       0
    2.539   2.526     0.31   0.15     99.13    250.61      52     329       0
    2.526   2.513     0.19   0.24     70.80    146.75      42     317       0
    2.513   2.500     0.20   0.31     91.10    185.30      24     273       0
   --------------------------------------------------------------------------
   43.663   2.500     3.27   8.50     24.45     10.62    6383   21981       0
 


 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR VARIOUS SUBSETS OF INCLUDED DATA IMAGES
 ******************************************************************************

 Data set statistics is reported below several times, each with a different
 upper limit on the number of images included. This provides the user with
 the information for deciding which data images should be excluded from the
 final data set because of radiation damage or other defects. If the user
 decides for a subset of "good" images that differs from the specification
 as given by the input parameter (see DATA_RANGE= in XDS.INP) the CORRECT-
 step of XDS must be repeated with the new parameter values for DATA_RANGE=.


 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       1      17
 ******************************************************************************


          COMPARISON OF DATA WITH REFERENCE DATA SET
          ------------------------------------------

 R-SCALE  = SUM(ABS(I(h,1)-I(h,2)))/SUM(0.5*(I(h,1)+I(h,2)))

 RESOLUTION  R-SCALE   NUMBER OF REFLECTIONS
     7.40      14.0%           255
     5.27      16.1%           479
     4.32      19.5%           613
     3.74      24.8%           768
     3.35      31.6%           813
     3.06      41.9%           920
     2.83      56.0%           953
     2.65      86.1%          1071
     2.50     143.5%          1113
    total      27.1%         13970

          COMPLETENESS AND QUALITY OF DATA SET
          ------------------------------------

 R-FACTOR
 observed = (SUM(ABS(I(h,i)-I(h))))/(SUM(I(h,i)))
 expected = expected R-FACTOR derived from Sigma(I)

 COMPARED = number of reflections used for calculating R-FACTOR
 I/SIGMA  = mean of intensity/Sigma(I) of unique reflections
            (after merging symmetry-related observations)
 Sigma(I) = standard deviation of reflection intensity I
            estimated from sample statistics

 R-meas   = redundancy independent R-factor (intensities)
            Diederichs & Karplus (1997), Nature Struct. Biol. 4, 269-275.

 CC(1/2)  = percentage of correlation between intensities from
            random half-datasets. Correlation significant at
            the 0.1% level is marked by an asterisk.
            Karplus & Diederichs (2012), Science 336, 1030-33
 Anomal   = percentage of correlation between random half-sets
  Corr      of anomalous intensity differences. Correlation
            significant at the 0.1% level is marked.
 SigAno   = mean anomalous difference in units of its estimated
            standard deviation (|F(+)-F(-)|/Sigma). F(+), F(-)
            are structure factor estimates obtained from the
            merged intensity observations in each parity class.
  Nano    = Number of unique reflections used to calculate
            Anomal_Corr & SigAno. At least two observations
            for each (+ and -) parity are required.


 SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION
 RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano
   LIMIT     OBSERVED  UNIQUE  POSSIBLE     OF DATA   observed  expected                                      Corr

     7.40         293     262      1823       14.4%       7.6%      2.3%       62   19.29     10.7%    94.4*     0    0.000       0
     5.27         501     493      3151       15.6%       1.4%      3.7%       16    9.50      2.0%   100.0*     0    0.000       0
     4.32         658     648      4043       16.0%       8.0%      3.3%       20    8.95     11.3%    98.3*     0    0.000       0
     3.74         809     797      4739       16.8%       6.1%      6.1%       24    7.17      8.6%    98.4*     0    0.000       0
     3.35         865     852      5379       15.8%       7.0%      7.9%       26    4.44      9.9%    99.1*     0    0.000       0
     3.06         968     954      5912       16.1%      11.5%      9.3%       28    2.50     16.3%    92.7*     0    0.000       0
     2.83        1033    1016      6445       15.8%      15.0%     27.4%       34    1.36     21.2%    92.3*     0    0.000       0
     2.65        1140    1127      6919       16.3%      27.8%     58.1%       26    0.83     39.4%    74.4      0    0.000       0
     2.50        1175    1157      7351       15.7%      31.0%     61.4%       36    0.47     43.8%    62.7      0    0.000       0
    total        7442    7306     45762       16.0%       7.9%      5.3%      272    4.15     11.1%    96.3*     0    0.000       0


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES      7442
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                         7442
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                   7306



 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       1      34
 ******************************************************************************


          COMPARISON OF DATA WITH REFERENCE DATA SET
          ------------------------------------------

 R-SCALE  = SUM(ABS(I(h,1)-I(h,2)))/SUM(0.5*(I(h,1)+I(h,2)))

 RESOLUTION  R-SCALE   NUMBER OF REFLECTIONS
     7.40      12.8%           420
     5.27      13.7%           832
     4.32      17.0%          1136
     3.74      22.6%          1454
     3.35      30.3%          1596
     3.06      42.1%          1859
     2.83      62.7%          1930
     2.65      97.7%          2141
     2.50     169.1%          2280
    total      26.3%         27296

          COMPLETENESS AND QUALITY OF DATA SET
          ------------------------------------

 R-FACTOR
 observed = (SUM(ABS(I(h,i)-I(h))))/(SUM(I(h,i)))
 expected = expected R-FACTOR derived from Sigma(I)

 COMPARED = number of reflections used for calculating R-FACTOR
 I/SIGMA  = mean of intensity/Sigma(I) of unique reflections
            (after merging symmetry-related observations)
 Sigma(I) = standard deviation of reflection intensity I
            estimated from sample statistics

 R-meas   = redundancy independent R-factor (intensities)
            Diederichs & Karplus (1997), Nature Struct. Biol. 4, 269-275.

 CC(1/2)  = percentage of correlation between intensities from
            random half-datasets. Correlation significant at
            the 0.1% level is marked by an asterisk.
            Karplus & Diederichs (2012), Science 336, 1030-33
 Anomal   = percentage of correlation between random half-sets
  Corr      of anomalous intensity differences. Correlation
            significant at the 0.1% level is marked.
 SigAno   = mean anomalous difference in units of its estimated
            standard deviation (|F(+)-F(-)|/Sigma). F(+), F(-)
            are structure factor estimates obtained from the
            merged intensity observations in each parity class.
  Nano    = Number of unique reflections used to calculate
            Anomal_Corr & SigAno. At least two observations
            for each (+ and -) parity are required.


 SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION
 RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano
   LIMIT     OBSERVED  UNIQUE  POSSIBLE     OF DATA   observed  expected                                      Corr

     7.40         590     427      1823       23.4%       7.8%      2.6%      324   20.85     11.1%    96.8*     0    0.000       0
     5.27        1015     846      3151       26.8%      10.6%      5.9%      336    9.46     15.0%    96.1*     0    0.000       0
     4.32        1313    1173      4043       29.0%      14.4%      5.6%      280    8.93     20.3%    93.7*     0    0.000       0
     3.74        1602    1486      4739       31.4%      14.0%      6.9%      232    6.84     19.8%    91.0*     0    0.000       0
     3.35        1722    1644      5379       30.6%      12.5%      9.6%      156    3.97     17.7%    93.9*     0    0.000       0
     3.06        1966    1902      5912       32.2%      13.9%     12.8%      128    2.15     19.7%    92.2*     0    0.000       0
     2.83        2072    2004      6445       31.1%      17.7%     23.6%      136    1.12     25.0%    91.6*     0    0.000       0
     2.65        2288    2213      6919       32.0%      26.9%     54.6%      150    0.70     38.0%    82.6*     0    0.000       0
     2.50        2406    2331      7351       31.7%      37.7%     80.4%      150    0.39     53.3%    65.5*     0    0.000       0
    total       14974   14026     45762       30.6%      11.4%      6.3%     1892    3.77     16.1%    96.4*     0    0.000       0


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     14974
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        14974
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  14026



 ******************************************************************************
  STATISTICS OF SAVED DATA SET "XDS_ASCII.HKL" (DATA_RANGE=       1      50)
 FILE TYPE:         XDS_ASCII      MERGE=FALSE          FRIEDEL'S_LAW=TRUE 
 ******************************************************************************

   REFLECTIONS OF TYPE H,0,0  0,K,0  0,0,L OR EXPECTED TO BE ABSENT (*)
   --------------------------------------------------------------------

   H    K    L  RESOLUTION  INTENSITY     SIGMA    INTENSITY/SIGMA  #OBSERVED

   32    0    0     5.929   0.1152E+01  0.5379E+01         0.21           1 
   34    0    0     5.581   0.4149E+03  0.1634E+02        25.39           1 
   36    0    0     5.271   0.8862E+02  0.8701E+01        10.19           1 
   38    0    0     4.993   0.6338E+02  0.8491E+01         7.47           1 
   40    0    0     4.743   0.9372E+03  0.2858E+02        32.79           1 
   42    0    0     4.518   0.6377E+01  0.7032E+01         0.91           1 
   44    0    0     4.312   0.1523E+04  0.4163E+02        36.58           1 
   46    0    0     4.125   0.4684E+03  0.1960E+02        23.90           1 
   48    0    0     3.953   0.1451E+02  0.8405E+01         1.73           1 
   50    0    0     3.795   0.1021E+02  0.8411E+01         1.21           1 
   52    0    0     3.649   0.1729E+03  0.1369E+02        12.63           1 
   54    0    0     3.514   0.4434E+02  0.9719E+01         4.56           1 
   56    0    0     3.388   0.4148E+02  0.9968E+01         4.16           1 
   60    0    0     3.162   0.8925E+01  0.9277E+01         0.96           1 
   62    0    0     3.060   0.4652E+02  0.1121E+02         4.15           1 
   64    0    0     2.965   0.3737E+01  0.9197E+01         0.41           1 
   66    0    0     2.875  -0.9880E+00  0.8789E+01        -0.11           1 
   68    0    0     2.790   0.8587E+01  0.9258E+01         0.93           1 
   70    0    0     2.711   0.3760E+01  0.8971E+01         0.42           1 
   72    0    0     2.635  -0.4030E+01  0.8606E+01        -0.47           1 
   74    0    0     2.564   0.3892E+01  0.8991E+01         0.43           1 

          COMPARISON OF DATA WITH REFERENCE DATA SET
          ------------------------------------------

 R-SCALE  = SUM(ABS(I(h,1)-I(h,2)))/SUM(0.5*(I(h,1)+I(h,2)))

 RESOLUTION  R-SCALE   NUMBER OF REFLECTIONS
     7.40      22.3%           555
     5.27      18.0%          1074
     4.32      19.1%          1461
     3.74      22.4%          1863
     3.35      30.4%          2084
     3.06      43.4%          2474
     2.83      70.4%          2616
     2.65     114.0%          2988
     2.50     204.7%          3221
    total      30.1%         36672

          COMPLETENESS AND QUALITY OF DATA SET
          ------------------------------------

 R-FACTOR
 observed = (SUM(ABS(I(h,i)-I(h))))/(SUM(I(h,i)))
 expected = expected R-FACTOR derived from Sigma(I)

 COMPARED = number of reflections used for calculating R-FACTOR
 I/SIGMA  = mean of intensity/Sigma(I) of unique reflections
            (after merging symmetry-related observations)
 Sigma(I) = standard deviation of reflection intensity I
            estimated from sample statistics

 R-meas   = redundancy independent R-factor (intensities)
            Diederichs & Karplus (1997), Nature Struct. Biol. 4, 269-275.

 CC(1/2)  = percentage of correlation between intensities from
            random half-datasets. Correlation significant at
            the 0.1% level is marked by an asterisk.
            Karplus & Diederichs (2012), Science 336, 1030-33
 Anomal   = percentage of correlation between random half-sets
  Corr      of anomalous intensity differences. Correlation
            significant at the 0.1% level is marked.
 SigAno   = mean anomalous difference in units of its estimated
            standard deviation (|F(+)-F(-)|/Sigma). F(+), F(-)
            are structure factor estimates obtained from the
            merged intensity observations in each parity class.
  Nano    = Number of unique reflections used to calculate
            Anomal_Corr & SigAno. At least two observations
            for each (+ and -) parity are required.


 SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION
 RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano
   LIMIT     OBSERVED  UNIQUE  POSSIBLE     OF DATA   observed  expected                                      Corr

     7.40         860     563      1823       30.9%      14.5%      2.7%      583   19.88     20.1%    89.5*     0    0.000       1
     5.27        1493    1088      3151       34.5%      20.6%      6.9%      783    8.68     28.6%    87.5*    43    0.581       2
     4.32        1924    1502      4043       37.2%      28.0%      6.7%      828    8.30     38.9%    76.1*     0    0.000       0
     3.74        2347    1895      4739       40.0%      29.4%      9.2%      892    6.14     41.3%    69.3*     0    0.000       0
     3.35        2527    2133      5379       39.7%      31.3%     18.0%      779    3.51     44.0%    73.5*     0    0.000       0
     3.06        2893    2518      5912       42.6%      34.7%     32.8%      748    1.83     49.1%    73.9*     0    0.000       0
     2.83        3024    2698      6445       41.9%      39.4%     58.3%      652    0.95     55.7%    74.8*     0    0.000       0
     2.65        3354    3068      6919       44.3%      57.5%    113.6%      572    0.57     81.3%    56.4*     0    0.000       0
     2.50        3559    3286      7351       44.7%      81.8%    180.7%      546    0.31    115.7%    44.3*     0    0.000       0
    total       21981   18751     45762       41.0%      24.5%     10.6%     6383    3.32     34.1%    87.0*   -92    1.459       3


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     21981
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        21981
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  18751



 ******************************************************************************
    WILSON STATISTICS OF DATA SET  "XDS_ASCII.HKL"
 ******************************************************************************

 Data is divided into resolution shells and a straight line 
 A - 2*B*SS is fitted to log<I>, where
   RES    = mean resolution (Angstrom) in shell
   SS     = mean of (sin(THETA)/LAMBDA)**2 in shell
   <I>    = mean reflection intensity in shell
   BO     = (A - log<I>)/(2*SS)
    #     = number of reflections in resolution shell

   WILSON LINE (using all data) : A=   5.191 B=  57.496 CORRELATION=  0.97
      #      RES      SS        <I>       log(<I>)       BO
     165    13.669   0.001  1.5055E+02       5.014      66.2
     350     8.655   0.003  9.4659E+01       4.550      96.0
     437     6.797   0.005  5.2329E+01       3.958     114.0
     569     5.765   0.008  4.4853E+01       3.803      92.3
     675     5.096   0.010  5.1517E+01       3.942      64.9
     681     4.627   0.012  6.4723E+01       4.170      43.7
     830     4.259   0.014  5.9381E+01       4.084      40.2
     905     3.967   0.016  4.6847E+01       3.847      42.3
    1015     3.728   0.018  3.2827E+01       3.491      47.3
     960     3.528   0.020  2.7159E+01       3.302      47.0
    1095     3.358   0.022  1.8506E+01       2.918      51.3
    1168     3.210   0.024  1.2593E+01       2.533      54.8
    1285     3.080   0.026  8.7617E+00       2.170      57.3
    1310     2.965   0.028  6.7015E+00       1.902      57.8
    1269     2.860   0.031  4.6460E+00       1.536      59.8
    1424     2.767   0.033  3.8036E+00       1.336      59.0
    1502     2.682   0.035  2.9612E+00       1.086      59.1
    1562     2.604   0.037  1.9152E+00       0.650      61.6
    1549     2.535   0.039  1.5794E+00       0.457      60.8


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF  CENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         3<I>**2     15<I>**3    105<I>**4 

       7    13.669        0.605        0.364        0.170
      10     8.655        7.379       16.974       30.370
      12     6.797        0.352        0.115        0.029
      14     5.765        0.879        0.620        0.357
      12     5.096        0.083        0.013        0.002
      15     4.627        2.320        2.784        2.589
      16     4.259        4.811        9.767       16.628
      12     3.967        1.452        1.760        1.664
      15     3.728        0.451        0.220        0.085
      13     3.528        5.345        8.606       11.591
      16     3.358        0.379        0.128        0.034
      12     3.210        2.550        3.423        3.440
      14     3.080        0.829        0.538        0.287
      17     2.965        1.876        3.091        3.976
      12     2.860        0.317        0.153        0.062
      19     2.767        0.675        0.234        0.079
      17     2.682        3.976        8.690       15.278
      13     2.604        0.798        0.333        0.146
      18     2.535        0.787       -0.342        0.346
     264   overall        1.856        2.925        4.434


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF ACENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         2<I>**2      6<I>**3     24<I>**4 

     158    13.669        1.104        1.217        1.253
     340     8.655        0.940        0.912        0.841
     425     6.797        1.185        1.528        2.060
     555     5.765        1.207        1.708        2.668
     663     5.096        1.104        1.174        1.165
     666     4.627        1.058        1.149        1.211
     814     4.259        1.217        1.869        3.165
     893     3.967        1.108        1.265        1.423
    1000     3.728        1.243        1.701        2.445
     947     3.528        1.266        1.804        2.550
    1079     3.358        1.282        1.714        2.233
    1156     3.210        1.292        1.767        2.433
    1271     3.080        1.499        2.549        4.710
    1293     2.965        1.764        3.605        7.739
    1257     2.860        1.620        2.742        5.373
    1405     2.767        2.440        9.971       57.519
    1485     2.682        2.106        3.940        8.634
    1549     2.604        3.543        9.381       39.172
    1531     2.535        3.508        5.925       15.511
   18487   overall        1.841        3.700       11.854

   ======= CUMULATIVE INTENSITY DISTRIBUTION =======
 DEFINITIONS:
   <I>    = mean reflection intensity
 Na(Z)exp = expected number of acentric reflections with I <= Z*<I>
 Na(Z)obs = observed number of acentric reflections with I <= Z*<I>
 Nc(Z)exp = expected number of  centric reflections with I <= Z*<I>
 Nc(Z)obs = observed number of  centric reflections with I <= Z*<I>



 Nc(Z)obs/Nc(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

       7    13.669  0.00  0.00  0.69  0.91  0.82  1.27  1.20  1.14  1.30  1.26
      10     8.655  0.81  0.87  0.96  0.85  0.77  0.71  0.84  0.80  0.76  0.73
      12     6.797  0.67  0.96  1.00  1.06  0.96  1.04  0.98  0.93  1.01  0.98
      14     5.765  0.58  1.03  1.20  1.06  1.10  1.15  1.08  1.02  0.98  0.94
      12     5.096  1.34  1.45  1.40  1.23  1.28  1.19  1.26  1.19  1.40  1.47
      15     4.627  1.34  0.96  0.96  0.99  0.90  0.95  1.00  0.95  0.91  0.88
      16     4.259  0.50  0.72  0.60  0.53  0.72  0.67  0.63  0.70  0.76  0.73
      12     3.967  1.01  1.21  1.20  1.06  0.96  0.89  0.98  0.93  0.89  1.10
      15     3.728  0.81  1.16  0.96  0.99  1.02  1.07  1.00  0.95  1.01  1.17
      13     3.528  0.31  0.67  0.55  0.49  0.44  0.41  0.39  0.49  0.59  0.56
      16     3.358  0.76  0.90  0.90  0.92  0.84  0.89  0.84  0.89  0.86  0.92
      12     3.210  2.01  1.45  1.40  1.41  1.28  1.19  1.12  1.06  1.14  1.10
      14     3.080  0.86  0.83  0.69  0.91  0.82  1.02  0.96  0.91  0.98  1.05
      17     2.965  0.95  0.68  0.85  0.99  1.13  1.05  1.08  1.12  1.07  1.03
      12     2.860  2.01  1.69  1.40  1.41  1.28  1.19  1.26  1.19  1.27  1.34
      19     2.767  1.06  0.76  0.76  0.78  0.91  0.94  0.88  0.84  0.80  0.77
      17     2.682  0.95  0.68  0.71  0.62  0.79  0.73  0.79  0.84  0.81  0.95
      13     2.604  1.55  1.11  1.11  0.98  0.89  0.82  1.03  1.10  1.05  1.01
      18     2.535  1.57  1.45  1.20  1.17  1.07  1.09  1.12  1.06  1.10  1.06
     264   overall  1.02  0.99  0.96  0.95  0.95  0.95  0.96  0.95  0.97  0.99


 Na(Z)obs/Na(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

     158    13.669  1.06  1.05  1.00  1.08  1.09  1.12  1.08  1.08  1.06  1.03
     340     8.655  1.14  1.22  1.13  1.08  1.09  1.07  1.04  0.98  1.00  1.02
     425     6.797  1.19  1.22  1.22  1.16  1.13  1.10  1.06  1.07  1.07  1.03
     555     5.765  1.23  1.18  1.14  1.11  1.12  1.15  1.10  1.11  1.09  1.06
     663     5.096  1.24  1.21  1.16  1.11  1.10  1.08  1.06  1.04  1.01  1.00
     666     4.627  1.09  1.05  1.11  1.12  1.09  1.05  1.04  1.05  1.06  1.03
     814     4.259  1.33  1.27  1.18  1.18  1.16  1.12  1.11  1.09  1.07  1.06
     893     3.967  1.31  1.25  1.14  1.13  1.08  1.06  1.04  1.03  1.02  1.02
    1000     3.728  1.32  1.24  1.25  1.24  1.17  1.14  1.11  1.08  1.06  1.03
     947     3.528  1.60  1.44  1.33  1.27  1.20  1.15  1.12  1.10  1.09  1.08
    1079     3.358  1.73  1.34  1.23  1.19  1.15  1.12  1.13  1.10  1.08  1.05
    1156     3.210  1.79  1.34  1.24  1.16  1.14  1.11  1.08  1.08  1.06  1.04
    1271     3.080  2.05  1.41  1.24  1.15  1.13  1.11  1.10  1.08  1.06  1.04
    1293     2.965  2.41  1.56  1.32  1.19  1.13  1.10  1.08  1.06  1.07  1.07
    1257     2.860  2.52  1.51  1.20  1.08  1.03  0.98  0.98  0.97  0.97  0.97
    1405     2.767  2.89  1.72  1.34  1.17  1.09  1.04  1.01  0.99  0.99  0.98
    1485     2.682  3.21  1.84  1.42  1.21  1.10  1.03  1.00  0.96  0.95  0.94
    1549     2.604  3.81  2.11  1.57  1.30  1.13  1.03  0.97  0.93  0.91  0.89
    1531     2.535  3.88  2.13  1.56  1.29  1.13  1.03  0.97  0.91  0.88  0.85
   18487   overall  2.27  1.54  1.30  1.19  1.12  1.07  1.05  1.03  1.01  1.00


 List of     52 reflections *NOT* obeying Wilson distribution (Z> 10.0)

   h    k    l     RES      Z     Intensity    Sigma

   66    2    3    2.81   32.37  0.2462E+03  0.1594E+02 "alien"
   34   36   -7    2.61   27.16  0.1040E+03  0.2076E+02 "alien"
   71    1    3    2.62   25.28  0.9682E+02  0.1278E+02 "alien"
   36   32   -7    2.80   25.01  0.1902E+03  0.2585E+02 "alien"
   30   34   -7    2.79   23.48  0.1786E+03  0.2475E+02 "alien"
   73    9   -2    2.56   19.55  0.6176E+02  0.1407E+02 "alien"
   32   36   -7    2.64   17.63  0.6752E+02  0.1878E+02 "alien"
   62   24   -4    2.55   16.02  0.5059E+02  0.1601E+02 "alien"
   69    5    4    2.64   14.45  0.8555E+02  0.1007E+02 "alien"
   29   33    6    2.83   14.33  0.1331E+03  0.1627E+02 "alien"
   49   23   -6    2.96   14.02  0.1879E+03  0.2424E+02 "alien"
   44   30    5    2.69   14.00  0.8293E+02  0.1049E+02 "alien"
   37   35   -8    2.59   13.88  0.5315E+02  0.1950E+02 "alien"
   67    9    5    2.64   13.67  0.5236E+02  0.6364E+01 "alien"
    3   41    8    2.54   13.37  0.4224E+02  0.1603E+02 "alien"
   34   36   -8    2.58   13.35  0.5114E+02  0.1863E+02 "alien"
   37   35   -7    2.61   13.22  0.5065E+02  0.1800E+02 "alien"
   14   32    7    3.11   13.17  0.2308E+03  0.2181E+02 "alien"
   65    9   -2    2.85   13.05  0.1212E+03  0.1649E+02 "alien"
   40   34   -7    2.61   13.01  0.4984E+02  0.1795E+02 "alien"
   73    9   -3    2.56   13.01  0.4108E+02  0.1374E+02 "alien"
   59   11   -2    3.08   12.96  0.2271E+03  0.1255E+02 "alien"
   26   32    6    2.95   12.83  0.1720E+03  0.1783E+02 "alien"
   42   32   -8    2.64   12.48  0.7392E+02  0.1925E+02 "alien"
   69    9   -3    2.70   12.30  0.7286E+02  0.1533E+02 "alien"
   62    8   -4    2.99   12.28  0.1646E+03  0.1179E+02 "alien"
   38   34   -7    2.65   12.20  0.7225E+02  0.2010E+02 "alien"
   55   29   -6    2.53   12.01  0.3793E+02  0.1611E+02 "alien"
   64    4   -1    2.96   11.81  0.1583E+03  0.1628E+02 "alien"
   71   15   -2    2.52   11.80  0.3728E+02  0.1424E+02 "alien"
   31   33    6    2.79   11.80  0.8977E+02  0.1419E+02 "alien"
   42   32   -7    2.67   11.39  0.6744E+02  0.1996E+02 "alien"
   71    3    3    2.61   11.26  0.4311E+02  0.9583E+01 "alien"
   70    8    0    2.66   11.06  0.6548E+02  0.1404E+02 "alien"
   72   14   -2    2.51   11.02  0.3482E+02  0.1452E+02 "alien"
   68   10   -3    2.72   10.97  0.6497E+02  0.1448E+02 "alien"
   34   32    6    2.79   10.97  0.8344E+02  0.1276E+02 "alien"
   51   27   -9    2.64   10.95  0.4196E+02  0.1723E+02 "alien"
   67   17   -2    2.61   10.87  0.4164E+02  0.1456E+02 "alien"
   58   20   -5    2.80   10.66  0.8107E+02  0.1691E+02 "alien"
    1   41    8    2.55   10.61  0.3352E+02  0.1674E+02 "alien"
   25   37    9    2.55   10.52  0.3324E+02  0.1282E+02 "alien"
   16   14   -6    5.74   10.46  0.9380E+03  0.2465E+02 "alien"
   41    7   -4    4.40   10.43  0.1238E+04  0.4113E+02 "alien"
   18   22    5    4.20   10.35  0.1229E+04  0.3822E+02 "alien"
   49   13   -4    3.51   10.27  0.5578E+03  0.3077E+02 "alien"
   38   28    5    2.96   10.25  0.1374E+03  0.1292E+02 "alien"
   30   30    6    3.00   10.23  0.1371E+03  0.1488E+02 "alien"
   50    2    0    3.79   10.19  0.6687E+03  0.1871E+02 "alien"
   61    3   -8    3.00   10.18  0.1364E+03  0.1285E+02 "alien"
   10   34    7    3.00   10.18  0.1364E+03  0.1942E+02 "alien"
   71    5    4    2.57   10.10  0.3868E+02  0.8195E+01 "alien"


 List of     52 reflections *NOT* obeying Wilson distribution (sorted by resolution)
 Ice rings could occur at (Angstrom):
 3.897,3.669,3.441, 2.671,2.249,2.072, 1.948,1.918,1.883,1.721

   h    k    l     RES      Z     Intensity    Sigma

   72   14   -2    2.51   11.02  0.3482E+02  0.1452E+02
   71   15   -2    2.52   11.80  0.3728E+02  0.1424E+02
   55   29   -6    2.53   12.01  0.3793E+02  0.1611E+02
    3   41    8    2.54   13.37  0.4224E+02  0.1603E+02
    1   41    8    2.55   10.61  0.3352E+02  0.1674E+02
   25   37    9    2.55   10.52  0.3324E+02  0.1282E+02
   62   24   -4    2.55   16.02  0.5059E+02  0.1601E+02
   73    9   -2    2.56   19.55  0.6176E+02  0.1407E+02
   73    9   -3    2.56   13.01  0.4108E+02  0.1374E+02
   71    5    4    2.57   10.10  0.3868E+02  0.8195E+01
   34   36   -8    2.58   13.35  0.5114E+02  0.1863E+02
   37   35   -8    2.59   13.88  0.5315E+02  0.1950E+02
   67   17   -2    2.61   10.87  0.4164E+02  0.1456E+02
   71    3    3    2.61   11.26  0.4311E+02  0.9583E+01
   40   34   -7    2.61   13.01  0.4984E+02  0.1795E+02
   34   36   -7    2.61   27.16  0.1040E+03  0.2076E+02
   37   35   -7    2.61   13.22  0.5065E+02  0.1800E+02
   71    1    3    2.62   25.28  0.9682E+02  0.1278E+02
   51   27   -9    2.64   10.95  0.4196E+02  0.1723E+02
   67    9    5    2.64   13.67  0.5236E+02  0.6364E+01
   32   36   -7    2.64   17.63  0.6752E+02  0.1878E+02
   69    5    4    2.64   14.45  0.8555E+02  0.1007E+02
   42   32   -8    2.64   12.48  0.7392E+02  0.1925E+02
   38   34   -7    2.65   12.20  0.7225E+02  0.2010E+02
   70    8    0    2.66   11.06  0.6548E+02  0.1404E+02
   42   32   -7    2.67   11.39  0.6744E+02  0.1996E+02
   44   30    5    2.69   14.00  0.8293E+02  0.1049E+02
   69    9   -3    2.70   12.30  0.7286E+02  0.1533E+02
   68   10   -3    2.72   10.97  0.6497E+02  0.1448E+02
   34   32    6    2.79   10.97  0.8344E+02  0.1276E+02
   30   34   -7    2.79   23.48  0.1786E+03  0.2475E+02
   31   33    6    2.79   11.80  0.8977E+02  0.1419E+02
   36   32   -7    2.80   25.01  0.1902E+03  0.2585E+02
   58   20   -5    2.80   10.66  0.8107E+02  0.1691E+02
   66    2    3    2.81   32.37  0.2462E+03  0.1594E+02
   29   33    6    2.83   14.33  0.1331E+03  0.1627E+02
   65    9   -2    2.85   13.05  0.1212E+03  0.1649E+02
   26   32    6    2.95   12.83  0.1720E+03  0.1783E+02
   64    4   -1    2.96   11.81  0.1583E+03  0.1628E+02
   38   28    5    2.96   10.25  0.1374E+03  0.1292E+02
   49   23   -6    2.96   14.02  0.1879E+03  0.2424E+02
   62    8   -4    2.99   12.28  0.1646E+03  0.1179E+02
   10   34    7    3.00   10.18  0.1364E+03  0.1942E+02
   61    3   -8    3.00   10.18  0.1364E+03  0.1285E+02
   30   30    6    3.00   10.23  0.1371E+03  0.1488E+02
   59   11   -2    3.08   12.96  0.2271E+03  0.1255E+02
   14   32    7    3.11   13.17  0.2308E+03  0.2181E+02
   49   13   -4    3.51   10.27  0.5578E+03  0.3077E+02
   50    2    0    3.79   10.19  0.6687E+03  0.1871E+02
   18   22    5    4.20   10.35  0.1229E+04  0.3822E+02
   41    7   -4    4.40   10.43  0.1238E+04  0.4113E+02
   16   14   -6    5.74   10.46  0.9380E+03  0.2465E+02

 NUMBER OF UNIQUE ALIEN REFLECTIONS WITH A Z-SCORE ABOVE LIMIT         5
 (ALIENS ABOVE LIMIT (REJECT_ALIEN=      20.0) ARE MARKED INVALID)

 NUMBER OF REFLECTION RECORDS ON OUTPUT FILE "XDS_ASCII.HKL"       21981
 NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES)   21976
 NUMBER OF REJECTED MISFITS & ALIENS (marked by -1*SIGMA(IOBS))        5


 cpu time used                  4.9 sec
 elapsed wall-clock time        3.1 sec

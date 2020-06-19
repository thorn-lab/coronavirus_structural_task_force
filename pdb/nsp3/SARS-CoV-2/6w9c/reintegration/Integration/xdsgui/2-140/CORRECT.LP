
 ***** CORRECT ***** (VERSION Jan 31, 2020  BUILT=20200417)  12-May-2020

 INPUT PARAMETER VALUES
 ----------------------
 SPACE_GROUP_NUMBER=    5 as used in the INTEGRATE step
 UNIT_CELL_CONSTANTS=   190.872   110.283    64.225  90.000  96.302  90.000 as used by INTEGRATE
 FRIEDEL'S_LAW=TRUE 
 PROFILE_FITTING= TRUE 
 OVERLOAD=   1267439     MINPK=  75.00000    WFAC1=   1.0
 INCLUDE_RESOLUTION_RANGE=    50.000     2.500
 NAME_TEMPLATE_OF_DATA_FRAMES=/home/dale/Structures/sars-2/nsp3/6w9c/images/IDP51000_6w9c/data/y3_b07b_?????.cbf CBF
 DATA_RANGE=       2     100
 ROTATION_AXIS= -0.999995  0.001201  0.002963
 OSCILLATION_RANGE=  0.500000
 STARTING_ANGLE=   -90.000     STARTING_FRAME=       1
 X-RAY_WAVELENGTH=  0.979180
 INCIDENT_BEAM_DIRECTION=  0.000048 -0.001614  0.999999
 FRACTION_OF_POLARIZATION=   0.980
 POLARIZATION_PLANE_NORMAL=  0.000000  1.000000  0.000000
 AIR=   0.00032
 DETECTOR=PILATUS
 SILICON=  3.703301 SENSOR_THICKNESS=  1.000000
 NUMBER OF DETECTOR SEGMENTS   1
 NX=  2463  NY=  2527    QX=  0.172000  QY=  0.172000
 ORGX=   1246.46  ORGY=   1266.86
 DETECTOR_DISTANCE=   516.819
 DIRECTION_OF_DETECTOR_X-AXIS=   1.00000   0.00000   0.00000
 DIRECTION_OF_DETECTOR_Y-AXIS=   0.00000   1.00000   0.00000
 BEAM_DIVERGENCE_E.S.D.=   0.019
 REFLECTING_RANGE_E.S.D.=   0.118
 MINIMUM_ZETA=     0.050
 MAXIMUM_ERROR_OF_SPOT_POSITION=   3.0
 MAXIMUM_ERROR_OF_SPINDLE_POSITION=   2.0
 MINIMUM_I/SIGMA=   3.0
 REFLECTIONS/CORRECTION_FACTOR=      50
 SNRC= 50.00 I/sigma for use in scaling factor determination
 STRICT_ABSORPTION_CORRECTION=FALSE 
 CORRECTIONS= DECAY MODULATION ABSORPTION                      
 REFERENCE_DATA_SET=                                                  
 FIT_B-FACTOR_TO_REFERENCE_DATA_SET=FALSE 

   43518 REFLECTIONS ON FILE "INTEGRATE.HKL"
       0 CORRUPTED REFLECTION RECORDS (IGNORED)
       0 MATCHING REFLECTIONS SPECIFIED IN FILE "FILTER.HKL"
       0 REFLECTIONS INCOMPLETE OR OUTSIDE IMAGE RANGE       2 ...     100
       0 OVERLOADED REFLECTIONS (IGNORED)
       1 REFLECTIONS OUTSIDE ACCEPTED RESOLUTION RANGES
                OR TOO CLOSE TO ROTATION AXIS (IGNORED)
   43517 REFLECTIONS ACCEPTED



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
 UNIT_CELL_CONSTANTS=   190.87   110.28    64.22  90.000  96.300  90.000
 UNIT_CELL_A-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 UNIT_CELL_B-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 UNIT_CELL_C-AXIS=     0.000     0.000     0.000 (0 0 0 : unknown)
 REIDX=  0  0  0  0  0  0  0  0  0  0  0  0 (all 0 : not specified)
 TEST_RESOLUTION_RANGE=   10.00    5.00 (Angstrom) for space group determination
 NUMBER OF ACCEPTED REFLECTIONS FOR CALCULATING Rmeas             4872
 NUMBER OF ACCEPTED UNIQUE REFLECTIONS FROM REFERENCE DATA SET       0


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

 *  31        aP          0.0      64.2  110.2  110.2  60.0  84.5  84.5    0  0  2  0 -1  1  0  0 -1 -1  0  0
 *  20        mC          0.0     190.9  110.3   64.2  90.0  96.3  90.0   -2  0  0  0  0  2  0  0  0  0 -2  0
 *  44        aP          1.8      64.2  110.2  110.3 120.0  90.0  95.5    0  0  2  0  1 -1  0  0  0  2  0  0
 *  41        mC          1.8     190.9  110.3   64.2  90.0  96.3  90.0    2  0  0  0  0  2  0  0  0  0  2  0
    30        mC         41.7     110.2  191.0   64.2  86.9  95.5  90.0   -1  1  0  0  1  3  0  0  0  0 -2  0
    35        mP         83.4     110.2   64.2  110.3  90.0 120.0  95.5   -1  1  0  0  0  0 -2  0  0 -2  0  0
    40        oC         83.4     110.3  190.9   64.2  83.7  90.0  90.0    0  2  0  0 -2  0  0  0  0  0  2  0
    25        mC         85.2     110.2  191.0   64.2  86.9  95.5  90.0    1  1  0  0 -1  3  0  0  0  0  2  0
    23        oC         85.2     110.2  191.0   64.2  86.9  95.5  90.0    1  1  0  0 -1  3  0  0  0  0  2  0
    22        hP         85.2     110.3  110.2   64.2  95.5  90.0 120.0    0 -2  0  0  1  1  0  0  0  0  2  0
    39        mC        170.3     223.7   64.2  110.3  90.0 119.5  78.8   -2  2 -2  0  0  0 -2  0  0 -2  0  0
    37        mC        170.3     223.7   64.2  110.3  90.0 119.5  78.8    2  2  2  0  0  0  2  0  0 -2  0  0
    42        oI        170.3      64.2  110.3  194.6  90.0 102.8  90.0    0  0 -2  0  0  2  0  0  2  0  2  0
    27        mC        336.9     223.7   64.2  110.3  90.0 119.5  78.8   -2  2 -2  0  0  0 -2  0  0 -2  0  0
    19        oI        336.9      64.2  110.3  194.6  90.0  77.2  90.0    0  0 -2  0  0 -2  0  0 -2  0 -2  0
    24        hR        507.2     198.1  191.0   64.2  93.1  74.3 120.0    1 -3  2  0  1  3  0  0  0  0  2  0
    43        mI        675.6     127.6  194.6  110.3  90.0 149.8  83.6    0 -2  2  0  2  0  2  0  0  2  0  0
    34        mP        739.1      64.2  110.3  110.2 120.0  95.5  90.0    0  0 -2  0  0 -2  0  0 -1  1  0  0
    33        mP        739.1      64.2  110.3  110.2 120.0  95.5  90.0    0  0 -2  0  0 -2  0  0 -1  1  0  0
    32        oP        820.7      64.2  110.2  110.3 120.0  90.0  95.5    0  0  2  0  1 -1  0  0  0  2  0  0
    21        tP        822.5     110.2  110.3   64.2  90.0  95.5 120.0    1 -1  0  0  0  2  0  0  0  0  2  0
    28        mC        863.2      64.2  223.7  110.2  62.3  95.5  78.8    0  0 -2  0 -2 -2 -2  0 -1  1  0  0
    29        mC        863.2      64.2  223.7  110.2  62.3  95.5  78.8    0  0  2  0  2 -2  2  0  1  1  0  0
    38        oC        907.6      64.2  223.7  110.3  60.5  90.0 101.2    0  0 -2  0  2 -2  2  0  0 -2  0  0
    36        oC        907.6      64.2  223.7  110.3  60.5  90.0 101.2    0  0 -2  0  2 -2  2  0  0 -2  0  0
    26        oF        947.4      64.2  223.7  223.7  59.1 101.2 101.2    0  0  2  0 -2  2 -2  0 -2 -2 -2  0
    18        tI        947.4     110.3  194.6   64.2  77.2  90.0  90.0    0 -2  0  0  2  0  2  0  0  0  2  0
     1        cF        999.0     127.6  127.6  194.6  96.4  96.4 119.6    0 -2  2  0  0  2  2  0 -2  0 -2  0
     2        hR        999.0     122.2  122.2  208.0 121.9  58.1 126.3    1 -1  2  0 -1 -1 -2  0  2  0 -2  0
     3        cP        999.0      64.2  110.3  110.2 120.0  95.5  90.0    0  0 -2  0  0 -2  0  0 -1  1  0  0
     5        cI        999.0     122.2  127.6  110.2  67.4  66.4  99.7   -1  1 -2  0  0 -2 -2  0 -1 -1  0  0
     4        hR        999.0     127.6  132.7  122.2  96.9  80.3  85.7    0  2 -2  0 -1  1  2  0  1  1  2  0
     6        tI        999.0     110.2  122.2  127.6  99.7  67.4  66.4    1 -1  0  0  1  1  2  0  0 -2  2  0
     7        tI        999.0     122.2  127.6  110.2  67.4  66.4  99.7    1  1  2  0  0 -2  2  0  1 -1  0  0
     8        oI        999.0     127.6  122.2  110.2  66.4  67.4  99.7    0  2 -2  0 -1 -1 -2  0 -1  1  0  0
     9        hR        999.0      64.2  122.2  294.1  76.9  98.5 116.1    0  0  2  0 -1  1 -2  0 -2 -4 -2  0
    10        mC        999.0     132.7  122.2  110.2  66.4 117.4 119.7   -1  1  2  0  1 -1  2  0  1  1  0  0
    11        tP        999.0      64.2  110.2  110.3 120.0  90.0  95.5    0  0  2  0  1 -1  0  0  0  2  0  0
    12        hP        999.0      64.2  110.2  110.3 120.0  90.0  95.5    0  0  2  0  1 -1  0  0  0  2  0  0
    13        oC        999.0     122.2  132.7  110.3 114.5 116.8  60.3    1 -1  2  0  1 -1 -2  0  0  2  0  0
    15        tI        999.0      64.2  110.3  194.6  90.0  77.2  90.0    0  0 -2  0  0 -2  0  0 -2  0 -2  0
    16        oF        999.0     127.6  127.6  194.6  83.6  96.4  60.4    0  2 -2  0  0  2  2  0  2  0  2  0
    14        mC        999.0     127.6  127.6  110.2 112.6 118.7  60.4    0 -2 -2  0  0 -2  2  0 -1  1  0  0
    17        mC        999.0     127.6  127.6  122.2  99.7 127.7  60.4    0  2  2  0  0  2 -2  0 -1 -1 -2  0

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

  *   0.00        0   20.0    2047    0.00  2  0  0  0  0  2  0  0  0  0  2  0

 ************ SELECTED SPACE GROUP AND UNIT CELL FOR THIS DATA SET ************

 SPACE_GROUP_NUMBER=    5
 UNIT_CELL_CONSTANTS=   190.87   110.28    64.22  90.000  96.300  90.000
 UNIT_CELL_A-AXIS=   162.885     5.530   -99.348
 UNIT_CELL_B-AXIS=    49.466    51.626    83.976
 UNIT_CELL_C-AXIS=    10.944   -56.583    28.339
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


 REFINED VALUES OF DIFFRACTION PARAMETERS DERIVED FROM      8991 INDEXED SPOTS
 REFINED PARAMETERS:   POSITION BEAM AXIS ORIENTATION CELL
 STANDARD DEVIATION OF SPOT    POSITION (PIXELS)     0.52
 STANDARD DEVIATION OF SPINDLE POSITION (DEGREES)    0.08
 SPACE GROUP NUMBER      5
 UNIT CELL PARAMETERS    190.952   110.297    64.278  90.000  96.293  90.000
 E.S.D. OF CELL PARAMETERS  2.3E-01 1.5E-01 8.5E-02 0.0E+00 2.7E-02 0.0E+00
 REC. CELL PARAMETERS   0.005269  0.009066  0.015652  90.000  83.707  90.000
 COORDINATES OF UNIT CELL A-AXIS   162.966     5.669   -99.361
 COORDINATES OF UNIT CELL B-AXIS    49.414    51.659    83.995
 COORDINATES OF UNIT CELL C-AXIS    11.002   -56.628    28.355
 CRYSTAL MOSAICITY (DEGREES)     0.118
 LAB COORDINATES OF ROTATION AXIS -0.999993  0.000417  0.003715
 DIRECT BEAM COORDINATES (REC. ANGSTROEM)   0.000204 -0.001703  1.021261
 DETECTOR COORDINATES (PIXELS) OF DIRECT BEAM    1246.62   1261.95
 DETECTOR ORIGIN (PIXELS) AT                     1246.02   1266.97
 CRYSTAL TO DETECTOR DISTANCE (mm)       517.07
 LAB COORDINATES OF DETECTOR X-AXIS  1.000000  0.000000  0.000000
 LAB COORDINATES OF DETECTOR Y-AXIS  0.000000  1.000000  0.000000


 THE DATA COLLECTION STATISTICS REPORTED BELOW ASSUMES:
 SPACE_GROUP_NUMBER=    5
 UNIT_CELL_CONSTANTS=   190.95   110.30    64.28  90.000  96.293  90.000


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
 -0.05  0.05      4341         33.001       1.063
  0.05  0.15      4256         34.700       1.011
  0.15  0.25      4379         35.245       0.996
  0.25  0.35      4338         35.084       1.000
  0.35  0.45      4399         36.889       0.951
  0.45  0.55      4451         35.903       0.977
  0.55  0.65      4405         33.381       1.051
  0.65  0.75      4364         34.474       1.018
  0.75  0.85      4265         36.036       0.974
  0.85  0.95      4319         36.204       0.969
 
 -0.05  0.95     43517         35.092       1.000
 

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

   43.737  21.742    28.76 103.40      6.86      1.56      46      58       0
   21.742  16.422    19.99   9.39      6.03      2.42      88      96       0
   16.422  13.735    19.80  17.10      8.07      2.32      97     114       0
   13.735  12.044    19.80  16.50      7.76      2.31      85     101       0
   12.044  10.855    19.92   9.98      6.94      2.38     118     144       0
   10.855   9.961    16.90  17.59     10.40      2.88     115     142       0
    9.961   9.256    16.40  16.25      9.47      2.86     151     184       0
    9.256   8.683    13.23  11.16     10.30      3.54     164     195       0
    8.683   8.204    10.63  11.86     13.05      4.69     180     210       0
    8.204   7.797    11.47   8.70     10.69      4.41     161     203       0
    7.797   7.445     8.46  13.30     15.71      6.28     180     230       0
    7.445   7.136     7.70   5.90     13.12      6.92     189     230       0
    7.136   6.864     7.35   4.92     13.66      7.20     158     212       0
    6.864   6.620     6.66   9.84     16.72      7.62     136     201       0
    6.620   6.400     6.29   3.82     16.78      9.83     191     245       0
    6.400   6.201     5.86   6.13     16.91      9.21     199     266       0
    6.201   6.019     5.26   5.79     16.47     10.72     190     254       0
    6.019   5.853     5.15   5.13     16.33     10.57     230     289       0
    5.853   5.699     5.28   2.67     14.33     11.52     215     294       0
    5.699   5.558     4.96   4.38     19.54     11.67     218     284       0
    5.558   5.426     5.50   5.43     17.38     10.75     249     338       0
    5.426   5.303     5.30   4.04     19.24     10.43     227     283       0
    5.303   5.188     5.13   3.16     16.45     10.81     272     368       0
    5.188   5.080     5.52   4.53     18.15      9.19     228     306       0
    5.080   4.979     5.54   6.36     19.96      9.88     275     367       0
    4.979   4.883     6.24   7.68     22.32      9.24     251     330       0
    4.883   4.793     6.31   9.62     21.95      8.23     271     366       0
    4.793   4.708     6.04   7.01     24.48     10.42     216     305       0
    4.708   4.627     6.59   8.78     22.52      8.71     199     301       0
    4.627   4.550     6.42   6.28     20.20      8.36     239     320       0
    4.550   4.477     5.71   4.40     21.10     10.96     253     372       0
    4.477   4.407     5.11   5.48     24.84     11.57     260     359       0
    4.407   4.340     4.92   4.92     23.18     11.57     264     375       0
    4.340   4.277     5.56   5.17     23.64     11.23     271     378       0
    4.277   4.216     5.02   7.19     25.23     11.39     272     379       0
    4.216   4.157     4.66   4.33     24.30     13.98     287     409       0
    4.157   4.101     4.65   5.74     25.93     13.56     290     400       0
    4.101   4.047     4.26   5.28     26.93     14.08     276     408       0
    4.047   3.996     3.99   4.40     27.94     17.78     290     413       0
    3.996   3.946     3.33   2.56     27.69     20.44     289     412       0
    3.946   3.898     3.22   2.98     27.45     18.71     301     442       0
    3.898   3.851     3.19   3.04     25.71     20.13     295     429       0
    3.851   3.807     2.68   2.60     29.64     23.22     319     448       0
    3.807   3.763     2.97   2.38     27.15     21.96     290     434       0
    3.763   3.722     2.22   1.46     35.44     35.06     327     475       0
    3.722   3.681     2.53   1.67     29.87     27.48     286     428       0
    3.681   3.642     2.46   1.98     32.28     30.07     353     506       0
    3.642   3.604     2.21   2.07     35.31     32.70     279     436       0
    3.604   3.568     2.30   1.95     32.41     32.22     299     427       0
    3.568   3.532     2.39   1.43     32.27     30.30     234     367       0
    3.532   3.497     2.08   1.94     36.56     33.09     272     433       0
    3.497   3.464     1.88   1.81     40.60     38.25     278     442       0
    3.464   3.431     1.75   1.44     38.07     40.11     311     463       0
    3.431   3.400     1.50   0.76     44.32     60.32     292     454       0
    3.400   3.369     1.39   0.68     44.28     60.16     339     488       0
    3.369   3.339     1.38   0.57     42.39     60.32     286     472       0
    3.339   3.309     1.39   0.90     44.06     57.93     303     471       0
    3.309   3.281     1.19   0.58     48.71     75.79     306     491       0
    3.281   3.253     1.08   0.54     51.43     79.42     344     506       0
    3.253   3.226     1.02   0.45     55.06     97.09     339     522       0
    3.226   3.200     1.02   0.60     50.95     80.26     331     511       0
    3.200   3.174     0.91   0.45     59.28     93.09     318     505       0
    3.174   3.149     0.85   0.42     56.19     97.33     331     527       0
    3.149   3.124     0.80   0.47     57.13     94.37     349     558       0
    3.124   3.100     0.82   0.30     61.76    123.84     328     516       0
    3.100   3.077     0.77   0.43     55.98     94.59     362     549       0
    3.077   3.054     0.63   0.28     70.80    145.90     348     541       0
    3.054   3.031     0.56   0.25     91.35    192.02     347     563       0
    3.031   3.009     0.53   0.33     82.39    154.27     365     563       0
    3.009   2.988     0.59   0.29     71.08    144.72     348     557       0
    2.988   2.967     0.52   0.37     90.48    162.48     340     554       0
    2.967   2.946     0.58   0.32     85.33    165.25     348     577       0
    2.946   2.926     0.45   0.34     94.17    186.69     394     589       0
    2.926   2.906     0.38   0.34    149.20    272.26     295     485       0
    2.906   2.887     0.49   0.30     99.57    184.37     288     502       0
    2.887   2.868     0.37   0.21     93.58    204.22     323     540       0
    2.868   2.849     0.41   0.28     91.37    192.41     307     533       0
    2.849   2.831     0.35   0.33    126.24    238.22     319     529       0
    2.831   2.813     0.40   0.28    114.43    217.31     335     567       0
    2.813   2.796     0.34   0.27    132.35    271.23     352     576       0
    2.796   2.779     0.38   0.20    126.87    297.12     315     520       0
    2.779   2.762     0.33   0.28    145.15    293.40     359     617       0
    2.762   2.745     0.32   0.26    144.38    291.64     349     611       0
    2.745   2.729     0.23   0.20    199.54    456.20     365     578       0
    2.729   2.713     0.21   0.23    219.43    479.06     337     578       0
    2.713   2.697     0.23   0.19    188.78    462.61     368     613       0
    2.697   2.681     0.21   0.22    203.29    462.41     367     610       0
    2.681   2.666     0.21   0.21    284.73    627.45     364     619       0
    2.666   2.651     0.23   0.22    187.69    414.18     349     604       0
    2.651   2.636     0.22   0.22    279.69    617.20     373     651       0
    2.636   2.622     0.16   0.19    269.70    645.27     376     638       0
    2.622   2.608     0.15   0.22    353.23    760.72     358     602       0
    2.608   2.594     0.17   0.17    187.46    456.12     411     671       0
    2.594   2.580     0.15   0.24    280.84    582.92     390     652       0
    2.580   2.566     0.17   0.20    235.32    519.61     321     583       0
    2.566   2.553     0.15   0.21    311.64    671.79     400     686       0
    2.553   2.540     0.17   0.20    239.07    545.27     391     659       0
    2.540   2.527     0.12   0.19    331.06    770.72     383     660       0
    2.527   2.514     0.08   0.22    399.83    877.10     399     656       0
    2.514   2.502     0.14   0.18    297.43    722.08     334     592       0
   --------------------------------------------------------------------------
   43.737   2.502     2.38   2.56     25.66     25.89   28380   43517       0
 


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
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       2      22
 ******************************************************************************


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

     7.41         362     308      1825       16.9%       4.8%      2.5%      108   19.28      6.8%    96.4*     0    0.000       0
     5.28         634     608      3146       19.3%       6.1%      4.3%       52    8.67      8.6%    99.1*     0    0.000       0
     4.32         803     787      4045       19.5%       7.2%      3.7%       32    8.48     10.2%    99.4*     0    0.000       0
     3.74         991     973      4742       20.5%       7.2%      7.2%       36    6.30     10.1%    97.2*     0    0.000       0
     3.35        1059    1032      5374       19.2%       8.5%      9.9%       54    3.70     12.0%    95.7*     0    0.000       0
     3.06        1206    1182      5919       20.0%      10.2%     12.4%       48    1.88     14.5%    95.7*     0    0.000       0
     2.84        1263    1239      6451       19.2%      19.7%     39.6%       48    1.05     27.8%    89.3*     0    0.000       0
     2.65        1402    1376      6928       19.9%      28.6%     68.5%       52    0.64     40.4%    74.1*     0    0.000       0
     2.50        1479    1450      7362       19.7%      82.0%    153.6%       58    0.34    115.9%    45.7      0    0.000       0
    total        9199    8955     45792       19.6%       6.8%      6.2%      488    3.65      9.6%    97.7*     0    0.000       0


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES      9199
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                         9199
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                   8955



 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       2      41
 ******************************************************************************


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

     7.41         689     486      1825       26.6%       3.8%      2.6%      401   20.83      5.4%    98.3*     0    0.000       0
     5.28        1199     943      3146       30.0%       6.8%      6.6%      506    8.98      9.5%    98.4*     0    0.000       0
     4.32        1542    1298      4045       32.1%       9.4%      6.6%      484    8.58     13.3%    96.7*     0    0.000       0
     3.74        1876    1648      4742       34.8%      11.0%      9.1%      456    5.99     15.5%    94.2*     0    0.000       0
     3.35        2006    1840      5374       34.2%      12.4%     16.5%      332    3.31     17.5%    95.7*     0    0.000       0
     3.06        2324    2185      5919       36.9%      17.7%     27.4%      278    1.62     25.0%    92.5*     0    0.000       0
     2.84        2431    2315      6451       35.9%      26.5%     43.1%      232    0.84     37.5%    85.7*     0    0.000       0
     2.65        2676    2565      6928       37.0%      36.0%     80.6%      222    0.51     50.9%    71.6*     0    0.000       0
     2.50        2848    2729      7362       37.1%      82.8%    163.4%      238    0.29    117.1%    30.7      0    0.000       0
    total       17591   16009     45792       35.0%       8.4%      8.4%     3149    3.33     11.8%    98.1*     0    0.000       0


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     17591
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        17591
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  16009



 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       2      61
 ******************************************************************************


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

     7.41        1033     655      1825       35.9%       4.6%      2.7%      739   21.11      6.4%    98.8*   -96    1.538       3
     5.28        1803    1234      3146       39.2%       9.1%      7.5%     1086    8.62     12.5%    97.3*   -68    0.582       5
     4.32        2314    1682      4045       41.6%      12.2%      7.4%     1221    8.36     16.9%    95.1*   -53    0.580       2
     3.74        2826    2132      4742       45.0%      15.3%     11.0%     1353    5.60     21.4%    91.7*     0    0.000       1
     3.35        3000    2360      5374       43.9%      21.1%     23.6%     1248    3.10     29.2%    88.7*     0    0.000       0
     3.06        3497    2821      5919       47.7%      30.2%     50.6%     1322    1.49     42.3%    82.1*     0    0.000       0
     2.84        3666    3042      6451       47.2%      49.1%     94.2%     1229    0.75     69.0%    70.8*     0    0.000       0
     2.65        4020    3412      6928       49.2%      89.3%    201.3%     1204    0.44    125.7%    40.2*     0    0.000       0
     2.50        4295    3699      7362       50.2%     142.0%    319.6%     1187    0.25    200.4%    16.0*     0    0.000       0
    total       26454   21037     45792       45.9%      13.6%     14.5%    10589    3.17     18.9%    97.6*   -69    0.806      11


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     26454
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        26454
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  21037



 ******************************************************************************
  SUMMARY OF DATA SET STATISTICS FOR IMAGE   DATA_RANGE=       2      80
 ******************************************************************************


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

     7.41        1362     805      1825       44.1%       6.7%      2.9%     1068   20.54      9.0%    97.9*   -86    1.162      14
     5.28        2367    1500      3146       47.7%      12.0%      8.5%     1625    8.07     16.4%    95.4*   -82    0.704      25
     4.32        3038    1995      4045       49.3%      16.1%      8.3%     1958    7.98     22.0%    92.0*   -73    1.235      14
     3.74        3729    2531      4742       53.4%      20.4%     13.8%     2258    5.20     27.7%    88.2*   -95    0.489      13
     3.35        3949    2773      5374       51.6%      28.6%     29.1%     2218    2.84     39.1%    81.9*   -81    0.723      13
     3.06        4606    3314      5919       56.0%      42.0%     67.6%     2459    1.36     57.8%    73.9*   -88    0.535       4
     2.84        4793    3548      6451       55.0%      70.0%    132.9%     2375    0.68     96.9%    60.0*   -55    0.299       5
     2.65        5280    3986      6928       57.5%     121.8%    266.8%     2459    0.40    168.1%    30.8*   -76    0.429       3
     2.50        5668    4338      7362       58.9%     210.7%    474.0%     2551    0.22    292.4%    13.0*   -93    0.244       2
    total       34792   24790     45792       54.1%      19.2%     19.9%    18971    3.03     26.2%    96.1*   -83    0.778      93


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     34792
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        34792
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  24790



 ******************************************************************************
  STATISTICS OF SAVED DATA SET "XDS_ASCII.HKL" (DATA_RANGE=       2     100)
 FILE TYPE:         XDS_ASCII      MERGE=FALSE          FRIEDEL'S_LAW=TRUE 
 ******************************************************************************

   REFLECTIONS OF TYPE H,0,0  0,K,0  0,0,L OR EXPECTED TO BE ABSENT (*)
   --------------------------------------------------------------------

   H    K    L  RESOLUTION  INTENSITY     SIGMA    INTENSITY/SIGMA  #OBSERVED

   32    0    0     5.931  -0.7436E+00  0.6288E+01        -0.12           1 
   34    0    0     5.582   0.3549E+03  0.1548E+02        22.93           1 
   36    0    0     5.272   0.9620E+02  0.9539E+01        10.09           1 
   38    0    0     4.995   0.6811E+02  0.9357E+01         7.28           1 
   40    0    0     4.745   0.8941E+03  0.2808E+02        31.84           1 
   42    0    0     4.519  -0.2613E+01  0.7745E+01        -0.34           1 
   44    0    0     4.314   0.1388E+04  0.3874E+02        35.84           1 
   46    0    0     4.126   0.4141E+03  0.1887E+02        21.95           1 
   48    0    0     3.954   0.1322E+02  0.9648E+01         1.37           1 
   50    0    0     3.796   0.1053E+02  0.1010E+02         1.04           1 
   52    0    0     3.650   0.1403E+03  0.1384E+02        10.14           1 
   54    0    0     3.515   0.3838E+02  0.1136E+02         3.38           1 
   56    0    0     3.389   0.2410E+02  0.1121E+02         2.15           1 
   60    0    0     3.163   0.4234E+01  0.1065E+02         0.40           1 
   62    0    0     3.061   0.6230E+02  0.1297E+02         4.81           1 
   64    0    0     2.966  -0.1369E+01  0.9723E+01        -0.14           1 
   66    0    0     2.876   0.2181E+01  0.1087E+02         0.20           1 
   68    0    0     2.791  -0.9839E+00  0.1071E+02        -0.09           1 
   70    0    0     2.711   0.4714E+00  0.9789E+01         0.05           1 
   72    0    0     2.636   0.4173E+01  0.1062E+02         0.39           1 
   74    0    0     2.565   0.2944E+01  0.1083E+02         0.27           1 

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

     7.41        1703     947      1825       51.9%       9.5%      3.2%     1407   19.71     12.5%    97.1*   -91    1.055      32
     5.28        2950    1723      3146       54.8%      16.5%      9.8%     2236    7.49     22.0%    92.2*   -82    0.805      56
     4.32        3811    2295      4045       56.7%      21.4%      9.7%     2753    7.34     28.6%    88.1*   -85    0.866      55
     3.74        4651    2860      4742       60.3%      26.7%     17.0%     3264    4.78     35.5%    83.5*   -88    0.600      64
     3.35        4928    3140      5374       58.4%      35.7%     36.9%     3238    2.58     47.7%    77.8*   -83    0.567      48
     3.06        5761    3747      5919       63.3%      53.5%     87.3%     3701    1.24     72.4%    68.3*   -68    0.408      42
     2.84        6030    3996      6451       61.9%      92.7%    181.5%     3708    0.62    125.7%    53.9*   -60    0.362      35
     2.65        6560    4442      6928       64.1%     161.6%    349.5%     3893    0.36    219.8%    22.4*   -36    0.442      36
     2.50        7123    4854      7362       65.9%     276.6%    623.9%     4180    0.19    376.9%     9.5    -11    0.287      25
    total       43517   28004     45792       61.2%      25.7%     25.9%    28380    2.85     34.4%    94.2*   -83    0.623     393


 NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES     43517
 NUMBER OF REJECTED MISFITS                                 0
 NUMBER OF SYSTEMATIC ABSENT REFLECTIONS                    0
 NUMBER OF ACCEPTED OBSERVATIONS                        43517
 NUMBER OF UNIQUE ACCEPTED REFLECTIONS                  28004



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

   WILSON LINE (using all data) : A=   5.015 B=  61.847 CORRELATION=  0.98
      #      RES      SS        <I>       log(<I>)       BO
     296    13.725   0.001  1.3478E+02       4.904      42.0
     571     8.662   0.003  8.6232E+01       4.457      83.7
     699     6.806   0.005  4.0303E+01       3.696     122.2
     905     5.769   0.008  3.4801E+01       3.550      97.5
    1038     5.101   0.010  4.1310E+01       3.721      67.4
    1046     4.628   0.012  5.0639E+01       3.925      46.7
    1245     4.262   0.014  4.4240E+01       3.790      44.5
    1387     3.969   0.016  3.1676E+01       3.456      49.1
    1493     3.730   0.018  2.2221E+01       3.101      53.3
    1415     3.530   0.020  1.8047E+01       2.893      52.9
    1632     3.359   0.022  1.2115E+01       2.494      56.9
    1752     3.211   0.024  8.2752E+00       2.113      59.8
    1882     3.081   0.026  5.5889E+00       1.721      62.5
    1921     2.966   0.028  4.0813E+00       1.406      63.5
    1894     2.861   0.031  3.0185E+00       1.105      64.0
    2049     2.768   0.033  2.5145E+00       0.922      62.7
    2179     2.683   0.035  1.6132E+00       0.478      65.3
    2280     2.606   0.037  1.3500E+00       0.300      64.1
    2320     2.536   0.039  1.1044E+00       0.099      63.2


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF  CENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         3<I>**2     15<I>**3    105<I>**4 

      23    13.725        1.124        1.008        0.702
      26     8.662        6.343       21.051       54.910
      28     6.806        0.971        0.895        0.722
      32     5.769        0.742        0.550        0.331
      29     5.101        0.194        0.059        0.014
      32     4.628        2.035        2.990        3.478
      32     4.262        4.001        9.448       19.101
      31     3.969        1.343        2.268        3.052
      32     3.730        0.308        0.159        0.066
      31     3.530        2.759        4.570        6.479
      35     3.359        0.361        0.154        0.053
      34     3.211        1.052        1.344        1.470
      32     3.081        1.062        1.032        0.851
      40     2.966        1.184        1.359        1.676
      31     2.861        0.976        0.220        0.400
      41     2.768        0.621        0.165        0.089
      38     2.683        3.761        9.472       22.753
      38     2.606        2.172        1.092        1.147
     627   overall        1.755        2.799        5.780


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF ACENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         2<I>**2      6<I>**3     24<I>**4 

     273    13.725        1.198        1.624        2.247
     545     8.662        1.012        1.060        1.062
     671     6.806        1.280        1.827        2.744
     873     5.769        1.363        2.267        4.322
    1009     5.101        1.231        1.588        2.056
    1014     4.628        1.215        1.638        2.256
    1213     4.262        1.354        2.353        4.597
    1356     3.969        1.377        2.016        2.886
    1461     3.730        1.433        2.232        3.616
    1384     3.530        1.558        2.753        4.747
    1597     3.359        1.608        2.883        5.324
    1718     3.211        1.691        3.038        5.522
    1850     3.081        1.980        4.583       12.489
    1881     2.966        2.379        5.949       17.168
    1863     2.861        2.155        3.987        9.881
    2008     2.768        3.109       11.560       67.836
    2141     2.683        3.944        7.431       22.379
    2242     2.606        4.698        8.852       30.316
    2278     2.536        6.008        9.068       34.989
   27377   overall        2.546        4.993       16.660

   ======= CUMULATIVE INTENSITY DISTRIBUTION =======
 DEFINITIONS:
   <I>    = mean reflection intensity
 Na(Z)exp = expected number of acentric reflections with I <= Z*<I>
 Na(Z)obs = observed number of acentric reflections with I <= Z*<I>
 Nc(Z)exp = expected number of  centric reflections with I <= Z*<I>
 Nc(Z)obs = observed number of  centric reflections with I <= Z*<I>



 Nc(Z)obs/Nc(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

      23    13.725  0.70  0.75  0.63  0.92  1.00  0.93  0.95  1.04  1.06  1.08
      26     8.662  1.24  1.22  1.02  0.98  0.96  1.03  0.97  0.92  0.94  0.96
      28     6.806  0.58  0.72  0.77  1.06  1.10  1.08  1.14  1.08  1.09  1.10
      32     5.769  1.13  0.99  1.28  1.12  1.20  1.17  1.15  1.24  1.19  1.15
      29     5.101  1.94  1.40  1.41  1.38  1.39  1.35  1.27  1.21  1.21  1.16
      32     4.628  0.88  1.18  1.20  1.19  1.08  1.06  1.10  1.04  1.00  0.96
      32     4.262  1.13  1.08  1.05  0.92  0.90  1.00  0.94  0.89  0.95  0.96
      31     3.969  1.82  1.68  1.70  1.57  1.43  1.32  1.24  1.23  1.18  1.18
      32     3.730  1.26  1.36  1.35  1.32  1.38  1.34  1.36  1.29  1.33  1.28
      31     3.530  1.04  1.12  1.01  1.09  1.05  0.98  0.92  0.87  0.83  0.85
      35     3.359  1.84  1.49  1.30  1.21  1.15  1.07  1.15  1.18  1.13  1.17
      34     3.211  2.01  1.62  1.41  1.37  1.30  1.26  1.28  1.22  1.25  1.25
      32     3.081  1.51  1.08  1.05  0.92  0.96  0.89  1.10  1.04  1.00  0.96
      40     2.966  1.41  1.08  0.90  0.85  0.77  0.94  0.96  0.99  0.95  1.03
      31     2.861  0.91  0.75  0.62  0.68  0.74  0.75  0.81  0.82  0.88  0.99
      41     2.768  1.87  1.34  1.23  1.13  1.03  1.00  0.98  1.01  0.97  0.97
      38     2.683  2.01  1.52  1.26  1.17  1.11  1.08  1.01  1.00  1.00  0.96
      38     2.606  1.48  1.07  1.01  0.95  0.91  0.84  0.79  0.80  0.76  0.77
     627   overall  1.32  1.13  1.06  1.03  1.00  0.99  0.99  0.98  0.97  0.97


 Na(Z)obs/Na(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

     273    13.725  0.89  1.03  1.10  1.10  1.13  1.10  1.13  1.11  1.09  1.07
     545     8.662  1.33  1.25  1.20  1.16  1.14  1.09  1.07  1.07  1.04  1.03
     671     6.806  1.38  1.38  1.35  1.25  1.21  1.17  1.15  1.11  1.09  1.07
     873     5.769  1.52  1.38  1.32  1.24  1.20  1.15  1.12  1.10  1.08  1.07
    1009     5.101  1.35  1.27  1.24  1.16  1.13  1.11  1.10  1.09  1.07  1.05
    1014     4.628  1.21  1.29  1.24  1.19  1.18  1.15  1.12  1.08  1.06  1.05
    1213     4.262  1.52  1.41  1.38  1.31  1.26  1.21  1.16  1.13  1.10  1.07
    1356     3.969  1.68  1.55  1.42  1.32  1.26  1.20  1.16  1.12  1.09  1.08
    1461     3.730  1.61  1.42  1.37  1.33  1.29  1.25  1.21  1.16  1.12  1.09
    1384     3.530  2.05  1.66  1.51  1.38  1.29  1.23  1.17  1.16  1.13  1.10
    1597     3.359  2.12  1.54  1.36  1.27  1.22  1.18  1.16  1.13  1.11  1.08
    1718     3.211  2.35  1.57  1.32  1.22  1.18  1.16  1.13  1.11  1.09  1.07
    1850     3.081  2.87  1.76  1.41  1.26  1.16  1.12  1.09  1.05  1.04  1.03
    1881     2.966  3.02  1.79  1.43  1.26  1.17  1.11  1.09  1.05  1.03  1.01
    1863     2.861  3.12  1.80  1.37  1.19  1.08  1.02  0.98  0.95  0.93  0.93
    2008     2.768  3.47  1.97  1.49  1.27  1.13  1.04  0.99  0.96  0.94  0.91
    2141     2.683  3.89  2.15  1.60  1.30  1.15  1.04  0.96  0.91  0.88  0.86
    2242     2.606  4.01  2.21  1.62  1.33  1.15  1.04  0.96  0.92  0.88  0.85
    2278     2.536  4.11  2.25  1.63  1.32  1.13  1.01  0.94  0.87  0.84  0.80
   27377   overall  2.67  1.74  1.43  1.27  1.18  1.11  1.07  1.03  1.01  0.99


 List of    120 reflections *NOT* obeying Wilson distribution (Z> 10.0)

   h    k    l     RES      Z     Intensity    Sigma

   66    2    3    2.81   33.99  0.1710E+03  0.1486E+02 "alien"
   36   32   -7    2.80   32.72  0.1646E+03  0.2460E+02 "alien"
    3   41    8    2.54   26.64  0.5885E+02  0.1849E+02 "alien"
   71    1    3    2.62   24.00  0.6479E+02  0.1229E+02 "alien"
   30   34   -7    2.79   23.72  0.1193E+03  0.2402E+02 "alien"
   44   30    5    2.69   21.25  0.6854E+02  0.1061E+02 "alien"
   29   33    6    2.83   20.48  0.1236E+03  0.1628E+02 "alien"
   14   32    7    3.11   20.42  0.2283E+03  0.2221E+02 "alien"
   51   27   -9    2.64   20.29  0.5480E+02  0.1953E+02 "alien"
   49   23   -6    2.97   20.19  0.1648E+03  0.2356E+02 "alien"
   38   34   -7    2.65   20.03  0.6462E+02  0.2094E+02 "alien"
   69    9   -3    2.70   19.26  0.6214E+02  0.1627E+02 "alien"
   69    5    4    2.64   18.73  0.5058E+02  0.9608E+01 "alien"
   72   14   -2    2.51   17.55  0.3876E+02  0.1646E+02 "alien"
   26   32    6    2.95   17.45  0.1425E+03  0.1729E+02 "alien"
   67    9    5    2.64   17.42  0.4703E+02  0.6910E+01 "alien"
   31   33    6    2.79   17.25  0.8675E+02  0.1450E+02 "alien"
   50   32   -6    2.52   17.01  0.3757E+02  0.1836E+02 "alien"
    5   37   11    2.64   16.64  0.4494E+02  0.1631E+02 "alien"
   62   24   -4    2.55   16.51  0.3648E+02  0.1699E+02 "alien"
    5   41   -8    2.55   16.33  0.3607E+02  0.1730E+02 "alien"
   34   32    6    2.79   16.23  0.8161E+02  0.1429E+02 "alien"
   41   23    6    3.11   16.11  0.1800E+03  0.1180E+02 "alien"
   62    8   -4    3.00   15.89  0.1297E+03  0.1208E+02 "alien"
   37   35   -8    2.59   15.66  0.4228E+02  0.2028E+02 "alien"
   42   32   -8    2.65   15.42  0.4977E+02  0.1865E+02 "alien"
   59   11   -2    3.08   15.41  0.1723E+03  0.2040E+02 "alien"
   42   32   -7    2.67   15.10  0.4870E+02  0.2004E+02 "alien"
   38   28    5    2.96   15.03  0.1227E+03  0.1307E+02 "alien"
   65    9   -2    2.86   14.42  0.8707E+02  0.1662E+02 "alien"
    9   35    7    2.94   14.08  0.1150E+03  0.1982E+02 "alien"
   10   34    7    3.00   14.06  0.1147E+03  0.1962E+02 "alien"
   37   35   -7    2.62   13.90  0.3752E+02  0.1839E+02 "alien"
   30   30    6    3.00   13.84  0.1130E+03  0.1565E+02 "alien"
   63    1    0    3.01   13.32  0.1087E+03  0.1023E+02 "alien"
   61    1    1    3.09   13.24  0.1480E+03  0.1082E+02 "alien"
   71    3    3    2.61   13.24  0.3574E+02  0.1017E+02 "alien"
   69   15   -2    2.59   13.13  0.3546E+02  0.1638E+02 "alien"
   16   14   -6    5.74   12.81  0.8914E+03  0.2411E+02 "alien"
   25   29   -7    3.24   12.79  0.2117E+03  0.2487E+02 "alien"
   18   22    5    4.21   12.77  0.1130E+04  0.3610E+02 "alien"
   50    2    0    3.79   12.69  0.5641E+03  0.2524E+02 "alien"
   68   10   -3    2.72   12.61  0.4069E+02  0.1482E+02 "alien"
   13   15   -6    5.72   12.60  0.8771E+03  0.3349E+02 "alien"
   64    4    0    2.95   12.60  0.1028E+03  0.1001E+02 "alien"
   36   26    4    3.19   12.53  0.2073E+03  0.1514E+02 "alien"
   32   24    6    3.37   12.52  0.3033E+03  0.1831E+02 "alien"
   20   28    6    3.40   12.42  0.3009E+03  0.2153E+02 "alien"
   23   21    5    4.11   12.38  0.1096E+04  0.3393E+02 "alien"
   29   35  -10    2.64   12.36  0.3338E+02  0.1876E+02 "alien"
   51   29   -8    2.59   12.30  0.3320E+02  0.2019E+02 "alien"
   59   11   -3    3.08   12.24  0.1368E+03  0.1139E+02 "alien"
   20   40   -9    2.51   12.23  0.2701E+02  0.2012E+02 "alien"
   64    4   -1    2.96   12.16  0.9923E+02  0.1026E+02 "alien"
   14   40  -10    2.51   12.06  0.2663E+02  0.1851E+02 "alien"
   70   10   -9    2.56   12.04  0.2659E+02  0.1766E+02 "alien"
   31    7  -24    2.51   11.96  0.2642E+02  0.2264E+02 "alien"
   33   33   -7    2.80   11.91  0.5990E+02  0.1969E+02 "alien"
   20   34    9    2.78   11.85  0.5959E+02  0.1572E+02 "alien"
   61    1    0    3.11   11.82  0.1321E+03  0.1546E+02 "alien"
   35   31    6    2.82   11.81  0.7130E+02  0.1330E+02 "alien"
   27   37   -8    2.63   11.79  0.3183E+02  0.1859E+02 "alien"
   28   10  -24    2.51   11.75  0.2595E+02  0.2170E+02 "alien"
   54    4    2    3.43   11.68  0.2830E+03  0.1504E+02 "alien"
   27   35    7    2.71   11.59  0.3740E+02  0.1385E+02 "alien"
   16   36    7    2.80   11.57  0.5817E+02  0.1659E+02 "alien"
   69    1    1    2.73   11.50  0.5784E+02  0.8748E+01 "alien"
   44   32  -11    2.51   11.49  0.2538E+02  0.1955E+02 "alien"
    5   13  -24    2.55   11.44  0.2527E+02  0.2054E+02 "alien"
   40   34   -7    2.61   11.29  0.3047E+02  0.2057E+02 "alien"
   15   37    7    2.75   11.23  0.5647E+02  0.1665E+02 "alien"
    1   41    8    2.55   11.15  0.2463E+02  0.1623E+02 "alien"
   19   33    8    2.91   11.13  0.6720E+02  0.1656E+02 "alien"
   29   25   -8    3.41   11.08  0.2684E+03  0.2723E+02 "alien"
   21    7   -3    7.60   11.05  0.8910E+03  0.2877E+02 "alien"
   72   14   -3    2.51   11.05  0.2441E+02  0.1500E+02 "alien"
   38   30  -11    2.71   10.94  0.3531E+02  0.1952E+02 "alien"
   56   26   -5    2.64   10.94  0.2954E+02  0.1831E+02 "alien"
   18   38    8    2.62   10.93  0.2950E+02  0.1467E+02 "alien"
   40   16   -9    3.56   10.92  0.3943E+03  0.2253E+02 "alien"
    8   14  -24    2.54   10.92  0.2413E+02  0.2009E+02 "alien"
   14   40    7    2.58   10.91  0.2946E+02  0.1561E+02 "alien"
   73    9   -2    2.56   10.90  0.2408E+02  0.8282E+01 "alien"
   59   23  -10    2.55   10.90  0.2407E+02  0.1980E+02 "alien"
   74    2   -2    2.58   10.89  0.2940E+02  0.9243E+01 "alien"
   43   13   -6    3.80   10.89  0.4839E+03  0.2941E+02 "alien"
   32   12  -23    2.53   10.89  0.2405E+02  0.2170E+02 "alien"
   16   36  -10    2.72   10.83  0.3495E+02  0.1815E+02 "alien"
   33   35    8    2.57   10.83  0.2923E+02  0.1273E+02 "alien"
   51   27  -12    2.53   10.81  0.2388E+02  0.1911E+02 "alien"
   41    7   -4    4.40   10.76  0.9520E+03  0.2312E+02 "alien"
   43   31    4    2.70   10.71  0.3454E+02  0.9752E+01 "alien"
   21   39    8    2.53   10.63  0.2348E+02  0.1418E+02 "alien"
   47   25   -7    2.90   10.62  0.6414E+02  0.1908E+02 "alien"
   50   30  -10    2.51   10.56  0.2333E+02  0.2006E+02 "alien"
   34   34    5    2.71   10.55  0.3404E+02  0.1189E+02 "alien"
   34   36   -8    2.59   10.52  0.2839E+02  0.2024E+02 "alien"
   39   31  -11    2.64   10.50  0.2835E+02  0.1822E+02 "alien"
   41    1   -4    4.58   10.49  0.1063E+04  0.1724E+02 "alien"
   18   38  -12    2.51   10.42  0.2302E+02  0.1728E+02 "alien"
   73    9   -3    2.56   10.41  0.2299E+02  0.1447E+02 "alien"
   24   20    5    4.18   10.39  0.9196E+03  0.2904E+02 "alien"
   69    9   -2    2.70   10.37  0.3345E+02  0.1483E+02 "alien"
   21   39   -8    2.58   10.36  0.2798E+02  0.1838E+02 "alien"
   69    5    2    2.69   10.36  0.3341E+02  0.8871E+01 "alien"
   69   17   -2    2.54   10.31  0.2276E+02  0.1442E+02 "alien"
    8   38    8    2.70   10.28  0.3318E+02  0.1599E+02 "alien"
    1   39   -8    2.67   10.25  0.3308E+02  0.1679E+02 "alien"
   54   28   -6    2.60   10.19  0.2750E+02  0.1753E+02 "alien"
   60    2    0    3.16   10.16  0.1682E+03  0.1123E+02 "alien"
   41   35   -7    2.55   10.15  0.2243E+02  0.1986E+02 "alien"
   13   25   -6    3.97   10.15  0.6432E+03  0.3364E+02 "alien"
   23   27   -8    3.39   10.14  0.2457E+03  0.2724E+02 "alien"
   62   20  -10    2.56   10.13  0.2238E+02  0.1707E+02 "alien"
    8   36   12    2.62   10.12  0.2731E+02  0.1679E+02 "alien"
   69    3    2    2.71   10.10  0.3257E+02  0.1010E+02 "alien"
   42   22    3    3.28   10.05  0.1664E+03  0.1019E+02 "alien"
   26   30   10    2.86   10.03  0.6053E+02  0.1516E+02 "alien"
   14   38  -10    2.62   10.00  0.2700E+02  0.1743E+02 "alien"
   24   24    7    3.57   10.00  0.3610E+03  0.2110E+02 "alien"


 List of    120 reflections *NOT* obeying Wilson distribution (sorted by resolution)
 Ice rings could occur at (Angstrom):
 3.897,3.669,3.441, 2.671,2.249,2.072, 1.948,1.918,1.883,1.721

   h    k    l     RES      Z     Intensity    Sigma

   20   40   -9    2.51   12.23  0.2701E+02  0.2012E+02
   18   38  -12    2.51   10.42  0.2302E+02  0.1728E+02
   28   10  -24    2.51   11.75  0.2595E+02  0.2170E+02
   14   40  -10    2.51   12.06  0.2663E+02  0.1851E+02
   50   30  -10    2.51   10.56  0.2333E+02  0.2006E+02
   44   32  -11    2.51   11.49  0.2538E+02  0.1955E+02
   72   14   -2    2.51   17.55  0.3876E+02  0.1646E+02
   31    7  -24    2.51   11.96  0.2642E+02  0.2264E+02
   72   14   -3    2.51   11.05  0.2441E+02  0.1500E+02
   50   32   -6    2.52   17.01  0.3757E+02  0.1836E+02
   32   12  -23    2.53   10.89  0.2405E+02  0.2170E+02
   51   27  -12    2.53   10.81  0.2388E+02  0.1911E+02
   21   39    8    2.53   10.63  0.2348E+02  0.1418E+02
    8   14  -24    2.54   10.92  0.2413E+02  0.2009E+02
    3   41    8    2.54   26.64  0.5885E+02  0.1849E+02
   69   17   -2    2.54   10.31  0.2276E+02  0.1442E+02
   41   35   -7    2.55   10.15  0.2243E+02  0.1986E+02
    1   41    8    2.55   11.15  0.2463E+02  0.1623E+02
   59   23  -10    2.55   10.90  0.2407E+02  0.1980E+02
    5   41   -8    2.55   16.33  0.3607E+02  0.1730E+02
    5   13  -24    2.55   11.44  0.2527E+02  0.2054E+02
   62   24   -4    2.55   16.51  0.3648E+02  0.1699E+02
   73    9   -2    2.56   10.90  0.2408E+02  0.8282E+01
   62   20  -10    2.56   10.13  0.2238E+02  0.1707E+02
   73    9   -3    2.56   10.41  0.2299E+02  0.1447E+02
   70   10   -9    2.56   12.04  0.2659E+02  0.1766E+02
   33   35    8    2.57   10.83  0.2923E+02  0.1273E+02
   14   40    7    2.58   10.91  0.2946E+02  0.1561E+02
   74    2   -2    2.58   10.89  0.2940E+02  0.9243E+01
   21   39   -8    2.58   10.36  0.2798E+02  0.1838E+02
   51   29   -8    2.59   12.30  0.3320E+02  0.2019E+02
   34   36   -8    2.59   10.52  0.2839E+02  0.2024E+02
   69   15   -2    2.59   13.13  0.3546E+02  0.1638E+02
   37   35   -8    2.59   15.66  0.4228E+02  0.2028E+02
   54   28   -6    2.60   10.19  0.2750E+02  0.1753E+02
   71    3    3    2.61   13.24  0.3574E+02  0.1017E+02
   40   34   -7    2.61   11.29  0.3047E+02  0.2057E+02
   14   38  -10    2.62   10.00  0.2700E+02  0.1743E+02
   71    1    3    2.62   24.00  0.6479E+02  0.1229E+02
   37   35   -7    2.62   13.90  0.3752E+02  0.1839E+02
   18   38    8    2.62   10.93  0.2950E+02  0.1467E+02
    8   36   12    2.62   10.12  0.2731E+02  0.1679E+02
   27   37   -8    2.63   11.79  0.3183E+02  0.1859E+02
    5   37   11    2.64   16.64  0.4494E+02  0.1631E+02
   56   26   -5    2.64   10.94  0.2954E+02  0.1831E+02
   51   27   -9    2.64   20.29  0.5480E+02  0.1953E+02
   67    9    5    2.64   17.42  0.4703E+02  0.6910E+01
   29   35  -10    2.64   12.36  0.3338E+02  0.1876E+02
   69    5    4    2.64   18.73  0.5058E+02  0.9608E+01
   39   31  -11    2.64   10.50  0.2835E+02  0.1822E+02
   42   32   -8    2.65   15.42  0.4977E+02  0.1865E+02
   38   34   -7    2.65   20.03  0.6462E+02  0.2094E+02
    1   39   -8    2.67   10.25  0.3308E+02  0.1679E+02
   42   32   -7    2.67   15.10  0.4870E+02  0.2004E+02
   44   30    5    2.69   21.25  0.6854E+02  0.1061E+02
   69    5    2    2.69   10.36  0.3341E+02  0.8871E+01
   43   31    4    2.70   10.71  0.3454E+02  0.9752E+01
    8   38    8    2.70   10.28  0.3318E+02  0.1599E+02
   69    9   -2    2.70   10.37  0.3345E+02  0.1483E+02
   69    9   -3    2.70   19.26  0.6214E+02  0.1627E+02
   69    3    2    2.71   10.10  0.3257E+02  0.1010E+02
   27   35    7    2.71   11.59  0.3740E+02  0.1385E+02
   34   34    5    2.71   10.55  0.3404E+02  0.1189E+02
   38   30  -11    2.71   10.94  0.3531E+02  0.1952E+02
   16   36  -10    2.72   10.83  0.3495E+02  0.1815E+02
   68   10   -3    2.72   12.61  0.4069E+02  0.1482E+02
   69    1    1    2.73   11.50  0.5784E+02  0.8748E+01
   15   37    7    2.75   11.23  0.5647E+02  0.1665E+02
   20   34    9    2.78   11.85  0.5959E+02  0.1572E+02
   34   32    6    2.79   16.23  0.8161E+02  0.1429E+02
   31   33    6    2.79   17.25  0.8675E+02  0.1450E+02
   30   34   -7    2.79   23.72  0.1193E+03  0.2402E+02
   16   36    7    2.80   11.57  0.5817E+02  0.1659E+02
   36   32   -7    2.80   32.72  0.1646E+03  0.2460E+02
   33   33   -7    2.80   11.91  0.5990E+02  0.1969E+02
   66    2    3    2.81   33.99  0.1710E+03  0.1486E+02
   35   31    6    2.82   11.81  0.7130E+02  0.1330E+02
   29   33    6    2.83   20.48  0.1236E+03  0.1628E+02
   65    9   -2    2.86   14.42  0.8707E+02  0.1662E+02
   26   30   10    2.86   10.03  0.6053E+02  0.1516E+02
   47   25   -7    2.90   10.62  0.6414E+02  0.1908E+02
   19   33    8    2.91   11.13  0.6720E+02  0.1656E+02
    9   35    7    2.94   14.08  0.1150E+03  0.1982E+02
   64    4    0    2.95   12.60  0.1028E+03  0.1001E+02
   26   32    6    2.95   17.45  0.1425E+03  0.1729E+02
   64    4   -1    2.96   12.16  0.9923E+02  0.1026E+02
   38   28    5    2.96   15.03  0.1227E+03  0.1307E+02
   49   23   -6    2.97   20.19  0.1648E+03  0.2356E+02
   62    8   -4    3.00   15.89  0.1297E+03  0.1208E+02
   10   34    7    3.00   14.06  0.1147E+03  0.1962E+02
   30   30    6    3.00   13.84  0.1130E+03  0.1565E+02
   63    1    0    3.01   13.32  0.1087E+03  0.1023E+02
   59   11   -3    3.08   12.24  0.1368E+03  0.1139E+02
   59   11   -2    3.08   15.41  0.1723E+03  0.2040E+02
   61    1    1    3.09   13.24  0.1480E+03  0.1082E+02
   41   23    6    3.11   16.11  0.1800E+03  0.1180E+02
   14   32    7    3.11   20.42  0.2283E+03  0.2221E+02
   61    1    0    3.11   11.82  0.1321E+03  0.1546E+02
   60    2    0    3.16   10.16  0.1682E+03  0.1123E+02
   36   26    4    3.19   12.53  0.2073E+03  0.1514E+02
   25   29   -7    3.24   12.79  0.2117E+03  0.2487E+02
   42   22    3    3.28   10.05  0.1664E+03  0.1019E+02
   32   24    6    3.37   12.52  0.3033E+03  0.1831E+02
   23   27   -8    3.39   10.14  0.2457E+03  0.2724E+02
   20   28    6    3.40   12.42  0.3009E+03  0.2153E+02
   29   25   -8    3.41   11.08  0.2684E+03  0.2723E+02
   54    4    2    3.43   11.68  0.2830E+03  0.1504E+02
   40   16   -9    3.56   10.92  0.3943E+03  0.2253E+02
   24   24    7    3.57   10.00  0.3610E+03  0.2110E+02
   50    2    0    3.79   12.69  0.5641E+03  0.2524E+02
   43   13   -6    3.80   10.89  0.4839E+03  0.2941E+02
   13   25   -6    3.97   10.15  0.6432E+03  0.3364E+02
   23   21    5    4.11   12.38  0.1096E+04  0.3393E+02
   24   20    5    4.18   10.39  0.9196E+03  0.2904E+02
   18   22    5    4.21   12.77  0.1130E+04  0.3610E+02
   41    7   -4    4.40   10.76  0.9520E+03  0.2312E+02
   41    1   -4    4.58   10.49  0.1063E+04  0.1724E+02
   13   15   -6    5.72   12.60  0.8771E+03  0.3349E+02
   16   14   -6    5.74   12.81  0.8914E+03  0.2411E+02
   21    7   -3    7.60   11.05  0.8910E+03  0.2877E+02

 NUMBER OF UNIQUE ALIEN REFLECTIONS WITH A Z-SCORE ABOVE LIMIT        11
 (ALIENS ABOVE LIMIT (REJECT_ALIEN=      20.0) ARE MARKED INVALID)

 NUMBER OF REFLECTION RECORDS ON OUTPUT FILE "XDS_ASCII.HKL"       43517
 NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES)   43506
 NUMBER OF REJECTED MISFITS & ALIENS (marked by -1*SIGMA(IOBS))       11


 cpu time used                  6.1 sec
 elapsed wall-clock time        3.7 sec

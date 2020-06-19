
 ***** XSCALE ***** (VERSION Jan 31, 2020  BUILT=20200417)  12-May-2020
 Author: Wolfgang Kabsch
 Copy licensed until 31-Mar-2021 to
  academic users for non-commercial applications   
 No redistribution.


 ******************************************************************************
                              CONTROL CARDS
 ******************************************************************************

 OUTPUT_FILE=temp.ahkl
 INPUT_FILE=../2-140/XDS_ASCII.HKL
 INPUT_FILE=../1-60/XDS_ASCII.HKL

 THE DATA COLLECTION STATISTICS REPORTED BELOW ASSUMES:
 SPACE_GROUP_NUMBER=    5
 UNIT_CELL_CONSTANTS=   190.95   110.30    64.28  90.000  96.293  90.000

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
 

 ALL DATA SETS WILL BE SCALED TO ../2-140/XDS_ASCII.HKL                                                                                                  


 ******************************************************************************
                    READING INPUT REFLECTION DATA FILES
 ******************************************************************************

 DATA    MEAN       REFLECTIONS        INPUT FILE NAME
 SET# INTENSITY  ACCEPTED REJECTED
   1  0.3622E+02    43502      0  ../2-140/XDS_ASCII.HKL
   2  0.4907E+02    21976      0  ../1-60/XDS_ASCII.HKL


 ******************************************************************************
                OVERALL SCALING AND CRYSTAL DISORDER CORRECTION
 ******************************************************************************

      CORRELATIONS BETWEEN INPUT DATA SETS AFTER CORRECTIONS

 DATA SETS  NUMBER OF COMMON  CORRELATION   RATIO OF COMMON   B-FACTOR
  #i   #j     REFLECTIONS     BETWEEN i,j  INTENSITIES (i/j)  BETWEEN i,j

    1    2       13428           0.996            1.1431        -2.7678


 K*EXP(B*SS) = Factor applied to intensities
    SS       = (2sin(theta)/lambda)^2

      K        B           DATA SET NAME
  1.000E+00   0.000    ../2-140/XDS_ASCII.HKL
  1.144E+00  -2.768    ../1-60/XDS_ASCII.HKL

 ******************************************************************************
           CORRECTION FACTORS AS FUNCTION OF IMAGE NUMBER & RESOLUTION
 ******************************************************************************

 RECIPROCAL CORRECTION FACTORS FOR INPUT DATA SETS MERGED TO
 OUTPUT FILE: temp.ahkl                                         

 THE CALCULATIONS ASSUME         FRIEDEL'S_LAW= TRUE
 TOTAL NUMBER OF CORRECTION FACTORS DEFINED      300
 DEGREES OF FREEDOM OF CHI^2 FIT             25496.0
 CHI^2-VALUE OF FIT OF CORRECTION FACTORS      0.856
 NUMBER OF CYCLES CARRIED OUT                      6

 CORRECTION FACTORS for visual inspection by XDS-Viewer DECAY_001.cbf       
 XMIN=     1.2 XMAX=    99.8 NXBIN=   10
 YMIN= 0.00052 YMAX= 0.15973 NYBIN=   20
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      25044

 CORRECTION FACTORS for visual inspection by XDS-Viewer DECAY_002.cbf       
 XMIN=     0.2 XMAX=    49.8 NXBIN=    5
 YMIN= 0.00052 YMAX= 0.15986 NYBIN=   20
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      16096


 ******************************************************************************
  CORRECTION FACTORS AS FUNCTION OF X (fast) & Y(slow) IN THE DETECTOR PLANE
 ******************************************************************************

 RECIPROCAL CORRECTION FACTORS FOR INPUT DATA SETS MERGED TO
 OUTPUT FILE: temp.ahkl                                         

 THE CALCULATIONS ASSUME         FRIEDEL'S_LAW= TRUE
 TOTAL NUMBER OF CORRECTION FACTORS DEFINED      830
 DEGREES OF FREEDOM OF CHI^2 FIT             25467.0
 CHI^2-VALUE OF FIT OF CORRECTION FACTORS      0.835
 NUMBER OF CYCLES CARRIED OUT                      4

 CORRECTION FACTORS for visual inspection by XDS-Viewer MODPIX_001.cbf      
 XMIN=     6.4 XMAX=  2456.8 NXBIN=   22
 YMIN=    12.8 YMAX=  2508.8 NYBIN=   23
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      25044

 CORRECTION FACTORS for visual inspection by XDS-Viewer MODPIX_002.cbf      
 XMIN=    11.2 XMAX=  2455.4 NXBIN=   18
 YMIN=    10.0 YMAX=  2511.8 NYBIN=   18
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      16096


 ******************************************************************************
   CORRECTION FACTORS AS FUNCTION OF IMAGE NUMBER & DETECTOR SURFACE POSITION
 ******************************************************************************

 RECIPROCAL CORRECTION FACTORS FOR INPUT DATA SETS MERGED TO
 OUTPUT FILE: temp.ahkl                                         

 THE CALCULATIONS ASSUME         FRIEDEL'S_LAW= TRUE
 TOTAL NUMBER OF CORRECTION FACTORS DEFINED      195
 DEGREES OF FREEDOM OF CHI^2 FIT             25493.3
 CHI^2-VALUE OF FIT OF CORRECTION FACTORS      0.825
 NUMBER OF CYCLES CARRIED OUT                      3

 CORRECTION FACTORS for visual inspection by XDS-Viewer ABSORP_001.cbf      
 XMIN=     1.2 XMAX=    99.8 NXBIN=   10
 DETECTOR_SURFACE_POSITION=    1232    1261
 DETECTOR_SURFACE_POSITION=    1648    1685
 DETECTOR_SURFACE_POSITION=     815    1685
 DETECTOR_SURFACE_POSITION=     815     837
 DETECTOR_SURFACE_POSITION=    1648     837
 DETECTOR_SURFACE_POSITION=    2173    1658
 DETECTOR_SURFACE_POSITION=    1622    2220
 DETECTOR_SURFACE_POSITION=     841    2220
 DETECTOR_SURFACE_POSITION=     290    1658
 DETECTOR_SURFACE_POSITION=     290     863
 DETECTOR_SURFACE_POSITION=     841     301
 DETECTOR_SURFACE_POSITION=    1622     301
 DETECTOR_SURFACE_POSITION=    2173     863
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      25044

 CORRECTION FACTORS for visual inspection by XDS-Viewer ABSORP_002.cbf      
 XMIN=     0.2 XMAX=    49.8 NXBIN=    5
 DETECTOR_SURFACE_POSITION=    1233    1261
 DETECTOR_SURFACE_POSITION=    1648    1686
 DETECTOR_SURFACE_POSITION=     818    1686
 DETECTOR_SURFACE_POSITION=     818     836
 DETECTOR_SURFACE_POSITION=    1648     836
 DETECTOR_SURFACE_POSITION=    2173    1659
 DETECTOR_SURFACE_POSITION=    1622    2222
 DETECTOR_SURFACE_POSITION=     844    2222
 DETECTOR_SURFACE_POSITION=     294    1659
 DETECTOR_SURFACE_POSITION=     294     863
 DETECTOR_SURFACE_POSITION=     844     299
 DETECTOR_SURFACE_POSITION=    1622     299
 DETECTOR_SURFACE_POSITION=    2173     863
 NUMBER OF REFLECTIONS USED FOR DETERMINING CORRECTION FACTORS      16096


 ******************************************************************************
    CORRECTION PARAMETERS FOR THE STANDARD ERROR OF REFLECTION INTENSITIES
 ******************************************************************************

 The variance v0(I) of the intensity I obtained from counting statistics is
 replaced by v(I)=a*(v0(I)+b*I^2). The model parameters a, b are chosen to
 minimize the discrepancies between v(I) and the variance estimated from
 sample statistics of symmetry related reflections. This model implicates
 an asymptotic limit ISa=1/SQRT(a*b) for the highest I/Sigma(I) that the
 experimental setup can produce (Diederichs (2010) Acta Cryst D66, 733-740).
 Often the value of ISa is reduced from the initial value ISa0 due to systematic
 errors showing up by comparison with other data sets in the scaling procedure.
 (ISa=ISa0=-1 if v0 is unknown for a data set.)

     a        b          ISa    ISa0   INPUT DATA SET
 9.591E-01  2.435E-03   20.69   50.00 ../2-140/XDS_ASCII.HKL
 1.155E+00  2.907E-03   17.26   50.00 ../1-60/XDS_ASCII.HKL
 

 FACTOR TO PLACE ALL DATA SETS TO AN APPROXIMATE ABSOLUTE SCALE 0.867786E+04
 (ASSUMING A PROTEIN WITH 50% SOLVENT)



 ******************************************************************************
  STATISTICS OF SCALED OUTPUT DATA SET : temp.ahkl
  FILE TYPE:         XDS_ASCII      MERGE=FALSE          FRIEDEL'S_LAW=TRUE 

        59 OUT OF     65478 REFLECTIONS REJECTED
     65419 REFLECTIONS ON OUTPUT FILE 

 ******************************************************************************
 DEFINITIONS:
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

    11.19         684     251       538       46.7%       4.0%      3.7%      645   25.95      4.8%    99.5*     6    1.049      83
     7.91        1386     513       958       53.5%       4.3%      4.0%     1317   21.57      5.3%    99.5*    19    1.028     150
     6.46        1664     648      1226       52.9%       5.8%      5.3%     1536   15.10      7.2%    99.4*     5    0.957     150
     5.59        2102     824      1469       56.1%       6.6%      6.7%     1937   12.27      8.2%    99.3*     1    0.822     179
     5.00        2439     969      1634       59.3%       6.9%      6.8%     2236   12.23      8.5%    99.2*     5    0.861     193
     4.57        2474    1010      1794       56.3%       6.5%      6.2%     2238   13.29      8.0%    99.1*    -6    0.844     179
     4.23        2775    1142      1969       58.0%       7.4%      6.9%     2513   11.97      9.1%    99.1*     0    0.918     197
     3.95        3109    1274      2122       60.0%       8.7%      8.2%     2826   10.28     10.8%    98.9*     5    0.954     205
     3.73        3349    1403      2248       62.4%      12.0%     11.7%     3017    7.81     15.0%    97.7*     3    0.870     203
     3.54        3289    1382      2357       58.6%      14.2%     14.5%     2950    6.68     17.7%    97.3*     9    0.885     197
     3.37        3437    1486      2478       60.0%      18.2%     19.5%     3039    5.09     22.8%    96.3*     5    0.762     185
     3.23        3707    1625      2609       62.3%      24.4%     26.6%     3267    3.97     30.7%    93.1*   -11    0.671     181
     3.10        3937    1740      2704       64.3%      33.0%     36.3%     3473    2.95     41.3%    89.2*    -4    0.744     178
     2.99        4213    1845      2820       65.4%      43.2%     48.1%     3737    2.18     54.2%    85.1*    13    0.743     200
     2.89        4067    1831      2914       62.8%      58.3%     63.9%     3546    1.69     73.2%    79.2*     9    0.707     165
     2.80        4143    1893      3017       62.7%      69.5%     78.8%     3576    1.29     87.2%    66.7*    -1    0.688     168
     2.71        4399    2009      3105       64.7%      86.4%     98.9%     3820    1.06    109.3%    59.6*    10    0.643     169
     2.64        4690    2138      3214       66.5%     112.9%    129.5%     4095    0.84    143.1%    52.7*     9    0.607     171
     2.57        4760    2172      3234       67.2%     156.0%    178.9%     4168    0.57    198.1%    34.3*     4    0.590     176
     2.50        4795    2232      3405       65.6%     177.7%    205.2%     4144    0.47    226.5%    25.7*   -10    0.529     145
    total       65419   28387     45815       62.0%      13.1%     13.6%    58080    5.09     16.3%    99.1*     4    0.790    3474


 ========== STATISTICS OF INPUT DATA SET ==========


  R-FACTORS FOR INTENSITIES OF DATA SET ../2-140/XDS_ASCII.HKL

 RESOLUTION   R-FACTOR   R-FACTOR   COMPARED
   LIMIT      observed   expected

    11.19         3.2%       3.3%       419
     7.91         3.6%       3.6%       855
     6.46         5.5%       5.1%       988
     5.59         6.4%       6.8%      1233
     5.00         6.7%       6.9%      1438
     4.57         6.3%       6.2%      1433
     4.23         7.3%       7.1%      1590
     3.95         9.1%       8.9%      1785
     3.73        13.4%      13.3%      1909
     3.54        16.1%      17.0%      1858
     3.37        21.6%      22.8%      1907
     3.23        29.7%      32.5%      2044
     3.10        41.2%      44.3%      2179
     2.99        55.3%      60.6%      2337
     2.89        74.9%      80.8%      2228
     2.80        86.2%      95.8%      2225
     2.71       112.0%     126.1%      2374
     2.64       150.9%     172.4%      2532
     2.57       189.6%     215.2%      2597
     2.50       224.1%     256.6%      2605
    total        14.3%      15.2%     36536

  R-FACTORS FOR INTENSITIES OF DATA SET ../1-60/XDS_ASCII.HKL

 RESOLUTION   R-FACTOR   R-FACTOR   COMPARED
   LIMIT      observed   expected

    11.19         5.2%       4.3%       226
     7.91         5.5%       4.7%       462
     6.46         6.3%       5.6%       548
     5.59         7.0%       6.7%       704
     5.00         7.2%       6.8%       798
     4.57         7.0%       6.2%       805
     4.23         7.5%       6.5%       923
     3.95         8.1%       7.2%      1041
     3.73        10.1%       9.4%      1108
     3.54        11.7%      11.2%      1092
     3.37        13.5%      14.7%      1132
     3.23        17.5%      19.0%      1223
     3.10        22.3%      26.0%      1294
     2.99        28.8%      33.1%      1400
     2.89        37.6%      43.0%      1318
     2.80        47.5%      56.4%      1351
     2.71        55.8%      66.3%      1446
     2.64        70.2%      81.3%      1563
     2.57       107.5%     126.5%      1571
     2.50       113.4%     134.0%      1539
    total        11.2%      11.3%     21544


 ******************************************************************************
    WILSON STATISTICS OF SCALED DATA SET: temp.ahkl                                         
 ******************************************************************************

 Data is divided into resolution shells and a straight line 
 A - 2*B*SS is fitted to log<I>, where
   RES    = mean resolution (Angstrom) in shell
   SS     = mean of (sin(THETA)/LAMBDA)**2 in shell
   <I>    = mean reflection intensity in shell
   BO     = (A - log<I>)/(2*SS)
    #     = number of reflections in resolution shell

   WILSON LINE (using all data) : A=  14.200 B=  64.497 CORRELATION=  0.98
      #      RES      SS        <I>       log(<I>)       BO
     297    13.682   0.001  1.2503E+06      14.039      60.4
     573     8.655   0.003  8.0895E+05      13.603      89.4
     705     6.805   0.005  3.7324E+05      12.830     126.9
     912     5.768   0.008  3.1781E+05      12.669     101.9
    1057     5.099   0.010  3.8141E+05      12.852      70.1
    1063     4.627   0.012  4.6944E+05      13.059      48.8
    1259     4.261   0.014  4.1251E+05      12.930      46.1
    1402     3.968   0.016  2.9285E+05      12.587      50.8
    1514     3.730   0.018  2.0570E+05      12.234      54.7
    1445     3.529   0.020  1.6449E+05      12.011      54.5
    1655     3.358   0.022  1.0855E+05      11.595      58.8
    1765     3.210   0.024  7.1987E+04      11.184      62.2
    1920     3.080   0.026  4.7602E+04      10.771      65.1
    1941     2.966   0.028  3.3891E+04      10.431      66.3
    1943     2.861   0.031  2.4647E+04      10.112      66.9
    2091     2.768   0.033  1.9337E+04       9.870      66.3
    2221     2.683   0.035  1.3778E+04       9.531      67.2
    2293     2.606   0.037  1.0471E+04       9.256      67.1
    2330     2.535   0.039  8.4316E+03       9.040      66.3


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF  CENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         3<I>**2     15<I>**3    105<I>**4 

      23    13.682        1.623        1.838        1.631
      26     8.655        5.472       15.407       34.498
      28     6.805        1.183        1.150        0.990
      32     5.768        0.694        0.433        0.221
      29     5.099        0.320        0.143        0.051
      32     4.627        1.743        2.133        2.161
      32     4.261        3.094        5.516        8.638
      31     3.968        1.088        1.453        1.592
      33     3.730        0.296        0.132        0.052
      30     3.529        3.110        5.121        7.347
      35     3.358        0.547        0.277        0.118
      34     3.210        1.152        1.166        0.970
      32     3.080        0.892        0.687        0.474
      40     2.966        1.315        1.498        2.002
      31     2.861        1.228        0.130        0.633
      41     2.768        0.795        0.213        0.136
      38     2.683        3.852        9.903       23.787
      40     2.606        2.826        1.722        2.195
     627   overall        1.818        2.360        4.525


 HIGHER ORDER MOMENTS OF WILSON DISTRIBUTION OF ACENTRIC DATA
    AS COMPARED WITH THEORETICAL VALUES. (EXPECTED: 1.00)    
      #      RES        <I**2>/      <I**3>/      <I**4>/  
                         2<I>**2      6<I>**3     24<I>**4 

     274    13.682        1.083        1.347        1.780
     547     8.655        0.989        1.034        1.063
     677     6.805        1.131        1.387        1.731
     880     5.768        1.179        1.583        2.371
    1028     5.099        1.118        1.293        1.510
    1031     4.627        1.068        1.197        1.346
    1227     4.261        1.196        1.716        2.701
    1371     3.968        1.221        1.546        1.909
    1481     3.730        1.296        1.820        2.667
    1415     3.529        1.378        2.101        3.198
    1620     3.358        1.438        2.228        3.659
    1731     3.210        1.530        2.402        3.921
    1888     3.080        1.828        3.987       11.167
    1901     2.966        2.163        4.672       11.742
    1912     2.861        1.987        3.227        6.960
    2050     2.768        2.415        4.151        9.124
    2183     2.683        3.269        6.270       19.108
    2253     2.606        4.091        6.915       22.875
    2290     2.535        5.457        7.127       27.928
   27759   overall        2.235        3.609        9.619

   ======= CUMULATIVE INTENSITY DISTRIBUTION =======
 DEFINITIONS:
   <I>    = mean reflection intensity
 Na(Z)exp = expected number of acentric reflections with I <= Z*<I>
 Na(Z)obs = observed number of acentric reflections with I <= Z*<I>
 Nc(Z)exp = expected number of  centric reflections with I <= Z*<I>
 Nc(Z)obs = observed number of  centric reflections with I <= Z*<I>



 Nc(Z)obs/Nc(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

      23    13.682  0.70  0.63  0.63  0.74  0.84  1.01  1.02  1.11  1.06  1.08
      26     8.655  0.93  1.33  1.11  1.06  0.96  0.89  0.97  0.92  0.94  0.90
      28     6.805  0.72  0.72  0.69  0.83  0.75  0.76  0.96  0.97  0.92  0.99
      32     5.768  1.01  0.90  0.98  0.99  1.02  1.06  1.05  1.04  1.00  1.01
      29     5.099  1.81  1.40  1.16  1.24  1.26  1.17  1.27  1.26  1.26  1.21
      32     4.627  0.88  0.90  0.98  0.92  1.02  1.00  0.99  0.99  1.00  0.96
      32     4.261  0.88  0.99  0.90  0.79  0.84  0.84  0.79  0.80  0.90  0.87
      31     3.968  1.04  1.49  1.47  1.36  1.43  1.32  1.24  1.18  1.13  1.09
      33     3.730  1.10  1.14  1.16  1.15  1.22  1.19  1.22  1.21  1.25  1.24
      30     3.529  0.94  0.87  0.80  0.92  0.90  0.95  0.89  0.85  0.91  0.88
      35     3.358  1.61  1.24  1.30  1.15  1.10  1.17  1.10  1.05  1.00  0.96
      34     3.210  1.89  1.45  1.27  1.24  1.19  1.26  1.23  1.17  1.12  1.12
      32     3.080  1.38  0.99  0.83  0.92  0.96  0.95  0.94  0.94  0.95  0.96
      40     2.966  1.01  0.87  0.84  0.79  0.86  0.85  1.00  0.95  0.95  0.92
      31     2.861  1.04  0.84  0.70  0.75  0.68  0.86  0.81  0.92  0.93  0.99
      41     2.768  1.57  1.20  1.05  1.08  1.03  0.96  0.94  0.93  0.93  0.89
      38     2.683  1.91  1.45  1.20  1.06  1.01  1.03  1.01  1.00  1.00  0.96
      40     2.606  1.41  1.08  1.02  0.90  0.82  0.80  0.75  0.72  0.72  0.70
     627   overall  1.16  1.02  0.95  0.93  0.93  0.94  0.94  0.93  0.93  0.92


 Na(Z)obs/Na(Z)exp versus resolution and Z (0.1-1.0)
      #      RES     0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0

     274    13.682  1.00  0.95  0.97  1.01  1.04  1.09  1.09  1.09  1.07  1.07
     547     8.655  1.21  1.15  1.14  1.10  1.08  1.10  1.08  1.05  1.04  1.04
     677     6.805  0.95  1.17  1.24  1.16  1.14  1.13  1.09  1.06  1.04  1.03
     880     5.768  1.17  1.14  1.13  1.07  1.10  1.08  1.05  1.05  1.05  1.04
    1028     5.099  1.16  1.08  1.06  1.09  1.06  1.04  1.04  1.03  1.01  1.00
    1031     4.627  1.01  1.02  1.03  1.11  1.07  1.06  1.07  1.05  1.04  1.04
    1227     4.261  1.28  1.19  1.16  1.13  1.13  1.14  1.12  1.10  1.07  1.06
    1371     3.968  1.40  1.24  1.19  1.15  1.13  1.10  1.08  1.06  1.06  1.05
    1481     3.730  1.37  1.20  1.15  1.15  1.14  1.12  1.11  1.09  1.08  1.06
    1415     3.529  1.90  1.45  1.30  1.24  1.19  1.14  1.10  1.08  1.06  1.06
    1620     3.358  1.91  1.41  1.26  1.18  1.12  1.11  1.08  1.06  1.05  1.04
    1731     3.210  2.14  1.41  1.21  1.13  1.07  1.06  1.05  1.06  1.04  1.03
    1888     3.080  2.59  1.63  1.31  1.20  1.16  1.09  1.05  1.03  1.01  1.01
    1901     2.966  2.73  1.68  1.34  1.14  1.08  1.05  1.03  1.01  1.01  0.99
    1912     2.861  2.83  1.66  1.28  1.09  1.02  0.98  0.95  0.94  0.93  0.91
    2050     2.768  3.07  1.82  1.38  1.19  1.08  1.01  0.97  0.94  0.92  0.91
    2183     2.683  3.58  1.99  1.49  1.24  1.11  1.02  0.96  0.92  0.89  0.87
    2253     2.606  3.80  2.07  1.51  1.25  1.10  1.01  0.93  0.89  0.86  0.85
    2290     2.535  3.86  2.10  1.54  1.25  1.08  0.99  0.92  0.87  0.84  0.81
   27759   overall  2.41  1.57  1.30  1.17  1.10  1.06  1.02  1.00  0.98  0.97


 List of     92 reflections *NOT* obeying Wilson distribution (Z> 10.0)

   h    k    l     RES      Z     Intensity    Sigma

   69    5    4    2.64   24.16  0.5059E+06  0.3365E+05 "alien"
   44   30    5    2.69   22.69  0.6254E+06  0.5544E+05 "alien"
   41   23    6    3.11   21.70  0.2066E+07  0.1181E+06 "alien"
   73    9   -2    2.56   20.51  0.3459E+06  0.3845E+05 "alien"
   29   33    6    2.83   17.89  0.8818E+06  0.7665E+05 "alien"
   62   24   -4    2.55   17.83  0.3007E+06  0.4369E+05 "alien"
   67    9    5    2.64   17.71  0.3708E+06  0.2266E+05 "alien"
   69    9   -3    2.70   17.35  0.4781E+06  0.4475E+05 "alien"
    3   41    8    2.54   17.15  0.2892E+06  0.6124E+05 "alien"
   31   33    6    2.79   16.34  0.6321E+06  0.4394E+05 "alien"
   38   34   -7    2.65   16.21  0.4468E+06  0.7147E+05 "alien"
   37   35   -8    2.59   16.05  0.3362E+06  0.5299E+05 "alien"
   49   23   -6    2.97   16.01  0.1085E+07  0.9732E+05 "alien"
   14   32    7    3.11   15.64  0.1489E+07  0.1136E+06 "alien"
   72   14   -2    2.51   15.62  0.2635E+06  0.4137E+05 "alien"
   26   32    6    2.95   15.55  0.1054E+07  0.5816E+05 "alien"
   32   36   -7    2.65   15.51  0.4273E+06  0.6834E+05 "alien"
   34   32    6    2.79   15.50  0.5994E+06  0.4194E+05 "alien"
   62    8   -4    3.00   15.50  0.1051E+07  0.4198E+05 "alien"
   42   32   -8    2.65   15.39  0.4242E+06  0.5057E+05 "alien"
   37   35   -7    2.62   14.76  0.3090E+06  0.4837E+05 "alien"
   42   32   -7    2.67   14.38  0.3962E+06  0.5244E+05 "alien"
   71    3    3    2.61   14.16  0.2966E+06  0.2951E+05 "alien"
   65    9   -2    2.86   14.01  0.6905E+06  0.4812E+05 "alien"
    5   41   -8    2.55   13.82  0.2330E+06  0.4609E+05 "alien"
   59   11   -2    3.08   13.58  0.1293E+07  0.5357E+05 "alien"
   38   28    5    2.96   13.54  0.9179E+06  0.4768E+05 "alien"
   31    7  -24    2.51   13.54  0.2283E+06  0.9639E+05 "alien"
   23   37    6    2.69   13.53  0.3728E+06  0.5539E+05 "alien"
   63    1    0    3.01   13.40  0.9082E+06  0.3650E+05 "alien"
   30   30    6    3.00   13.38  0.9068E+06  0.5269E+05 "alien"
   64    4   -1    2.96   13.31  0.9021E+06  0.4376E+05 "alien"
   40   34   -7    2.61   13.26  0.2776E+06  0.5115E+05 "alien"
   34   36   -8    2.59   13.24  0.2773E+06  0.5204E+05 "alien"
   51   27   -9    2.64   13.20  0.2764E+06  0.6297E+05 "alien"
   28   10  -24    2.51   13.18  0.2223E+06  0.9162E+05 "alien"
   70   10   -9    2.56   13.17  0.2221E+06  0.7298E+05 "alien"
   68   10   -3    2.72   13.01  0.3586E+06  0.3963E+05 "alien"
   73    9   -3    2.56   13.01  0.2194E+06  0.3726E+05 "alien"
    5   13  -24    2.55   12.85  0.2166E+06  0.8684E+05 "alien"
    1   41    8    2.55   12.51  0.2110E+06  0.4444E+05 "alien"
   10   34    7    3.00   12.38  0.8394E+06  0.5686E+05 "alien"
   32   12  -23    2.53   12.32  0.2077E+06  0.9228E+05 "alien"
   23   21   11    3.43   12.30  0.2670E+07  0.2065E+06 "alien"
    8   14  -24    2.54   12.29  0.2072E+06  0.8505E+05 "alien"
    5   37   11    2.64   12.03  0.2519E+06  0.4253E+05 "alien"
   67   17   -2    2.61   11.98  0.2508E+06  0.4924E+05 "alien"
   71    5    5    2.54   11.86  0.2000E+06  0.3056E+05 "alien"
   69    1    1    2.73   11.78  0.4555E+06  0.2601E+05 "alien"
   74    2   -2    2.58   11.70  0.2450E+06  0.3043E+05 "alien"
   61    1    1    3.09   11.69  0.1113E+07  0.3988E+05 "alien"
   16   36    7    2.80   11.66  0.4509E+06  0.4544E+05 "alien"
   32   24    6    3.37   11.59  0.2515E+07  0.1081E+06 "alien"
    9   35    7    2.94   11.47  0.7772E+06  0.5482E+05 "alien"
   64    4    0    2.95   11.43  0.7745E+06  0.3542E+05 "alien"
   50   32   -6    2.52   11.10  0.1871E+06  0.4606E+05 "alien"
   59   11   -3    3.08   11.01  0.1048E+07  0.3922E+05 "alien"
   27   37   -8    2.63   10.93  0.2290E+06  0.4758E+05 "alien"
   69    5    2    2.69   10.93  0.3012E+06  0.3003E+05 "alien"
   49   13   -4    3.52   10.91  0.3590E+07  0.1219E+06 "alien"
   59   23  -10    2.55   10.89  0.1836E+06  0.5056E+05 "alien"
   50    2    0    3.79   10.80  0.4442E+07  0.1491E+06 "alien"
   68    6   -2    2.78   10.76  0.4163E+06  0.3423E+05 "alien"
   14   40    7    2.58   10.74  0.2249E+06  0.4195E+05 "alien"
   13   15   -6    5.72   10.68  0.6788E+07  0.2676E+06 "alien"
   41    7   -4    4.40   10.67  0.8807E+07  0.2758E+06 "alien"
   27   35    7    2.71   10.67  0.2941E+06  0.3637E+05 "alien"
   23   37    9    2.58   10.62  0.2224E+06  0.3821E+05 "alien"
   56    8    1    3.27   10.61  0.1527E+07  0.9615E+05 "alien"
    1   27    6    3.81   10.57  0.4349E+07  0.2745E+06 "alien"
   16   14   -6    5.74   10.53  0.6694E+07  0.1869E+06 "alien"
   22   38    9    2.54   10.52  0.1774E+06  0.3714E+05 "alien"
   70    8    0    2.66   10.50  0.2893E+06  0.2907E+05 "alien"
   55   29   -6    2.53   10.50  0.1771E+06  0.4678E+05 "alien"
   25   29   -7    3.24   10.44  0.1503E+07  0.8205E+05 "alien"
   36   32   -8    2.77   10.44  0.4036E+06  0.5217E+05 "alien"
   61    1    0    3.11   10.43  0.9927E+06  0.5345E+05 "alien"
   47   25   -7    2.90   10.37  0.5112E+06  0.4987E+05 "alien"
   20   28    6    3.40   10.33  0.2243E+07  0.1001E+06 "alien"
   72   14   -3    2.51   10.30  0.1738E+06  0.3582E+05 "alien"
   69    3    2    2.71   10.28  0.2834E+06  0.2473E+05 "alien"
   65    7    3    2.81   10.23  0.3958E+06  0.2802E+05 "alien"
   33   33   -7    2.80   10.20  0.3946E+06  0.5128E+05 "alien"
   56   10    4    3.11   10.19  0.9700E+06  0.5366E+05 "alien"
   18   22    5    4.21   10.17  0.8392E+07  0.3258E+06 "alien"
   43   31    4    2.70   10.13  0.2791E+06  0.2717E+05 "alien"
   25   37    9    2.55   10.06  0.1697E+06  0.3661E+05 "alien"
   35   31    6    2.82   10.05  0.4954E+06  0.3775E+05 "alien"
   33   27    4    3.22   10.02  0.1443E+07  0.1017E+06 "alien"
   23   21    5    4.11   10.01  0.8258E+07  0.3197E+06 "alien"
   14   38  -10    2.62   10.01  0.2096E+06  0.4475E+05 "alien"
   12   18  -23    2.54   10.01  0.1687E+06  0.8794E+05 "alien"


 List of     92 reflections *NOT* obeying Wilson distribution (sorted by resolution)
 Ice rings could occur at (Angstrom):
 3.897,3.669,3.441, 2.671,2.249,2.072, 1.948,1.918,1.883,1.721

   h    k    l     RES      Z     Intensity    Sigma

   28   10  -24    2.51   13.18  0.2223E+06  0.9162E+05
   72   14   -2    2.51   15.62  0.2635E+06  0.4137E+05
   31    7  -24    2.51   13.54  0.2283E+06  0.9639E+05
   72   14   -3    2.51   10.30  0.1738E+06  0.3582E+05
   50   32   -6    2.52   11.10  0.1871E+06  0.4606E+05
   32   12  -23    2.53   12.32  0.2077E+06  0.9228E+05
   55   29   -6    2.53   10.50  0.1771E+06  0.4678E+05
   22   38    9    2.54   10.52  0.1774E+06  0.3714E+05
    8   14  -24    2.54   12.29  0.2072E+06  0.8505E+05
   12   18  -23    2.54   10.01  0.1687E+06  0.8794E+05
    3   41    8    2.54   17.15  0.2892E+06  0.6124E+05
   71    5    5    2.54   11.86  0.2000E+06  0.3056E+05
    1   41    8    2.55   12.51  0.2110E+06  0.4444E+05
   59   23  -10    2.55   10.89  0.1836E+06  0.5056E+05
    5   41   -8    2.55   13.82  0.2330E+06  0.4609E+05
   25   37    9    2.55   10.06  0.1697E+06  0.3661E+05
    5   13  -24    2.55   12.85  0.2166E+06  0.8684E+05
   62   24   -4    2.55   17.83  0.3007E+06  0.4369E+05
   73    9   -2    2.56   20.51  0.3459E+06  0.3845E+05
   73    9   -3    2.56   13.01  0.2194E+06  0.3726E+05
   70   10   -9    2.56   13.17  0.2221E+06  0.7298E+05
   23   37    9    2.58   10.62  0.2224E+06  0.3821E+05
   14   40    7    2.58   10.74  0.2249E+06  0.4195E+05
   74    2   -2    2.58   11.70  0.2450E+06  0.3043E+05
   34   36   -8    2.59   13.24  0.2773E+06  0.5204E+05
   37   35   -8    2.59   16.05  0.3362E+06  0.5299E+05
   67   17   -2    2.61   11.98  0.2508E+06  0.4924E+05
   71    3    3    2.61   14.16  0.2966E+06  0.2951E+05
   40   34   -7    2.61   13.26  0.2776E+06  0.5115E+05
   14   38  -10    2.62   10.01  0.2096E+06  0.4475E+05
   37   35   -7    2.62   14.76  0.3090E+06  0.4837E+05
   27   37   -8    2.63   10.93  0.2290E+06  0.4758E+05
    5   37   11    2.64   12.03  0.2519E+06  0.4253E+05
   51   27   -9    2.64   13.20  0.2764E+06  0.6297E+05
   67    9    5    2.64   17.71  0.3708E+06  0.2266E+05
   69    5    4    2.64   24.16  0.5059E+06  0.3365E+05
   32   36   -7    2.65   15.51  0.4273E+06  0.6834E+05
   42   32   -8    2.65   15.39  0.4242E+06  0.5057E+05
   38   34   -7    2.65   16.21  0.4468E+06  0.7147E+05
   70    8    0    2.66   10.50  0.2893E+06  0.2907E+05
   42   32   -7    2.67   14.38  0.3962E+06  0.5244E+05
   23   37    6    2.69   13.53  0.3728E+06  0.5539E+05
   44   30    5    2.69   22.69  0.6254E+06  0.5544E+05
   69    5    2    2.69   10.93  0.3012E+06  0.3003E+05
   43   31    4    2.70   10.13  0.2791E+06  0.2717E+05
   69    9   -3    2.70   17.35  0.4781E+06  0.4475E+05
   69    3    2    2.71   10.28  0.2834E+06  0.2473E+05
   27   35    7    2.71   10.67  0.2941E+06  0.3637E+05
   68   10   -3    2.72   13.01  0.3586E+06  0.3963E+05
   69    1    1    2.73   11.78  0.4555E+06  0.2601E+05
   36   32   -8    2.77   10.44  0.4036E+06  0.5217E+05
   68    6   -2    2.78   10.76  0.4163E+06  0.3423E+05
   34   32    6    2.79   15.50  0.5994E+06  0.4194E+05
   31   33    6    2.79   16.34  0.6321E+06  0.4394E+05
   16   36    7    2.80   11.66  0.4509E+06  0.4544E+05
   33   33   -7    2.80   10.20  0.3946E+06  0.5128E+05
   65    7    3    2.81   10.23  0.3958E+06  0.2802E+05
   35   31    6    2.82   10.05  0.4954E+06  0.3775E+05
   29   33    6    2.83   17.89  0.8818E+06  0.7665E+05
   65    9   -2    2.86   14.01  0.6905E+06  0.4812E+05
   47   25   -7    2.90   10.37  0.5112E+06  0.4987E+05
    9   35    7    2.94   11.47  0.7772E+06  0.5482E+05
   64    4    0    2.95   11.43  0.7745E+06  0.3542E+05
   26   32    6    2.95   15.55  0.1054E+07  0.5816E+05
   64    4   -1    2.96   13.31  0.9021E+06  0.4376E+05
   38   28    5    2.96   13.54  0.9179E+06  0.4768E+05
   49   23   -6    2.97   16.01  0.1085E+07  0.9732E+05
   62    8   -4    3.00   15.50  0.1051E+07  0.4198E+05
   10   34    7    3.00   12.38  0.8394E+06  0.5686E+05
   30   30    6    3.00   13.38  0.9068E+06  0.5269E+05
   63    1    0    3.01   13.40  0.9082E+06  0.3650E+05
   59   11   -3    3.08   11.01  0.1048E+07  0.3922E+05
   59   11   -2    3.08   13.58  0.1293E+07  0.5357E+05
   61    1    1    3.09   11.69  0.1113E+07  0.3988E+05
   41   23    6    3.11   21.70  0.2066E+07  0.1181E+06
   14   32    7    3.11   15.64  0.1489E+07  0.1136E+06
   61    1    0    3.11   10.43  0.9927E+06  0.5345E+05
   56   10    4    3.11   10.19  0.9700E+06  0.5366E+05
   33   27    4    3.22   10.02  0.1443E+07  0.1017E+06
   25   29   -7    3.24   10.44  0.1503E+07  0.8205E+05
   56    8    1    3.27   10.61  0.1527E+07  0.9615E+05
   32   24    6    3.37   11.59  0.2515E+07  0.1081E+06
   20   28    6    3.40   10.33  0.2243E+07  0.1001E+06
   23   21   11    3.43   12.30  0.2670E+07  0.2065E+06
   49   13   -4    3.52   10.91  0.3590E+07  0.1219E+06
   50    2    0    3.79   10.80  0.4442E+07  0.1491E+06
    1   27    6    3.81   10.57  0.4349E+07  0.2745E+06
   23   21    5    4.11   10.01  0.8258E+07  0.3197E+06
   18   22    5    4.21   10.17  0.8392E+07  0.3258E+06
   41    7   -4    4.40   10.67  0.8807E+07  0.2758E+06
   13   15   -6    5.72   10.68  0.6788E+07  0.2676E+06
   16   14   -6    5.74   10.53  0.6694E+07  0.1869E+06

 cpu time used by XSCALE        1.5 sec
 elapsed wall-clock time        2.7 sec


 ***** COLSPOT ***** (VERSION Jan 31, 2020  BUILT=20200131)   4-May-2020

 INPUT PARAMETER VALUES
 ----------------------
 MAXIMUM_NUMBER_OF_PROCESSORS=   0  (0: automatic choice of OpenMP threads)
 MAXIMUM_NUMBER_OF_JOBS=   0  (0:automatic choice of forked main tasks)
 number of forked COLSPOT tasks   1
 CLUSTER_NODES=
 SECONDS=     0
 NAME_TEMPLATE_OF_DATA_FRAMES=/nfs/loop1/mnt/synchrotron/kay/proteindiffraction/IDP51000_6w9c/data/y3_b07b_?????.cbf CBF
 DATA_RANGE=       1     140
 BACKGROUND_PIXEL=    6.00
 STRONG_PIXEL=    4.00
 MAXIMUM_NUMBER_OF_STRONG_PIXELS=   1500000
 MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT=    3 SPOT_MAXIMUM-CENTROID=    3.00
 SPOT_RANGE=       1      30
 ------------------------------------------------------------------------

 Task # 1 scans a subset of      30 images in the range      1 ...    30
 ------------------------------------------------------------------------

 RESULTS FOR FORKED COLSPOT TASK # 1
 USING   24 OUT OF   24 PROCESSORS
 PROCESS #  1 scans     2  images in the range       1 ...      2
 PROCESS #  2 scans     2  images in the range       3 ...      4
 PROCESS #  3 scans     2  images in the range       5 ...      6
 PROCESS #  4 scans     2  images in the range       7 ...      8
 PROCESS #  5 scans     2  images in the range       9 ...     10
 PROCESS #  6 scans     2  images in the range      11 ...     12
 PROCESS #  7 scans     1  images in the range      13 ...     13
 PROCESS #  8 scans     1  images in the range      14 ...     14
 PROCESS #  9 scans     1  images in the range      15 ...     15
 PROCESS # 10 scans     1  images in the range      16 ...     16
 PROCESS # 11 scans     1  images in the range      17 ...     17
 PROCESS # 12 scans     1  images in the range      18 ...     18
 PROCESS # 13 scans     1  images in the range      19 ...     19
 PROCESS # 14 scans     1  images in the range      20 ...     20
 PROCESS # 15 scans     1  images in the range      21 ...     21
 PROCESS # 16 scans     1  images in the range      22 ...     22
 PROCESS # 17 scans     1  images in the range      23 ...     23
 PROCESS # 18 scans     1  images in the range      24 ...     24
 PROCESS # 19 scans     1  images in the range      25 ...     25
 PROCESS # 20 scans     1  images in the range      26 ...     26
 PROCESS # 21 scans     1  images in the range      27 ...     27
 PROCESS # 22 scans     1  images in the range      28 ...     28
 PROCESS # 23 scans     1  images in the range      29 ...     29
 PROCESS # 24 scans     1  images in the range      30 ...     30

 *** DEFINITION OF SYMBOLS ***
 NBKG      = NUMBER OF BACKGROUND PIXELS ON DATA IMAGE
 NSTRONG   = NUMBER OF STRONG PIXELS ON DATA IMAGE
 I/O-FLAG  = ERROR CODE AFTER ACCESSING DATA IMAGE
              0: NO ERROR
             -1: CANNOT OPEN OR READ IMAGE FILE
             -3: WRONG DATA FORMAT

 FRAME #      NBKG     NSTRONG   I/O-FLAG

 !!! ERROR !!! CANNOT READ IMAGE /nfs/loop1/mnt/synchrotron/kay/proteindiffraction/IDP51000_6w9c/data/y3_b07b_00001.cbf
               I/O-FLAG  =   -1
               DOES FILE EXIST AND HAS "READ" ACCESS ?

       1         0           0      -1
       2   5262898        1522       0
       3   5263009        1411       0
       4   5263303        1117       0
       5   5263179        1241       0
       6   5263040        1380       0
       7   5262943        1477       0
       8   5262903        1517       0
       9   5263107        1313       0
      10   5263096        1324       0
      11   5263167        1253       0
      12   5263188        1232       0
      13   5263110        1310       0
      14   5263057        1363       0
      15   5263069        1351       0
      16   5263108        1312       0
      17   5263087        1333       0
      18   5263144        1276       0
      19   5263021        1399       0
      20   5263119        1301       0
      21   5263143        1277       0
      22   5263132        1288       0
      23   5263050        1370       0
      24   5263150        1270       0
      25   5263144        1276       0
      26   5263261        1159       0
      27   5263295        1125       0
      28   5263336        1084       0
      29   5263271        1149       0
      30   5263106        1314       0

 NUMBER OF STRONG PIXELS EXTRACTED FROM IMAGES       37744

 NUMBER OF DIFFRACTION SPOTS LOCATED                  4413
 IGNORED BECAUSE OF SPOT CLOSE TO UNTRUSTED REGION     547
 WEAK SPOTS OMITTED                                      0
 NUMBER OF DIFFRACTION SPOTS ACCEPTED                 3866

 total elapsed wall-clock time for COLSPOT       1.6 sec

 TASK     cpu time (sec)    elapsed wall-clock time (sec)
   1          10.6                     1.6

import re
FORMAT = '%H.%M.%S %d/%m/%Y'
CALORIMETER_STRING = ' =====> HITS IN   ** ELECTRO-MAGNETIC CALORIMETER **'
SPECTROMETER_STRING = ' =====>HITS IN DETECTOR ** MAGNETIC SPECTROMETER **'
MUON_STRING = ' =====>HITS IN DETECTOR **    MUON DETECTORR     **'
TRACKS_STRING = '''          CHARGED TRACKS RECONSTRUCTION
          =============================
'''
VERTECES_STRING = '''          CHARGED TRACKS VERTECES RECONSTRUCTION
          ======================================
'''
TRACKS_RE = re.compile(r'\s+Track No.   (\d)\s+=============')
FIT_PARAM = ' *                             Fit Parameters                              *'
FIT_ERROR = ' *                             Fit Error Matrix'
EM_CLUSTER = '          ELECTROMAGNETIC CLUSTERS'

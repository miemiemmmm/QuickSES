import argparse
import re, os
# import sys
# from datetime import datetime
# import functools

import numpy as np
import open3d as o3d
import matplotlib.cm as cm


"""
MAP from atom type to its corresponding atom name and residue name
# 1   , ^O$     , ^.*$    
# 1   , ^OD1$   , ^ASN$   
# 1   , ^OD1[AB]?$, ^ASX$   
# 1   , ^OE1$   , ^GLN$   
# 1   , ^OXO$   , ^FS3$   
# 1   , ^O1$    , ^HEM$   
# 1   , ^O2$    , ^HEM$   
# 1   , ^O2$    , ^FMN$   
# 1   , ^O4$    , ^FMN$   
# 1   , ^O.*$   , ^.*$    
# 1   , ^.O.*$  , ^FAD|NAD|AMX|APU$
##################################
# 2   , ^O.*$   , ^WAT|HOH|H2O|DOD|DIS$
# 2   , ^OG$    , ^SER$   
# 2   , ^OG1$   , ^THR$   
# 2   , ^OH$    , ^TYR$   
# 2   , ^OH2$   , ^HEM$   
# 2   , ^O7$    , ^MPD$   
# 2   , ^O8$    , ^MPD$   
# 2   , ^O[234]\*$, ^FMN$   
##################################
# 3   , ^O1$    , ^GLN$   
# 3   , ^O2$    , ^GLN$   
# 3   , ^AD1$   , ^ASN$   
# 3   , ^AD2$   , ^ASN$   
# 3   , ^OD[12][AB]?$, ^ASP$   
# 3   , ^ED[12][AB]?$, ^ASP$   
# 3   , ^AD1$   , ^ASX$   
# 3   , ^AD2$   , ^ASX$   
# 3   , ^OD2$   , ^ASX$   
# 3   , ^OE[12][AB]?$, ^GLU$   
# 3   , ^EE[12][AB]?$, ^GLU$   
# 3   , ^AE[12]$, ^GLN|GLX$
# 3   , ^OD1$   , ^CSO$   
# 3   , ^OD2$   , ^CSO$   
# 3   , ^O[12][AD]$, ^HEM$   
# 3   , ^O[1234]$, ^SO4|SUL$
# 3   , ^O[1234]$, ^PO4|PHO$
# 3   , ^O4$    , ^PC$    
# 3   , ^O[123]$, ^PC$    
# 3   , ^O5\*$  , ^FMN$   
# 3   , ^OP[1-3]$, ^FMN$   
# 3   , ^OT1$   , ^ALK|MYR$
# 3   , ^OXT$   , ^.*$    
# 3   , ^OT.*$  , ^.*$    
# 3   , ^E.*$   , ^.*$    
##################################
# 4   , ^N$     , ^.*$    
# 4   , ^NE$    , ^ARG$   
# 4   , ^RE$    , ^ARG$   
# 4   , ^ND1$   , ^HID|HIP$
# 4   , ^RD1$   , ^HID|HIP$
# 4   , ^NE2$   , ^HIS|HIE|HIP$
# 4   , ^RE2$   , ^HIS|HIE|HIP$
# 4   , ^A[DE][12]$, ^HIS|HID|HIP|HISD$
# 4   , ^NE1$   , ^TRP$   
# 4   , ^N1$    , ^FMN$   
# 4   , ^N5$    , ^FMN$   
# 4   , ^N10$   , ^FMN$   
# 4   , ^N.*$   , ^.*$    
# 4   , ^R.*$   , ^.*$    
# 4   , ^.N.*$  , ^FAD|NAD|AMX|APU$
##################################
# 5   , ^NH[12][AB]?$, ^ARG$   
# 5   , ^RH[12][AB]?$, ^ARG$   
# 5   , ^ND2$   , ^ASN$   
# 5   , ^ND2$   , ^ASX$   
# 5   , ^NE2$   , ^GLN$   
##################################
# 6   , ^NZ$    , ^LYS$   
# 6   , ^KZ$    , ^LYS$   
# 6   , ^K.*$   , ^.*$    
##################################
# 7   , ^CA$    , ^.*$    
# 7   , ^CB$    , ^ILE|THR|VAL$
# 7   , ^CG$    , ^LEU$   
# 7   , ^C4$    , ^MPD$   
# 7   , ^C.*$   , ^.*$    
# 7   , ^.C.*$  , ^FAD|NAD|AMX|APU$
##################################
# 8   , ^CB$    , ^.*$    
# 8   , ^CG$    , ^ARG|GLU|GLN|GLX|MET$
# 8   , ^CG$    , ^.*$    
# 8   , ^CD$    , ^ARG$   
# 8   , ^CG1$   , ^ILE$   
# 8   , ^C[GDE]$, ^LYS$   
# 8   , ^C[GD]$ , ^PRO|CPR$
# 8   , ^CD$    , ^.*$    
# 8   , ^CE$    , ^.*$    
# 8   , ^C[AB][AD]$, ^HEM$   
# 8   , ^C3$    , ^MPD$   
# 8   , ^C[12]$ , ^PC$    
# 8   , ^C[12345]\*$, ^FMN$   
# 8   , ^C.*$   , ^ALK|MYR$
##################################
# 9   , ^CA$    , ^ACE$   
# 9   , ^CB$    , ^ALA$   
# 9   , ^CH3$   , ^ACE$   
# 9   , ^CG2$   , ^ILE$   
# 9   , ^CD|CD1$, ^ILE$   
# 9   , ^CD1$   , ^LEU$   
# 9   , ^CD2$   , ^LEU$   
# 9   , ^CE$    , ^MET$   
# 9   , ^SE$    , ^CSO$   
# 9   , ^SEG$   , ^CSO$   
# 9   , ^CG2$   , ^THR$   
# 9   , ^CG1$   , ^VAL$   
# 9   , ^CG2$   , ^VAL$   
# 9   , ^CM[A-D]$, ^HEM$   
# 9   , ^C1$    , ^MPD$   
# 9   , ^C5$    , ^MPD$   
# 9   , ^C6$    , ^MPD$   
# 9   , ^C[345]$, ^PC$    
# 9   , ^C[78]M$, ^FMN$   
# 9   , ^C16$   , ^ALK$   
# 9   , ^C14$   , ^MYR$   
# 9   , ^SEG$   , ^.*$    
##################################
# 10  , ^C$     , ^.*$    
# 10  , ^CG$    , ^ASN|ASP|ASX|HIS|HIP|HIE|HID|HISN|HISL|LEU|PHE|TRP|TYR$
# 10  , ^CZ$    , ^ARG$   
# 10  , ^CD$    , ^GLU|GLN|GLX$
# 10  , ^CD2$   , ^TRP$   
# 10  , ^CE2$   , ^TRP$   
# 10  , ^CZ$    , ^TYR$   
# 10  , ^C[1-4][A-D]$, ^HEM$   
# 10  , ^CG[AD]$, ^HEM$   
# 10  , ^C2$    , ^MPD$   
# 10  , ^C[2478]$, ^FMN$   
# 10  , ^C[459]A$, ^FMN$   
# 10  , ^C10$   , ^FMN$   
# 10  , ^C01$   , ^ALK|MYR$
##################################
# 11  , ^CE1|CD2$, ^HIS|HID|HIE|HIP|HISL$
# 11  , ^C[DE][12]$, ^PHE$   
# 11  , ^CZ$    , ^PHE$   
# 11  , ^CD1$   , ^TRP$   
# 11  , ^CE3$   , ^TRP$   
# 11  , ^CZ2$   , ^TRP$   
# 11  , ^CZ3$   , ^TRP$   
# 11  , ^CH2$   , ^TRP$   
# 11  , ^C[DE][12]$, ^TYR$   
# 11  , ^CH[A-D]$, ^HEM$   
# 11  , ^C[AB][BC]$, ^HEM$   
# 11  , ^C[69]$ , ^FMN$   
# 11  , ^A.*$   , ^.*$    
##################################
# 12  , ^SG$    , ^CYH$   
##################################
# 13  , ^P$     , ^.*$    
# 13  , ^LP[12]$, ^CYS|MET$
# 13  , ^SG$    , ^CY[SXM]$
# 13  , ^SD$    , ^MET$   
# 13  , ^S[1-7]$, ^FS[34]$
# 13  , ^S$     , ^SO4|SUL$
# 13  , ^P1$    , ^PC$    
# 13  , ^S.*$   , ^.*$    
# 13  , ^P[A-D]$, ^.*$    
# 13  , ^P.*$   , ^.*$    
# 13  , ^.P.*$  , ^FAD|NAD|AMX|APU$
##################################
# 14  , ^ND1$   , ^HIS|HIE|HISL$
# 14  , ^NE2$   , ^HID|HISL$
# 14  , ^RE2$   , ^HID|HISL$
# 14  , ^N[A-D]$, ^HEM$   
# 14  , ^N [A-D]$, ^HEM$   
# 14  , ^N[123]$, ^AZI$   
# 14  , ^N1$    , ^PC$    
# 14  , ^N3$    , ^FMN$   
##################################
# 15  , ^[0-9]*H.*$, ^.*$    
# 15  , ^[0-9]*D.*$, ^.*$    
# 15  , ^.H.*$  , ^FAD|NAD|AMX|APU$
##################################
# 17  , ^BAL$   , ^BIG$   
##################################
# 18  , ^CA$    , ^CA$    
##################################
# 19  , ^ZN$    , ^.*$    
##################################
# 20  , ^CU$    , ^.*$    
##################################
# 21  , ^FE[1-7]$, ^FS[34]$
# 21  , ^FE1$   , ^FEO$   
# 21  , ^FE2$   , ^FEO$   
# 21  , ^FE$    , ^HEM$   
##################################
# 22  , ^CD$    , ^CD$    
# 22  , ^CD  $  , ^.*$    
##################################
# 23  , ^POI$   , ^POI$   
# 23  , ^DOT$   , ^DOT$   
##################################
# 24  , ^MN$    , ^.*$    
##################################
# 25  , ^FE$    , ^.*$    
##################################
# 26  , ^MG$    , ^.*$    
##################################
# 27  , ^MN$    , ^.*$    
##################################
# 28  , ^CO$    , ^.*$    
##################################
# 29  , ^SE$    , ^.*$    
##################################
# 31  , ^YB$    , ^.*$    
##################################
"""


ATOM_PATTERNS = {0: '^[0-9]*H.*$', 1: '^[0-9]*D.*$', 2: '^O.*$', 3: '^CA$', 4: '^CD$', 5: '^CD  $', 6: '^CA$',
                 7: '^N$', 8: '^CA$', 9: '^C$', 10: '^O$', 11: '^P$', 12: '^CB$', 13: '^CB$', 14: '^CB$', 15: '^CG$',
                 16: '^CG$', 17: '^CG$', 18: '^CG$', 19: '^O1$', 20: '^O2$', 21: '^CH3$', 22: '^CD$', 23: '^NE$',
                 24: '^RE$', 25: '^CZ$', 26: '^NH[12][AB]?$', 27: '^RH[12][AB]?$', 28: '^OD1$', 29: '^ND2$',
                 30: '^AD1$', 31: '^AD2$', 32: '^OD[12][AB]?$', 33: '^ED[12][AB]?$', 34: '^OD1[AB]?$', 35: '^ND2$',
                 36: '^AD1$', 37: '^AD2$', 38: '^OD2$', 39: '^LP[12]$', 40: '^SG$', 41: '^SG$', 42: '^OE[12][AB]?$',
                 43: '^EE[12][AB]?$', 44: '^CD$', 45: '^OE1$', 46: '^NE2$', 47: '^AE[12]$', 48: '^CE1|CD2$',
                 49: '^ND1$', 50: '^ND1$', 51: '^RD1$', 52: '^NE2$', 53: '^RE2$', 54: '^NE2$', 55: '^RE2$',
                 56: '^A[DE][12]$', 57: '^CG1$', 58: '^CG2$', 59: '^CD|CD1$', 60: '^CD1$', 61: '^CD2$',
                 62: '^C[GDE]$', 63: '^NZ$', 64: '^KZ$', 65: '^SD$', 66: '^CE$', 67: '^C[DE][12]$', 68: '^CZ$',
                 69: '^C[GD]$', 70: '^SE$', 71: '^SEG$', 72: '^OD1$', 73: '^OD2$', 74: '^OG$', 75: '^OG1$',
                 76: '^CG2$', 77: '^CD1$', 78: '^CD2$', 79: '^CE2$', 80: '^NE1$', 81: '^CE3$', 82: '^CZ2$',
                 83: '^CZ3$', 84: '^CH2$', 85: '^C[DE][12]$', 86: '^CZ$', 87: '^OH$', 88: '^CG1$', 89: '^CG2$',
                 90: '^CD$', 91: '^CE$', 92: '^FE[1-7]$', 93: '^S[1-7]$', 94: '^OXO$', 95: '^FE1$', 96: '^FE2$',
                 97: '^O1$', 98: '^O2$', 99: '^FE$', 100: '^CH[A-D]$', 101: '^N[A-D]$', 102: '^N [A-D]$',
                 103: '^C[1-4][A-D]$', 104: '^CM[A-D]$', 105: '^C[AB][AD]$', 106: '^CG[AD]$', 107: '^O[12][AD]$',
                 108: '^C[AB][BC]$', 109: '^OH2$', 110: '^N[123]$', 111: '^C1$', 112: '^C2$', 113: '^C3$',
                 114: '^C4$', 115: '^C5$', 116: '^C6$', 117: '^O7$', 118: '^O8$', 119: '^S$', 120: '^O[1234]$',
                 121: '^O[1234]$', 122: '^O4$', 123: '^P1$', 124: '^O[123]$', 125: '^C[12]$', 126: '^N1$',
                 127: '^C[345]$', 128: '^BAL$', 129: '^POI$', 130: '^DOT$', 131: '^CU$', 132: '^ZN$', 133: '^MN$',
                 134: '^FE$', 135: '^MG$', 136: '^MN$', 137: '^CO$', 138: '^SE$', 139: '^YB$', 140: '^N1$',
                 141: '^C[2478]$', 142: '^O2$', 143: '^N3$', 144: '^O4$', 145: '^C[459]A$', 146: '^N5$',
                 147: '^C[69]$', 148: '^C[78]M$', 149: '^N10$', 150: '^C10$', 151: '^C[12345]\\*$',
                 152: '^O[234]\\*$', 153: '^O5\\*$', 154: '^OP[1-3]$', 155: '^OT1$', 156: '^C01$', 157: '^C16$',
                 158: '^C14$', 159: '^C.*$', 160: '^SEG$', 161: '^OXT$', 162: '^OT.*$', 163: '^E.*$', 164: '^S.*$',
                 165: '^C.*$', 166: '^A.*$', 167: '^O.*$', 168: '^N.*$', 169: '^R.*$', 170: '^K.*$', 171: '^P[A-D]$',
                 172: '^P.*$', 173: '^.O.*$', 174: '^.N.*$', 175: '^.C.*$', 176: '^.P.*$', 177: '^.H.*$'}

RESIDUE_PATTERNS = {0: '^.*$', 1: '^.*$', 2: '^WAT|HOH|H2O|DOD|DIS$', 3: '^CA$', 4: '^CD$', 5: '^.*$', 6: '^ACE$',
                    7: '^.*$', 8: '^.*$', 9: '^.*$', 10: '^.*$', 11: '^.*$', 12: '^ALA$', 13: '^ILE|THR|VAL$',
                    14: '^.*$', 15: '^ASN|ASP|ASX|HIS|HIP|HIE|HID|HISN|HISL|LEU|PHE|TRP|TYR$',
                    16: '^ARG|GLU|GLN|GLX|MET$', 17: '^LEU$', 18: '^.*$', 19: '^GLN$', 20: '^GLN$', 21: '^ACE$',
                    22: '^ARG$', 23: '^ARG$', 24: '^ARG$', 25: '^ARG$', 26: '^ARG$', 27: '^ARG$', 28: '^ASN$',
                    29: '^ASN$', 30: '^ASN$', 31: '^ASN$', 32: '^ASP$', 33: '^ASP$', 34: '^ASX$', 35: '^ASX$',
                    36: '^ASX$', 37: '^ASX$', 38: '^ASX$', 39: '^CYS|MET$', 40: '^CY[SXM]$', 41: '^CYH$',
                    42: '^GLU$', 43: '^GLU$', 44: '^GLU|GLN|GLX$', 45: '^GLN$', 46: '^GLN$', 47: '^GLN|GLX$',
                    48: '^HIS|HID|HIE|HIP|HISL$', 49: '^HIS|HIE|HISL$', 50: '^HID|HIP$', 51: '^HID|HIP$',
                    52: '^HIS|HIE|HIP$', 53: '^HIS|HIE|HIP$', 54: '^HID|HISL$', 55: '^HID|HISL$',
                    56: '^HIS|HID|HIP|HISD$', 57: '^ILE$', 58: '^ILE$', 59: '^ILE$', 60: '^LEU$', 61: '^LEU$',
                    62: '^LYS$', 63: '^LYS$', 64: '^LYS$', 65: '^MET$', 66: '^MET$', 67: '^PHE$', 68: '^PHE$',
                    69: '^PRO|CPR$', 70: '^CSO$', 71: '^CSO$', 72: '^CSO$', 73: '^CSO$', 74: '^SER$', 75: '^THR$',
                    76: '^THR$', 77: '^TRP$', 78: '^TRP$', 79: '^TRP$', 80: '^TRP$', 81: '^TRP$', 82: '^TRP$',
                    83: '^TRP$', 84: '^TRP$', 85: '^TYR$', 86: '^TYR$', 87: '^TYR$', 88: '^VAL$', 89: '^VAL$',
                    90: '^.*$', 91: '^.*$', 92: '^FS[34]$', 93: '^FS[34]$', 94: '^FS3$', 95: '^FEO$', 96: '^FEO$',
                    97: '^HEM$', 98: '^HEM$', 99: '^HEM$', 100: '^HEM$', 101: '^HEM$', 102: '^HEM$', 103: '^HEM$',
                    104: '^HEM$', 105: '^HEM$', 106: '^HEM$', 107: '^HEM$', 108: '^HEM$', 109: '^HEM$', 110: '^AZI$',
                    111: '^MPD$', 112: '^MPD$', 113: '^MPD$', 114: '^MPD$', 115: '^MPD$', 116: '^MPD$', 117: '^MPD$',
                    118: '^MPD$', 119: '^SO4|SUL$', 120: '^SO4|SUL$', 121: '^PO4|PHO$', 122: '^PC$', 123: '^PC$',
                    124: '^PC$', 125: '^PC$', 126: '^PC$', 127: '^PC$', 128: '^BIG$', 129: '^POI$', 130: '^DOT$',
                    131: '^.*$', 132: '^.*$', 133: '^.*$', 134: '^.*$', 135: '^.*$', 136: '^.*$', 137: '^.*$',
                    138: '^.*$', 139: '^.*$', 140: '^FMN$', 141: '^FMN$', 142: '^FMN$', 143: '^FMN$', 144: '^FMN$',
                    145: '^FMN$', 146: '^FMN$', 147: '^FMN$', 148: '^FMN$', 149: '^FMN$', 150: '^FMN$', 151: '^FMN$',
                    152: '^FMN$', 153: '^FMN$', 154: '^FMN$', 155: '^ALK|MYR$', 156: '^ALK|MYR$', 157: '^ALK$',
                    158: '^MYR$', 159: '^ALK|MYR$', 160: '^.*$', 161: '^.*$', 162: '^.*$', 163: '^.*$', 164: '^.*$',
                    165: '^.*$', 166: '^.*$', 167: '^.*$', 168: '^.*$', 169: '^.*$', 170: '^.*$', 171: '^.*$',
                    172: '^.*$', 173: '^FAD|NAD|AMX|APU$', 174: '^FAD|NAD|AMX|APU$', 175: '^FAD|NAD|AMX|APU$',
                    176: '^FAD|NAD|AMX|APU$', 177: '^FAD|NAD|AMX|APU$'}

ATOM_NUM = {0: 15, 1: 15, 2: 2, 3: 18, 4: 22, 5: 22, 6: 9, 7: 4, 8: 7, 9: 10, 10: 1, 11: 13, 12: 9, 13: 7, 14: 8,
            15: 10, 16: 8, 17: 7, 18: 8, 19: 3, 20: 3, 21: 9, 22: 8, 23: 4, 24: 4, 25: 10, 26: 5, 27: 5, 28: 1,
            29: 5, 30: 3, 31: 3, 32: 3, 33: 3, 34: 1, 35: 5, 36: 3, 37: 3, 38: 3, 39: 13, 40: 13, 41: 12, 42: 3,
            43: 3, 44: 10, 45: 1, 46: 5, 47: 3, 48: 11, 49: 14, 50: 4, 51: 4, 52: 4, 53: 4, 54: 14, 55: 14, 56: 4,
            57: 8, 58: 9, 59: 9, 60: 9, 61: 9, 62: 8, 63: 6, 64: 6, 65: 13, 66: 9, 67: 11, 68: 11, 69: 8, 70: 9,
            71: 9, 72: 3, 73: 3, 74: 2, 75: 2, 76: 9, 77: 11, 78: 10, 79: 10, 80: 4, 81: 11, 82: 11, 83: 11, 84: 11,
            85: 11, 86: 10, 87: 2, 88: 9, 89: 9, 90: 8, 91: 8, 92: 21, 93: 13, 94: 1, 95: 21, 96: 21, 97: 1, 98: 1,
            99: 21, 100: 11, 101: 14, 102: 14, 103: 10, 104: 9, 105: 8, 106: 10, 107: 3, 108: 11, 109: 2, 110: 14,
            111: 9, 112: 10, 113: 8, 114: 7, 115: 9, 116: 9, 117: 2, 118: 2, 119: 13, 120: 3, 121: 3, 122: 3,
            123: 13, 124: 3, 125: 8, 126: 14, 127: 9, 128: 17, 129: 23, 130: 23, 131: 20, 132: 19, 133: 24, 134: 25,
            135: 26, 136: 27, 137: 28, 138: 29, 139: 31, 140: 4, 141: 10, 142: 1, 143: 14, 144: 1, 145: 10, 146: 4,
            147: 11, 148: 9, 149: 4, 150: 10, 151: 8, 152: 2, 153: 3, 154: 3, 155: 3, 156: 10, 157: 9, 158: 9,
            159: 8, 160: 9, 161: 3, 162: 3, 163: 3, 164: 13, 165: 7, 166: 11, 167: 1, 168: 4, 169: 4, 170: 6,
            171: 13, 172: 13, 173: 1, 174: 4, 175: 7, 176: 13, 177: 15}

# 15 -> H
ELEMENT_NAME ={
  1: "O",
  2: "O",
  3: "O",
  4: "N",
  5: "N",
  6: "N",  # Also K
  7: "C",
  8: "C",
  9: "C",
  10: "C",
  11: "C",
  12: "S",
  13: "S",  # Also P
  14: "N",
  15: "H",
  17: "UNK",
  18: "C",
  19: "ZN",
  20: "CU",
  21: "FE",
  22: "C",
  23: "UNK",
  24: "MN",
  25: "FE",
  26: "MG",
  27: "MN",
  28: "C",
  29: "S",
  31: "UNK",
}

element_color_map = {
  # BASIC ELEMENTS
  "C": [0.5, 0.5, 0.5],
  "H": [1, 1, 1],
  "N": [0, 0, 1],
  "O": [1, 0, 0],
  "S": [1, 1, 0],
  "P": [1, 0.6, 0.4],

  # METALS
  "NA": [0.7, 0.7, 0.1],
  "MG": [0.7, 0.7, 0.1],
  "CA": [0.7, 0.7, 0.1],
  "K" : [0, 0.5, 1],
  "ZN": [0.8, 0.4, 0.1],
  "CU": [0.8, 0.4, 0.1],
  "FE": [0.8, 0.4, 0.1],
  "MN": [0.6, 0, 0.4],

  # UNKNOWNS
  "UNK": [0.5, 0.5, 0.5],
  "U": [0.5, 0.5, 0.5],
}

####################################################################################################
################################# Generate Open3D readable object ##################################
####################################################################################################
def getAtomNum(atom="", residue=""):
  """
  Get the atomic number of an atom based on its atom name and residue name.
  Args:
    atom (str): atom name
    residue (str): residue name
  """
  atom = atom.replace(" ", "")
  residue = residue.replace(" ", "")
  for pat in range(len(ATOM_NUM)):
    if re.match(ATOM_PATTERNS[pat], atom) and re.match(RESIDUE_PATTERNS[pat], residue):
      break
  if pat == len(ATOM_NUM):
    print(f"Warning: Atom {atom} in {residue} not found in the available patterns. Using default radius of 0.01")
    return "U"
  else:
    return ELEMENT_NAME.get(ATOM_NUM[pat], "U")


def rotation_matrix_from_vectors(vec1, vec2):
  """ 
  Find the rotation matrix that aligns vec1 to vec2
  Args: 
    vec1: A 3d "source" vector
    vec2: A 3d "destination" vector
  Returns:
    mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
  """
  a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
  v = np.cross(a, b)
  c = np.dot(a, b)
  s = np.linalg.norm(v)
  kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
  rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
  return rotation_matrix


def create_sphere(center, radius=0.5, color=[0, 0, 1]):
  sphere = o3d.geometry.TriangleMesh.create_sphere(radius)
  sphere.paint_uniform_color(color)
  sphere.translate(center)
  sphere.compute_vertex_normals()
  return sphere


def create_box(center, size=0.5, color=[0, 0, 1]):
  box = o3d.geometry.TriangleMesh.create_box(size, size, size)
  box.paint_uniform_color(color)
  box.translate(center)
  box.compute_vertex_normals()
  return box
  
def create_cylinder(start, end, radius=0.2, color=[0.4275, 0.2941, 0.0745]):
  vec = end - start
  length = np.linalg.norm(vec)
  cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius, length)
  cylinder.paint_uniform_color(color)
  
  direction = vec / length
  if list(direction) != [0,0,1]:
    rot = rotation_matrix_from_vectors([0, 0, 1], direction)  # Change to z-axis
    cylinder.rotate(rot, center=[0, 0, 0])  # Rotate around the origin
  
  mid = (start + end) / 2
  cylinder.translate(mid - cylinder.get_center())
  cylinder.compute_vertex_normals()
  return cylinder


def create_bounding_box(dims, origin=[0,0,0]):
  boxpoints = np.array([
    [0,0,0],
    [dims[0],0,0],
    [0, dims[1], 0],
    [0,0,dims[2]],
    [dims[0], dims[1], 0],
    [dims[0], 0, dims[2]],
    [0, dims[1], dims[2]],
    [dims[0], dims[1], dims[2]],
  ])
  if origin != [0,0,0]:
    boxpoints += np.asarray(origin)
  lines = [
    [0,1], [0,2], [0,3], [1,4],
    [1,5], [2,4], [2,6], [3,5],
    [3,6], [4,7], [5,7], [6,7],
  ]
  ret = []
  for line in lines:
    cylinder = create_cylinder(boxpoints[line[0]], boxpoints[line[1]], radius=0.1, color=[0,0,1])
    cylinder.compute_vertex_normals()
    ret.append(cylinder)
  return ret


def traj_to_o3d(traj): 
  atoms = list(traj.top.atoms)
  residues = list(traj.top.residues)
  coords = list(traj.xyz[0])
  geometries = []
  for idx, c in enumerate(coords):
    theatom = atoms[idx]
    resname = residues[theatom.resid].name
    atomtype = getAtomNum(theatom.name, resname)
    print(f"Atom Name: {theatom.name:8s} | Res Name: {resname:8s} | ---> {atomtype} |")
    color = element_color_map.get(atomtype, [0.5,0.5,0.5])
    geometries.append(create_sphere(c, radius=0.5, color=color))
  for bond in list(traj.top.bonds):
    n_i, n_j = bond.indices
    pos_1 = coords[n_i]
    pos_2 = coords[n_j]
    if np.linalg.norm(pos_1 - pos_2) < 3:      # Simple condition to check if there is a bond
      geometries.append(create_cylinder(pos_1, pos_2, radius=0.15))
  return geometries


def molecule_to_o3d(pdb_path):
  # Load PDB structure
  from pytraj import load as ptload
  structure = ptload(pdb_path)
  atoms = list(structure.top.atoms)
  residues = list(structure.top.residues)
  coords = list(structure.xyz[0])

  # Add spheres as each atom
  geometries = []
  for idx, c in enumerate(coords):
    theatom = atoms[idx]
    resname = residues[theatom.resid].name
    atomtype = getAtomNum(theatom.name, resname)
    print(f"Atom Name: {theatom.name:8s} | Res Name: {resname:8s} | ---> {atomtype} |")
    color = element_color_map.get(atomtype, [0.5,0.5,0.5])
    geometries.append(create_sphere(c, radius=0.5, color=color))

  # Add cylinders as bonds
  for bond in list(structure.top.bonds):
    n_i, n_j = bond.indices
    pos_1 = coords[n_i]
    pos_2 = coords[n_j]
    if np.linalg.norm(pos_1 - pos_2) < 3:  # Simple condition to check if there is a bond
      geometries.append(create_cylinder(pos_1, pos_2, radius=0.15))
  return geometries


def xyzr_to_o3d(xyzr_path, radius_factor=1.0):
  # Load PDB structure
  with open(xyzr_path, "r") as f:
    lines = f.readlines()
  coords = []
  radii = []
  for line in lines:
    line = line.strip().split()
    coords.append([float(line[0]), float(line[1]), float(line[2])])
    radii.append(float(line[3]))
  coords = np.array(coords)
  radii = np.array(radii)*radius_factor
  geometries = []
  for idx, c in enumerate(coords):
    color = [0.5,0.5,0.5]
    geometries.append(create_sphere(c, radius=radii[idx], color=color))
    # geometries.append(create_box(c, size=radii[idx], color=color))
  return geometries


def return_geom(obj, settings):
  if isinstance(obj, (o3d.geometry.TriangleMesh)):
    retobj = obj
    if settings.autonormal:
      ret_obj = retobj.compute_vertex_normals()
    if settings.wireframe:
      retobj = o3d.geometry.LineSet.create_from_triangle_mesh(obj)
    return retobj
  else:
    return obj


def color_geom(obj, index, cmap=None):
  if isinstance(obj, (o3d.geometry.TriangleMesh)):
    if cmap:
      color_map = cm.get_cmap(cmap)
      color = cmap(color_map)
      obj.paint_uniform_color(color)
    elif (cmap == "uniform"):
      obj.paint_uniform_color([1, 0, 0])
    elif (cmap == "random"):
      obj.paint_uniform_color(np.random.rand(3))
    else:
      color_map = cm.get_cmap("jet")
      color = color_map(index)
      obj.paint_uniform_color(color)
  return obj


def view3d_parser():
  parser = argparse.ArgumentParser(description='View 3D objects')
  # Add additional objects for reference
  parser.add_argument('-c', '--cube', type=float, default=0, help='Length of cube')
  parser.add_argument('-ccenter', '--cube_center', nargs=3, type=float, help='Center of cube')
  parser.add_argument('-s', '--sphere', type=float, default=0, help='Radius of sphere')
  parser.add_argument('-scenter', '--sphere_center', nargs=3, type=float, help='Center of sphere')
  parser.add_argument('-cf', '--coordinate_frame', type=int, default=0, help='Whether or not to add an additional coordinate frame')

  parser.add_argument('-w', '--wireframe', type=int, default=0, help='Whether or not to use lines instead of triangles')
  parser.add_argument('-n', '--autonormal', type=int, default=1, help='Whether or not to use the normals from the mesh file')
  parser.add_argument('-cmap', '--color_map', type=str, default=None, help='Color map to use for the mesh')
  parser.add_argument('-d', '--debug', type=int, default=0, help='Whether or not to use the normals from the mesh file')
  args, other_args = parser.parse_known_args()
  return (args, other_args)


def view3d_runner():
  # Supported MolFormat: pdb, sdf, mol2
  # Supported ObjFormat: pcd, obj, ply, off, xyzr
  settings, filelist = view3d_parser()
  if settings.debug:
    print("The following files will be rendered: \n", filelist, "\n")
    print("With the following configurations: \n", settings, "\n")

  final_geometries = []
  for file in filelist:
    if not os.path.exists(file):
      raise Exception(f"File {file} does not exist.")
    if ".pdb" in file or ".mol2" in file or ".sdf" in file:
      geometries = molecule_to_o3d(file)
      if settings.autonormal:
        for geo in geometries:
          geo.compute_vertex_normals()
      final_geometries += geometries
    elif ".ply" in file or ".obj" in file or ".off" in file:
      try:
        mesh = o3d.io.read_triangle_mesh(file)
        if np.array(mesh.triangles).shape[0] == 0:
          raise Exception("No face normals found in the ply file.")
      except:
        # If failed to read as triangle mesh, try to read as point cloud
        mesh = o3d.io.read_point_cloud(file)
      if settings.autonormal and isinstance(mesh, (o3d.geometry.TriangleMesh)):
        # Compute the norm of triangle mesh if it is a triangle mesh
        mesh.compute_vertex_normals()
      mesh.paint_uniform_color([0.5,0.1,0.1])
      newgeo = return_geom(mesh, settings)
      final_geometries += [newgeo]
    elif ".xyzr" in file:
      xyzr_geoms = xyzr_to_o3d(file, radius_factor=1)
      final_geometries += xyzr_geoms
    else:
      print(f"Warning: {file} is not a supported file type. Skipping...")
      print(f"Check this website for supported file types: http://www.open3d.org/docs/0.9.0/tutorial/Basic/file_io.html")

  if settings.cube:
    c_length = settings.cube
    if settings.cube_center:
      c_center = settings.cube_center
    else:
      c_center = [0, 0, 0]
    cuboid = create_box(c_center, size=c_length)
    final_geometries += [cuboid]
  if settings.sphere:
    if settings.scenter:
      s_center = settings.scenter
    else:
      s_center = [0, 0, 0]
    mesh = create_sphere(s_center, radius=settings.sphere)
    final_geometries += [mesh]
  if settings.coordinate_frame:
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
    final_geometries += [mesh_frame]

  # Finally draw the geometries
  o3d.visualization.draw_geometries(final_geometries)
  # timestamp = datetime.now().strftime('%Y%m%d_%H%M')
  # o3d.io.write_triangle_mesh(f"/tmp/OBJSET_mesh_{timestamp}.ply", functools.reduce(lambda a, b: a + b, geometries), write_ascii=True)
  # o3d.io.write_triangle_mesh(f"/tmp/OBJSET_surface_{timestamp}.ply", mesh, write_ascii=True)


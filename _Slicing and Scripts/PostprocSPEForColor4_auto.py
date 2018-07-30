
# coding: utf-8

# In[ ]:

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


# In[ ]:




# In[ ]:


import sys
import os

# import typing
# from typing import Optional
# Optional[X] is equivalent to Union[X, None].

# With code originally from https://github.com/amcquistan/Python-read-file-line-by-line
def order_bag_of_words(bag_of_words, desc=False):
    words = [(word, cnt) for word, cnt in bag_of_words.items()]
    return sorted(words, key=lambda x: x[1], reverse=desc)

def record_word_cnt(words, bag_of_words):
    for word in words:
        if word != '':
            if word.lower() in bag_of_words:
                bag_of_words[word.lower()] += 1
            else:
                bag_of_words[word.lower()] = 0

# assumes only one token may begin with Z
def bHasZValue(tokens): # -> Optional[float]:
    bHasZ = False
    for token in tokens:
        if token.startswith('Z'):
            bHasZ = True
            break
    return bHasZ

def bHasValue(tokens, param):
    bHasParamValue = False
    for token in tokens:
        if token.startswith(param):
            bHasParamValue = True;
            break
    return bHasParamValue

# assumes a M907 line begins exactly "M907"
def bIsM907Command(line):
    bIsM907 = False
    if line.startswith("M907"):
        bIsM907 = True
    return bIsM907

# assumes a M900 line begins exactly "M900"
def bIsM900Command(line):
    bIsM900 = False
    if line.startswith("M900"):
        bIsM900 = True
    return bIsM900

# assumes this type of command only if the typeCommand string is the start of the line
# WARNING: that means if you call with e.g. "M1", you'll not only get true M1 commands
#   but also M104, M109, etc.
def bIsSpecifiedCommand(line, typeCommand):
    bIsCommand = False
    if (line.startswith(typeCommand)):
        bIsCommand = True
    return bIsCommand

# we provide a separate comment-checking method to avoid the assumptions inherent in attempting isSpecifiedCommand(line, ";")
def bIsComment(line):
    bIsComment = False
    if (line.strip().startswith(';')):
        bIsComment = True
    return bIsComment

def sGetZValue(tokens):
    bZValue = None
    for token in tokens:
        if token.startswith('Z'):
            bZValue = token.lstrip('Z')
            break
    return bZValue

def sGetValue(tokens, param):
    bParamValue = None
    for token in tokens:
        if token.startswith(param):
            bParamValue = token.lstrip(param)
    return bParamValue




# In[ ]:


# NOTES: total layers are 0 .. n-1
#        e.g. 150 layers at 0.3 mm = 45 mm object
#        layer 0 is 100% "color" 0, layer n-1 is 100% "color" 1
#        that means there are n-2 steps between the two points, for a total of n color mixing ratios specified

def fGetMixRatioExcl(nLayersPerSegment, nCurrentLayerInSegment, sMethod):
    fMaterialPct = 1.0
    
    if "Exponential" == sMethod:
        fMaterialPct = 0.0
    else: # default to linear
        fMaterialPct = float(nCurrentLayerInSegment) / float(nLayersPerSegment) # - 1 -- use ...Incl() version if you need this
        
    return fMaterialPct

def fGetMixRatioIncl(nLayersPerSegment, nCurrentLayerInSegment, sMethod):
    fMaterialPct = 1.0
    
    if "Exponential" == sMethod:
        fMaterialPct = 0.0
    else: # default to linear
        fMaterialPct = float(nCurrentLayerInSegment) / float(nLayersPerSegment - 1)
        
    return fMaterialPct

def printZandMixRatioV2():
    nLayerCount = 119
    
    fFirstLayerHeight = 0.3
    fOtherLayersHeight = 0.35
    
    fCurrentLayerZ = 0
    
    nSegmentNumber = 0 # will go 0..3
    nLayersPerSegment = nLayerCount / 3
    
    for nLayer in range(0, nLayerCount):
        if 0 == nLayer:
            fCurrentLayerZ += fFirstLayerHeight
        else:
            fCurrentLayerZ += fOtherLayersHeight
            
        print str(nLayer + 1) + " at " + str(fCurrentLayerZ)

        fMaterialTwoPct = fGetMixRatio(nLayersPerSegment, nLayer % nLayersPerSegment, "Linear")
        fMaterialOnePct = 1.0 - fMaterialTwoPct
        # fMaterialOnePct = 1.0 - (float(nLayer % nLayersPerSegment) / float(nLayersPerSegment - 1))
        # fMaterialTwoPct = float(nLayer % nLayersPerSegment) / float(nLayersPerSegment - 1)
        
        if 0 == nSegmentNumber:
            print "M567 P0 E{0:.3f}:{1:.3f}:0:0".format(fMaterialOnePct, fMaterialTwoPct)
        elif 1 == nSegmentNumber:
            print "M567 P0 E0:{0:.3f}:{1:.3f}:0".format(fMaterialOnePct, fMaterialTwoPct)
        elif 2 == nSegmentNumber:
            print "M567 P0 E0:0:{0:.3f}:{1:.3f}".format(fMaterialOnePct, fMaterialTwoPct)
        elif 3 == nSegmentNumber:
            print "M567 P0 E{1:.3f}:0:0:{0:.3f}".format(fMaterialOnePct, fMaterialTwoPct)
        else:
            False
            
        if 0 == (nLayer + 1) % nLayersPerSegment:
            nSegmentNumber += 1

# printZandMixRatioV2()

def fGetDynamicMixRatio(fMixStart, fMixEnd, nTotalLayers, nCurrentLayer, sMethod):
    fMaterialPct = 1.0

    # TODO
    if "Elliptic" == sMethod:
        fLinearFactor = float(nCurrentLayer) / float(nTotalLayers - 1)
        
        fMaterialPct = 4 - ((0.12 * fLinearFactor * fLinearFactor) + (1.12 * fLinearFactor) + 2.78)
        fMaterialPct = clamp(fMaterialPct, 0, 1)
        fMaterialPct = float(fMixStart) + float(fMixEnd - fMixStart) * pow(fMaterialPct, 0.5)
    else: # default to linear
        # we go from nMixStart to nMixEnd
        # i.e. nMixStart + (nMixEnd - nMixStart)* nCurrentLayer / (nTotalLayers - 1)
        fMaterialPct = float(fMixStart) + float(fMixEnd - fMixStart) * float(nCurrentLayer) / float(nTotalLayers - 1)
        
    return fMaterialPct

def sGetMix(afStartMix, afEndMix, nTotalLayers, nCurrentLayer, sMethod):
    sMix = ""
    
    for nDriveIndex in range(0, len(afStartMix)):
        sMix += "{0:.3f}".format(fGetDynamicMixRatio(afStartMix[nDriveIndex], afEndMix[nDriveIndex], nTotalLayers, nCurrentLayer, sMethod)) + ":"
    
    return sMix

def printZandMixRatioV3():
    nLayerCount = 11 # 119
    
    anTools = [0, 1, 2, 3]
    # C-Y linear, Y-M linear, M-K elliptic, K-C elliptic
    asTransitionMethod = ["Linear", "Linear", "Elliptic", "Elliptic"]
    
    aafStartMix =       [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    aafEndMix =       [[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 0.0]]
    
    fFirstLayerHeight = 0.3
    fOtherLayersHeight = 0.2
    
    fCurrentLayerZ = 0
    
    # nSegmentNumber = 0 # will go 0..3
    nLayersPerSegment = nLayerCount # / 3
    
    for nLayer in range(0, nLayerCount):
        if 0 == nLayer:
            fCurrentLayerZ += fFirstLayerHeight
        else:
            fCurrentLayerZ += fOtherLayersHeight
            
        print "Layer " + str(nLayer + 1) + " at Z = " + str(fCurrentLayerZ) + " mm"

        for nToolIndex in range(0, len(anTools)):
            print "  tool {} mix {}".format(anTools[nToolIndex], sGetMix(aafStartMix[nToolIndex], aafEndMix[nToolIndex], nLayerCount, nLayer, asTransitionMethod[nToolIndex]))
            
        # print sGetMix(aanStartMix[0], aanEndMix[0], nLayerCount, nLayer, "Linear")
        
        # fMaterialTwoPct = fGetMixRatioIncl(nLayersPerSegment, nLayer % nLayersPerSegment, "Linear")
        # fMaterialOnePct = 1.0 - fMaterialTwoPct
        # # fMaterialOnePct = 1.0 - (float(nLayer % nLayersPerSegment) / float(nLayersPerSegment - 1))
        # # fMaterialTwoPct = float(nLayer % nLayersPerSegment) / float(nLayersPerSegment - 1)
        
        # print "M567 P0 E{0:.3f}:{1:.3f}:0:0".format(fMaterialOnePct, fMaterialTwoPct)
            
        print ""
            
        # if 0 == (nLayer + 1) % nLayersPerSegment:
            # nSegmentNumber += 1

# printZandMixRatioV3()

def sGetMixRatioCommand(nTotalLayers, nSegments, nCurrentLayer):
    nLayersPerSegment = nTotalLayers / nSegments
    nSegmentNumber = nCurrentLayer / (nTotalLayers / nSegments)
    # print "segment {0}, layer {1}".format(nSegmentNumber, nCurrentLayer)
    
    # fMaterialOnePct = 1.0 - (float(nCurrentLayer % nLayersPerSegment) / float(nLayersPerSegment - 1))
    fMaterialTwoPct = fGetMixRatioIncl(nLayersPerSegment, nCurrentLayer % nLayersPerSegment, "Linear") # float(nCurrentLayer % nLayersPerSegment) / float(nLayersPerSegment - 1)
    fMaterialOnePct = 1.0 - fMaterialTwoPct
    
    sCommand = ""
    
    if 0 == nSegmentNumber:
        sCommand = "M567 P0 E{0:.3f}:{1:.3f}:0:0 ; segment {2} layer {3}".format(fMaterialOnePct, fMaterialTwoPct, nSegmentNumber, nCurrentLayer)
    elif 1 == nSegmentNumber:
        sCommand = "M567 P0 E0:{0:.3f}:{1:.3f}:0 ; segment {2} layer {3}".format(fMaterialOnePct, fMaterialTwoPct, nSegmentNumber, nCurrentLayer)
    elif 2 == nSegmentNumber:
        sCommand = "M567 P0 E0:0:{0:.3f}:{1:.3f} ; segment {2} layer {3}".format(fMaterialOnePct, fMaterialTwoPct, nSegmentNumber, nCurrentLayer)
    else:
        # do nothing
        False

    # print "M567 P0 E0:0:0:0".format()
    # return "M567 P0 E0:0:0:0".format()

    # print sCommand
    return sCommand


# In[ ]:




# In[ ]:

#
# PROCESSING STEP
#
# Adjust the following in main:
#   firstLayerHeight = 0.2
#   otherLayerHeight = 0.3
#   fileInPath = "Working/ed_MAN1_frog_x3_T09_supportv5.gcode"
#   fileOutPath = "Working/ed_AUT2_frog_x3_T09_supportv5.gcode"
#

import Queue

# 2018.05.06 MJC working on 30% tower (for solids) (1 of n)

def bHasX(line):
    return bHasValue(line.strip().split(' '), 'X')

def bHasY(line):
    return bHasValue(line.strip().split(' '), 'Y')

def bHasZ(line):
    return bHasValue(line.strip().split(' '), 'Z')

def bHasE(line):
    return bHasValue(line.strip().split(' '), 'E')

def bHasF(line):
    return bHasValue(line.strip().split(' '), 'F')

def bIsMovement(line, bIncludeCheckingComments = False):
    return bIsG0(line, bIncludeCheckingComments) or bIsG1(line, bIncludeCheckingComments)

def bIsG0(line, bIncludeCheckingComments = False):
    return bIsSpecifiedCommand(line.strip(), "G0") or (bIncludeCheckingComments and bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G0"))

def bIsG1(line, bIncludeCheckingComments = False):
    return bIsSpecifiedCommand(line.strip(), "G1") or (bIncludeCheckingComments and bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G1"))

def bDropLineOrCommentOut(line):
    bIsM900 = False
    bIsM907 = False
    bIsM220 = False
    bIsM300 = False
    bIsM1 = False
    
    if bIsM907Command(line.strip()):
        bIsM907 = True
                    
    if bIsM900Command(line.strip()):
        bIsM900 = True
                
    # M220 set speed factor override percentage
    if bIsSpecifiedCommand(line.strip(), "M220"):
        bIsM220 = True

    if bIsSpecifiedCommand(line.strip(), "M300"):
        bIsM300 = True

    if bIsSpecifiedCommand(line.strip(), "M1"):
        bIsM1 = True
    
    return bIsM907 or bIsM900 or bIsM220 or bIsM300 or bIsM1

def bDropLineEntirely(line):
    bIsM900 = False
    bIsM907 = False
    bIsM220 = False
    bIsM300 = False
    
    if bIsM907Command(line.strip()):
        bIsM907 = True
                    
    if bIsM900Command(line.strip()):
        bIsM900 = True
                
    # M220 set speed factor override percentage
    if bIsSpecifiedCommand(line.strip(), "M220"):
        bIsM220 = True

    if bIsSpecifiedCommand(line.strip(), "M300"):
        bIsM300 = True

    return bIsM907 or bIsM900 or bIsM220 or bIsM300

bToolLoaded = True # MC 2018.04.30
fFilamentExtruded = 0.0
        
bInToolchangeSequence = False
        
bInLoadSequence = False
bInUnloadSequence = False # generally will be true when bToolLoaded is false, but for before the initial toolchange
bHasReadFirstUnloadCommandLine = False
bHasSeenM104Command = False
bIgnoreRestOfUnloadSequence = False
bInWipeSequence = False
nLinesWithinSequence = 0
        
bAddLinePost = False
sAddLine = ""

def bDropChangeCommand(line):
# def bDropChangeCommand(line, bToolLoaded, fFilamentExtruded, bInToolchangeSequence, bInLoadSequence, bInUnloadSequence, \
  # bHasReadFirstUnloadCommandLine, bHasSeenM104Command, bIgnoreRestOfUnloadSequence, bInWipeSequence, nLinesWithinSequence, bAddLinePost, sAddLine):
    bStripChangeCommand = False
    
    global bToolLoaded
    global fFilamentExtruded
        
    global bInToolchangeSequence
        
    global bInLoadSequence
    global bInUnloadSequence
    global bHasReadFirstUnloadCommandLine
    global bHasSeenM104Command
    global bIgnoreRestOfUnloadSequence
    global bInWipeSequence
    global nLinesWithinSequence
        
    global bAddLinePost
    global sAddLine
    
    if "TOOLCHANGE" in line:
        bInUnloadSequence = False
        bInLoadSequence = False
        bInWipeSequence = False
                    
        if "TOOLCHANGE START" in line:
            bInToolchangeSequence = True
            print("\r\nToolchange start...")

        elif "TOOLCHANGE UNLOAD" in line: # -1 <> line.upper().find("UNLOAD"):
            bInUnloadSequence = True
            bHasReadFirstUnloadCommandLine = False
            bHasSeenM104Command = False
            bIgnoreRestOfUnloadSequence = False
            nLinesWithinSequence = 0
        
            fFilamentExtruded = 0.0
            print("Unload...")

        elif "TOOLCHANGE LOAD" in line:
            bInLoadSequence = True
            nLinesWithinSequence = 0
                        
            if bToolLoaded:
                print("ERROR: Loading tool, but tool already loaded!")
            else:
                bToolLoaded = True
            print("  Total unload filament driven: {}".format(fFilamentExtruded))
            fFilamentExtruded = 0.0
            print("Load...")

        elif "TOOLCHANGE WIPE" in line:
            bInWipeSequence = True
            nLinesWithinSequence = 0

            if bToolLoaded:
                bToolLoaded = False
            else:
                print("ERROR: Unloading tool, but no tool loaded!")
            print("  Total load filament driven: {}".format(fFilamentExtruded))
            print("Wipe...")

        elif "TOOLCHANGE END" in line:
            bInToolchangeSequence = False
            print("Toolchange end.\r\n")

    else: # not itself a TOOLCHANGE "command" line (G-Code comment, but used as command to this script)
        if bInUnloadSequence:
            # from design doc: "read first line, should be XY(F) move line (no E)"
            #                  "  then place the toolchange command here (will need to be sought in the file, or tracked/predicted otherwise)"
            if not bHasReadFirstUnloadCommandLine and bHasValue(line.strip().split(' '), 'X') and bHasValue(line.strip().split(' '), 'Y') and not bHasValue(line.strip().split(' '), 'E'):
                print("  Found XY(F) line and placing toolchange following ({})".format(line.strip()))
                bAddLinePost = True
                sAddLine = "Tx\r\n"
                            
                True

            # from design doc: "read all remaining lines"
            if bHasReadFirstUnloadCommandLine and not bIgnoreRestOfUnloadSequence:
                if bIsMovement(line) and bHasE(line) and not bHasX(line) and not bHasY(line):
                    # "if line is E(F) (no X or Y) only, comment line"
                    bStripChangeCommand = True # bStripCommand = True
                    # print("  Stripping E(F) line ({})".format(line.strip()))
                elif bIsSpecifiedCommand(line.strip(), "M104"):
                    # "if line is M104, comment line"
                    bStripChangeCommand = True
                    bHasSeenM104Command = True
                    print("  Stripping M104 line ({})".format(line.strip()))
                elif bHasSeenM104Command and bIsMovement(line) and bHasX(line) and bHasE(line) and not bHasY(line):
                    # "if line is XE(F) (no Y) only following M104, comment line"
                    bStripChangeCommand = True
                    # print("  Stripping post-M104 XE(F) line ({})".format(line.strip()))
                elif bIsSpecifiedCommand(line.strip(), "G4"):
                    # "if line is G4, ignore all subsequent lines"
                    bIgnoreRestOfUnloadSequence = True
                        
            bHasReadFirstUnloadCommandLine = True
            # WARNING/TODO: does not care if it's a comment or not!

            True
        elif bInLoadSequence:
            if bIsMovement(line) and bHasE(line) and (9.99 < float(sGetValue(line.strip().split(' '), 'E'))):
                bStripChangeCommand = True
                # print("  Stripping extrusion g.t.e. 10 line ({})".format(line.strip()))
                            
                True
                        
            True
        elif bInWipeSequence:
            if bIsMovement(line) and bHasX(line) and not bHasY(line) and not bHasE(line):
                bStripChangeCommand = True
                # print("  Stripping X(F) line ({})".format(line.strip()))
                            
                True
                        
            True
                        
    return bStripChangeCommand


def main():
    # TODO: fix/remove this hardcode construct if you're actually running from command line

    bVerbose = False
    
    firstLayerHeight = 0.2
    otherLayerHeight = 0.3
    fileInPath = "Working/ed_MAN1_frog_x3_T09_supportv5.gcode"
    fileOutPath = "Working/ed_AUT2_frog_x3_T09_supportv5.gcode"

    # if len(sys.argv) < 2:
        # filepath = input("Enter file path here:")
    # else:
        # filepath = sys.argv[1]

    if not os.path.isfile(fileInPath):
        print("File path {} does not exist. Exiting...".format(fileInPath))
        sys.exit()

    # The output file should not exist -- warn and quit if it does
    if os.path.isfile(fileOutPath):
        print("Output file path {} exists. Exiting...".format(fileOutPath))
        sys.exit()
        
    fNextZBreak = firstLayerHeight
    with open(fileInPath) as fileIn:
        cnt = 0

        nTotalLayers = 0
        
        # OLD: Once this gets set True once, we can assume that we're inside the TOOLCHANGE UNLOAD ... TOOLCHANGE LOAD region whenever it is False afterward
        global bToolLoaded
        global fFilamentExtruded
        
        global bInToolchangeSequence
        
        global bInLoadSequence
        global bInUnloadSequence
        global bHasReadFirstUnloadCommandLine
        global bHasSeenM104Command
        global bIgnoreRestOfUnloadSequence
        global bInWipeSequence
        global nLinesWithinSequence
        
        global bAddLinePost
        global sAddLine

        # bToolLoaded = True # MC 2018.04.30
        # fFilamentExtruded = 0.0
        
        # bInToolchangeSequence = False
        
        # bInLoadSequence = False
        # bInUnloadSequence = False # generally will be true when bToolLoaded is false, but for before the initial toolchange
        # bHasReadFirstUnloadCommandLine = False
        # bHasSeenM104Command = False
        # bIgnoreRestOfUnloadSequence = False
        # bInWipeSequence = False
        # nLinesWithinSequence = 0
        
        # bAddLinePost = False
        # sAddLine = ""
        
        with open(fileOutPath, "w+") as fileOut:
            
            line = fileIn.readline()
            while line:
            # for line in fileIn:
                cnt += 1

                # record_word_cnt(line.strip().split(' '), bag_of_words)
                
                bStripCommand = False
                
                # TODO: don't really want a state machine, but it would be the most foolproof checking...
                
                if "BEFORE_LAYER_CHANGE" in line:
                    print "Layer demarcation"
                
                # bAddColorCommand = False
                # sColorCommand = ""
                
                fEpsilon = -0.0001
                
                if (not bIsComment(line)) and bHasZValue(tokens=line.strip().split(' ')):
                    fActualZ = float(sGetZValue(tokens=line.strip().split(' ')))
                    if fNextZBreak + fEpsilon <= fActualZ:
                        print "Layer change sensed based on Z height achieved: planned {0:.2f}, actual {1:.2f}".format(fNextZBreak, fActualZ)
                        fNextZBreak += otherLayerHeight
                        # sColorCommand = sGetMixRatioCommand(139, 3, nTotalLayers)
                        # bAddColorCommand = True
                        nTotalLayers += 1
                
                # bStripChangeCommand = bDropChangeCommand(line, bToolLoaded, fFilamentExtruded, bInToolchangeSequence, bInLoadSequence, bInUnloadSequence, \
                  # bHasReadFirstUnloadCommandLine, bHasSeenM104Command, bIgnoreRestOfUnloadSequence, bInWipeSequence, nLinesWithinSequence, bAddLinePost, sAddLine)
                bStripChangeCommand = bDropChangeCommand(line)

                if (bInLoadSequence or bInUnloadSequence) and                   ((bIsSpecifiedCommand(line.strip(), "G0") or bIsSpecifiedCommand(line.strip(), "G1")) or
                     (bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G0") or bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G1"))) \
                  and bHasValue(line.strip().split(' '), 'E'):
                    nLinesWithinSequence += 1
                        
                    if bIsComment(line):
                        if bVerbose:
                            print "  {} ({}) *comment only".format(sGetValue(line.strip().split(' '), 'E'), cnt)
                        # bStripChangeCommand = True
                        # fFilamentExtruded += float(sGetValue(line.strip().split(' '), 'E'))
                        True
                    else:
                        if bVerbose:
                            print "  {} ({})".format(sGetValue(line.strip().split(' '), 'E'), cnt)
                        # bStripCommand = True
                        # bStripChangeCommand = True
                        fFilamentExtruded += float(sGetValue(line.strip().split(' '), 'E'))
                        # print "fFilamentExtruded to {}".format(fFilamentExtruded)
                        True

                # TODO/WARNING: bypasses bAddLinePost
                if bIsComment(line):
                    fileOut.write(line)
                    line = fileIn.readline()
                    continue
                
                bHasZ = False
                
                # bIsM567 = False
                
                # if bIsSpecifiedCommand(line.strip(), "M567"):
                    # line = fileIn.readline()
                    # continue
                
                bStripCommand = bStripCommand or bDropLineOrCommentOut(line)
                    
                if bIsSpecifiedCommand(line.strip(), "G0") or                   bIsSpecifiedCommand(line.strip(), "G1") or                   bIsSpecifiedCommand(line.strip(), "G4") or                   bIsSpecifiedCommand(line.strip(), "G92") or                   bStripCommand:
                    True
                else:
                    tokens = line.strip().split(' ')
                    if len(tokens[0]) > 0:
                        print("G-Code of interest: {}".format(tokens[0]))

                if bIsSpecifiedCommand(line.strip(), "M221"):
                    print("WARNING: Found M221 command")

                if True == bHasZValue(tokens=line.strip().split(' ')):
                    bHasZ = True
                    # print("line {} transitions to Z = {}".format(cnt, sGetZValue(line.strip().split(' '))))
                    # print("line {} contents {}".format(cnt, line.strip()))

                # Write the Z move BEFORE any color change command
                if bStripCommand:
                    # if bIsM900 or bIsM907 or bIsM220 or bIsM300:
                    if bDropLineEntirely(line):
                        False
                    else:
                        fileOut.write("; {}".format(line))
                elif bStripChangeCommand:
                    False
                else:
                    # fileOut.write(line)
                    
                    # NEW 2018.07.26 If we are writing "Tx", scan ahead to the next "T<x>" line, queueing all lines read
                    #   Replace the "Tx" that is about to be written with "T<x>"
                    #   Write this additional line, then write all the queued lines...
                    
                    q = Queue.Queue()
                    
                    # if ("Tx" == sAddLine):
                    if (bIsSpecifiedCommand(sAddLine, "Tx")):
                        print("Adding Tx now...")
                        q.put(line)
                        
                        # re-enter file and seek so that we can use the simple line2 in fileIn2?
                        
                        line = fileIn.readline()
                        while line:
                            q.put(line)
                            if (bIsSpecifiedCommand(line, "T")):
                                break;
                            line = fileIn.readline()
                        
                        # Now we've just read T<x> line
                        sAddLine = line
                    else:
                        fileOut.write(line)
                    
                    if bAddLinePost:
                        fileOut.write(sAddLine)
                        bAddLinePost = False
                        sAddLine = ""
                        
                    while (not q.empty()):
                        restoreLine = q.get()
                        
                        # if (bDropCommandOrCommentOut(restoreLine)):
                            # if bDropLineEntirely(line):
                                # False
                            # else:
                        # if (bIsSpecifiedCommand(restoreLine, "M1")):
                            # fileOut.write("; {}".format(restoreLine))
                        
                        if (not bDropChangeCommand(restoreLine)):
                            fileOut.write(restoreLine)
                            
                        elif (bIsSpecifiedCommand(restoreLine, "M1")):
                            fileOut.write("; {}".format(restoreLine))
                    
                # if bAddColorCommand:
                    # fileOut.write(sColorCommand)
                    # fileOut.write('\r\n')
                    
                line = fileIn.readline()
                    
            fileOut.close()
            
        print("Total layers: {}".format(nTotalLayers))
    
if __name__ == '__main__':
    print("\r\n!!!\r\n!!! WARNING: This code does not understand z-hop.  Use with caution! !!!\r\n!!!\r\n")
    main()


# In[ ]:




# In[ ]:

#
# VERIFICATION STEP
#
# Adjust the following in vVerifyNoUnload, to match the output file from the processing step:
#   fileInPath = "Working/ed_AUT2_frog_x3_T09_supportv5.gcode"
#

# 2018.05.06 MJC working on 30% tower (for solids) (2 of n)

def vVerifyNoUnload():
    fileInPath = "Working/ed_AUT2_frog_x3_T09_supportv5.gcode"
    
    bAnyErrors = False

    if not os.path.isfile(fileInPath):
        print("File path {} does not exist. Exiting...".format(fileInPath))
        sys.exit()

    fNextZBreak = 0.2
    with open(fileInPath) as fileIn:
        cnt = 0

        nTotalLayers = 0
        
        # Once this gets set True once, we can assume that we're inside the TOOLCHANGE UNLOAD ... TOOLCHANGE LOAD region whenever it is False afterward
        bToolLoaded = True
        fFilamentExtruded = 0.0
        
        bInToolchangeSequence = False
        
        bToolchangeFound = False
        sNewTool = ""
        
        bInLoadSequence = False
        bInUnloadSequence = False # generally will be true when bToolLoaded is false, but for before the initial toolchange
        bInWipeSequence = False
        
        for line in fileIn:
            cnt += 1

            # record_word_cnt(line.strip().split(' '), bag_of_words)
                
            bStripCommand = False
                
            # TODO: don't really want a state machine, but it would be the most foolproof checking...
                
            if "BEFORE_LAYER_CHANGE" in line:
                print "\r\nLayer demarcation"
                
            # bAddColorCommand = False
            # sColorCommand = ""
                
            fEpsilon = -0.0001
            
            if (not bIsComment(line)) and bHasZValue(tokens=line.strip().split(' ')):
                fActualZ = float(sGetZValue(tokens=line.strip().split(' ')))
                if fNextZBreak + fEpsilon <= fActualZ:
                    print "Layer change sensed based on Z height achieved: planned {0:.2f}, actual {1:.2f}".format(fNextZBreak, fActualZ)
                    fNextZBreak += 0.2
                    # sColorCommand = sGetMixRatioCommand(139, 3, nTotalLayers)
                    # bAddColorCommand = True
                    nTotalLayers += 1
                
            if "TOOLCHANGE" in line:
                bInUnloadSequence = False
                bInLoadSequence = False
                bInWipeSequence = False
                    
                if "TOOLCHANGE START" in line:
                    bInToolchangeSequence = True
                    bToolchangeFound = False
                    sNewTool = ""
                    print("\r\nToolchange start...")

                elif "TOOLCHANGE UNLOAD" in line: # -1 <> line.upper().find("UNLOAD"):
                    bInUnloadSequence = True

                    fFilamentExtruded = 0.0
                    print("  Unload...")

                elif "TOOLCHANGE LOAD" in line:
                    bInLoadSequence = True
                    if bToolLoaded:
                        print("ERROR: Loading tool, but tool already loaded!")
                        # bAnyErrors = True
                    else:
                        bToolLoaded = True
                    print("    Total unload filament driven: {}".format(fFilamentExtruded))
                    fFilamentExtruded = 0.0
                    print("  Load...")
                    
                elif "TOOLCHANGE WIPE" in line:
                    bInWipeSequence = True

                    if bToolLoaded:
                        bToolLoaded = False
                    else:
                        print("ERROR: Unloading tool, but no tool loaded!")
                        # bAnyErrors = True
                    print("    Total load filament driven: {}".format(fFilamentExtruded))
                    print("  Wipe...")

                elif "TOOLCHANGE END" in line:
                    bInToolchangeSequence = False
                    print("Toolchange end.")

            else: # not itself a TOOLCHANGE "command" line (G-Code comment, but used as command to this script)
                if bInToolchangeSequence:
                    if bIsSpecifiedCommand(line.strip(), "T"):
                        if not bToolchangeFound:
                            sNewTool = line.strip()
                            bToolchangeFound = True
                        else:
                            if line.strip() <> sNewTool:
                                print("ERROR: Switched to tool {} when G-Code calls for tool {} instead ({})".format(sNewTool, line.strip(), cnt))
                                bAnyErrors = True
                            else:
                                print("  INFO: {} {}".format(sNewTool, line.strip()))
                    
                    True

            if (bInLoadSequence or bInUnloadSequence) and                ((bIsSpecifiedCommand(line.strip(), "G0") or bIsSpecifiedCommand(line.strip(), "G1")) or
                (bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G0") or bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G1"))) \
              and bHasValue(line.strip().split(' '), 'E'):
                if bIsComment(line):
                    # print "{} ({}) *comment only".format(sGetValue(line.strip().split(' '), 'E'), cnt)
                    # fFilamentExtruded += float(sGetValue(line.strip().split(' '), 'E'))
                    True
                else:
                    # print "      {} ({})".format(sGetValue(line.strip().split(' '), 'E'), cnt)
                    # bStripCommand = True
                    fFilamentExtruded += float(sGetValue(line.strip().split(' '), 'E'))
                    # print "fFilamentExtruded to {}".format(fFilamentExtruded)
                    False
            elif bInToolchangeSequence and                  ((bIsSpecifiedCommand(line.strip(), "G0") or bIsSpecifiedCommand(line.strip(), "G1")) or
                  (bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G0") or bIsSpecifiedCommand(line.strip().lstrip(';').lstrip(), "G1"))) \
              and bHasValue(line.strip().split(' '), 'E'):
                fEValue = float(sGetValue(line.strip().split(' '), 'E'))
                if fEValue < -3.0:
                    print("WARNING!!! ({})".format(fEValue))
                elif fEValue > 4.0:
                    print("RECR       ({})".format(fEValue))

            if bIsComment(line):
                # fileOut.write(line)
                continue
                
            bIsM900 = False
            bIsM907 = False
            bIsM220 = False
            bIsM300 = False
            bIsM1 = False
            bHasZ = False
                
            # bIsM567 = False
                
            # if bIsSpecifiedCommand(line.strip(), "M567"):
                # continue
                
            if bIsM907Command(line.strip()):
                bIsM907 = True
                    
            if bIsM900Command(line.strip()):
                bIsM900 = True
                
            # M220 set speed factor override percentage
            if bIsSpecifiedCommand(line.strip(), "M220"):
                bIsM220 = True

            if bIsSpecifiedCommand(line.strip(), "M300"):
                bIsM300 = True

            if bIsSpecifiedCommand(line.strip(), "M1"):
                bIsM1 = True
                    
            bStripCommand = bStripCommand or bIsM907 or bIsM900 or bIsM220 or bIsM300 or bIsM1
                    
            if bIsSpecifiedCommand(line.strip(), "G0") or               bIsSpecifiedCommand(line.strip(), "G1") or               bIsSpecifiedCommand(line.strip(), "G4") or               bIsSpecifiedCommand(line.strip(), "G92") or               bStripCommand:
                True
            else:
                tokens = line.strip().split(' ')
                if len(tokens[0]) > 0:
                    print("G-Code of interest: {}".format(tokens[0]))

            if bIsSpecifiedCommand(line.strip(), "M221"):
                print("WARNING: Found M221 command")

            if True == bHasZValue(tokens=line.strip().split(' ')):
                bHasZ = True
                # print("line {} transitions to Z = {}".format(cnt, sGetZValue(line.strip().split(' '))))
                # print("line {} contents {}".format(cnt, line.strip()))

            # Write the Z move BEFORE any color change command
            if bStripCommand:
                print("WARNING: This version of code suggests a command needs to be dropped that has not been...")
                if bIsM900 or bIsM907 or bIsM220 or bIsM300:
                    False # drop entirely; do not even leave as a comment
                else:
                    # fileOut.write("; {}".format(line))
                    True # keep, but only as a comment
            else:
                # fileOut.write(line)
                True # keep the line as-is

            # if bAddColorCommand:
                # fileOut.write(sColorCommand)
                # fileOut.write('\r\n')
            
    print("Total layers: {}".format(nTotalLayers))
    print("Errors? : {}".format(bAnyErrors))
    
if __name__ == '__main__':
    print("\r\n!!!\r\n!!! WARNING: This code does not understand z-hop.  Use with caution! !!!\r\n!!!\r\n")
    vVerifyNoUnload()


# In[ ]:




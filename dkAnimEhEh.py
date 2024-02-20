##############################################################################################################
#NAME: dkAnimEhEh
#VERSION: See variable dkver below. The version history is now in the file : dkAnimEhEh_Manual.html
#AUTHOR: David Saber, www.dreamcraftdigital.com, based on Dan Erwin and Daniel Kramer's code.
#SCRIPTING LANGUAGE: Maya Python
#DATE OF LATEST VERSION: 2024-02-17
#LATEST VERSION BY: David Saber
#USAGE: This tool is intended to save animation data to a *.dkanim file to then be able to import said animation to same, or almost the same rig, in another or same Autodesk Maya scene file.
#MANUAL: it's now in the file : dkAnimEhEh_Manual.html
#LINKS: Check author's link
#SUPPORT: Contact David Saber, see author above
#LATEST UPDATES: read the file : dkAnimEhEh_Manual.html
#TODO: read the file : dkAnimEhEh_Manual.html
##############################################################################################################


# Imports
import os
# Import Maya Python API
import maya.cmds as cmds
import maya.mel
from functools import partial
# Import Regular expressions
import re
import datetime

# Global variables
DKANIM_REFRESH = 1 #in Channels Window, 1 indicates that the channels list is NOT refreshed, MUST be refreshed
DKANIM_REFRESH_KEEP = 1 #in Channels Window, 1 indicates that the current selected channels must stay selected
progressBar_Maya = maya.mel.eval('$tmp = $gMainProgressBar')
progressWin_DK = "dre_dkAnimLoadProgress_window"
progressBar_DK = "dre_dkAnimLoadProgWin_progressBar"


def dkAnimEhEh():
    print("\ndkAnim: Starting")
    # If dk windows are opened, close them
    if cmds.window('dkAnim', exists=True):
        cmds.deleteUI('dkAnim')
    if cmds.window('dkAnim_channels', exists=True):
        cmds.deleteUI('dkAnim_channels')
    # dk main window title
    dkver = "2.05"
    windowstits = "dkAnimEhEh Export-Import " + dkver
    # Create Window
    cmds.window('dkAnim', s=False, ip=True, w=600, h=450, title=windowstits)
    cmds.columnLayout("cl_global", co=('left',10), rs=20, bgc=(0.2, 0.15, 0.45))
    # Header Frame
    cmds.rowColumnLayout(parent="cl_global", nc=1, cw=[(1, 550)], cs=[(1, 0)], height=1)
    # Write Options Frame
    cmds.frameLayout(parent="cl_global", borderVisible=True, labelVisible=True, li=10, h=120, w=575, label="WriteOptions", marginWidth=5, marginHeight=5, bgc=(0.45, 0.27, 0.15))
    cmds.columnLayout("cl_WO", rs=5, bgc=(0.28, 0.27, 0.05))
    cmds.rowColumnLayout(parent="cl_WO", nc=1, cw=[(1, 550)], cs=[(2, 5)])
    cmds.rowColumnLayout(parent="cl_WO", nc=2, cw=[(1, 500), (2, 50)], cs=[(2, 5)])
    cmds.textField("dk_outname", text="out.dkanim", ed=1)
    cmds.button(label="Browse", bgc=(0.45, 0.27, 0.15), command=partial(dk_browse_output, 'w'))
    cmds.rowColumnLayout(parent="cl_WO", nc=2, cw=[(1, 100), (2, 450)], cs=[(2, 5)])
    cmds.checkBox('dk_hierarchy', v=1, label=" Save Hierarchy")
    cmds.button(label="Write Anim", w=400, bgc=(0.45, 0.27, 0.15), command=partial(dk_animWrite_progress, "dk_outname", "dk_hierarchy"))
    # Read Options Frame
    cmds.frameLayout(parent="cl_global", borderVisible=True, labelVisible=True, li=10, h=265, w=575, label="ReadOptions", marginWidth=5, marginHeight=5, bgc=(0.08, 0.32, 0.16))
    cmds.columnLayout("cl_RO", rs=5, bgc=(0.14, 0.43, 0.13))
    cmds.rowColumnLayout(parent="cl_RO", nc=2, cw=[(1, 500), (2, 50)], cs=[(1, 5),(2, 5)])
    cmds.textField("dk_inname", text="in.dkanim",  ed=1, changeCommand=partial(dk_setRefresh, 0))
    cmds.button(label="Browse", bgc=(0.08, 0.32, 0.16), command=partial(dk_browse_output, 'r'))
    cmds.separator(height=10, w=550, style="out")
    cmds.rowColumnLayout(parent="cl_RO", nc=1, cs=[(1, 5)], cw=[(1, 550)])
    dk_doReplace = cmds.checkBox("dk_doReplace", al="left", v=0, label="Use Search and Replace", changeCommand=partial(dk_setRefresh, 1))
    cmds.rowColumnLayout(parent="cl_RO", nc=2, cs=[(1, 5),(2, 5)], cw=[(1, 275), (2, 275)])
    dk_search = cmds.textFieldGrp("dk_search", cal=[(1,'left'),(2,'left')], cw=[(1, 100), (2, 170)], label="  Search For:", changeCommand=partial(dk_setRefresh, 1))
    dk_replace = cmds.textFieldGrp("dk_replace", cw=[(1, 100), (2, 165)], label="Replace With:", changeCommand=partial(dk_setRefresh, 1))
    cmds.separator(height=5, w=550, style="out")
    cmds.rowColumnLayout(parent="cl_RO", nc=2, cs=[(1, 5),(2, 5)], cw=[(1, 300), (2, 250)])
    dk_prefix = cmds.textFieldGrp("dk_prefix", cal=[(1,'left'),(2,'left')], cw=[(1, 100), (2, 174)], label="  Add Prefix:", changeCommand=partial(dk_setRefresh, 1))
    dk_topNodes = cmds.checkBox("dk_topNodes", v=0, label="Add To Top Nodes Only", changeCommand=partial(dk_setRefresh, 1))
    cmds.separator(height=5, w=550, style="out")
    cmds.rowColumnLayout(parent="cl_RO", nc=2, cs=[(1, 5),(2, 5)], cw=[(1, 300), (2, 250)])
    dk_paths = cmds.checkBox("dk_paths", al="left", v=1, label="Load Explicit Node Paths", changeCommand=partial(dk_setRefresh, 1))
    dk_unKeyed = cmds.checkBox("dk_unKeyed", v=0, label="Load Un-Keyed Attributes", changeCommand=partial(dk_setRefresh, 0))
    cmds.separator(height=5, w=550, style="out")
    cmds.rowColumnLayout(parent="cl_RO", nc=2, cs=[(1, 5),(2, 5)], cw=[(1, 300), (2, 245)])
    dk_useChannels = cmds.checkBox("dk_useChannels", label="Limit Channels to Scope", al="left")
    cmds.button(label="Define Channel Scope", bgc=(0.08, 0.32, 0.16), command=partial(dk_channels, "dk_inname"))
    cmds.separator(height=5, w=550, style="out")
    cmds.rowColumnLayout(parent="cl_RO", nc=1, cs=[(1, 5)], cw=[(1, 550)])
    cmds.button(label="Read Anim", w=549, bgc=(0.08, 0.32, 0.16), command=partial(dk_animRead_progress, "dk_inname", "dk_paths"))
    cmds.showWindow('dkAnim')
    
# def testor(inputarg, *args):
    # print("DKDEBUG: Value of: inputarg : " + str(inputarg))

def dk_setRefresh(keep_selection, *args):
    # This function decides if the channels window should be refreshed
    #cmds.confirmDialog(title="Function start", message="dk_setRefresh", button="Ok", defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
    global DKANIM_REFRESH_KEEP
    global DKANIM_REFRESH
    DKANIM_REFRESH = 1
    DKANIM_REFRESH_KEEP = keep_selection
    if cmds.window('dkAnim_channels', exists=True):
        dk_updateChanLabel()

#def dk_channels(filepathandname, *args):
def dk_channels(InTextFieldName, *args):
    #global DKANIM_REFRESH commented out as it is is defined globaly and is not re-assigned in this function.
    strFilePathAndName = cmds.textField(InTextFieldName, q=True, text=True)
    #print("DKDEBUG: Value of: cmds.window dkAnim_channels exists=True : " + str(cmds.window('dkAnim_channels', exists=True)))
    test = os.path.isfile(strFilePathAndName)
    if not test:
        cmds.confirmDialog(title="File Doesn't Exist", message="But you didn't choose a file!", button="Ok", defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
        return
    booWinChansExists = cmds.window('dkAnim_channels', q=True, exists=True)
    #print("DKDEBUG : Value of: booWinChansExists : " + str(booWinChansExists))
    #if cmds.window('dkAnim_channels', q=True, exists=True):
    if booWinChansExists:
        #print("DKDEBUG: if : Value of: cmds.window dkAnim_channels exists=True : " + str(cmds.window('dkAnim_channels', q=True, exists=True)))
        if DKANIM_REFRESH == 1:
            dk_loadChannels()
    else:
        # interactivePlacement(ip)	Deprecated flag. Recognized but not implemented. This flag will be removed in a future version of Maya.
        #print("DKDEBUG: else : Value of: cmds.window dkAnim_channels exists=True : " + str(cmds.window('dkAnim_channels', exists=True)))
        cmds.window("dkAnim_channels", ret=True, ip=True, title='Channels', w=416, h=416)
        dk_scroll_layout = cmds.scrollLayout("dk_scroll_layout", horizontalScrollBarThickness=16, verticalScrollBarThickness=16, w=400, h=400, rc="dk_resize_chanList()")
        cmds.columnLayout("dkc_ColMain", rs=5) #a columnLayout's child is like a horizontal frame and rs will add space between the frames, but not above the 1st frame and not below the last frame
        cmds.rowColumnLayout("dkc_Buttons", parent="dkc_ColMain", nc=3, cw=[(1, 100), (2, 100), (3, 165)], cs=[(1, 3),(2, 3),(3, 3)], w=400, h=25)
        #cmds.button(label='Add', c='dk_matchChannels(1)')
        cmds.button(label='Add', command=partial(dk_matchChannels,1))
        #cmds.button(label='Remove', c='dk_matchChannels(0)')
        cmds.button(label='Remove',  command=partial(dk_matchChannels,0))
        cmds.textField("dk_wildCard", tx='*', w=160)
        cmds.rowColumnLayout("dkc_Refresh", parent="dkc_ColMain", nc=2, cw=[(1, 100), (2, 265)], cs=(1, 3), w=400, h=25)
        #cmds.button(label='Refresh List', c='dk_loadChannels()')
        cmds.button(label='Refresh List', command=partial(dk_loadChannels))
        dk_chanLabel = cmds.text("dk_chanLabel", label='1000 Channels Scoped')
        cmds.rowColumnLayout("dkc_space", parent="dkc_ColMain", nc=1, cs=(1, 0), cw=[(1, 365)], w=400, h=2)
        #old code : dk_chanList = cmds.textScrollList(parent=dk_scroll_layout, nr=40, allowMultiSelection=True, sc='dk_updateChanLabel', h=(cmds.scrollLayout(dk_scroll_layout, q=True, h=True) - 60))
        cmds.textScrollList("dk_chanList", parent="dk_scroll_layout", nr=40, allowMultiSelection=True, w=400, h=(cmds.scrollLayout(dk_scroll_layout, q=True, h=True) - 78), sc=partial(dk_updateChanLabel))
        #print("DKDEBUG: end of else : Value of: cmds.window dkAnim_channels exists=True : " + str(cmds.window('dkAnim_channels', exists=True)))
        dk_loadChannels()
        cmds.window("dkAnim_channels", e=True, w=416, h=416)
        dk_matchChannels(1)
    cmds.showWindow('dkAnim_channels')
    dk_resize_chanList()

def dk_resize_chanList():
    # As of 2024-02-17 I still fully understand the need for this function, must be tested further
    #print("DKDEBUG: Value of: dk_resize_chanList : " + "dk_resize_chanList starting")
    filtered_names = []
    # cmds.textScrollList -e -nr `cmds.textScrollList -q -ni dk_chanList` dk_chanList;
    cmds.textScrollList("dk_chanList", e=True, nr=40)
    cmds.textScrollList("dk_chanList", e=True, a="tempSizerLine")
    cmds.textScrollList("dk_chanList", e=True, ri="tempSizerLine")
    if cmds.textScrollList("dk_chanList", q=True, w=True) < cmds.scrollLayout("dk_scroll_layout", q=True, w=True):
        cmds.textScrollList("dk_chanList", e=True, w=(cmds.scrollLayout("dk_scroll_layout", q=True, w=True) - 25), h=(cmds.scrollLayout("dk_scroll_layout", q=True, h=True) - 78))

def dk_loadChannels(*args):
    # In this function: selected channels are badly managed, need to rewrite and clean
    #print("dk_loadChannels : " + "start")
    global DKANIM_REFRESH
    global DKANIM_REFRESH_KEEP
    lisSelectedChans = []
    size = 0
    buffer = []
    chan = ""
    node = ""
    path = ""
    i = 0
    filename = cmds.textField("dk_inname", q=True, text=True)
    #Old code : test = cmds.filetest("-r", filename) 
    test = os.path.isfile(filename)
    #print("DKDEBUG: LC: Value of: test : " + str(test))
    #print("DKDEBUG: LC: Value of: cmds.textScrollList 1 dk_chanList q=True ai=True : " + str(cmds.textScrollList("dk_chanList", q=True, ai=True)))
    # The following line gets an already existing channels selection 
    #print("DKDEBUG: LC: Value of: dkAnim_channels visib true : " + str(cmds.window('dkAnim_channels', q=True, visible=True)))
    #print("DKDEBUG: LC: Value of: dkAnim_channels exists true : " + str(cmds.window('dkAnim_channels', q=True, exists=True)))
    #Following line should be at the top of this function?
    if cmds.window('dkAnim_channels', q=True, exists=True):
        lisSelectedChans = cmds.textScrollList("dk_chanList", q=True, sii=True) or [] #selectIndexedItem(sii) Select the indexed item. Indices are 1-based.
        if lisSelectedChans == []:
            DKANIM_REFRESH_KEEP = 0
        #print("DKDEBUG: LC: Value of: lisSelectedChans : " + str(lisSelectedChans))
        cmds.textScrollList("dk_chanList", e=True, w=10, h=10, vis=0, m=0)
        print("dkAnim: Loading Channel List...")
        if not test:
            cmds.textScrollList("dk_chanList", e=True, w=10, h=10, vis=0, m=0, ra=True)
            # confirm = cmds.confirmDialog(title="Warning", message="File Doesn't Exist", button="Ok", defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
        else:
            cmds.textScrollList("dk_chanList", e=True, w=10, h=10, vis=0, m=0, ra=True)
            fileID = open(filename, "r+") # Open for reading and writing.  The stream is positioned at the beginning of the file.
            while True: # means loop forever
                line = fileID.readline()
                if not line:
                    break # means exit loop at last line
                buffer = line.split()
                size = len(buffer)
                if size > 0:
                    if line[:5] == "anim " or line[:7] == "static ":
                        if size == 6 or size == 7:
                            if line[:5] == "anim " or (line[:7] == "static " and cmds.checkBox("dk_unKeyed", q=True, v=True)):
                                filtered_names = dk_filter_nodes(line, cmds.checkBox("dk_paths", q=True, v=True))
                                node = filtered_names[2]
                                chan = filtered_names[3]
                                # This will populate dk_chanList
                                cmds.textScrollList("dk_chanList", e=True, a=(node + "." + chan), w=10, h=10, vis=0, m=0)
                                #print("DKDEBUG: LC: Value of: cmds.textScrollList 3 dk_chanList q=True, ai=True : " + str(cmds.textScrollList("dk_chanList", q=True, ai=True)))
            arrayAllItems = cmds.textScrollList("dk_chanList", q=True, ai=True)
            fileID.close()
        DKANIM_REFRESH = 0
        #print("DKDEBUG: LC: Value of: lisSelectedChans : " + str(lisSelectedChans))
        #print("DKDEBUG: LC: Value of: cmds.textScrollList dk_chanList q=True ai=True : " + str(cmds.textScrollList("dk_chanList", q=True, ai=True)))
        #print("DKDEBUG: LC: Value of: cmds.textScrollList dk_chanList q=True, sii=True : " + str(cmds.textScrollList("dk_chanList", q=True, sii=True)))
        #print("DKDEBUG: LC: Value of: DKANIM_REFRESH_KEEP : " + str(DKANIM_REFRESH_KEEP))
        # Next line : if channels selection does not already exist, create a new one based on the list of all items
        if DKANIM_REFRESH_KEEP == 1:
            for item in lisSelectedChans:
                cmds.textScrollList("dk_chanList", e=True, sii=item)
                #print("DKDEBUG: LC: Value of: cmds.textScrollList dk_chanList q=True sii=item : " + str(cmds.textScrollList("dk_chanList", q=True, sii=item)))
        else:
            i = 1
            #print("DKDEBUG: LC: Value of: arrayAllItems : " + str(arrayAllItems))
            #print("DKDEBUG: LC: LENGTH of: arrayAllItems : " + str(len(arrayAllItems)))
            #if i <= len(arrayAllItems):
                #print("DKDEBUG: LC: i less than arrayAllItems : " + "true")
            while i <= len(arrayAllItems):
                #print("DKDEBUG: LC: i less than arrayAllItems : " + str(i))
                cmds.textScrollList("dk_chanList", edit=True, sii=i)
                i += 1
        arraySelIndexes = cmds.textScrollList("dk_chanList", q=True, sii=True)
        #print("DKDEBUG: LC: Value of: sii : " + str(cmds.textScrollList("dk_chanList", q=True, sii=True)))
        #print("DKDEBUG: LC: LENGTH of: ssi : " + str(len(cmds.textScrollList("dk_chanList", q=True, sii=True))))
        #print("DKDEBUG: LC: values of: arraySelIndexes : " + str(arraySelIndexes))
        #print("DKDEBUG: LC: length of: arraySelIndexes : " + str(len(arraySelIndexes)))
        i=0
        while i <= len(arraySelIndexes)-1:
            #print("DKDEBUG: LC: selected item name " + str(i) + " : " + str(arrayAllItems[i]))
            i += 1
        lisSelectedChans = arraySelIndexes
        #print("DKDEBUG: LC: Value of: lisSelectedChans : " + str(lisSelectedChans))
        cmds.textScrollList("dk_chanList", e=True, w=10, h=10, vis=1, m=1)
        #print("DKDEBUG: LC: Value of: cmds.textScrollList 5 dk_chanList q=True, ai=True : " + str(cmds.textScrollList("dk_chanList", q=True, ai=True)))
        DKANIM_REFRESH_KEEP = 1
        dk_updateChanLabel()
        dk_resize_chanList()
        print("dkAnim: Done Loading Channel List")

def dk_updateChanLabel(*args):
    #global DKANIM_REFRESH  commented out as it is is defined globaly and is not re-assigned in this function.
    #global DKANIM_REFRESH_KEEP  commented out as it is is defined globaly and is not re-assigned in this function.
    #num = cmds.textScrollList("dk_chanList", q=True, nsi=True) or 0
    num = 0
    if cmds.window('dkAnim_channels', q=True, visible=True):
        #print("DKDEBUG: Value of: dkchan exists : " + str(cmds.window('dkAnim_channels', q=True, visible=True)))
        num = cmds.textScrollList("dk_chanList", q=True, nsi=True)
    #else:
    #    print("DKDEBUG: dkchan is NOT visible" )
    s = "s" if num != 1 else ""
    state = "Refresh Needed" if DKANIM_REFRESH else "Refreshed"
    cmds.text("dk_chanLabel", e=True, label="{} Channel{} Scoped ({})".format(num, s, state))

def dk_matchChannels(mode, *args):
    loop = 1
    total = cmds.textScrollList("dk_chanList", q=True, ni=True)
    #print("DKDEBUG: Value of: total : " + str(total))
    all_items = cmds.textScrollList("dk_chanList", q=True, ai=True)
    #print("DKDEBUG: Value of: all_items : " + str(all_items))
    strTextWildCard = cmds.textField("dk_wildCard", q=True, tx=True)
    strTextRegex = wildcard_to_regex(strTextWildCard)
    #print("DKDEBUG: Value of: strTextWildCard : " + strTextWildCard)
    #print("DKDEBUG: Value of: strTextRegex : " + strTextRegex)
    while loop <= total:
        #print("DKDEBUG: Value of: all_items[loop - 1] " + all_items[loop - 1])
        text_found = re.search(strTextRegex, all_items[loop - 1], re.IGNORECASE)
        #old code : if strTextRegex in all_items[loop - 1]:
        if text_found :
            #print("DKDEBUG: Value of: text_found.group(0) " + text_found.group(0))
            #print("DKDEBUG: Value of: strTextRegex : FOUND in " + all_items[loop - 1])
            if mode:
                cmds.textScrollList("dk_chanList", e=True, sii=loop)
            else:
                cmds.textScrollList("dk_chanList", e=True, dii=loop)
        #else:
        #    print("DKDEBUG: Value of: strTextRegex : NOT FOUND in " + all_items[loop - 1])
        loop += 1
    dk_updateChanLabel()
    
def wildcard_to_regex(wildcard_pattern):
    # Escape special characters
    escaped_pattern = re.escape(wildcard_pattern)
    # Translate wildcards to regex equivalents
    regex_pattern = escaped_pattern.replace(r'\*', '.*').replace(r'\?', '.')
    return regex_pattern

def dre_dkAnimCheckPath(txName):
    goodPath = ""
    currentPath = cmds.textField(txName, query=True, tx=True)
    # If it's a file, then get the path
    if os.path.isfile(currentPath):
        path = os.path.dirname(currentPath)
    # If it's not a file, if it's a path, then define it as the dir
    elif os.path.isdir(currentPath):
        path = currentPath
    # If it's not a file or a directory, get the current file path and convert it to a directory path
    else: 
        cfp = cmds.file(q=True, sn=True)
        #but if cfp="" then Maya should open the last opened file's directory
        path = os.path.dirname(cfp)
    # If it's a good folder, then return it
    if os.path.isdir(path):
        goodPath = path
    return goodPath

def dk_browse_output(field, *args):
    dkAnimFilter = "*.dkAnim"
    mayaVersion = cmds.about(v=True)
    workSpaceDir = cmds.workspace(q=True, fullName=True)
    multipleFilters = "dkAnim Files (*.dkanim)"
    if field == 'w':
        #Following line : will check for the text field dk_outname's content
        checkPath = dre_dkAnimCheckPath("dk_outname")
        if checkPath != "":
            workSpaceDir = checkPath
        fileName = cmds.fileDialog2(fm=0, cap="Animation Export", okc="Save", startingDirectory=workSpaceDir, fileFilter=multipleFilters)
        #print("DKDEBUG: Value of: fileName : " + str(fileName))
        if fileName and len(fileName):
            file_path = dre_dkAnimPath(fileName[0])
            print("dkAnim: File path : [{}]".format(file_path))
            cmds.textField("dk_outname", e=True, tx=file_path)
    elif field == 'r':
        checkPath = dre_dkAnimCheckPath("dk_inname")
        if checkPath != "":
            workSpaceDir = checkPath
        fileName = cmds.fileDialog2(fm=1, cap="Animation Import", okc="Open", startingDirectory=workSpaceDir)
        if fileName and len(fileName):
            file_path = dre_dkAnimPath(fileName[0])
            print("dkAnim: File path : [{}]".format(file_path))
            cmds.textField("dk_inname", e=True, tx=file_path)

def dre_dkAnimPath(file_path):
    #ctypes.windll.user32.MessageBoxW(0, file_path, "Value of: file_path", 1) #TEST
    # According to https://www.regextranslator.com/ : begin with, anything, never or more, literally "/" , which means it will separate the path from the file name (and extension).
    # old code : dir_name = re.search("^.*/", file_path, re.IGNORECASE)
    dir_name = re.search(".*[\\/]", file_path, re.IGNORECASE)
    #ctypes.windll.user32.MessageBoxW(0, dir_name.group(0), "Value of: dir_name", 1) #TEST
    # will extract the file name WITHOUT its extension from the path
    file_name = re.search("[ \w-]+?(?=\.)", file_path, re.IGNORECASE)
    #ctypes.windll.user32.MessageBoxW(0, file_name.group(0), "Value of: file_name", 1) #TEST
    # will combine the path and the file name and will add the proper file extension.
    new_file_path = dir_name.group(0) + file_name.group(0) + ".dkAnim"
    #ctypes.windll.user32.MessageBoxW(0, new_file_path, "Value of: new_file_path", 1) #TEST
    return new_file_path

def dk_edit_output(file_name, file_type):
    file_name = dre_dkAnimPath(file_name)
    cmds.textField("dk_outname", e=True, tx=file_name)

#def dk_animWrite_progress(filename, hi, *args):
def dk_animWrite_progress(OutTextFieldName, hiCheckBoxName, *args):
    strFilename = cmds.textField(OutTextFieldName, q=True, text=True)
    booSaveHierarchy = cmds.checkBox(hiCheckBoxName, q=True, value=True)
    # print("DKDEBUG: Value of: strFilename : " + str(strFilename))
    # print("DKDEBUG: Value of: booSaveHierarchy : " + str(booSaveHierarchy))
    # print("DKDEBUG: Value of: txtfield : " + cmds.textField('dk_outname', q=True, text=True))
    #global progressBar_Maya  : This is defined on maya startup, old name : gMainProgressBar, commented out as it is is defined globaly and is not reset in this function.
    global progressBar_DK # will be a string that will be defined inside this function, by calling another function
    #global progressWin_DK # A string variable that will be defined in the dre_dkAnim_progressWin_proc function, commented out in 2024-01-06 because it is defined globally, is not reassigned here, is just accessed here.
    #Moved to global variables section : progressBar_Maya = maya.mel.eval('$tmp = $gMainProgressBar')
    # Next line: if hierarchy check box is checked, select already selected objects with their hierarchy
    if booSaveHierarchy:
        cmds.select(hi=True)
    objects = cmds.ls(sl=True, l=True) # long(l)	boolean	: Return full path names for Dag objects. By default the shortest unique name is returned.
    # Error out when nothing is selected to export
    if not objects:
        nosl_message = "No objects selected to export animation for."
        cmds.confirmDialog(title="Nothing Selected to Export", message=nosl_message, icon="critical", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
        raise RuntimeError(nosl_message)
    #bordel= objects[0] + ". Obj2: " + objects[1]
    #cmds.confirmDialog(title="Value of: objects", message=bordel, icon="information", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
    # Folder check
    error_message = "File Directory does not exist.\nDefine or navigate to a new file path and try again."
    #print("DKDEBUG: Value of: strFilename : " + str(strFilename))
    dir_name = re.search(".*[\\/]", strFilename, re.IGNORECASE)
    #print("DKDEBUG: Value of: dir_name : " + str(dir_name))
    if dir_name:
        
        dir_name = dir_name.group(0)
        # Does directory exist? (old code: if not cmds.filetest("-d", strFilename):)
        if not os.path.isdir(dir_name):
            cmds.confirmDialog(title="But directory does NOT exist!", icon="critical", message=error_message, button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
            raise RuntimeError(error_message)
    else:
        cmds.confirmDialog(title="Invalid path", message="The path chosen does not have a valid syntax", icon="critical", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
        raise RuntimeError(error_message)
    # Does File Exist?
    test = os.path.isfile(strFilename)
    if test:
        confirm = cmds.confirmDialog(title="Overwrite file?", message="File Exists, Do you want to Overwrite it?", button=["Yes", "No"], defaultButton="No", cancelButton="No", dismissString="No")
        if confirm == "No":
            return
    # Prompt user of job about to occur
    file_short_name = re.search("[^(\\/)]*$", strFilename)
    objs_count = len(objects)
    confirm = cmds.confirmDialog(title=("Write Anim for {}?".format(objs_count)), message=("Are you sure you want to write animation for {} selected objects\ninto the file : {}".format(objs_count, file_short_name.group(0))), button=["Yes", "Cancel"], defaultButton="Yes", cancelButton="Cancel", dismissString="Cancel")
    if confirm == "Cancel":
        return
    # Progress Bar DK, old name : dkAnimErwin_progressBar
    progressBar_DK = dre_dkAnim_progressWin_proc("Exporting Animation", objs_count)
    # Do writing to file
    #try: uncomment when all is working well
    dk_animWrite(strFilename, booSaveHierarchy)
    #except Exception as e:
    #    raise RuntimeError("Error writing animation to file: {}".format(str(e)))
    # Close progress bar DK 
    cmds.progressBar(progressBar_DK, edit=True, endProgress=True)
    try:
        cmds.deleteUI(progressWin_DK)
    except Exception:
        pass
    # Reset progress bar Maya 
    cmds.progressBar(progressBar_Maya, edit=True, endProgress=True)

def dk_animWrite(filename, hi):
    parent = 0
    objects = cmds.ls(sl=True, l=True)
    print("dkAnim: Writing Animation Curves...")
    start_time = cmds.date(time=True)
    start_timer = cmds.timerX()
    print("dk_animWrite: Writing Animation started at [{}]".format(start_time))
    with open(filename, 'w') as file_id:
        file_id.write("#Generated by dkAnim script\n#\n#dkAnim written by Daniel Kramer danl_kramer@yahoo.com\n")
        file_id.write("#dkAnimErwin is a version of dkAnim by Dan Erwin - danimations@gmail.com\n")
        file_id.write("#dkAnimEhEh is a version of dkAnimErwin by David Saber - dreamcraftdigital.com\n")
        file_id.write("#Written out of {}\n#\n\n".format(cmds.file(q=True, sn=True)))
        # define scene space units
        file_id.write("sceneUnit {}\n\n".format(cmds.currentUnit(q=True, linear=True)))
        if hi:
            cmds.select(hi=True)
        count = 0
        objs_count = len(objects)
        #print("DKDEBUG: Value of: objs_count : " + str(objs_count))
        for item in objects:
            #print("DKDEBUG: Value of: item : " + item)
            #short items: what is it for? It's never used elsewhere in the code. Commented out. Original mel code : $shortItem = `ls -sl $item`;. ChatGPT translated code: short_item = cmds.ls(sl=item)[0] . Code to attempt to fix 1st: short_item = cmds.ls(sl=True)[0]. Code to attempt to fix 2nd: short_item = cmds.ls(sn=True)[0]
            #cmds.confirmDialog(title="Value of: short_item", message=short_item, icon="information", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK") #TEST
            channels = cmds.listConnections(item, type='animCurve')
            #begin Detecting if selected object has animations
            #print("DKDEBUG: Value of: channels type : " + str(type(channels)))
            if channels:
                #print("Channel has content!")
                for chan in channels:
                    #print("DKDEBUG: Value of: chan : " + chan + " . Type of: chan : " + str(type(chan)))
                    connects = cmds.listConnections(chan, p=True)
                    cur_attr = connects[0]
                    num = len(cur_attr.split("."))
                    node = ".".join(cur_attr.split(".")[:-1])
                    node_temp = cmds.ls(node, l=True) #The ls command returns the names (and optionally the type names) of objects in the scene.
                    attr = cur_attr.split(".")[-1]
                    node = node_temp[0]
                    node_temp = cmds.listRelatives(node, p=True)
                    if node_temp:
                        parent = 1
                    else:
                        parent = 0
                    testit = cmds.listAnimatable(cur_attr)
                    testit2 = cmds.keyframe(chan, q=True)
                    if testit and testit2:
                        pre_in = cmds.getAttr("{}.preInfinity".format(chan))
                        post_in = cmds.getAttr("{}.postInfinity".format(chan))
                        weighted = cmds.getAttr("{}.weightedTangents".format(chan))
                        file_id.write("anim {} {} {} {} 0 0;\n".format(attr, attr, node, parent))
                        file_id.write("animData {\n")
                        file_id.write("  weighted {};\n".format(weighted))
                        file_id.write("  preInfinity {};\n".format(pre_in))
                        file_id.write("  postInfinity {};\n".format(post_in))
                        file_id.write("  keys {\n")
                        keys = cmds.keyframe(chan, q=True)
                        values = cmds.keyframe(chan, q=True, vc=True)
                        in_tan = cmds.keyTangent(chan, q=True, itt=True) #outTangentType inTangentType. "Fixed tangents" means retaining the tangent’s angle
                        out_tan = cmds.keyTangent(chan, q=True, ott=True)
                        tan_lock = cmds.keyTangent(chan, q=True, lock=True) #Lock a tangent so in and out tangents move together. Returns an int[] when queried.
                        weight_lock = cmds.keyTangent(chan, q=True, weightLock=True) #Lock the weight of a tangent so it is fixed. -weightLock off means tangent has free length, and on means locked length
                        #print("DKDEBUG: Value of: weight_lock : " + str(item) + " : " + str(weight_lock)) most of the time, all of these are false
                        breakdown = cmds.keyframe(chan, q=True, breakdown=True)
                        in_angle = cmds.keyTangent(chan, q=True, inAngle=True) #the following 4 lines are float values for tangents angles and length
                        out_angle = cmds.keyTangent(chan, q=True, outAngle=True)
                        in_weight = cmds.keyTangent(chan, q=True, inWeight=True)
                        out_weight = cmds.keyTangent(chan, q=True, outWeight=True)
                        for i in range(len(keys)):
                            bd = 0
                            if breakdown:
                                for bd_item in breakdown:
                                    if bd_item == keys[i]:
                                        bd = 1
                            file_id.write("    {} {} {} {} {} {} {}".format(keys[i], values[i], in_tan[i], out_tan[i], tan_lock[i], weight_lock[i], bd))
                            if in_tan[i] == "fixed":
                                file_id.write(" {} {}".format(in_angle[i], in_weight[i]))
                            if out_tan[i] == "fixed":
                                file_id.write(" {} {}".format(out_angle[i], out_weight[i]))
                            file_id.write(";\n")
                        file_id.write("  }\n}\n")
            #else:
                #cmds.confirmDialog(title="Value of: channels", message="NOTHING?", icon="information", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
            #end Detecting if selected object has animations
            #Below, dkAnim will store static , non animated values inside the text file
            static_chans = cmds.listAnimatable(item)
            if static_chans:
                for static_chan in static_chans:
                    cur_attr = static_chan
                    num = len(cur_attr.split("."))
                    node = ".".join(cur_attr.split(".")[:-1])
                    node_temp = cmds.ls(node, l=True)
                    attr = cur_attr.split(".")[-1]
                    node = node_temp[0]
                    node_temp = cmds.listRelatives(node, p=True)
                    if node_temp:
                        parent = 1
                    else:
                        parent = 0
                    static_chan = "{}.{}".format(node, attr)
                    testit = cmds.keyframe(static_chan, q=True)
                    connected = cmds.listConnections(static_chan, d=False)
                    if not testit and not connected:
                        file_id.write("static {} {} {} {} {}\n".format(attr, attr, node, parent, cmds.getAttr(static_chan)))
            # progress progressBar one step further 
            cmds.progressBar(progressBar_DK, edit=True, step=1, max=objs_count)
            cmds.progressBar(progressBar_Maya, edit=True, step=1, max=objs_count)
            count += 1
            #cmds.confirmDialog(title="Value of: count", message=count, icon="information", button="OK", defaultButton="OK", cancelButton="OK", dismissString="OK")
            if objs_count == count or cmds.progressBar(progressBar_DK, query=True, isCancelled=True):
                if cmds.progressBar(progressBar_DK, query=True, isCancelled=True):
                    print("dkAnim: User canceled exporting animation file...")
                break
    endTime = cmds.date(time=True)
    print("dk_animWrite: Finished Writing Animation at [" + str(endTime) + "]")
    print("dkAnim: script completed")

def dk_filter_nodes(line, paths):
    #print("DKDEBUG: DFN: Value of line : " + line)
    global DKANIM_REFRESH # this is a global variable
    DKANIM_REFRESH = 0  
    buffer = line.split()
    return_val = []
    # use search and replace
    strSearch = cmds.textFieldGrp("dk_search", q=True, text=True)
    strReplace = cmds.textFieldGrp("dk_replace", q=True, text=True)
    boodo_replace = cmds.checkBox("dk_doReplace", q=True, v=True)
    if boodo_replace and strSearch:
        #print("DKDEBUG: DFN : Value of: strSearch strReplace boodo_replace : " + strSearch + " " + strReplace + " " + str(boodo_replace))
        #match = "*" + strSearch + "*"
        buffer[3] = buffer[3].replace(strSearch, strReplace)
    #print("DKDEBUG: DFN : Value of: buffer[3] : " + buffer[3]) 
    # Add Prefix:
    prefix = cmds.textFieldGrp("dk_prefix", q=True, text=True)
    # David Saber says in 2024-02: I added the following if statement as I beleive it was missing...
    if prefix != "":
        new_path = ""
        #print("DKDEBUG: DFN : Value of: checkBox dk_topNodes : " + str(cmds.checkBox("dk_topNodes", q=True, v=True)))
        #print("DKDEBUG: DFN : Value of: checkBox buffer[4] : " + str(buffer[4]))
        #buffer[4] is the parental status: 0 means no parent and 1 means "has a parent", so next line means : if check box is unchecked, or if it is checked but object has no parent
        if (cmds.checkBox("dk_topNodes", q=True, v=True) and buffer[4] == "0") or not cmds.checkBox("dk_topNodes", q=True, v=True):
            if "|" in buffer[3]:
                buffer2 = buffer[3].split("|")
                #print("DKDEBUG: DFN : Value of: buffer2 : " + str(buffer2))
                for item in buffer2:
                    if item != "" :
                        new_path += "|" + prefix + item
                        #print("DKDEBUG: DFN : Value of: new_path : " + new_path)
                buffer[3] = new_path
            else:
                buffer[3] = prefix + buffer[3]
        # Add to top nodes only
        if cmds.checkBox("dk_topNodes", q=True, v=True) and buffer[4] == "1":
            if "|" in buffer[3]:
                buffer2 = buffer[3].split("|")
                for i in range(len(buffer2)):
                    if i == 0:
                        new_path = "|" + prefix + buffer2[i]
                    else:
                        new_path += "|" + buffer2[i]
                buffer[3] = new_path
    # Load explicit node path: if this checkbox is unchecked :
    #print("DKDEBUG: DFN : before LENP: Value of: buffer[3] : " + buffer[3])
    if paths == 0:
        buffer3 = buffer[3].split("|")
        buffer[3] = buffer3[-1]
    #print("DKDEBUG: DFN : after Load explicit node path: Value of: buffer[3] : " + buffer[3])
    # Use selected channels in channels window
    #print("DKDEBUG: DFN : Value of: cmds.window dkAnim_channels visible=True : " + str(cmds.window("dkAnim_channels", q=True, visible=True)))
    if cmds.checkBox("dk_useChannels", q=True, v=True) and cmds.window("dkAnim_channels", q=True, ex=True):
        if cmds.window("dkAnim_channels", q=True, visible=True):
            pass_val = 0
            loop = 0
            total = cmds.textScrollList("dk_chanList", q=True, ni=True)
            all_items = cmds.textScrollList("dk_chanList", q=True, ai=True)
            #print("DKDEBUG: DFN: value of all_items : " + str(all_items))
            selected = cmds.textScrollList("dk_chanList", q=True, sii=True) #selectIndexedItem(sii)	: Select the indexed item. Indices are 1-based.
            # if there's no selection, create one based on all items
            if not selected:
                i = 1
                while i <= total:
                    #print("DKDEBUG: DFN: i less than arrayAllItems : " + str(i))
                    cmds.textScrollList("dk_chanList", edit=True, sii=i)
                    i += 1
            #print("DKDEBUG: DFN : Value of: selected : " + str(selected))
            #print("DKDEBUG: DFN : Value of: selected.len : " + str(len(selected)))
            text = "{}.{}".format(buffer[3], buffer[2])
            #print("DKDEBUG: DFN : Value of: total : " + str(total))
            #print("DKDEBUG: DFN : Value of: text : " + text)
            #print("DKDEBUG: DFN : Value of: selected : " + str(selected))
            #while loop <= total:
            strToFind = ""
            while loop < len(selected):
                strToFind = all_items[selected[loop] - 1]
                #strToFind = "caca"
                #strFoundMatch = re.search(strToFind, text, re.IGNORECASE)
                #strFoundMatch = re.search("(?:" + strToFind + ")*", text, re.IGNORECASE)
                #print("DKDEBUG: DFN : Value of: loop : " + str(loop))
                #print("DKDEBUG: DFN : Value of: loop - 1 : " + str(loop - 1))
                #print("DKDEBUG: DFN : Value of: selected [loop] : " + str(selected[loop]))
                #print("DKDEBUG: DFN : Value of strToFind : " + strToFind)
                if strToFind == text :
                    #print("DKDEBUG: DFN : Value of: strToFind : " + "MATCH FOUND")
                # if strFoundMatch :
                    # print("DKDEBUG: DFN : Value of: strFoundMatch : " + str(strFoundMatch.group(0)))
                # else:
                    # print("DKDEBUG: DFN : Value of: strFoundMatch : " + "is null")
                # #if cmds.match(all_items[selected[loop - 1] - 1], text):
                # if re.search(all_items[selected[loop - 1] - 1], text, re.IGNORECASE):
                    pass_val = 1
                loop += 1
            if pass_val == 0:
                # The following may give error message "object dk skip does not exist"
                return_val = ["dk_skip", "dk_skip", buffer[3], buffer[2]]
                return return_val
    return_val = [buffer[3], buffer[2], buffer[3], buffer[2]]
    return return_val

def dre_fileLineCount(file):
    # This function will count the number of lines inside the text file which extension is *.dkanim.
    # For each line : First it filters out lines that are null, the others will be counted as real lines. Then it filters out lines that have a blank space. Then it keeps lines starting by anim or static, these will be counted as objects.
    # old code : file_id = cmds.fopen(file, "r")
    #file_id = os.open(file, os.O_RDONLY)
    # old code : next_line = cmds.fgetline(file_id), translated code : next_line = cmds.file(file_id, q=True)
    count = 1
    obj_count = 0
    # new code? fgetline is a MEL command that is not available in Python. However, you can use the open function to read a file line by line in Python. Here’s an example:
    with open(file, 'r') as file_id:
        for next_line in file_id:
            if len(next_line) > 0:
                if next_line[0] != " ":
                    if next_line[:5] == "anim " or next_line[:7] == "static ": #next line from char 0 to 5
                        obj_count += 1
                # #next_line = cmds.fgetline(file_id)
                count += 1
                #print("DKDEBUG: Value of: next_line : " + next_line + " . Value of: count : " + str(count) +  " . Value of: obj_count : " + str(obj_count))
    #file_id.close commented out because The "with" block ensures that the file will be closed when control leaves the block
    file_data = [count, obj_count]
    #print("DKDEBUG: Value of: file_data : " + str(file_data))
    return file_data

def dre_dkAnim_progressWin_proc(load_title, count):
    #Progress Bar variable names for GUI elements names
    global progressWin_DK
    #global progressBar_Maya commented out at 2024-02-06 as it is defined globally and not reset here.
    progressWin_DK = "dre_dkAnimLoadProgress_window"
    prog_layout_DK = "dkAnimProgess_columnLayout"
    progress_bar_name_DK = "dre_dkAnimLoadProgWin_progressBar"
    # Create Window
    if cmds.window(progressWin_DK, exists=True):
        cmds.deleteUI(progressWin_DK)
    load_message = f"{load_title}...."
    max_value = 1 if count <= 1 else count - 1 #Conditional Variable Setting
    cmds.window(progressWin_DK, s=0, title=load_message)
    cmds.columnLayout(prog_layout_DK)
    cmds.progressBar(progress_bar_name_DK, p=prog_layout_DK, maxValue=max_value, width=600)
    cmds.showWindow(progressWin_DK)
    # Main progress to cancel job.
    cmds.progressBar(progressBar_Maya, edit=True, beginProgress=True, isInterruptable=True, status=load_message, maxValue=max_value)
    return progress_bar_name_DK

#def dk_animRead_progress(filename, paths):
def dk_animRead_progress(InTextFieldName, pathsCheckBoxName, *args):
    #recall progressWin_DK as global? Necessary te re-assign it below? no, commented out.
    strFileName = cmds.textField(InTextFieldName, q=True, text=True)
    booUseObjPath = cmds.checkBox(pathsCheckBoxName, q=True, value=True)
    # print("DKDEBUG: Value of InTextFieldName : " + str(InTextFieldName))
    # print("DKDEBUG: Value of pathsCheckBoxName : " + str(pathsCheckBoxName))
    # print("DKDEBUG: Value of strFileName : " + str(strFileName))
    # print("DKDEBUG: Value of booUseObjPath : " + str(booUseObjPath))
    #old code : if not cmds.filetest("-r", strFileName):
    test = os.path.isfile(strFileName)
    if not test:
        cmds.confirmDialog(title="Warning", message="File Doesn't Exist", button="Ok", defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
        return
    # Progress Bar
    file_count = dre_fileLineCount(strFileName)
    line_count = file_count[0]
    obj_count = file_count[1]
    # Prompt user of the job about to occur
    # old translated code : file_short_name = cmds.match("[^(\\/)]*$", strFileName)
    file_short_name = re.search("[ \w-]+?(?=\.)", strFileName, re.IGNORECASE)
    #print("DKDEBUG: Value of: file_short_name : " + file_short_name.group(0))
    confirm = cmds.confirmDialog(title=f"Read Anim for {obj_count} channels?", message=f"Are you sure you want to read animation for {obj_count} attributes in the file\n\n{file_short_name.group(0)} ?", button=["Yes", "Cancel"], defaultButton="Yes", cancelButton="Cancel", dismissString="Cancel")
    if confirm == "Cancel":
        return
    #global progressBar_Maya commented out at 2024-02-06 as it is defined globally and not reset here.
    progressBar_DK = dre_dkAnim_progressWin_proc("Importing Animation", line_count) #variable should be renamed? I did it at 2024-02-06
    #Commented out as this variable is defined in function dre_dkAnim_progressWin_proc: progressWin_DK = "MayaWindow|dkAnimProgess_columnLayout"
    # Do reading from file
    #try: uncomment when all script is fixed
    dk_animRead(strFileName, pathsCheckBoxName)
    #except Exception as e:
    #    cmds.warning(f"An error occurred during animation import: {e}")
    # Close progress bar
    cmds.progressBar(progressBar_DK, edit=True, endProgress=True)
    cmds.deleteUI(progressWin_DK)
    #global progressBar_Maya = "MayaWindow|mainProgressBar"  # This is defined on maya startup
    cmds.progressBar(progressBar_Maya, edit=True, endProgress=True)

def dk_animRead(filename, paths):
    import shlex # mel tokenize equivalent
    # Variables
    global DKANIM_REFRESH
    #global progressBar_DK commented out at 2024-02-06 as it is defined globally , not assigned but just accessed here.
    #global progressBar_Maya  commented out at 2024-02-06 as it is defined globally and not reset here.
    tan1 = 0.0
    tan2 = 0.0
    weight1 = 0.0
    weight2 = 0.0
    weighted = ""
    preI = ""
    postI = ""
    attr = ""
    node = ""
    line = ""
    curAttr = ""
    buffer = []
    buffer2 = []
    buffer3 = []
    readtime = 0.0
    value = 0.0
    inType = ""
    outType = ""
    tanLock = 0
    weightLock = 0
    intWeightLock = 0
    breakDown = 0
    filteredNames = []
    lisObjDotAtt = []
    #old code : selected = cmds.ls(sl=True) or []; rEMOVED " or []", what was this for?
    selected = cmds.ls(sl=True)
    size = 0
    endit = 0
    # Progress Bar
    fileID = open(filename, "r+")
    print("dkAnimRead: Reading Animation Curves...")
    startTime = cmds.date(time=True)
    startTimer = cmds.timerX()
    # Variables again
    currentSceneUnit = ""
    lineCount = 0
    warningCount = []
    attrWarningCount = []
    controlCount = []
    line = fileID.readline()
    # If selection is not empty, deselect graph editor keys
    #print("DKDEBUG: Value of cmds.ls( selection=True ) : " + str(cmds.ls( selection=True )))
    if selected != []:
        cmds.selectKey(clear=True)
    #old code : while not cmds.feof(fileID):
    # Now dkAnim will read all lines and apply the animation on the scene object, but it seems dkAnim does not need to start with selected objetcs here, it will "select" objects based on the file info
    while line:
        # Process the line
        #old code : line = cmds.fgetline(fileID)
        line = fileID.readline()
        # Progress progressBar one step further
        cmds.progressBar(progressBar_DK, edit=True, step=1)
        cmds.progressBar(progressBar_Maya, edit=True, step=1)
        weightState = 0
        if len(line) > 0:
            #old code : if cmds.substring(line, 1, 5) == "anim " or cmds.substring(line, 1, 7) == "static ":
            if line[:5] == "anim " or line[:7] == "static ": # To get characters from the begining of the line to the character N°5, it should be coded as : line[0:5]. What it means is that the first char is N°0 and the selection ends BEFORE char N°5 as char N° 5 IS NOT included, more info at https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/ 
                #print("DKDEBUG: Value of line[0:5] : " + line[0:5] + ".")
                buffer = shlex.split(line, " ") #Buffer is the array of items that have been separated by spaces using the split function
                #print("DKDEBUG: Value of buffer : " + str(buffer))
                size = len(buffer)
                #print("DKDEBUG: Value of size : " + str(size))
                # old code : size = len(cmds.tokenize(line, " ", buffer))
                if size == 6 or size == 7:
                    if cmds.checkBox("dk_useChannels", q=True, v=True) and cmds.window("dkAnim_channels", ex=True):
                        if DKANIM_REFRESH == 1:
                            dk_loadChannels()
                    #print("DKDEBUG: Value of line : " + line)
                    filteredNames = dk_filter_nodes(line, paths)
                    #print("DKDEBUG: Value of filteredNames : " + str(filteredNames))
                    # Next lines : there does not seem to be a difference between the return values of curAttr and curAttrLong, and these 2 do not seem to be very useful in this function area, so this will need to be tested and cleaned
                    curAttr = filteredNames[0] + "." + filteredNames[1]
                    node = filteredNames[0]
                    attr = filteredNames[1]
                    endit = 0
                    curAttrLong = node + "." + attr
                    # print("DKDEBUG: Value of node : " + node)
                    # print("DKDEBUG: Value of attr : " + attr)
                    # print("DKDEBUG: Value of curAttr : " + curAttr)
                    # print("DKDEBUG: Value of curAttrLong : " + curAttrLong)
                    lineCount += 1
                    controlCount.append(node)
                    if cmds.objExists(node):
                        # The following line will return the name of the scene object according to what's in the text file
                        lisObjDotAtt = cmds.ls(curAttrLong)
                        #print("DKDEBUG: Value of lisObjDotAtt : obj name dot channel name : " + str(lisObjDotAtt))
                        if len(lisObjDotAtt) > 0:
                            if line[:7] == "static " and cmds.checkBox("dk_unKeyed", q=True, value=True):
                                #print("DKDEBUG: unkeyed values will be loaded : " + "checkbox checked")
                                connected = cmds.listConnections(curAttrLong, d=0, s=0, p=1, c=1, type="animCurve", source=True)
                                if cmds.getAttr(curAttrLong, lock=True) == 0 and not connected:
                                    #old code : setMe = "setAttr " + curAttrLong.replace('||', '|') + " " + buffer[5] + ";"
                                    #setMe = "cmds.setAttr(" + curAttrLong + " " + buffer[5] + ")"
                                    #try: uncomment when all script is fixed
                                    #cmds.evalDeferred(setMe)
                                    cmds.setAttr(curAttrLong, float(buffer[5]))
                                    #except Exception:
                                    #    print("Error caught! If possible mail this file to me so I can debug the error: mail danl_kramer@yahoo.com\nmoving on...\n")
                                else:
                                    print("dkAnim: Warning: Attribute is locked - " + curAttr)
                            if line[:5] == "anim ":
                                #print("DKDEBUG: anim line : " + "reading")
                                while endit == 0: #old code
                                    #Old code : line = cmds.fgetline(fileID)
                                    line = next(fileID)
                                    #print("DKDEBUG: Value of line : " + line)
                                    # Progress progressBar one step further
                                    cmds.progressBar(progressBar_DK, edit=True, step=1)
                                    cmds.progressBar(progressBar_Maya, edit=True, step=1)
                                    if line[2:11] == "weighted ":
                                        if line[11:12] == "T":
                                            #print("DKDEBUG: weighted : " + "TRUE")
                                            # old code : weighted = "keyTangent -edit -weightedTangents True " + curAttr
                                            #Commented out , command used later in the code : weighted = "cmds.keyTangent(edit=True, weightedTangents=True, at='" + curAttr +"')"
                                            weightState = 1
                                        else:
                                            weightState = 0
                                    if line[2:7] == "preIn":
                                        # old code : buffer = cmds.tokenize(line, " ")
                                        buffer = shlex.split(line, " ")
                                        #print("DKDEBUG: value of buffer1 : " + str(buffer))
                                        #print("DKDEBUG: value of buffer[1] : " + str(buffer[1]))
                                        #Old code : buffer = cmds.tokenize(buffer[1], ";")
                                        #buffer = shlex.split(buffer[1], ";")
                                        preI = buffer[1].replace(';', '')
                                        #print("DKDEBUG: value of preI : " + str(preI))
                                    if line[2:8] == "postIn":
                                        #Old code : buffer = cmds.tokenize(line, " ")
                                        buffer = shlex.split(line, " ")
                                        #Old code : buffer = cmds.tokenize(buffer[1], ";")
                                        #buffer = shlex.split(buffer[1], ";")
                                        postI = buffer[1].replace(';', '')
                                        #print("DKDEBUG: value of postI : " + str(postI))
                                    if line[2:8] == "keys {":
                                        line = next(fileID)
                                        #print("DKDEBUG: Value of line : " + line)
                                        # Progress progressBar one step further
                                        cmds.progressBar(progressBar_DK, edit=True, step=1)
                                        cmds.progressBar(progressBar_Maya, edit=True, step=1)
                                        while line[2:3] != "}":
                                            #Old code : argNum = len(cmds.tokenize(line, " ", buffer))
                                            buffer = shlex.split(line, " ")
                                            #print("DKDEBUG: value of buffer : " + str(buffer))
                                            argNum = len(buffer)
                                            readtime = float(buffer[0])
                                            value = float(buffer[1])
                                            inType = buffer[2]
                                            outType = buffer[3]
                                            #print("DKDEBUG: value of buffer[4] : " + str(buffer[4]))
                                            tanLock = bool(buffer[4])
                                            #weightLock = 1 if buffer[5] == "True" else 0
                                            weightLock = str(buffer[5])
                                            if weightLock == "True":
                                                intWeightLock = 1
                                            else:
                                                intWeightLock = 0
                                            #print("DKDEBUG: value of intWeightLock : " + str(intWeightLock))
                                            breakDown = int(buffer[6].replace(';', ''))
                                            if argNum > 7:
                                                #print("DKDEBUG: value of argNum : " + str(argNum))
                                                tan1 = float(buffer[7].replace(';', ''))
                                                #Old code : buffer2 = cmds.tokenize(buffer[8], ";")
                                                weight1 = float(buffer[8].replace(';', ''))
                                            if argNum > 9:
                                                tan2 = float(buffer[9].replace(';', ''))
                                                weight2 = float(buffer[10].replace(';', ''))
                                            # This function section does not rely on selected objects so it must be fed an object name. Could the attribute tag accept a syntax such as : objname.attribute? Tested : NO. So I added the node and the short attribute name to each setKeyframe, keytangeant and setinfinity
                                            #Old code : cmds.setKeyframe(time=readtime, value=value, bd=breakDown, at=curAttr)
                                            cmds.setKeyframe(node, time=readtime, value=value, bd=breakDown, at=attr)
                                            #cmds.keyTangent(time=(readtime, readtime), lock=tanLock, at=curAttr)
                                            cmds.keyTangent(node, time=(readtime, readtime), lock=tanLock, at=attr)
                                            if weightState == 1:
                                                #weighted = "keyTangent -edit -weightedTangents True " + curAttr , should be weightedTangents=True ?
                                                #cmds.evalDeferred(weighted)
                                                cmds.keyTangent(node, edit=True, weightedTangents=True, at=attr)
                                                cmds.keyTangent(node, time=(readtime, readtime), weightLock=intWeightLock, at=attr)
                                            if inType != "fixed" and outType != "fixed":
                                                cmds.keyTangent(node, e=True, a=True, time=(readtime, readtime), itt=inType, ott=outType, at=attr)
                                            if inType == "fixed" and outType != "fixed":
                                                cmds.keyTangent(node, e=True, a=True, time=(readtime, readtime), inAngle=tan1, inWeight=weight1, itt=inType, ott=outType, at=attr)
                                            if inType != "fixed" and outType == "fixed":
                                                cmds.keyTangent(node, e=True, a=True, time=(readtime, readtime), outAngle=tan1, inWeight=weight1, itt=inType, ott=outType, at=attr)
                                            if inType == "fixed" and outType == "fixed":
                                                cmds.keyTangent(node, e=True, a=True, time=(readtime, readtime), inAngle=tan1, inWeight=weight1, outAngle=tan2, outWeight=weight2, itt=inType, ott=outType, at=attr)
                                            #Old code : line = cmds.fgetline(fileID)
                                            line = next(fileID)
                                            # Progress progressBar one step further
                                            cmds.progressBar(progressBar_DK, edit=True, step=1)
                                            cmds.progressBar(progressBar_Maya, edit=True, step=1)
                                        cmds.setInfinity(node, poi=postI, pri=preI, at=attr)
                                        endit = 1
                        else:
                            if curAttr != "dk_skip":
                                cmds.warning("[" + curAttr + "] Does not exist... Skipping")
                                attrWarningCount.append(curAttr)
                    else:
                        if node != "dk_skip":
                            if lineCount == 1:
                                # If this is the first line to read data and the object does not exist... and user chooses to continue trying to import animation...
                                confirmMess = ("Object to import animation onto does not exist:\n" + node + "\nAnimation may not import properly.\nDo you want to continue trying to import animation?")
                                print("dkAnim: " + confirmMess)
                                nonExist = cmds.confirmDialog(title="Continue?? Object Does not Exist...", message=confirmMess, button=["Yes", "No"], defaultButton="No", cancelButton="No", dismissString="No",)
                                if nonExist == "No":
                                    # catch(deleteUI($progressWin_DK)) # close progresBar window
                                    print("dkAnim: " + nonExist + ", user stopped animation import.")
                                    return
                                else:
                                    print("dkAnim: " + nonExist + ", user Continued animation import.")
                            else:
                                cmds.warning("[" + node + "] Does not exist... Skipping")
                                warningCount.append(node)
            #old code : elif cmds.substring(line, 1, 10) == "sceneUnit ":
            elif line[:10] == "sceneUnit ":
                currentSceneUnit = cmds.currentUnit(q=True, linear=True)
                #Old code : parts = cmds.tokenize(line, " ")
                parts = shlex.split(line, " ")
                partsSize = len(parts)
                # Get second part of string data, remove trailing characters (i.e. whitespace, new line, tab, etc.)
                #Old code : unitData = cmds.substitute("[( \n\t\r)]*$", parts[1], "")
                unitData = re.sub("[( \n\t\r)]*$", "", parts[1])
                print("dkAnim: Storing current scene unit preference [" + currentSceneUnit + "] ")
                print("dkAnim: Setting current scene unit preference to [" + unitData + "] ")
                if len(unitData) > 0:
                    cmds.currentUnit(linear=unitData)
        if cmds.progressBar(progressBar_DK, q=True, isCancelled=True):
            print("dkAnim: User canceled importing animation file...")
            break
    # When the loop while line exits, you've reached the end of the file
    #Old code : cmds.fclose(fileID)
    fileID.close()
    # Set current scene unit back
    if currentSceneUnit != "":
        print("dkAnim: Setting current scene unit preference back to [" + currentSceneUnit + "] ")
        cmds.currentUnit(linear=currentSceneUnit)
    if len(attrWarningCount) > 0:
        # If there were warnings loading animation...
        attrWarningCount = list(set(attrWarningCount))
        cmds.warning("[" + str(len(attrWarningCount)) + "] attributes do NOT exist to import animation to.")
    if len(warningCount) > 0:
        # If there were warnings loading animation...
        warningCount = list(set(warningCount))
        controlCount = list(set(controlCount))
        cmds.warning("[" + str(len(warningCount)) + " of " + str(len(controlCount)) + "] controls do NOT exist to import animation to.")
    endTime = cmds.date(time=True)
    totalTime = cmds.timerX(startTime=startTimer)
    print("dk_animRead: Finished Reading Animation at [" + endTime + "]")
    print("dkAnim: Total elapsed time to Read Animation:   " + str(datetime.timedelta(seconds=round(totalTime))))
    cmds.select(clear=True)
    for item in selected:
        cmds.select(item, add=True)
    print("dkAnim: script completed")

#Comment out following line when not testing
#dkAnimEhEh()
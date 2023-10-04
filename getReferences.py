#Author- Craig Hollabaugh
#Description- prints designs with cross-project references

import adsk.core, adsk.fusion, adsk.cam, traceback

# logger
#   https://modthemachine.typepad.com/my_weblog/2021/03/log-debug-messages-in-fusion-360.html

# fusion api reference manual
#   https://help.autodesk.com/view/fusion360/ENU

# fusion object model
#   https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/ExtraFiles/Fusion.pdf

# fusion single-user project transfer to Team Hub
#   https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-move-projects-folders-and-designs-from-a-single-user-Hub-to-a-different-Team-Hub.html

# there's no doubt a faster way of doing this

debug = False
loggerFile = False

class UiLogger:
    def __init__(self, forceUpdate):  
        app = adsk.core.Application.get()
        ui  = app.userInterface
        palettes = ui.palettes
        self.textPalette = palettes.itemById("TextCommands")
        self.forceUpdate = forceUpdate
        self.textPalette.isVisible = True 
    
    def print(self, text): 
        self.textPalette.writeText(text)
        if (self.forceUpdate):
            adsk.doEvents() 

class FileLogger:
    def __init__(self, filePath): 
        try:
            open(filePath, 'a').close()
        
            self.filePath = filePath
        except:
            raise Exception("Could not open/create file = " + filePath)

    def print(self, text):
        with open(self.filePath, 'a') as txtFile:
            txtFile.writelines(text + '\r\n')

def scanFiles(project,folder,path):
    dataFiles = folder.dataFiles
    for i in range(len(dataFiles)):
        datafile = dataFiles.item(i)
        if debug or datafile.hasChildReferences or datafile.hasParentReferences: 
            logger.print(path+"/"+datafile.name)
        if datafile.hasChildReferences:
            for c in range(len(datafile.childReferences)):
                childProjectName = str(datafile.childReferences.item(c).parentProject.name)
                if childProjectName != project.name:
                    logger.print(" uses **    " + childProjectName+"   "+ str(datafile.childReferences.item(c).name))
                else:
                    logger.print(" uses       " + childProjectName+"   "+ str(datafile.childReferences.item(c).name))
        if datafile.hasParentReferences:
            for p in range(len(datafile.parentReferences)):
                parentName = str(datafile.parentReferences.item(p).name)
                parentProjectName = str(datafile.parentReferences.item(p).parentProject.name)
                if parentProjectName != project.name:
                    logger.print(" used in ** " + parentProjectName+"   "+ str(datafile.parentReferences.item(p).name))
                else:
                    logger.print(" used in    " + parentProjectName+"   "+ str(datafile.parentReferences.item(p).name))

def scanFolder(project,folder,path):
    scanFiles(project,folder,path)
    for i in range(len(folder.dataFolders)):
        childFolder = folder.dataFolders.item(i) 
        scanFolder(project,childFolder,path+"/"+childFolder.name)

if FileLogger:
    logger = FileLogger("/Users/holla/Documents/log.txt")
else:
    logger = UiLogger(True)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        logger.print("--- getReferences start")
        for i in range(len(app.data.dataProjects)):
            project = app.data.dataProjects.item(i)
            logger.print(  "--- scanning project \""+project.name+"\"")
            folder = project.rootFolder
            scanFolder(project,folder,project.name)
            logger.print(  "--- scanning project \""+project.name+"\" done\n")
            break

        logger.print("--- done ---")
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
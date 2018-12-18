
import configparser
import os
from .utils import raiseError, list_toString

class CfgParser:
    mandatoryFields = () #("builderToUse", "themeToUse")

    def __init__(self, cfgPath):
        # Useful information to store in order to display meaningful error
        # messages
        self.cfgPath = cfgPath 

        # configparser requires the "key = value" lines to be precesses by
        # a "[sectionName]" line. Since we don't use sections, artificially
        # add a section named "Dummy section" at the beginning of the file
        with open(cfgPath, 'r') as cfgFile:
            cfgFileContent = '[Dummy section]\n' + cfgFile.read()
        buildCfg = configparser.ConfigParser()
        buildCfg.read_string(cfgFileContent)
        self.cfgDict = buildCfg["Dummy section"]

        # Assess that all mandatory fields are present
        for field in self.mandatoryFields:
            if not field in self.cfgDict:
                msg = (f"Key \"{field}\" is mandatory in "
                      +f"configuration file \"{self.cfgPath}\"\n")
                otherMandatoryFields = set(self.mandatoryFields).difference([field])
                if otherMandatoryFields:
                    msg += f"\tOther mandatory fields: "
                    msg += list_toString(otherMandatoryFields)
                raiseError(msg)

        # Perform checks specific to specialization classes
        self.performChecks()

    def performChecks(self):
        pass

    def __getitem__(self, key):
        try: return self.cfgDict[key]
        except:
            raiseError(f"Key \"{key}\" could not be found in file "
                      +f"\"{self.cfgPath}\"")

class WebsiteCfgParser(CfgParser):
    mandatoryFields = ("websiteRoot",)



def getAvailableBuilders():
    builders = []
    for builderDir in os.scandir("builders/"):
        if builderDir.is_dir():
            builders.append(builderDir.name)
    return builders

def getAvailableThemes():
    themes = []
    for themeDir in os.scandir("themes/"):
        if themeDir.is_dir():
            themes.append(themeDir.name)
    return themes


class DirBuildingCfgParser(CfgParser):
    mandatoryFields = ("builderToUse", "themeToUse")

    def performChecks(self):
        # CHECK THAT BUILDER TO USE EXISTS
        availableBuilders = getAvailableBuilders()
        builderToUse = self.cfgDict["builderToUse"]
        if not builderToUse in availableBuilders:
            raiseError(f"Could not find builder: builderToUse = \"{builderToUse}\"\n"
                      +f"While parsing configuration file \"{self.cfgPath}\"\n"
                      +f"Known builders are: {list_toString(availableBuilders)}")

        # CHECK THAT THEME TO USE EXISTS
        availableThemes = getAvailableThemes()
        themeToUse = self.cfgDict["themeToUse"]
        if not themeToUse in availableThemes:
            print("While parsing configuration file \"{self.cfgPath}\"")
            raiseError(f"Could not find theme: themeToUse = \"{themeToUse}\"\n"
                      +f"While parsing configuration file \"{self.cfgPath}\"\n"
                      +f"Known themes are: {list_toString(availableThemes)}")



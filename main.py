# SpaceCheck_IFC - IFC toolkit and geometry engine
# Copyright (C) Elobo68
#
#
# SpaceCheck_IFC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpaceCheck_IFC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
#


import ifcopenshell.geom

from pydantic import  BaseModel, ConfigDict, Field


import ifcopenshell.api
import ifcopenshell
from ifcopenshell.util import shape,element
from ifcclash import ifcclash
import ifcopenshell.util.selector

import pandas as pd
import sys
import json
import logging

class Parameters_SpaceCheck(BaseModel):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True, json_schema_extra={
        'description': "Lorem Ipsum"})

    Path_ParamSave: str = Field(title="Titre",
                          description="Save location of the configuration Json",
                          default=None, examples=[""],TypeMeta="Path")

    Data_Model_Path: str = Field(title="Titre",
                          description="Path to the main model to check",
                          default=None, examples=[""],TypeMeta="Path")

    Space_Model_Path: str = Field(title="Titre",
                          description="Path to the space model",
                          default=None, examples=[""],TypeMeta="Path")

    Data_Selector: str = Field(title="Titre",
                                    description="Liste of all element to check, it use the IfcOpenShell Selector",
                                    default="IfcElement,!IfcWall,!IfcOpeningElement,!IfcFlowSegment,!IfcFlowFitting,!IfcCovering", examples=[""], TypeMeta="String")

    Space_Selector: str = Field(title="Titre",
                                    description="Select all the space of the model",
                                    default="IfcSpace", examples=[""], TypeMeta="String")

    Data_Save: str = Field(title="Titre",
                                  description="Save the data of the main model",
                                  default=None, examples=[""], TypeMeta="Path")

    Space_Save: str = Field(title="Titre",
                                  description="Save the data of the space model",
                                  default=None, examples=[""], TypeMeta="Path")

    Data_Property: str = Field(title="Titre",
                                  description="One Property to export form the model",
                                  default=None, examples=[""], TypeMeta="Path")

    Space_Property: str = Field(title="Titre",
                                  description="One Property to export form the model",
                                  default=None, examples=[""], TypeMeta="Path")






    Clash_Name: str = Field(title="Titre",
                          description="Name of the clash check, needed by IfcClash",
                          default="Nom Clash Exemple", examples=[""],TypeMeta="String")

    Clash_Mode: str = Field(title="Titre",
                          description="Mode of the clash, needed by IfcClash",
                          default="intersection", examples=[""],TypeMeta="Data")

    Clash_Tolerance: float = Field(title="Titre",
                          description="Tolerance of the clash needed by IfcClash",
                          default=0, examples=[""],TypeMeta="Data")

    Clash_CheckAll: bool = Field(title="Titre",
                          description="Parameter of IfcClash, needed by IfcClash",
                          default=False, examples=[""],TypeMeta="Data")








    Space_ModeSelect: str = Field(title="Titre",
                           description="Needed by IfcClash",
                           default="i", examples=[""], TypeMeta="Data")


    Data_ModeSelect: str = Field(title="Titre",
                           description="Needed by IfcClash",
                           default="i", examples=[""], TypeMeta="Data")



    Json_Clash1: str = Field(title="Titre",
                                    description="",
                                    default=None, examples=[""], TypeMeta="Path")

    CSV_Clash1: str = Field(title="Titre",
                                        description="Description",
                                        default=None, examples=[""], TypeMeta="Path")

    Path_MissObject: str = Field(title="Titre",
                                     description="Description",
                                     default=None, examples=[""], TypeMeta="Path")

    Json_Clash2: str = Field(title="Titre",
                                    description="Description",
                                    default=None, examples=[""], TypeMeta="Path")

    CSV_Clash2: str = Field(title="Titre",
                                        description="Description",
                                        default=None, examples=[""], TypeMeta="Path")


    Path_Result: str = Field(title="Titre",
                                        description="Description",
                                        default=None, examples=[""], TypeMeta="Path")



    def Creation_JSON_Configuration_Clash(self):
        DictNomClash={"name":self.Clash_Name,
        "mode":self.Clash_Mode ,
        "tolerance":self.Clash_Tolerance ,
        "check_all":self.Clash_CheckAll }

        DictGroupeA={"file":self.Space_Model_Path,
        "selector":self.Space_Selector ,
        "mode":self.Space_ModeSelect }

        DictGroupeB={"file":self.Data_Model_Path,
        "selector":self.Data_Selector ,
        "mode":self.Data_ModeSelect }

        DictNomClash["a"]=[DictGroupeA]
        DictNomClash["b"] = [DictGroupeB]

        return DictNomClash

    def CorrectionFormatMetadonnee(self):
        if type(self.Clash_Tolerance) is not float:
            self.Clash_Tolerance=float(self.Clash_Tolerance)
        if type(self.Clash_CheckAll) is not bool:
            self.Clash_CheckAll=bool(self.Clash_CheckAll)


def Step1_Clash(LaConfiguration):
    LaConfiguration.CorrectionFormatMetadonnee()

    settings = ifcclash.ClashSettings()
    settings.output = LaConfiguration.Json_Clash1
    settings.logger = logging.getLogger("Clash")
    settings.logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    settings.logger.addHandler(handler)
    ifc_clasher = ifcclash.Clasher(settings)

    ifc_clasher.clash_sets = [LaConfiguration.Creation_JSON_Configuration_Clash()]

    ifc_clasher.clash()
    ifc_clasher.export()


def Step2_DataExport(LaConfiguration):
    def FonctionExtractionData(elements, Parameters_SpaceCheck,SpaceOrData):

        Pset_Prop=None
        Pset=None
        Prop=None

        if SpaceOrData=="Space" and not Parameters_SpaceCheck.Space_Property is None:
            Pset_Prop=Parameters_SpaceCheck.Space_Property
            Pset=Pset_Prop.split(".")[0]
            Prop = Pset_Prop.split(".")[1]
        if SpaceOrData=="Data" and not Parameters_SpaceCheck.Data_Property is None:
            Pset_Prop=Parameters_SpaceCheck.Data_Property
            Pset=Pset_Prop.split(".")[0]
            Prop = Pset_Prop.split(".")[1]


        ListDict=[]
        for OneElement in elements:
            Dict={}

            Dict["IFC_GUID"]=OneElement.GlobalId
            Dict["IFC_Name"]=OneElement.Name
            Dict["IFC_Class"] = OneElement.is_a()

            try:
                Dict["Pset_Prop"] = ifcopenshell.util.element.get_pset(OneElement, name=Pset, prop=Prop)
            except:
                Dict["Pset_Prop"]=""

            ListDict.append(Dict)

        DF_IFC=pd.DataFrame.from_dict(ListDict)

        return DF_IFC

    LaConfiguration.CorrectionFormatMetadonnee()

    MNEspace=ifcopenshell.open(LaConfiguration.Space_Model_Path)
    Espaces=ifcopenshell.util.selector.filter_elements(MNEspace, LaConfiguration.Space_Selector)

    MNMetier=ifcopenshell.open(LaConfiguration.Data_Model_Path)
    Metiers = ifcopenshell.util.selector.filter_elements(MNMetier, LaConfiguration.Data_Selector)

    df_Space = FonctionExtractionData(Espaces,LaConfiguration,"Space")
    df_Metier = FonctionExtractionData(Metiers, LaConfiguration,"Data")

    df_Space.to_csv(LaConfiguration.Space_Save,sep="|")
    df_Metier.to_csv(LaConfiguration.Data_Save, sep="|")

def Step2_Fuse(LaConfiguration):

    df_Lien=Read_Clash_Result(LaConfiguration.Json_Clash1)

    df_Space=pd.read_csv(LaConfiguration.Space_Save,sep="|")
    df_Metier=pd.read_csv(LaConfiguration.Data_Save, sep="|")

    df_Lien = df_Lien.merge(df_Space,how="outer",left_on="b_global_id",right_on="IFC_GUID")
    df_Lien = df_Lien.merge(df_Metier, how="outer", left_on="a_global_id", right_on="IFC_GUID",suffixes=('_Space', '_Object'))


    df_Lien=df_Lien[["a_global_id","b_global_id","IFC_GUID_Object","IFC_GUID_Space","IFC_Name_Space","IFC_Name_Object",'IFC_Class_Space',"IFC_Class_Object","Pset_Prop_Space","Pset_Prop_Object","distance","type","p1","p2"]]
    df_Lien["Path_Space"] = LaConfiguration.Space_Model_Path
    df_Lien["Path_Data"] = LaConfiguration.Data_Model_Path

    df_Lien.to_csv(LaConfiguration.CSV_Clash1, sep="|")

    NomColonne = "WithoutSpace"
    Filtre = df_Lien["IFC_Name_Space"].isna()
    df_Lien[NomColonne] = False
    df_Lien[NomColonne].loc[Filtre] = True

    df_EnErreure = df_Lien.loc[Filtre]
    df_EnErreure.to_csv(LaConfiguration.Path_MissObject, sep="|")

    print("End of First Compilation")

def Step3_Clash_Part2(LaConfiguration):

    def Creation_Configuration_Clearance(LaConfiguration,ListeEquipement):

        Texte=""
        for x in ListeEquipement:
            if Texte=="":
                Texte=x
            else:
                Texte=Texte+","+x


        DictNomClash = {"name": LaConfiguration.Clash_Name,
                        "mode": "clearance",
                        "clearance": 3,
                        "check_all": True}

        DictGroupeA = {"file": LaConfiguration.Space_Model_Path,
                       "selector": LaConfiguration.Space_Selector,
                       "mode": LaConfiguration.Space_ModeSelect}

        DictGroupeB = {"file": LaConfiguration.Data_Model_Path,
                       "selector": Texte,
                       "mode": LaConfiguration.Data_ModeSelect}

        DictNomClash["a"] = [DictGroupeA]
        DictNomClash["b"] = [DictGroupeB]

        return DictNomClash

    df=pd.read_csv(LaConfiguration.Path_MissObject, sep="|")

    ListeEquipement=df["IFC_GUID_Object"].to_list()
    Configuration_Clash=Creation_Configuration_Clearance(LaConfiguration,ListeEquipement)

    settings = ifcclash.ClashSettings()
    settings.output = LaConfiguration.Json_Clash2
    settings.logger = logging.getLogger(None)
    settings.logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    settings.logger.addHandler(handler)
    ifc_clasher = ifcclash.Clasher(settings)

    ifc_clasher.clash_sets = [Configuration_Clash]

    ifc_clasher.clash()
    ifc_clasher.export()

def Step4_Fuse_Part2(LaConfiguration):
    df_Link2=Read_Clash_Result(LaConfiguration.Json_Clash2)

    df_Space=pd.read_csv(LaConfiguration.Space_Save,sep="|")
    df_Metier=pd.read_csv(LaConfiguration.Data_Save, sep="|")

    df_Link2 = df_Link2.merge(df_Space,how="outer",left_on="b_global_id",right_on="IFC_GUID")
    df_Link2 = df_Link2.merge(df_Metier, how="outer", left_on="a_global_id", right_on="IFC_GUID",suffixes=('_Space', '_Object'))

    df_Link2 = df_Link2[["a_global_id","b_global_id","IFC_GUID_Object","IFC_GUID_Space","IFC_Name_Space","IFC_Name_Object",'IFC_Class_Space',"IFC_Class_Object","Pset_Prop_Space","Pset_Prop_Object","distance","type","p1","p2"]]
    df_Link2["Path_Space"] = LaConfiguration.Space_Model_Path
    df_Link2["Path_Data"] = LaConfiguration.Data_Model_Path

    Filtre=df_Link2["IFC_GUID_Space"].isna()
    df_Link2=df_Link2.loc[~Filtre]

    df_Link2.to_csv(LaConfiguration.CSV_Clash2, sep="|")

    ###======================COMPILATION CLASH 1 ET CLASH 2
    df_Link1=pd.read_csv(LaConfiguration.CSV_Clash1,sep="|")
    df_Link1["From"] = "Clash1"
    df_Link2["From"] = "CLash2"

    df_Lien_Complet=pd.concat([df_Link1,df_Link2])
    df_Lien_Complet.sort_values(by='From', ascending=False,inplace=True)
    df_Lien_Complet.sort_values(by='distance', ascending=True, inplace=True)
    df_Lien_Complet.drop_duplicates(subset=['IFC_GUID_Object'], keep='first',inplace=True)

    Filtre=df_Lien_Complet["IFC_GUID_Object"].isna()
    df_Lien_Complet=df_Lien_Complet.loc[~Filtre]

    df_Lien_Complet.to_csv(LaConfiguration.Path_Result,sep="|")

    print("End of 2nd analyze")

def Read_Clash_Result(JsonPath):
    f = open(JsonPath)
    # returns JSON object as a dictionary
    data = json.load(f)[0]
    LesClashes = data["clashes"]

    ListeOfDict = []

    for x in LesClashes:
        ListeOfDict.append(LesClashes[x])

    df=pd.DataFrame(ListeOfDict)

    df.rename(columns={"a_global_id": "a", "b_global_id": "c"})

    Filtre=df["b_ifc_class"]=="IfcSpace"
    Df_B_Space=df.loc[Filtre]
    Df_A_Space=df.loc[~Filtre]
    DictRenamne={'a_global_id':"b_global_id", 'b_global_id':"a_global_id", 'a_ifc_class':"b_ifc_class", 'b_ifc_class':"a_ifc_class", 'a_name':"b_name",'b_name':"a_name","p2":"p1","p1":"p2"}
    Df_A_Space=Df_A_Space.rename(columns=DictRenamne)

    df=pd.concat([Df_B_Space,Df_A_Space])

    return df




if __name__ == '__main__':

    pd.options.mode.chained_assignment = None

    Param=Parameters_SpaceCheck()

    Param.Path_ParamSave = r"C:\Users\Public\Space_Check\Configuration.json"

    Param.Space_Model_Path = r"C:\Users\Public\Space_Check\PN1801_17_EXE_MOD_000177_01_H_0810P_GEN_2x3-Finale.ifc"
    Param.Data_Model_Path=r"C:\Users\Public\Space_Check\PN1629_64_EXE_MOD_000154_03_E_0810P_G10_V20.ifc"

    Param.Space_Save = r"C:\Users\Public\Space_Check\Espace_Data.csv"
    Param.Data_Save = r"C:\Users\Public\Space_Check\Metier_Data.csv"

    Param.Space_Property = r"Pset_SpaceCommon.Reference"
    Param.Data_Property = r"Pset_SpaceCommon.Reference"


    Param.Json_Clash1 = r"C:\Users\Public\Space_Check\Lien_Clash1.json"
    Param.CSV_Clash1 = r"C:\Users\Public\Space_Check\Resultat_Clash1.csv"
    Param.Path_MissObject = r"C:\Users\Public\Space_Check\Non_Correspondance.csv"
    Param.Json_Clash2 = r"C:\Users\Public\Space_Check\Lien_Clash2.json"
    Param.CSV_Clash2 = r"C:\Users\Public\Space_Check\Resultat_Clash2.csv"
    Param.Path_Result= r"C:\Users\Public\Space_Check\Compilation_Resultat_Clash_TEST_IGR.csv"

    Step1_Clash(Param)
    Step2_DataExport(Param)
    Step2_Fuse(Param)
    Step3_Clash_Part2(Param)
    Step4_Fuse_Part2(Param)



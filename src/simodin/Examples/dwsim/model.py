from ... import interface as link
import pythoncom
pythoncom.CoInitialize()

import clr

from System.IO import Directory, Path, File
from System import String, Environment

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation3
from DWSIM.GlobalSettings import Settings

class dwsim_model(link.SimModel):
    def init_model(self, dwsimpath, **params):
        '''
        dwsim_path: Path to the DWSIM executable. Should be something like:
        C:\\Users\\USERNAME\\AppData\\Local\\DWSIM\\
        '''
        
        clr.AddReference(dwsimpath + "CapeOpen.dll")
        clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
        clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
        clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
        clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
        clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
        clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.ThermoC.dll")
        clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")
        clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
        clr.AddReference(dwsimpath + "System.Buffers.dll")



        self.params = params
        Directory.SetCurrentDirectory(dwsimpath)

        # create automation manager
        self.interf = Automation3()
        self.model = self.interf.CreateFlowsheet()

        # add water
        water = self.model.AvailableCompounds["Water"]
        self.model.SelectedCompounds.Add(water.Name, water)

        # create and connect objects
        m1 =self.model.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
        m2 =self.model.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
        e1 =self.model.AddObject(ObjectType.EnergyStream, 100, 50, "power")
        h1 =self.model.AddObject(ObjectType.Heater, 100, 50, "heater")

        m1 = m1.GetAsObject()
        m2 = m2.GetAsObject()
        e1 = e1.GetAsObject()
        h1 = h1.GetAsObject()

        self.model.ConnectObjects(m1.GraphicObject, h1.GraphicObject, -1, -1)
        self.model.ConnectObjects(h1.GraphicObject, m2.GraphicObject, -1, -1)
        self.model.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1)

        self.model.AutoLayout()

        # steam tables property package
        stables = PropertyPackages.SteamTablesPropertyPackage()
        self.model.AddPropertyPackage(stables)

        # set inlet stream temperature
        # default properties: T = 298.15 K, P = 101325 Pa, Mass Flow = 1 kg/s

        m1.SetTemperature(300.0) # K
        m1.SetMassFlow(self.params['massflow']) # kg/s

        # set heater outlet temperature

        h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
        h1.OutletTemperature = 400 # K

        
    def calculate_model(self, **model_params):
        '''
        Abstract method to calculate the model based on the parameters provided.
        '''
        
        # request a calculation
        Settings.SolverMode = 0
        errors = self.interf.CalculateFlowsheet2(self.model)

        print(String.Format("Heater Heat Load: {0} kW", self.model.GetObject('heater').GetAsObject().DeltaQ))

    @property
    def technosphere(self):
        technosphere={
            'thermal energy demand':link.technosphere_edge(name= 'thermal energy demand', 
                                                    source = None,
                                                    target = self,
                                                    amount= self.model.GetObject('power').GetAsObject().GetEnergyFlow, 
                                                                                #self.model.GetObject('power').GetAsObject().GetPropertyUnit('PROP_ES_0'))*self.ureg.second,
                                                    model_unit=f'{self.model.GetObject('power').GetAsObject().GetPropertyUnit('PROP_ES_0')} * second',
                                                    type= link.technosphereTypes.input,

                                                           ),
            'heated flow': link.technosphere_edge(name= 'thermal energy demand',
                                                    source= self,
                                                    target = None,
                                                    amount= self.model.GetObject('outlet').GetAsObject().GetMassFlow, 
                                                            #                 self.model.GetObject('outlet').GetAsObject().GetPropertyUnit('PROP_MS_2')),
                                                    model_unit=self.model.GetObject('outlet').GetAsObject().GetPropertyUnit('PROP_MS_2'),
                                                    type=link.technosphereTypes.product,
                                                    allocationfactor= 1.0,
                                                    functional= True)
        }
        return technosphere
    
    @property
    def biosphere(self):
        return {}
    
    def recalculate_model(self, **model_params):
        '''
        Abstract method to recalculate the model based on the parameters provided.
        '''
        pass

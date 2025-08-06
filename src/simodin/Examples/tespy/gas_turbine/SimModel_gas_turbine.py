from simodin import interface as link
from simodin import tespy 

from tespy.networks import Network
from tespy.components import (
    DiabaticCombustionChamber, Turbine, Source, Sink, Compressor,
    Generator, PowerBus, PowerSink
)
from tespy.connections import Connection, Ref, PowerConnection

class tespy_model(link.SimModel):
    def __init__(self,name):
        super().__init__(name=name)
        self.ureg.define('m3 = meter**3')


    def init_model(self,  **params):
        self.model = Network(p_unit="bar", T_unit="C")

        cp = Compressor("Compressor")
        cc = DiabaticCombustionChamber("combustion chamber")
        tu = Turbine("turbine")
        air = Source("air source")
        fuel = Source("fuel source")
        fg = Sink("flue gas sink")
        c1 = Connection(air, "out1", cp, "in1", label="1")
        c2 = Connection(cp, "out1", cc, "in1", label="2")
        c3 = Connection(cc, "out1", tu, "in1", label="3")
        c4 = Connection(tu, "out1", fg, "in1", label="4")
        c5 = Connection(fuel, "out1", cc, "in2", label="5")
    
        cc.set_attr(pr=1, eta=1, lamb=1.5, ti=10e6)
        c5.set_attr(p=1, T=20, fluid={"CO2": 0.04, "CH4": 0.96, "H2": 0})
        
        self.model.add_conns(c1, c2, c3, c4, c5)

        generator = Generator("generator")
        grid = PowerSink("grid")
        shaft = PowerBus("shaft", num_in=1, num_out=2)

        e1 = PowerConnection(tu, "power", shaft, "power_in1", label="e1")
        e2 = PowerConnection(shaft, "power_out1", cp, "power", label="e2")
        e3 = PowerConnection(shaft, "power_out2", generator, "power_in", label="e3")
        e4 = PowerConnection(generator, "power_out", grid, "power", label="e4")

        self.model.add_conns(e1, e2, e3, e4)

        generator.set_attr(eta=0.98)
        cp.set_attr(eta_s=0.85, pr=15)
        tu.set_attr(eta_s=0.90)
        c1.set_attr(
            p=1, T=20,
            fluid={"Ar": 0.0129, "N2": 0.7553, "CO2": 0.0004, "O2": 0.2314}
        )
        #c3.set_attr(m=30)
        c4.set_attr(p=Ref(c1, 1, 0))

   

    def calculate_model(self):
        self.model.solve("design")
        
        # unset the value, set Referenced value instead
        self.model.get_conn('5').set_attr(p=None)
        self.model.get_conn('5').set_attr(p=Ref(self.model.get_conn('2'), 1.05, 0))
        self.model.solve("design")

    def recalculate_model(self, **model_params):
        return super().recalculate_model(**model_params)
    
    @property
    def technosphere(self):
        #get all technosphere flows:
        technosphere=tespy.extract_technosphere_flows(self, self.model)
        technosphere['fuel source'].amount = (self.ureg.Quantity(self.model.get_conn('5').v.val,
                                        self.model.get_conn('5').v.unit)
                                        * self.ureg.hour
                                        ).to('meter**3')
        del technosphere['flue gas sink']
        #set functional unit:
        technosphere['grid'].functional = True
        return technosphere
        
    @property
    def biosphere(self) -> dict:
        biosphere={}
        biosphere['flue gas sink']=link.biosphere_edge(
            name='flue gas sink',
            source= self,
            target= None,
            amount= (self.ureg.Quantity(self.model.get_conn('4').m.val*
                                        self.model.get_conn('4').fluid.val['CO2'],
                                        self.model.get_conn('4').m.unit)
                                        * self.ureg.hour
                                        ).to('kg'),
        )
        return biosphere
    
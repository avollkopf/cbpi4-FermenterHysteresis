import asyncio
from asyncio import tasks
import logging
from cbpi.api import *
import aiohttp
from aiohttp import web
from cbpi.controller.kettle_controller import KettleController
from cbpi.api.dataclasses import Kettle, Props, Step
from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType
import json
import webbrowser

class FermenterAutostart(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())
        self.controller : KettleController = cbpi.kettle


    async def run(self):
        logging.info("Starting Fermenter Autorun")
        #get all kettles
        self.kettle = self.controller.get_state()
        for id in self.kettle['data']:
            if (id['type']) == "Fermenter Hysteresis":
                try:
                    self.autostart=(id['props']['AutoStart'])
                    logging.info(self.autostart)
                    if self.autostart == "Yes":
                        fermenter_id=(id['id'])
                        self.fermenter=self.cbpi.kettle.find_by_id(fermenter_id)
                        logging.info(self.fermenter)
                        try:
                            if (self.fermenter.instance is None or self.fermenter.instance.state == False):
                                await self.cbpi.kettle.toggle(self.fermenter.id)
                                logging.info("Successfully switched on Ferenterlogic for Fermenter {}".format(self.fermenter.id))
                        except Exception as e:
                            logging.error("Failed to switch on FermenterLogic {} {}".format(self.fermenter.id, e))
                except:
                    pass


@parameters([Property.Number(label="HeaterOffsetOn", configurable=True, description="Offset as decimal number when the heater is switched on. Should be greater then 'HeaterOffsetOff'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="HeaterOffsetOff", configurable=True, description="Offset as decimal number when the heater is switched off. Should be smaller then 'HeaterOffsetOn'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="CoolerOffsetOn", configurable=True, description="Offset as decimal number when the cooler is switched on. Should be greater then 'CoolerOffsetOff'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="CoolerOffsetOff", configurable=True, description="Offset as decimal number when the cooler is switched off. Should be smaller then 'CoolerOffsetOn'. For example a value of 1 switches off the cooler if the current temperature is 1 degree below the target temperature"),
             Property.Select(label="AutoStart", options=["Yes","No"],description="Autostart Fermenter on cbpi start"),
             Property.Text(label="BrewName", configurable=True,description="Name of your Beer"),
             Property.Number(label="TargetTemp", configurable=True, description="Fermenter Target Temp"),
             Property.Sensor(label="sensor2",description="Optional Sensor (e.g. iSpindle)")])

class FermenterHysteresis(CBPiKettleLogic):
    
    async def run(self):
        try:
            self.heater_offset_min = float(self.props.get("HeaterOffsetOn", 0))
            self.heater_offset_max = float(self.props.get("HeaterOffsetOff", 0))
            self.cooler_offset_min = float(self.props.get("CoolerOffsetOn", 0))
            self.cooler_offset_max = float(self.props.get("CoolerOffsetOff", 0))
        
            self.kettle = self.get_kettle(self.id)
            self.heater = self.kettle.heater
            self.cooler = self.kettle.agitator

            target_temp = self.get_kettle_target_temp(self.id)
            if target_temp == 0:
                await self.set_target_temp(self.id,int(self.props.get("TargetTemp", 0)))
 

            while self.running == True:
                
                sensor_value = self.get_sensor_value(self.kettle.sensor).get("value")
                target_temp = self.get_kettle_target_temp(self.id)

                if sensor_value + self.heater_offset_min <= target_temp:
                    if self.heater:
                        await self.actor_on(self.heater)
                    
                if sensor_value + self.heater_offset_max >= target_temp:
                    if self.heater:
                        await self.actor_off(self.heater)

                if sensor_value >=  self.cooler_offset_min + target_temp:
                    if self.cooler:
                        await self.actor_on(self.cooler)
                    
                if sensor_value <= self.cooler_offset_max + target_temp:
                    if self.cooler:
                        await self.actor_off(self.cooler)

                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("CustomLogic Error {}".format(e))
        finally:
            self.running = False
            if self.heater:
                await self.actor_off(self.heater)
            if self.cooler:
                await self.actor_off(self.cooler)



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("Fermenter Hysteresis", FermenterHysteresis)
    cbpi.plugin.register("Fermenter Autostartt", FermenterAutostart)

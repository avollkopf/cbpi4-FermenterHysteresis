# Craftbeerpi4 Plugin for simple Fermenter Logic (Hysteresis) 

As long as femrentation is not yet integrated with CBPi4, the user can define a kettle as fermenter.

Installation / Configuration:
1. Install this plugin
2. Add a kettle to the hardware and select corresponding temp sensor, heater (Actor) and cooler (Agitator) elements
3. Select Fermenter Hysteresis as Kettle logic
4. Configure the on and off parameters as you did with cbpi3
5. Set a target temperature in the Fermenter logic
6. Select Yes or No for Autostart.
7. Add the kettle and  kettle logic to your dashboard

Operation:
1. You can select a temperatur as target temp in the dashboard (if not or set to 0, the temperature defined in the logic will be choosen)
2. Push the Autostart Symbol for your kettle logic and the Logic will start and run your Kettle at the selected temp while switching either heater or cooler on and off.
3. If you reboot your system and Autostart is set to Yes, the logic will be switched back on for this particular Fermenter with the target temperature set in the logic

By using this plugin, you can run several fermenters in parallel in auto mode and run also a kettle for brewing in addition.

Only drawback is that you cannot define different temperatures and times. Therefore, we need to wait for Manuel

- Software installation:

	- sudo pip3 install cbpi4-FermenterHysteresis
	- or install from repo: sudo pip3 install https://github.com/avollkopf/cbpi4-FermenterHysteresis/archive/main.zip 
	- cbpi add cbpi4-FermenterHysteresis

- Changelog:

	- 28.08.21 (0.0.2): Cooler and Heater are now optional, fix descriptions
	- 11.06.21 (0.0.1): Initial Release

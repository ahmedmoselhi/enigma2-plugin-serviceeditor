class Transponder:
	essential = [
			"frequency",
			"polarization",
			"symbol_rate",
			]
		
	niceToHave = [
			"system",
			"fec_inner",
			"tsid",
			"onid",
			]
		
	transSystem = {
			"0":"DVB-S",
			"1":"DVB-S2",
			"dvb-s":"DVB-S",
			"dvb-s2":"DVB-S2",
			}
		
	reTransSystem = {
			"DVB-S":"0",
			"DVB-S2":"1",
			}
		
	transPolarisation = {
			"0":"H",
			"h":"H",
			"1":"V",
			"v":"V",
			"2":"L",
			"cl":"L",
			"l":"L",
			"3":"R",
			"cr":"R",
			"r":"R",
			"i":"i",
			}
		
	reTransPolarisation = {
			"H":"0",
			"V":"1",
			"L":"2",
			"R":"3",
			}
		
	transModulation = {
			"0":"AUTO",
			"1":"QPSK",
			"2":"8PSK",
			"3":"QAM16",
			}
		
	reTransModulation = {
			"AUTO" :"0",
			"QPSK" :"1",
			"8PSK" :"2",
			"QAM16":"3",
			}
		
	transRolloff = {
			"0":"0_35",
			"1":"0_25",
			"2":"0_20",
			}
		
	reTransRolloff = {
			"0_35":"0",
			"0_25":"1",
			"0_20":"2",
			}
		
	transOnOff = {
			"0":"OFF",
			"1":"ON",
			"2":"AUTO",
			}
	reTransOnOff = {
			"OFF" :"0",
			"ON"  :"1",
			"AUTO":"2",
			}
		
	transFec = {
			"0":"FEC_AUTO",
			"1":"FEC_1_2",
			"2":"FEC_2_3",
			"3":"FEC_3_4",
			"4":"FEC_5_6",
			"5":"FEC_7_8",
			"6":"FEC_8_9",
			"7":"FEC_3_5",
			"8":"FEC_4_5",
			"9":"FEC_9_10",
			"15":"FEC_NONE",
			"auto":"FEC_AUTO",
			"1/2":"FEC_1_2",
			"2/3":"FEC_2_3",
			"3/4":"FEC_3_4",
			"5/6":"FEC_5_6",
			"7/8":"FEC_7_8",
			"8/9":"FEC_8_9",
			"3/5":"FEC_3_5",
			"4/5":"FEC_4_5",
			"9/10":"FEC_9_10",
			"none":"FEC_NONE",
			}
		
	reTransFec = {
			"FEC_AUTO":"0",
			"FEC_1_2":"1",
			"FEC_2_3":"2",
			"FEC_3_4":"3",
			"FEC_5_6":"4",
			"FEC_7_8":"5",
			"FEC_8_9":"6",
			"FEC_3_5":"7",
			"FEC_4_5":"8",
			"FEC_9_10":"9",
			"FEC_NONE":"15",
			}

	onlyDVBS2Fec = [
			"FEC_8_9",
			"FEC_3_5",
			"FEC_4_5",
			"FEC_9_10",
			]
	
	transBand = {
		"KU":("10700000","12750000"),
		"C":("3400000","4200000"),
	}
	
	def __init__(self,transponder):
		self.rawData = transponder
		
		self.system = "DVB-S"
		self.__frequency = "10700000"
		self.__symbolrate = "27500000"
		self.polarisation = "H"
		self.modulation = "QPSK"
		self.pilot = "OFF"
		self.rolloff = "0_35"
		self.fec = "FEC_AUTO"
		self.inversion = "AUTO"
		self.__tsid = "0"
		self.useTsid = False
		self.__onid = "0"
		self.useOnid = False
		self.band = "KU"
		self.__importColor = None
		self.transponderDoctor(self.rawData)
	
	def transponderDoctor(self,transponder):
		if not isinstance(transponder, dict):
			print "transponderDoctor: Transponderdaten muessen vom Type DICT sein"
			print transponder
			return

		param = transponder.keys()	# erst mal sehn welche Parameter wir bekommen
		
		#dann wird alles in kleinbuchstaben uebersetzt
		transParam = {}
		for x in param:
			transParam[x] = x.lower()
		if "polarisation" in transParam:
			transParam.update({"polarization":transParam.get("polarisation").lower()})
			del transParam["polarisation"]
		
## check essential parameters #################
		missing = []
		for x in self.essential:
			if x not in transParam:
				missing.append(x)
		if len(missing):
			print "transponderDoctor: Folgende Parameter fehlen:", missing
			return		# da laesst sich nichts machen
		
		self.polarisation = self.transPolarisation.get(transponder.get(transParam.get("polarization"),"i").lower())
		if self.polarisation == "i":
			print "transponderDoctor: unbekannter Wert fuer Polarisation (%s)" %transParam.get("polarization")
			return		# da laesst sich nichts machen
		
		self.__frequency = transponder.get(transParam.get("frequency"),"i").lower()
		
		self.__symbolrate = transponder.get(transParam.get("symbol_rate"),"i").lower()

# welches system?  ##########################################
		dvb_s_cnt = 0
		dvb_s2_cnt = 0
			
		self.__importColor = transponder.get("import",None)
		
		if "system" in transParam:
			self.system = self.transSystem.get(transponder.get(transParam.get("system"),"i").lower())
			if self.system == "DVB-S":
				dvb_s_cnt += 1
			if self.system == "DVB-S2":
				dvb_s2_cnt += 1
		
		if "modulation" in transParam:
			self.modulation = self.transModulation.get(transponder.get(transParam.get("modulation"),"i").lower())
			if (self.modulation == "8PSK") or (self.modulation == "QAM16"):
				dvb_s2_cnt += 1

		if "pilot" in transParam:
			self.pilot = self.transOnOff.get(transponder.get(transParam.get("pilot"),"i").lower())
			if (self.pilot == "ON") or (self.pilot == "AUTO"):
				dvb_s2_cnt += 1

		if "rolloff" in transParam:
			self.rolloff = self.transRolloff.get(transponder.get(transParam.get("rolloff"),"i").lower())
			if (self.rolloff == "0_25"):
				dvb_s2_cnt += 1

		if "fec_inner" in transParam:
			self.fec = self.transFec.get(transponder.get(transParam.get("fec_inner"),"i").lower())
			if self.fec in self.onlyDVBS2Fec:
				dvb_s2_cnt += 1

		if dvb_s2_cnt:
			self.system = "DVB-S2"
		else:
			self.system = "DVB-S"
		
		if "inversion" in transParam:
			self.inversion = self.transOnOff.get(transponder.get(transParam.get("inversion"),"i").lower())

		if "tsid" in transParam:
			self.__tsid = transponder.get(transParam.get("tsid"),"i").lower()
			self.useTsid = True
		
		if "onid" in transParam:
			self.__onid = transponder.get(transParam.get("onid"),"i").lower()
			self.useOnid = True

	def getFrequency(self):
		return self.__frequency
	
	def setFrequency(self,frequency):
		if isinstance(frequency, list):
			if len(frequency) == 2:
				if isinstance(frequency[0], int) and isinstance(frequency[1], int):
					self.__frequency = str(frequency[0]*1000 + frequency[1])
					return
		else:
			self.__frequency = str(frequency)
	
	frequency = property(getFrequency, setFrequency)
	
	importColor = property(lambda self:self.__importColor)
	
	def getSymbolrate(self):
		return self.__symbolrate
	
	def setSymbolrate(self,symbolrate):
		self.__symbolrate = str(symbolrate)
	
	symbolrate = property(getSymbolrate, setSymbolrate)
	
	
	def setTsid(self,newTsid):
		self.__tsid = str(newTsid)
	
	tsid = property(lambda self:self.__tsid, setTsid)
	
	
	def getOnid(self):
		return self.__onid
	
	def setOnid(self,newOnid):
		self.__onid = str(newOnid)
	
	onid = property(lambda self:self.__onid, setOnid)
	
	def exportImportColor(self):
		return {"import":self.__importColor}
	
	def exportSystem(self):
		return {"system":self.reTransSystem.get(self.system)}
	
	def exportFec(self):
		return {"fec_inner":self.reTransFec.get(self.fec)}
	
	
	def exportFrequency(self):
		return {"frequency":self.__frequency}
	
	def exportPolarisation(self):
		return {"polarization":self.reTransPolarisation.get(self.polarisation)}
	
	def exportSymbolrate(self):
		return {"symbol_rate":self.__symbolrate}
	
	def exportModulation(self):
		return {"modulation":self.reTransModulation.get(self.modulation)}

	def exportOnid(self):
		return {"onid":self.__onid}

	def exportTsid(self):
		return {"tsid":self.__tsid}
		
	def exportInversion(self):
		return {"inversion":self.reTransOnOff.get(self.inversion)}
		
	def exportPilot(self):
		return {"pilot":self.reTransOnOff.get(self.pilot)}
			
	def exportRolloff(self):
		return {"rolloff":self.reTransRolloff.get(self.rolloff)}
	
	def exportClean(self):
		res = {}
		res.update(self.exportSystem())
		res.update(self.exportFec())
		res.update(self.exportFrequency())
		res.update(self.exportPolarisation())
		res.update(self.exportSymbolrate())
		res.update(self.exportModulation())
		if self.useOnid:
			res.update(self.exportOnid())
		if self.useTsid:
			res.update(self.exportTsid())
		if self.inversion != "AUTO" :
			res.update(self.exportInversion())
		if self.system == "DVB-S2":
			if self.pilot != "OFF":
				res.update(self.exportPilot())
		if self.rolloff != "0_35":
			res.update(self.exportRolloff())
		return res
	
	def exportAll(self):
		res = self.exportClean()
		res.update(self.exportImportColor())
		return res
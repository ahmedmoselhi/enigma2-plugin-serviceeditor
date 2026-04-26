import _thread
class Lamedb:
	def __init__(self):
		self.readcnt = 0
		self.database = {}
		self.databaseState=0
		_thread.start_new_thread(self._initDatabase,(None,))
#		self._initDatabase(None,)
		
	def _initDatabase(self,dummy):
		self.database.clear()
		self.databaseState=0
		print("phase1")
		self.translateTransponders(self.getTransponders(self.readLamedb()))
		print("phase2")
		self.translateServices(self.getServices(self.readLamedb()))
		print("phase3")

	def readLamedb(self):
		f = open("/etc/enigma2/lamedb","r")
		lamedb = f.readlines()
		f.close()
		if lamedb[0].find("/3/") != -1:
			self.version = 3
		elif lamedb[0].find("/4/") != -1:
			self.version = 4
		else:
			print("unbekante Version: ",lamedb[0])
			return
		print("import version %d" % self.version)
		return lamedb

	def writeLamedb(self,version = 4):
		if version != 4:
			print("only version 4 yet")
			return
		puffer = []
		puffer.append("eDVB services /4/\n")
		puffer.append("transponders\n")
		for tp_key in self.database:
			tp = self.database[tp_key]
			puffer.append(("%s:%s:%s\n")%(tp.get("namespace", "0"), tp.get("tsid", "0"), tp.get("onid", "0")))
			if tp.get("namespace", "0")[:4].lower()=="ffff":
				c_params = [
					tp.get("frequency", "0"), tp.get("symbol_rate", "0"), tp.get("inversion", "0"),
					tp.get("modulation", "0"), tp.get("fec_inner", "0"), tp.get("flags", "0")
				]
				c_params.extend(tp.get("extra_cable_params", []))
				puffer.append(("\tc %s\n") % ":".join(c_params))
			elif tp.get("namespace", "0")[:4].lower()=="eeee":
				t_params = [
					tp.get("frequency", "0"), tp.get("bandwidth", "0"), tp.get("code_rate_HP", "0"),
					tp.get("code_rate_LP", "0"), tp.get("modulation", "0"), tp.get("transmission_mode", "0"),
					tp.get("guard_interval", "0"), tp.get("hierarchy", "0"), tp.get("inversion", "0"), tp.get("flags", "0")
				]
				t_params.extend(tp.get("extra_terr_params", []))
				puffer.append(("\tt %s\n") % ":".join(t_params))
			else:
				s_params = [
					tp.get("frequency", "0"), tp.get("symbol_rate", "0"), tp.get("polarization", "0"), tp.get("fec_inner", "0"),
					tp.get("position", "0"), tp.get("inversion", "0"), tp.get("flags", "0")
				]
				if "system" in tp:
					s_params.extend([
						tp.get("system", "0"),
						tp.get("modulation", "1"),
						tp.get("rolloff", "0"),
						tp.get("pilot", "0"),
					])
				s_params.extend(tp.get("extra_sat_params", []))
				puffer.append(("\ts %s\n") % ":".join(s_params))
			puffer.append("/\n")	
		puffer.append("end\n")
		puffer.append("services\n")
		for tp_key in self.database:
			for service_key in self.database[tp_key].get("services", {}):
				service = self.database[tp_key]["services"][service_key]
				puffer.append(("%s:%s:%s:%s:%s:%s\n")%(service.get("sid", "0"), service.get("namespace", "0"), service.get("tsid", "0"), service.get("onid", "0"), service.get("type", "0"), service.get("number", "0")))
				puffer.append(("%s\n")%service.get("name", ""))
				tmp = ""
				cacheIDs = service.get("cacheIDs",None)
				if cacheIDs is not None:
					for cacheID in cacheIDs:
						tmp += ",c:" + cacheID
				caIDs = service.get("caIDs",None)
				if caIDs is not None:
					for caID in caIDs:
						tmp += ",C:" + caID
				flags = service.get("flags",None)
				if flags is not None and int(flags,16)!=0:
					tmp += ",f:" + flags
				extras = service.get("extras", None)
				if extras is not None:
					for extra in extras:
						tmp += "," + extra
				puffer.append(("p:%s%s\n")%(service.get("provider", ""),tmp))
		puffer.append("end\n")
		puffer.append("Have a lot of bugs!\n")
		f = open("/etc/enigma2/lamedb","w")
		f.writelines(puffer)
		f.close()
		
	def getServices(self, lamedb):
		print("getServices", end=' ')
		if lamedb is None:
			return []
		collect = False
		services = []
		x = 0
		while x < len(lamedb):
			line = lamedb[x]
			if line == "services\n":
				collect = True
				x += 1
				continue
			if line == "end\n":
				collect = False
				x += 1
				continue
			
			if collect and (x + 2) < len(lamedb):
				tmp = line.split(":")
				if len(tmp) >= 6:
					transponder_key = (tmp[1] + tmp[2] + tmp[3]).lower()
					if transponder_key in self.database:
						services.append((lamedb[x], lamedb[x+1], lamedb[x+2]))
				x += 3
			else:
				x += 1
		print(" fertig")
		return services
	
	
	def translateService(self, serviceData):
		t1 = ["sid","namespace","tsid","onid","type","number"]
		if serviceData is None:
			return
		service = {}
		tp_data = serviceData[0].strip().split(":")
		for y in range(min(len(t1), len(tp_data))):
			service.update({t1[y]:tp_data[y]})
		name = serviceData[1].strip('\n').replace('\xc2\x86', '').replace('\xc2\x87', '')
		service.update({"name":name})
		provider_data = serviceData[2].strip().split(",")
		for y in provider_data:
			raw = y.split(":", 1)
			if len(raw) != 2:
				continue
			if raw[0]=="p":
				service["provider"] = raw[1].replace('\xc2\x86', '').replace('\xc2\x87', '')
			elif raw[0]=="c":
				cacheIDs = service.get("cacheIDs",None)
				if cacheIDs is None:
					service["cacheIDs"] = [raw[1],]
				else:
					cacheIDs.append(raw[1])
			elif raw[0]=="C":
				caIDs = service.get("caIDs",None)
				if caIDs is None:
					service["caIDs"] = [raw[1],]
				else:
					caIDs.append(raw[1])
			elif raw[0]=="f":
				service["flags"] = raw[1]
			else:
				extras = service.get("extras", [])
				extras.append(y)
				service["extras"] = extras
				
		if "namespace" not in service or "tsid" not in service or "onid" not in service or "sid" not in service:
			return
			
		uniqueTransponder = (service["namespace"] + service["tsid"] + service["onid"]).lower()
		if uniqueTransponder not in self.database:
			return
			
		if (int(service.get("flags","0"),16) & dxNoDVB):
			tmp = ''
			for cacheID in service.get("cacheIDs",[]):
				tmp += cacheID
			uniqueService = uniqueTransponder + tmp
		else:
			uniqueService = uniqueTransponder + service["sid"]
		service["usk"] = uniqueService
		self.database[uniqueTransponder]["services"][uniqueService] = service
		self.readcnt += 1
		self.databaseState=3
	
	def translateServices(self, services):
		if services is None:
			return
		for x in services:
			self.translateService(x)
		self.databaseState=4
	

	def getTransponders(self, lamedb):
		if lamedb is None:
			return []
		collect = False
		transponders = []
		tp = []
		for x in lamedb:
			if x == "transponders\n":
				collect = True
				continue
			if x == "end\n":
				collect = False
				continue
			y = x.strip().split(":")
			if collect:
				if y[0] == "/":
					transponders.append(tp)
					tp = []
				else:
					tp.append(y)
		return transponders

	def translateTransponders(self, transponders):
		t1 = ["namespace","tsid","onid"]
		t2_sv3 = ["frequency",
			"symbol_rate",
			"polarization",
			"fec_inner",
			"position",
			"inversion",
			"system",
			"modulation",
			"rolloff",
			"pilot",
			]
		t2_sv4 = ["frequency",
			"symbol_rate",
			"polarization",
			"fec_inner",
			"position",
			"inversion",
			"flags",
			"system",
			"modulation",
			"rolloff",
			"pilot"
			]
		t2_t = ["frequency",
			"bandwidth",
			"code_rate_HP",
			"code_rate_LP",
			"modulation",
			"transmission_mode",
			"guard_interval",
			"hierarchy",
			"inversion",
			"flags",
			]
		t2_c = ["frequency",
			"symbol_rate",
			"inversion",
			"modulation",
			"fec_inner",
			"flags",
			]

		if transponders is None:
			return
		for x in transponders:
			if len(x[0]) > len(t1):
				print("zu viele Parameter (t1) in ",x[0])
				continue
			if len(x) < 2 or not x[1]:
				continue
			freq = x[1][0].split()
			if len(freq) != 2:
				print("zwei Parameter erwartet in ",freq)
				continue
			tp = {"services":{}}
			x[1][0] = freq[1]
			if freq[0] == "s" or freq[0] == "S":
				for y in range(len(x[0])):
					tp.update({t1[y]:x[0][y]})
				for y in range(min(len(x[1]), len(t2_sv4 if self.version == 4 else t2_sv3))):
					if self.version == 3:
						tp.update({t2_sv3[y]:x[1][y]})
					elif self.version == 4:
						tp.update({t2_sv4[y]:x[1][y]})
				if self.version == 4 and len(x[1]) > len(t2_sv4):
					tp["extra_sat_params"] = x[1][len(t2_sv4):]
					
				# Removed strict position check since e2 permits mismatches
				
				transponder_key = (tp.get("namespace", "") + tp.get("tsid", "") + tp.get("onid", "")).lower()
				if transponder_key:
					self.database[transponder_key] = tp
					self.databaseState=1
			elif freq[0] == "c" or freq[0] == "C":
				for y in range(len(x[0])):
					tp.update({t1[y]:x[0][y]})
				for y in range(min(len(x[1]), len(t2_c))):
					tp.update({t2_c[y]:x[1][y]})
				if len(x[1]) > len(t2_c):
					tp["extra_cable_params"] = x[1][len(t2_c):]
					
				transponder_key = (tp.get("namespace", "") + tp.get("tsid", "") + tp.get("onid", "")).lower()
				if transponder_key:
					self.database[transponder_key] = tp
					self.databaseState=1
			elif freq[0] == "t" or freq[0] == "T":
				for y in range(len(x[0])):
					tp.update({t1[y]:x[0][y]})
				for y in range(min(len(x[1]), len(t2_t))):
					tp.update({t2_t[y]:x[1][y]})
				if len(x[1]) > len(t2_t):
					tp["extra_terr_params"] = x[1][len(t2_t):]
					
				transponder_key = (tp.get("namespace", "") + tp.get("tsid", "") + tp.get("onid", "")).lower()
				if transponder_key:
					self.database[transponder_key] = tp
					self.databaseState=1
		self.databaseState=2

dxNoSDT=1    	# don't get SDT
dxDontshow=2
dxNoDVB=4		# dont use PMT for this service ( use cached pids )
dxHoldName=8
dxNewFound=64

#typ der cacheIDs
VIDEO_PID = 0
AUDIO_PID = 1		#wenn aPid, dann darf kein ac3Pid vorhanden sein
TXT_PID = 2
PCR_PID = 3
AC3_PID = 4		#wenn ac3Pid, dann darf kein aPid vorhanden sein
VIDEOTYPE = 5		# 0=MPEG2, 1=MPEG4_H264, 2=MPEG1, 3=MPEG4_Part2, 4=VC1, 5=VC1_SM
AUDIOCHANNEL = 6	#Audiochannel
AC3_DELAY = 7
PCM_DELAY = 8
SUBTITLE_PID = 9

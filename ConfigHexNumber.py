from Components.config import config, ConfigText, KEY_NUMBERS, KEY_ASCII, getKeyNumber
from enigma import getPrevAsciiCode
class ConfigHexNumber(ConfigText):
	def __init__(self, default = "0000", size= 4):
		try:
			dummy = int(default,16)
		except:
			default="0"*size
		ConfigText.__init__(self, default, fixed_size = False)
		self.mapping = []
		self.mapping.append ("0") # 0
		self.mapping.append ("1") # 1
		self.mapping.append ("2ABC") # 2
		self.mapping.append ("3DEF") # 3
		self.mapping.append ("4") # 4
		self.mapping.append ("5") # 5
		self.mapping.append ("6") # 6
		self.mapping.append ("7") # 7
		self.mapping.append ("8") # 8
		self.mapping.append ("9") # 9
		
		self.size = size
	
	def getValue(self):
		return self.text

	def setValue(self, val):
		self.text = val

	value = property(getValue, setValue)
	_value = property(getValue, setValue)

	def conform(self):
		print(self.text)
		self.text = self.text[-self.size:].zfill(self.size)
		print(self.text)
		if self.marked_pos >= self.size:
			self.marked_pos = self.size-1
		pos = len(self.text) - self.marked_pos
		print(pos)
		print(self.marked_pos)
		if pos > len(self.text):
			self.marked_pos = 0
		else:
			self.marked_pos = len(self.text) - pos

	def handleKey(self, key):
		if key in KEY_NUMBERS or key == KEY_ASCII:
			if key == KEY_ASCII:
				owr = False
				ascii_code = getPrevAsciiCode()
				if not ((48 <= ascii_code <= 57) or (65 <= ascii_code <= 70) or (97 <= ascii_code <= 102)):
					return
				newChar = chr(ascii_code)
			else:
				owr = self.lastKey == getKeyNumber(key)
				newChar = self.getKey(getKeyNumber(key))
			if self.allmarked:
				self.text = "0" * self.size
				self.allmarked = False
				self.marked_pos = 0
			self.insertChar(newChar, self.marked_pos, True)
		else:
			ConfigText.handleKey(self, key)
		self.conform()

	def onSelect(self, session):
		self.allmarked = (self.value != "")

	def onDeselect(self, session):
		self.marked_pos = 0
		self.offset = 0
		if not self.last_value == self.value:
			self.changedFinal()
			self.last_value = self.value

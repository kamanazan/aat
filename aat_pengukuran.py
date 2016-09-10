import glob
import os
import wx

import random
import time
import csv
import decimal


class ViewerPanel(wx.Panel):
	""""""
	def __init__(self, parent):
		"""Constructor"""
		wx.Panel.__init__(self, parent)

		self.widthDisp, self.heightDisp = wx.DisplaySize()
		width, height = wx.DisplaySize()
		# self.picPaths = []
		self.category = ''
		self.picPaths = glob.glob('images\*.jpg')
		self.currentImage = ''
		self.totalPictures = 0
		self.widthDisp, self.heightDisp = wx.DisplaySize()
		self.startTime = 0.0
		self.responseTime = 0.0
		self.firstResponse = 0.0
		self.score = []
		self.isWrong = ''
		self.photoMaxSize = height - 200
		self.layout()

	def layout(self):
		"""
			Layout the widgets on the panel
			"""

		self.mainSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)


		self.images = []

		img = wx.EmptyImage(self.photoMaxSize, self.photoMaxSize)
		self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY,
										 wx.BitmapFromImage(img))
		self.mainSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)

		self.SetSizer(self.mainSizer)

	def prepareImages(self):
		image_list = self.picPaths
		print "total image: ", len(image_list)

		image_list_happy = [img for img in image_list if img.count('Happy')] * 4
		image_list_neutral = [img for img in image_list if img.count('Neutral')] * 4
		image_list_angry = [img for img in image_list if img.count('Angry')] * 4
		img_g_happy = [face for face in image_list_happy if face.count('_G')]
		img_s_happy = [face for face in image_list_happy if face.count('_S')]

		img_g_neutral = [face for face in image_list_neutral if face.count('_G')]
		img_s_neutral = [face for face in image_list_neutral if face.count('_S')]
		img_g_angry = [face for face in image_list_angry if face.count('_G')]
		img_s_angry = [face for face in image_list_angry if face.count('_S')]

		population_g_happy = len(img_g_happy)
		population_s_happy = len(img_s_happy)
		population_g_neutral = len(img_g_neutral)
		population_s_neutral = len(img_s_neutral)
		population_g_angry = len(img_g_angry)
		population_s_angry = len(img_s_angry)

		# -----------------------------------------------------------------------------------------------

		image_g_happy_list = random.sample(img_g_happy, population_g_happy)
		image_s_happy_list = random.sample(img_s_happy, population_s_happy)
		image_g_neutral_list = random.sample(img_g_neutral, population_g_neutral)
		image_s_neutral_list = random.sample(img_s_neutral, population_s_neutral)
		image_g_angry_list = random.sample(img_g_angry, population_g_angry)
		image_s_angry_list = random.sample(img_s_angry, population_s_angry)

		image_used = list(
			image_g_happy_list + image_s_happy_list + image_g_neutral_list + image_s_neutral_list + image_g_angry_list + image_s_angry_list)
		# image_bw_list.extend(image_sp_list)
		random.shuffle(image_used)
		# image_used = image_bw_list
		self.images = image_used  # tsting only

	def setResponden(self, responden_data):
		self.category = 'NO'
		self.score.append(responden_data)
		self.score.append(['TGL', 'RAS', 'GENDER', 'EKSPRESI', 'WARNA', 'RESPON AWAL', 'RESPON AKHIR', 'KET'])

	def getRandomImage(self):
		return self.images.pop(self.images.index(random.choice(self.images)))

	def shouldStop(self):
		return len(self.images) == 0

	def loadImage(self, action):
		""""""
		image = self.currentImage
		image_name = os.path.basename(image)
		img = wx.Image(image, wx.BITMAP_TYPE_ANY)

		width = img.GetWidth()
		height = img.GetHeight()

		if self.heightDisp > height:
			scale = self.heightDisp / float(height)
		else:
			scale = height / float(self.heightDisp)
		NewW = 400
		NewH = 400
		if action is not None:
			if action == 'PUSH':
				print 'PUSH!'
				if image_name.count('_G'):
					self.isWrong = 'SALAH'
				NewW = 20
				NewH = 20
			elif action == 'PULL':
				print 'PULL!'
				if image_name.count('_S'):
					self.isWrong = 'SALAH'
				NewW = self.heightDisp
				NewH = self.heightDisp

			self.calculateResponse(image_name)

			self.startTime = 0.0
		else:
			self.startTime = time.time()
			self.isWrong = ''

		img = img.Scale(NewW, NewH)
		self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
		self.mainSizer.Remove(0)
		self.mainSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
		self.Layout()
		self.Refresh()

	def setCurrentImage(self, image):
		self.currentImage = image

	def calculateResponse(self, img):

		info = img.split('.')[0]
		race, gender, expr, color = info.split('_')
		response = (time.time() - self.startTime) * 1000
		date = time.strftime(" %d/%m/%Y %H:%M:%S", time.localtime())
		score_set = [date, race, gender, expr, color, self.firstResponse, response, self.isWrong]
		self.score.append(score_set)


	def calculateFirstResponse(self):
		self.firstResponse = (time.time() - self.startTime) * 1000

	def resetFirstResponse(self):
		self.firstResponse = 0.0

	def getScore(self):
		return self.score

	def clearScore(self):
		self.score = []


class FormLatihan(wx.Panel):
	""""""

	def __init__(self, parent):
		"""Constructor"""
		wx.Panel.__init__(self, parent)

		self.widthDisp, self.heightDisp = wx.DisplaySize()

		self.category = ''
		print "frame size:", self.widthDisp, self.heightDisp

		self.img_latih_g_salah = 'images\Latihan_G_salah.jpeg'
		self.img_latih_s_salah = 'images\Latihan_S_salah.jpeg'
		self.img_latih_g = 'images\Latihan_G.jpeg'
		self.img_latih_s = 'images\Latihan_S.jpeg'
		self.images = []
		self.currentImage = self.img_latih_g

		self.totalPictures = 0

		self.startTime = 0.0
		self.responseTime = 0.0
		self.score = []
		self.isWrong = ''
		self.layout()

	def layout(self):
		"""
			Layout the widgets on the panel
			"""
		self.imgSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)


		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		image = self.currentImage
		image_name = os.path.basename(image)
		img = wx.Image(image, wx.BITMAP_TYPE_ANY)

		self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img))
		self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)

		self.imgSizer.Fit(self)
		self.SetSizer(self.imgSizer)

	def prepareImages(self):
		self.images = [self.img_latih_g, self.img_latih_s] * 6
		self.images = random.sample(self.images,12)
		self.images.append(self.img_latih_g)
		# self.currentImage = self.images.pop(self.images.index(random.choice(self.images)))
		self.currentImage = self.images.pop(0)

	def loadImage(self, action):
		""""""
		image = self.currentImage
		image_name = os.path.basename(image)
		img = wx.Image(image, wx.BITMAP_TYPE_ANY)

		width = img.GetWidth()
		height = img.GetHeight()

		if self.heightDisp > height:
			scale = self.heightDisp / float(height)
		else:
			scale = height / float(self.heightDisp)

		NewW = 400
		NewH = 400
		if action is not None:

			if action == 'PUSH':
				print 'PUSH!'
				if image_name.count('_G'):
					image = self.img_latih_g_salah
					# image = self.currentImage
					image_name = os.path.basename(image)
					img = wx.Image(image, wx.BITMAP_TYPE_ANY)

				else:
					self.textLabel = 'TARIK'

					# self.currentImage = self.img_latih_g
					NewW = 20
					NewH = 20
					self.currentImage = self.images.pop(0)
			elif action == 'PULL':
				print 'PULL!'
				if image_name.count('_S'):
					image = self.img_latih_s_salah
					# image = self.currentImage
					image_name = os.path.basename(image)
					img = wx.Image(image, wx.BITMAP_TYPE_ANY)
				else:
					self.textLabel = 'DORONG'
					# self.currentImage = self.img_latih_s
					NewW = self.heightDisp
					NewH = self.heightDisp
					self.currentImage = self.images.pop(0)

		img = img.Scale(NewW, NewH)
		self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
		self.imgSizer.Remove(0)
		self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
		self.Layout()
		self.Refresh()

	def shouldStop(self):
		return len(self.images) == 0


class FormIdentitas(wx.Panel):

	def __init__(self, parent):
		# Add a panel so it looks correct on all platforms
		wx.Panel.__init__(self, parent)
		title = wx.StaticText(self, wx.ID_ANY, 'Masukan identitas')
		lblSize = (50, -1)

		labelOne = wx.StaticText(self, wx.ID_ANY, 'ID')
		inputTxtOne = wx.TextCtrl(self, wx.ID_ANY, '')

		labelTwo = wx.StaticText(self, wx.ID_ANY, 'Nama')
		inputTxtTwo = wx.TextCtrl(self, wx.ID_ANY, '')

		labelThree = wx.StaticText(self, wx.ID_ANY, 'Gender')

		genderChoices = ['L', 'P']
		inputTxtThree = wx.Choice(self, wx.ID_ANY, choices=genderChoices)

		self.txt1 = inputTxtOne
		self.txt2 = inputTxtTwo
		self.genchoice = inputTxtThree

		topSizer = wx.BoxSizer(wx.VERTICAL)
		titleSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
		inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
		inputTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
		inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)

		titleSizer.Add(title, 0, wx.ALIGN_CENTER, 5)

		inputOneSizer.Add((20, 20), proportion=1)  # this is a spacer
		inputOneSizer.Add(labelOne, 0, wx.ALL | wx.ALIGN_LEFT, 2)

		inputTwoSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
		inputTwoSizer.Add(labelTwo, 0, wx.ALL | wx.ALIGN_LEFT, 2)

		inputThreeSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
		inputThreeSizer.Add(labelThree, 0, wx.ALL | wx.ALIGN_LEFT, 2)

		# Add the 3-item sizer to the gridsizer and
		gridSizer.Add(inputOneSizer, 0, wx.ALIGN_LEFT)
		# Set the TextCtrl to expand on resize
		gridSizer.Add(inputTxtOne, 0, wx.ALIGN_LEFT | wx.EXPAND)
		gridSizer.Add(inputTwoSizer, 0, wx.ALIGN_LEFT)
		gridSizer.Add(inputTxtTwo, 0, wx.ALIGN_LEFT | wx.EXPAND)
		gridSizer.Add(inputThreeSizer, 0, wx.ALIGN_LEFT)
		gridSizer.Add(inputTxtThree, 0, wx.ALIGN_LEFT)

		self.pesan = 'Gerakan Joystick ke kanan untuk melanjutkan'
		self.title = wx.StaticText(self, wx.ID_ANY, label=self.pesan, style=wx.ALIGN_CENTER)
		font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.title.SetFont(font)
		topSizer.Add(titleSizer, 0, wx.ALIGN_CENTER)
		topSizer.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)
		topSizer.Add(gridSizer, 0, wx.ALIGN_CENTER | wx.EXPAND, 5)
		topSizer.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)
		topSizer.Add(self.title, 0, wx.ALIGN_CENTER, 5)  #topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
		self.SetSizer(topSizer)
		topSizer.Fit(self)

	def getValues(self):
		nama = str(self.txt2.GetValue())
		idresponden = str(self.txt1.GetValue())
		gender = str(self.genchoice.GetStringSelection())
		responden_data = ['IDENTITAS:', idresponden, nama, gender]

		return responden_data

	def onCancel(self, event):
		self.closeProgram()


	def closeProgram(self):
		self.Close()


class FormJeda(wx.Panel):

	def __init__(self, parent):
		# Add a panel so it looks correct on all platforms
		wx.Panel.__init__(self, parent)

		self.pesan = 'PESAN SPONSOR'
		self.title = wx.StaticText(self, wx.ID_ANY, label=self.pesan, style=wx.ALIGN_CENTER)
		font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.title.SetFont(font)

		titleSizer = wx.GridSizer(rows=1, cols=1)

		titleSizer.Add(self.title, 0, wx.ALIGN_CENTER, 0)

		self.SetSizer(titleSizer)
		titleSizer.Fit(self)
		self.Layout()
		self.Refresh()

	def WritePesan(self, msg):
		self.title.SetLabel(msg)


class ViewerFrame(wx.Frame):
	""""""
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, wx.ID_ANY, title="Image Viewer")
		self.formViewer = FormIdentitas(self)
		self.mainViewer = ViewerPanel(self)
		self.sesiJeda = FormJeda(self)
		self.sesiLatihan = FormLatihan(self)

		self.sesiLatihan.Hide()
		self.sesiJeda.Hide()
		self.mainViewer.Hide()
		self.formViewer.Show()

		self.folderPath = ""
		self.wait = True
		self.latihan = True
		self.jenisJeda = 'INS1'  #[INS1|INS2|OPN|REST|END]
		self.jumlahLatihan = 1
		self.lockPanel = False
		self.txtINS1 = "Kepada anda akan disajikan\nFoto-foto berwarna HITAM PUTIH dan SEPHIA\n\n\n\nTugas Anda adalah\nMENARIK joystick untuk foto HITAM PUTIH\nMENDORONG Joystick untuk foto SEPHIA\n\n\nPada saat MENARIK, foto akan membesar\nPada saat MENDORONG, foto akan mengecil\nAnda diminta untuk MENARIK/MENDORONG joystick hingga maksimal\n(Tidak dapat bergerak lagi)\n\n\nSetelah itu Anda diminta untuk mengembalikan joystick ke posisi tengah kembali dan\nfoto baru akan ditampilkan\n\n\n\nGeser joystick ke kanan untuk memulai"

		self.txtINS2 = 'Berikut ini adalah sesi latihan\n\n\n\nKepada Anda akan disajikan foto pemandangan berwarna HITAM PUTIH dan SEPHIA\n\n\nTARIK joystick mendekati tubuh jika yang tersaji adalah foto berwarna HITAM PUTIH\nDORONG joystick menjauhi tubuh jika yang tersaji adalah foto berwarna SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan \nMENGEMBALIKAN joystick ke posisi tengah untuk melihat foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'

		self.txtOPN = 'Berikut ini adalah sesi program\n\n\n\nTARIK joystick untuk gambar HITAM PUTIH\nDORONG joystick untuk gambar SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan\nMENGEMBALIKAN joystick ke posisi tengah untuk melihat foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'

		self.txtREST = 'SESI 1 telah berakhir\n\n\nSilahkan tunggu instruksi selanjutnya'

		self.txtEND = 'Sesi program telah selesai\n\n\nTerima kasih atas partisipasi anda'

		self.dec = decimal.Decimal
		self.ONEPLACE = self.dec(10) ** -1

		self.sesiJeda.WritePesan(self.txtINS1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.formViewer, 1, wx.EXPAND)
		self.sizer.Add(self.mainViewer, 1, wx.EXPAND)
		self.sizer.Add(self.sesiJeda, 1, wx.EXPAND)
		self.sizer.Add(self.sesiLatihan, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

		self.Show()
		self.sizer.Fit(self)

		self.ShowFullScreen(True)
		self.joystick = wx.Joystick()
		self.joystick.SetCapture(self)
		self.Bind(wx.EVT_JOY_MOVE, self.onMove)
		self.JOY_DO_SOMETHING = True
#----------------------------------------------------------------------
	def onMove(self, event):
		# Rules:
		# 1. one panel only use one axis
		# 2. whenever axis is moved make sure JOY_DO_SOMETHING is set to False
		# 3. whenever axis returns idle make sure JOY_DO_SOMETHING is set to True

		# Normalize position in linux
		# posx = (float(x)-32767.0)/32767.0
		# posy = (float(y)-32767.0)/32767.0
		pos = self.joystick.GetPosition()
		x, y = pos
		posx = self.dec((x - 32767) * 2 / 65535.).quantize(self.ONEPLACE)
		posy = self.dec(-(y - 32767) * 2 / 65535.).quantize(self.ONEPLACE)

		print "posx,posy: ", posx, posy
		if self.formViewer.IsShown():
			if self.lockPanel:
				# if abs(posx) <= 0.0001:
				if abs(posx) == 0.0:
					self.JOY_DO_SOMETHING = True
					self.lockPanel = False
				else:
					pass
			else:
				if posx >= 0.9:
					self.JOY_DO_SOMETHING = False
					self.onSwitchPanels('jeda')
		elif self.sesiLatihan.IsShown():
			if self.lockPanel:
				# if abs(posx) <= 0.0001:
				if abs(posx) == 0.0:
					self.JOY_DO_SOMETHING = True
					self.lockPanel = False
					print 'stat:', self.JOY_DO_SOMETHING, self.lockPanel, posx, posy
				else:
					pass
			else:
				if posy >= .9 and self.JOY_DO_SOMETHING:
					self.sesiLatihan.loadImage('PUSH')
					print "posx,posy: ", posx, posy
					self.JOY_DO_SOMETHING = False
				elif posy <= -.9 and self.JOY_DO_SOMETHING:
					self.sesiLatihan.loadImage('PULL')
					print "posx,posy: ", posx, posy
					self.JOY_DO_SOMETHING = False
				elif (abs(posy) == 0.0 ) and not self.JOY_DO_SOMETHING:
					print 'NEXT!'
					print "posx,posy: ", posx, posy
					if self.sesiLatihan.shouldStop():
						self.sesiJeda.WritePesan(self.txtOPN)
						self.jenisJeda = 'OPN'
						self.onSwitchPanels('jeda')

					else:
						self.sesiLatihan.loadImage(None)
					self.JOY_DO_SOMETHING = True
				else:
					pass
		elif self.mainViewer.IsShown():
			if self.lockPanel:
				if abs(posx) == 0.0:
					self.JOY_DO_SOMETHING = True
					self.lockPanel = False
					print 'stat:', self.JOY_DO_SOMETHING, self.lockPanel, posx, posy
				else:
					pass
			else:
				if posy >= .89 and self.JOY_DO_SOMETHING:
					self.mainViewer.loadImage('PUSH')
					print "posx,posy: ", posx, posy
					self.JOY_DO_SOMETHING = False
				elif posy <= -.89 and self.JOY_DO_SOMETHING:
					self.mainViewer.loadImage('PULL')
					print "posx,posy: ", posx, posy
					self.JOY_DO_SOMETHING = False
				elif abs(posy) > .3 and self.JOY_DO_SOMETHING:
					self.mainViewer.calculateFirstResponse()
				elif (abs(posy) == 0.0 ) and not self.JOY_DO_SOMETHING:
					self.JOY_DO_SOMETHING = True
					if not self.mainViewer.shouldStop():
						print 'NEXT!'
						print "posx,posy: ", posx, posy
						self.mainViewer.resetFirstResponse()
						self.mainViewer.setCurrentImage(self.mainViewer.getRandomImage())
						self.mainViewer.loadImage(None)
					elif self.mainViewer.shouldStop():
						print 'STOP!'
						print "posx,posy: ", posx, posy
						self.mainViewer.resetFirstResponse()
						self.writeScore(self.mainViewer.getScore())
						self.mainViewer.clearScore()
						self.sesiJeda.WritePesan(self.txtEND)
						self.onSwitchPanels('jeda')
						self.jenisJeda = 'END'
				else:
					pass
		elif self.sesiJeda.IsShown():
			print self.jenisJeda
			if posx >= 0.9 and self.JOY_DO_SOMETHING:
				self.JOY_DO_SOMETHING = False
				self.lockPanel = True
				if self.jenisJeda == 'INS1':
					self.sesiJeda.WritePesan(self.txtINS2)
					self.onSwitchPanels('jeda')
					self.jenisJeda = 'INS2'
				elif self.jenisJeda == 'INS2':

					self.onSwitchPanels('latihan')
					self.sesiLatihan.prepareImages()
					self.sesiLatihan.loadImage(None)
				elif self.jenisJeda == 'OPN':
					self.onSwitchPanels('main')
					data_responden = self.formViewer.getValues()
					#responden.append('SESI 2')
					self.mainViewer.setResponden(data_responden)
					self.mainViewer.prepareImages()
					self.mainViewer.setCurrentImage(self.mainViewer.getRandomImage())
					self.mainViewer.loadImage(None)
				elif self.jenisJeda == 'REST':
					self.jenisJeda = 'OPN'
					self.sesiJeda.WritePesan(self.txtOPN)
					self.onSwitchPanels('jeda')
				elif self.jenisJeda == 'END':
					self.jenisJeda = 'INS1'
					self.sesiJeda.WritePesan(self.txtINS1)
					self.onSwitchPanels('menu')
					self.wait = True

			elif abs(posx) == 0.0 and not self.JOY_DO_SOMETHING:
				self.JOY_DO_SOMETHING = True
			else:
				pass

	def writeScore(self, data):
		if not os.path.exists('hasil'):
			os.makedirs('hasil')
		if len(data):
			file_name = 'hasil/' + '_'.join(data[0][1:]) + '.csv'  #nama_id.csv
			valid_data = [x for x in data[2:] if x[7] == '' or x[6] > 200]
			total_response = sum([x[6] for x in valid_data])
			if len(valid_data):
				avg = float(total_response) / float(len(valid_data))
			else:
				avg = 0.0
			data.append(['RERATA:', avg])
			with open(file_name, 'ab') as csvfile:
				scorewriter = csv.writer(csvfile)
				scorewriter.writerows(data[0:])
		else:
			pass

	def onSwitchPanels(self, window):
		""""""
		if window == 'main':
			self.formViewer.Hide()
			self.sesiLatihan.Hide()
			self.sesiJeda.Hide()
			self.mainViewer.Show()
		elif window == 'jeda':
			self.mainViewer.Hide()
			self.formViewer.Hide()
			self.sesiLatihan.Hide()
			self.sesiJeda.Show()
		elif window == 'latihan':
			self.sesiJeda.Hide()
			self.sesiLatihan.Show()
			self.formViewer.Hide()
			self.mainViewer.Hide()
		elif window == 'menu':
			self.sesiJeda.Hide()
			self.sesiLatihan.Hide()
			self.mainViewer.Hide()
			self.formViewer.Show()
		else:
			self.sesiJeda.Show()
			self.sesiJeda.Hide()
			self.formViewer.Hide()
			self.mainViewer.Hide()
			self.sesiLatihan.Hide()
			self.wait = True
		self.Update()
		self.Layout()
		self.Refresh()

if __name__ == "__main__":
	app = wx.App()
	frame = ViewerFrame()
	app.MainLoop()

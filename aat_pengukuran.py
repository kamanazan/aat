import glob
import os
import wx

import random
import time
import csv
import decimal

class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.widthDisp, self.heightDisp = wx.DisplaySize()
        self.image_name = ''
        self.currentImage = ''
        self.images = []
        self.totalPictures = 0
        self.isWrong = False
        self.picPaths = glob.glob('images\*.jpg')
        self.layout()

    def wrong_action(self, warna=None):
        pass

    def prepareImages(self):
        pass

    def setCurrentImage(self, image):
        self.currentImage = image
        print "img left:", len(self.images)

    def getRandomImage(self):
        return self.images.pop(self.images.index(random.choice(self.images))) if self.images else None

    def shouldStop(self):
        return len(self.images) == 0

    def layout(self):
        """
        Layout the widgets on the panel
        """
        self.img = wx.EmptyImage(1,1)
        self.imgSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.img))
        self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        self.imgSizer.Fit(self)
        self.SetSizer(self.imgSizer)

    def loadImage(self, action, scale):
        """
        action: 'PUSH' or 'PULL', determine whether the image should be zoomed out/zoomed in
        scale: current y-axis of the joystick, this is used for smoother scaling
        """
        image = self.currentImage
        self.image_name = os.path.basename(image)
        self.img = wx.Image(image, wx.BITMAP_TYPE_ANY)
        width = 400
        height = 400

        if action is not None:
            if action == 'PUSH':
                # the final size is 1x1 pixels to make the image "disappear"
                target_size = 399
                print 'PUSH!'
                if self.image_name.count('_G'):
                    self.wrong_action(warna='G')
                else:
                    self.wrong_action()
                width = 400 - (target_size * scale)
                height = 400 - (target_size * scale)
            elif action == 'PULL':
                target_size = self.heightDisp - 400
                print 'PULL!'
                if self.image_name.count('_S'):
                    self.wrong_action(warna='S')
                else:
                    self.wrong_action()
                width = 400 + (target_size * scale)
                height = 400 + (target_size * scale)
            elif action == 'TESTPUSH':
                # the final size is 1x1 pixels to make the image "disappear"
                target_size = 399
                print 'TESTPUSH!'
                if self.image_name.count('_G'):
                    self.wrong_action(warna='G')
                else:
                    self.wrong_action()
                    width = 400 - (target_size * scale)
                    height = 400 - (target_size * scale)
            elif action == 'TESTPULL':
                target_size = self.heightDisp - 400
                print 'TESTPULL!'
                if self.image_name.count('_S'):
                    self.wrong_action(warna='S')
                else:
                    self.wrong_action()
                    width = 400 + (target_size * scale)
                    height = 400 + (target_size * scale)

        print 'new size: ', int(width), int(height)
        self.img = self.img.Scale(int(width), int(height))
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(self.img))
        self.imgSizer.Remove(0)
        self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        self.Update()
        self.Layout()
        self.Refresh()


class FormPenilaian(ImagePanel):
    """"""
    def __init__(self, parent):
        """Constructor"""
        super(FormPenilaian, self).__init__(parent)
        self.category = ''
        self.firstResponse = 0.0
        self.startTime = time.time()
        self.score = []
        self.DONE = False
        self.wrongImages = []

    def wrong_action(self, warna=None):
        if warna:
            self.isWrong = True
        else:
            self.isWrong = False

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
        self.images = image_used

    def setResponden(self, responden_data):
        self.category = 'NO'
        self.score.append(responden_data)
        self.score.append(['TGL', 'RAS', 'GENDER', 'EKSPRESI', 'WARNA', 'RESPON AWAL', 'RESPON AKHIR', 'KET'])

    def calculateResponse(self):
        info = self.image_name.split('.')[0]
        race, gender, expr, color = info.split('_')
        response = (time.time() - self.startTime) * 1000
        print 'RESPON AKHIR:', response
        date = time.strftime(" %d/%m/%Y %H:%M:%S", time.localtime())
        score_set = [date, race, gender, expr, color, self.firstResponse, response, 'SALAH' if self.isWrong else '']
        self.score.append(score_set)
        self.DONE = True

    def calculateFirstResponse(self):
        self.firstResponse = (time.time() - self.startTime) * 1000
        print 'RESPON AWAL: ', self.firstResponse

    def resetFirstResponse(self):
        self.firstResponse = 0.0
        self.DONE = False

    def getScore(self):
        return self.score

    def clearScore(self):
        self.score = []


class FormLatihan(ImagePanel):
    """"""

    def __init__(self, parent):
        """Constructor"""
        super(FormLatihan, self).__init__(parent)
        self.img_latih_g_salah = 'images\Latihan_G_salah.jpeg'
        self.img_latih_s_salah = 'images\Latihan_S_salah.jpeg'
        self.img_latih_g = 'images\Latihan_G.jpeg'
        self.img_latih_s = 'images\Latihan_S.jpeg'
        self.currentImage = self.img_latih_g
        self.layout()

    def wrong_action(self, warna=None):
        if warna == 'G':
            image = self.img_latih_g_salah
        elif warna == 'S':
            image = self.img_latih_s_salah
        else:
            self.isWrong = False
        if warna:
            self.img = wx.Image(image, wx.BITMAP_TYPE_ANY)
            self.isWrong = True

    def prepareImages(self):
        self.images = [self.img_latih_g, self.img_latih_s] * 6
        self.images = random.sample(self.images,12)
        self.images.append(self.img_latih_g)
        # self.currentImage = self.images.pop(self.images.index(random.choice(self.images)))
        self.currentImage = self.images.pop(0)


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

        self.idresponden = inputTxtOne
        self.nama = inputTxtTwo
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
        nama = str(self.nama.GetValue())
        idresponden = str(self.idresponden.GetValue())
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
        self.formIdentitas = FormIdentitas(self)
        self.sesiPenilaian = FormPenilaian(self)
        self.sesiJeda = FormJeda(self)
        self.sesiLatihan = FormLatihan(self)

        self.sesiLatihan.Hide()
        self.sesiJeda.Hide()
        self.sesiPenilaian.Hide()
        self.formIdentitas.Show()

        self.folderPath = ""
        self.wait = True
        self.latihan = True
        self.jenisJeda = 'INS1'  #[INS1|INS2|OPN|REST|END]
        self.jumlahLatihan = 1
        self.LOCK_PANEL = False
        self.txtINS1 = "Kepada anda akan disajikan\nFoto-foto berwarna HITAM PUTIH dan SEPHIA\n\n\n\nTugas Anda adalah\nMENARIK joystick untuk foto HITAM PUTIH\nMENDORONG Joystick untuk foto SEPHIA\n\n\nPada saat MENARIK, foto akan membesar\nPada saat MENDORONG, foto akan mengecil\nAnda diminta untuk MENARIK/MENDORONG joystick hingga maksimal\n(Tidak dapat bergerak lagi)\n\n\nSetelah itu Anda diminta untuk mengembalikan joystick ke posisi tengah kembali dan\nfoto baru akan ditampilkan\n\n\n\nGeser joystick ke kanan untuk memulai"

        self.txtINS2 = 'Berikut ini adalah sesi latihan\n\n\n\nKepada Anda akan disajikan foto pemandangan berwarna HITAM PUTIH dan SEPHIA\n\n\nTARIK joystick mendekati tubuh jika yang tersaji adalah foto berwarna HITAM PUTIH\nDORONG joystick menjauhi tubuh jika yang tersaji adalah foto berwarna SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan \nMENGEMBALIKAN joystick ke posisi tengah untuk melihat foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'

        self.txtOPN = 'Berikut ini adalah sesi program\n\n\n\nTARIK joystick untuk gambar HITAM PUTIH\nDORONG joystick untuk gambar SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan\nMENGEMBALIKAN joystick ke posisi tengah untuk melihat foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'

        self.txtREST = 'SESI 1 telah berakhir\n\n\nSilahkan tunggu instruksi selanjutnya'

        self.txtEND = 'Sesi program telah selesai\n\n\nTerima kasih atas partisipasi anda'

        self.dec = decimal.Decimal
        self.ONEPLACE = self.dec(10) ** -1

        self.sesiJeda.WritePesan(self.txtINS1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formIdentitas, 1, wx.EXPAND)
        self.sizer.Add(self.sesiPenilaian, 1, wx.EXPAND)
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
        self.NEUTRAL = True

    def onMove(self, event):
        # Rules:
        # 1. one panel only use one axis(LOCK_PANEL) this will prevent user to accidentally change session
        # 2. whenever axis reach maximum position make sure JOY_DO_SOMETHING is set to False
        # 3. whenever axis returns idle make sure JOY_DO_SOMETHING is set to True

        # Normalize position in linux
        # posx = (float(x)-32767.0)/32767.0
        # posy = (float(y)-32767.0)/32767.0
        pos = self.joystick.GetPosition()
        x, y = pos
        posx = self.dec((x - 32767) * 2 / 65535.).quantize(self.dec('0.01'), rounding='ROUND_HALF_UP')
        posy = self.dec(-(y - 32767) * 2 / 65535.).quantize(self.dec('0.01'), rounding='ROUND_HALF_UP')
        # the value considered as 'neutral'(center position).
        # this cannot be exactly 0.0 as the x/y axis rarely have that value in neutral position
        neutral = 0.2
        full = 0.9
        print "pos:",posx, posy, x, y

        if self.formIdentitas.IsShown():
            if self.LOCK_PANEL:
                # if abs(posx) <= 0.0001:
                if posx <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                else:
                    pass
            else:
                if posx >= full:
                    data = self.formIdentitas.getValues()
                    if all(not x for x in data[1:]):
                        self.formIdentitas.title.SetLabel('DATA TIDAK LENGKAP')
                    else:
                        self.JOY_DO_SOMETHING = False
                        self.onSwitchPanels('jeda')
        elif self.sesiLatihan.IsShown():
            if self.LOCK_PANEL:
                # if abs(posx) <= 0.0001:
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                    # print 'stut:', self.JOY_DO_SOMETHING, self.LOCK_PANEL, posx, posy
                else:
                    pass
            else:
                if posy > neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy >= full else True
                    scale = abs(posy)
                    if posy >= full:
                        scale = 1.0
                    self.sesiLatihan.loadImage('TESTPUSH', scale)
                    print "posx,posy: ", posx, posy
                elif posy < -neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy <= -full else True
                    scale = abs(posy)
                    if posy <= -full:
                        scale = 1.0
                    self.sesiLatihan.loadImage('TESTPULL', scale)
                    print "posx,posy: ", posx, posy
                elif (abs(posy) <= neutral ) and self.JOY_DO_SOMETHING:
                    # When joystick return to normal position before fully push/pull return image to original size
                    self.sesiLatihan.loadImage(None, 0)
                elif (abs(posy) <= neutral ) and not self.JOY_DO_SOMETHING:
                    print 'NEXT!'
                    print "posx,posy: ", posx, posy
                    self.JOY_DO_SOMETHING = True
                    if self.sesiLatihan.shouldStop() and not self.sesiLatihan.isWrong:
                        self.sesiJeda.WritePesan(self.txtOPN)
                        self.jenisJeda = 'OPN'
                        self.onSwitchPanels('jeda')
                    else:
                        if not self.sesiLatihan.isWrong:
                            self.sesiLatihan.setCurrentImage(self.sesiLatihan.getRandomImage())
                        self.sesiLatihan.loadImage(None,0)
                else:
                    pass
        elif self.sesiPenilaian.IsShown():
            if self.LOCK_PANEL:
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                    # print 'stat:', self.JOY_DO_SOMETHING, self.LOCK_PANEL, posx, posy
                else:
                    pass
            else:
                # Joystick moves and image is zoomed in/out
                if abs(posy) > neutral and self.NEUTRAL:
                    self.NEUTRAL = False
                    self.sesiPenilaian.calculateFirstResponse()
                if posy > neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy >= full else True
                    scale = abs(posy)
                    if posy >= full:
                        self.sesiPenilaian.calculateResponse()
                        scale = 1.0
                    assert not self.NEUTRAL
                    self.sesiPenilaian.loadImage('PUSH', scale)
                    # print "posx,posy: ", posx, posy
                elif posy < -neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy <= -full else True
                    scale = abs(posy)
                    if posy <= -full:
                        self.sesiPenilaian.calculateResponse()
                        scale = 1.0
                    assert not self.NEUTRAL
                    self.sesiPenilaian.loadImage('PULL', scale)
                    # print "posx,posy: ", posx, posy
                elif (abs(posy) <= neutral ) and self.JOY_DO_SOMETHING:
                    # When joystick return to normal position before fully push/pull return image to original size
                    self.sesiPenilaian.loadImage(None, 0)
                elif (abs(posy) <= neutral ) and not self.JOY_DO_SOMETHING:
                    self.NEUTRAL = True
                    self.JOY_DO_SOMETHING = True
                    if not self.sesiPenilaian.shouldStop():
                        print 'NEXT!', posx, posy, abs(posy)
                        if self.sesiPenilaian.isWrong:
                            self.sesiPenilaian.wrongImages.append(self.sesiPenilaian.currentImage)
                        self.sesiPenilaian.resetFirstResponse()
                        self.sesiPenilaian.setCurrentImage(self.sesiPenilaian.getRandomImage())
                        self.sesiPenilaian.loadImage(None, 0)
                        self.sesiPenilaian.startTime = time.time()
                    elif self.sesiPenilaian.shouldStop():
                        self.sesiPenilaian.resetFirstResponse()
                        jumlah_salah = len(self.sesiPenilaian.wrongImages)
                        if jumlah_salah > 10:
                            print '===============REMEDIAL==============='
                            print 'Jumlah Salah:', jumlah_salah
                            self.sesiPenilaian.images.extend(self.sesiPenilaian.wrongImages)
                            self.sesiPenilaian.wrongImages = []
                            self.sesiPenilaian.setCurrentImage(self.sesiPenilaian.getRandomImage())
                            self.sesiPenilaian.loadImage(None, 0)
                            self.sesiPenilaian.startTime = time.time()
                        else:
                            self.writeScore(self.sesiPenilaian.getScore())
                            self.sesiPenilaian.clearScore()
                            self.sesiPenilaian.wrongImages = []
                            print "scoreIsClear:", len(self.sesiPenilaian.getScore()) == 0
                            self.sesiJeda.WritePesan(self.txtEND)
                            self.onSwitchPanels('jeda')
                            self.jenisJeda = 'END'
                else:
                    pass
        elif self.sesiJeda.IsShown():
            print self.jenisJeda
            if posx >= full and self.JOY_DO_SOMETHING:
                self.JOY_DO_SOMETHING = False
                self.LOCK_PANEL = True
                print "STAT:", self.jenisJeda
                print "==========="
                print "do something? ", self.JOY_DO_SOMETHING
                print "panel locked? ", self.LOCK_PANEL
                print "wait? ", self.wait
                if self.jenisJeda == 'INS1':
                    self.sesiJeda.WritePesan(self.txtINS2)
                    self.onSwitchPanels('jeda')
                    self.jenisJeda = 'INS2'
                elif self.jenisJeda == 'INS2':
                    self.onSwitchPanels('latihan')
                    self.sesiLatihan.prepareImages()
                    self.sesiLatihan.setCurrentImage(self.sesiLatihan.getRandomImage())
                    self.sesiLatihan.loadImage(None,0)
                elif self.jenisJeda == 'OPN':
                    self.onSwitchPanels('main')
                    data_responden = self.formIdentitas.getValues()
                    #responden.append('SESI 2')
                    self.sesiPenilaian.setResponden(data_responden)
                    self.sesiPenilaian.prepareImages()
                    self.sesiPenilaian.setCurrentImage(self.sesiPenilaian.getRandomImage())
                    self.sesiPenilaian.loadImage(None, 0)
                elif self.jenisJeda == 'REST':
                    self.jenisJeda = 'OPN'
                    self.sesiJeda.WritePesan(self.txtOPN)
                    self.onSwitchPanels('jeda')
                elif self.jenisJeda == 'END':
                    self.jenisJeda = 'INS1'
                    self.sesiJeda.WritePesan(self.txtINS1)
                    self.onSwitchPanels('menu')
                    self.wait = True
            elif abs(posx) <= neutral and not self.JOY_DO_SOMETHING:
                self.JOY_DO_SOMETHING = True
            else:
                pass

    def writeScore(self, data):
        if not os.path.exists('hasil'):
            os.makedirs('hasil')
        if len(data):
            file_name = 'hasil/' + '_'.join(data[0][1:]) + '.csv'  #nama_id.csv
            print 'file name: ', file_name, data
            valid_data = [x for x in data[2:] if x[7] == '' or x[6] > 200]
            total_response = sum([x[6] for x in valid_data])
            # Generate category and calculate average response time for each of them
            categ_list = [x[3:5] for x in data[2:]]
            categ = [list(x) for x in set(tuple(x) for x in categ_list)]  # create unique list
            for c in categ:
                categ_data = [i for i in data[2:] if i[3:5] == c]
                categ_data_len = len(categ_data)
                categ_tot_resp_awal = sum([i[5] for i in categ_data])
                categ_tot_resp_akhir = sum([i[6] for i in categ_data])
                categ_avg_resp_awal = float(categ_tot_resp_awal / categ_data_len)
                categ_avg_resp_akhir = float(categ_tot_resp_akhir / categ_data_len)
                data.append(['RERATA', 'UNTUK', 'KATEGORI', c[0], c[1], categ_avg_resp_awal, categ_avg_resp_akhir])
            if len(valid_data):
                avg = float(total_response) / float(len(valid_data))
            else:
                avg = 0.0
            data.append(['RERATA:', avg])
            print data
            with open(file_name, 'ab') as csvfile:
                scorewriter = csv.writer(csvfile)
                scorewriter.writerows(data[0:])
        else:
            pass

    def onSwitchPanels(self, window):
        """"""
        if window == 'main':
            self.formIdentitas.Hide()
            self.sesiLatihan.Hide()
            self.sesiJeda.Hide()
            self.sesiPenilaian.Show()
        elif window == 'jeda':
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.sesiLatihan.Hide()
            self.sesiJeda.Show()
        elif window == 'latihan':
            self.sesiJeda.Hide()
            self.sesiLatihan.Show()
            self.formIdentitas.Hide()
            self.sesiPenilaian.Hide()
        elif window == 'menu':
            self.sesiJeda.Hide()
            self.sesiLatihan.Hide()
            self.sesiPenilaian.Hide()
            self.formIdentitas.Show()
        else:
            self.sesiJeda.Show()
            self.sesiJeda.Hide()
            self.formIdentitas.Hide()
            self.sesiPenilaian.Hide()
            self.sesiLatihan.Hide()
            self.wait = True
        self.Update()
        self.Layout()
        self.Refresh()

if __name__ == "__main__":
    app = wx.App()
    frame = ViewerFrame()
    app.MainLoop()

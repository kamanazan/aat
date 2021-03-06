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
        self.startTime = 0
        self.score = []
        self.DONE = False
        self.wrongImages = []

    def wrong_action(self, warna=None):
        if warna:
            self.isWrong = True
        else:
            self.isWrong = False

    def prepareImages(self):
        image_list = [img for img in self.picPaths if (img.count('Angry') or img.count('Neutral'))]
        print "total image: ", len(image_list)
        if self.category == 'B':
            image_list_angry = [img for img in image_list if img.count('Angry')] * 6
            image_list_neutral = [img for img in image_list if img.count('Neutral')] * 6

            img_g_angry = [face for face in image_list_angry if face.count('_G')]
            img_s_angry = [face for face in image_list_angry if face.count('_S')]

            img_g_neutral = [face for face in image_list_neutral if face.count('_G')]
            img_s_neutral = [face for face in image_list_neutral if face.count('_S')]
            print "Angry : ", len(image_list_angry)
            print "detail "
            print "grey: ", len(img_g_angry)  # 96 image
            print "sephia: ", len(img_s_angry)  # 96 image
            print "==========================="
            print "neutral : ", len(image_list_neutral)
            print "detail "
            print "grey: ", len(img_g_neutral)  # 96 image
            print "sephia: ", len(img_s_neutral)  # 96 image
            population_g_angry = len(img_g_angry)
            population_s_angry = len(img_s_angry)
            population_g_neutral = len(img_g_neutral)
            population_s_neutral = len(img_s_neutral)
        elif self.category == 'A':

            image_list_angry = [img for img in image_list if img.count('Angry')]
            image_list_neutral = [img for img in image_list if img.count('Neutral')]

            img_g_angry = [face for face in image_list_angry if face.count('_G')] * 11
            img_s_angry = [face for face in image_list_angry if face.count('_S')] * 1

            img_g_neutral = [face for face in image_list_neutral if face.count('_G')] * 1
            img_s_neutral = [face for face in image_list_neutral if face.count('_S')] * 11

            print "Angry : ", len(image_list_angry)
            print "detail "
            print "     grey: ", len(img_g_angry)
            print "     sephia: ", len(img_s_angry)
            print "==========================="
            print "neutral : ", len(image_list_neutral)
            print "detail "
            print "     grey: ", len(img_g_neutral)  # 96 image
            print "     sephia: ", len(img_s_neutral)  # 96 image
            population_g_angry = len(img_g_angry)
            population_s_angry = len(img_s_angry)
            population_g_neutral = len(img_g_neutral)
            population_s_neutral = len(img_s_neutral)

        # -----------------------------------------------------------------------------------------------

        image_g_angry_list = random.sample(img_g_angry, population_g_angry)
        image_s_angry_list = random.sample(img_s_angry, population_s_angry)
        image_g_neutral_list = random.sample(img_g_neutral, population_g_neutral)
        image_s_neutral_list = random.sample(img_s_neutral, population_s_neutral)

        image_used = list(image_g_angry_list + image_s_angry_list + image_g_neutral_list + image_s_neutral_list)
        # image_bw_list.extend(image_sp_list)
        random.shuffle(image_used)
        # image_used = image_bw_list
        print "jumlah foto: ", len(image_used)
        self.images = image_used

    def setResponden(self, responden_data):
        self.category = responden_data[-1]
        self.score.append(responden_data)
        self.score.append(['TGL', 'RAS', 'SEX', 'EKSPRESI', 'WARNA', 'RESPON AWAL(REACTION TIME)(ms)',
                           'RESPON AKHIR(RESPONSE TIME)(ms)', 'KET'])

    def calculateResponse(self):
        info = self.image_name.split('.')[0]
        race, gender, expr, color = info.split('_')
        response = (time.time() - self.startTime) * 1000
        print 'RESPON AKHIR:', response
        date = time.strftime(" %d/%m/%Y %H:%M:%S", time.localtime())
        not_valid = self.firstResponse < 100 or self.firstResponse > 2000
        if self.isWrong and not_valid:
            keterangan = 'TIDAK VALID DAN SALAH'
        elif self.isWrong:
            keterangan = 'SALAH'
        elif not_valid:
            keterangan = 'TIDAK VALID'
        else:
            keterangan = ''
        score_set = [date, race, gender, expr, color, self.firstResponse, response, keterangan]
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

        labelFour = wx.StaticText(self, wx.ID_ANY, 'Category')

        categoryChoices = ['A', 'B']
        inputTxtFour = wx.Choice(self, wx.ID_ANY, choices=categoryChoices)

        self.idresponden = inputTxtOne
        self.nama = inputTxtTwo
        self.genchoice = inputTxtThree
        self.catchoice = inputTxtFour

        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputFourSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(title, 0, wx.ALIGN_CENTER, 5)

        inputOneSizer.Add((20, 20), proportion=1)  # this is a spacer
        inputOneSizer.Add(labelOne, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputTwoSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputTwoSizer.Add(labelTwo, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputThreeSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputThreeSizer.Add(labelThree, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputFourSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputFourSizer.Add(labelFour, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        # Add the 3-item sizer to the gridsizer and
        gridSizer.Add(inputOneSizer, 0, wx.ALIGN_LEFT)
        # Set the TextCtrl to expand on resize
        gridSizer.Add(inputTxtOne, 0, wx.ALIGN_LEFT | wx.EXPAND)
        gridSizer.Add(inputTwoSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(inputTxtTwo, 0, wx.ALIGN_LEFT | wx.EXPAND)
        gridSizer.Add(inputThreeSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(inputTxtThree, 0, wx.ALIGN_LEFT)
        gridSizer.Add(inputFourSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(inputTxtFour, 0, wx.ALIGN_LEFT)

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
        category = str(self.catchoice.GetStringSelection())
        responden_data = ['IDENTITAS:', idresponden, nama, gender, category]

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


class FormContoh(wx.Panel):

    def __init__(self, parent):
        # Add a panel so it looks correct on all platforms
        wx.Panel.__init__(self, parent)

        self.pesan_contoh1 = 'Contoh Foto Sephia'
        self.pesan_contoh2 = 'Contoh Foto Hitam Putih'
        self.pesan_next = 'Gerakan Joystick ke kanan untuk melanjutkan'
        font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title1 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_contoh1, style=wx.ALIGN_CENTER)
        self.title2 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_contoh2, style=wx.ALIGN_CENTER)
        self.title3 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_next, style=wx.ALIGN_CENTER)
        self.title1.SetFont(font)
        self.title2.SetFont(font)
        self.title3.SetFont(font)

        self.imgs = wx.Image('images/Latihan_S.jpeg', wx.BITMAP_TYPE_ANY).Scale(400,400)
        self.imgg = wx.Image('images/Latihan_G.jpeg', wx.BITMAP_TYPE_ANY).Scale(400,400)
        self.imageCtrls = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.imgs), style=wx.ALIGN_BOTTOM)
        self.imageCtrlg = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.imgg), style=wx.ALIGN_CENTER)

        foto1 = wx.BoxSizer(wx.VERTICAL)
        foto2 = wx.BoxSizer(wx.VERTICAL)
        tmpsizer = wx.BoxSizer(wx.VERTICAL)
        fotoSizer = wx.BoxSizer()
        sizer = wx.GridSizer(rows=1, cols=1)

        foto1.Add(self.title1, 0, wx.ALIGN_CENTER, 0)
        foto1.Add((10,10))
        foto2.Add(self.title2, 0, wx.ALIGN_CENTER, 0)
        foto2.Add((10,10))
        foto1.Add(self.imageCtrls, 0, wx.ALIGN_CENTER, 0)
        foto2.Add(self.imageCtrlg, 0, wx.ALIGN_CENTER, 0)
        fotoSizer.Add(foto1,0, wx.ALIGN_CENTER, 0)
        fotoSizer.Add((20,20))
        fotoSizer.Add(foto2,0, wx.ALIGN_CENTER, 0)
        tmpsizer.Add(fotoSizer,0, wx.ALIGN_CENTER, 0)
        tmpsizer.Add((30,30))
        tmpsizer.Add(self.title3, 0, wx.ALIGN_CENTER, 0)
        sizer.Add(tmpsizer, 0, wx.ALIGN_CENTER,0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.Refresh()


class FormContohSalah(wx.Panel):
    def __init__(self, parent):
        # Add a panel so it looks correct on all platforms
        wx.Panel.__init__(self, parent)

        self.pesan1 = 'Jika terdapat tanda "X" warna merah seperti ini:\n'
        self.pesan2 = """



artinya, Anda keliru dalam MENARIK / MENDORONG.
Ingat, TARIK joystick mendekati tubuh jika yang tersaji adalah foto berwarna HITAM PUTIH
dan
DORONG joystick mendekati tubuh jika yang tersaji adalah foto berwarna SEPHIA.
Jika keliru, teruskan saja untuk mengerjakan"""
        self.pesan_next = 'Gerakan Joystick ke kanan untuk melanjutkan'
        font = wx.Font(22, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font_big = wx.Font(246, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title1 = wx.StaticText(self, wx.ID_ANY, label=self.pesan1, style=wx.ALIGN_CENTER)
        self.title2 = wx.StaticText(self, wx.ID_ANY, label=self.pesan2, style=wx.ALIGN_CENTER)
        self.title3 = wx.StaticText(self, wx.ID_ANY, label='X', style=wx.ALIGN_CENTER)
        self.title4 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_next, style=wx.ALIGN_CENTER)
        self.title1.SetFont(font)
        self.title2.SetFont(font)
        self.title4.SetFont(font)
        self.title3.SetFont(font_big)
        self.title3.SetForegroundColour((255,0,0))

        titleSizer = wx.GridSizer(rows=4, cols=1, vgap=10)

        titleSizer.Add(self.title1, 0, wx.ALIGN_CENTER, 0)
        titleSizer.Add(self.title3, 0, wx.ALIGN_CENTER, 0)
        titleSizer.Add(self.title2, 0, wx.ALIGN_CENTER, 0)
        titleSizer.Add(self.title4, 0, wx.ALIGN_CENTER, 0)

        self.SetSizer(titleSizer)
        titleSizer.Fit(self)
        self.Layout()
        self.Refresh()


class ViewerFrame(wx.Frame):
    """"""
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="AAT Retraining")
        self.formIdentitas = FormIdentitas(self)
        self.sesiPenilaian = FormPenilaian(self)
        self.sesiJeda = FormJeda(self)
        self.sesiLatihan = FormLatihan(self)
        self.contohGambar = FormContoh(self)
        self.contohSalah = FormContohSalah(self)
        self.contohGambar.Hide()
        self.contohSalah.Hide()
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
        self.txtINS1 = "Kepada anda akan disajikan\nFoto-foto berwarna HITAM PUTIH dan SEPHIA\n\n\n\nTugas Anda adalah\nMENARIK joystick untuk foto HITAM PUTIH\nMENDORONG Joystick untuk foto SEPHIA\n\n\nPada saat MENARIK, foto akan membesar\nPada saat MENDORONG, foto akan mengecil dan menghilang\nAnda diminta untuk MENARIK/MENDORONG joystick hingga maksimal\n(Tidak dapat bergerak lagi)\n\n\nSetelah itu Anda diminta untuk mengembalikan joystick ke posisi tengah kembali dan\nfoto baru akan ditampilkan\n\n\n\nGeser joystick ke kanan untuk memulai"
        self.txtINS2 = 'Berikut ini adalah sesi latihan\n\n\n\nKepada Anda akan disajikan foto pemandangan berwarna HITAM PUTIH dan SEPHIA\n\n\nTARIK joystick mendekati tubuh jika yang tersaji adalah foto berwarna HITAM PUTIH\nDORONG joystick menjauhi tubuh jika yang tersaji adalah foto berwarna SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan \nMENGEMBALIKAN joystick ke posisi tengah, setelah itu akan ditampilkan foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'
        self.txtOPN = 'Berikut ini adalah sesi program\n\n\n\nTARIK joystick untuk foto HITAM PUTIH\nDORONG joystick untuk foto SEPHIA\n\n\nIngat anda harus MENDORONG\MENARIK joystick hingga MAKSIMAL dan\nMENGEMBALIKAN joystick ke posisi tengah untuk melihat foto berikutnya\n\n\nLAKUKAN SECEPAT DAN SEAKURAT MUNGKIN\n\n\n\nGeser joystick ke kanan untuk memulai'
        self.txtREST = 'SESI 1 telah berakhir\n\n\nSilahkan tunggu instruksi selanjutnya'
        self.txtEND = 'Sesi program telah selesai\n\n\nTerima kasih atas partisipasi anda'
        self.dec = decimal.Decimal
        self.sesiJeda.WritePesan(self.txtINS1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.formIdentitas, 1, wx.EXPAND)
        self.sizer.Add(self.contohGambar, 1, wx.EXPAND)
        self.sizer.Add(self.contohSalah, 1, wx.EXPAND)
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
        self.hasil = []

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
                    if any(not x for x in data[1:]):
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
                    self.sesiLatihan.loadImage('TESTPUSH', abs(posy))
                    print "posx,posy: ", posx, posy
                elif posy < -neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy <= -full else True
                    self.sesiLatihan.loadImage('TESTPULL', abs(posy))
                    print "posx,posy: ", posx, posy
                elif (abs(posy) <= neutral ) and self.JOY_DO_SOMETHING:
                    # When joystick return to normal position before fully push/pull return image to original size
                    self.sesiLatihan.loadImage(None, 0)
                elif (abs(posy) <= neutral ) and not self.JOY_DO_SOMETHING:
                    print 'NEXT!'
                    print "posx,posy: ", posx, posy
                    self.JOY_DO_SOMETHING = True
                    if self.sesiLatihan.shouldStop() and not self.sesiLatihan.isWrong :
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
                    self.sesiPenilaian.startTime = time.time()
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
                        self.writeScore(self.sesiPenilaian.getScore())
                        self.sesiPenilaian.clearScore()
                        self.sesiPenilaian.wrongImages = []
                        print "scoreIsClear:", len(self.sesiPenilaian.getScore()) == 0
                        if self.wait:
                            self.jenisJeda = 'REST'
                            self.sesiJeda.WritePesan(self.txtREST)
                            self.onSwitchPanels('jeda')
                            self.wait = False
                        else:
                            self.hasil = []
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
                    self.onSwitchPanels('contoh')
                elif self.jenisJeda == 'INS2':
                    self.onSwitchPanels('salah')
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
        elif self.contohGambar.IsShown():
            if self.LOCK_PANEL:
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                else:
                    pass
            elif posx >= full and self.JOY_DO_SOMETHING:
                self.JOY_DO_SOMETHING = False
                self.sesiJeda.WritePesan(self.txtINS2)
                self.onSwitchPanels('jeda')
                self.jenisJeda = 'INS2'
        elif self.contohSalah.IsShown():
            if self.LOCK_PANEL:
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                else:
                    pass
            elif posx >= full and self.JOY_DO_SOMETHING:
                self.JOY_DO_SOMETHING = False
                self.onSwitchPanels('latihan')
                self.sesiLatihan.prepareImages()
                self.sesiLatihan.setCurrentImage(self.sesiLatihan.getRandomImage())
                self.sesiLatihan.loadImage(None,0)

    def hitung_rerata(self, valid_data):
        data = []
        total_response_akhir = sum([x[6] for x in valid_data])
        avg_akhir = float(total_response_akhir) / float(len(valid_data))
        total_response_awal = sum([x[5] for x in valid_data])
        avg_awal = float(total_response_awal) / float(len(valid_data))
        # Generate category and calculate average response time for each of them
        # ekspresi dan warna
        categ_list = [x[3:5] for x in valid_data]
        categ = [list(x) for x in set(tuple(x) for x in categ_list)]  # create unique list
        for c in categ:
            categ_data = [i for i in valid_data if i[3:5] == c]
            categ_data_len = len(categ_data)
            categ_tot_resp_awal = sum([i[5] for i in categ_data])
            categ_tot_resp_akhir = sum([i[6] for i in categ_data])
            categ_avg_resp_awal = float(categ_tot_resp_awal) / float(categ_data_len)
            categ_avg_resp_akhir = float(categ_tot_resp_akhir) / float(categ_data_len)
            data.append(['RERATA', 'UNTUK', 'KATEGORI', c[0], c[1], categ_avg_resp_awal, categ_avg_resp_akhir])
        # ras
        categ_ras_i = [c for c in valid_data if c[1] == 'I']
        categ_ras_c = [c for c in valid_data if c[1] == 'C']
        len_i = len(categ_ras_i)
        len_c = len(categ_ras_c)
        ras_i_tot_resp_awal = sum([i[5] for i in categ_ras_i])
        ras_c_tot_resp_awal = sum([i[5] for i in categ_ras_c])
        ras_i_tot_resp_akhir = sum([i[6] for i in categ_ras_i])
        ras_c_tot_resp_akhir = sum([i[6] for i in categ_ras_c])
        ras_i_avg_resp_awal = float(ras_i_tot_resp_awal) / float(len_i)
        ras_c_avg_resp_awal = float(ras_c_tot_resp_awal) / float(len_c)
        ras_i_avg_resp_akhir = float(ras_i_tot_resp_akhir) / float(len_i)
        ras_c_avg_resp_akhir = float(ras_c_tot_resp_akhir) / float(len_c)
        data.append(['RERATA', 'UNTUK', 'KATEGORI', 'RAS', 'I', ras_i_avg_resp_awal, ras_i_avg_resp_akhir])
        data.append(['RERATA', 'UNTUK', 'KATEGORI', 'RAS', 'C', ras_c_avg_resp_awal, ras_c_avg_resp_akhir])
        # ras ekspresi gender
        categ_list = [[x[1], x[3], x[2][0]] for x in valid_data]
        categ = [list(x) for x in set(tuple(x) for x in categ_list)]  # create unique list
        for c in categ:
            categ_data = [i for i in valid_data if i[1] == c[0] and i[2].startswith(c[2]) and i[3] == c[1]]
            categ_data_len = len(categ_data)
            categ_tot_resp_awal = sum([i[5] for i in categ_data])
            categ_tot_resp_akhir = sum([i[6] for i in categ_data])
            categ_avg_resp_awal = float(categ_tot_resp_awal) / float(categ_data_len)
            categ_avg_resp_akhir = float(categ_tot_resp_akhir) / float(categ_data_len)
            data.append(['RERATA', 'UNTUK', c[0], c[1], c[2], categ_avg_resp_awal, categ_avg_resp_akhir])
        # ras ekspresi gender warna
        categ_list = [[x[1], x[3], x[2][0], x[4]] for x in valid_data]
        categ = [list(x) for x in set(tuple(x) for x in categ_list)]  # create unique list
        for c in categ:
            categ_data = [i for i in valid_data if
                          i[1] == c[0] and i[2].startswith(c[2]) and i[3] == c[1] and i[4] == c[3]]
            categ_data_len = len(categ_data)
            categ_tot_resp_awal = sum([i[5] for i in categ_data])
            categ_tot_resp_akhir = sum([i[6] for i in categ_data])
            categ_avg_resp_awal = float(categ_tot_resp_awal) / float(categ_data_len)
            categ_avg_resp_akhir = float(categ_tot_resp_akhir) / float(categ_data_len)
            data.append(['RERATA UNTUK', c[0], c[1], c[2], c[3], categ_avg_resp_awal, categ_avg_resp_akhir])
        data.append(['RERATA', 'KESELURUHAN:', '','','', avg_awal, avg_akhir])
        return data

    def writeScore(self, data):
        '''
        :param data:
        data[0] -> (list) identitas peserta
        data[1] -> (list) nama kolom
        data[2:] -> data hasil pengujian dengan format:
                    0: timestamp
                    1: ras
                    2: gender
                    3: ekspresi
                    4: warna
                    5: respon awal
                    6: respon akhir
                    7: keterangan('SALAH' kalo aksi tidak sesuai warna gambar, '' kalo benar)
        '''
        if not len(data):
            return False
        # pastikan data hasil pengujian tidak tercemar
        if any(len(x) != 8 for x in data[2:]):
            return False
        if not os.path.exists('hasil'):
            os.makedirs('hasil')
        file_name = 'hasil/' + '_'.join(data[0][1:]) + '.csv'  #nama_id.csv
        # cek keadaan file, kalo tidak bisa diakses ganti nama file
        try:
            f = open(file_name, 'ab')
        except IOError:
            ts = int(time.time())
            file_name = 'hasil/' + 'DARURAT_' + '_'.join(data[0][1:]) + '_' + str(ts) + '.csv'
        else:
            f.close()
        print 'file name: ', file_name, data
        if self.wait:
            data[0].append('SESI 1')
        else:
            data[0].append('SESI 2')
        # amankan hasil pengujian
        with open(file_name, 'ab') as csvfile:
            scorewriter = csv.writer(csvfile)
            scorewriter.writerows(data[0:])
        # Mulai menghitung rerata
        valid_data = [x for x in data[2:] if not x[7]]
        if not len(valid_data):
            return False
        rerata = []
        self.hasil.extend(valid_data)
        rerata.extend(self.hitung_rerata(valid_data))
        if not self.wait and self.hasil:
            rerata.append(['RERATA', 'SEMUA', 'SESI'])
            rerata.extend(self.hitung_rerata(self.hasil))
        with open(file_name, 'ab') as csvfile:
            scorewriter = csv.writer(csvfile)
            scorewriter.writerows(rerata[0:])
        return True

    def onSwitchPanels(self, window):
        """"""
        if window == 'main':
            self.formIdentitas.Hide()
            self.sesiLatihan.Hide()
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiPenilaian.Show()
        elif window == 'jeda':
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.sesiLatihan.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiJeda.Show()
        elif window == 'latihan':
            self.sesiJeda.Hide()
            self.sesiLatihan.Show()
            self.formIdentitas.Hide()
            self.sesiPenilaian.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
        elif window == 'menu':
            self.sesiJeda.Hide()
            self.sesiLatihan.Hide()
            self.sesiPenilaian.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.formIdentitas.Show()
        elif window == 'contoh':
            self.sesiJeda.Hide()
            self.contohSalah.Hide()
            self.sesiLatihan.Hide()
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.contohGambar.Show()
        elif window == 'salah':
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.sesiLatihan.Hide()
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.contohSalah.Show()
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

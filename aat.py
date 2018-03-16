import os
from pathlib2 import Path
import wx
import wx.adv

import random
import time
import csv
import decimal

from collections import defaultdict

JENIS_BLOK = ['Latihan', 'BLOK A', 'BLOK B', 'BLOK C']


class AatImage:
    def __init__(self, curr_path):
        """
        get list of image in current directory
        curr_path: PosixPAth object parent dir of the images, starts with push* / pull*
        """

        self.action = 'PUSH' if curr_path.name.count('Push') else 'PULL'
        self.category = curr_path.parents[0].name
        # since glob is generator we use next() to get the first item and resolve() to get the full path
        self.phases = {
            0: str(curr_path.glob('*medium.jpg').next().resolve()),
            1: str(curr_path.glob('*1.jpg').next().resolve()),
            2: str(curr_path.glob('*2.jpg').next().resolve()),
            3: str(curr_path.glob('*3.jpg').next().resolve()),
        }
        self.wrong_image = str(curr_path.glob('*SALAH.jpg').next().resolve())

    def image_on_phase(self, scale):
        if scale <= 0.2:
            phase = 0
        elif (scale > 0.2) and (scale <=0.5):
            phase = 1
        elif (scale > 0.5) and (scale <= 0.9):
            phase = 2
        else:
            phase = 3
        return self.phases[phase]

    def wrong_image(self):
        return self.wrong_image

    def __str__(self):
        return '%s - %s' % (self.action, self.category)

    def __repr__(self):
        return self.__str__()


class ImagePanel(wx.Panel):

    def __init__(self, parent, rep=1):
        """

        :param parent: default param for wx.Panel instance
        :param rep: extra param that set the number of repetition for the image set
        """
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('BLACK')
        self.__img_repetition__ = rep
        self.widthDisp, self.heightDisp = wx.DisplaySize()
        self.displayed_image = wx.Image(1, 1)
        self.image_name = ''
        self.current_image = None
        self.images = []
        self.totalPictures = 0
        self.isWrong = False
        self.picPaths = Path('images')
        # Preparing the layout
        self.imgSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)
        self.imageCtrl = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=wx.Bitmap(wx.Image(self.displayed_image)))
        self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        self.imgSizer.Fit(self)
        self.SetSizer(self.imgSizer)

    def wrong_action(self, warna=None):
        pass

    def prepare_images(self, blok):
        img_path = '*%s*/*/*' % JENIS_BLOK[blok]
        path_to_image = list(self.picPaths.glob(img_path))
        image_used = []
        for x in xrange(self.__img_repetition__):
            # image must be repeated 12 times
            image_used.extend([AatImage(folder) for folder in path_to_image])  # something like that
        # image_bw_list.extend(image_sp_list)
        random.shuffle(image_used)
        # image_used = image_bw_list
        print "jumlah foto: ", len(image_used)
        self.images = image_used

    def setCurrentImage(self, image):
        self.current_image = image
        self.isWrong = False
        print "img left:", len(self.images)

    def getRandomImage(self):
        return self.images.pop(self.images.index(random.choice(self.images))) if self.images else None

    def shouldStop(self):
        return len(self.images) == 0


    def loadImage(self, action, scale):
        """
        action: 'PUSH' or 'PULL', determine whether the image should be zoomed out/zoomed in
        scale: current y-axis of the joystick, this is used for smoother scaling
        """
        self.image_name = self.current_image
        self.isWrong = self.current_image.action != action if action and not self.isWrong else self.isWrong
        self.displayed_image = self.current_image.wrong_image if self.isWrong else self.current_image.image_on_phase(scale)
        print 'Displayed Image:', self.displayed_image
        self.imageCtrl.SetBitmap(wx.Bitmap(self.displayed_image))
        self.imgSizer.Remove(0)
        self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        self.Update()
        self.Layout()
        self.Refresh()


class FormPenilaian(ImagePanel):
    """"""
    def __init__(self, parent, rep):
        """Constructor"""
        super(FormPenilaian, self).__init__(parent, rep)
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

    def prepare_images(self, blok):
        super(FormPenilaian, self).prepare_images(blok)
        assert len(self.images) == 168

    def setResponden(self, responden_data):
        self.category = responden_data[-1]
        # JUDUL
        self.score.append(
            ['Identitas', '', '', '', '', '', 'Jenis Crowd', 'Waktu reaksi dalam miliseconds (pengulangan ke-)', '', '', '', '', '', '',
             '', '', '', '', ''])
        # SUB JUDUL
        self.score.append(['NO', 'NAMA', 'JENIS KELAMIN', 'USIA', 'ASAL SEKOLAH', 'KODE BLOK', '', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
        self.score.append(responden_data)

    def calculateResponse(self):
        info = self.image_name
        response = (time.time() - self.startTime) * 1000
        if self.isWrong:
            response *= -1.0
        print 'RESPON AKHIR:', response
        score_set = (str(info), response)
        self.score.append(score_set)
        self.DONE = True

    def calculateFirstResponse(self):
        # TODO: mungkin ga dipake
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
    def __init__(self, parent, rep):
        """Constructor"""
        super(FormLatihan, self).__init__(parent, rep)
        self.img_latih_g_salah = 'images\Latihan_G_salah.jpeg'
        self.img_latih_s_salah = 'images\Latihan_S_salah.jpeg'
        self.img_latih_g = 'images\Latihan_G.jpeg'
        self.img_latih_s = 'images\Latihan_S.jpeg'
        self.currentImage = self.img_latih_g
        # self.layout()

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

    def prepare_images(self):
        self.images = [self.img_latih_g, self.img_latih_s] * 6
        self.images = random.sample(self.images,12)
        self.images.append(self.img_latih_g)
        self.currentImage = self.images.pop(0)


class FormIdentitas(wx.Panel):

    def __init__(self, parent):
        # Add a panel so it looks correct on all platforms
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('WHITE')
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

        titleSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)

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
        self.imageCtrls = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.Bitmap(wx.Image(self.imgs)), style=wx.ALIGN_BOTTOM)
        self.imageCtrlg = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.Bitmap(wx.Image(self.imgg)), style=wx.ALIGN_CENTER)

        foto1 = wx.BoxSizer(wx.VERTICAL)
        foto2 = wx.BoxSizer(wx.VERTICAL)
        tmpsizer = wx.BoxSizer(wx.VERTICAL)
        fotoSizer = wx.BoxSizer()
        sizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)

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
        font = wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_big = wx.Font(256, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title1 = wx.StaticText(self, wx.ID_ANY, label=self.pesan1, style=wx.ALIGN_CENTER)
        self.title2 = wx.StaticText(self, wx.ID_ANY, label=self.pesan2, style=wx.ALIGN_CENTER)
        self.title3 = wx.StaticText(self, wx.ID_ANY, label='X', style=wx.ALIGN_CENTER)
        self.title4 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_next, style=wx.ALIGN_CENTER)
        self.title1.SetFont(font)
        self.title2.SetFont(font)
        self.title4.SetFont(font)
        self.title3.SetFont(font_big)
        self.title3.SetForegroundColour((255,0,0))

        titleSizer = wx.GridSizer(rows=4, cols=1, hgap=1, vgap=10)

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
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Approach-Avoidance Task")
        self.formIdentitas = FormIdentitas(self)
        self.sesiPenilaian = FormPenilaian(self, 12)
        self.sesiJeda = FormJeda(self)
        # self.sesiLatihan = FormLatihan(self)
        self.sesiLatihan = ImagePanel(self, 2)
        self.contohGambar = FormContoh(self)
        self.contohSalah = FormContohSalah(self)
        self.contohGambar.Hide()
        self.contohSalah.Hide()
        self.sesiLatihan.Hide()
        self.sesiJeda.Hide()
        self.sesiPenilaian.Hide()
        self.formIdentitas.Show()
        self.folderPath = ""
        self.sesi = 0 # dipakai untuk menentukan jenis block, 0=Latihan, 1..3=Blok A..C
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
        self.joystick = wx.adv.Joystick()
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
        # print "pos:",posx, posy, x, y

        if self.formIdentitas.IsShown():
            if self.LOCK_PANEL:
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
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                    print 'LOCK RELEASE!'
                else:
                    pass
            else:
                if posy > neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy >= full else True
                    scale = abs(posy)
                    if posy >= full:
                        scale = 1.0
                    print "PUSH - posx,posy: ", posx, posy, scale
                    self.sesiLatihan.loadImage('PUSH', scale)
                elif posy < -neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy <= -full else True
                    scale = abs(posy)
                    if posy <= -full:
                        scale = 1.0
                    print "PULL - posx,posy: ", posx, posy, scale
                    self.sesiLatihan.loadImage('PULL', scale)
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
                        # if not self.sesiLatihan.isWrong:
                        #     self.sesiLatihan.setCurrentImage(self.sesiLatihan.getRandomImage())
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
                elif posy < -neutral and self.JOY_DO_SOMETHING:
                    self.JOY_DO_SOMETHING = False if posy <= -full else True
                    scale = abs(posy)
                    if posy <= -full:
                        self.sesiPenilaian.calculateResponse()
                        scale = 1.0
                    assert not self.NEUTRAL
                    self.sesiPenilaian.loadImage('PULL', scale)
                elif (abs(posy) <= neutral ) and self.JOY_DO_SOMETHING:
                    # When joystick return to normal position before fully push/pull return image to original size
                    self.sesiPenilaian.loadImage(None, 0)
                elif (abs(posy) <= neutral ) and not self.JOY_DO_SOMETHING:
                    self.NEUTRAL = True
                    self.JOY_DO_SOMETHING = True
                    if not self.sesiPenilaian.shouldStop():
                        print 'NEXT!', posx, posy, abs(posy)
                        if self.sesiPenilaian.isWrong:
                            self.sesiPenilaian.wrongImages.append(self.sesiPenilaian.current_image)
                        self.sesiPenilaian.resetFirstResponse()
                        self.sesiPenilaian.setCurrentImage(self.sesiPenilaian.getRandomImage())
                        self.sesiPenilaian.loadImage(None, 0)
                        self.sesiPenilaian.startTime = time.time()
                    elif self.sesiPenilaian.shouldStop():
                        self.sesiPenilaian.resetFirstResponse()
                        self.save(self.sesiPenilaian.getScore())
                        self.sesiPenilaian.clearScore()
                        self.sesiPenilaian.wrongImages = []
                        print "scoreIsClear:", len(self.sesiPenilaian.getScore()) == 0
                        if self.sesi < 3:
                            self.jenisJeda = 'REST'
                            self.sesiJeda.WritePesan(self.txtREST)
                            self.onSwitchPanels('jeda')
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
                if self.jenisJeda == 'INS1':
                    self.onSwitchPanels('contoh')
                elif self.jenisJeda == 'INS2':
                    self.onSwitchPanels('salah')
                elif self.jenisJeda == 'OPN':
                    self.onSwitchPanels('main')
                    # data_responden = self.formIdentitas.getValues()
                    # self.sesiPenilaian.setResponden(data_responden)
                    self.sesi += 1
                    self.sesiPenilaian.prepare_images(self.sesi)
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
                self.LOCK_PANEL = True
                self.onSwitchPanels('latihan')
                self.sesiLatihan.prepare_images(self.sesi)
                self.sesiLatihan.setCurrentImage(self.sesiLatihan.getRandomImage())
                self.sesiLatihan.loadImage(None,0)

    def save(self, data):
        """
        :param data:
        data[0] -> (list) Judul kolom
        data[1] -> (list) Subjudul kolom
        data[2:] -> (list of tuple) data hasil pengujian dengan format:
                    0: Jenis Crowd (Pull/Push - kombinasi crows)
                    1: response
        """
        def group_score(score):
            """
            Group the list by image_name and combine the score
            :param score: list of tuple with format [('image_name', response_time)...]
            :return: grouped score sorted by image_name
            """
            d = defaultdict(list)
            for k, v in score:
                d[k].append(v)
            # Output: defaultdict(<type 'list'>, {'a': [1, 2, 3], 'c': [1, 2, 3], 'b': [1, 2, 3]})
            # >>> d['a']
            # [1, 2, 3]
            # We flatten it into a list of list and later save it as csv
            score_list = []
            for name, score in d.iteritems():
                data = [name]
                data.extend(score)
                score_list.append(data)
            # >>> score_list
            # [['a', 1, 2, 3], ['c', 1, 2, 3], ['b', 1, 2, 3]]
            # return sorted by crowd name
            score_list.sort(key=lambda x: x[0])
            return score_list


        def list_extend(list1, list2):
            extended_list = list(list1) # create new list since list1 is a reference to list object
            extended_list.extend(list2)
            return extended_list


        if not len(data):
            return False
        if not os.path.exists('hasil'):
            os.makedirs('hasil')
        file_name = 'hasil/output.csv'
        # cek keadaan file, kalo tidak bisa diakses ganti nama file
        score_list = group_score(data)
        try:
            f = open(file_name, 'ab')
        except IOError:
            ts = int(time.time())
            file_name = 'hasil/' + 'output_' + '_' + str(ts) + '.csv'
        else:
            f.close()
        print 'file name: ', file_name, data
        # if self.wait:
        #     data[0].append('SESI 1')
        # else:
        #     data[0].append('SESI 2')
        # amankan hasil pengujian
        with open(file_name, 'ab') as csvfile:
            scorewriter = csv.writer(csvfile)
            if self.sesi == 1:
                scorewriter.writerow(['Identitas', '', '', '', '', '', 'Jenis Crowd', 'Waktu reaksi dalam miliseconds (pengulangan ke-)', '', '', '', '', '', '', '', '', '', '', ''])
                scorewriter.writerow(['NO', 'NAMA', 'JENIS KELAMIN', 'USIA', 'ASAL SEKOLAH', 'KODE BLOK', '', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
                # TODO: ganti dengan identitas peserta
                first_row = ['NO', 'NAMA', 'JENIS KELAMIN', 'USIA', 'ASAL SEKOLAH', JENIS_BLOK[self.sesi]]
                first_row.extend(score_list[0])
            else:
                first_row = ['', '', '', '', '', JENIS_BLOK[self.sesi]]
                first_row.extend(score_list[0])
            scorewriter.writerow(first_row)
            score_list = score_list[1:]
            padding = ['', '', '', '', '', '']
            padded_score = [list_extend(padding, s) for s in score_list]
            scorewriter.writerows(padded_score)


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
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiLatihan.Show()
            self.formIdentitas.Hide()
            self.sesiPenilaian.Hide()
        elif window == 'menu':
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiLatihan.Hide()
            self.sesiPenilaian.Hide()
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
        self.Update()
        self.Layout()
        self.Refresh()


if __name__ == "__main__":
    app = wx.App()
    frame = ViewerFrame()
    app.MainLoop()

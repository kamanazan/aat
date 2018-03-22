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
        # TODO: DRY
        if curr_path:
            self.action = 'PUSH' if curr_path.name.count('Push') else 'PULL'
            self.category = curr_path.parents[0].name
            # since glob is generator we use next() to get the first item
            # and resolve() to get the full path
            self.phases = {
                0: str(curr_path.glob('*medium.jpg').next().resolve()),
                1: str(curr_path.glob('*1.jpg').next().resolve()),
                2: str(curr_path.glob('*2.jpg').next().resolve()),
                3: str(curr_path.glob('*3.jpg').next().resolve()),
                9: wx.Image(1, 1)  # blank image
            }
            self.wrong_image = str(
                curr_path.glob('*SALAH.jpg').next().resolve())
        else:
            self.action = ''
            self.category = ''
            self.phases = {
                0: wx.Image(1, 1),
                1: wx.Image(1, 1),
                2: wx.Image(1, 1),
                3: wx.Image(1, 1),
                9: wx.Image(1, 1)
            }
            self.wrong_image = ''

    def image_on_phase(self, scale):
        if scale <= 0.2:
            phase = 0
        elif (scale > 0.2) and (scale <=0.4):
            phase = 1
        elif (scale > 0.4) and (scale <= 0.6):
            phase = 2
        elif (scale > 0.6) and (scale <= 0.9):
            phase = 3
        else:
            phase = 9
        return self.phases[phase]

    def __str__(self):
        return '%s - %s' % (self.action, self.category)

    def __repr__(self):
        return self.__str__()


class ImagePanel(wx.Panel):

    def __init__(self, parent):
        """

        :param parent: default param for wx.Panel instance
        :param rep: extra param that set the number of repetition for the image set
        """
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('BLACK')
        self.widthDisp, self.heightDisp = wx.DisplaySize()
        self.displayed_image = wx.Image(1, 1)
        self.image_name = ''
        self.current_image = None
        self.images = []
        self.totalPictures = 0
        self.isWrong = False
        self.picPaths = Path('images')
        self.wrongImages = []  # TODO: need this?
        # scores
        self.firstResponse = 0.0
        self.startTime = 0
        self.score = []
        # Preparing the layout
        self.imgSizer = wx.GridSizer(rows=2, cols=1, hgap=5, vgap=5)
        self.imageCtrl = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=wx.Bitmap(wx.Image(self.displayed_image)))
        pesan_next = 'Gerakan Joystick ke kanan untuk melanjutkan'
        self.pesan_salah = wx.StaticText(
            self, wx.ID_ANY, label=pesan_next, style=wx.ALIGN_CENTER)
        self.pesan_salah.Hide()
        self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        self.imgSizer.Add(self.pesan_salah, 0, wx.ALIGN_CENTER, 5)
        self.imgSizer.Fit(self)
        self.SetSizer(self.imgSizer)

    def prepare_images(self, blok):
        img_path = '*%s*/*/*' % JENIS_BLOK[blok]
        path_to_image = list(self.picPaths.glob(img_path))
        image_used = []
        repetition = 2 if blok == 0 else 12
        for x in xrange(repetition):
            image_used.extend([AatImage(folder) for folder in path_to_image])
        random.shuffle(image_used)
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
        print 'Displayed Image:', self.displayed_image if isinstance(self.displayed_image, str) else 'BLANK'
        self.imageCtrl.SetBitmap(wx.Bitmap(self.displayed_image))
        # TODO: test what will happen
        # self.imgSizer.Remove(0)
        # self.imgSizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER, 5)
        if self.isWrong:
            self.pesan_salah.Show()
        else:
            self.pesan_salah.Hide()
        self.Update()
        self.Layout()
        self.Refresh()

    def calculateResponse(self):
        info = self.image_name
        response = (time.time() - self.startTime) * 1000
        if self.isWrong:
            response *= -1.0
        score_set = (str(info), response)
        self.score.append(score_set)
        self.DONE = True

    def calculateFirstResponse(self):
        # TODO: mungkin ga dipake
        self.firstResponse = (time.time() - self.startTime) * 1000

    def resetFirstResponse(self):
        self.firstResponse = 0.0
        self.DONE = False

    def getScore(self):
        return self.score

    def clearScore(self):
        self.score = []


class FormOpening(wx.Panel):

    def __init__(self, parent):
        # Add a panel so it looks correct on all platforms
        wx.Panel.__init__(self, parent)

        self.pesan = '''
Approach-Avoidance Task



Program
'''
        self.title = wx.StaticText(self, wx.ID_ANY, label=self.pesan, style=wx.ALIGN_CENTER)
        font = wx.Font(36,  wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)

        titleSizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)

        titleSizer.Add(self.title, 0, wx.ALIGN_CENTER, 0)

        self.SetSizer(titleSizer)
        titleSizer.Fit(self)
        self.Layout()
        self.Refresh()


class FormIdentitas(wx.Panel):

    def __init__(self, parent):
        # Add a panel so it looks correct on all platforms
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('WHITE')
        title = wx.StaticText(self, wx.ID_ANY, 'Mohon isilah form identitas di bawah ini')
        font_underline = wx.Font(14,  wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        font_underline.SetUnderlined(True)
        title.SetFont(font_underline)

        label_nopeserta = wx.StaticText(self, wx.ID_ANY, 'No. Peserta')
        input_nopeserta = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, -1))

        label_nama = wx.StaticText(self, wx.ID_ANY, 'Nama')
        input_nama = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, -1))

        label_gender = wx.StaticText(self, wx.ID_ANY, 'Jenis Kelamin')
        gender_choices = ['Laki-laki', 'Perempuan']
        input_gender = wx.RadioBox(self, wx.ID_ANY, choices=gender_choices)

        label_usia = wx.StaticText(self, wx.ID_ANY, 'Usia')
        input_usia = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, -1))

        label_sekolah = wx.StaticText(self, wx.ID_ANY, 'Asal Sekolah')
        input_sekolah = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, -1))

        self.idresponden = input_nopeserta
        self.nama = input_nama
        self.genchoice = input_gender
        self.usia = input_usia
        self.sekolah = input_sekolah

        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.GridSizer(rows=5, cols=2, hgap=5, vgap=5)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputTwoSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputFourSizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sekolah_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(title, 0, wx.ALIGN_CENTER, 5)

        inputOneSizer.Add((20, 20), proportion=1)  # this is a spacer
        inputOneSizer.Add(label_nopeserta, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputTwoSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputTwoSizer.Add(label_nama, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputThreeSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputThreeSizer.Add(label_gender, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        inputFourSizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        inputFourSizer.Add(label_usia, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        input_sekolah_sizer.Add((20, 20), 1, wx.EXPAND)  # this is a spacer
        input_sekolah_sizer.Add(label_sekolah, 0, wx.ALL | wx.ALIGN_LEFT, 2)

        gridSizer.Add(inputOneSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(input_nopeserta, 0, wx.ALIGN_LEFT)

        gridSizer.Add(inputTwoSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(input_nama, 0, wx.ALIGN_LEFT)

        gridSizer.Add(inputThreeSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(input_gender, 0, wx.ALIGN_LEFT)

        gridSizer.Add(inputFourSizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(input_usia, 0, wx.ALIGN_LEFT)

        gridSizer.Add(input_sekolah_sizer, 0, wx.ALIGN_LEFT)
        gridSizer.Add(input_sekolah, 0, wx.ALIGN_LEFT)

        self.pesan = 'Gerakan Joystick ke kanan untuk melanjutkan'
        self.title = wx.StaticText(self, wx.ID_ANY, label=self.pesan, style=wx.ALIGN_CENTER)
        font = wx.Font(20,  wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        topSizer.Add(titleSizer, 0, wx.ALIGN_CENTER)
        topSizer.Add((20, 20), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(gridSizer, 0, wx.ALIGN_CENTER, 5)
        topSizer.Add(wx.StaticLine(self), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(self.title, 0, wx.ALIGN_CENTER, 5)  #topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(topSizer)
        topSizer.Fit(self)

    @property
    def identitas_peserta(self):
        idresponden = str(self.idresponden.GetValue())
        nama = str(self.nama.GetValue())
        gender = str(self.genchoice.GetStringSelection())
        usia = str(self.usia.GetValue())
        sekolah = str(self.sekolah.GetValue())
        responden_data = [idresponden, nama, gender, usia, sekolah, JENIS_BLOK[1]]

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
        font = wx.Font(28,  wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
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
        font = wx.Font(22,  wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title1 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_contoh1, style=wx.ALIGN_CENTER)
        self.title2 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_contoh2, style=wx.ALIGN_CENTER)
        self.title3 = wx.StaticText(self, wx.ID_ANY, label=self.pesan_next, style=wx.ALIGN_CENTER)
        self.title1.SetFont(font)
        self.title2.SetFont(font)
        self.title3.SetFont(font)

        foto1 = wx.BoxSizer(wx.VERTICAL)
        foto2 = wx.BoxSizer(wx.VERTICAL)
        tmpsizer = wx.BoxSizer(wx.VERTICAL)
        fotoSizer = wx.BoxSizer()
        sizer = wx.GridSizer(rows=1, cols=1, hgap=5, vgap=5)

        foto1.Add(self.title1, 0, wx.ALIGN_CENTER, 0)
        foto1.Add((10,10))
        foto2.Add(self.title2, 0, wx.ALIGN_CENTER, 0)
        foto2.Add((10,10))
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
        self.opening = FormOpening(self)
        self.formIdentitas = FormIdentitas(self)
        self.sesiPenilaian = ImagePanel(self)
        self.sesiJeda = FormJeda(self)
        self.contohGambar = FormContoh(self)
        self.contohSalah = FormContohSalah(self)

        self.opening.Show()
        self.contohGambar.Hide()
        self.contohSalah.Hide()
        self.sesiJeda.Hide()
        self.sesiPenilaian.Hide()
        self.formIdentitas.Hide()

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
        self.sizer.Add(self.opening, 1, wx.EXPAND)
        self.sizer.Add(self.formIdentitas, 1, wx.EXPAND)
        self.sizer.Add(self.contohGambar, 1, wx.EXPAND)
        self.sizer.Add(self.contohSalah, 1, wx.EXPAND)
        self.sizer.Add(self.sesiPenilaian, 1, wx.EXPAND)
        self.sizer.Add(self.sesiJeda, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.ShowFullScreen(True)
        self.joystick = wx.adv.Joystick()
        self.joystick.SetCapture(self)
        self.Bind(wx.EVT_JOY_MOVE, self.onMove)
        wx.CallLater(100, self.opening_splashscreen)
        self.JOY_DO_SOMETHING = True
        self.NEUTRAL = True
        self.IMAGE_TRANSITION = False
        self.IMAGE_TRANSITION_TIMEOUT = 0 # WHEN the timeout occure (10 seconds after reaching NEUTRAL)
        self.hasil = []
        self.Show()

    def opening_splashscreen(self):
        print 'HERE!'
        present = time.time() + 3
        timeout = 3
        while timeout > 0:
            ct = time.time()
            timeout = present - ct
            print 'Timeout', timeout
        self.onSwitchPanels('menu')

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

        if self.formIdentitas.IsShown():
            if self.LOCK_PANEL:
                if posx <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                else:
                    pass
            else:
                if posx >= full:
                    # TODO: handle data tidak lengkap
                    data = self.formIdentitas.identitas_peserta
                    if len(data) < 5:
                        self.formIdentitas.title.SetLabel('DATA TIDAK LENGKAP')
                    else:
                        self.JOY_DO_SOMETHING = False
                        self.onSwitchPanels('jeda')
        elif self.sesiPenilaian.IsShown():
            if self.LOCK_PANEL:
                if abs(posx) <= neutral:
                    self.JOY_DO_SOMETHING = True
                    self.LOCK_PANEL = False
                    self.sesiPenilaian.startTime = time.time()
                else:
                    pass
            else:
                if not self.IMAGE_TRANSITION:
                    # Joystick moves and image is zoomed in/out
                    if abs(posy) > neutral and self.NEUTRAL:
                        self.NEUTRAL = False
                        self.sesiPenilaian.calculateFirstResponse()
                    if posy > neutral and self.JOY_DO_SOMETHING:
                        self.JOY_DO_SOMETHING = False if posy >= full else True
                        scale = abs(posy)
                        if posy >= full and self.sesi != 0:
                            self.sesiPenilaian.calculateResponse()
                            scale = 1.0
                        assert not self.NEUTRAL
                        self.sesiPenilaian.loadImage('PUSH', scale)
                    elif posy < -neutral and self.JOY_DO_SOMETHING:
                        self.JOY_DO_SOMETHING = False if posy <= -full else True
                        scale = abs(posy)
                        if posy <= -full and self.sesi != 0:
                            self.sesiPenilaian.calculateResponse()
                            scale = 1.0
                        assert not self.NEUTRAL
                        self.sesiPenilaian.loadImage('PULL', scale)
                    elif (abs(posy) <= neutral ) and self.JOY_DO_SOMETHING:
                        # TODO: 21 Mar 2018, Test FIRST and then refactor
                        # When joystick return to normal position before
                        # fully push/pull return image to original size
                        if self.sesiPenilaian.isWrong:
                            self.NEUTRAL = True
                            self.JOY_DO_SOMETHING = True
                            self.IMAGE_TRANSITION = True
                        self.sesiPenilaian.loadImage(None, 0)
                    elif (abs(posy) <= neutral ) and not self.JOY_DO_SOMETHING:
                        self.NEUTRAL = True
                        self.JOY_DO_SOMETHING = True
                        self.IMAGE_TRANSITION = True
                        # Set timeout for 10 seconds
                        self.IMAGE_TRANSITION_TIMEOUT = time.time() + 10
                    else:
                        pass
                else:
                    # TODO: test this, not working bro(220318)
                    curr_time = time.time()
                    time_remaining = self.IMAGE_TRANSITION_TIMEOUT - curr_time
                    print "TIME: ", time_remaining
                    if (posx >= full and self.NEUTRAL) or time_remaining < 0:
                        self.NEUTRAL = False
                        self.IMAGE_TRANSITION = False if self.sesiPenilaian.shouldStop() or time_remaining < 0 else self.IMAGE_TRANSITION
                        if not self.sesiPenilaian.shouldStop():
                            print 'Load Next Image'
                            if self.sesiPenilaian.isWrong:
                                self.sesiPenilaian.wrongImages.append(self.sesiPenilaian.current_image)
                            self.sesiPenilaian.resetFirstResponse()
                            self.sesiPenilaian.setCurrentImage(self.sesiPenilaian.getRandomImage())
                            self.sesiPenilaian.loadImage(None, 0)
                            self.sesiPenilaian.startTime = time.time()
                        elif self.sesiPenilaian.shouldStop():
                            self.IMAGE_TRANSITION = False
                            if self.sesi == 0:
                                self.sesiJeda.WritePesan(self.txtOPN)
                                self.jenisJeda = 'OPN'
                                self.onSwitchPanels('jeda')
                            else:
                                self.sesiPenilaian.resetFirstResponse()
                                self.save(self.sesiPenilaian.getScore())
                                self.sesiPenilaian.clearScore()
                                self.sesiPenilaian.wrongImages = []
                                print "scoreIsClear:", len(
                                    self.sesiPenilaian.getScore()) == 0
                                jeda = 'REST' if 1 <= self.sesi < 3 else 'END'
                                pesan = self.txtREST if 1 <= self.sesi < 3 else self.txtEND
                                self.jenisJeda = jeda
                                self.sesiJeda.WritePesan(pesan)
                                self.onSwitchPanels('jeda')
                    elif posx <= neutral and not self.NEUTRAL:
                        self.NEUTRAL = True
                        self.IMAGE_TRANSITION = False
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
                    self.sesi += 1
                    self.sesiPenilaian.prepare_images(self.sesi)
                    self.sesiPenilaian.setCurrentImage(AatImage(''))
                    self.sesiPenilaian.loadImage(None, 0)
                    self.onSwitchPanels('main')
                elif self.jenisJeda == 'REST':
                    self.jenisJeda = 'OPN'
                    self.sesiJeda.WritePesan(JENIS_BLOK[self.sesi + 1])
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
                self.sesi = 0
                self.sesiPenilaian.prepare_images(self.sesi)
                self.sesiPenilaian.setCurrentImage(AatImage(''))
                self.sesiPenilaian.loadImage(None, 0)
                self.onSwitchPanels('main')

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
            # TODO: RESEARCH find pythonic way to do this
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
        is_exist = os.path.exists(file_name)

        with open(file_name, 'ab') as csvfile:
            scorewriter = csv.writer(csvfile)
            if not is_exist:
                # Tambah table header
                scorewriter.writerow(
                    ['Identitas', '', '', '', '', '', 'Jenis Crowd',
                     'Waktu reaksi dalam miliseconds (pengulangan ke-)', '',
                     '', '', '', '', '', '', '', '', '', ''])
                # Tambah table sub-header
                scorewriter.writerow(
                    ['NO', 'NAMA', 'JENIS KELAMIN', 'USIA', 'ASAL SEKOLAH',
                     'KODE BLOK', '', '1', '2', '3', '4', '5', '6', '7', '8',
                     '9', '10', '11', '12'])
            if self.sesi == 1:
                first_row = self.formIdentitas.identitas_peserta
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
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiPenilaian.Show()
            self.IMAGE_TRANSITION = True
            self.IMAGE_TRANSITION_TIMEOUT = time.time() + 10
        elif window == 'jeda':
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiJeda.Show()
        elif window == 'menu':
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.contohSalah.Hide()
            self.sesiPenilaian.Hide()
            self.opening.Hide()
            self.formIdentitas.Show()
        elif window == 'contoh':
            self.sesiJeda.Hide()
            self.contohSalah.Hide()
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.contohGambar.Show()
        elif window == 'salah':
            self.sesiJeda.Hide()
            self.contohGambar.Hide()
            self.sesiPenilaian.Hide()
            self.formIdentitas.Hide()
            self.contohSalah.Show()
        else:
            self.sesiJeda.Show()
            self.sesiJeda.Hide()
            self.formIdentitas.Hide()
            self.sesiPenilaian.Hide()
        self.Update()
        self.Layout()
        self.Refresh()


if __name__ == "__main__":
    app = wx.App()
    frame = ViewerFrame()
    app.MainLoop()

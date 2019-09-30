from PySide2.QtWidgets import QFileDialog, QGridLayout, QVBoxLayout, QLabel, QWidget, QSlider, QCheckBox, QColorDialog, QMessageBox, QSpinBox, QDoubleSpinBox, QSpacerItem
from PySide2.QtCore import Slot, Qt,SIGNAL
from PySide2.QtGui import QImage, QPixmap, QColor
import cv2

import numpy as np
from skimage import img_as_ubyte

from skimage.segmentation import slic, mark_boundaries, flood_fill

class Canvas (QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.file = "thumb-350-404213.jpg"

        self.__img = cv2.imread(self.file)
        self.__mask = np.zeros(1)
        self.original = cv2.imread(self.file)
        self.__thirdChannelMask = np.dstack((self.__mask, self.__mask, self.__mask))

        self.__nseg = 1
        self.__sig = 1
        self.__comp = 1

        self.nSlider = QSlider(orientation=Qt.Horizontal)
        self.sigSlider = QSlider(orientation=Qt.Horizontal)
        self.thicSlider = QSlider(orientation=Qt.Horizontal)

        self.resize_spinbox = QSpinBox(self)
        self.resize_spinbox.setRange(1, 100)
        self.resize_spinbox.setValue(100)
        self.resize_spinbox.setSuffix(" %")

        self.double_spin_width = QDoubleSpinBox(self)
        self.double_spin_width.setSuffix(" px")
        self.double_spin_width.setValue(0)
        self.double_spin_width.setRange(1, 2000)

        self.double_spin_height = QDoubleSpinBox(self)
        self.double_spin_height.setSuffix(" px")
        self.double_spin_height.setValue(0)
        self.double_spin_height.setRange(1, 2000)

        self.zeroModeCheck = QCheckBox("Usar SLIC0")

        self.__highlightcolor = QColor(255, 255, 255)

        self.__AllColors = [self.__highlightcolor.toTuple()[:3]]

        nLabel = QLabel("Numero de segmentos:")
        sigLabel = QLabel("Sigma:")
        thicLabel = QLabel("Compactação:")
        resizeLabel = QLabel("Fator de resize da image:")
        makssizeLabel = QLabel("Dimensão da mascara de saída:")

        self.__label = QLabel()

        nLabel.setToolTip("O número aproximado de labels da imagem segmentada")
        sigLabel.setToolTip("A largura da Gaussiana")
        thicLabel.setToolTip("Equilibra a proximidade das cores e a proximidade do espaço, maiores valores tornam os Superpixels mais quadrados")

        self.nSlider.setMinimum(1)
        self.nSlider.setMaximum(100)

        self.sigSlider.setMinimum(1)
        self.sigSlider.setMaximum(100)

        self.thicSlider.setMinimum(1)
        self.thicSlider.setMaximum(100)

        glayout1 = QGridLayout()
        glayout1.addWidget(nLabel, 0, 0)
        glayout1.addWidget(self.nSlider, 0, 1)
        glayout1.addWidget(sigLabel, 1, 0)
        glayout1.addWidget(self.sigSlider, 1, 1)
        glayout1.addWidget(thicLabel, 2, 0)
        glayout1.addWidget(self.thicSlider, 2, 1)

        glayout2 = QGridLayout()
        glayout2.addWidget(resizeLabel, 0, 0)
        glayout2.addWidget(self.resize_spinbox, 0, 1)
        glayout2.addWidget(self.zeroModeCheck, 0, 2)
        glayout2.addWidget(makssizeLabel, 1, 0)
        glayout2.addWidget(self.double_spin_width, 1, 1)
        glayout2.addWidget(self.double_spin_height, 1, 2)

        glayout2.setColumnStretch(3, 1)

        self.__label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(glayout1)
        mainlayout.addLayout(glayout2)
        mainlayout.addStretch(1)
        mainlayout.addWidget(self.__label)
        mainlayout.addStretch(1)
        mainlayout.setAlignment(Qt.AlignCenter)
        self.setLayout(mainlayout)

        self.nSlider.sliderReleased.connect(self.onNsegChange)
        self.sigSlider.sliderReleased.connect(self.onSigChange)
        self.thicSlider.sliderReleased.connect(self.onCompChange)

        self.__label.mousePressEvent = self.Highlight

        self.resize_spinbox.valueChanged.connect(self.Resize)

    def getBackgoud(self):
        mask = self.__thirdChannelMask.copy()
        mask_r = mask[:, :, 2]
        mask_g = mask[:, :, 1]
        mask_b = mask[:, :, 0]

        offImage = list()
        for color in self.__AllColors:
            b_off = mask_b != color[2]
            g_off = mask_g != color[1]
            r_off = mask_r != color[0]
            aux = np.logical_and(b_off, g_off)
            offImage.append(np.logical_and(aux, r_off))

        final = offImage[0]
        for cut in offImage:
            final = np.logical_or(final, cut)

        return final

    def changeImage(self):
        self.__mask = slic(self.__img, n_segments=self.__nseg, compactness=self.__comp, sigma=self.__sig, convert2lab=True, slic_zero=self.zeroModeCheck.isChecked())

        mask = self.__mask.copy()
        # to_black = np.where(mask != color for color in self.__AllColors)
        # mask[to_black] = 0
        mask = np.dstack((mask, mask, mask))
        mask = img_as_ubyte(mask)

        self.__thirdChannelMask = mask
        img = cv2.addWeighted(self.__img, 1, mask, 0.5, 0)
        marc_img = mark_boundaries(img, self.__mask)
        self.open_image(marc_img)

    def load_image(self):
        self.__img = cv2.imread(self.file)
        self.original = self.__img
        self.double_spin_width.setValue(self.__img.shape[1])
        self.double_spin_height.setValue(self.__img.shape[0])

        val = self.resize_spinbox.value()
        newDim = int(self.__img.shape[1]*val/100), int(self.__img.shape[0]*val/100)

        self.__img = cv2.resize(self.__img, newDim)

        self.open_image(self.__img)

    def open_image(self, img):
        if img.shape[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888

        copy = img_as_ubyte(img)
        qimg = QImage(copy.data, copy.shape[1], copy.shape[0], copy.strides[0], qformat).rgbSwapped()
        pixmap = QPixmap.fromImage(qimg)

        self.__label.setPixmap(pixmap)
        self.__label.adjustSize()

    @Slot()
    def onNsegChange(self,):
        self.__nseg = self.nSlider.value()
        self.changeImage()

    @Slot()
    def onSigChange(self):
        self.__sig = self.sigSlider.value()
        self.changeImage()

    @Slot()
    def onCompChange(self):
        self.__comp = self.thicSlider.value()
        self.changeImage()

    @Slot()
    def onFileOpen(self):
        self.thicSlider.setValue(1)
        self.nSlider.setValue(1)
        self.sigSlider.setValue(1)
        diag = QFileDialog()
        file = diag.getOpenFileName()[0]
        if file != "":
            self.file = file
            self.load_image()

    @Slot()
    def onSaveFile(self):
        diag = QFileDialog()
        file = diag.getSaveFileName()[0]
        if self.file != "":
            self.__label.pixmap().save(file)

    @Slot()
    def onSaveMask(self):
        diag = QFileDialog()
        file = diag.getSaveFileName()[0]
        final_img = cv2.resize(self.__mask, (self.double_spin_width.value(), self.double_spin_height.value()))

        if file != "":
            cv2.imwrite(file, final_img)

    @Slot()
    def Highlight(self, e):
        if e.x() < 0 or e.x() > self.__img.shape[1] or e.y() < 0 or e.y() > self.__img.shape[0]:
            return

        self.__mask = flood_fill(self.__mask, (e.y(), e.x()), 255)

        self.__thirdChannelMask[:, :, 2] = flood_fill(self.__thirdChannelMask[:, :, 2], (e.y(), e.x()), self.__highlightcolor.red())
        self.__thirdChannelMask[:, :, 1] = flood_fill(self.__thirdChannelMask[:, :, 1], (e.y(), e.x()), self.__highlightcolor.green())
        self.__thirdChannelMask[:, :, 0] = flood_fill(self.__thirdChannelMask[:, :, 0], (e.y(), e.x()), self.__highlightcolor.blue())

        img = cv2.addWeighted(self.__img, 1, self.__thirdChannelMask, 0.5, 0)
        marc_img = mark_boundaries(img, self.__mask)
        self.open_image(marc_img)


    @Slot()
    def exportBinary(self):
        diag = QFileDialog()
        file = diag.getSaveFileName()[0]
        mask = self.__thirdChannelMask.copy()
        final = self.getBackgoud()
        b = mask[:, :, 0]
        g = mask[:, :, 1]
        r = mask[:, :, 2]
        b[final] = 0
        g[final] = 0
        r[final] = 0

        final_img = cv2.resize(mask, (int(self.double_spin_width.value()), int(self.double_spin_height.value())))
        if file != "":
            cv2.imwrite(file, final_img)

    @Slot()
    def onRemoveBackgroud(self):
        box = QMessageBox()
        box.setText("Você deverá escolher a cor do backgroud!!")
        box.setIcon(QMessageBox.Information)
        box.exec()
        diag = QColorDialog()
        backColor = diag.getColor()

        final = self.getBackgoud()
        b = self.__img[:, :, 0]
        g = self.__img[:, :, 1]
        r = self.__img[:, :, 2]
        b[final] = backColor.blue()
        g[final] = backColor.green()
        r[final] = backColor.red()

        self.open_image(self.__img)

    @Slot()
    def Resize(self):
        val = self.resize_spinbox.value()
        newDim = int(self.original.shape[1] * val / 100), int(self.original.shape[0] * val / 100)
        self.__img = cv2.resize(self.original, newDim)
        self.open_image(self.__img)

    @Slot()
    def setHighlightColor(self, color):
        self.__highlightcolor = color

    @Slot()
    def getAllColors(self, colors):
        self.__AllColors = colors

    @Slot()
    def setTran(self, value):
        self.__transparency = 1- value/100

    @Slot()
    def onUndo(self):
        self.thicSlider.setValue(1)
        self.nSlider.setValue(1)
        self.sigSlider.setValue(1)
        self.onNsegChange()
        self.onSigChange()
        self.onCompChange()
        self.__img = self.original
        self.open_image(self.__img)

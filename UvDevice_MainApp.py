import sys
import time
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QIcon, QPalette
from uvdevice_app.uvdevice_ui_01 import Ui_Form
from uvdevice_app.setup_form import UiFormSetUp
from uvdevice_app.appconfig import MyConfParser
from uvdevice_app.modbus import PyModBus
import threading


class UvDeviceMainApp(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(UvDeviceMainApp, self).__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.init()
        self.setWindowTitle("多路数字电源调节控制软件")
        self.setWindowIcon(QIcon(":/uvdevice_config/uvdevice_ico_02.ico"))
        self.ser = serial.Serial()
        self.Com_Dict = {}
        self.port_check()
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        # 串口接收数据处理变量
        self.serial_time_count = 0
        self.serial_receive_frame = 0
        self.serial_receive_buf = []
        self.serial_receive_bytes_count = 0
        self.serial_link_count = 0
        self.serial_link_status = 0
        # 第1组电压电流数据
        self.dc1_module_voltage = 0.0
        self.dc1_module_current = 0.0
        # 第2组电压电流数据
        self.dc2_module_voltage = 0.0
        self.dc2_module_current = 0.0
        # 第3组电压电流数据
        self.dc3_module_voltage = 0.0
        self.dc3_module_current = 0.0
        # 第4组电压电流数据
        self.dc4_module_voltage = 0.0
        self.dc4_module_current = 0.0
        # 第5组电压电流数据
        self.dc5_module_voltage = 0.0
        self.dc5_module_current = 0.0
        # 第6组电压电流数据
        self.dc6_module_voltage = 0.0
        self.dc6_module_current = 0.0
        # 第7组电压电流数据
        self.dc7_module_voltage = 0.0
        self.dc7_module_current = 0.0
        # 第8组电压电流数据
        self.dc8_module_voltage = 0.0
        self.dc8_module_current = 0.0
        self.x = 0.0
        self.pe = QPalette()
        self.pe.setColor(QPalette.Base, Qt.green)
        self.pe.setColor(QPalette.Text, Qt.black)
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.setDisplayFormat("yyyy:MM:dd HH:mm:ss")
        # self.dateTimeEdit.setEnabled(False)
        self.th = threading.Thread(target=self.update_time, args=(), name='update_time_thread')
        self.th.setDaemon(True)
        self.th.start()

    def init(self):
        # 参数设置按钮
        self.setup_button.clicked.connect(app_setup)
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)
        self.timer_send_cb.setEnabled(False)
        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除发送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

        # 波特率修改
        self.s1__box_3.currentIndexChanged.connect(self.port_baudrate_refactor)

    def update_time(self):
        while True:
            self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
            time.sleep(1)

    def closeEvent(self, event):
        try:
            self.timer.stop()
            self.timer_send.stop()
            self.ser.close()

        except:
            pass
        qApp.quit()
        event.accept()

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    def port_baudrate_refactor(self):
        self.ser.baudrate = int(self.s1__box_3.currentText())

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（已开启）")
            self.data_send_timer()
            self.timer_send_cb.setEnabled(True)
            # 打开串口接收定时器，周期为2ms
            self.timer.start(2)

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except IOError:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Port Error", "串口关闭异常！")
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串口状态（已关闭）")
        self.timer_send_cb.setEnabled(False)
        self.timer_send_cb.setChecked(False)

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            # QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收数据
    def data_receive(self):
        self.serial_link_count = self.serial_link_count + 1
        if self.serial_link_count > 2500:   # 2500*2ms=5000ms=5s 通信链路断开
            self.serial_link_count = 0
            self.serial_link_status = 1
            self.pe.setColor(QPalette.Base, Qt.gray)  # 设置背景颜色：灰色
            self.lineEdit_5.setPalette(self.pe)
            self.lineEdit_4.setPalette(self.pe)
            self.lineEdit_10.setPalette(self.pe)
            self.lineEdit_9.setPalette(self.pe)
            self.lineEdit_12.setPalette(self.pe)
            self.lineEdit_11.setPalette(self.pe)
            self.lineEdit_14.setPalette(self.pe)
            self.lineEdit_13.setPalette(self.pe)
            self.lineEdit_16.setPalette(self.pe)
            self.lineEdit_15.setPalette(self.pe)
            self.lineEdit_18.setPalette(self.pe)
            self.lineEdit_17.setPalette(self.pe)
            self.lineEdit_20.setPalette(self.pe)
            self.lineEdit_19.setPalette(self.pe)
            self.lineEdit_22.setPalette(self.pe)
            self.lineEdit_21.setPalette(self.pe)

        if self.serial_time_count > 0:
            self.serial_time_count = self.serial_time_count - 1
            if self.serial_time_count == 0:
                if self.serial_receive_bytes_count == 38 and self.serial_receive_buf[0] == 0x55 \
                        and self.serial_receive_buf[2] == 0xB1:
                    self.serial_receive_frame = 0x01   # 运行数据帧
                    self.dc1_module_current = (self.serial_receive_buf[3] << 8) | self.serial_receive_buf[4]
                    self.dc1_module_voltage = (self.serial_receive_buf[5] << 8) | self.serial_receive_buf[6]

                    self.dc2_module_current = (self.serial_receive_buf[7] << 8) | self.serial_receive_buf[8]
                    self.dc2_module_voltage = (self.serial_receive_buf[9] << 8) | self.serial_receive_buf[10]

                    self.dc3_module_current = (self.serial_receive_buf[11] << 8) | self.serial_receive_buf[12]
                    self.dc3_module_voltage = (self.serial_receive_buf[13] << 8) | self.serial_receive_buf[14]

                    self.dc4_module_current = (self.serial_receive_buf[15] << 8) | self.serial_receive_buf[16]
                    self.dc4_module_voltage = (self.serial_receive_buf[17] << 8) | self.serial_receive_buf[18]

                    self.dc5_module_current = (self.serial_receive_buf[19] << 8) | self.serial_receive_buf[20]
                    self.dc5_module_voltage = (self.serial_receive_buf[21] << 8) | self.serial_receive_buf[22]

                    self.dc6_module_current = (self.serial_receive_buf[23] << 8) | self.serial_receive_buf[24]
                    self.dc6_module_voltage = (self.serial_receive_buf[25] << 8) | self.serial_receive_buf[26]

                    self.dc7_module_current = (self.serial_receive_buf[27] << 8) | self.serial_receive_buf[28]
                    self.dc7_module_voltage = (self.serial_receive_buf[29] << 8) | self.serial_receive_buf[30]

                    self.dc8_module_current = (self.serial_receive_buf[31] << 8) | self.serial_receive_buf[32]
                    self.dc8_module_voltage = (self.serial_receive_buf[33] << 8) | self.serial_receive_buf[34]
                    # 第1组模块 电压电流数值
                    self.lineEdit_5.setText("{:.03f}".format(self.dc1_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_4.setText("{:.03f}".format((self.dc1_module_voltage / 819) * 41.16))
                    # 第2组模块 电压电流数值
                    self.lineEdit_10.setText("{:.03f}".format(self.dc2_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_9.setText("{:.03f}".format((self.dc2_module_voltage / 819) * 41.16))
                    # 第3组模块 电压电流数值
                    self.lineEdit_12.setText("{:.03f}".format(self.dc3_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_11.setText("{:.03f}".format((self.dc3_module_voltage / 819) * 41.16))
                    # 第4组模块 电压电流数值
                    self.lineEdit_14.setText("{:.03f}".format(self.dc4_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_13.setText("{:.03f}".format((self.dc4_module_voltage / 819) * 41.16))
                    # 第5组模块 电压电流数值
                    self.lineEdit_16.setText("{:.03f}".format(self.dc5_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_15.setText("{:.03f}".format((self.dc5_module_voltage / 819) * 41.16))
                    # 第6组模块 电压电流数值
                    self.lineEdit_18.setText("{:.03f}".format(self.dc6_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_17.setText("{:.03f}".format((self.dc6_module_voltage / 819) * 41.16))
                    # 第7组模块 电压电流数值
                    self.lineEdit_20.setText("{:.03f}".format(self.dc7_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_19.setText("{:.03f}".format((self.dc7_module_voltage / 819) * 41.16))
                    # 第8组模块 电压电流数值
                    self.lineEdit_22.setText("{:.03f}".format(self.dc8_module_current / 819 / 79.2 / 0.015))
                    self.lineEdit_21.setText("{:.03f}".format((self.dc8_module_voltage / 819) * 41.16))
                    self.serial_link_status = 0
                    self.serial_link_count = 0

                    self.x = float(str(self.lineEdit_5.text()))
                    if SetUpFormShow.DC1_i_HighLimit >= self.x >= SetUpFormShow.DC1_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_5.setPalette(self.pe)
                        self.lineEdit_4.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_5.setPalette(self.pe)
                        self.lineEdit_4.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_10.text()))
                    if SetUpFormShow.DC2_i_HighLimit >= self.x >= SetUpFormShow.DC2_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_10.setPalette(self.pe)
                        self.lineEdit_9.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_10.setPalette(self.pe)
                        self.lineEdit_9.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_12.text()))
                    if SetUpFormShow.DC3_i_HighLimit >= self.x >= SetUpFormShow.DC3_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_12.setPalette(self.pe)
                        self.lineEdit_11.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_12.setPalette(self.pe)
                        self.lineEdit_11.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_14.text()))
                    if SetUpFormShow.DC4_i_HighLimit >= self.x >= SetUpFormShow.DC4_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_14.setPalette(self.pe)
                        self.lineEdit_13.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_14.setPalette(self.pe)
                        self.lineEdit_13.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_16.text()))
                    if SetUpFormShow.DC5_i_HighLimit >= self.x >= SetUpFormShow.DC5_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_16.setPalette(self.pe)
                        self.lineEdit_15.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_16.setPalette(self.pe)
                        self.lineEdit_15.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_18.text()))
                    if SetUpFormShow.DC6_i_HighLimit >= self.x >= SetUpFormShow.DC6_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_18.setPalette(self.pe)
                        self.lineEdit_17.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_18.setPalette(self.pe)
                        self.lineEdit_17.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_20.text()))
                    if SetUpFormShow.DC7_i_HighLimit >= self.x >= SetUpFormShow.DC7_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_20.setPalette(self.pe)
                        self.lineEdit_19.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_20.setPalette(self.pe)
                        self.lineEdit_19.setPalette(self.pe)

                    self.x = float(str(self.lineEdit_22.text()))
                    if SetUpFormShow.DC8_i_HighLimit >= self.x >= SetUpFormShow.DC8_i_LowLimit:
                        self.pe.setColor(QPalette.Base, Qt.green)  # 设置背景颜色：绿色
                        self.lineEdit_22.setPalette(self.pe)
                        self.lineEdit_21.setPalette(self.pe)
                    else:
                        self.pe.setColor(QPalette.Base, Qt.red)  # 设置背景颜色：红色
                        self.lineEdit_22.setPalette(self.pe)
                        self.lineEdit_21.setPalette(self.pe)

                elif self.serial_receive_bytes_count == 6 and self.serial_receive_buf[0] == 0x55 \
                        and self.serial_receive_buf[2] == 0xB2:
                    self.serial_receive_frame = 0x02  # 调节电流参数 返回帧
                elif self.serial_receive_bytes_count == 6 and self.serial_receive_buf[0] == 0x55 \
                        and self.serial_receive_buf[2] == 0xB3:
                    self.serial_receive_frame = 0x03  # 设置默认参数 返回帧
                else:
                    pass
                # 串口任务结尾--数据清零
                self.serial_receive_buf.clear()
                self.serial_receive_frame = 0
                self.serial_receive_bytes_count = 0
                self.s2__receive_text.insertPlainText(str(self.dateTimeEdit.text()) + '\n')
                # 获取到text光标
                cursor = self.s2__receive_text.textCursor()
                # 滚动到底部
                cursor.movePosition(cursor.End)
                # 设置光标到text中去
                self.s2__receive_text.setTextCursor(cursor)
                if self.data_num_received >= 4095:
                    self.receive_data_clear()
            else:
                pass
        else:
            pass

        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0 and self.serial_receive_frame == 0 and self.serial_receive_bytes_count < 1024:
            self.serial_time_count = 25
            data = self.ser.read(num)
            num = len(data)
            self.serial_receive_buf.extend(data)
            self.serial_receive_bytes_count += num
            # hex显示
            if self.hex_receive.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s2__receive_text.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成utf-8字符串才能输出到窗口中去
                self.s2__receive_text.insertPlainText(data.decode('utf-8', 'ignore'))  # iso-8859-1

            # 统计接收字符的数量
            self.data_num_received += num
            self.lineEdit.setText(str(self.data_num_received))

            # # 获取到text光标
            # cursor = self.s2__receive_text.textCursor()
            # # 滚动到底部
            # cursor.movePosition(cursor.End)
            # # 设置光标到text中去
            # self.s2__receive_text.setTextCursor(cursor)
        else:
            pass

    # 定时发送数据
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)

    # 清除显示
    def send_data_clear(self):
        self.s3__send_text.setText("")
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))

    def receive_data_clear(self):
        self.s2__receive_text.setText("")
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))


class SetUp(QtWidgets.QWidget, UiFormSetUp):
    def __init__(self):
        super(SetUp, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("参数设置")
        self.setWindowIcon(QIcon(":/uvdevice_config/uvdevice_ico_02.ico"))
        self.comboBox.setToolTip("255:广播地址")  # Tool tip
        self.comboBox_2.setToolTip("A2:485远程调节电流 \r\nA3:设置最大输出电流(0--3.0A)")  # Tool tip
        self.DC1_i_HighLimit = MyConfig.dc1_i_h
        self.DC1_i_SetValue = MyConfig.dc1_i_s
        self.DC1_i_LowLimit = MyConfig.dc1_i_l

        self.DC2_i_HighLimit = MyConfig.dc2_i_h
        self.DC2_i_SetValue = MyConfig.dc2_i_s
        self.DC2_i_LowLimit = MyConfig.dc2_i_l

        self.DC3_i_HighLimit = MyConfig.dc3_i_h
        self.DC3_i_SetValue = MyConfig.dc3_i_s
        self.DC3_i_LowLimit = MyConfig.dc3_i_l

        self.DC4_i_HighLimit = MyConfig.dc4_i_h
        self.DC4_i_SetValue = MyConfig.dc4_i_s
        self.DC4_i_LowLimit = MyConfig.dc4_i_l

        self.DC5_i_HighLimit = MyConfig.dc5_i_h
        self.DC5_i_SetValue = MyConfig.dc5_i_s
        self.DC5_i_LowLimit = MyConfig.dc5_i_l

        self.DC6_i_HighLimit = MyConfig.dc6_i_h
        self.DC6_i_SetValue = MyConfig.dc6_i_s
        self.DC6_i_LowLimit = MyConfig.dc6_i_l

        self.DC7_i_HighLimit = MyConfig.dc7_i_h
        self.DC7_i_SetValue = MyConfig.dc7_i_s
        self.DC7_i_LowLimit = MyConfig.dc7_i_l

        self.DC8_i_HighLimit = MyConfig.dc8_i_h
        self.DC8_i_SetValue = MyConfig.dc8_i_s
        self.DC8_i_LowLimit = MyConfig.dc8_i_l

        self.lineEdit_12.setText("{:.03f}".format(self.DC1_i_HighLimit))
        self.lineEdit.setText("{:.03f}".format(self.DC1_i_SetValue))
        self.lineEdit_20.setText("{:.03f}".format(self.DC1_i_LowLimit))

        self.lineEdit_14.setText("{:.03f}".format(self.DC2_i_HighLimit))
        self.lineEdit_2.setText("{:.03f}".format(self.DC2_i_SetValue))
        self.lineEdit_22.setText("{:.03f}".format(self.DC2_i_LowLimit))

        self.lineEdit_10.setText("{:.03f}".format(self.DC3_i_HighLimit))
        self.lineEdit_3.setText("{:.03f}".format(self.DC3_i_SetValue))
        self.lineEdit_18.setText("{:.03f}".format(self.DC3_i_LowLimit))

        self.lineEdit_11.setText("{:.03f}".format(self.DC4_i_HighLimit))
        self.lineEdit_4.setText("{:.03f}".format(self.DC4_i_SetValue))
        self.lineEdit_19.setText("{:.03f}".format(self.DC4_i_LowLimit))

        self.lineEdit_15.setText("{:.03f}".format(self.DC5_i_HighLimit))
        self.lineEdit_6.setText("{:.03f}".format(self.DC5_i_SetValue))
        self.lineEdit_23.setText("{:.03f}".format(self.DC5_i_LowLimit))

        self.lineEdit_16.setText("{:.03f}".format(self.DC6_i_HighLimit))
        self.lineEdit_7.setText("{:.03f}".format(self.DC6_i_SetValue))
        self.lineEdit_24.setText("{:.03f}".format(self.DC6_i_LowLimit))

        self.lineEdit_9.setText("{:.03f}".format(self.DC7_i_HighLimit))
        self.lineEdit_5.setText("{:.03f}".format(self.DC7_i_SetValue))
        self.lineEdit_17.setText("{:.03f}".format(self.DC7_i_LowLimit))

        self.lineEdit_13.setText("{:.03f}".format(self.DC8_i_HighLimit))
        self.lineEdit_8.setText("{:.03f}".format(self.DC8_i_SetValue))
        self.lineEdit_21.setText("{:.03f}".format(self.DC8_i_LowLimit))

        self.DC1_i_SetValueHex = int(float(str(self.lineEdit.text())) * 100)
        self.DC2_i_SetValueHex = int(float(str(self.lineEdit_2.text())) * 100)
        self.DC3_i_SetValueHex = int(float(str(self.lineEdit_3.text())) * 100)
        self.DC4_i_SetValueHex = int(float(str(self.lineEdit_4.text())) * 100)
        self.DC5_i_SetValueHex = int(float(str(self.lineEdit_6.text())) * 100)
        self.DC6_i_SetValueHex = int(float(str(self.lineEdit_7.text())) * 100)
        self.DC7_i_SetValueHex = int(float(str(self.lineEdit_5.text())) * 100)
        self.DC8_i_SetValueHex = int(float(str(self.lineEdit_8.text())) * 100)

        self.send_buf = []
        self.send_buf.append("{:02X}".format(0x55))  # 帧头 索引位置0

        self.send_buf.append("{:02X}".format(int(self.comboBox.currentText())))  # 地址码 索引位置1

        self.send_buf.append("{:02X}".format(int(self.comboBox_2.currentText(), 16)))  # 功能码 索引位置2

        self.send_buf.append("{:02X}".format(self.DC1_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC1_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC2_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC2_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC3_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC3_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC4_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC4_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC5_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC5_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC6_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC6_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC7_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC7_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(self.DC8_i_SetValueHex // 256))
        self.send_buf.append("{:02X}".format(self.DC8_i_SetValueHex % 256))

        self.send_buf.append("{:02X}".format(0x00))  # crc_h
        self.send_buf.append("{:02X}".format(0x00))  # crc_l

        self.send_buf.append("{:02X}".format(0xAA))  # 帧尾

        self.send_buf_s = " ".join(self.send_buf)

    def set_param(self):
        try:
            # -----------------------------------------------------------------
            self.DC1_i_HighLimit = float(str(self.lineEdit_12.text()))
            self.DC2_i_HighLimit = float(str(self.lineEdit_14.text()))
            self.DC3_i_HighLimit = float(str(self.lineEdit_10.text()))
            self.DC4_i_HighLimit = float(str(self.lineEdit_11.text()))
            self.DC5_i_HighLimit = float(str(self.lineEdit_15.text()))
            self.DC6_i_HighLimit = float(str(self.lineEdit_16.text()))
            self.DC7_i_HighLimit = float(str(self.lineEdit_9.text()))
            self.DC8_i_HighLimit = float(str(self.lineEdit_13.text()))

            self.DC1_i_SetValue = float(str(self.lineEdit.text()))
            self.DC2_i_SetValue = float(str(self.lineEdit_2.text()))
            self.DC3_i_SetValue = float(str(self.lineEdit_3.text()))
            self.DC4_i_SetValue = float(str(self.lineEdit_4.text()))
            self.DC5_i_SetValue = float(str(self.lineEdit_6.text()))
            self.DC6_i_SetValue = float(str(self.lineEdit_7.text()))
            self.DC7_i_SetValue = float(str(self.lineEdit_5.text()))
            self.DC8_i_SetValue = float(str(self.lineEdit_8.text()))

            self.DC1_i_LowLimit = float(str(self.lineEdit_20.text()))
            self.DC2_i_LowLimit = float(str(self.lineEdit_22.text()))
            self.DC3_i_LowLimit = float(str(self.lineEdit_18.text()))
            self.DC4_i_LowLimit = float(str(self.lineEdit_19.text()))
            self.DC5_i_LowLimit = float(str(self.lineEdit_23.text()))
            self.DC6_i_LowLimit = float(str(self.lineEdit_24.text()))
            self.DC7_i_LowLimit = float(str(self.lineEdit_17.text()))
            self.DC8_i_LowLimit = float(str(self.lineEdit_21.text()))

            # 8组模块电流设定值
            MyConfig.add_section('i_SetValue')
            MyConfig.add_section_content('i_SetValue', 'module_01', str(self.lineEdit.text()))
            MyConfig.add_section_content('i_SetValue', 'module_02', str(self.lineEdit_2.text()))
            MyConfig.add_section_content('i_SetValue', 'module_03', str(self.lineEdit_3.text()))
            MyConfig.add_section_content('i_SetValue', 'module_04', str(self.lineEdit_4.text()))
            MyConfig.add_section_content('i_SetValue', 'module_05', str(self.lineEdit_6.text()))
            MyConfig.add_section_content('i_SetValue', 'module_06', str(self.lineEdit_7.text()))
            MyConfig.add_section_content('i_SetValue', 'module_07', str(self.lineEdit_5.text()))
            MyConfig.add_section_content('i_SetValue', 'module_08', str(self.lineEdit_8.text()))

            # 8组模块电流上限判定值
            MyConfig.add_section('i_HighValue')
            MyConfig.add_section_content('i_HighValue', 'module_01', str(self.lineEdit_12.text()))
            MyConfig.add_section_content('i_HighValue', 'module_02', str(self.lineEdit_14.text()))
            MyConfig.add_section_content('i_HighValue', 'module_03', str(self.lineEdit_10.text()))
            MyConfig.add_section_content('i_HighValue', 'module_04', str(self.lineEdit_11.text()))
            MyConfig.add_section_content('i_HighValue', 'module_05', str(self.lineEdit_15.text()))
            MyConfig.add_section_content('i_HighValue', 'module_06', str(self.lineEdit_16.text()))
            MyConfig.add_section_content('i_HighValue', 'module_07', str(self.lineEdit_9.text()))
            MyConfig.add_section_content('i_HighValue', 'module_08', str(self.lineEdit_13.text()))

            # 8组模块电流下限判定值
            MyConfig.add_section('i_LowValue')
            MyConfig.add_section_content('i_LowValue', 'module_01', str(self.lineEdit_20.text()))
            MyConfig.add_section_content('i_LowValue', 'module_02', str(self.lineEdit_22.text()))
            MyConfig.add_section_content('i_LowValue', 'module_03', str(self.lineEdit_18.text()))
            MyConfig.add_section_content('i_LowValue', 'module_04', str(self.lineEdit_19.text()))
            MyConfig.add_section_content('i_LowValue', 'module_05', str(self.lineEdit_23.text()))
            MyConfig.add_section_content('i_LowValue', 'module_06', str(self.lineEdit_24.text()))
            MyConfig.add_section_content('i_LowValue', 'module_07', str(self.lineEdit_17.text()))
            MyConfig.add_section_content('i_LowValue', 'module_08', str(self.lineEdit_21.text()))
            # --------------------------------------------------------------
            self.DC1_i_SetValueHex = int(float(str(self.lineEdit.text())) * 100)
            self.DC2_i_SetValueHex = int(float(str(self.lineEdit_2.text())) * 100)
            self.DC3_i_SetValueHex = int(float(str(self.lineEdit_3.text())) * 100)
            self.DC4_i_SetValueHex = int(float(str(self.lineEdit_4.text())) * 100)
            self.DC5_i_SetValueHex = int(float(str(self.lineEdit_6.text())) * 100)
            self.DC6_i_SetValueHex = int(float(str(self.lineEdit_7.text())) * 100)
            self.DC7_i_SetValueHex = int(float(str(self.lineEdit_5.text())) * 100)
            self.DC8_i_SetValueHex = int(float(str(self.lineEdit_8.text())) * 100)

            self.send_buf = []
            self.send_buf.append("{:02X}".format(0x55))  # 帧头

            self.send_buf.append("{:02X}".format(int(self.comboBox.currentText())))  # 地址码

            self.send_buf.append("{:02X}".format(int(self.comboBox_2.currentText(), 16)))  # 功能码

            self.send_buf.append(("{:02X}".format(self.DC1_i_SetValueHex // 256 % 256)))
            self.send_buf.append(("{:02X}".format(self.DC1_i_SetValueHex % 256)))

            self.send_buf.append("{:02X}".format(self.DC2_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC2_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC3_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC3_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC4_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC4_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC5_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC5_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC6_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC6_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC7_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC7_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(self.DC8_i_SetValueHex // 256 % 256))
            self.send_buf.append("{:02X}".format(self.DC8_i_SetValueHex % 256))

            self.send_buf.append("{:02X}".format(MyModBus.crc16(1, 18, self.send_buf[:]) // 256 % 256))  # crc_h
            self.send_buf.append("{:02X}".format(MyModBus.crc16(1, 18, self.send_buf[:]) % 256))  # crc_l

            self.send_buf.append("{:02X}".format(0xAA))  # 帧尾

            self.send_buf_s = " ".join(self.send_buf)
        except:
            pass
            # raise
            return

    def init(self):
        # 参数设置确认按钮
        self.confirm_Button.clicked.connect(self.confirm)

        # 参数设置取消按钮
        self.cancel_Button_2.clicked.connect(self.cancel)

    def cancel(self):
        self.hide()
        MainFormShow.show()
        MainFormShow.data_send_timer()
        MainFormShow.formGroupBox_2.setEnabled(True)

    def confirm(self):
        self.set_param()
        MainFormShow.s3__send_text.setText("")
        MainFormShow.s3__send_text.insertPlainText(self.send_buf_s)
        MainFormShow.data_send()
        MainFormShow.timer_send_cb.setChecked(False)
        time.sleep(0.05)
        self.hide()
        MainFormShow.show()
        MainFormShow.data_send_timer()
        MainFormShow.formGroupBox_2.setEnabled(True)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.hide()
            MainFormShow.show()
            MainFormShow.data_send_timer()
            MainFormShow.formGroupBox_2.setEnabled(True)
            event.accept()
        else:
            event.ignore()


def app_setup():
    MainFormShow.timer_send.stop()
    # MainFormShow.hide()
    SetUpFormShow.setWindowFlags(Qt.WindowStaysOnTopHint)   # 设置参数窗口前置
    SetUpFormShow.show()    # 设置参数窗口显示
    SetUpFormShow.raise_()  # 设置参数窗口激活唤醒
    MainFormShow.formGroupBox_2.setEnabled(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MyConfig = MyConfParser()  # config 参数配置
    MyModBus = PyModBus()
    MainFormShow = UvDeviceMainApp()
    MainFormShow.show()
    qApp = QtWidgets.QApplication.instance()
    SetUpFormShow = SetUp()
    sys.exit(app.exec_())

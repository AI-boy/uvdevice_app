# -*- coding:utf-8 -*-
import configparser


class MyConfParser:
    def __init__(self):
        self.config_file = "config.txt"
        self.fpath = ".\\" + self.config_file
        self.cf = configparser.ConfigParser()
        self.cf.read(self.fpath)
        with open(self.fpath, 'w') as self.fh:
            self.cf.write(self.fh)
        self.fh.close()
        self.dc1_i_s = 0.0
        self.dc2_i_s = 0.0
        self.dc3_i_s = 0.0
        self.dc4_i_s = 0.0
        self.dc5_i_s = 0.0
        self.dc6_i_s = 0.0
        self.dc7_i_s = 0.0
        self.dc8_i_s = 0.0

        self.dc1_i_h = 0.0
        self.dc2_i_h = 0.0
        self.dc3_i_h = 0.0
        self.dc4_i_h = 0.0
        self.dc5_i_h = 0.0
        self.dc6_i_h = 0.0
        self.dc7_i_h = 0.0
        self.dc8_i_h = 0.0

        self.dc1_i_l = 0.0
        self.dc2_i_l = 0.0
        self.dc3_i_l = 0.0
        self.dc4_i_l = 0.0
        self.dc5_i_l = 0.0
        self.dc6_i_l = 0.0
        self.dc7_i_l = 0.0
        self.dc8_i_l = 0.0

        self.init()

        self.init()

    def init(self):
        try:
            self.dc1_i_s = self.getfloat('i_SetValue', 'module_01')
            self.dc2_i_s = self.getfloat('i_SetValue', 'module_02')
            self.dc3_i_s = self.getfloat('i_SetValue', 'module_03')
            self.dc4_i_s = self.getfloat('i_SetValue', 'module_04')
            self.dc5_i_s = self.getfloat('i_SetValue', 'module_05')
            self.dc6_i_s = self.getfloat('i_SetValue', 'module_06')
            self.dc7_i_s = self.getfloat('i_SetValue', 'module_07')
            self.dc8_i_s = self.getfloat('i_SetValue', 'module_08')

            self.dc1_i_h = self.getfloat('i_HighValue', 'module_01')
            self.dc2_i_h = self.getfloat('i_HighValue', 'module_02')
            self.dc3_i_h = self.getfloat('i_HighValue', 'module_03')
            self.dc4_i_h = self.getfloat('i_HighValue', 'module_04')
            self.dc5_i_h = self.getfloat('i_HighValue', 'module_05')
            self.dc6_i_h = self.getfloat('i_HighValue', 'module_06')
            self.dc7_i_h = self.getfloat('i_HighValue', 'module_07')
            self.dc8_i_h = self.getfloat('i_HighValue', 'module_08')

            self.dc1_i_l = self.getfloat('i_LowValue', 'module_01')
            self.dc2_i_l = self.getfloat('i_LowValue', 'module_02')
            self.dc3_i_l = self.getfloat('i_LowValue', 'module_03')
            self.dc4_i_l = self.getfloat('i_LowValue', 'module_04')
            self.dc5_i_l = self.getfloat('i_LowValue', 'module_05')
            self.dc6_i_l = self.getfloat('i_LowValue', 'module_06')
            self.dc7_i_l = self.getfloat('i_LowValue', 'module_07')
            self.dc8_i_l = self.getfloat('i_LowValue', 'module_08')

        except:
            # 8组模块电流设定值
            self.add_section('i_SetValue')
            self.add_section_content('i_SetValue', 'module_01', '1.500')
            self.add_section_content('i_SetValue', 'module_02', '1.500')
            self.add_section_content('i_SetValue', 'module_03', '1.500')
            self.add_section_content('i_SetValue', 'module_04', '1.500')
            self.add_section_content('i_SetValue', 'module_05', '1.500')
            self.add_section_content('i_SetValue', 'module_06', '1.500')
            self.add_section_content('i_SetValue', 'module_07', '1.500')
            self.add_section_content('i_SetValue', 'module_08', '1.500')

            # 8组模块电流上限判定值
            self.add_section('i_HighValue')
            self.add_section_content('i_HighValue', 'module_01', '1.800')
            self.add_section_content('i_HighValue', 'module_02', '1.800')
            self.add_section_content('i_HighValue', 'module_03', '1.800')
            self.add_section_content('i_HighValue', 'module_04', '1.800')
            self.add_section_content('i_HighValue', 'module_05', '1.800')
            self.add_section_content('i_HighValue', 'module_06', '1.800')
            self.add_section_content('i_HighValue', 'module_07', '1.800')
            self.add_section_content('i_HighValue', 'module_08', '1.800')

            # 8组模块电流下限判定值
            self.add_section('i_LowValue')
            self.add_section_content('i_LowValue', 'module_01', '1.200')
            self.add_section_content('i_LowValue', 'module_02', '1.200')
            self.add_section_content('i_LowValue', 'module_03', '1.200')
            self.add_section_content('i_LowValue', 'module_04', '1.200')
            self.add_section_content('i_LowValue', 'module_05', '1.200')
            self.add_section_content('i_LowValue', 'module_06', '1.200')
            self.add_section_content('i_LowValue', 'module_07', '1.200')
            self.add_section_content('i_LowValue', 'module_08', '1.200')
            pass

    def __del__(self):
        self.fh.close()
        pass

    def add_section(self, s):
        sections = self.cf.sections()
        if s in sections:
            return
        else:
            self.cf.add_section(s)

    def remove_section(self, s):
        return self.cf.remove_section(s)

    def get(self, s, o):
        return self.cf.get(s, o)

    def getfloat(self, s, o):
        return self.cf.getfloat(s, o)

    def set(self, s, o, v):
        if self.cf.has_section(s):
            self.cf.set(s, o, v)

    def remove_option(self, s, o):
        if self.cf.has_section(s):
            return self.cf.remove_option(s, o)
        return False

    def items(self, s):
        return self.cf.items(s)

    def sections(self):
        return self.cf.sections()

    def options(self, s):
        return self.cf.options(s)

    def add_section_content(self, s, *arg):
        self.cf.set(s, arg[0], arg[1])
        self.cf.write(open(self.fpath, "w"))



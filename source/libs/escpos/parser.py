# -*- coding:utf-8 -*-

import re
from .command import Commander


class Parser:
    regex = re.compile(r"((.*?)<(.*?)>)", re.S)

    cmd = bytearray()
    alignment = 0
    receiving_data = False

    alignment_history = [0]
    font_multiplier_history = [(1, 1)]
    data_received = None

    @staticmethod
    def init():
        Parser.cmd = bytearray()
        Parser.cmd.extend(Commander.reset())
        Parser.alignment = 0
        Parser.receiving_data = False

        Parser.alignment_history = [0]
        Parser.font_multiplier_history = [(1, 1)]
        Parser.data_received = None

    @staticmethod
    def send_text(text):
        if Parser.receiving_data:
            # 保存待打印的内容
            Parser.data_received = text
        else:
            Parser.cmd.extend(Commander.text(text))

    @staticmethod
    def dispatch_command(cmd):
        if cmd.upper() == 'C':
            Parser.cmd.extend(Commander.alignment(1))
            Parser.alignment_history.append(1)

        elif cmd.upper() == 'R':
            Parser.cmd.extend(Commander.alignment(2))
            Parser.alignment_history.append(2)

        elif cmd.upper() == 'FB':
            Parser.cmd.extend(Commander.bold(True))

        elif cmd.upper().startswith('FW'):
            multiplier = int(cmd[2:])
            height = Parser.font_multiplier_history[-1][1]
            Parser.cmd.extend(Commander.font_multiplies(multiplier, height))
            Parser.font_multiplier_history.append((multiplier, height))

        elif cmd.upper().startswith('FH'):
            multiplier = int(cmd[2:])
            width = Parser.font_multiplier_history[-1][0]
            Parser.cmd.extend(Commander.font_multiplies(width, multiplier))
            Parser.font_multiplier_history.append((width, multiplier))

        elif cmd.upper().startswith('FS'):
            multiplier = int(cmd[2:])
            Parser.cmd.extend(Commander.font_multiplies(multiplier, multiplier))
            Parser.font_multiplier_history.append((multiplier, multiplier))

        elif cmd.upper() == 'BR' or cmd.upper() == 'QR':
            # 标记图形码内容等标签关闭后再打印
            Parser.receiving_data = True

        elif cmd.upper() == 'N':
            # 标记单据号内容等标签关闭后再打印
            Parser.receiving_data = True

        elif cmd.upper() == 'CUT':
            Parser.cmd.extend(Commander.cut_paper())

        elif cmd.upper() == 'IMG':
            Parser.receiving_data = True

        elif cmd.upper() == "SIG":
            Parser.receiving_data = True

    @staticmethod
    def restore_command(cmd):
        if cmd.upper() == 'C' or cmd.upper() == 'R':
            # 对齐只对当前行生效，因此对齐内容输出完毕后立刻换行，避免影响当前行剩余文本
            Parser.cmd.extend(Commander.text("\n"))
            # 恢复上一个对齐方式
            Parser.alignment_history.pop()
            Parser.cmd.extend(Commander.alignment(Parser.alignment_history[-1]))

        elif cmd.upper() == 'FB':
            Parser.cmd.extend(Commander.bold(False))

        elif cmd.upper().startswith('FW') or cmd.upper().startswith('FH') or cmd.upper().startswith('FS'):
            # 恢复上一组字体宽高
            Parser.font_multiplier_history.pop()
            Parser.cmd.extend(
                Commander.font_multiplies(Parser.font_multiplier_history[-1][0], Parser.font_multiplier_history[-1][1]))

        elif cmd.upper() == 'BR':
            # 打印保存的条码内容
            Parser.cmd.extend(Commander.barcode(Parser.data_received))
            Parser.data_received = None
            Parser.receiving_data = False

        elif cmd.upper() == 'QR':
            # 打印保存的二维码内容
            Parser.cmd.extend(Commander.qrcode(Parser.data_received))
            Parser.data_received = None
            Parser.receiving_data = False

        elif cmd.upper() == 'N':
            # 打印保存的单据号 (单据号指令必须在指令开头)
            Parser.cmd = Commander.receipt_id(Parser.data_received) + Parser.cmd
            Parser.data_received = None
            Parser.receiving_data = False

        elif cmd.upper() == "IMG":
            Parser.cmd.extend(Commander.image(Parser.data_received))
            Parser.data_received = None
            Parser.receiving_data = False

        elif cmd.upper() == "SIG":
            Parser.cmd.extend(Commander.signature(Parser.data_received))
            Parser.data_received = None
            Parser.receiving_data = False

    @staticmethod
    def parse(text):
        Parser.init()

        search = Parser.regex.search(text)
        while search:
            groups = search.groups()

            Parser.send_text(groups[1])

            if groups[2]:
                if not groups[2].startswith('/'):
                    Parser.dispatch_command(groups[2])
                else:
                    Parser.restore_command(groups[2][1:])

            text = text.replace(groups[0], "", 1)

            search = Parser.regex.search(text)

        Parser.send_text(text)
        # Parser.send_text('\r\n')
        # Parser.cmd.extend(Commander.print_and_feed())
        return Parser.cmd

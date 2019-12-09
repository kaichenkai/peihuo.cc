from handlers.base.pub_func import WirelessPrintFunc


class ReceiptPrinter:
    def __init__(self, wireless_print_num, wireless_print_key=""):
        self.printer = WirelessPrintFunc(2)
        self.wireless_print_num = wireless_print_num
        self.wireless_print_key = wireless_print_key

    def test_order_template(self, printer_remarks, printer_num, printer_key, operator_name, create_time):
        """测试打印小票"""
        float_middle = self.printer.float_middle
        zoom_in = self.printer.zoom_in
        line_break = self.printer.line_break
        barcode = self.printer.barcode
        default_size = self.printer.default_size

        order_no = '1234567890'

        content_title = "【打印测试】"
        content_remarks = "{}".format(printer_remarks)
        content_order_no_barcode = "{}".format(order_no)
        content_order_no = "测试单号：{}".format(order_no)
        content_num = "打印机终端号：{}".format(printer_num)
        content_key = "打印机密钥：{}".format(printer_key)
        content_operator = "操作人：{} 时间：{}".format(operator_name, create_time)
        content_support = "技术支持：森果 服务热线：400-027-0135"

        content_body = ""
        content_body += float_middle(zoom_in(content_title), 2)
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_remarks), 3)
        content_body += float_middle(barcode(content_order_no_barcode))
        content_body += line_break("")
        content_body += line_break(zoom_in(content_order_no, 2))
        content_body += line_break(zoom_in(content_num, 2))
        content_body += line_break(zoom_in(content_key, 2))
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_operator, default_size))
        content_body += float_middle(zoom_in(content_support, default_size))

        return content_body

    def stock_out_order_template(self, goods_name, order_no, amount, operator_name, create_time):
        """出库单小票"""
        float_middle = self.printer.float_middle
        zoom_in = self.printer.zoom_in
        line_break = self.printer.line_break
        barcode = self.printer.barcode
        default_size = self.printer.default_size

        content_title = "【出库单】"
        content_goods_name = "{}".format(goods_name)
        content_order_no_barcode = "{}".format(order_no)
        content_order_no = "单号：{}".format(order_no)
        content_amount = "数量：{}".format(amount)
        content_operator = "操作人：{} 时间：{}".format(operator_name, create_time)
        content_support = "技术支持：森果 服务热线：400-027-0135"

        content_body = ""
        content_body += float_middle(zoom_in(content_title), 2)
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_goods_name), 3)
        content_body += float_middle(barcode(content_order_no_barcode))
        content_body += line_break("")
        content_body += line_break(zoom_in(content_order_no, 2))
        content_body += line_break(zoom_in(content_amount, 2))
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_operator, default_size))
        content_body += float_middle(zoom_in(content_support, default_size))

        return content_body

    def firm_settlement_voucher_template(self, receipt_type, goods_name, firm_name, order_no, amount,
                                         remarks, operator_name, create_time, should_cut=False):
        """
        供货商待结算单小票
        receipt_type: 小票类型 0-会计联 1-客户联
        """
        float_middle = self.printer.float_middle
        zoom_in = self.printer.zoom_in
        line_break = self.printer.line_break
        barcode = self.printer.barcode
        default_size = self.printer.default_size
        color_invert = self.printer.color_invert
        accountant_space = self.printer.accountant_space
        customer_space = self.printer.customer_space
        cut = self.printer.cut

        if receipt_type == 0:
            content_header = "[会计联]" + accountant_space
        elif receipt_type == 1:
            content_header = "[客户联]" + customer_space
        else:
            content_header = ""
        content_title = "【供货商待结算单】"
        content_goods_name = "{}({})".format(goods_name, firm_name)
        content_order_no_barcode = "{}".format(order_no)
        content_order_no = "单号：{}".format(order_no)
        content_total_amount = "数量：{}件".format(amount)
        content_remarks = "备注：{}".format(remarks)
        content_operator = "操作人：{} 时间：{}".format(operator_name, create_time)
        content_support = "技术支持：森果 服务热线：400-027-0135"

        content_body = ""
        if receipt_type == 0:
            content_body += line_break(zoom_in(color_invert(content_header), default_size))
        elif receipt_type == 1:
            content_body += line_break(zoom_in(content_header, default_size))
        content_body += float_middle(zoom_in(content_title), 2)
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_goods_name), 3)
        content_body += float_middle(barcode(content_order_no_barcode))
        content_body += line_break("")
        content_body += line_break(zoom_in(content_order_no, 2))
        content_body += line_break(zoom_in(content_total_amount, 2))
        if remarks:
            content_body += line_break(zoom_in(content_remarks, 2))
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_operator, default_size))
        content_body += float_middle(zoom_in(content_support, default_size))
        if should_cut:
            content_body += cut()

        return content_body

    def allocation_order_template(self, goods_name, firm_name, order_no, total_amount, allocation_list, operator_name, create_time):
        """分车单小票"""
        float_middle = self.printer.float_middle
        float_left = self.printer.float_left
        zoom_in = self.printer.zoom_in
        line_break = self.printer.line_break
        bottom_line_break = self.printer.bottom_line_break
        barcode = self.printer.barcode
        default_size = self.printer.default_size

        content_title = "【分车单】"
        content_goods_name = "{}({})".format(goods_name, firm_name)
        content_order_no_barcode = "{}".format(order_no)
        content_order_no = "单号：{}".format(order_no)
        content_total_amount = "总件数：{}".format(total_amount)
        allocation_list = [i for i in allocation_list if i.get("allocating_amount")]

        shop_order = {"仓库": -999, "总部": 1, "刘园": 2, "侯台": 3,
                      "咸水沽": 4, "华明": 5,
                      "大港": 6, "杨村": 7, "新立": 8, "大寺": 9, "汉沽": 10,
                      "沧州": 11, "静海": 13, "芦台": 14, "工农村": 15, "唐山": 16, "廊坊": 17,
                      "哈尔滨": 18, "西青道": 19, "双鸭山": 20, "承德": 21,
                      "张胖子": 22, "固安": 23, "燕郊": 24, "胜芳": 25, "蓟县": 26, }
        allocation_list = sorted(allocation_list, key=lambda d: shop_order.get(d["shop_name"], 999))

        if len(allocation_list) % 2 == 1:
            allocation_list.append(None)
        content_shop_list = ["{} {}".format(data[0]["shop_name"], data[0]["allocating_amount"] or '-')
                             + ("    {} {}".format(data[1]["shop_name"], data[1]["allocating_amount"] or '-') if data[1] else "")
                             for data in zip(allocation_list[0::2], allocation_list[1::2])]
        content_operator = "操作人：{} 时间：{}".format(operator_name, create_time)
        content_support = "技术支持：森果 服务热线：400-027-0135"

        content_body = ""
        content_body += float_middle(zoom_in(content_title), 2)
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_goods_name), 3)
        content_body += float_middle(barcode(content_order_no_barcode))
        content_body += line_break("")
        content_body += zoom_in(content_order_no, 2)
        content_body += line_break("")
        content_body += zoom_in(content_total_amount, 2)
        content_body += line_break("") * 2
        content_body += bottom_line_break()
        for content_shop in content_shop_list:
            content_body += line_break("")
            content_body += float_left(zoom_in(content_shop, 2))
            content_body += line_break("") * 2
            content_body += bottom_line_break()
        content_body += float_middle(zoom_in(content_operator, default_size))
        content_body += float_middle(zoom_in(content_support, default_size))

        return content_body

    def packing_order_template(self, shop_name, order_no, goods_list, operator_name, create_time):
        """店铺配货单小票"""
        float_middle = self.printer.float_middle
        float_left = self.printer.float_left
        zoom_in = self.printer.zoom_in
        line_break = self.printer.line_break
        barcode = self.printer.barcode
        default_size = self.printer.default_size
        bottom_line_break = self.printer.bottom_line_break

        content_title = "【店铺配货单】"
        content_shop_name = "{}".format(shop_name)
        content_order_no_barcode = "{}".format(order_no)
        content_order_no = "单号：{}".format(order_no)
        content_goods_list = [
            ("{}".format(data["goods_name"]),
             "订货量：{} 实配量：{}".format(data["allocated_amount"] or '-', data["allocated_amount"] or '-'))
            for data in goods_list
        ]
        content_operator = "操作人：{} 时间：{}".format(operator_name, create_time)
        content_support = "技术支持：森果 服务热线：400-027-0135"

        content_body = ""
        content_body += float_middle(zoom_in(content_title), 2)
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_shop_name), 3)
        content_body += float_middle(barcode(content_order_no_barcode))
        content_body += line_break("")
        content_body += zoom_in(content_order_no, 2)
        content_body += line_break("") * 2
        content_body += bottom_line_break()
        for content_goods, content_allocation in content_goods_list:
            content_body += zoom_in(content_goods, default_size)
            content_body += line_break("")
            content_body += zoom_in(content_allocation, default_size)
            content_body += line_break("")
            content_body += bottom_line_break()
        content_body += line_break("")
        content_body += float_middle(zoom_in(content_operator, default_size))
        content_body += float_middle(zoom_in(content_support, default_size))

        return content_body

    def print(self, content_body):
        if_print_success, error_txt = self.printer.send_print_request(content_body,
                                                                      self.wireless_print_num, self.wireless_print_key)
        return if_print_success, error_txt

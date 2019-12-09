import handlers.common
import handlers.login
import handlers.shop
import handlers.goods
import handlers.warehouse
import handlers.wish_order
import handlers.quotation_order
import handlers.firm
import handlers.staff
import handlers.demand
import handlers.wxevent
import handlers.station
import handlers.purchase_order
import handlers.summary
import handlers.print
import handlers.order_search
import handlers.configuration
import handlers.servererror
import handlers.allocation_order
import handlers.settlement
import handlers.export
import handlers.parser_order
import handlers.financial
import handlers.pf_api

handlers = [
    # 登录
    (r"/login", handlers.login.LoginState, {}, "LoginState"),  # 登录
    (r"/login/applet", handlers.login.AppletLogin, {}, "AppletLogin"),  # 小程序登录
    (r"/login/wxauth", handlers.login.WxOAuth, {}, "WxOAuth"),  #  微信网页授权
    (r"/bind", handlers.login.AccountBind, {}, "AccountBind"),  # 微信手机号绑定
    (r"/wxticket", handlers.login.WxTicket, {}, "WxTicket"),  # 微信登录二维码
    (r"/wxmessage", handlers.wxevent.WxMessage, {}, "WxMessage"),  # 公众号事件推送
    # (r"/login/oauth", handlers.login.Login, {"action": "oauth"}, "oauth"),  # 微信授权回调
    (r"/purchase/currentstaff", handlers.staff.PurchaseCurrentStaff, {}, "PurchaseCurrentStaff"),  # 小程序获取当前用户的员工身份
    (r"/station/currentstaff", handlers.staff.StationCurrentStaff, {}, "StationCurrentStaff"),  # 中转站获取当前用户的员工身份
    # TODO 兼容旧的接口，一段时间后删除，createtime: 2019-01-04
    (r"/currentstaff", handlers.staff.StationCurrentStaff, {}, "CurrentStaff"),  # 中转站获取当前用户的员工身份

    (r"/currentstation", handlers.station.CurrentTransferStation, {}, "CurrentTransferStation"),  # 平台获取当前用户登录的中转站
    (r"/purchase/currentstation", handlers.station.PurchaseCurrentTransferStation, {}, "PurchaseCurrentTransferStation"),  # 小程序获取当前用户登录的中转站
    (r"/currentshop", handlers.demand.CurrentShop, {}, "CurrentShop"),  # 当前用户登录的门店

    # 公共接口
    (r"/common/logincode", handlers.common.LoginVerifyCode, {}, 'LoginVerifyCode'),  # 登录/注册验证码
    (r"/config", handlers.configuration.Configuration, {}, 'Configuration'),  # 设置
    (r"/servererror/(\w+)", handlers.servererror.ServerErrorDetail, {}, 'ServerErrorDetail'),  # 服务器报错详情
    (r"/banks", handlers.common.BankList, {}, 'BankList'),  # 银行列表
    (r"/branchbanks", handlers.common.BranchBankList, {}, 'BranchBankList'),  # 支行列表
    (r"/bankareas", handlers.common.BankAreaList, {}, 'BankAreaList'),  # 银行所在地区

    # 中转站
    (r"/station", handlers.station.TransferStation, {}, 'TransferStationCreate'),  # 中转站
    (r"/station/(\d+)", handlers.station.TransferStation, {}, 'TransferStationUpdate'),  # 中转站
    (r"/stations", handlers.station.TransferStationList, {}, 'TransferStationList'),  # 平台获取中转站列表
    (r"/purchase/stations", handlers.station.PurchaseTransferStationList, {}, 'PurchaseTransferStationList'),  # 小程序获取中转站列表

    # 门店
    (r"/shop", handlers.shop.Shop, {}, 'ShopCreate'),  # 门店
    (r"/shop/(\d+)", handlers.shop.Shop, {}, 'ShopUpdate'),  # 门店
    (r"/shops", handlers.shop.ShopList, {}, 'ShopList'),  # 门店列表

    # 意向单
    (r"/wishorder", handlers.wish_order.WishOrder, {}, 'WishOrderCreate'),  # 意向单
    (r"/wishorder/(\d+)", handlers.wish_order.WishOrder, {}, 'WishOrderUpdate'),  # 意向单
    (r"/demandwishorder/(\d+)", handlers.demand.WishOrder, {}, 'DemandWishOrder'),  # 订货端用意向单
    (r"/wishorders", handlers.wish_order.WishOrderList, {}, 'WishOrderList'),  # 意向单列表
    (r"/wishorder/last", handlers.wish_order.LastWishOrder, {}, 'LastWishOrder'),  # 最近的意向单
    (r"/wishorder/demand/(\d+)", handlers.wish_order.WishOrderDemandInfo, {}, "WishOrderDemandInfo"),  # 意向单相关的订货单信息
    (r"/wishorder/current", handlers.wish_order.CurrentWishOrder, {}, 'CurrentWishOrder'),  # 当前的意向单
    (r"/demandwishorder/current", handlers.demand.CurrentWishOrder, {}, 'DemandCurrentWishOrder'),  # 当前的意向单
    (r"/wishorderidbydate", handlers.wish_order.WishOrderIdByWishDate, {}, 'WishOrderIdByWishDate'),  # 意向日期对应的意向单

    # 报价单
    (r"/quotation/order/(?P<order_id>\d+)", handlers.quotation_order.QuotationOrder, {}, 'QuotationOrder'),  # 报价单

    # 订货单
    (r"/demandorder", handlers.demand.ShopDemandOrder, {}, 'ShopDemandOrderCreate'),  # 门店创建订货单
    (r"/shop/demandorder/(\d+)", handlers.demand.ShopDemandOrder, {}, 'ShopDemandOrderUpdate'),  # 门店通过链接访问订货单
    (r"/station/demandorder/(\d+)", handlers.demand.StationDemandOrder, {}, 'StationDemandOrderUpdate'),  # 中转站获取订货单详情
    (r"/demandorders", handlers.demand.DemandOrderList, {}, 'DemandOrderList'),  # 订货单列表
    (r"/demandorder/shop/list", handlers.demand.DemandShopList, {}, 'DemandShopList'),  # 订货单门店列表
    (r"/demandordersync", handlers.demand.DemandOrderSyncronization, {}, 'DemandOrderSyncronization'),  # 订货单同步
    (r"/demandorder/station", handlers.demand.DemandOrderStationCookie, {}, "DemandOrderStationCookie"),  # 设置订货单中转站cookie

    # 汇总单
    (r"/summary", handlers.summary.SummaryTable, {}, 'SummaryTable'),  # 汇总单
    (r"/shopdemandinglist", handlers.summary.ShopDemandingList, {}, 'ShopDemandingList'),  # 门店订货状态列表
    (r"/shoppackingprice", handlers.summary.ShopPackingPrice, {}, 'ShopPackingPrice'),  # 门店配货价格
    (r"/demandcutoff", handlers.summary.DemandCutoff, {}, 'DemandCutoff'),  # 汇总单截止订货
    (r"/summarynotifications", handlers.summary.SummaryNotifications, {}, 'SummaryNotifications'),  # 汇总单提醒
    (r"/demand/amount", handlers.summary.DemandAmount, {}, 'DemandAmount'),  # 操作订货量
    (r"/summary/purchasing/dynamics", handlers.summary.StationPurchasingDynamics, {}, 'StationPurchasingDynamics'),  # 中转站查看采购动态
    (r"/allocationorder", handlers.allocation_order.AllocationOrder, {}, 'AllocationOrderCreate'),  # 创建分车记录
    (r"/allocationorder/(\d+)", handlers.allocation_order.AllocationOrder, {}, 'AllocationOrderUpdate'),  # 更新分车记录
    (r"/goodsallocations", handlers.allocation_order.GoodsAllocationList, {}, 'GoodsAllocationList'),  # 单品分车记录列表
    (r"/allocationrecords", handlers.allocation_order.AllocationRecordList, {}, 'AllocationRecordList'),  # 分车记录列表
    (r"/allocationgoodslist", handlers.allocation_order.AllocationOrderGoodsList, {}, 'AllocationOrderGoodsList'),  # 分车单商品列表

    # 采购单
    (r"/purchase/order/list", handlers.purchase_order.PurchaseOrderList, {}, 'PurchaseOrderList'),  # 采购单列表
    (r"/purchase/order/(?P<order_id>\d+)", handlers.purchase_order.PurchaseOrder, {}, 'PurchaseOrder'),  # 采购单商品列表
    (r"/purchase/order/goods", handlers.purchase_order.PurchaseOrderGoods, {}, 'PurchaseOrderGoodsCreate'),  # 新建采购单商品
    (r"/purchase/order/goods/(?P<goods_id>\d+)", handlers.purchase_order.PurchaseOrderGoods, {}, 'PurchaseOrderGoods'),  # 采购单商品数据录入
    (r"/purchase/order/goods/purchaser", handlers.purchase_order.SetPurchaser, {}, 'SetPurchaser'),  # 给采购单商品设置采购员
    (r"/purchase/order/goods/return", handlers.purchase_order.GoodsReturn, {}, 'GoodsReturn'),  # 采购单商品退货
    (r"/purchase/scancodeentry", handlers.purchase_order.ScanCodeEntry, {}, 'ScanCodeEntry'),  # 扫码录入商品数据
    (r"/purchasing/dynamics", handlers.purchase_order.PurchasingDynamics, {}, 'PurchasingDynamics'),  # 采购小程序查看采购动态

    # 商品
    (r"/purchase/goods/list", handlers.goods.PurchaseGoodsList, {}, "PurchaseGoodsList"),  # 采购小程序获取商品列表
    (r"/station/goods/list", handlers.goods.StationGoodsList, {}, "StationGoodsList"),  # 中转站获取商品列表
    (r"/(?P<goods_id>\d+)/firm/list", handlers.goods.GoodsFirmList, {}, "GoodsFirmList"),  # 商品的供货商列表
    (r"/purchase/goods", handlers.goods.PurchaseGoods, {}, "PurchaseGoodsCreate"),  # 采购小程序添加商品
    (r"/purchase/goods/(?P<goods_id>\d+)", handlers.goods.PurchaseGoods, {}, "PurchaseGoodsUpdate"),  # 采购小程序商品处理
    (r"/station/goods", handlers.goods.StationGoods, {}, "StationGoodsCreate"),  # 中转站添加商品
    (r"/station/goods/(?P<goods_id>\d+)", handlers.goods.StationGoods, {}, "StationGoodsUpdate"),  # 中转站商品处理

    # TODO 兼容旧的接口，一段时间后删除，createtime: 2019-01-04
    (r"/goods", handlers.goods.PurchaseGoods, {}, "GoodsCreate"),  # 添加商品
    (r"/goods/(?P<goods_id>\d+)", handlers.goods.PurchaseGoods, {}, "GoodsUpdate"),  # 商品处理

    # 仓库
    (r"/warehouse/stockout/list", handlers.warehouse.StockOutList, {}, "StockList"),  # 出库清单
    (r"/warehouse/stockout", handlers.warehouse.StockOutRecord, {}, "StockOutRecordCreate"),  # 出库确认
    (r"/warehouse/stockout/(?P<stock_outin_record_id>\d+)", handlers.warehouse.StockOutRecord, {}, "StockOutRecordUpdate"),  # 出库确认
    (r"/warehouse/stockin", handlers.warehouse.StockInRecord, {}, "StockInRecord"),  # 入库确认
    (r"/warehouse/stockoutin/record", handlers.warehouse.StockOutInRecord, {}, "StockOutIn"),  # 出入库记录
    (r"/warehouse/stockoutin/statistics/list", handlers.warehouse.StockOutInStatisticsList, {}, "StockOutInStatisticsList"),  # 出入库统计列表

    # 库存
    (r"/warehouse/stock/list", handlers.warehouse.WarehouseStockList, {}, "WarehouseStockList"),  # 仓库库存列表
    (r"/warehouse/stock/(?P<goods_id>\d+)", handlers.warehouse.WarehouseStock, {}, "WarehouseStock"),  # 仓库库存处理
    (r"/warehouse/stock/operation/record", handlers.warehouse.StockOperationRecord, {}, "StockOperationRecord"),  # 库存操作记录
    (r"/warehouse/goodsstocks", handlers.warehouse.GoodsStocks, {}, "GoodsStocks"),  # 商品当前库存

    # 供货商
    (r"/purchase/firm/list", handlers.firm.PurchaseFirmList, {}, "PurchaseFirmList"),  # 采购小程序获取供货商列表
    (r"/station/firm/list", handlers.firm.StationFirmList, {}, "StationFirmList"),  # 中转站获取供货商列表
    (r"/(?P<firm_id>\d+)/goods/list", handlers.firm.FirmGoodsList, {}, "FirmGoodsList"),  # 供货商的货品列表
    (r"/firm", handlers.firm.Firm, {}, "FirmCreate"),  # 供货商处理
    (r"/firm/(?P<firm_id>\d+)", handlers.firm.Firm, {}, "FirmUpdate"),  # 供货商处理
    (r"/firm/operation/record", handlers.firm.FirmOperationRecord, {}, "FirmOperationRecord"),  # 供货商操作记录
    (r"/firm/(\d+)/paymentaccount", handlers.firm.FirmPaymentAccount, {}, "FirmPaymentAccountCreate"),  # 供货商收款账户
    (r"/firm/(\d+)/paymentaccount/(\d+)", handlers.firm.FirmPaymentAccount, {}, "FirmPaymentAccountUpdate"),  # 供货商收款账户
    (r"/firm/paymentaccounts", handlers.firm.FirmPaymentAccountList, {}, "FirmPaymentAccountList"),  # 供货商收款账户列表

    # 供货商结算
    (r"/firmsettlementvoucher", handlers.settlement.FirmSettlementVoucher, {}, "FirmSettlementVoucher"),  # 供货商待结算单
    (r"/firmsettlementvouchers", handlers.settlement.FirmSettlementVoucherList, {}, "FirmSettlementVoucherList"),  # 供货商待结算单列表
    (r"/firmsettlementorder", handlers.settlement.FirmSettlementOrder, {}, "FirmSettlementOrderCreate"),  # 供货商结算单
    (r"/firmsettlementorder/(\d+)", handlers.settlement.FirmSettlementOrder, {}, "FirmSettlementOrderUpdate"),  # 供货商结算单
    (r"/firmsettlementorders", handlers.settlement.FirmSettlementOrderList, {}, "FirmSettlementOrderList"),  # 供货商结算流水
    (r"/firmsettlementsummary", handlers.settlement.FirmSettlementSummary, {}, "FirmSettlementSummary"),  # 供货商结算汇总

    # 费用对账
    (r"/fee", handlers.financial.Fee, {}, "FeeCreate"),  # 费用
    (r"/fees", handlers.financial.FeeList, {}, "FeeList"),  # 费用列表
    (r"/feesummarys", handlers.financial.FeeSummaryList, {}, "FeeSummaryList"),  # 费用汇总

    # 分店对账
    (r"/shopaccounting", handlers.financial.ShopAccountingList, {}, "ShopAccountingList"),  # 门店账单
    (r"/shoppayout", handlers.financial.ShopPayout, {}, "ShopPayoutCreate"),  # 门店其他支出
    (r"/shoppayout/(\d+)", handlers.financial.ShopPayout, {}, "ShopPayoutUpdate"),  # 门店其他支出
    (r"/shoppayoutlist", handlers.financial.ShopPayoutList, {}, "ShopPayoutList"),  # 门店其他支出列表

    # 员工
    (r"/staff", handlers.staff.Staff, {}, 'StaffCreate'),  # 员工
    (r"/staff/(\d+)", handlers.staff.Staff, {}, 'StaffUpdate'),  # 员工
    (r"/stafflist", handlers.staff.StaffList, {}, 'StaffList'),  # 员工列表
    (r"/accountsearch/(\w+)", handlers.staff.AccountSearch, {}, 'AccountSearch'),  # 用户搜索
    (r"/staff/operation/record", handlers.staff.StaffOperationRecord, {}, "StaffOperationRecord"),  # 员工操作记录

    # 打印
    (r"/printer", handlers.print.Printer, {}, 'PrinterCreate'),  # 打印机
    (r"/printer/(\d+)", handlers.print.Printer, {}, 'PrinterUpdate'),  # 打印机
    (r"/printers", handlers.print.PrinterList, {}, 'PrinterList'),  # 打印机列表
    (r"/print/test", handlers.print.TestPrint, {}, 'TestPrint'),  # 测试打印
    (r"/print/stockout", handlers.print.StockOutPrint, {}, 'StockOutPrint'),  # 出库单打印
    (r"/print/shoppacking", handlers.print.ShopPackingPrint, {}, 'ShopPackingPrint'),  # 店铺配货单打印
    (r"/print/allocationorderreprint", handlers.print.AllocationOrderReprint, {}, 'AllocationOrderReprint'),  #  分车单重新打印

    # 订单搜索
    (r"/ordersearch/(\w+)", handlers.order_search.OrderSearch, {}, 'OrderSearch'),  # 单号搜索

    # 导出
    (r"/export/wishorder/(\w+)", handlers.export.WishOrderExport, {}, 'WishOrderExport'),  # 意向单导出
    (r"/export/shoppackingorder/(\d+)", handlers.export.ShopPackingOrderExport, {}, 'ShopPackingOrderExport'),  # 店铺配货单导出
    (r"/export/summary", handlers.export.SummaryExport, {}, 'SummaryExport'),  # 各店进货单导出

    # 导入(嘿麻用户从平台导入意向单、订货单的表格数据)
    (r"/parser/order", handlers.parser_order.ParserOrder, {}, 'ParserOrder'),

    # 订货助手
    (r"/demand/pfshops", handlers.demand.PfShopList, {}, 'PfShopList'),  # 可订货的批发店铺
    (r"/demand/pfdemandorder", handlers.demand.PfDemandOrder, {}, 'PfDemandOrderCreate'),  # 批发订货单
    (r"/demand/pfdemandorder/(\d+)", handlers.demand.PfDemandOrder, {}, 'PfDemandOrderUpdate'),  # 批发订货单
    (r"/demand/pfdemandorders", handlers.demand.PfDemandOrderList, {}, 'PfDemandOrderList'),  # 批发订货单列表

    # 外部 API
    (r"/oauth/pf/demandorder/(\d+)", handlers.pf_api.PfDemandOrder, {}, 'PfDemandOrderApi'),  # 批发订货单接口
]

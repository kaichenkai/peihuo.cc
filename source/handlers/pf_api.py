import dal.models as models
from handlers.base.pub_func import check_float, check_int, AuthFunc
from handlers.base.pub_web import GlobalBaseHandler
from handlers.base.webbase import BaseHandler
from handlers.call_pifa import GetPifaData


# 批发订货单
class PfDemandOrder(GlobalBaseHandler):
    @BaseHandler.check_arguments("action:str", "status:int")
    def put(self, order_id):
        action = self.args["action"]

        if action == "update_status":
            return self.update_status(order_id)

    def update_status(self, order_id):
        status = self.args["status"]

        order = models.ExternalDemandOrder.get_by_id(self.session, order_id)
        if not order:
            return self.send_fail("没有找到对应的订货单")

        if status not in {0, 1, 2, 3, 4}:
            return self.send_fail("status 无效: {}".format(str(status)))

        order.status = status
        self.session.commit()
        return self.send_success()

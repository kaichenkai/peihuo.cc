#!/bin/bash
os=`uname`
if [ "$os" == "Linux" ];then
	echo "------ Statistic Date" `date -d "-$1 day" +%Y-%m-%d` "in progress ------"
else
	echo "------ Statistic Date" `date -v "-"$1"d" +%Y-%m-%d`  "in progress ------"
fi


#根据用户判断脚本执行路径
os_user=`echo "$USER"`

if [ "$os_user" == "yy" ];then
	code_path="/Users/yy/Desktop/"
elif [ "$os_user" == "sunmenghua" ];then
	code_path="/Users/sunmenghua/"
else
	code_path="/home/monk/www/"
fi

excute_path=$code_path"caigou.senguo.cc/cgsource/handlers/base/pub_statistic.py"


echo "Start Runing One Day Statistic - " `date '+%Y-%m-%d %H:%M:%S'`

echo "	1.Runing One Day PurchaseOrderGoodsFirm - " `date '+%Y-%m-%d %H:%M:%S'`
eval python3 $excute_path --action=purchase_order_goods_firm --timetype="$1"

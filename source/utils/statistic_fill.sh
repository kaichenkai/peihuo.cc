#!/bin/bash
#---$1的值为外部传入需要补齐统计的天数
#---$2的值为外部传入的统计方法名称
os=`uname`
os_user=`echo "$USER"`

echo "Start Statistic Fill - " `date '+%Y-%m-%d %H:%M:%S'`
for((i=$1;i>=0;i--))
	do

	if [ "$os" == "Linux" ]
	then
		echo `date -d "-$i day" +%Y-%m-%d` "$2 in progress"
	else
		echo `date -v "-"$i"d" +%Y-%m-%d`  "$2 in progress"
	fi

	if [ "$os_user" == "yy" ]
	then
		python3 /Users/yy/Desktop/caigou.senguo.cc/cgsource/handlers/base/pub_statistic.py --action="$2" --timetype="$i"
	elif [ "$os_user" == "sunmenghua" ]
	then
		python3 /Users/sunmenghua/caigou.senguo.cc/cgsource/handlers/base/pub_statistic.py --action="$2" --timetype="$i"
	else
		python3 /home/monk/www/caigou.senguo.cc/cgsource/handlers/base/pub_statistic.py --action="$2" --timetype="$i"
	fi

	done
echo "End Statistic Fill - " `date '+%Y-%m-%d %H:%M:%S'`

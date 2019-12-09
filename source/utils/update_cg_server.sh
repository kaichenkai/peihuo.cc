#!/bin/sh
#function: 更新master分支代码到本地，并平滑重启服务
# 如果有参数，则不重启本服务器，只拉代码
sudo -v
echo "... Connected, Updating branch master"
cd ~/www/caigou.senguo.cc/cgsource
#git branch
echo "[1/5]Delete previous temp branch"
git branch -D temp
echo "[2/5]Fetch master to temp"
git fetch origin master:temp
echo "[3/5]Merge temp to master"
git merge temp
echo "[4/5]Delete temp branch"
git branch -D temp

# 预跑测试
echo "[6/7] Start run test"
python3 ./app.py --port=8899 --debug=2

if [ $? = 0 ];then
	echo "[5/5]Restarting senguo.cc, please wait..."
	#逐个启动tornado每个端口进程，不中断服务
	sudo supervisorctl restart caigou:8891
	sudo supervisorctl restart caigou:8892
	sudo supervisorctl restart caigou:8893
	sudo supervisorctl restart caigou:8894
else
    # 预跑测试失败，回滚到此次更新前的版本
    echo "[7/7] Run test FAILED, reset commit to $commit_id"
    git reset --hard $commit_id
fi

# 记录更新时间
echo "[DONE] `date +%F" "%H:%M:%S`"
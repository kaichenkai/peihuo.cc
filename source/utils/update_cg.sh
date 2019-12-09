#!/bin/sh
#function: 更新senguo2.5分支代码到所有服务器
echo "\033[1m\033[36m>>> Connecting to Other->Caigou\033[0m"
ssh -t monk@other.senguo.cc "~/www/caigou.senguo.cc/cgsource/utils/update_cg_server.sh"
echo ""
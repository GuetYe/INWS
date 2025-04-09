###
 # @Author: 孙石泉 786721684@qq.com
 # @Date: 2023-11-24 10:46:04
 # @LastEditTime: 2024-02-27 11:48:24
 # @LastEditors: 孙石泉
 # @Description: 
 # @FilePath: \SD-UANET_load_balance\SDN\run\main.sh
# 用ryu的例程话网络拓扑
# ../ryu_operation/gui_topology.py
### 



ryu-manager ../ryu_operation/network_structure.py ../ryu_operation/network_monitor.py ../ryu_operation/network_delay.py  ../ryu_operation/network_shortest_path.py ../ryu_operation/arp_handle.py ../ryu_operation/host_multi_attr_decision_make.py ../ryu_operation/host_get_msg.py ../ryu_operation/network_overload_node.py main.py --observe-links
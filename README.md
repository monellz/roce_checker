# RoCE Checker

检测多机roce环境

## 依赖

*   python3

## 使用方式

```bash
# 当前目录应为库主目录
# 启动测试
# ip_list.txt为ip集合，由换行符分割
python3 rocectl.py start -f ip_list.txt > /dev/null

# 查看当前测试情况
python3 rocectl.py top

# 停止当前测试
python3 rocectl.py stop

# 查看当前性能数据
python3 rocectl.py view
```

*   详细数据会在```.roce_result/```下

*   ```ip_list.txt```样例如下

    ```bash
    172.16.201.4
    172.16.201.5
    172.16.201.6
    172.16.201.7
    ```

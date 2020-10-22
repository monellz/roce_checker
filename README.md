# RoCE Checker

检测多机roce环境

## 依赖

*   python3

## 使用方式

```bash
# 当前目录应为库主目录
# 启动测试
# ip_list.txt为ip集合，由换行符分割
python3 rocectl.py start -f ip_list.txt  > /dev/null
# -nc NUM_CONSUMER 指定并行数量(可选，默认为7)
# -db DATABASE_PATH 指定数据库位置(可选，默认为roce.db)

# 查看当前测试情况
python3 rocectl.py top
# -db DATABASE_PATH 指定数据库位置(可选，默认为roce.db)

# 停止当前测试
python3 rocectl.py stop
python3 rocectl.py stop -f # 强行终止
# -db DATABASE_PATH 指定数据库位置(可选，默认为roce.db)

# 查看当前性能数据(输出到stdout)
python3 rocectl.py view
python3 rocectl.py view -csv # 以csv格式输出
# -db DATABASE_PATH 指定数据库位置(可选，默认为roce.db)
```

*   详细数据会在```.roce_result/```下

*   ```ip_list.txt```样例如下

    ```bash
    172.16.201.4
    172.16.201.5
    172.16.201.6
    172.16.201.7
    ```

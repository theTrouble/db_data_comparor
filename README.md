# db_data_comparor
# 比较多个数据库中同结构表数据差异

## 功能说明
同时对比多个数据库中同结构表数据差异，对比各表数据中id相同的行数据和相对缺失某id的行，生成较为直观差异展示excel文件:<br>
![image](https://github.com/theTrouble/db_data_comparor/blob/master/result_excel.png)

## 注意
小工具使用python3编写<br>
使用前请在脚本中配置需要对比的数据库信息<br>
数据库目前支持mysql<br>
脚本认为表中第一列为id<br>
脚本简单地读所有表数据到内存，无法应对大数据量的比较，可稍作修改变为分批比较以应对大数据量<br>
不要对比空表<br>

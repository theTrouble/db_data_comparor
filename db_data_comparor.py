import pymysql
import xlwt
import os

############################################ 脚本说明 #############################################
# 比较多个数据库（mysql）中同结构表数据（空表就别比了会报错）差异
# 根据id(必须在第一列)相互比较各表，生成差异文件（在脚本的运行时的工作目录中），文件记录各表间相对差异和相对缺省记录
# 注意：脚本实现简单读所有表数据到内存，无法应对大数据量的比较，稍作修改可分批比较数据
# 另：脚本使用python3
############################################ 说明结束 #############################################


############################################ 配置区域 #############################################
#数据库信息配置，按示例配置要比较的数据源信息，可配置随意个
dbs_info = (\
	{"db_ip":"localhost", "db_user":"root", "db_password":"123456", "db_name":"testdb", "table_name":"test_table1"},\
	{"db_ip":"10.1.66.66", "db_user":"root", "db_password":"123456", "db_name":"testdb", "table_name":"test_table2"},\
	{"db_ip":"111.111.111.111", "db_user":"root", "db_password":"123456", "db_name":"testdb", "table_name":"test_table3"},\
	)

#生成的差异文件名
comparison_result_excel_name = "对比结果"
comparison_result_excel_suffix = ".xls"
############################################ 配置结束 #############################################



#函数定义居然要放在函数使用前，这样让人不能首先看到重点啊，差评
#纯解释型语言顺序逐句解释语句的原因？

def is_all_arrays_ended(arrs, indexes):
	for i in range(0, len(arrs)):
		if indexes[i] < len(arrs[i]):
			return False
	return True

#获取在指定行上的指定表间列数据存在差异的列
def get_columns_having_different_value_between_selected_tables(table_data_arr, row_indexe_arr, selected_tables):
	result = []

	for column_index in range(0, len(table_data_arr[0][0])):
		for i in range(0, len(selected_tables) - 1):
			if table_data_arr[selected_tables[i]][row_indexe_arr[selected_tables[i]]][column_index]\
			 != table_data_arr[selected_tables[i + 1]][row_indexe_arr[selected_tables[i + 1]]][column_index]:
				result.append(column_index)

	return result

#获取row_indexe_arr指定行上拥有最小id的表的index数组（可能存在多个）
def get_tables_having_min_id(table_data_arr, row_indexe_arr):
	result = []

	minValue = table_data_arr[0][row_indexe_arr[0]][0]

	for i in range(1, len(table_data_arr)):
		if table_data_arr[i][row_indexe_arr[i]][0] < minValue:
			minValue = table_data_arr[i][row_indexe_arr[i]][0]

	for j in range(0, len(table_data_arr)):
		if table_data_arr[j][row_indexe_arr[j]][0] == minValue:
			result.append(j)

	return result



#各表中的数据(三维数组[表][行][列])
table_data_arr = []
#各表数据的行指针
row_indexe_arr = []
#表字段名
column_name_arr = []

#取数据库数据
for i in range(0, len(dbs_info)):
	try:
		db = pymysql.connect(dbs_info[i]["db_ip"], dbs_info[i]["db_user"], dbs_info[i]["db_password"], dbs_info[i]["db_name"])
		cursor = db.cursor()
		cursor.execute("select * from %s order by id asc" %dbs_info[i]["table_name"])
		#取第一个表的字段名
		if i == 0:
			dscp = cursor.description
			for column_dscp in dscp:
				column_name_arr.append(column_dscp[0])
		#各表数据放入db_data数组
		table_data_arr.append(cursor.fetchall())
		#各表行指针指向第一行
		row_indexe_arr.append(0)
	except Exception as e:
		print("something wrong when try to execute sql and fetch data!")
	finally:
		db.close()

table_count = len(table_data_arr)
column_count = len(table_data_arr[0][0])

#在每个表表数据最后加上一行id相等的数据，使得最后的一次比较各表的游标（行指针）都正好滑到最后一行了
max_id = table_data_arr[0][len(table_data_arr[0]) - 1][0]
for i in range(1, table_count):
	if table_data_arr[i][len(table_data_arr[i]) - 1][0] > max_id:
		max_id = table_data_arr[i][len(table_data_arr[i]) - 1][0]

for i in range(0, table_count):
	addition_row = []
	if isinstance(max_id, str):
		addition_row.append(max_id + str(1))
	else:
		addition_row.append(max_id + 1)
	# addition_row.append("compare completed %d" %i)
	for j in range(1, column_count):
		addition_row.append("")
	table_data_list = list(table_data_arr[i])
	table_data_list.append(addition_row)
	table_data_arr[i] = table_data_list

wbk = xlwt.Workbook()
sheet = wbk.add_sheet('sheet1')
current_excel_row_num = 0

#设置差异列的样式
font_of_different_data = xlwt.Font()
font_of_different_data.colour_index = 2 #这个2是红色，天啦
style_of_different_data = xlwt.XFStyle()
style_of_different_data.font = font_of_different_data

#设置首行样式
style_of_head_line = xlwt.XFStyle()
font_of_head_line = xlwt.Font()
font_of_head_line.bold = True
style_of_head_line.font = font_of_head_line
alignment_of_head_line = xlwt.Alignment()
alignment_of_head_line.horz = 0x02      # 水平居中??!!
alignment_of_head_line.vert = 0x01      # 垂直居中??!!
style_of_head_line.alignment = alignment_of_head_line

#首行列出字段名
sheet.write(current_excel_row_num, 0, "table_name", style_of_head_line)
for i in range(0, len(column_name_arr)):
	sheet.write(current_excel_row_num, i + 1, column_name_arr[i], style_of_head_line)
current_excel_row_num = current_excel_row_num + 1

#冻结首行首列
sheet.panes_frozen= True
sheet.horz_split_pos= 1
sheet.vert_split_pos= 1

#直到所有表都历遍完它的所有行
while not is_all_arrays_ended(table_data_arr, row_indexe_arr):
	#获取所有有差异的列
	different_colum_indexes = get_columns_having_different_value_between_selected_tables(table_data_arr, row_indexe_arr, range(len(table_data_arr)))
	#如果各表行指针指向的行都有相同的id时(id对齐)
	if 0 not in different_colum_indexes:
		#存在有差异的列时向差异文件中写入差异信息
		if len(different_colum_indexes) > 0:
			for i in range(0, table_count):
				sheet.write(current_excel_row_num, 0, dbs_info[i]["table_name"])
				for j in range(0, column_count):
					#差异列用使用特殊样式便于查看
					if j in different_colum_indexes:
						sheet.write(current_excel_row_num, j + 1, table_data_arr[i][row_indexe_arr[i]][j], style_of_different_data)
					else:
						sheet.write(current_excel_row_num, j + 1, table_data_arr[i][row_indexe_arr[i]][j])
				current_excel_row_num = current_excel_row_num + 1
			#写一个空行
			sheet.write_merge(current_excel_row_num, current_excel_row_num, 0, column_count - 1, '')
			current_excel_row_num = current_excel_row_num + 1

		#所有表行指针加一
		for i in range(0, len(row_indexe_arr)):
			row_indexe_arr[i] = row_indexe_arr[i] + 1
	#没有相同id时意味存在表缺某条记录时，记录相对缺省情况，滑动游标（即行指针）
	else:
		#查找在当前游标下拥有最小id的表，其他表在该id处为缺省，记录一个空行表示缺省，将拥有最小id的表的游标后滑一行
		tables_have_min_id = get_tables_having_min_id(table_data_arr, row_indexe_arr)
		#拥有最小id的表之间对比差异
		different_colum_indexes = get_columns_having_different_value_between_selected_tables(table_data_arr, row_indexe_arr, tables_have_min_id)
		for i in range(0, table_count):
			sheet.write(current_excel_row_num, 0, dbs_info[i]["table_name"])
			if i in tables_have_min_id:
				for j in range(0, column_count):
					#差异列用使用特殊样式便于查看
					if j in different_colum_indexes:
						sheet.write(current_excel_row_num, j + 1, table_data_arr[i][row_indexe_arr[i]][j], style_of_different_data)
					else:
						sheet.write(current_excel_row_num, j + 1, table_data_arr[i][row_indexe_arr[i]][j])
				#最小id的行指针后滑一行
				row_indexe_arr[i] = row_indexe_arr[i] + 1
			current_excel_row_num = current_excel_row_num + 1
		#写一个空行
		sheet.write_merge(current_excel_row_num, current_excel_row_num, 0, column_count - 1, '')
		current_excel_row_num = current_excel_row_num + 1

#保存excel，文件已存在时给文件名后加数字
if not os.path.exists("%s%s" %(comparison_result_excel_name, comparison_result_excel_suffix)):
	wbk.save("%s%s" %(comparison_result_excel_name, comparison_result_excel_suffix))
else:
	file_name_var = 1
	while os.path.exists("%s%d%s" %(comparison_result_excel_name, file_name_var, comparison_result_excel_suffix)):
		file_name_var = file_name_var + 1
	wbk.save("%s%d%s" %(comparison_result_excel_name, file_name_var, comparison_result_excel_suffix))

print("compare completed")
input()
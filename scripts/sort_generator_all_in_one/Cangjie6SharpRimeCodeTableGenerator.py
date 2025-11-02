from gentoolbox import sort_cj6
from io import StringIO
import os
import re
from datetime import datetime
import shutil
import glob
class Cangjie6SharpRimeCodeTableGenerator(object):
	def __init__(self):
		self.cj6_raw_file = open('./cangjie6_sharp.tsv')
		self.cj6_with_num = StringIO()
		self.cj6_sorted = StringIO()
		self.cj6_sorted_traditional_preference = StringIO()
		self.cj6_sorted_simplified_preference = StringIO()
		self.cj6_with_pua = StringIO()
	def generate_rime_table_without_num(self):
		self.remove_ids()
		self.cj6_sorted_traditional_preference = self.sort("C", "Tradional")
		self.cj6_sorted_simplified_preference = self.sort("D", "Simplified")
		self.cj6_sorted = self.sort("B", "General")
		self.write_to_rime_template()
		self.write_to_cj2356_file()
		self.close()
	
	def sort(self, score_type, custom_priority_mode):
		sorter = sort_cj6.Cangjie6CodeTableSort()
		cj6_sorted_temp = StringIO()
		sorter.sort(source = self.cj6_sorted, output = cj6_sorted_temp, score_type = score_type, custom_priority_mode = custom_priority_mode)
		return cj6_sorted_temp

	def write_to_rime_template(self):
		date_str = datetime.now().strftime("%Y%m%d")
		zsymbols_text = self.get_zsymbols()
		zsymbols_without_num_text = self.get_zsymbols_without_num()
		extra_symbols_text = self.get_extra_symbols()
		
		# 定义要生成的目录及对应模板目录和内容
		template_tasks = [
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp_Num",
				"template_glob": "./rime_template/cj6_sharp_num/*.yaml",
				"dict_file": "cangjie6_sharp_num.dict.yaml",
				"content": self.cj6_with_num.getvalue().rstrip('\n') + '\n' + zsymbols_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp/一般排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp/傳統漢字優先排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted_traditional_preference.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp/簡體中文優先排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted_simplified_preference.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp_With_Legacy_Symbols/一般排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text.rstrip('\n') + '\n' + extra_symbols_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp_With_Legacy_Symbols/傳統漢字優先排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted_traditional_preference.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text.rstrip('\n') + '\n' + extra_symbols_text,
			},
			{
				"target_dir": f"RimeData_{date_str}_Cangjie6_Sharp_With_Legacy_Symbols/簡體中文優先排序",
				"template_glob": "./rime_template/cj6_sharp/*.yaml",
				"dict_file": "cangjie6_sharp.dict.yaml",
				"content": self.cj6_sorted_simplified_preference.getvalue().rstrip('\n') + '\n' + zsymbols_without_num_text.rstrip('\n') + '\n' + extra_symbols_text,
			},
			# 将来可以增加其他排序方式，比如繁體優先排序
			# {
			#	 "target_dir": f"RimeData_{date_str}_Cangjie6_Sharp/繁體優先排序",
			#	 "template_glob": "./rime_template/cj6_sharp/*.yaml",
			#	 "dict_file": "cangjie6_sharp.dict.yaml",
			#	 "content": self.cj6_sorted_traditional.getvalue(),
			# },
		]
		
		for task in template_tasks:
			os.makedirs(task["target_dir"], exist_ok=True)
			# 复制模板文件
			for file in glob.glob(task["template_glob"]):
				shutil.copy(file, f"{task['target_dir']}/")
			# 合并模板内容和生成内容
			dict_path = os.path.join(task["target_dir"], task["dict_file"])
			with open(dict_path, "r", encoding="utf8") as f:
				template_content = f.read()
			with open(dict_path, "w", encoding="utf8") as f:
				f.write(template_content + task["content"])

	def get_zsymbols(self):
		with open('./symbols/zsymbols.txt', 'r', encoding = 'utf8') as f:
			return f.read()
	def get_zsymbols_without_num(self):
		with open('./symbols/zsymbols_without_num.txt', 'r', encoding = 'utf8') as f:
			return f.read()
	def get_extra_symbols(self):
		with open('./symbols/symbols_legacy.txt', 'r', encoding = 'utf8') as f:
			return f.read()


	def write_to_cj2356_file(self):
		with open('./2356_cangjie6.txt', 'w', encoding = 'utf8') as output:
			output.write(self.cj6_with_pua.getvalue())

	def remove_ids(self):
		pua_start_point = 0xF0000
		pua_pattern = re.compile(r"ffyp[1,2]")
		self.cj6_raw_file.seek(0)

		for line in self.cj6_raw_file:
			line = line.lower().strip("\n")
			ch, cj6_inner_code, cj6_code, *_ = line.split('\t')

			# cj6_with_num 和 cj6_sorted
			if len(ch) > 1:
				self.cj6_with_num.write(f"□\t{cj6_inner_code}\n")
			else:
				self.cj6_with_num.write(f"{ch}\t{cj6_inner_code}\n")
				self.cj6_sorted.write(f"{ch}\t{cj6_code}\n")

			# cj6_with_pua
			pua_ch = ch
			if len(ch) > 1 or pua_pattern.match(cj6_inner_code):
				pua_ch = chr(pua_start_point)
				pua_start_point += 1
			self.cj6_with_pua.write(f"{pua_ch}\t{cj6_inner_code}\n")
			if re.search(r"[0-9]", cj6_inner_code):
				self.cj6_with_pua.write(f"{pua_ch}\t{cj6_code}\n")
		print("生成的2356_cangjie6.txt含有私用區字符，僅作為倉頡字典2356 For iOS內部使用，以確保查找唯一性，請不要使用它作為您的碼表！請使用文件夾中的Rime碼表作為您的碼表。")

	def close(self):
		self.cj6_raw_file.close()



if __name__ == "__main__":
	generator = Cangjie6SharpRimeCodeTableGenerator()
	generator.generate_rime_table_without_num()

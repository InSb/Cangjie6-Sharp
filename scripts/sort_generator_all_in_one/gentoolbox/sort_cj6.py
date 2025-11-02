#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sort the Cangjie6 code table according to the score function.
"""

__author__ = 'ArthurMcArthur'


import math
class Cangjie6CodeTableSort(object):
	def __init__(self):
		self.simple_freq_dic = {}
		self.traditional_freq_dic = {}
		self.load_freq_tables()
		self.score_func_map = {
			"A": self.score_ch_A, 
			"B": self.score_ch_B, 
			"C": self.score_ch_C, 
			"D": self.score_ch_D, 
		}

	def load_freq_tables(self):
		"""加载简体与繁体字频表"""
		with open('./freq_files/简体字频表.txt', 'r', encoding='utf8') as simple_f, \
			 open('./freq_files/香港字频表.txt', 'r', encoding='utf8') as trad_f:
			for line in simple_f:
				freq_data = line.strip().split('\t')
				self.simple_freq_dic[freq_data[1]] = float(freq_data[3])
			for line in trad_f:
				freq_data = line.strip().split('\t')
				self.traditional_freq_dic[freq_data[1]] = float(freq_data[3])

	def load_table(self, source):
		"""加载待排序的仓颉码表"""
		if isinstance(source, str):
			with open(source, 'r', encoding='utf8') as f:
				lines = f.readlines()
		else:
			source.seek(0)
			lines = source.readlines()
		return [line.strip() for line in lines]

	def build_score_dict(self, table_lines, sort_func):
		"""根据评分函数构建 cjcode -> [(汉字, 分数), ...] 字典"""
		score_dic = {}
		for line in table_lines:
			han_ch, cjcode = line.split('\t')
			score = sort_func(han_ch, self.simple_freq_dic, self.traditional_freq_dic)
			score_dic.setdefault(cjcode, []).append((han_ch, score))
		return score_dic

	def apply_sort(self, score_dic):
		"""对每个编码下的汉字按分数降序排序"""
		for k in score_dic:
			score_dic[k].sort(key=lambda x: x[1], reverse=True)
		return score_dic

	# def write_output(self, score_dic, output_source):
	# 	"""将排序结果写入文件"""
	# 	if isinstance(output_source, str): 
	# 		with open(output_source, 'w', encoding='utf8') as f:
	# 			for k, items in score_dic.items():
	# 				for ch, _ in items:
	# 					f.write(f"{ch}\t{k}\n")
	# 	else:
	# 		for k, items in score_dic.items():
	# 				for ch, _ in items:
	# 					f.write(f"{ch}\t{k}\n")

	def write_output(self, score_dic, output_source):
		"""将排序结果写入文件或 file-like 对象"""
	
		def _write(f):
			for k, items in score_dic.items():
				for ch, _ in items:
					f.write(f"{ch}\t{k}\n")
		
		if isinstance(output_source, str):
			# output_source 是路径，自动打开文件
			with open(output_source, 'w', encoding='utf8') as f:
				_write(f)
		else:
			# output_source 已经是 file-like 对象
			_write(output_source)

	def sort(self, source = "./cj6_official_sort.txt", output = './cj6_freq_sorted.txt', score_type = "B", custom_priority_mode = False):
		"""主排序函数：读取、计算、应用优先级、排序、输出"""
		sort_func = self.score_func_map.get(score_type, self.score_ch_B)
		
		table_lines = self.load_table(source)
		score_dic = self.build_score_dict(table_lines, sort_func)

		if custom_priority_mode:
			score_dic = self.custom_priority_score(score_dic, custom_priority_mode)

		score_dic = self.apply_sort(score_dic)
		self.write_output(score_dic, output)

	def score_ch_A(self, ch, simple_freq_dic, traditional_freq_dic):  # 一般排序評分，A方案
		is_traditional = False
		if ch in traditional_freq_dic:
			is_traditional = True
		if is_traditional == True:
			is_traditional_bonus = 1
		else:
			is_traditional_bonus = 0

		alpha = 0.05
		beta = 0.1

		if (ch in simple_freq_dic) and (ch in traditional_freq_dic):
			ch_freq = max(simple_freq_dic[ch], traditional_freq_dic[ch])
		elif ch in simple_freq_dic:
			ch_freq = simple_freq_dic[ch]
		elif ch in traditional_freq_dic:
			ch_freq = traditional_freq_dic[ch]
		else:
			ch_freq = -ord(ch)

		if ch_freq > 0:
			normalized_freq = math.log(1 + ch_freq)
			return alpha * is_traditional_bonus + beta * normalized_freq
		else:
			return ch_freq


	def score_ch_B(self, ch, simple_freq_dic, traditional_freq_dic):  # 一般排序評分，B方案
		is_traditional = False
		if ch in traditional_freq_dic:
			is_traditional = True
		if is_traditional == True:
			is_traditional_bonus = 1
		else:
			is_traditional_bonus = 0

		alpha = 10
		beta = 0.1

		if (ch in simple_freq_dic) and (ch in traditional_freq_dic):
			ch_freq = max(simple_freq_dic[ch], traditional_freq_dic[ch])
		elif ch in simple_freq_dic:
			ch_freq = simple_freq_dic[ch]
		elif ch in traditional_freq_dic:
			ch_freq = traditional_freq_dic[ch]
		else:
			ch_freq = -ord(ch)

		if ch_freq > 0:
			normalized_freq = math.log(1 + ch_freq)
			return (1 + alpha * is_traditional_bonus) * (beta * normalized_freq)
		else:
			return ch_freq

	def score_ch_C(self, ch, simple_freq_dic, traditional_freq_dic):  # 傳統漢字優先評分
		if (ch in traditional_freq_dic):
			ch_freq = traditional_freq_dic[ch]
		elif (ch in simple_freq_dic):
			ch_freq = 0
		else:
			ch_freq = -ord(ch)
		return ch_freq

	def score_ch_D(self, ch, simple_freq_dic, traditional_freq_dic):  # 簡體中文優先評分
		if (ch in simple_freq_dic):
			ch_freq = simple_freq_dic[ch]
		elif (ch in traditional_freq_dic):
			ch_freq = 0
		else:
			ch_freq = -ord(ch)
		return ch_freq

	def custom_priority_score(self, d, mode):
		if mode == "Traditional": 
			high_score_set = {
				("己", "已"), 
				("犬", "义", "庆"), 
				("久", "欠", "飞"), 
				("文", "头", "达"), 
				("皮", "板"), 
				("尹", "刃", "区"), 
			}
		elif mode == "Simplified": 
			high_score_set = {
				("己", "已"), 
				("犬", "义", "庆"), 
				("久", "欠", "飞"), 
				("文", "头", "达"), 
				("皮", "板"), 
			}
		elif mode == "General":
			high_score_set = {
				("犬", "义", "庆"), 
				("不", "灭", "灰"), 
				("己", "已"), 
				("双", "汉"), 
				("区", "尹", "刃"), 
				("久", "欠", "飞"), 
				("汤", "溺"), 
				("吗", "叼"), 
				("怀", "恢"), 
				("扫", "韦"), 
				("击", "扎"), 
				("麦", "扳"), 
				("皮", "板"), 
				("荚", "莽"), 
				("骞", "寒"), 
				("难", "淮"), 
			}
		else:
			high_score_set = {
				("己", "已"), 
			}

		for cjcode, han_ch_info in d.items():
			han_chars = {ch for ch, _ in han_ch_info}
			for subset in high_score_set:
				if set(subset) <= han_chars:
					n = len(subset)
					high_map = {ch: 999999 - i for i, ch in enumerate(subset)}
					new_lst = []
					for ch, score in han_ch_info:
						if ch in high_map:
							new_lst.append((ch, high_map[ch]))
						else:
							new_lst.append((ch, score))
					d[cjcode] = new_lst
					break
		return d

if __name__ == "__main__":
	sorter = Cangjie6CodeTableSort()
	sorter.sort(score_type = "B", custom_priority_mode = True)

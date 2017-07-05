#encoding: utf-8
import sets
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def intersection(a, b):
	result = []
	for each in a:
		if each in b:
			del b[b.index(each)] #删除，a,b元素一一对应，包含重复元素
			result.append(each)
	return result


"""
遍历句子列表，选出句子中前三个关联度最高的实体，并打分作为后续特征
"""
def entity_link(sentence):
	f1 = open('../data/person_name_list.txt', 'r')
	f2 = open('../data/work_name_list.txt', 'r')

	entity_list = []

	for line in f1:
		entity_list.append(unicode(line.strip()))
	for line in f2:
		entity_list.append(unicode(line.strip()))


	top3_entity = []
	for entity in entity_list:
		if entity == "":
			continue

		share_word = intersection(list(sentence), list(entity))
		share_len = len(share_word) / float(len(entity))

		min_index = 10000
		max_index = -1
		for word in share_word:
			cur_index_min = sentence.index(word) #正序查找
			cur_index_max = sentence.rindex(word) #倒序查找，防止重复元素

			if cur_index_min < min_index:
				min_index = cur_index_min
			if cur_index_min > max_index:
				max_index = cur_index_max
		share_dis = len(share_word) / float(max_index - min_index + 1)
		if len(share_word) == 1:
			share_dis = 0


		score = (share_len + share_dis) / 2
		if len(top3_entity) >= 3:
			for index in range(0,3):
				if score > top3_entity[index][0]:
					top3_entity[index][0] = score
					top3_entity[index][1] = entity
					break
		else:
			top3_entity.append([score, entity])
		


	for entity in top3_entity:
		print "(" + str(entity[1]) + " " + str(entity[0]) + ")"


entity_link(u"大幂幂在三生三世中扮演谁") #传入unicode
"""
(幂幂 1.0)
(大幂幂 1.0)
(三生三世十里桃花 0.75)
"""

entity_link(u"刘德华的父亲是谁") 
"""
(刘德华 1.0)
(父亲 1.0)
(我的父亲 0.875)
"""

entity_link(u"玛丽昂·歌迪亚是谁") 
"""
(玛丽昂·歌迪亚 1.0)
(阿丽玛 0.833333333333)
(玛丽森 0.833333333333)
"""

#其他待补充特征
#实体的多长部分出现在了句子内
#mention能不能被连接到搜索子图里的实体  即句子里的其他实体和子图是否相关

#有BUG  实体出现了多个重复字不好办，不过情况不多。




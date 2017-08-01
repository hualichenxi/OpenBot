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
def EntityLinkingScore(sentence):
	f1 = open('../data/person_name_list.txt', 'r')
	f2 = open('../data/work_name_list.txt', 'r')

	entity_list = []

	#[别名, 别名加括号, 真名, 真名加括号]
	for line in f1:
		names = line.strip().split('\t')
		if len(names) >= 4:
			entity_list.append(names)
	for line in f2:
		names = line.strip().split('\t')
		entity_list.append([names[0], names[1], names[0], names[1]])


	top3_entity = []
	for names in entity_list:
		entity = unicode(names[0])
		if entity == "":
			continue

		share_word = intersection(list(sentence), list(entity))
		if len(share_word) == 0:
			continue

		#重合度
		share_len = len(share_word) / float(len(entity))

		#重合部分的离散度
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

		#重合部分的顺序  相同字都按最小来算
		#三生三世在句子里和实体里排序分别是(4, 4, 5, 7)和(0, 0, 1, 3)，顺序相同，分数为1。
		sentence_indexes = []
		entity_indexes = []
		for word in share_word:
			sentence_indexes.append((word, sentence.index(word)))
			entity_indexes.append((word, entity.index(word)))

		sentence_indexes.sort(key=lambda x:x[1])
		entity_indexes.sort(key=lambda x:x[1]) 

		count = 0
		for index in range(0, len(share_word)):
			if sentence_indexes[index][0] == entity_indexes[index][0]:
				count += 1
		share_order = float(count) / len(share_word)


		score = (share_len + share_dis + share_order) / 3

		"""
		去除映射到相同实体的词，仅更新分数
		"""
		rep = 0
		for index in range(0, len(top3_entity)):
			if names[3] == top3_entity[index][1]:
				if score > top3_entity[index][0]:
					top3_entity[index][0] = score
				rep = 1
				break
		if rep == 1:
			continue

		if len(top3_entity) >= 3:
			for index in range(0,3):
				if score > top3_entity[index][0]:
					top3_entity[index][0] = score
					top3_entity[index][1] = names[3]
					break
		else:
			top3_entity.append([score, entity]) 
		
	for entity in top3_entity:
		print "(" + str(entity[1]) + " " + str(entity[0]) + ")"
	return top3_entity


"""
子图的aggregation节点在问题中的占比
"""
def ConstraintEntityWord(candidate, question):
	aggregation_list = []
	for i in range(1, len(candidate) - 1): #首尾节点不找
		aggregations = candidate[i].aggregations
		for relation, entity in aggregations:
			aggregation_list.append(entity.name)

	score = 0
	for aggregation in aggregation_list:
		share_word = intersection(list(aggregation), list(question))
		score += len(share_word) / float(len(entity))

	score /= len(aggregation_list)

	return score

"""
子图的aggregation的实体节点是否能链接到知识库
"""
def ConstraintEntityInQ(candidate, question):
	entity_list = []
	aggregation_list = []

	top3_entity = EntityLinkingScore(question)  #这里改成top4比较好？第一个不算
	for entity in top3_entity:
		entity_list.append(entity[0])

	score = 0
	for i in range(1, len(candidate) - 1):
		aggregations = candidate[i].aggregations
		for relation, entity in aggregations:
			if entity.is_aggr == True:
				aggregation_list.append(entity.name)

	for aggregation in aggregation_list:
		if aggregation in entity_list:
			score += 1

	score /= float(len(aggregation_list))
	return score



EntityLinkingScore(u"大幂幂在三生三世中扮演谁") #传入unicode
"""
(杨幂 1.0)
(三生三世十里桃花 0.833333333333)
(学院传说之三生三世桃花缘 0.777777777778)
"""

EntityLinkingScore(u"刘德华的父亲是谁") 
"""
(刘德华 1.0)
(父亲 1.0)
(我的父亲 0.916666666667)
"""

EntityLinkingScore(u"玛丽昂·歌地亚是谁") 
"""
(玛丽昂·歌迪亚 0.904761904762)
(歌者森 0.888888888889)
(玛丽娜 0.888888888889)
"""

#其他待补充特征
#实体的多长部分出现在了句子内
#mention能不能被连接到搜索子图里的实体  即句子里的其他实体和子图是否相关

#有BUG  实体出现了多个重复字不好办，不过情况不多。




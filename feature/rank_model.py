#encoding: utf-8
import sets
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import os
import extract_features

def generate_candidates(qid, question):
	all_candidates = []
	top3_entity = EntityLinkingScore(question) #(实体，score)
	for entity in top3_entity:
		candidates = generate_core_chain(entity[0]) #旦龙的函数，返回的子图数据结构需要对接
		for candidate in candidates:
			res_entity = candidate.get_last_node()[1].name #(actor, x)  最终答案节点
			feature_1 = entity[1]  #当前实体的分数
			feature_2 = PatChain(candidate) #师兄写的函数，核心链score
			feature_3 = ConstraintEntityWord(candidate, question) #aggregation出现在句中的比重
			feature_4 = ConstraintEntityInQ(candidate, question) #aggregation中的实体类能链接到知识库的比重
			feature_5 = candidate.get_node_num() #子图有多少节点
			feature_6 = len(candidates) #一共返回了几个候选子图
			feature_str = "1:" + str(feature_1) + " 2:" + str(feature_2) + " 3:" + str(feature_3) \
						+ " 4:" + str(feature_4) + " 5:" + str(feature_4) + " 6:" + str(feature_4) + "\n"
			candidate_str = "qid:" + qid + " " + feature_str
			all_candidates.append(candidate_str, res_entity)
	return all_candidates


	"""
	qid:1 1:1 2:1 3:0 4:0.2 # 候选图1
	qid:1 1:0 2:0 3:1 4:0.1 # 候选图2
	qid:1 1:0 2:1 3:0 4:0.4 # 候选图3
	qid:1 1:0 2:0 3:1 4:0.3 # 候选图4
	"""


def generate_label_data(qid, question):
	train = open('train.txt', 'w')
	all_candidates = generate_candidates(qid, question)
	for candidates in all_candidates:
		train.write("0 " + candidates[0] + "# " + candidates[1])
		train.writes("\n")

	#然后自己手动打标啊，增加第一列排序

def train():
	#train.txt 已经打标好的
	os.system('java -jar bin/RankLib.jar -train train.txt -save mymodel.txt')

def train_and_validate():
	#cross-calidation
	os.system('java -jar bin/RankLib.jar -kcv 5 -kcvmc models/ -kcvmn ca -metric2t NDCG@10 -metric2T ERR@10 -train train.txt -save mymodel.txt')
	#直接得出validation上评测的结果

	
def evaluate(question):
	test = open('test.txt', 'w')
	all_candidates = generate_candidates(0, question)
	for candidates in all_candidates:
		test.write("0 " + candidates[0] + "# " + candidates[1])
		test.writes("\n")

	os.system('java -jar bin/RankLib.jar -load mymodel.txt -rank test.txt -score myscorefile.txt')

	#把最高分和res_entity对上
	f = open('myscorefile.txt', 'r')
	scores = []
	count = 0
	for line in f:
		scores.append([line.split('\t')[2], all_candidates[count][1]])
		count += 1

	scores.sort(key=lambda x:x[0])

	print scores[0]

	#刘恺威
	"""
	1	0	1.7064098119735718	# 刘恺威
	1	1	-2.13559889793396	# 小糯米
	1	2	1.5903208255767822	# 赵又廷
	1	3	0.6610940098762512	# 刘诗诗
	"""




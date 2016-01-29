import numpy as np
from math import log
from itertools import islice
import csv

def get_entropy(data_set):
    labels_count = {}
    record_nums = len(data_set)
    for data in data_set:
        label = data[-1]
        labels_count[label] = labels_count.get(label, 0) + 1
    entropy = 0.0
    for key in labels_count:
        p = float(labels_count[key])/record_nums
        entropy -= p*log(p,2)
    return  entropy

def get_conditional_entropy(branch_dict,total_record_nums):
    entropy = 0.0
    for feature_value in branch_dict.keys():
        p = float(len(branch_dict[feature_value]))/total_record_nums
        entropy += p*get_entropy(branch_dict[feature_value])
    return entropy

def create_tree(date_sets, feature_labels):
    labels = [list[-1] for list in date_sets]
    labels_set = set(labels)
    if len(labels_set) == 1:
        return labels_set.pop()
    feature_num = len(date_sets[0])-1
    if feature_num == 1:
        return get_most_common_value(labels)
    entropy_oringal = get_entropy(date_sets)
    record_nums = len(date_sets)
    information_gain = 0.0
    best_information_gain = 0.0
    best_feature_index = 0.0
    best_brahcn_dict = {}
    for index in range(0,feature_num):
        branch_dict = get_branch_sets(date_sets,index)
        entropy_condition = get_conditional_entropy(branch_dict,record_nums)
        information_gain = entropy_oringal - entropy_condition
        if(information_gain>best_information_gain):
            best_information_gain = information_gain
            best_feature_index = index
            best_brahcn_dict = branch_dict
    if 0 == information_gain:
        return get_most_common_value(labels)
    feature = feature_labels[best_feature_index]
    del(feature_labels[best_feature_index])
    tree_node = {}
    for feature_value in best_brahcn_dict.keys():
        tree_node[feature_value] = create_tree(best_brahcn_dict[feature_value], feature_labels[:])
    tree = {}
    tree[feature] = tree_node
    return tree

def search_tree(tree, feature_labels, test_data):
    feature = tree.keys()[0]
    feature_index = feature_labels.index(feature)
    sub_tree = tree[feature][test_data[feature_index]]
    if isinstance(sub_tree, dict):
        return search_tree(sub_tree, feature_labels, test_data)
    else :
        return sub_tree

def get_most_common_value(list):
    count_dict = {}
    for label in list:
        count_dict[label] = count_dict.get(label,0) + 1
    keys = count_dict.keys()
    temp = keys[0]
    for key in keys:
        if count_dict[key] > count_dict[temp]:
            temp = key
    return temp

def get_branch_sets(data_set,feature_index):
    branch_sets = []
    branch_dict = {}
    for record in data_set:
        value = record[feature_index]
        if value not in branch_dict:
            branch_dict[value] = []
        new_record = record[0:feature_index]
        new_record.extend(record[feature_index+1:])
        branch_dict[value].append(new_record)
    for key in branch_dict.keys():
        branch_sets.append(branch_dict[key])
    return branch_dict

def classcify_bench(train_set, feature_labels, test_data_set):
    result = []
    print "creating tree..."
    tree = create_tree(train_set, feature_labels[:])
    print "classifing tree..."
    for test_data in test_data_set:
        result.append(search_tree(tree,feature_labels, test_data))
    return result

def discretize_dataset(data_set,splite_value_dict):
    num_features = len(data_set[0]) - 1
    for i in range(num_features):
        for j in range(len(data_set)):
            if(data_set[j][i]<splite_value_dict[i]):
                data_set[j][i] = 0
            else:
                data_set[j][i] = 1

def split_data_set(data_set,feature_index,value):
    samller_set = []
    bigger_set = []
    for data in data_set:
        new_record = data[:feature_index]
        new_record.extend(data[feature_index+1:])
        if data[feature_index] >= value:
            bigger_set.append(new_record)
        else:
            samller_set.append(new_record)
    return samller_set,bigger_set

def get_discretize_splite_value_dict(data_set,clip_count = 2):
    best_splite_value_dict = {}
    features_num = len(data_set[0]) - 1
    record_num = len(data_set)
    entropy_oringinal = get_entropy(data_set)
    for index in range(0,features_num):
        print "caluting the " + str(index) + " th feathre splite point"
        best_information_gain = 0.0
        values = [record[index] for record in data_set]
        values_set = set(values)
        values_list = list(values_set)
        values_num = len(values_list)
        distance = values_num/clip_count
        if clip_count > values_num:
            distance = 1
            clip_count = values_num
        splite_index = -1
        for clip_times in range(0,clip_count):
            splite_index += distance
            splite_value = values_list[splite_index]
            set1,set2 = split_data_set(data_set, index, splite_value)
            entropy_conditional = get_conditional_entropy({"set1":set1,"set2":set2},record_num)
            infomation_gain = entropy_oringinal - entropy_conditional
            if infomation_gain > best_information_gain:
                best_information_gain = infomation_gain
                best_splite_value_dict[index] = splite_value
    return best_splite_value_dict

#///////////////////////////////////////////////////////////////////////////

def lod_csv_file_dt(path):
    data_set = []
    labels = []
    csvfile = file(path,'rb')
    reader = csv.reader(csvfile)
    index = 0
    for line in reader:
        if(0==index):
            labels.extend(line[:-1])
        else:
            line =  map(float,line)
            data_set.append(line)
        index = index+1
    return data_set, labels

def write_list(list,path):
    f=file(path,"w+")
    for value in list:
        f.writelines(str(value)+"\n")
    f.close()

def run():
    data__set_path = "lab5/Datac_all.csv"
    result_path = "lab5/dt_result.txt"
    train_num = 27751
    data_list,feature_labels = lod_csv_file_dt(data__set_path)
    print "calculating splite points..."
    splite_value_dict = get_discretize_splite_value_dict(data_list[:train_num],20)
    discretize_dataset(data_list,splite_value_dict)
    result = classcify_bench(data_list[:train_num], feature_labels, data_list[train_num:])
    print "finish"
    write_list(result,result_path)

run()
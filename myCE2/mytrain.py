import argparse
import csv
import queue
import time
import os

import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader

from myCE2.mymscn.myDB import get_model_info, get_models_dnv_vals, get_db_column_min_max_dnv_vals
from myCE2.mymscn.myparser import split_sqlArr_to_access_sqlJsons, sqlJson_to_sqlArr
from mymscn.myutil import *
from mymscn.mydata import get_model_datasets, load_model_data
from mymscn.mynn import my_nn


def unnormalize_torch(labels_norm, min_val, max_val, model_dnv_vals):
    card_norm = labels_norm[:, 0:1]
    dnv_norm = labels_norm[0:, 1:]

    # card_norm = np.array(card_norm, dtype=np.float32)
    cards = (card_norm * (max_val - min_val)) + min_val
    cards = torch.exp(cards)

    dnvs = dnv_norm * torch.log(torch.tensor(model_dnv_vals))
    dnvs = torch.exp(dnvs)

    result = torch.cat([cards, dnvs], dim=1)
    return result


def qerror_loss(preds, targets, min_val, max_val, column_dnv):
    qerror = []
    preds = unnormalize_labels(preds, min_val, max_val, column_dnv)
    targets = unnormalize_labels(targets, min_val, max_val, column_dnv)

    max = torch.maximum(preds, targets)
    min = torch.minimum(preds, targets)

    rate = torch.mean(max / min)
    return rate
    # for i in range(len(targets)):
    #     if (preds[i] > targets[i]).cpu().data.numpy()[0]:
    #         qerror.append(preds[i] / targets[i])
    #     else:
    #         qerror.append(targets[i] / preds[i])
    # return torch.mean(torch.cat(qerror))


def predict(n_network, data_loader, cuda):
    preds = []
    t_total = 0.

    n_network.eval()
    for batch_idx, data_batch in enumerate(data_loader):

        samples, predicates, joins, targets, sample_masks, predicate_masks, join_masks = data_batch

        if cuda:
            samples, predicates, joins, targets = samples.cuda(), predicates.cuda(), joins.cuda(), targets.cuda()
            sample_masks, predicate_masks, join_masks = sample_masks.cuda(), predicate_masks.cuda(), join_masks.cuda()
        samples, predicates, joins, targets = Variable(samples), Variable(predicates), Variable(joins), Variable(
            targets)
        sample_masks, predicate_masks, join_masks = Variable(sample_masks), Variable(predicate_masks), Variable(
            join_masks)

        t = time.time()
        outputs = n_network(samples, predicates, joins, sample_masks, predicate_masks, join_masks)
        t_total += time.time() - t

        for i in range(outputs.data.shape[0]):
            preds.append(outputs.data[i].numpy().tolist())

    return torch.tensor(preds), t_total
    # return outputs, t_total


def print_qerror(preds_unnorm, labels_unnorm):
    qerror = []

    max_unnorm = torch.maximum(preds_unnorm, labels_unnorm)
    min_unnorm = torch.minimum(preds_unnorm, labels_unnorm)

    for i in range(len(min_unnorm)):
        max_item = max_unnorm[i]
        min_item = min_unnorm[i]
        err = torch.mean(max_item / min_item)

        qerror.append(err)

    print("Median: {}".format(np.median(qerror)))
    print("90th percentile: {}".format(np.percentile(qerror, 90)))
    print("95th percentile: {}".format(np.percentile(qerror, 95)))
    print("99th percentile: {}".format(np.percentile(qerror, 99)))
    print("Max: {}".format(np.max(qerror)))
    print("Mean: {}".format(np.mean(qerror)))


# 读取模型的相关配置
global_modelConfigInfo = get_model_info()
global_column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()
global_model_dnv_vals = get_models_dnv_vals()


# 构建和训练神经网络模型
def model_construct_and_train(num_queries_percent, num_epochs, batch_size, hid_units, cuda):

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    modelDataPath = './data/model_train_data'
    modelFiles = os.listdir(modelDataPath)  # 采用listdir来读取所有文件
    modelFiles.sort()  # 排序

    # 读取模型的相关配置
    modelConfigInfo = get_model_info()
    column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()
    models_properties_dnv_vals = get_models_dnv_vals()
    num_materialized_samples = 1000

    models = {}
    i = 0
    for modelFileName in modelFiles:
        # 循环读取每个文件名

        if i > 1:
            break
        # i = i + 1

        modelFilePath = modelDataPath + '/' + modelFileName
        model_name = os.path.basename(modelFilePath).split('.')[0]

        print("-----------------------------------------------------model: %s construct start" % model_name)

        model_column_dnv_vals = models_properties_dnv_vals[model_name]
        model_column_dnv_list = [model_column_dnv_vals[key] for key in model_column_dnv_vals]

        # Load training and validation data
        dicts, \
        model_card_max_val, \
        model_card_min_val, \
        labels_train, \
        labels_test, \
        max_num_joins, \
        max_num_predicates, \
        train_data, \
        test_data \
            = get_model_datasets(
            modelFilePath,
            model_column_dnv_vals,
            column_min_max_dnv_vals,
            num_queries_percent,
            num_materialized_samples)

        table2vec, column2vec, op2vec, join2vec = dicts

        modelData = {
            'dists': {
                'table2vec': table2vec,
                'column2vec': column2vec,
                'op2vec': op2vec,
                'join2vec': join2vec
                },
            'card_max': model_card_max_val,
            'card_min': model_card_min_val,
            'train_data': train_data,
            'train_label': labels_train,
            'test_data': test_data,
            'test_label': labels_test,
            'model_column_dnv': model_column_dnv_list
        }

        # 神经网络结构
        sample_feats_num = len(table2vec)
        predicate_feats_num = len(column2vec) + len(op2vec) + 1
        join_feats_num = len(join2vec)
        label_units_num = len(model_column_dnv_list) + 1
        n_network = my_nn(sample_feats_num, predicate_feats_num, join_feats_num, label_units_num, hid_units)
        optimizer = torch.optim.Adam(n_network.parameters(), lr=0.005)

        model = {
            'model_name': model_name,
            'model_data': modelData,
            'model_n_networl': n_network,
            'model_n_network_opt': optimizer
        }

        models[model_name] = model

        print("-----------------------------------------------------model: %s construct end" % model_name)

    for model_name in models.keys():

        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++ model: %s train start" % model_name)

        model = models[model_name]

        if cuda:
            model.cuda()

        train_data = model['model_data']['train_data']
        labels_train = torch.from_numpy(model['model_data']['train_label'])

        test_data = model['model_data']['test_data']
        labels_test = torch.from_numpy(model['model_data']['test_label'])

        train_data_loader = DataLoader(train_data, batch_size=batch_size)
        test_data_loader = DataLoader(test_data, batch_size=batch_size)

        n_network = model['model_n_networl']
        n_network_opt = model['model_n_network_opt']

        card_min = model['model_data']['card_min']
        card_max = model['model_data']['card_max']

        column_dnv = model['model_data']['model_column_dnv']
        n_network.train()
        for epoch in range(num_epochs):
            loss_total = 0.

            for batch_idx, data_batch in enumerate(train_data_loader):

                samples, predicates, joins, targets, sample_masks, predicate_masks, join_masks = data_batch

                if cuda:
                    samples, predicates, joins, targets = samples.cuda(), predicates.cuda(), joins.cuda(), targets.cuda()
                    sample_masks, predicate_masks, join_masks = sample_masks.cuda(), predicate_masks.cuda(), join_masks.cuda()
                samples, predicates, joins, targets = Variable(samples), Variable(predicates), Variable(
                    joins), Variable(
                    targets)
                sample_masks, predicate_masks, join_masks = Variable(sample_masks), Variable(predicate_masks), Variable(
                    join_masks)

                n_network_opt.zero_grad()
                outputs = n_network(samples, predicates, joins, sample_masks, predicate_masks, join_masks)
                loss = qerror_loss(outputs, targets.float(), card_min, card_max, column_dnv)
                loss_total += loss.item()
                loss.backward()
                n_network_opt.step()

            print("Epoch {}, loss: {}".format(epoch, loss_total / len(train_data_loader)))

        # Get final training and validation set predictions
        preds_train, t_total = predict(n_network, train_data_loader, cuda)
        print("Prediction time per training sample: {}".format(t_total / len(labels_train) * 1000))

        preds_test, t_total = predict(n_network, test_data_loader, cuda)
        print("Prediction time per validation sample: {}".format(t_total / len(labels_test) * 1000))

        # Unnormalize
        preds_train_unnorm = unnormalize_labels(preds_train, card_min, card_max, column_dnv)
        labels_train_unnorm = unnormalize_labels(labels_train, card_min, card_max, column_dnv)

        preds_test_unnorm = unnormalize_labels(preds_test, card_min, card_max, column_dnv)
        labels_test_unnorm = unnormalize_labels(labels_test, card_min, card_max, column_dnv)

        # Print metrics
        print("\nQ-Error training set:")
        print_qerror(preds_train_unnorm, labels_train_unnorm)

        print("\nQ-Error validation set:")
        print_qerror(preds_test_unnorm, labels_test_unnorm)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++ model: %s train end" % model_name)

    return models


# 预测一行已存在对应模型的sql的基数
def predict_access_sqlArr(sqlArr_str, tar_model):
    sqlArr = sqlArr_str.split('#')
    model_name = tar_model['model_name']
    model_tables_str = sqlArr[0]
    joins_str = sqlArr[1]
    predicates_str = sqlArr[2]
    # card_and_dnv_str = sqlArr[3]

    model_nn = tar_model['model_n_networl']
    min_val = tar_model['model_data']['card_min']
    max_val = tar_model['model_data']['card_max']

    table2vec, column2vec, op2vec, join2vec = tuple(
        tar_model['model_data']['dists'][key] for key in tar_model['model_data']['dists'])

    samples_vec, samples_mask = encode_row_samples(model_tables_str, [], table2vec)
    predicates_vec, predicates_mask, joins_vec, joins_mask = encode_row_data(predicates_str, joins_str,
                                                                             global_column_min_max_dnv_vals, column2vec,
                                                                             op2vec, join2vec)

    model_nn.zero_grad()
    outputs = model_nn(samples_vec, predicates_vec, joins_vec, samples_mask, predicates_mask, joins_mask)

    predict_card_dnv = unnormalize_row_outputs(outputs, min_val, max_val, list(global_model_dnv_vals[model_name].values()))
    predict_row_result = predict_card_dnv.detach().numpy().tolist()

    card = predict_row_result[0]
    properties_dnv = {}
    model_column_properties = global_modelConfigInfo[model_name]['properties']
    for i, column_properties in enumerate(model_column_properties):
        properties_dnv[column_properties] = predict_row_result[i+1]
    return card, properties_dnv


# train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)
def train_and_predict(test_file_name, num_queries_percent, num_epochs, batch_size, hid_units, cuda):
    """
    workload_name:训练集
    num_queries:查询数量
    num_epochs:迭代次数
    batch_size:每批数量
    hid_units:隐藏层单元数量
    cuda:是否启用cuda
    """

    tables_model_map = {}
    for key in global_modelConfigInfo:
        tables_model_map[','.join(global_modelConfigInfo[key]['table'])] = key

    models = model_construct_and_train(num_queries_percent, num_epochs, batch_size, hid_units, cuda)

    predict_result = []

    # Load test data
    file_name = "data/model_test_data/" + test_file_name + ".csv"
    with open(file_name, 'r') as f:
        for row_str in f:
            row = row_str.split('#')
            print(row)
            model_tables_str = row[0]
            true_card = row[3].split(',')[0]
            if model_tables_str in tables_model_map.keys() and tables_model_map[model_tables_str] in models.keys():
                model_name = tables_model_map[model_tables_str]
                tar_model = models[model_name]
                card, _ = predict_access_sqlArr(row_str, tar_model)
                predict_result.append('%s,%s' % (card, true_card))
            else:
                access_sqlJsons = split_sqlArr_to_access_sqlJsons(row_str)
                # print(access_sqlJsons)
                ele_queue = queue.Queue()
                for key in access_sqlJsons:
                    access_sqlJson = access_sqlJsons[key]
                    access_sqlArr = sqlJson_to_sqlArr(access_sqlJson)
                    access_sqlArr_tables_str = access_sqlArr.split('#')[0]
                    model_name = tables_model_map[access_sqlArr_tables_str]
                    tar_model = models[model_name]
                    card, column_dnv = predict_access_sqlArr(access_sqlArr, tar_model)

                    connect_keys = {}
                    joins = access_sqlJson['exports']
                    for join_str in joins:
                        join_columns = join_str.split('=')
                        left_column = join_columns[0]
                        right_column = join_columns[1]
                        if left_column in column_dnv.keys():
                            connect_keys[join_str] = column_dnv[left_column]
                        else:
                            connect_keys[join_str] = column_dnv[right_column]

                    element = {
                        'card': card,
                        'joins': joins,
                        'connect_keys': connect_keys
                    }
                    ele_queue.put(element)
                # print(ele_queue)
                first_ele = ele_queue.get()
                while not ele_queue.empty():
                    tmp_ele = ele_queue.get()
                    if first_ele['joins'].isdisjoint(tmp_ele['joins']):
                        ele_queue.put(tmp_ele)
                        continue
                    else:
                        intersection_joins = first_ele['joins'].intersection(tmp_ele['joins'])
                        intersection_join_str = intersection_joins.pop()
                        new_joins = first_ele['joins'].symmetric_difference(tmp_ele['joins'])

                        first_dnv = first_ele['connect_keys'].pop(intersection_join_str)
                        tmp_dnv = tmp_ele['connect_keys'].pop(intersection_join_str)

                        new_connect_keys = dict()
                        new_connect_keys.update(first_ele['connect_keys'])
                        new_connect_keys.update(tmp_ele['connect_keys'])


                        first_card = first_ele['card']
                        tmp_card = tmp_ele['card']
                        new_card = (first_card*tmp_card) / max(first_dnv, tmp_dnv)

                        first_ele = {
                            'card': new_card,
                            'joins': new_joins,
                            'connect_keys': new_connect_keys
                        }
                predict_result.append('%s,%s' % (first_ele['card'], true_card))

    # Print metrics
    print("\nQ-Error " + test_file_name + ":")
    # Write predictions
    file_name = "results/predictions_" + test_file_name + "_" + str(int(time.time())) + ".csv"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        for card_result in predict_result:
            f.write("%s\n" % card_result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--testset", help="synthetic, scale, or job-light", type=str, default='test_last')
    parser.add_argument("--queries", help="percent of training queries (default: 0.9)", type=float, default=0.9)
    parser.add_argument("--epochs", help="number of epochs (default: 100)", type=int, default=100)
    parser.add_argument("--batch", help="batch size (default: 1024)", type=int, default=300)
    parser.add_argument("--hid", help="number of hidden units (default: 256)", type=int, default=256)
    parser.add_argument("--cuda", help="use CUDA", action="store_true")
    args = parser.parse_args()
    train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)


if __name__ == "__main__":
    main()

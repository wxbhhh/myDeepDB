import argparse
import time
import os

import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader

from mymscn.myutil import *
from mymscn.mydata import get_model_datasets, get_models_dnv_vals, get_db_column_min_max_dnv_vals
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
def get_model_info():
    modelConfigInfo = {}
    modelConfigPath = './data/model_config.csv'
    with open(modelConfigPath, 'r') as modelConfigFile:
        for row in modelConfigFile:
            lineArr = row.split(',')
            modelName = lineArr[1]
            modelIndex = lineArr[0]
            modelTables = lineArr[2].split('#')
            modelProperties = lineArr[3].strip().split('#')

            model = {'index': modelIndex, 'table': modelTables, 'properties': modelProperties}
            modelConfigInfo[modelName] = model
    return modelConfigInfo

# 构建和训练神经网络模型
def model_construct_and_train(num_queries_percent, num_epochs, batch_size, hid_units, cuda):

    timeStamp = time.strftime("%Y%m%d%H%M%S")
    modelDataPath = './data/model_data'
    modelFiles = os.listdir(modelDataPath)  # 采用listdir来读取所有文件
    modelFiles.sort()  # 排序

    # 读取模型的相关配置
    modelConfigInfo = get_model_info()
    column_min_max_dnv_vals = get_db_column_min_max_dnv_vals()
    model_dnv_vals = get_models_dnv_vals()
    num_materialized_samples = 1000

    models = {}
    i = 0
    for modelFileName in modelFiles:
        # 循环读取每个文件名

        if i > 0:
            break
        # i = i + 1

        modelFilePath = modelDataPath + '/' + modelFileName
        model_name = os.path.basename(modelFilePath).split('.')[0]

        print("-----------------------------------------------------model: %s construct start" % model_name)

        model_column_dnv_vals = model_dnv_vals[model_name]

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
            'dists': dicts,
            'card_max': model_card_max_val,
            'card_min': model_card_min_val,
            'train_data': train_data,
            'train_label': labels_train,
            'test_data': test_data,
            'test_label': labels_test,
            'model_column_dnv': model_column_dnv_vals
        }

        # 神经网络结构
        sample_feats_num = len(table2vec)
        predicate_feats_num = len(column2vec) + len(op2vec) + 1
        join_feats_num = len(join2vec)
        label_units_num = len(model_column_dnv_vals) + 1
        n_network = my_nn(sample_feats_num, predicate_feats_num, join_feats_num, label_units_num, hid_units)
        optimizer = torch.optim.Adam(n_network.parameters(), lr=0.001)

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


# train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)
def train_and_predict(workload_name, num_queries_percent, num_epochs, batch_size, hid_units, cuda):
    """
    workload_name:训练集
    num_queries:查询数量
    num_epochs:迭代次数
    batch_size:每批数量
    hid_units:隐藏层单元数量
    cuda:是否启用cuda
    """

    models = model_construct_and_train(num_queries_percent, num_epochs, batch_size, hid_units, cuda)

    # Load test data
    file_name = "workloads/" + workload_name
    joins, predicates, tables, samples, label = load_data(file_name, num_materialized_samples)

    # Get feature encoding and proper normalization
    samples_test = encode_samples(tables, samples, table2vec)
    predicates_test, joins_test = encode_data(predicates, joins, column_min_max_vals, column2vec, op2vec, join2vec)
    labels_test, _, _ = normalize_labels(label, min_val, max_val)

    print("Number of test samples: {}".format(len(labels_test)))

    max_num_predicates = max([len(p) for p in predicates_test])
    max_num_joins = max([len(j) for j in joins_test])

    # Get test set predictions
    test_data = make_dataset(samples_test, predicates_test, joins_test, labels_test, max_num_joins, max_num_predicates)
    test_data_loader = DataLoader(test_data, batch_size=batch_size)

    preds_test, t_total = predict(model, test_data_loader, cuda)
    print("Prediction time per test sample: {}".format(t_total / len(labels_test) * 1000))

    # Unnormalize
    preds_test_unnorm = unnormalize_labels(preds_test, min_val, max_val)

    # Print metrics
    print("\nQ-Error " + workload_name + ":")
    print_qerror(preds_test_unnorm, label)

    # Write predictions
    file_name = "results/predictions_" + workload_name + "_" + str(int(time.time())) + "_m.csv"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        for i in range(len(preds_test_unnorm)):
            f.write(str(preds_test_unnorm[i]) + "," + label[i] + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--testset", help="synthetic, scale, or job-light", type=str, default='synthetic')
    parser.add_argument("--queries", help="percent of training queries (default: 0.9)", type=float, default=0.9)
    parser.add_argument("--epochs", help="number of epochs (default: 10)", type=int, default=10)
    parser.add_argument("--batch", help="batch size (default: 1024)", type=int, default=1024)
    parser.add_argument("--hid", help="number of hidden units (default: 256)", type=int, default=256)
    parser.add_argument("--cuda", help="use CUDA", action="store_true")
    args = parser.parse_args()
    train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)


if __name__ == "__main__":
    main()

import argparse
import pickle
import time
import os

import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader

from mscn.util import *
from mscn.data import get_train_datasets, load_data, make_dataset
from mscn.model import SetConv


def unnormalize_torch(vals, min_val, max_val):
    vals = (vals * (max_val - min_val)) + min_val
    return torch.exp(vals)


def qerror_loss(preds, targets, min_val, max_val):
    qerror = []
    preds = unnormalize_torch(preds, min_val, max_val)
    targets = unnormalize_torch(targets, min_val, max_val)

    for i in range(len(targets)):
        if (preds[i] > targets[i]).cpu().data.numpy()[0]:
            qerror.append(preds[i] / targets[i])
        else:
            qerror.append(targets[i] / preds[i])
    return torch.mean(torch.cat(qerror))


def predict(model, data_loader, cuda):
    preds = []
    t_total = 0.

    model.eval()
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
        outputs = model(samples, predicates, joins, sample_masks, predicate_masks, join_masks)
        t_total += time.time() - t

        for i in range(outputs.data.shape[0]):
            preds.append(outputs.data[i])

    return preds, t_total


def print_qerror(preds_unnorm, labels_unnorm):
    qerror = []
    for i in range(len(preds_unnorm)):
        if preds_unnorm[i] > float(labels_unnorm[i]):
            qerror.append(preds_unnorm[i] / float(labels_unnorm[i]))
        else:
            qerror.append(float(labels_unnorm[i]) / float(preds_unnorm[i]))

    print("Median: {}".format(np.median(qerror)))
    print("90th percentile: {}".format(np.percentile(qerror, 90)))
    print("95th percentile: {}".format(np.percentile(qerror, 95)))
    print("99th percentile: {}".format(np.percentile(qerror, 99)))
    print("Max: {}".format(np.max(qerror)))
    print("Mean: {}".format(np.mean(qerror)))


def model_train(num_queries, num_epochs, batch_size, hid_units, cuda):
    """
        num_queries:查询数量
        num_epochs:迭代次数
        batch_size:每批数量
        hid_units:隐藏层单元数量
        cuda:是否启用cuda
    """
    # Load training and validation data
    num_materialized_samples = 1000
    # num_materialized_samples = 0
    dicts, \
    column_min_max_vals, \
    min_val, \
    max_val, \
    labels_train, \
    labels_test, \
    max_num_joins, \
    max_num_predicates, \
    train_data, \
    test_data \
        = get_train_datasets(num_queries, num_materialized_samples)
    table2vec, column2vec, op2vec, join2vec = dicts

    # Train model
    # sample_feats = len(table2vec) + num_materialized_samples
    sample_feats = len(table2vec)
    predicate_feats = len(column2vec) + len(op2vec) + 1
    join_feats = len(join2vec)

    nn = SetConv(sample_feats, predicate_feats, join_feats, hid_units)

    optimizer = torch.optim.Adam(nn.parameters(), lr=0.0005)

    if cuda:
        nn.cuda()

    train_data_loader = DataLoader(train_data, batch_size=batch_size)
    test_data_loader = DataLoader(test_data, batch_size=batch_size)

    nn.train()
    for epoch in range(num_epochs):
        loss_total = 0.

        for batch_idx, data_batch in enumerate(train_data_loader):

            samples, predicates, joins, targets, sample_masks, predicate_masks, join_masks = data_batch

            if cuda:
                samples, predicates, joins, targets = samples.cuda(), predicates.cuda(), joins.cuda(), targets.cuda()
                sample_masks, predicate_masks, join_masks = sample_masks.cuda(), predicate_masks.cuda(), join_masks.cuda()
            samples, predicates, joins, targets = Variable(samples), Variable(predicates), Variable(joins), Variable(
                targets)
            sample_masks, predicate_masks, join_masks = Variable(sample_masks), Variable(predicate_masks), Variable(
                join_masks)

            optimizer.zero_grad()
            outputs = nn(samples, predicates, joins, sample_masks, predicate_masks, join_masks)
            loss = qerror_loss(outputs, targets.float(), min_val, max_val)
            loss_total += loss.item()
            loss.backward()
            optimizer.step()

        print("Epoch {}, loss: {}".format(epoch, loss_total / len(train_data_loader)))

    # Get final training and validation set predictions
    preds_train, t_total = predict(nn, train_data_loader, cuda)
    print("Prediction time per training sample: {}".format(t_total / len(labels_train) * 1000))

    preds_test, t_total = predict(nn, test_data_loader, cuda)
    print("Prediction time per validation sample: {}".format(t_total / len(labels_test) * 1000))

    # Unnormalize
    preds_train_unnorm = unnormalize_labels(preds_train, min_val, max_val)
    labels_train_unnorm = unnormalize_labels(labels_train, min_val, max_val)

    preds_test_unnorm = unnormalize_labels(preds_test, min_val, max_val)
    labels_test_unnorm = unnormalize_labels(labels_test, min_val, max_val)

    # Print metrics
    print("\nQ-Error training set:")
    print_qerror(preds_train_unnorm, labels_train_unnorm)

    print("\nQ-Error validation set:")
    print_qerror(preds_test_unnorm, labels_test_unnorm)
    print("")

    model = {
        'nn': nn,
        'num_materialized_samples': num_materialized_samples,
        'table2vec': table2vec,
        'op2vec': op2vec,
        'join2vec': join2vec,
        'column2vec': column2vec,
        'column_min_max_vals': column_min_max_vals,
        'min_val': min_val,
        'max_val': max_val,
    }

    # save model
    timeStamp = time.strftime("%Y%m%d%H%M%S")
    nn_saved_path = './model_saved/model_%s.nn' % timeStamp
    nn_file = open(nn_saved_path, "wb")
    pickle.dump(model, nn_file)
    nn_file.close()

    return model


def model_predict(workload_name, model, batch_size, cuda):
    nn = model['nn']
    num_materialized_samples = model['num_materialized_samples']
    table2vec = model['table2vec']
    op2vec = model['op2vec']
    join2vec = model['join2vec']
    column2vec = model['column2vec']
    column_min_max_vals = model['column_min_max_vals']
    min_val = model['min_val']
    max_val = model['max_val']

    # Load test data
    file_name = "workloads/" + workload_name
    joins, predicates, tables, samples, label = load_data(file_name, num_materialized_samples, is_train=False)

    # Get feature encoding and proper normalization
    samples_test = encode_samples(tables, samples, table2vec)
    predicates_test, joins_test = encode_data(predicates, joins, column_min_max_vals, column2vec, op2vec, join2vec)
    labels_test, _, _ = normalize_labels(label, min_val, max_val)

    print("Number of test samples: {}".format(len(labels_test)))

    max_num_predicates = max([len(p) for p in predicates_test])
    max_num_joins = max([len(j) for j in joins_test])

    # Get test set predictions
    test_data = make_dataset(samples_test, predicates_test, joins_test, labels_test, max_num_joins, max_num_predicates)
    test_data_loader = DataLoader(test_data, batch_size)

    preds_test, t_total = predict(nn, test_data_loader, cuda)
    print("Prediction time per test sample: {}".format(t_total / len(labels_test) * 1000))

    # Unnormalize
    preds_test_unnorm = unnormalize_labels(preds_test, min_val, max_val)

    # Print metrics
    print("\nQ-Error " + workload_name + ":")
    print_qerror(preds_test_unnorm, label)

    # Write predictions
    timeStamp = time.strftime("%Y%m%d%H%M%S")
    file_name = "results/predictions_" + workload_name + "_" + timeStamp + ".csv"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        for i in range(len(preds_test_unnorm)):
            f.write(str(preds_test_unnorm[i]) + "," + label[i] + "\n")


# train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)
def train_and_predict(workload_name, num_queries, num_epochs, batch_size, hid_units, cuda):
    """
    workload_name:训练集
    num_queries:查询数量
    num_epochs:迭代次数
    batch_size:每批数量
    hid_units:隐藏层单元数量
    cuda:是否启用cuda
    """
    model = model_train(num_queries, num_epochs, batch_size, hid_units, cuda)

    model_predict(workload_name, model, batch_size, cuda)


# 使用保存好的模型预测
def predict_with_exist_nn(test_file_name, nn_file_name):
    # Load
    nn_file_path = './model_saved/' + nn_file_name
    nn_file = open(nn_file_path, 'rb')
    model = pickle.load(nn_file)
    model_predict(test_file_name, model, 100, False)
    nn_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("testset", help="synthetic, scale, or job-light")
    parser.add_argument("--queries", help="number of training queries (default: 10000), max 102122", type=int, default=100000)
    parser.add_argument("--epochs", help="number of epochs (default: 10)", type=int, default=100)
    parser.add_argument("--batch", help="batch size (default: 1024)", type=int, default=1024)
    parser.add_argument("--hid", help="number of hidden units (default: 256)", type=int, default=256)
    parser.add_argument("--cuda", help="use CUDA", action="store_true")
    args = parser.parse_args()
    train_and_predict(args.testset, args.queries, args.epochs, args.batch, args.hid, args.cuda)
    # predict_with_exist_nn(args.testset, 'model_1.nn')


if __name__ == "__main__":
    main()

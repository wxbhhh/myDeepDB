import csv
import random

from torch.utils.data import dataset
from myCE.mymscn.myutil import *


def make_model_dataset(samples, predicates, joins, labels, max_num_joins, max_num_predicates):
    """Add zero-padding and wrap as tensor dataset."""

    sample_masks = []
    sample_tensors = []
    for sample in samples:
        sample_tensor = np.vstack(sample)
        num_pad = max_num_joins + 1 - sample_tensor.shape[0]
        sample_mask = np.ones_like(sample_tensor).mean(1, keepdims=True)
        sample_tensor = np.pad(sample_tensor, ((0, num_pad), (0, 0)), 'constant')
        sample_mask = np.pad(sample_mask, ((0, num_pad), (0, 0)), 'constant')
        sample_tensors.append(np.expand_dims(sample_tensor, 0))
        sample_masks.append(np.expand_dims(sample_mask, 0))
    sample_tensors = np.vstack(sample_tensors)
    sample_tensors = torch.FloatTensor(sample_tensors)
    sample_masks = np.vstack(sample_masks)
    sample_masks = torch.FloatTensor(sample_masks)

    predicate_masks = []
    predicate_tensors = []
    for predicate in predicates:
        predicate_tensor = np.vstack(predicate)
        num_pad = max_num_predicates - predicate_tensor.shape[0]
        predicate_mask = np.ones_like(predicate_tensor).mean(1, keepdims=True)
        predicate_tensor = np.pad(predicate_tensor, ((0, num_pad), (0, 0)), 'constant')
        predicate_mask = np.pad(predicate_mask, ((0, num_pad), (0, 0)), 'constant')
        predicate_tensors.append(np.expand_dims(predicate_tensor, 0))
        predicate_masks.append(np.expand_dims(predicate_mask, 0))
    predicate_tensors = np.vstack(predicate_tensors)
    predicate_tensors = torch.FloatTensor(predicate_tensors)
    predicate_masks = np.vstack(predicate_masks)
    predicate_masks = torch.FloatTensor(predicate_masks)

    join_masks = []
    join_tensors = []
    for join in joins:
        join_tensor = np.vstack(join)
        num_pad = max_num_joins - join_tensor.shape[0]
        join_mask = np.ones_like(join_tensor).mean(1, keepdims=True)
        join_tensor = np.pad(join_tensor, ((0, num_pad), (0, 0)), 'constant')
        join_mask = np.pad(join_mask, ((0, num_pad), (0, 0)), 'constant')
        join_tensors.append(np.expand_dims(join_tensor, 0))
        join_masks.append(np.expand_dims(join_mask, 0))
    join_tensors = np.vstack(join_tensors)
    join_tensors = torch.FloatTensor(join_tensors)
    join_masks = np.vstack(join_masks)
    join_masks = torch.FloatTensor(join_masks)

    target_tensor = torch.FloatTensor(labels)

    return dataset.TensorDataset(sample_tensors, predicate_tensors, join_tensors, target_tensor, sample_masks,
                                 predicate_masks, join_masks)


# ????????????????????????????????????????????????
def load_model_data(file_name, num_materialized_samples):
    joins = []
    predicates = []
    tables = []
    samples = []
    label = []

    # Load queries
    with open(file_name, 'rU') as f:
        data_raw = list(list(rec) for rec in csv.reader(f, delimiter='#'))

        # ????????????
        random.shuffle(data_raw)

        for row in data_raw:
            tables.append(row[0].split(','))
            joins.append(row[1].split(','))
            predicates.append(row[2].split(','))
            row_label = row[3].split(',')

            # ?????????dnv???0??????????????????????????????????????????????????????
            # for i, v in enumerate(row_label):
            #     if float(v) <= 0:
            #         row_label[i] = 1

            label.append(row_label)
    # Split predicates
    predicates = [list(chunks(d, 3)) for d in predicates]
    print("Loaded queries")

    return joins, predicates, tables, samples, label


# ??????????????????????????????????????????????????????
def load_and_encode_model_data(train_data_file, model_column_dnv_vals, column_min_max_dnv_vals, num_queries_percent, num_materialized_samples, model_max_card):
    joins, predicates, tables, samples, label = load_model_data(train_data_file, num_materialized_samples)

    column_dict = list(model_column_dnv_vals.keys())

    # Get column name dict
    column_names = get_all_column_names(predicates)
    #column2vec, idx2column = get_set_encoding(column_names)
    column2vec, idx2column = get_set_encoding(column_dict)

    # Get table name dict
    table_names = get_all_table_names(tables)
    table2vec, idx2table = get_set_encoding(table_names)

    # Get operator name dict
    # operators = get_all_operators(predicates)
    operators = ['>', '>=', '<', '<=', '=']
    op2vec, idx2op = get_set_encoding(operators)

    # Get join name dict
    join_set = get_all_joins(joins)
    join2vec, idx2join = get_set_encoding(join_set)

    # Get feature encoding and proper normalization
    samples_enc = encode_samples(tables, samples, table2vec)

    predicates_enc, joins_enc = encode_data(predicates, joins, column_min_max_dnv_vals, column2vec, op2vec, join2vec)
    model_column_dnv_list = [model_column_dnv_vals[key] for key in model_column_dnv_vals]
    label_norm = normalize_labels(label, model_max_card, model_column_dnv_list)

    num_queries = len(label_norm)
    # Split in training and validation samples
    num_train = int(num_queries * num_queries_percent)
    num_test = num_queries - num_train

    samples_train = samples_enc[:num_train]
    predicates_train = predicates_enc[:num_train]
    joins_train = joins_enc[:num_train]
    labels_train = label_norm[:num_train]

    samples_test = samples_enc[num_train:num_train + num_test]
    predicates_test = predicates_enc[num_train:num_train + num_test]
    joins_test = joins_enc[num_train:num_train + num_test]
    labels_test = label_norm[num_train:num_train + num_test]

    print("Number of training samples: {}".format(len(labels_train)))
    print("Number of validation samples: {}".format(len(labels_test)))

    max_num_joins = max(max([len(j) for j in joins_train]), max([len(j) for j in joins_test]))
    max_num_predicates = max(max([len(p) for p in predicates_train]), max([len(p) for p in predicates_test]))

    dicts = [table2vec, column2vec, op2vec, join2vec]
    train_data = [samples_train, predicates_train, joins_train]
    test_data = [samples_test, predicates_test, joins_test]
    return dicts, labels_train, labels_test, max_num_joins, max_num_predicates, train_data, test_data


# ????????????????????????????????????????????????
def get_model_datasets(train_data_file, model_column_dnv_vals, column_min_max_dnv_vals, num_queries, num_materialized_samples, model_max_card):

    dicts, \
    labels_train, \
    labels_test, \
    max_num_joins, \
    max_num_predicates, \
    train_data, \
    test_data = \
        load_and_encode_model_data(train_data_file, model_column_dnv_vals, column_min_max_dnv_vals, num_queries, num_materialized_samples, model_max_card)

    train_dataset = make_model_dataset(*train_data, labels=labels_train, max_num_joins=max_num_joins,
                                 max_num_predicates=max_num_predicates)
    print("Created TensorDataset for training data")

    test_dataset = make_model_dataset(*test_data, labels=labels_test, max_num_joins=max_num_joins,
                                max_num_predicates=max_num_predicates)
    print("Created TensorDataset for validation data")

    return dicts, labels_train, labels_test, max_num_joins, max_num_predicates, train_dataset, test_dataset

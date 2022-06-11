import numpy as np


# Helper functions for data processing
import torch


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_all_column_names(predicates):
    column_names = set()
    for query in predicates:
        for predicate in query:
            if len(predicate) == 3:
                column_name = predicate[0]
                column_names.add(column_name)
    return column_names


def get_all_table_names(tables):
    table_names = set()
    for query in tables:
        for table in query:
            table_names.add(table)
    return table_names


def get_all_operators(predicates):
    operators = set()
    for query in predicates:
        for predicate in query:
            if len(predicate) == 3:
                operator = predicate[1]
                operators.add(operator)
    return operators


def get_all_joins(joins):
    join_set = set()
    for query in joins:
        for join in query:
            join_set.add(join)
    return join_set


def idx_to_onehot(idx, num_elements):
    onehot = np.zeros(num_elements, dtype=np.float32)
    onehot[idx] = 1.
    return onehot


def get_set_encoding(source_set, onehot=True):
    num_elements = len(source_set)
    source_list = list(source_set)
    # Sort list to avoid non-deterministic behavior
    source_list.sort()
    # Build map from s to i
    thing2idx = {s: i for i, s in enumerate(source_list)}
    # Build array (essentially a map from idx to s)
    idx2thing = [s for i, s in enumerate(source_list)]
    if onehot:
        thing2vec = {s: idx_to_onehot(i, num_elements) for i, s in enumerate(source_list)}
        return thing2vec, idx2thing
    return thing2idx, idx2thing


def get_min_max_vals(predicates, column_names):
    min_max_vals = {t: [float('inf'), float('-inf')] for t in column_names}
    for query in predicates:
        for predicate in query:
            if len(predicate) == 3:
                column_name = predicate[0]
                val = float(predicate[2])
                if val < min_max_vals[column_name][0]:
                    min_max_vals[column_name][0] = val
                if val > min_max_vals[column_name][1]:
                    min_max_vals[column_name][1] = val
    return min_max_vals


def normalize_data(val, column_name, column_min_max_vals):
    min_val = column_min_max_vals[column_name]['min']
    max_val = column_min_max_vals[column_name]['max']
    val = float(val)
    val_norm = 0.0
    if max_val > min_val:
        val_norm = (val - min_val) / (max_val - min_val)
    return np.array(val_norm, dtype=np.float32)


def normalize_labels(labels, model_max_card, model_dnv_vals):
    card_labels = np.array([np.log(float(l[0])) for l in labels])
    model_max_card_log = np.log(float(model_max_card))
    card_labels_norm = card_labels / model_max_card_log

    dnv_labels = []
    for l in labels:
        dnv_l = []
        for i, dnv in enumerate(l):
            if i == 0:
                continue
            dnv_l.append(np.log(float(dnv)) / np.log(model_dnv_vals[i-1]))
        dnv_labels.append(dnv_l)
    dnv_labels_norm = np.array(dnv_labels)
    labels_norm = np.column_stack((card_labels_norm, dnv_labels_norm))
    return labels_norm


def unnormalize_labels(labels_norm, model_max_card, model_dnv_vals):
    card_norm = labels_norm[:, 0:1]
    dnv_norm = labels_norm[0:, 1:]

    # card_norm = np.array(card_norm, dtype=np.float32)
    cards = card_norm*torch.log(torch.tensor(float(model_max_card)))
    cards = torch.exp(cards)

    dnvs = dnv_norm*torch.log(torch.tensor(model_dnv_vals))
    dnvs = torch.exp(dnvs)

    result = torch.cat([cards, dnvs], dim=1)
    return result


def unnormalize_row_outputs(labels_norm, model_max_card, model_dnv_vals):
    card_norm = labels_norm[0:1]
    dnv_norm = labels_norm[1:]

    # card_norm = np.array(card_norm, dtype=np.float32)
    cards = card_norm * torch.log(torch.tensor(float(model_max_card)))
    cards = torch.exp(cards)

    dnvs = dnv_norm * torch.log(torch.tensor(model_dnv_vals))
    dnvs = torch.exp(dnvs)

    result = torch.cat([cards, dnvs], dim=0)
    return result

def encode_samples(tables, samples, table2vec):
    samples_enc = []
    for i, query in enumerate(tables):
        samples_enc.append(list())
        for j, table in enumerate(query):
            sample_vec = []
            # Append table one-hot vector
            sample_vec.append(table2vec[table])
            # Append bit vector
            # 暂时关闭
            # sample_vec.append(samples[i][j])
            sample_vec = np.hstack(sample_vec)
            samples_enc[i].append(sample_vec)
    return samples_enc


def encode_data(predicates, joins, column_min_max_vals, column2vec, op2vec, join2vec):
    predicates_enc = []
    joins_enc = []
    for i, query in enumerate(predicates):
        predicates_enc.append(list())
        joins_enc.append(list())
        for predicate in query:
            if len(predicate) == 3:
                # Proper predicate
                column = predicate[0]
                operator = predicate[1]
                val = predicate[2]
                norm_val = normalize_data(val, column, column_min_max_vals)

                pred_vec = []
                pred_vec.append(column2vec[column])
                pred_vec.append(op2vec[operator])
                pred_vec.append(norm_val)
                pred_vec = np.hstack(pred_vec)
            else:
                pred_vec = np.zeros((len(column2vec) + len(op2vec) + 1))

            predicates_enc[i].append(pred_vec)

        for predicate in joins[i]:
            # Join instruction
            join_vec = join2vec[predicate]
            joins_enc[i].append(join_vec)
    return predicates_enc, joins_enc


def encode_row_samples(tables_str, samples, table2vec):
    query = tables_str.split(',')
    samples_enc = []
    for j, table in enumerate(query):
        sample_vec = table2vec[table]
        # Append bit vector
        # 暂时关闭
        # sample_vec.append(samples[i][j])
        sample_vec = np.hstack(sample_vec)
        samples_enc.append(sample_vec)

    sample_tensor = np.vstack(samples_enc)
    sample_tensor = torch.FloatTensor(sample_tensor)

    sample_mask = np.ones_like(sample_tensor).mean(1, keepdims=True)
    sample_mask = np.vstack(sample_mask)
    sample_mask = torch.FloatTensor(sample_mask)

    return sample_tensor, sample_mask


def encode_row_data(predicates_str, joins_str, column_min_max_vals, column2vec, op2vec, join2vec):
    predicates = []

    # 谓词部分为空时补上默认谓词
    if predicates_str is '':
        for column_name in column2vec:
            if column_name.endswith('.id'):
                predicates_str = '%s,<=,%s' % (column_name, column_min_max_vals[column_name]['max'])
                break

    predicates_arr = predicates_str.split(',')
    for i in range(len(predicates_arr)//3):
        column = predicates_arr[i*3]
        operator = predicates_arr[i*3+1]
        val = predicates_arr[i*3+2]
        predicates.append([column, operator, val])

    predicates_enc = []
    for predicate in predicates:
        pred_vec = []
        if len(predicate) == 3:
            # Proper predicate
            column = predicate[0]
            operator = predicate[1]
            val = predicate[2]
            norm_val = normalize_data(val, column, column_min_max_vals)

            pred_vec.append(column2vec[column])
            pred_vec.append(op2vec[operator])
            pred_vec.append(norm_val)
            pred_vec = np.hstack(pred_vec)
        else:
            pred_vec = np.zeros((len(column2vec) + len(op2vec) + 1))

        predicates_enc.append(pred_vec)

    predicates_tensor = np.vstack(predicates_enc)
    predicates_tensor = torch.FloatTensor(predicates_tensor)

    predicates_mask = np.ones_like(predicates_tensor).mean(1, keepdims=True)
    predicates_mask = np.vstack(predicates_mask)
    predicates_mask = torch.FloatTensor(predicates_mask)

    joins = joins_str.split(',')
    joins_enc = []
    for join in joins:
        # Join instruction
        join_vec = join2vec[join]
        joins_enc.append(join_vec)
    joins_tensor = np.vstack(joins_enc)
    joins_tensor = torch.FloatTensor(joins_tensor)

    joins_mask = np.ones_like(joins_tensor).mean(1, keepdims=True)
    joins_mask = np.vstack(joins_mask)
    joins_mask = torch.FloatTensor(joins_mask)

    return predicates_tensor, predicates_mask, joins_tensor, joins_mask

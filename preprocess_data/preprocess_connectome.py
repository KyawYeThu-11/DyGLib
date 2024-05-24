import numpy as np
import os
import pandas as pd
from pathlib import Path
import argparse
from pandas.testing import assert_frame_equal
from distutils.dir_util import copy_tree


def preprocess(dataset_name: str):
    """
    read the original data file and return the DataFrame that has columns ['u', 'i', 'ts', 'label', 'idx']
    :param dataset_name: str, dataset name
    :return:
    """
    u_list, i_list, ts_list, label_list = [], [], [], []
    feat_l = []
    idx_list = []

    with open(dataset_name) as f:
        # skip the first line
        s = next(f)
        previous_time = -1
        for idx, line in enumerate(f):
            e = line.strip().split(',')
            # user_id
            u = int(e[0])
            # item_id
            i = int(e[1])

            # timestamp
            ts = float(e[2])
            # check whether time in ascending order
            assert ts >= previous_time
            previous_time = ts
            # state_label
            label = float(e[3])

            # edge features
            feat = np.array([float(x) for x in e[4:]])

            u_list.append(u)
            i_list.append(i)
            ts_list.append(ts)
            label_list.append(label)
            # edge index
            idx_list.append(idx)

            feat_l.append(feat)
    return pd.DataFrame({'u': u_list,
                         'i': i_list,
                         'ts': ts_list,
                         'label': label_list,
                         'idx': idx_list}), np.array(feat_l)


def reindex(df: pd.DataFrame, bipartite: bool = True):
    """
    reindex the ids of nodes and edges
    :param df: DataFrame
    :param bipartite: boolean, whether the graph is bipartite or not
    :return:
    """
    new_df = df.copy()
    if bipartite:
        # check the ids of users and items
        assert (df.u.max() - df.u.min() + 1 == len(df.u.unique()))
        assert (df.i.max() - df.i.min() + 1 == len(df.i.unique()))
        assert df.u.min() == df.i.min() == 0

        # if bipartite, discriminate the source and target node by unique ids (target node id is counted based on source node id)
        upper_u = df.u.max() + 1
        new_i = df.i + upper_u

        new_df.i = new_i

    # make the id start from 1
    new_df.u += 1
    new_df.i += 1
    new_df.idx += 1

    return new_df


def preprocess_data(read_dir: str, save_dir: str, dataset_name: str, bipartite: bool = True, node_feat_dim: int = 172):
    """
    preprocess the data
    :param dataset_name: str, dataset name
    :param bipartite: boolean, whether the graph is bipartite or not
    :param node_feat_dim: int, dimension of node features
    :return:
    """
    gdrive_path = 'Dataset/Preprocessed Data'
    os.makedirs(os.path.join(gdrive_path, save_dir, dataset_name), exist_ok=True)
    OUT_DF = os.path.join(gdrive_path, save_dir, dataset_name, 'ml_{}.csv'.format(dataset_name))
    OUT_FEAT = os.path.join(gdrive_path, save_dir, dataset_name, 'ml_{}.npy'.format(dataset_name))
    OUT_NODE_FEAT = os.path.join(gdrive_path, save_dir, dataset_name, 'ml_{}_node.npy'.format(dataset_name))
    PATH = '/content/DG_data/{}/{}.csv'.format(read_dir, dataset_name)

    # os.makedirs(os.path.join('../processed_data', save_dir, dataset_name), exist_ok=True)
    # OUT_DF = os.path.join('../processed_data', save_dir, dataset_name, 'ml_{}.csv'.format(dataset_name))
    # OUT_FEAT = os.path.join('../processed_data', save_dir, dataset_name, 'ml_{}.npy'.format(dataset_name))
    # OUT_NODE_FEAT = os.path.join('../processed_data', save_dir, dataset_name, 'ml_{}_node.npy'.format(dataset_name))
    # PATH = '../DG_data/{}/{}.csv'.format(read_dir, dataset_name)
    
    df, edge_feats = preprocess(PATH)
    new_df = reindex(df, bipartite)

    # edge feature for zero index, which is not used (since edge id starts from 1)
    empty = np.zeros(edge_feats.shape[1])[np.newaxis, :]
    # Stack arrays in sequence vertically(row wise),
    edge_feats = np.vstack([empty, edge_feats])

    # node features with one additional feature for zero index (since node id starts from 1)
    max_idx = max(new_df.u.max(), new_df.i.max())
    node_feats = np.zeros((max_idx + 1, node_feat_dim))


    new_df.to_csv(OUT_DF)  # edge-list
    np.save(OUT_FEAT, edge_feats)  # edge features
    np.save(OUT_NODE_FEAT, node_feats)  # node features


parser = argparse.ArgumentParser('Interface for preprocessing datasets')
parser.add_argument('--dataset_name', type=str, help='Dataset name')
parser.add_argument('--node_feat_dim', type=int, default=172, help='Number of node raw features')
parser.add_argument('--check', type=bool, default=False, help='Check the processed data')
parser.add_argument('--save_dir', type=str, default='gdrive', help='Save directory: Temporarily Imported Repo or Google Drive', choices=['gdrive', 'repo'])
parser.add_argument('--read_dir', type=str, help='Dataset path')

args = parser.parse_args()

print(f'preprocess dataset {args.dataset_name}...')
preprocess_data(save_dir=args.save_dir, read_dir=args.read_dir, dataset_name=args.dataset_name, bipartite=False, node_feat_dim=args.node_feat_dim)
print(f'{args.dataset_name} is processed successfully.')

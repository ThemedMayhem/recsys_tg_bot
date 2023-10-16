from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from multiprocessing import Pool, cpu_count
from pandas.core.common import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


class EASE:
    def __init__(self):
        self.user_enc = LabelEncoder()
        self.item_enc = LabelEncoder()

    def _get_users_and_items(self, df):
        users = self.user_enc.fit_transform(df.loc[:, 'user_id'])
        items = self.item_enc.fit_transform(df.loc[:, 'item_id'])
        return users, items

    def fit(self, df, lambda_: float = 0.5, implicit=True):
        """
        df: pandas.DataFrame with columns user_id, item_id and (rating)
        lambda_: l2-regularization term
        implicit: if True, ratings are ignored and taken as 1, else normalized ratings are used
        """
        users, items = self._get_users_and_items(df)
        
        # print(users)
        # print(items)
        values = (
            np.ones(df.shape[0])
            if implicit
            else df['rating'].astype(int).to_numpy() / df['rating'].astype(int).max()
        )

        X = csr_matrix((values, (users, items)))
        self.X = X
        

        G = X.T.dot(X).toarray()
        diagIndices = np.diag_indices(G.shape[0])
        G[diagIndices] += lambda_
        P = np.linalg.inv(G)
        B = P / (-np.diag(P))
        B[diagIndices] = 0

        self.B = B
        self.pred = X.dot(B)
        
        # print(self.pred)

    def predict(self, train, users, items, k):
        items = self.item_enc.transform(items)
        dd = train.loc[train.user_id.astype(str).isin(users)]
        dd['ci'] = self.item_enc.transform(dd.item_id)
        dd['cu'] = self.user_enc.transform(dd.user_id)
        g = dd.groupby('cu')
        user_preds = []
        for user, group in g:
            user_pred = self.predict_for_user(user, group, self.pred[user, :], items, k)
            user_preds.append(user_pred)
        # with Pool(cpu_count()) as p:
        #     user_preds = p.starmap(
        #         self.predict_for_user,
        #         [(user, group, self.pred[user, :], items, k) for user, group in g],
        #     )
        df = pd.concat(user_preds)
        df['item_id'] = self.item_enc.inverse_transform(df['item_id'])
        df['user_id'] = self.user_enc.inverse_transform(df['user_id'])
        return df

    @staticmethod
    def predict_for_user(user, group, pred, items, k):
        watched = set(group['ci'])
        candidates = [item for item in items if item not in watched]
        pred = np.take(pred, candidates)
        res = np.argpartition(pred, -k)[-k:]
        r = pd.DataFrame(
            {
                "user_id": [user] * len(res),
                "item_id": np.take(candidates, res),
                "score": np.take(pred, res),
            }
        ).sort_values('score', ascending=False)
        return r
    
def csv_unique_actions(filename='user_actions.csv'):
# Загрузка данных из CSV
    data = pd.read_csv(filename, header=None, names=['user_id', 'item_id', 'rating'])
    
    # Группировка данных по user_id и item_id и выбор последнего значения rating
    data_sorted = data.sort_values(by=['user_id', 'item_id'])
    data_grouped = data_sorted.groupby(['user_id', 'item_id']).last().reset_index()
    
    # Назначение новых числовых значений для rate
    rate_dict = {'dislike': 0, 'like': 1, 'fire': 2}
    data_grouped['rating'] = data_grouped['rating'].map(rate_dict)
    # Запись в CSV файл
    data_grouped.to_csv(f'{filename[:-4]}_unique.csv', index=False)
    
def make_recs(users, items, k=10):        
    csv_unique_actions(filename='user_actions.csv')
    
    df = pd.read_csv('user_actions_unique.csv')
    
    ease_method = EASE()
    ease_method.fit(df, implicit=False)
    
    # users=['1572576417']
    # items = df.item_id.tolist()
    
    return ease_method.predict(train=df, users=users, items=items, k=k)

import pandas as pd
import numpy as np

# Загрузка данных из CSV
data = pd.read_csv('user_actions.csv', header=None, names=['user_id', 'item_id', 'rating'])

# Назначение новых числовых значений для rate
rate_dict = {'dislike': 0, 'like': 1, 'fire': 2}
data['rate'] = data['rate'].map(rate_dict)

# Группировка данных по user_id и item_id и выбор последнего значения rate
data_sorted = data.sort_values(by=['user_id', 'item_id'])
data_grouped = data_sorted.groupby(['user_id', 'item_id']).last().reset_index()

# Создание таблицы соответствия
pivot_table = pd.pivot_table(data_grouped, values='rate', index='user_id', columns='item_id', fill_value=0)

# Создание списков user_id и item_id
user_id_list = pivot_table.index.tolist()
item_id_list = pivot_table.columns.tolist()

# Преобразование в numpy array
numpy_data = pivot_table.values



def matr_to_csv(numpy_data):
    # Создание обратной таблицы
    df = pd.DataFrame(data=numpy_data, index=user_id_list, columns=item_id_list).reset_index()
    
    # Преобразование таблицы в нужный формат
    df = df.melt(id_vars=df.columns[0], var_name='item_id', value_name='rating').rename(columns={df.columns[0]:'user_id'})
    
    # Возвращаем строки в исходные значения
    reverse_rate_dict = {0: 'dislike', 1: 'like', 2: 'fire'}
    df['rating'] = df['rating'].map(reverse_rate_dict)
    
    # Запись в CSV файл
    df.to_csv('output.csv', index=False)

print(numpy_data)
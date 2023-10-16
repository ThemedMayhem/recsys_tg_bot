import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import numpy as np
from collections import Counter
# Чтение данных из файла
df = pd.read_csv('user_actions_unique.csv')

# Создание словаря для результатов
result = {category: {'like': 0, 'dislike': 0, 'fire': 0} for category in 
          ['car', 'clothes', 'education', 'flowers', 'food', 'home', 'jawelery', 
           'marketplace', 'medicine', 'others', 'service', 'travel']}





# Словарь для преобразования чисел в названия
rating_dict = {0: 'dislike', 1: 'like', 2: 'fire'}

# Путь к папке с категориями
base_path = "offers"

# Обход данных и подсчет 'like', 'dislike', 'fire'
for _, row in df.iterrows():
    item = row['item_id']
    rating = rating_dict[row['rating']]   # Преобразование числа в название
    for category in result.keys():
        if item in os.listdir(f"{base_path}/{category}"):
            result[category][rating] += 1
            break

# Подготовка данных для графика
# Подготовка данных для графика
labels = list(result.keys())
like = np.array([v['like'] for v in result.values()])
dislike = np.array([v['dislike'] for v in result.values()])
fire = np.array([v['fire'] for v in result.values()])
total = like + dislike + fire  # общее количество оценок для каждой категории

like = like / total  # нормализация данных
dislike = dislike / total
fire = fire / total

print(total.sum())

# Создание графика
x = range(len(labels))  # Количество категорий
plt.figure(dpi=180)
plt.bar(x, dislike, width=0.3, label='dislike')
plt.bar(x, like, width=0.3, bottom=dislike, label='like')
plt.bar(x, fire, width=0.3, bottom=[i+j for i, j in zip(like, dislike)], label='fire')
plt.xticks(x, labels, rotation=45)
plt.ylim(0, 1)
plt.legend(loc='lower left')
plt.show()


with open('users.txt') as file:
    all_users = [line.rstrip() for line in file]

print(len(all_users))



# Чтение данных из файла
df = pd.read_csv('user_actions_unique.csv')

# Создание словарей для подсчета рейтингов
like_counter = Counter()
dislike_counter = Counter()


rating_dict = {0: 'dislike', 1: 'like', 2: 'fire'}

# Обход данных и подсчет 'like' и 'dislike'
for _, row in df.iterrows():
    item = row['item_id']
    rating = rating_dict[row['rating']]
    if rating == 'like' or rating == 'fire':
        like_counter[item] += 1

    else:
        dislike_counter[item] += 1

# Вывод топ 5 элементов с самым большим количеством 'like' и 'dislike'
top_5_likes = like_counter.most_common(5)
top_5_dislikes = dislike_counter.most_common(5)

print('Топ 5 элементов с максимальным количеством "like": ', top_5_likes)
print('Топ 5 элементов с максимальным количеством "dislike": ', top_5_dislikes)



# Чтение данных из файла
df = pd.read_csv('user_actions_unique.csv')

# Создание словаря для результатов
user_stats = {}

# Словарь для преобразования чисел в названия
rating_dict = {0: 'dislike', 1: 'like', 2: 'like'}

# Обход данных и подсчет 'like', 'dislike' для каждого пользователя
for _, row in df.iterrows():
    user = row['user_id']
    rating = rating_dict[row['rating']]

    if user not in user_stats:
        user_stats[user] = {'dislike': 0, 'like': 0}

    user_stats[user][rating] += 1

sorted_users  = sorted(user_stats.items(), key=lambda x: x[1]['like'], reverse=True)

# Подготовка данных для графика
labels = [user[0] for user in sorted_users]
like = np.array([user[1]['like'] for user in sorted_users])
dislike = np.array([user[1]['dislike'] for user in sorted_users])

total = like + dislike

# like = like / total 
# dislike = dislike / total 
# fire = fire / total 

# Создание графика
x = range(len(labels)) 
plt.figure(dpi=180)
plt.bar(x, dislike, width=0.5, bottom=like, label='dislike')
plt.bar(x, like, width=0.5,  label='like')
plt.legend()
plt.show()




import pandas as pd
import matplotlib.pyplot as plt

# Читаем CSV файл
df = pd.read_csv('user_actions_unique.csv')

# Подсчет общего количества записей для каждого пользователя
total_user_entries = df['user_id'].value_counts()

# Подсчет количества элементов с rating 1 или 2 для каждого пользователя
user_entries_with_rating_1_or_2 = df[df['rating'].isin([1, 2])]['user_id'].value_counts()

# Расчет относительной величины
relative_value = user_entries_with_rating_1_or_2 / total_user_entries

# Создание dataframe с результатами
result = pd.DataFrame({'total': total_user_entries, 'rating_1_or_2': user_entries_with_rating_1_or_2, 'relative': relative_value})

# Построение гистограммы
result['relative'].plot(kind='bar', figsize=(24, 12))
plt.xlabel('Users')
plt.ylabel('Relative value')
plt.title('Relative value of ratings 1 or 2 over total entries per user')
plt.show()




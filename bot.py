API_TOKEN = 

import telebot
import csv
import pandas as pd
import random
from random import randrange
import os
from rec_model import *
import json

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Load items from a CSV file into a DataFrame (Assuming you have a CSV file with a "text" column)
items_df = pd.read_csv('items.csv', encoding='UTF-8')

with open('users.txt') as file:
    all_users = [line.rstrip() for line in file]


last_bot_messages = {}


prob_cats = {}

# Create a dictionary to keep track of user states (which item they are currently rating)
user_states = {}

emoji_dict = {
    'dislike': '👎',
    'like': '👍',
    'fire': '🔥',
}

buffer_last_30 = {}

# Функция для загрузки статистики из файла
def load_stats():
    try:
        with open('stats.txt', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Функция для сохранения статистики в файл
def save_stats(stats):
    with open('stats.txt', 'w') as f:
        json.dump(stats, f)
        
stats = load_stats()

# Функция для обработки команды "Статистика"
@bot.message_handler(commands=['stats'])
def send_stats(message):
    user_id = str(message.from_user.id)
    if user_id in last_bot_messages and last_bot_messages[user_id]:
        # удалить последнее сообщение бота
        try:
            bot.delete_message(chat_id=user_id, message_id=last_bot_messages[user_id])
        except telebot.apihelper.ApiException:
            pass

    stats = load_stats()
    user_stats = stats.get(user_id, 0)
    stat_message = f'Вы уже оценили {user_stats} элемент(ов).'
    
    if user_id in last_bot_messages and last_bot_messages[user_id]:
        # удалить последнее сообщение бота
        try:
            bot.delete_message(chat_id=user_id, message_id=last_bot_messages[user_id])
        except telebot.apihelper.ApiException:
            pass

    # сохранить идентификатор отправленного сообщения
    sent_message = bot.send_message(user_id, stat_message)
    last_bot_messages[user_id] = sent_message.message_id


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = telebot.types.KeyboardButton('/start')
    stats_button = telebot.types.KeyboardButton('/stats')
    markup.row(start_button, stats_button)

    user_id = message.from_user.id
    if user_id in last_bot_messages and last_bot_messages[user_id]:
        # удалить последнее сообщение бота
        try:
            bot.delete_message(chat_id=user_id, message_id=last_bot_messages[user_id])
        except telebot.apihelper.ApiException:
            pass

    # сохранить идентификатор отправленного сообщения  
    send_random_item_for_rating(user_id)



def send_random_item_for_rating(user_id):
    if user_id not in user_states:
        user_states[user_id] = []
        

    remaining_items = items_df[~items_df.index.isin(user_states[user_id])]
    
    
    if remaining_items.empty:
        bot.send_message(user_id, "You have rated all items.")
        remaining_items = pd.read_csv('items.csv', encoding='UTF-8')
        

    if str(user_id) not in all_users:
        all_users.append(str(user_id))
        # print(all_users)
        
        with open('users.txt', 'a') as f:
            f.writelines(str(user_id) + '\n')
        
        random_item = remaining_items.sample(n=1)
        
    else:
        try:
            df_of_recs = make_recs(users=[str(user_id)], items=remaining_items.image.tolist(), k=10)
            print(df_of_recs)
            if not df_of_recs.empty:
                
                e = randrange(0,100)/100
                print(e)
                
                if e<0.1:
                    random_item = remaining_items.sample(n=1)
                    print('random')
                else:
                    imname = df_of_recs.sample().iloc[0]['item_id']
                    random_item = remaining_items.loc[remaining_items['image'] == imname]
                    print(imname)
                
            else:
                random_item = remaining_items.sample(n=1)
                print('random')
                
        except: 
            random_item = remaining_items.sample(n=1)
            print('random')
        

    
    
    if user_id not in buffer_last_30:
        buffer_last_30[user_id] = random_item['image']
    else:
        if len(buffer_last_30[user_id])>29:
            buffer_last_30[user_id] = pd.concat([buffer_last_30[user_id], random_item['image']])[1:]
            
        else:
            buffer_last_30[user_id] = pd.concat([buffer_last_30[user_id], random_item['image']])
    
    
        
    item_text = random_item.iloc[0]['image']
    user_states[user_id].append(random_item.index[0])

    markup = telebot.types.InlineKeyboardMarkup()
    
    markup.add(
        telebot.types.InlineKeyboardButton("👎", callback_data="dislike"),
        telebot.types.InlineKeyboardButton("👍", callback_data="like"),
        telebot.types.InlineKeyboardButton("🔥", callback_data="fire"),
    )

    # bot.send_message(user_id, item_text, reply_markup=markup)
    
    
    random_img = 'photos/'  + item_text #+ random.choice(os.listdir('photos'))
    
    text = 'Оцени кешбэк'
    sent_message = bot.send_photo(user_id, photo=open(random_img, 'rb'), caption=text, reply_markup = markup)
    
    last_bot_messages[user_id] = sent_message.message_id
    

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    reaction = call.data

    if user_id in user_states:
        user_states[user_id] = user_states.get(user_id, [])
        if user_states[user_id]:
            last_rated_item_index = user_states[user_id][-1]
            item_text = items_df.loc[last_rated_item_index]['image']

            # Register the user's action in a CSV file with UTF-8 encoding
            with open("user_actions.csv", "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["user_id", "item_text", "reaction"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({"user_id": user_id, "item_text": item_text, "reaction": reaction})

            if reaction in ['like', 'fire']:
                # кнопки становятся не кликабельными и сообщение не удаляется, если пользователь выбрал "like" или "fire"
                bot.edit_message_caption(caption=f"Ваша реакция: {emoji_dict[reaction]}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

            else:
                # Пользователь выбрал 'dislike', сообщение удаляется  
               bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id) 

            # Update the statistics after a rating
        
        stats[str(user_id)] = stats.get(str(user_id), 0) + 1
        save_stats(stats)
        
        
        send_random_item_for_rating(user_id)

# Start the bot
if __name__ == '__main__':
    bot.polling(none_stop=True)

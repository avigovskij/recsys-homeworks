from typing import List
from functools import reduce
from collections import defaultdict

import json
from core import cos_sim


with open('./data.json', 'r') as json_data_file_desc:
    json_data = json.load(json_data_file_desc)

def transpond_matrix(data):
    """Функция транспонирования JSON'а"""
    new_data = defaultdict(dict)
    for user_id, user_data in data.items():
        for product_id, similarity_value in user_data.items():
            new_data[product_id][user_id] = similarity_value
    return new_data


def load_cos_sim(data):
    """Главная функция, работающая с форматом данных из ./data.json"""
    matrix = {}

    for first_category in data:
        for second_category in data:
            if (
                first_category != second_category and
                (first_category, second_category) not in matrix and
                (second_category, first_category) not in matrix
            ):
                matrix[(first_category, second_category)] = {
                    'values': {
                        first_category: data[first_category],
                        second_category: data[second_category]
                    }
                }

    results = {}

    for pair, pair_data in matrix.items():
        pair_member_1, pair_member_2 = pair
        cos_sim_result = cos_sim(
            list(pair_data['values'][pair_member_1].values()),
            list(pair_data['values'][pair_member_2].values())
        )
        print(f'Косинусное подобие между {pair_member_1} и {pair_member_2} равно: {cos_sim_result}')
        results[pair] = cos_sim_result

    max_pair = None
    max_pair_result = 0

    for result_pair, result_value in results.items():
        if result_value > max_pair_result:
            max_pair = result_pair
            max_pair_result = result_value

    print(f'Наиболее близкие категории: {max_pair}')

    return results

load_cos_sim(data=json_data)
load_cos_sim(data=transpond_matrix(data=json_data))

from typing import List
from functools import reduce
from collections import defaultdict

import json
import argparse
import math

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


def load_cos_sim(
        data,
        filter_base,
        similarity_barrier
    ):
    """
    Функция построения матрицы косинусных подобий, работающая с форматом данных из ./data.json
    :param data: dict – словарь данных
    :param filter_base: ID категории, подобие с которой выступает в основе фильтрации
    :param similarity_barrier: float – минимальное значение косинусного подобия для фильтрации
    """
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
        if filter_base in (pair_member_1, pair_member_2) and cos_sim_result >= similarity_barrier:
            results[pair] = cos_sim_result

    max_pair = None
    max_pair_result = 0

    for result_pair, result_value in results.items():
        if result_value > max_pair_result:
            max_pair = result_pair
            max_pair_result = result_value

    return results


def get_mid_rate(data, category_id):
    """Функция, возвращающая средние оценки по категории, не учитывая нулевые"""
    rate_sum = 0
    rate_num = 0
    for _, rate in data[category_id].items():
        # Не учитываем категории, которым не была проставлена оценка
        if rate == 0:
            continue
        rate_sum += rate
        rate_num += 1

    return rate_sum / rate_num


def get_most_valueable_product(rating, count = 1):
    """"""
    return sorted(
        rating.items(),
        key=lambda rating_pair: rating_pair[1],
        reverse=True
    )[:count]


def get_products_for_user(data, base_user_id):
    """"""
    product_based_matrix = transpond_matrix(data=data)
    is_new = not reduce(
        lambda previous_rate, next_rate: previous_rate or next_rate,
        data.get(base_user_id, {}).values(),
        0
    )

    product_averages = {}

    if is_new:
        for product_id in product_based_matrix:
            product_averages[product_id] = get_mid_rate(
                data=product_based_matrix,
                category_id=product_id
            )
        return get_most_valueable_product(
            rating=product_averages
        )

    cos_sim_matrix = load_cos_sim(data=data, filter_base=base_user_id, similarity_barrier=0.7)

    product_rates = {}
    base_user_average_rate = get_mid_rate(data=data, category_id=base_user_id)

    print(f'Средняя оценка пользователя "{base_user_id}" равна: {base_user_average_rate}')

    similar_users = set()
    for user_pair in cos_sim_matrix:
        for user_pair_member in user_pair:
            if user_pair_member != base_user_id:
                similar_users.add(user_pair_member)

    print(f'В качестве похожих пользователей для {base_user_id} взяты пользователи {similar_users}')
    print(f'Значения косинусных подобий для пользователя: ' + str([f'{pair_id}: {pair_value}' for pair_id, pair_value in cos_sim_matrix.items() if base_user_id in pair_id]))


    for product_id in product_based_matrix:
        product_average_rate = get_mid_rate(data=product_based_matrix, category_id=product_id)

        all_similars = sum([
            abs(similarity_value)
            for similarity_ids, similarity_value in cos_sim_matrix.items()
            if base_user_id in similarity_ids and set(similarity_ids) & similar_users
        ])
        bias_sum = 0

        for user_id in similar_users:
            if user_id == base_user_id:
                continue
            user_average_rate = get_mid_rate(data=data, category_id=user_id)
            similarity = cos_sim_matrix[
                (base_user_id, user_id)
                if (base_user_id, user_id) in cos_sim_matrix
                else (user_id, base_user_id)
            ]
            bias_sum += (product_average_rate - user_average_rate) * similarity
        product_rates[product_id] = (
            base_user_average_rate + (
                (bias_sum) / (all_similars)
            ) if all_similars else 0
        )
    
    return get_most_valueable_product({
        product_id: product_rate for product_id, product_rate in product_rates.items()
        if product_rate >= base_user_average_rate
    }, count=5)

argparser = argparse.ArgumentParser()

argparser.add_argument('--user_id', type=str, required=True)

parsed_args = argparser.parse_args()
user_id = parsed_args.user_id

product_rates = get_products_for_user(data=json_data, base_user_id=user_id)

print('Наиболее подходящие продукты и их рейтинг:')
print('\n'.join([f'{value[0]}: {value[1]}' for value in product_rates]))

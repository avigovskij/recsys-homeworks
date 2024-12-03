import json
from typing import List, Tuple


def reshape_matrix(data: dict, left_element_to_merge_id: str, right_element_to_merge_id: str) -> dict:
    """
    Метод, который принимает матрицу data, первый элемент слияния и второй элемент слияния.
    Возвращает матрицу, в которой два элемента объеденены в tuple, а расстояния до других элементов перерассчитаны
    """
    data_copy = {**data}
    left_element_distances = data_copy[left_element_to_merge_id]
    right_element_distances = data_copy[right_element_to_merge_id]

    del data_copy[left_element_to_merge_id]
    del data_copy[right_element_to_merge_id]

    reshaped_data = {}

    reshaped_data[(left_element_to_merge_id, right_element_to_merge_id)] = {
        neighbour_id: max(left_element_distances[neighbour_id], right_element_distances[neighbour_id])
        for neighbour_id in data_copy
    }
    reshaped_data = {
        **reshaped_data,
        **data_copy
    }

    print('Состояние матрицы косинусных расстояний:')
    for cluster, cluster_data in reshaped_data.items():
        print(f'Расстояния для кластера {cluster}')
        if cluster:
            print(cluster_data)
    print('Получившиеся кластеры:')
    print(' | '.join([str(cluster) for cluster in reshaped_data.keys()]))

    return reshaped_data


def get_maximum_similar_element(distances) -> Tuple[str, int]:
    """
    Фукнция вычитывает, какой элемент имеет самое большое косинусное расстояние среди представленных
    Возвращает Tuple[str]
    """
    maximum_distance = 0
    maximum_distance_element_id = None
    for element_id, distance in distances.items():
        if distance > maximum_distance:
            maximum_distance = distance
            maximum_distance_element_id = element_id
    return maximum_distance_element_id, maximum_distance


def clasterize_matrix(data: dict, cluster_radius: float):
    """"""
    for category_element, category_distances in data.items():
        maximum_distance_element_id, maximum_distance = get_maximum_similar_element(category_distances)
        
        if maximum_distance >= cluster_radius:
            clasterize_matrix(
                data=reshape_matrix(
                    data=data,
                    left_element_to_merge_id=category_element,
                    right_element_to_merge_id=maximum_distance_element_id                    
                ),
                cluster_radius=cluster_radius
            )
        else:
            continue


with open('./data.json', 'r') as json_data_file_desc:
    json_data = json.load(json_data_file_desc)

print(clasterize_matrix(data=json_data, cluster_radius=0.85))

from typing import List
from functools import reduce


def cos_sim(vector_1: List[float], vector_2: List[float]):
    """
    Функция, имплементирующая косинусное подобие
    """
    a = sum([
        (
            (vector_1[index] if index < len(vector_1) else 0) * 
            (vector_2[index] if index < len(vector_2) else 0)
        )
        for index in range(max(len(vector_1), len(vector_2)))
    ])

    v_results = []
    for vector in [vector_1, vector_2]:
        v_results.append(sum([vector_element**2 for vector_element in vector])**0.5)

    denominator = reduce(lambda x, y: x * y, v_results, 1)

    return (a / denominator) if denominator else 0

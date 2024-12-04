import json
import abc
from typing import List
from functools import reduce
from collections import defaultdict


class MatrixReducer(abc.ABC):

    def __init__(self, matrix, null_value = 0) -> None:
        self._matrix = matrix
        self._null_value = null_value

    def print_matrix(self, matrix):
        """"""
        for data_row in matrix:
            print(data_row)
    
    def print_source_matrix(self):
        """"""
        self.print_matrix(matrix=self._matrix)

    def _get_count_of_non_nullable_objects(self, vector):
        return reduce(
            lambda accumulator, current_element: accumulator + (1 if (current_element != self._null_value) else 0),
            vector,
            0
        )

    def reduce(self):
        """"""
        raise NotImplemented()
    
    def verbose(self):
        """"""
        print('Исходная матрица:')
        self.print_source_matrix()


class CoordinateWay(MatrixReducer):
    """"""
    def reduce(self):
        values = []
        rows_coordinates = []
        cols_coordinates = []

        for row_index, matrix_row_element in enumerate(self._matrix):
            for col_index, matrix_colum_element in enumerate(matrix_row_element):
                if matrix_colum_element != self._null_value:
                    values.append(matrix_colum_element)
                    rows_coordinates.append(row_index)
                    cols_coordinates.append(col_index)

        return values, rows_coordinates, cols_coordinates
    
    def verbose(self):
        super().verbose()
        values, rows_coordinates, cols_coordinates = self.reduce()

        print('Структура хранения матрицы в координатном формате:')
        print('Values:')
        print(values)

        print('Row:')
        print(rows_coordinates)

        print('Col:')
        print(cols_coordinates)
    

class CoordinateWayWithIndex(CoordinateWay):
    """"""
    def reduce(self):
        """"""
        values, _, cols_coordinates = super().reduce()

        row_index = []


        for index_of_row in range(len(self._matrix) + 1):
            if index_of_row == 0:
                row_index.append(0)
            else:
                non_nullable_objects = self._get_count_of_non_nullable_objects(
                    vector=self._matrix[index_of_row - 1]
                )
                row_index.append(
                    non_nullable_objects + (row_index[index_of_row - 1] if index_of_row >= 0 else 0)
                )

        return values, cols_coordinates, row_index

    def verbose(self):
        super(CoordinateWay, self).verbose()
        values_indexed, cols_coordinates_indexed, row_index = self.reduce()
        print('Структура хранения матрицы в координатном формате со сжатием по строке:')
        print('Values:')
        print(values_indexed)

        print('Col:')
        print(cols_coordinates_indexed)

        print('Row Index:')
        print(row_index)


class ReduceWithEllpack(MatrixReducer):
    """"""

    def reduce(self):
        """"""
        values = []
        column_cooridnates = []
        max_column_cooridnates_row_len = 0

        for row_data in self._matrix:
            non_null_count = self._get_count_of_non_nullable_objects(
                vector=row_data
            )
            if non_null_count > max_column_cooridnates_row_len:
                max_column_cooridnates_row_len = non_null_count
        
        for row_data in self._matrix:
            row_values_data = []
            column_cooridnates_data = []
            for col_index, col_data in enumerate(row_data):
                if col_data != self._null_value:
                    row_values_data.append(col_data)
                    column_cooridnates_data.append(col_index)
            if len(row_values_data) < max_column_cooridnates_row_len:
                row_values_data.extend(([None] * (max_column_cooridnates_row_len - len(row_values_data))))
            if len(column_cooridnates_data) < max_column_cooridnates_row_len:
                column_cooridnates_data.extend(([None] * (max_column_cooridnates_row_len - len(column_cooridnates_data))))
            values.append(row_values_data)
            column_cooridnates.append(column_cooridnates_data)

        return values, column_cooridnates

    def verbose(self):
        super().verbose()
        values_ellpack, cols_ellpack = self.reduce()
        print('Структура хранения матрицы ELLPACK:')
        print('Values:')
        self.print_matrix(values_ellpack)

        print('Col:')
        self.print_matrix(cols_ellpack)


class FilterReducer:
    """"""
    def __init__(self, data: dict, null_value = 0, rating_barrier = 4) -> None:
        self._data = data
        self._null_value = null_value
        self._barrier = rating_barrier

    def _get_count_of_non_nullable_objects(self, vector):
        return reduce(
            lambda accumulator, current_element: accumulator + (1 if (current_element != self._null_value) else 0),
            vector,
            0
        )
    
    def transponded_matrix(self):
        """Функция транспонирования JSON'а"""
        new_data = defaultdict(dict)
        for user_id, user_data in self._data.items():
            for product_id, similarity_value in user_data.items():
                new_data[product_id][user_id] = similarity_value

        return new_data

    def print_matrix(self, matrix):
        for user_id, user_data in matrix.items():
            print(f'Оценки пользователя {user_id}')
            print(user_data)

    def print_source_matrix(self):
        self.print_matrix(self._data)

    def reduce(self):
        result_matrix = defaultdict(dict)
        filtered_user_ids = []
        filtered_product_ids = []

        for user_id, user_data in self._data.items():
            non_null_values_count = self._get_count_of_non_nullable_objects(
                vector=list(user_data.values())
            )
            if not non_null_values_count:
                filtered_user_ids.append(user_id)

        for product_id, product_data in self.transponded_matrix().items():
            non_nullable_values = list(filter(
                lambda element:
                element,
                product_data.values()
            ))
            if non_nullable_values:
                mid_value = sum(non_nullable_values) / len(non_nullable_values)
                if mid_value < self._barrier:
                    filtered_product_ids.append(product_id)
            else:
                filtered_product_ids.append(product_id)
        for user_id, user_data in self._data.items():
            for product_id, rating in user_data.items():
                if user_id not in filtered_user_ids and product_id not in filtered_product_ids:
                    result_matrix[user_id][product_id] = rating
        return result_matrix

    def verbose(self):
        """"""
        self.print_source_matrix()
        reduced_data = self.reduce()
        self.print_matrix(reduced_data)


with open('./data.json', 'r') as json_data_file_desc:
    json_data = json.load(json_data_file_desc)
    matrix_reducers_data = json_data['matrixes']
    user_product = json_data['user_product']


classes = [CoordinateWay, CoordinateWayWithIndex, ReduceWithEllpack]

for reducer_class in classes:
    reducer_object = reducer_class(matrix=matrix_reducers_data)
    reducer_object.verbose()

user_products_reducer = FilterReducer(data=user_product)
user_products_reducer.verbose()

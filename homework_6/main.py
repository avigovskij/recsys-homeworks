md1 = 0.8
mnd1 = 0.3
# AND
md2 = 0.75
mnd2 = 0.25


md3 = 0.4
mnd3 = 0.5
# OR
md4 = 0.6
mnd4 = 0.2

input_data = {
    'MD1': md1,
    'MND1': mnd1,

    'MD2': md2,
    'MND2': mnd2,

    'MD3': md3,
    'MND3': mnd3,

    'MD4': md4,
    'MND4': mnd4
}

print('Входные данные:')

for input_var_name, input_var_val in input_data.items():
    print(f'{input_var_name} = {input_var_val}')


md_e_1 = min(md1, md2)
md_e_2 = max(md3, md4)

mnd_e_1 = min(mnd1, mnd2)
mnd_e_2 = max(mnd3, mnd4)

md_h_e1_e2 = md_e_1 + md_e_2 * (1 - md_e_1)
mnd_h_e1_e2 = mnd_e_1 + mnd_e_2 * (1 - mnd_e_1)

print(f'Рассчитаем MD[H:E1,E2]: {md_h_e1_e2}')
print(f'Рассчитаем MND[H:E1,E2]: {mnd_h_e1_e2}')


ku = md_h_e1_e2 - mnd_h_e1_e2
print(f'Рассчитаем KU[H:E] = {ku}')
print(f'KU{"" if ku < 1 and ku > -1 else " не"} входит в диапазон [-1:1]')

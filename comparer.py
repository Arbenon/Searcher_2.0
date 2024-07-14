import pandas as pd

# Завантаження даних з файлів
df1 = pd.read_excel('/home/arbenon/Documents/STUDY/pdfs/working.xls')
df2 = pd.read_excel('/home/arbenon/Documents/STUDY/pdfs/extracted_data.xlsx')

# З'єднання за кадастровим номером
merged_df = pd.merge(df1, df2, on='Кадастровий номер', how='left')

# Копія об'єднаного DataFrame для обробки
processing_df = merged_df.copy()

# Проходження кожним рядком у копії DataFrame
for index, row in processing_df.iterrows():
    if row['Частка'] != 1.00:
        # Отримання значення кадастрового номера з поточного рядка
        cadastre_number = row['Кадастровий номер']
        
        # Знаходження рядків з таким самим кадастровим номером у копії DataFrame
        same_cadastre_rows = processing_df[processing_df['Кадастровий номер'] == cadastre_number]

        if len(same_cadastre_rows) > 1:
            # Обчислення суми площ та сум для всіх рядків з однаковим кадастровим номером
            total_area = same_cadastre_rows['Площа, Га_x'].sum()
            total_sum = same_cadastre_rows['Сума з витягу_x'].sum()
            
            # Оновлення значення площі та суми в оригінальному DataFrame
            merged_df.loc[merged_df['Кадастровий номер'] == cadastre_number, 'Площа, Га_x'] = total_area
            merged_df.loc[merged_df['Кадастровий номер'] == cadastre_number, 'Сума з витягу_x'] = total_sum

            # Видалення оброблених рядків з копії DataFrame
            processing_df = processing_df[processing_df['Кадастровий номер'] != cadastre_number]

# Додавання нових колонок для результатів порівняння, з округленням до двох знаків після коми
merged_df['Площа_різниця'] = (merged_df['Площа, Га_x'] - merged_df['Площа, Га_y']).round(4)
merged_df['Сума_різниця'] = (merged_df['Сума з витягу_x'] - merged_df['Сума з витягу_y']).round(4)

# Збереження з'єднаного DataFrame на вказаному шляху
merged_df.to_excel('/home/arbenon/Documents/STUDY/pdfs/merged_file.xlsx', index=False)

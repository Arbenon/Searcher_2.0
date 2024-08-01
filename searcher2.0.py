#SEARCH++++++++++++++++++++++++++++++++++++++++++



import fitz
import os
import openpyxl
import re
import locale

def extract_text_from_pdf(pdf_file):
    text = ""
    doc = fitz.open(pdf_file)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    doc.close()
    return text

def clean_text(text):
    return re.sub(r'\s+', ' ', text)

def extract_value_after_keyword(text, keyword, regex_pattern):
    pattern = re.escape(keyword) + regex_pattern
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None

def parse_pdf_text(pdf_text):
    pdf_text = clean_text(pdf_text)
    
    data = {
        'name': '',
        'area': '',
        'value': '',
        'record_number': '',
        'atk_mentioned': 'No',
        'cad_number': ''
    }

    # Extract the name
    name_keyword = "Прізвище, ім'я та по батькові фізичної особи"
    data['name'] = extract_value_after_keyword(pdf_text, name_keyword, r'\s*([\w\s]+?(?=\s*Дата державної реєстрації права|$))')
    print(f"Extracted name: {data['name']}")

    # Extract the area
    area_keyword = "Площа земельної ділянки"
    data['area'] = extract_value_after_keyword(pdf_text, area_keyword, r'\s*([\d\.]+)')
    print(f"Extracted area: {data['area']}")

    # Extract the value
    value_keyword = "Значення, гривень"
    data['value'] = extract_value_after_keyword(pdf_text, value_keyword, r'\s*([\d\.]+)')
    print(f"Extracted value: {data['value']}")

    # Extract the record number
    record_number_keyword = "Номер запису про право (в державному реєстрі прав)"
    data['record_number'] = extract_value_after_keyword(pdf_text, record_number_keyword, r'\s*([\d]+)')
    print(f"Extracted record number: {data['record_number']}")

    # Check for ATK mention
    if 'А.Т.К' in pdf_text:
        data['atk_mentioned'] = 'Yes'

    # Extract the cadastral number
    cad_number_keyword = "Кадастровий номер земельної ділянки"
    data['cad_number'] = extract_value_after_keyword(pdf_text, cad_number_keyword, r'\s*([\d:]+)')
    print(f"Extracted cadastral number: {data['cad_number']}")

    return data

def write_to_excel(data_list, excel_file):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Extracted Data"
    
    headers = ['ПІБ', 'Площа, Га', 'Сума з витягу', 'Правовласність', 'ATK згаданий', 'Кадастровий номер']
    sheet.append(headers)
    
    # Set locale to Ukrainian for correct sorting
    try:
        locale.setlocale(locale.LC_COLLATE, 'uk_UA.UTF-8')
    except locale.Error:
        print("Locale 'uk_UA.UTF-8' not supported. Using default locale.")

    # Sort data list by the first column (name), handling None values
    data_list.sort(key=lambda x: locale.strxfrm(x['name'] if x['name'] is not None else ''))

    for data in data_list:
        row = [
            data.get('name', ''),
            data.get('area', ''),
            data.get('value', ''),
            data.get('record_number', ''),
            data.get('atk_mentioned', ''),
            data.get('cad_number', ''),
        ]
        sheet.append(row)
    
    workbook.save(excel_file)

def main(pdf_folder, excel_file):
    data_list = []
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            pdf_text = extract_text_from_pdf(pdf_path)
            parsed_data = parse_pdf_text(pdf_text)
            data_list.append(parsed_data)
    
    write_to_excel(data_list, excel_file)

if __name__ == "__main__":
    pdf_folder = "D:\Yevhenii\pdfs"
    excel_file = "D:\Yevhenii\pdfs\extracted_data.xlsx"
    main(pdf_folder, excel_file)




# COMPARE+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++




import os
import pandas as pd

# Шлях до папки з файлами .xls
folder_path = 'D:\Yevhenii\pdfs'

# Отримання списку усіх файлів у папці
files = os.listdir(folder_path)

# Відфільтрування тільки файлів з розширенням .xls або .xlsx
xls_files = [file for file in files if file.endswith('.xls')]

# Завантаження першого файлу знайденого .xls або .xlsx
if xls_files:
    file_path = os.path.join(folder_path, xls_files[0])
    df1 = pd.read_excel(file_path)
    print(f"Завантажено файл: {file_path}")
else:
    print("У папці немає файлів з розширенням .xls або .xlsx")

# Завантаження другого файлу, який ми вже знаємо
df2 = pd.read_excel('D:\Yevhenii\pdfs\extracted_data.xlsx')

# Перевірка назв стовпців
print("Стовпці у df1:", df1.columns)
print("Стовпці у df2:", df2.columns)

# З'єднання за кадастровим номером
merged_df = pd.merge(df1, df2, on='Кадастровий номер', how='left')

# Копія об'єднаного DataFrame для обробки
processing_df = merged_df.copy()

# Проходження кожним рядком у копії DataFrame
for index, row in processing_df.iterrows():
    if 'Частка' in row and row['Частка'] != 1.00:
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
merged_df.to_excel('D:\Yevhenii\pdfs\merged_file.xlsx', index=False)

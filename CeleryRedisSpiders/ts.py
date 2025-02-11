


import pandas as pd

csv_file = 'pubmed_article_data.csv'
df = pd.read_csv(csv_file)

excel_file = 'pubmed_article_data.xlsx'
df.to_excel(excel_file, index=False)

print(f"CSV 文件已成功转换为 Excel 文件，保存为 {excel_file}")


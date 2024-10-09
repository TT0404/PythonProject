import pandas as pd
from pygtrans import Translate
import os
import chardet
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 自动检测文件编码
def detect_encoding(input_file):
    with open(input_file, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']


# 转换文件编码到 UTF-8
def convert_to_utf8(input_file, temp_file):
    try:
        encoding = detect_encoding(input_file)
        logging.info(f"检测到文件编码: {encoding}")

        with open(input_file, 'r', encoding=encoding) as f:
            decoded_data = f.read()

        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(decoded_data)
        return True
    except Exception as e:
        logging.error(f"转换文件编码到 UTF-8 失败: {e}")
        return False


# 批量翻译文本
def translate_texts(texts, client, source_lang='en', target_lang='zh'):
    try:
        translations = client.translate(texts, source=source_lang, target=target_lang)
        return [translation.translatedText for translation in translations]
    except Exception as e:
        logging.error(f"翻译失败: {e}")
        return texts


# 翻译 CSV 文件的指定列
def translate_csv(input_csv, output_csv, columns_to_translate):
    temp_csv = "temp_utf8.csv"

    if not convert_to_utf8(input_csv, temp_csv):
        logging.error("文件转换失败，无法继续翻译")
        return

    if not os.path.isfile(temp_csv):
        logging.error(f"错误: 文件 {temp_csv} 不存在")
        return

    data = pd.read_csv(temp_csv)
    logging.info(f"读取数据成功，数据示例: \n{data.head()}")

    # 创建翻译客户端，不使用代理
    client = Translate()

    for column in columns_to_translate:
        if column in data.columns:
            texts_to_translate = data[column].dropna().astype(str).tolist()
            logging.info(f"开始翻译列: {column}")
            translations = translate_texts(texts_to_translate, client)

            # 确保新列的长度与原始数据框匹配
            translation_series = pd.Series(translations, index=data[column].dropna().index)
            new_column_name = f"{column}_翻译"
            data[new_column_name] = translation_series.reindex(data.index)  # 重新索引以匹配原始数据框

        else:
            logging.warning(f"列 {column} 不存在于数据中，跳过翻译")

    data.to_csv(output_csv, index=False, encoding='utf-8-sig')
    logging.info(f"翻译完成，结果保存到 {output_csv}")


if __name__ == "__main__":
    input_csv = "C:\\Users\\liFF\\Desktop\\HUAWEI-WLAN-DEVICE-MIB.csv"     # 原始文件
    output_csv = "C:\\Users\\liFF\\Desktop\\HUAWEI-WLAN-DEVICE-MIB-CN.csv"  # 翻译后的文件
    columns_to_translate = ['OBJECT_DESCRIPTION']  # 在这里替换为你想要翻译的列名,可多列翻译 格式: "['列1','列2']"

    logging.info(f"输入的 CSV 文件路径: {input_csv}")
    logging.info(f"输出的 CSV 文件路径: {output_csv}")
    translate_csv(input_csv, output_csv, columns_to_translate)

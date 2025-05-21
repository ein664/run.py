import openpyxl
from openpyxl.styles import Font
import re


def txt_to_excel(txt_path, excel_path):
    # 创建Excel工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "价格记录"

    # 添加表头
    headers = ["物品名称", "价格", "堆叠", "神器1", "神器2", "神器3", "神器4"]
    ws.append(headers)

    # 设置表头样式
    header_font = Font(bold=True, color='FF0000')
    for cell in ws[1]:
        cell.font = header_font

    # 读取并处理文件
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 初始化行数据
            row_data = [None] * 7

            # 解析物品名称（第一个冒号前）
            if ':' in line:
                parts = line.split(':', 1)
                row_data[0] = parts[0].strip()
                remaining = parts[1]
            else:
                continue

            # 提取价格（第一个数字）
            price_match = re.search(r'([\d.]+)', remaining)
            if price_match:
                row_data[1] = price_match.group(1)
                # 移除已提取的价格部分
                remaining = remaining[price_match.end():]

            # 使用正则表达式提取所有键值对
            pattern = r'(\S+)[：:]\s*(\S+)'
            matches = re.findall(pattern, remaining)
            data_dict = dict(matches)

            # 填充堆叠数据
            if '堆叠' in data_dict:
                row_data[2] = data_dict['堆叠']

            # 填充神器数据
            if '神器' in data_dict and '神器种类' in data_dict:
                artifact_type = data_dict['神器种类']
                artifact_value = data_dict['神器']
                col_index = 3 + int(artifact_type) - 1  # 计算正确的列索引
                if 3 <= col_index <= 6:  # 确保列索引在有效范围内
                    row_data[col_index] = artifact_value

            # 添加行数据
            ws.append(row_data)

    # 调整列宽
    for col in ws.columns:
        max_length = max(
            (len(str(cell.value)) for cell in col),
            default=0
        )
        column_letter = col[0].column_letter
        ws.column_dimensions[column_letter].width = max_length + 2

    # 保存Excel文件
    wb.save(excel_path)
    print(f"Excel文件已成功生成：{excel_path}")


# 使用示例
txt_path = r"C:\PythonCode\pyqt\Record_price.txt"
excel_path = r"C:\PythonCode\pyqt\Record_price.xlsx"
txt_to_excel(txt_path, excel_path)
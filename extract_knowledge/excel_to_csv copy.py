import pandas as pd
import sys


def build_hierarchy(df):
    name_to_parent = {}
    name_to_children = {}
    
    ROOT_KEY = '__ROOT__'
    
    for _, row in df.iterrows():
        parent = row['上级目录']
        name = row['目录名']
        
        if pd.isna(parent):
            parent_key = ROOT_KEY
        else:
            parent_key = parent
        
        name_to_parent[name] = parent
        
        if parent_key not in name_to_children:
            name_to_children[parent_key] = []
        name_to_children[parent_key].append(name)
    
    return name_to_parent, name_to_children, ROOT_KEY


def traverse(name, name_to_parent, name_to_children, path, results, max_depth):
    new_path = path + [name]
    
    if len(new_path) >= max_depth:
        results.append(new_path)
        return
    
    children = name_to_children.get(name, [])
    
    if not children:
        results.append(new_path)
        return
    
    for child in children:
        traverse(child, name_to_parent, name_to_children, new_path, results, max_depth)


def extract_levels(max_depth):
    input_file = 'c:/Users/win/Desktop/4/result_expanded.xlsx'
    output_file = 'c:/Users/win/Desktop/4/result_tree.csv'
    
    df = pd.read_excel(input_file)
    
    name_to_parent, name_to_children, root_key = build_hierarchy(df)
    
    root_nodes = name_to_children.get(root_key, [])
    
    results = []
    for root in root_nodes:
        traverse(root, name_to_parent, name_to_children, [], results, max_depth)
    
    columns = [f'Level{i+1}' for i in range(max_depth)]
    
    df_result = pd.DataFrame(results)
    df_result.columns = columns[:len(df_result.columns)]
    
    for i in range(len(df_result.columns), max_depth):
        df_result[columns[i]] = ''
    
    df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f'Successfully converted! Output file: {output_file}')
    print(f'Total rows: {len(df_result)}')
    print(f'Levels: {max_depth}')
    
    return df_result


def main():
    if len(sys.argv) > 1:
        try:
            max_depth = int(sys.argv[1])
        except ValueError:
            print('Please provide a valid number for levels')
            return
    else:
        print('Excel文件中有以下层级结构：')
        print('  Level1: 第一章 集合, 第二章 函数, 高考新题型...')
        print('  Level2: Venn图法解决集合运算问题, 函数的解析式求法, 开放性试题...')
        print('  Level3: 利用Venn图求解交集、并集与补集, 待定系数法求函数解析式, 条件补充型求解...')
        print('  Level4: 已知函数类型求解析式, 直接换元法...')
        print('  Level5: 更深层的考法...')
        print()
        
        while True:
            try:
                max_depth = int(input('请输入要提取的层级数(1-5): '))
                if 1 <= max_depth <= 5:
                    break
                else:
                    print('请输入1到5之间的数字')
            except ValueError:
                print('请输入有效的数字')
    
    extract_levels(max_depth)


if __name__ == '__main__':
    main()
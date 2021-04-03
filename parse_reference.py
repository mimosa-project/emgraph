import glob
import json
import os
import re
import itertools
from pathlib import Path
from pprint import pprint

MML_DIRECTORY_PATH = Path("mml")



def get_mizfiles_name():
    """
    MML_DIRECTORY_PATH内のmizファイルの名前の一覧をリストで取得する
    """
    cwd = os.getcwd()
    try:
        os.chdir(MML_DIRECTORY_PATH)
        miz_files = glob.glob("*.miz")
    finally:
        os.chdir(cwd)

    return miz_files

def read_miz_file(miz_file):
    """
    引数で指定したmizファイルをreadlinesで読み込む。
    Args:
        miz_file: 読み込むファイル
    Return:
        読み込んだファイルの名前(str)と中身(list)
    """
    text_lines = []

    cwd = os.getcwd()
    try:
        os.chdir(MML_DIRECTORY_PATH)
        with open(miz_file, encoding="utf-8", errors="ignore") as f:
            # ファイル名の.mizの部分を除去し大文字に
            file_name = str.upper(miz_file[0:-4])
            text_lines = f.readlines()

    finally:
        os.chdir(cwd)

    return file_name, text_lines


def make_quotation_dict(file_name, text_lines, quotation_dict):
    """
    mizファイルから引用部を抜き出した辞書を作成する
    Args:
        file_name: ファイル名(例:ABCMIZ_0)
        text_lines: ファイルの中身をリストで保持
        quotation_dict: 出力を格納するための入れ物
            {
                "ABCMIZ_0:1" : [参照先のリスト],
                "ABCMIZ_0:2" : [],
                ...
            }
    """

    label_dict = make_Label_dict(text_lines)
    
    is_theorem = False
    is_def = False
    is_numbered_definition = False
    defpred_flag = False
    is_contains_lf = False  # 複数行に渡って書かれていればTrue
    theorem_number = 0
    def_number = 0
    prev_line = ''  # by以降が複数行にわたるときに前の行を保存しておく
    
    
    for line in text_lines:
        #print(line) #テスト用
        # theoremの終わり
        if line == '\n' and is_theorem == True:
            is_theorem = False

        # definitionの終わり判定
        if line == "end;\n" and is_def == True:
            is_def = False
            is_numbered_definition = False

        
        # コメント行読み飛ばし、またCT、CDの処理
        if re.match(r'::', line):
            if re.match(r"::\$CT", line):
                if re.search(r'\d+', line):
                    theorem_number = theorem_number + int(re.sub("\D*", "", line))
                else:
                    theorem_number += 1

            if re.match(r"::\$CD", line):
                if re.search(r'\d+', line):
                    def_number = def_number + int(re.sub("\D*", "", line))
                else:
                    def_number += 1

            continue

        # theoremの始まり判定
        if re.match(r"\btheorem\b", line):
            is_theorem = True
            theorem_number += 1
            quotation_dict[file_name + ':' + str(theorem_number)] = list()
            continue

        # definitionの始まり判定
        if re.match(r"\bdefinition\b", line):
            is_def = True
            continue
        
        # defpredが複数行になっている場合それらを一行にまとめる
        if defpred_flag == True:
            line = prev_line + ' ' + line
            defpred_flag = False
        if is_def == True and re.search(r"\bdefpred\b", line):
            if re.search(r"\bdefpred\b.*;", line):
                pass
            else:
                prev_line = line[:-1]
                defpred_flag = True
                continue

        # definitionの番号を割り当てる
        if not re.search(r"\bdefpred\b.*;", line) and re.search(r"means|equals", line) and is_def:
            def_number += 1
            is_numbered_definition = True  
            quotation_dict[file_name + ':def' + str(def_number)] = list()
            continue

        #theoremとdefinitionの中
        if is_theorem == True or is_def == True and is_numbered_definition == True:

            # by以降が複数行にわたる時それらを1行にまとめる
            if is_contains_lf:
                line = prev_line + ' ' + line
                is_contains_lf = False

            #by～;までに改行が含まれない場合
            m = re.search(r"\sby.*\.=|\sby.*;|\sfrom.*\(|\sfrom .*;", line):
            if m:
                quoted_part = m  # 引用部を文字列のまま抜き出す
                if quoted_part != None:
                    quotation = extract_quoted_parts(quoted_part.group(), label_dict, file_name)
                if quotation:
                    # theoremの場合キーは"filename:番号"
                    if is_theorem:
                        quotation_dict[file_name + ':' + str(theorem_number)].append(quotation)
                    # definitionの場合キーは"filename:def番号
                    if is_def and is_numbered_definition:
                        quotation_dict[file_name + ':def' + str(def_number)].append(quotation)
                    continue
                continue

            #by～;までに改行が含まれる場合
            if re.search(r"by.*\n|from.*\n", line):
                prev_line = line.rstrip('\r\n')  # 末尾の改行を除いた部分を保存
                is_contains_lf = True
                continue

    return quotation_dict

def extract_quoted_parts(quoted_part, label_dict, filename):
    """
    引用部文字列から引用元だけをリストにまとめる。
    また、引用元の名前を修正
    Args:
        quoted_part: 引用部分(例："by ~ ;" , "from ~ ;")
        label_dict: ファイル内のtheoremとdefinitionのラベル(Th1:1,Th2:2,...)をまとめたリスト
        filename: ファイルの名前
    Return:
        引用だけをまとめたリスト
    """
    removed = re.sub("by|from|\s|;|\n|\.=|\(", '', quoted_part)  # 必要のないものを除去
    refs = removed.split(',')

    renamed_refs = list()

    #theoremの名前を変更し、同じ命題内での引用を除去
    for r in refs:

        if r in label_dict:
            renamed_refs.append(filename + ':' + label_dict[r])
        else:
            # 別ファイルからの引用の場合
            if ':' in r:
                renamed_refs.append(r)
            



    return renamed_refs

        
def make_Label_dict(text_lines):
    """
    theoremとdefinitionのラベルをまとめたリストをつくる
    Args:
        text_lines:
    Return:
        label_dict: keyがファイル名、valueがラベルと番号をまとめたdict
                　label_dict = {
                    Th1: 1,
                    Th2: 2,
                    Th4: 4,
                    ...
                  }
    """
    label_dict = dict()
    th_num = 0
    def_num = 0
    in_def = False
    prev_line = ''
    defpred_flag = False
    for line in text_lines:
        # ::$CT(canceled theorem)の処理
        if re.match(r"::\$CT", line):
            if re.search(r'\d+', line):
                th_num = th_num + int(re.sub("\D*", "", line))
            else:
                th_num += 1

        # ::$CD(canceled definition)の処理
        if re.match(r"::\$CD", line):
            if re.search(r'\d+', line):
                def_num = def_num + int(re.sub("\D*", "", line))
            else:
                def_num += 1

        # theoremのラベルについての処理
        if re.match(r"\btheorem\b",line):
            # ラベルがあるとき
            m = re.match(r"theorem\s+([a-zA-Z0-9]+):", line)
            if m:
                th_num += 1
                label_dict[m.group(1)] = str(th_num)
                continue
            # ラベルがないとき
            else:
                th_num += 1
                continue


        # definitionのラベルについての処理
        if line == "end;\n" and in_def == True:
            in_def = False

        if re.match(r"\bdefinition\b", line):
            in_def = True
            continue
    
        if defpred_flag == True:
            line = prev_line + ' ' + line
            defpred_flag = False
        if in_def == True and re.search(r"\bdefpred\b", line):
            if re.search(r"\bdefpred\b.*;", line):
                pass
            else:
                prev_line = line[:-1]
                defpred_flag = True
                continue

        if not re.search(r"\bdefpred\b.*;", line) and re.search(r"means|equals", line) and in_def:
            def_num += 1

        m = re.search(r":([a-zA-Z0-9]+):", line)
        if m and in_def:
            label_dict[re.search(r":([a-zA-Z0-9]+):", line).group(1)] = "def" + str(def_num)


    return label_dict



def reformat_quotation_dict(quotation_dict):
    """
    quotation_dictに対してグラフのノード化のために
        - 参照先のリストをフラットにする
        - 定理のURLを追加
    を行う。
    Args:
        quotation_dict(整形前)
        {
            "ABCMIZ_0:1" : [参照先のリスト],
            "ABCMIZ_0:2" : [],
            ...
        }
    Return:
        keyが参照元(str)、valueが参照先(list)とURL(str)の辞書
        例:{
            "ABCMIZ_0:1" : {
                "dependency_article": [参照先のリスト],
                "url": "参照元定理(ABCMIZ_0:1)のurl
            },
            "ABCMIZ_0:2" : {},
            ...
        }
    """
    # quotation_dictのvalueのリストをフラットに
    for key, value in quotation_dict.items():
        quotation_dict[key] = list(set(list(itertools.chain.from_iterable(value))))

    reformatted_dict = dict()
    for key, value in quotation_dict.items():
        reformatted_dict[key] = dict()
        reformatted_dict[key]["dependency_articles"] = list()

        for v in value:
            if v in quotation_dict.keys() and not v is key:
                reformatted_dict[key]["dependency_articles"].append(v)

        # definitionのURL追加
        if 'def' in key:
            reformatted_dict[key]['url'] = "http://mizar.org/version/current/html/"\
                                + str.lower(re.sub(r':.*', '', key)) + ".html#D" + re.sub(r'.*:def', '', key)
        # theoremのURL追加
        else:
            reformatted_dict[key]['url'] = "http://mizar.org/version/current/html/"\
                                + str.lower(re.sub(r':.*', '', key)) + ".html#T" + re.sub(r'.*:', '', key)

    return reformatted_dict
    

def main():
    mizfiles = get_mizfiles_name()
    quotation_dict = dict()
    
    for m in mizfiles:
        print("processing file: " + m)
        fn, tl = read_miz_file(m)
        make_quotation_dict(fn, tl, quotation_dict)


    nodes = reformat_quotation_dict(quotation_dict)
    with open("nodes1.json", mode='w') as f:
        json.dump(nodes, f, indent=4)

if __name__ == "__main__":
    main()

import glob
import json
import os
import re
import itertools
from pathlib import Path
from pprint import pprint

MML_DIRECTORY_PATH = Path("mmlfull")

def read_miz_files():
    """
    MML_DIRECTORY_PATHで指定したディレクトリ内のmizファイルをすべて読み込む。
    Args:
    Return:
        text_lines: keyがmizファイル名、valueがファイルの中身
    """
    text_lines = dict()

    cwd = os.getcwd()
    try:
        os.chdir(MML_DIRECTORY_PATH)
        miz_files = glob.glob("*.miz")
        for mf in miz_files:
            with open(mf, encoding="utf-8", errors="ignore") as f:
                filename = str.upper(mf[0:-4])  # ファイル名の.mizの部分を除去 
                text_lines[filename] = f.readlines()

    finally:
        os.chdir(cwd)

    return text_lines



def make_quotation_dict(text_lines):
    """
    mizファイルから引用部を抜き出した辞書を作成する
    Args:
        text_lines: keyがmizファイル名、valueがファイルの中身
    Return:
        nodes = {
        }

    """
    # 全ファイルのtheoremのラベルを取得
    th_label = make_ThLabel_dict(text_lines)

    quotation_dict = dict()
    pattern = r"begin"\
                "|theorem.*\n"\
                "|definition.*\n"\
                "|registration.*\n"\
                "|notation.*\n"\
                "|reserve"\
                "|::.CT"\
                "|::.CD"
    
    for filename, lines in text_lines.items():

        is_theorem = False
        is_def = False
        exist_key = False
        is_contains_lf = False
        theorem_number = 0
        def_number = 0
        prev_line = ''  # by以降が複数行にわたるときに前の行を保存しておく
        
        for line in lines:
            # theoremの終わり
            if line == '\n' and is_theorem == True:
                is_theorem = False

            # definitionの終わり判定
            if is_def == True and re.match(pattern, line):
                is_def = False
                exist_key = False

            # コメント行読み飛ばし、またCT、CDの処理
            if re.match(r'::', line):
                if re.match(r"::.CT", line):
                    if re.search(r'\d+', line):
                        theorem_number = theorem_number + int(re.sub("\D*", "", line))
                    else:
                        theorem_number += 1
                
                if re.match(r"::.CD", line):
                    if re.search(r'\d+', line):
                        def_number = def_number + int(re.sub("\D*", "", line))
                    else:
                        def_number += 1

                continue
            

            # theoremの始まり判定
            if line == "theorem\n" or line[0:8] == "theorem " or re.match(r"Th\d+", line):
                is_theorem = True
                theorem_number += 1
                quotation_dict[filename + ':' + str(theorem_number)] = list()
                continue
                     
            # definitionの始まり判定
            if line == "definition\n" or line[0:11] == "definition ":
                is_def = True
                continue

            # definitionの番号を割り当てる
            if not re.search(r"defpred", line) and re.search(r"means|equals", line) and is_def:
                def_number += 1
                exist_key = True
                quotation_dict[filename + ':def' + str(def_number)] = list()
                continue

            #theoremとdefinitionの中
            if is_theorem == True or is_def == True and exist_key == True:
                
                # by以降が複数行にわたる時それらを1行にまとめる
                if is_contains_lf:
                    line = prev_line + ' ' + line
                    is_contains_lf = False

                #by～;までに改行が含まれない場合
                if re.search(r"\sby.*\.=|\sby.*;|\sfrom.*\(|from .*;", line):
                    quoted_part = re.search(r"\sby.*\.=|\sby.*;|\sfrom.*\(|\sfrom.*;", line)  # 引用部を文字列のまま抜き出す
                    if quoted_part != None:
                        quotation = extract_quoted_parts(quoted_part.group(), th_label[filename], filename)
                    if quotation:
                        # theoremの場合キーは"filename:番号"
                        if is_theorem:
                            quotation_dict[filename + ':' + str(theorem_number)].append(quotation)
                        # definitionの場合キーは"filename:def番号
                        if is_def and exist_key:
                            quotation_dict[filename + ':def' + str(def_number)].append(quotation)
                        continue
                    continue

                #by～;までに改行が含まれる場合
                if re.search(r"by.*\n|from.*\n", line):
                    prev_line = line[:-1]  # 末尾の改行を除いた部分を保存
                    is_contains_lf = True
                    continue

            

                    

    #quotation_dictのvalueのリストをフラットに
    for key, value in quotation_dict.items():
        quotation_dict[key] = list(set(list(itertools.chain.from_iterable(value))))

    #urlを追加するために整形
    nodes = dict()
    for key, value in quotation_dict.items():
        nodes[key] = dict()
        nodes[key]["dependency_articles"] = list()
        
        for v in value:
            if v in quotation_dict.keys() and not v is key:
                nodes[key]["dependency_articles"].append(v)

        # definitionのURL追加
        if 'def' in key:
            nodes[key]['url'] = "http://mizar.org/version/current/html/"\
                                + str.lower(re.sub(r':.*', '', key)) + ".html#D" + re.sub(r'.*:def', '', key)
        # theoremのURL追加
        else:
            nodes[key]['url'] = "http://mizar.org/version/current/html/"\
                                + str.lower(re.sub(r':.*', '', key)) + ".html#T" + re.sub(r'.*:', '', key)

    return nodes



def extract_quoted_parts(quoted_part, th_label_dict, filename):
    """
    引用部文字列から引用元だけをリストにまとめる。
    また、引用元の名前を修正
    Args:
        quoted_part: 引用部分(例："by ~ ;" , "from ~ ;")
        th_label_dict: ファイル内のtheoremのラベル(Th1:1,Th2:2,...)をまとめたリスト
        filename: ファイルの名前
    Return:
        引用元だけをまとめたリスト
    """
    removed = re.sub("by|from|\s|;|\n|\.=|\(", '', quoted_part)  # 必要のないものを除去
    quotation1 = removed.split(',')

    quotation2 = list()

    #theoremの名前を変更し、同じ命題内での引用を除去
    for q in quotation1:

        if q in th_label_dict.keys():
            quotation2.append(filename + ':' + th_label_dict[q])
        else:
            # 別ファイルからの引用の場合
            if ':' in q:
                quotation2.append(q)
            
            # 同じファイルのdefの引用の場合
            if re.search(r"Def\d*", q):
                quotation2.append(filename + ':' + str.lower(q))



    return quotation2



def make_ThLabel_dict(text_lines):
    """
    各ファイルのtheoremのラベルをまとめたリストをつくる
    Args:
        text_lines: mizファイル
    Return:
        th_label: keyがファイル名、valueがtheoremのラベルと番号をまとめたdict
                　th_label = {
                    ファイル１: {Th1:1,Th3:3,Th4:4},
                    ファイル２: {Th2:2,Th3:3},
                    ...
                  }
    """
    th_label = dict()

    for filename, lines in text_lines.items():
        th_label[filename] = dict()
        number = 0
        for line in lines:
            # ::$CT(canceled theorem)の処理
            if re.match(r"::.CT", line):
                number += 1

            # ラベルがついてないtheorem
            if line == "theorem\n":
                number += 1
                continue

            # ラベルがついたtheoremはそのラベルと番号を紐づける
            if line[0:8] == "theorem ":
                number += 1
                th_label[filename][re.sub("theorem\s|:|\n", "", line)] = str(number)

    return th_label


# -----------------------------------------------------------------------------------------
text = read_miz_files()
nodes = make_quotation_dict(text)


with open("nodes.json", mode='w') as f:
    json.dump(nodes, f, indent=4)

#pprint(nodes)
        
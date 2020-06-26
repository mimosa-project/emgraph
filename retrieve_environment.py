import os
import glob
from pathlib import Path
MIZAR_LIBRARY_DIRECTORY_PATH = Path("mml")


def make_library_dependency():
    """
    各カテゴリ内で参照しているファイルを取得する。
    Args:
    Return:
        miz_file_dict: 各カテゴリ(vocabularies, constructors等)において、各ライブラリが
                       どのライブラリを参照しているかを示す辞書。
                       例：lib_aがlib_x, lib_y, ... をvocabulariesで参照している場合、
                        miz_file_dict = {
                            'vocabularies': {
                                'lib_a': {'lib_x', 'lib_y', ...},
                                ...
                            }
                            'constructors': { ... },
                            ...
                        }
    """
    miz_files_dict = dict()
    categories = ['vocabularies', 'constructors', 'notations', 'registrations', 'theorems', 'schemes',
                  'definitions', 'requirements', 'expansions', 'equalities']
    for category in categories:
        miz_files_dict[category] = dict()

    cwd = os.getcwd()
    try:
        os.chdir(MIZAR_LIBRARY_DIRECTORY_PATH)
        miz_files = glob.glob("*.miz")  # mmlディレクトリの.mizファイルを取り出す
        
        category_dict = create_key2list(categories)

    finally:
        os.chdir(cwd)

    return miz_files_dict


def extract_articles(contents):
    """
    mizファイルが環境部(environ~begin)で参照しているarticleを
    各カテゴリごとに取得する。
    Args:
        contents: mizファイルのテキスト(内容)
    Retrun:
        category2articles: keyがカテゴリ名、valueが参照しているarticleのリスト
    """
    category2articles = create_key2list(CATEGORIES)
    # 単語、改行、::、;で区切ってファイルの内容を取得
    file_words = re.findall(r"\w+|\n|::|;", contents)
    is_comment = False
    environ_words = list()

    # mizファイルから環境部を抜き出す
    for word in file_words:
        # コメント行の場合
        if word == "::" and not is_comment:
            is_comment = True
            continue
        # コメント行の終了
        if re.search(r"\n", word) and is_comment:
            is_comment = False
            continue
        # コメント以外の部分(environ ~ beginまで)
        if not is_comment:
            environ_words.append(word)
            # 本体部に入ったら、ループから抜け出す
            if re.match(r"begin", word):
                break

    # 改行文字の削除
    environ_words = [w for w in environ_words if not re.match(r"\n", w)] 

    # カテゴリでどのarticleを参照しているかを得る
    category_name = str()
    for word in environ_words:
        # 環境部の終了条件
        if re.match(r"begin", word):
            break
        # カテゴリ名が来たとき
        if word in category2articles.keys():
            category_name = word
            continue
        # ;でそのカテゴリでの参照が終わったとき
        if re.match(r";", word):
            category_name = str()
            continue
        # カテゴリ名が決まっているとき
        if category_name:
            category2articles[category_name].append(word)
        
    return category2articles


def create_key2list(keys):
    """
    keyがkeys，valueがlist()の辞書を作成する．
    Args:
        keys: keyに設定したい値(リスト)
    return:
        key2list: keyがkeys，valueがlist()の辞書
    """
    key2list = dict()
    for i in keys:
        key2list[i] = list()
    return key2list


def create_key2False(keys):
    """
    keyがkeys，valueがFalseの辞書を作成する．
    Args:
        keys: keyに設定したい値(リスト)
    return:
        key2false: keyがkeys，valueがFalseの辞書
    """
    key2false = dict()
    for k in keys:
        key2false[k] = False
    return key2false


def remove_comment(line):
    """
    与えられた文字列の"::"以降(右)を除去する
    Args:
        line: コメントを取り除きたい文字列
    Return:
        先頭がコメントだった場合(コメントのみの行だった場合): 空文字
        それ以外: コメント部分を取り除いた文字列
    """
    return "" if line.index("::") == 0 else line.split("::")[0]


def switch_to_true_only_select_key(key2bool, select_key):
    """
    選択したkeyのvalueをTrueに，それ以外のkeyのvalueをFalseにする．
    Args:
        key2bool: 全てのvalueがbool値になっている辞書
        select_key: valueをTrueにしたいkey2bool内の1つのkey
    Return:
        key2bool: key=select_keyのvalueをTrue、その他のkeyのvalueをFalseにした辞書
    """
    for k in key2bool:
        key2bool[k] = False
    key2bool[select_key] = True
    return key2bool

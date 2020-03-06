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
        
        category_dict = create_category2list(categories)

    finally:
        os.chdir(cwd)

    return miz_files_dict


def create_category2list(categories):
    """
    環境部の各カテゴリー名をキーとし、空リストを値とする辞書の作成を行う。
    key=カテゴリー名, value=list()
    Args:
        categories: 環境部のカテゴリー名をまとめたリスト
    Return:
        dict: {"vocabularies": list(), "constructors": list(), "notations": list(), ...}
    """
    return dict.fromkeys(categories, list())


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

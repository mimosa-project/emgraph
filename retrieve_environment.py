import os
import glob
from pathlib import Path


def make_library_dependence():
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

    path = Path("mml")
    os.chdir(path)
    miz_files = glob.glob("*.miz")  # mmlディレクトリの.mizファイルを取り出す

    os.chdir("../")

    return miz_files_dict

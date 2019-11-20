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

    finally:
        os.chdir(cwd)

    return miz_files_dict

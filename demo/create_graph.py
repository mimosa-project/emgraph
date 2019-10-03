"""
依存関係を階層形式で表示する
・階層化の手順
　　1. 階層割当
　　2. 交差削減
　　3．座標決定
"""
import networkx as nx
import json


class Node:
    """
    ノードをクラスとして定義する。
    Attributes:
        name: ノードの名前。str()。
        target_nodes: 自身が指しているノードの集合。set()。デフォルトは空集合set()。
        source_nodes: 自身を指しているノードの集合。set()。デフォルトは空集合set()。
        x, y: ノードの座標(x,y)。ともにint()。デフォルトは-1。
        href: ノードのリンク。str()。デフォルトは空列 ""。
        is_dummy: ノードがダミーか否か。bool()。デフォルトはFalse。
    """

    def __init__(self, name, target_nodes=None, source_nodes=None, x=None, y=None, href=None, is_dummy=None):
        self.name = name
        self.target_nodes = set() if target_nodes is None else target_nodes
        self.source_nodes = set() if source_nodes is None else source_nodes
        self.x = -1 if x is None else x
        self.y = -1 if y is None else y
        self.href = "" if href is None else href
        self.is_dummy = False if is_dummy is None else is_dummy

    def __str__(self):
        name = self.name
        target_nodes = self.target_nodes
        source_nodes = self.source_nodes
        x = self.x
        y = self.y
        return f"name: {name}, target_nodes: {target_nodes}, source_nodes: {source_nodes}, (x, y)= ({x}, {y})"


def create_node_list(input_node_dict):
    """
    input_node_dictをNodeクラスでインスタンス化したものをリストにまとめる。
    各属性には次の物を格納する。
        ・name:  input_node_dictのkey。str。
        ・target_nodes: input_node_dictのvalueの第一要素。set()。
        ・source_nodes: target_nodesをもとに作成したsource_nodes。set()。
        ・x, y: -1。int。
        ・href: INPUT_NODE_DICTのvalueの第二要素。str。
        ・is_dummy: False。bool。

    Args:
        input_node_dict: 入力されたノードの関係を示す辞書型データ。
                         ノードの名前をキーに持ち、値としてリストを持つ。リストの要素は次のようになる。
                             第1要素: keyのノードが指すノードの集合。set()
                             第2要素: keyのノードのリンク先URL。str()   
        
    Returns:
        インスタンス化されたノードのリスト。
    """
    node_list = []
    name2node = {}
    # node_dict, node_listの作成
    # k: ノードの名前(str)、v[1]: ノードkのリンクURL(str)
    for k, v in input_node_dict.items():
        n = Node(name=k, href=v[1])
        name2node[k] = n
        node_list.append(n)

    # target_nodesの作成
    # k: ノードの名前(str)、v[0]: ノードkがターゲットとするノードの名前(str)の集合
    for k, v in input_node_dict.items():
        for target in v[0]:
            name2node[k].target_nodes.add(name2node[target])

    # source_nodesの作成
    # k: ノードの名前(str)、v: ノードkのNodeオブジェクト(object)
    for k, v in name2node.items():
        for target in v.target_nodes:
            target.source_nodes.add(name2node[k])
    return node_list
            
            
def main():
    """
    関数の実行を行う関数。

    Return:
    """
    import random

    def shuffle_dict(d):
        """
        辞書（のキー）の順番をランダムにする
        Args:
            d: 順番をランダムにしたい辞書。
        Return:
            dの順番をランダムにしたもの
        """
        keys = list(d.keys())
        random.shuffle(keys)
        return dict([(key, d[key]) for key in keys])

    """
       input_node_dict: 全ノードについての情報を辞書にまとめたもの。dict()
           key: ノードの名前。
           value: リスト
               第1要素: keyのノードが指すノードの集合。set()
               第2要素: keyのノードのリンク先URL。str()

    """
    input_node_dict = {"a": [set(), "example.html"],
                       "b": [{"a"}, "example.html"],
                       "c": [{"b", "e"}, "example.html"],
                       "d": [{"c", "a"}, "example.html"],
                       "e": [{"a"}, "example.html"],
                       "f": [{"e", "b", "a"}, "example.html"],
                       "g": [{"e"}, "example.html"],
                       "h": [{"g", "f"}, "example.html"],
                       "i": [{"a"}, "example.html"],
                       "j": [{"i"}, "example.html"],
                       "k": [{"j", "m"}, "example.html"],
                       "l": [{"i", "a"}, "example.html"],
                       "m": [{"i"}, "example.html"],
                       "n": [{"j", "m"}, "example.html"],
                       "o": [{"m", "l"}, "example.html"],
                       "p": [{"n", "k"}, "example.html"],
                       "q": [{"k", "o", "i"}, "example.html"],
                       }

    node_list = create_node_list(shuffle_dict(input_node_dict))
    
    
if __name__ == "__main__":
    main()
    

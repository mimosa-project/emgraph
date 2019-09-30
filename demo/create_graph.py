"""
依存関係を階層形式で表示する
・階層化の手順
　　1. 階層割当
　　2. 交差削減
　　3．座標決定
"""
import networkx as nx
import json

"""
INPUT_NODE_DICT: 全ノードについての情報を辞書にまとめたもの。dict()
    key: ノードの名前。
    value: リスト
        第1要素: keyのノードが指すノードの集合。set()
        第2要素: keyのノードのリンク先URL。str()

"""

INPUT_NODE_DICT = {"f": [{"e", "b", "a"}, "example.html"], "g": [{"e"}, "example.html"],
                   "h": [{"g", "f"}, "example.html"], "i": [{"a"}, "example.html"], "o": [{"m", "l"}, "example.html"],
                   "p": [{"n", "k"}, "example.html"], "q": [{"k", "o", "i"}, "example.html"],
                   "j": [{"i"}, "example.html"], "k": [{"j", "m"}, "example.html"], "l": [{"i", "a"}, "example.html"],
                   "m": [{"i"}, "example.html"], "n": [{"j", "m"}, "example.html"], "a": [set(), "example.html"],
                   "b": [{"a"}, "example.html"], "c": [{"b", "e"}, "example.html"], "d": [{"c", "a"}, "example.html"],
                   "e": [{"a"}, "example.html"]}


class Node:
    """
    ノードをクラスとして定義する。

    Attributes:
        name: ノードの名前。str()。
        target_nodes: 自身が指しているノードの集合。set()。
        source_nodes: 自身を指しているノードの集合。set()。
        x, y: ノードの座標(x,y)。ともにint()。
        href: ノードのリンク。str()。
        is_dummy: ノードがダミーか否か。bool()。
    """
    def __init__(self, name, target_nodes, source_nodes, x, y, href, is_dummy):
        self.name = name
        self.target_nodes = target_nodes
        self.source_nodes = source_nodes
        self.x = x
        self.y = y
        self.href = href
        self.is_dummy = is_dummy

    def __str__(self):
        name = self.name
        target_nodes = self.target_nodes
        source_nodes = self.source_nodes
        x = self.x
        y = self.y
        return f"name: {name}, target_nodes: {target_nodes}, source_nodes: {source_nodes}, (x, y)= ({x}, {y})"


def create_node_list():
    """
    INPUT_NODE_DICTをNodeクラスでインスタンス化したものをリストにまとめる。
    各属性には次の物を格納する。
        ・name:  INPUT_NODE_DICTのkey。str。
        ・target_nodes: INPUT_NODE_DICTのvalueの第一要素。set()。
        ・source_nodes: INPUT_NODE_DICTを用いてsourceとなるノードを検索し、まとめた集合source_nodes。set()。
        ・x, y: -1。int。
        ・href: INPUT_NODE_DICTのvalueの第二要素。str。
        ・is_dummy: False。bool。

    Args:
        INPUT_NODE_DICT（global）
    Returns:
        インスタンス化されたノードのリスト。
    """
    node_data_list = []
    for node_name, node_data in INPUT_NODE_DICT.items():
        # source_nodesの作成
        source_nodes = set()
        for source, source_data in INPUT_NODE_DICT.items():
            for target_node in source_data[0]:
                if target_node == node_name:
                    source_nodes.add(source)
        # node_date_listの作成
        n = Node(node_name, node_data[0], source_nodes, -1, -1, node_data[1], False)
        node_data_list.append(n)
    return node_data_list


def create_dependence_graph(graph, node_list):
    """
    依存関係を示すグラフを作成する。

    Args:
        graph:操作するグラフ。
        node_list:全ノードをNodeクラスでまとめたリスト。

    Return:
    """
    for source_node in node_list:
        graph.add_node(source_node.name)
        for target_node in source_node.target_nodes:
            graph.add_node(target_node)
            graph.add_edge(source_node.name, target_node)


"""
#1．階層割当(最長パス法)
"""


def assign_top_node(node_list):
    """
    グラフのルートを決定する。ルートは矢印が出ていない(参照をしていない)ノードとなる。
　　その後、level2node()でその下の階層のノードを決めていく。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。

    Return:

    """
    for top_node in node_list:
        if set() == top_node.target_nodes:
            top_node.y = 0
            top_node.x = 0
            assign_level2node_recursion(node_list, top_node, 0)


def assign_level2node_recursion(node_list, target, target_level):
    """
    階層が1以上（y座標が1以上）のノードの階層を再帰的に決定する。階層の割当は次のルールに従う。
    ・まだ階層を割り当てていないノードならば、targetの1つ下の階層に割り当てる。
    ・既に座標を割り当てており、その階層が今の階層(source_node_level)以上高い階層ならば、一つ下の階層に再割当する。
　　・既に階層を割り当てており、その階層が今の階層よりも低い階層ならば、何もしない。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。
        target: ターゲットとなるノード。このノードを指すノードに階層を割り当てていく。
        target_level: targetの階層。targetを指すノードは基本的にこの階層の1つ下の階層に割り当てられる。
    """
    assign_node_level = target_level + 1
    for assign_node_name in target.source_nodes:
        assign_node = [source for source in node_list if source.name == assign_node_name][0]
        if assign_node.x < 0:
            assign_node.y = assign_node_level
            assign_node.x = 0
            assign_level2node_recursion(node_list, assign_node, assign_node_level)
        if assign_node.x > -1 and assign_node.y <= assign_node_level:
            assign_node.y = assign_node_level
        else:
            pass


def assign_x_coordinate(node_list):
    """
    全てのノードに対して、x座標を割り当てる。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。

    Return:
    """
    below_level = max([node.y for node in node_list])
    assigning_level = 0
    while assigning_level <= below_level:
        x_coordinate = 0
        for equal_level_node in [node for node in node_list if node.y == assigning_level]:
            equal_level_node.x = x_coordinate
            x_coordinate += 1
        assigning_level += 1


def node_list2node_dict(node_list):
    """
    ノードについての情報（属性）をリスト形式から辞書形式に変換する。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。

    Return:
        各ノードのname, href, x, y, is_dummyを持つ辞書。
        キーはnameで、その値としてhref, x, y, is_dummyをキーに持つ辞書が与えられる。
        例:
        node_dict = {"f": { "href": "example.html", "x": 0, "y": 2, "is_dummy": false}, ... }
    """
    node_dict = {}
    for node in node_list:
        node_name = str(node.name)
        node_dict[node_name] = {}
        node_dict[node_name]["href"] = str(node.href)
        node_dict[node_name]["x"] = int(node.x)
        node_dict[node_name]["y"] = int(node.y)
        node_dict[node_name]["is_dummy"] = bool(node.is_dummy)
    return node_dict


def main():
    """
    関数の実行を行う関数。

    Return:
    """
    node_list = create_node_list()

    # 有向グラフGraphの作成
    graph = nx.DiGraph()

    create_dependence_graph(graph, node_list)
    assign_top_node(node_list)
    assign_x_coordinate(node_list)
    node_attributes = node_list2node_dict(node_list)

    # nodes_attrsを用いて各ノードの属性値を設定
    nx.set_node_attributes(graph, node_attributes)

    # グラフの描画
    nx.draw_networkx(graph)

    # cytoscape.jsの記述形式(JSON)でグラフを記述
    graph_json = nx.cytoscape_data(graph, attrs=None)

    with open('demo_sample.json', 'w') as f:
        f.write(json.dumps(graph_json))


main()

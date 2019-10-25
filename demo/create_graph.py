"""
依存関係を階層形式で表示する
・階層化の手順
　　1. 階層割当
　　2. 交差削減
　　3．座標決定
"""
import networkx as nx
import json
from collections import defaultdict


class Node:
    """
    ノードをクラスとして定義する。

    Attributes:
        name: ノードの名前。str()。
        targets: 自身が指しているノードの集合。set()。デフォルトは空集合set()。
        sources: 自身を指しているノードの集合。set()。デフォルトは空集合set()。
        x, y: ノードの座標(x,y)。ともにint()。デフォルトは-1。
        href: ノードのリンク。str()。デフォルトは空列 ""。
        is_dummy: ノードがダミーか否か。bool()。デフォルトはFalse。
    """

    def __init__(self, name, targets=None, sources=None, x=None, y=None, href=None, is_dummy=None):
        self.name = name
        self.targets = set() if targets is None else targets
        self.sources = set() if sources is None else sources
        self.x = -1 if x is None else x
        self.y = -1 if y is None else y
        self.href = "" if href is None else href
        self.is_dummy = False if is_dummy is None else is_dummy

    def __str__(self):
        name = self.name
        targets = self.targets
        sources = self.sources
        x = self.x
        y = self.y
        return f"name: {name}, targets: {targets}, sources: {sources}, (x, y)= ({x}, {y})"


class Stack:
    """
    スタック構造のクラス。

    Attributes:
        items: スタックの内容。list。
    """
    def __init__(self):
        self.items = []

    def is_empty(self):
        """スタック内が空かどうか調べる"""
        return self.items == []

    def push(self, item):
        """スタックに値をプッシュする"""
        self.items.append(item)

    def pop(self):
        """スタックの内容をポップする"""
        return self.items.pop()


class Count:
    """
    関数が何度呼ばれたかをカウントするクラス。

    Attributes:
        count: 関数funcを読んだ回数。int。
        func: 関数オブジェクト。
    """
    def __init__(self, func):
        self.count = 0
        self.func = func

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

    def reset(self):
        """カウンタをリセットする"""
        self.count = 0


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

    # targetsの作成
    # k: ノードの名前(str)、v[0]: ノードkがターゲットとするノードの名前(str)の集合
    for k, v in input_node_dict.items():
        for target in v[0]:
            name2node[k].targets.add(name2node[target])

    # sourcesの作成
    # k: ノードの名前(str)、v: ノードkのNodeオブジェクト(object)
    for k, v in name2node.items():
        for target in v.targets:
            target.sources.add(name2node[k])
    return node_list


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
        if not top_node.targets:
            top_node.y = 0
            top_node.x = 0
            assign_level2node_recursively(node_list, top_node, 0)


def assign_level2node_recursively(node_list, target, target_level):
    """
    階層が1以上（y座標が1以上）のノードの階層を再帰的に決定する。階層の割当は次のルールに従う。
    ・まだ階層を割り当てていないノードならば、targetの1つ下の階層に割り当てる。そして、再帰する。
    ・既に座標を割り当てており、その階層が今の階層(assign_node_level)以上高い階層ならば、一つ下の階層に再割当する。
　　・既に階層を割り当てており、その階層が今の階層よりも低い階層ならば、何もしない。

    Args:
        node_list: 全ノードをNodeクラスでまとめたリスト。
        target: ターゲットとなるノード。このノードを指すノードに階層を割り当てていく。
        target_level: targetの階層。targetを指すノードは基本的にこの階層の1つ下の階層に割り当てられる。
    """
    assign_node_level = target_level + 1
    for assign_node in target.sources:
        if assign_node.x < 0:
            assign_node.y = assign_node_level
            assign_node.x = 0
            assign_level2node_recursively(node_list, assign_node, assign_node_level)
        elif assign_node.x > -1 and assign_node.y <= assign_node_level:
            assign_node.y = assign_node_level


def assign_x_sequentially(node_list):
    """
    全てのノードに対して、x座標を割り当てる。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。
    """
    y2x = defaultdict(int)
    for node in node_list:
        node.x = y2x[node.y]
        y2x[node.y] += 1


"""
#2. 交差削減
"""


def cut_edges_higher_than_1(node_list):
    """
    階層が2以上はなれているエッジを見つけ、スタックに格納する。
    その後、スタックの内容をcut_edge()を用いてダミーノードを取得し、
    それをnode_listに挿入し、階層差がすべて1になるようにする。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。

    Return:
    """
    cut_edge_stack = Stack()
    for target in node_list:
        for source in target.sources:
            if calc_edge_height(source, target) > 1:
                cut_edge_stack.push((source, target))

    while cut_edge_stack.is_empty() is False:
        source, target = cut_edge_stack.pop()
        dummy = cut_edge(source, target)
        # dummyの内容はcut_edges()のReturn:を参照。
        node_list.append(dummy)
        if calc_edge_height(dummy, target) > 1:
            cut_edge_stack.push((dummy, target))


def calc_edge_height(node1, node2):
    """
    node1とnode2の階層差を返す

    Args:
        node1, node2: 階層差を比較するノード。Nodeオブジェクト。

    Return:
         node1, node2の階層差。絶対値でint。
    """
    return abs(node1.y - node2.y)


@Count
def cut_edge(source, target):
    """
    source_nodeとtarget_nodeのエッジを切り、その間にダミーノードを挿入する。

    Args:
        source: target_nodesからtargetを取り除き、間にダミーノードを入れたいノード。Nodeオブジェクト。
        target: source_nodesからsourceを取り除き、間にダミーノードを入れたいノード。Nodeオブジェクト。

    Return:
        dummy: sourceとtargetの間に挿入したダミーノード。階層はsourceの一つ上にする。Nodeオブジェクト。
            属性は次のように設定する。
            name: "dummy1"(数字はインクリメントしていく)。
            targets: 要素がtargetのみの集合。
            sources: 要素がsourceのみの集合。
            x: 0
            y: source.y-1
            href: ""
            is_dummy: True
    """
    assert calc_edge_height(source, target) > 1
    dummy_counter = cut_edge.count
    source.targets.remove(target)
    target.sources.remove(source)
    dummy = Node("dummy" + str(dummy_counter),
                 targets={target},
                 sources={source},
                 x=0,
                 y=source.y-1,
                 is_dummy=True
                 )
    source.targets.add(dummy)
    target.sources.add(dummy)

    return dummy


def sort_nodes_by_xcenter(all_nodes, downward):
    """
    重心が小さいノードから左に配置する。
    重心の計算はcalc_xcenter()にて説明。
    上の階層から下の階層へ、もしくは下の階層から上の階層へと操作を行う。
    Args:
        all_nodes:全ノードをNodeオブジェクトでまとめたリスト。
        downward: Trueなら階層の上から下へ操作を行う。Falseなら階層の下から上へと操作を行う。
    Return:
    """
    level2nodes = divide_nodes_by_level(all_nodes)
    if downward:
        for level, nodes in sorted(level2nodes.items()):  # levelでループ
            assign_x_by_xcenter(node2xcenter(nodes, from_targets=False))
    else:
        for level, nodes in sorted(level2nodes.items(), key=lambda k: -k[0]):
            assign_x_by_xcenter(node2xcenter(nodes, from_targets=False))


def divide_nodes_by_level(nodes):
    """
    ノードを階層ごとにkeyで分け、辞書形式で返す。
    Args:
        nodes:全ノードをNodeオブジェクトでまとめたリスト。
    Return:
        each_level_nodes: key=階層, value=階層がkeyのノードのリスト　となる辞書。
    """
    each_level_nodes = defaultdict(list)
    for node in nodes:
        each_level_nodes[node.y].append(node)
    return each_level_nodes


def node2xcenter(nodes, from_targets):
    """
    (v1, v2)のタプルのリストを作る。
        v1=Nodeオブジェクト、v2=v1の重心の値(float)
    Args:
        nodes:重心を求めたいNodeオブジェクトのリスト。Nodeオブジェクトの階層は等しいのが好ましい。
        from_targets: True:重心をtargetsを用いて計算する, False:重心をsourcesを用いて計算する。
    Return:
         (v1, v2)となるタプルのリスト。
            v1: Nodeオブジェクト
            v2: 重心の値(float)
    """
    if from_targets:
        return [(node, calc_xcenter(node.targets)) for node in nodes]
    else:
        return [(node, calc_xcenter(node.sources)) for node in nodes]


def calc_xcenter(nodes):
    """
    nodeの重心をターゲットもしくはソースの集合から計算する
    重心の計算
        ターゲット(もしくはソース)が存在する場合：
            重心 = (ターゲット(ソース)のx座標の総和) / (ターゲット(ソース)の数)
        ターゲット（もしくはソース）が存在しない場合：
            重心 = 正の無限大, float('infinity')
    Args:
        nodes: ソートしたい階層のノードのリスト。
    Return:
        重心の値(float)
    """
    if len(nodes) > 0:
        return sum([node.x for node in nodes]) / len(nodes)
    else:
        return float('infinity')


def assign_x_by_xcenter(node2xcenter_tuple):
    """
    タプル(v1, v2)のリストをソートし、それらに順にx座標を割り当てる。
        v1: Nodeオブジェクト
        v2: v1の重心の値(float)
    Args:
        node2xcenter_tuple: (v1, v2) のタプルのリスト(v1, v2は同上)
    Return:
    """
    sorted_node2xcenter = sorted(node2xcenter_tuple, key=lambda tup: tup[1])  # 重心の値で昇順にソート
    sorted_nodes = [node[0] for node in sorted_node2xcenter]
    assign_x_sequentially(sorted_nodes)


"""
交差の計測
エッジの総和の計測
"""


def count_cross(all_nodes):
    """
    交差数を階層ごとに上から下へと数える。
    交差条件
        2つのエッジedge=(s1, t1), other_edge=(s2, t2)において
        ・s1とs2のy座標が等しい
        ・s1のx座標がs2のx座標より小さい
        ・t1のx座標がt2のx座標より大きい
    Args:
        all_nodes:全てのノード。Nodeオブジェクトのリスト。
    Return:
        cross_counter: 交差数(int)
    """
    cross_counter = 0
    level2nodes = divide_nodes_by_level(all_nodes)
    for level, nodes in sorted(level2nodes.items()):
        edges = make_edge(nodes)
        for edge in edges:
            for other_edge in edges:
                # edge[0]: sourceノード, エッジのソース.  edge[1]: targetノード, エッジのターゲット.
                if edge[0].y == other_edge[0].y and edge[0].x < other_edge[0].x and edge[1].x > other_edge[1].x:
                    cross_counter += 1
    return cross_counter


def make_edge(nodes):
    """
    グラフのエッジを取得する。ノードのソースを用いて作成する。
    Args:
        nodes: (ソースが存在する)全ノード
    Return:
        edges:エッジを(source, target)としてタプルで作成し、リストにまとめたもの。
              source, targetはともにNodeオブジェクト。
              edges = [(source1, target1), (source2, target2), ...]
    """
    edges = []
    for node in nodes:
        for source in node.sources:
            edges.append((source, node))
    return edges


def calc_edge_length_sum(all_nodes):
    """
    エッジの長さの総和を返す。
    ソースとターゲットの離れ具合を測る。
    Args:
        all_nodes: 総和を求めたいエッジを持つ全ノード。Nodeオブジェクト。
    Return:
        total_edge_length: 全エッジの長さの総和。float。
    """
    total_edge_length = 0.0
    level2nodes = divide_nodes_by_level(all_nodes)
    for level, nodes in sorted(level2nodes.items()):  # levelでループ
        edges = make_edge(nodes)
        for source, target in edges:
            total_edge_length += math.sqrt(1 + pow(source.x - target.x, 2))
    return total_edge_length


"""
仕上げ
"""


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
        node_dict[node.name] = {
            "href": node.href,
            "x": node.x,
            "y": node.y,
            "is_dummy": node.is_dummy
        }
    return node_dict


def create_dependency_graph(node_list, graph):
    """
    依存関係を示すグラフを作成する。

    Args:
        node_list:全ノードをNodeクラスでまとめたリスト。
        graph:操作する有向グラフ。networkx.DiGraph()

    Return:
    """
    for source in node_list:
        graph.add_node(source.name)
        for target in source.targets:
            graph.add_node(target.name)
            graph.add_edge(source.name, target.name)


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
    assign_top_node(node_list)
    assign_x_sequentially(node_list)
    cut_edges_higher_than_1(node_list)
    assign_x_sequentially(node_list)
    sort_nodes_by_xcenter(node_list, downward=True)
    sort_nodes_by_xcenter(node_list, downward=False)

    node_attributes = node_list2node_dict(node_list)

    # 有向グラフGraphの作成
    graph = nx.DiGraph()

    create_dependency_graph(node_list, graph)

    # nodes_attrsを用いて各ノードの属性値を設定
    nx.set_node_attributes(graph, node_attributes)

    # グラフの描画
    nx.draw_networkx(graph)

    # cytoscape.jsの記述形式(JSON)でグラフを記述
    graph_json = nx.cytoscape_data(graph, attrs=None)

    with open('demo_sample.json', 'w') as f:
        f.write(json.dumps(graph_json))


if __name__ == "__main__":
    main()

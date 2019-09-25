"""
依存関係を階層形式で表示する
・階層化の手順
　　1. 階層割当
　　2. 交差削減
　　3．座標決定
"""
import networkx as nx
import json

# ノード同士の関係および各ノードのリンク(デモではすべて同じリンク)
node_dict = {"f": [{"e", "b", "a"}, "example.html"], "g": [{"e"}, "example.html"], "h": [{"g", "f"}, "example.html"],
             "i": [{"a"}, "example.html"], "o": [{"m", "l"}, "example.html"], "p": [{"n", "k"}, "example.html"],
             "q": [{"k", "o", "i"}, "example.html"], "j": [{"i"}, "example.html"], "k": [{"j", "m"}, "example.html"],
             "l": [{"i", "a"}, "example.html"], "m": [{"i"}, "example.html"], "n": [{"j", "m"}, "example.html"],
             "a": [set(), "example.html"], "b": [{"a"}, "example.html"], "c": [{"b", "e"}, "example.html"],
             "d": [{"c", "a"}, "example.html"], "e": [{"a"}, "example.html"]}

# 各ノードの属性値 node_attrs = {node_name: {"x": x, "y": y, "dummy": 0 or 1, "href": html}
# x: x座標の値、y: y座標の値, dummy: ダミーノードか否か(0：ダミーでない、1:ダミーである), href: 各ノードのリンク
node_attrs = {}

# 有向グラフGraphの作成
Graph = nx.DiGraph()

for node, node_data in node_dict.items():
    node_attrs[node] = {}
    node_attrs[node]["href"] = node_data[1]

# 依存関係グラフの作成

for source_node, node_data in node_dict.items():
    Graph.add_node(source_node)
    for target_node in node_data[0]:
        Graph.add_node(target_node)
        Graph.add_edge(source_node, target_node)

# 1．階層割当(最長パス法)

# ノードの座標リスト seat_table
# キー：階層(1が最上、その下は一階層下がるにつれて1ずつ増える)。
# 値：その階層に存在するノードのリスト。インデックスはx座標となる。

seat_table = {1: []}

"""
hierarchy_assignment(): グラフの階層を決定する
  target_node: あるノードの親となっているノード
  hierarchy: ノードの階層。
"""


def hierarchy_assignment(parent, hierarchy):
    hierarchy += 1
    for node, node_data in node_dict.items():
        for parent_node in node_data[0]:
            if parent == parent_node:
                if "y" in node_attrs[node]:
                    # 階層の更新(出来るだけ下の階層に持っていく)
                    if node_attrs[node]["y"] < hierarchy:
                        old_hierarchy = node_attrs[node]["y"]
                        seat_table[node_attrs[node]["y"]].remove(node)
                        for update_node in seat_table[old_hierarchy]:
                            node_attrs[update_node].update({"x": seat_table[old_hierarchy].index(update_node) + 1,
                                                            "y": old_hierarchy, "dummy": 0})
                        if hierarchy not in seat_table:
                            seat_table[hierarchy] = []
                        seat_table[hierarchy].append(node)
                        node_attrs[node].update({"x": seat_table[hierarchy].index(node) + 1,
                                                 "y": hierarchy, "dummy": 0})
                    else:
                        pass
                else:
                    if hierarchy not in seat_table:
                        seat_table[hierarchy] = []
                    seat_table[hierarchy].append(node)
                    node_attrs[node] .update({"x": seat_table[hierarchy].index(node) + 1,
                                              "y": hierarchy, "dummy": 0})
                hierarchy_assignment(node, hierarchy)


# シンクを取得し、階層をhierarchy_assignment()を使って決めていく
for node, node_data in node_dict.items():
    if node_data[0] == set():
        node_attrs[node].update({"x": 1, "y": 1, "dummy": 0})
        seat_table[1].append(node)
        hierarchy_assignment(node, 1)


# nodes_attrsを用いて各ノードの属性値を設定
nx.set_node_attributes(Graph, node_attrs)

# グラフの描画
nx.draw_networkx(Graph)

# cytoscape.jsの記述形式(JSON)でグラフを記述
graph_json = nx.cytoscape_data(Graph, attrs=None)

with open('demo_sample.json', 'w') as f:
    f.write(json.dumps(graph_json))

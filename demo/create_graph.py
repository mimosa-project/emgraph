"""
依存関係を階層形式で表示する
・階層化の手順
　　1. 階層割当
　　2. 交差削減
　　3．座標決定
"""
import networkx as nx
import json

# ノード同士の関係
node_dict = {"f": {"e", "b", "a"}, "g": {"e"}, "h": {"g", "f"}, "i": {"a"},
             "o": {"m", "l"}, "p": {"n", "k"}, "q": {"k", "o", "i"},
             "j": {"i"}, "k": {"j", "m"}, "l": {"i", "a"}, "m": {"i"}, "n": {"j", "m"},
             "a": set(), "b": {"a"}, "c": {"b", "e"}, "d": {"c", "a"}, "e": {"a"}}

# 各ノードの属性値 node_attrs = {node_name: {"x": x, "y": y, "dummy": 0 or 1}
# x: x座標の値、y: y座標の値, dummy: ダミーノードか否か(0：ダミーでない、1:ダミーである)
node_attrs = {}

# 有向グラフGraphの作成
Graph = nx.DiGraph()

# 依存関係グラフの作成
for base_node in node_dict.keys():
    Graph.add_node(base_node)
    for obtained_node, parent_nodes in node_dict.items():
        for parent_node in parent_nodes:
            if base_node == parent_node:
                Graph.add_node(parent_node)
                Graph.add_edge(obtained_node, base_node)

# グラフの描画
nx.draw_networkx(Graph)

# cytoscape.jsの記述形式(JSON)でグラフを記述
graph_json = nx.cytoscape_data(Graph, attrs=None)

with open('demo_sample.json', 'w') as f:
    f.write(json.dumps(graph_json))

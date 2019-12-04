/*
createGraph.pyで出力されたファイルとcytoscape.jsを使って
グラフの描画を行う
*/
$(function(){
    $.getJSON("./demo_sample.json", function(graph_data) {
        //描画(graph_draw()をここに書き写す)
        // cytoscapeグラフの作成(初期化)
        let cy = cytoscape({
            container: document.getElementById('demo'),
            elements: [],

            boxSelectionEnabled: true,
            autounselectify: false,
            selectionType: "additive"
        });
        // グラフにノードを追加
        for(let data in graph_data["elements"]["nodes"]){
            for(let component in graph_data["elements"]["nodes"][data]){
                cy.add({
                    group: "nodes",
                    data:{
                        id: graph_data["elements"]["nodes"][data][component]["id"],
                        name: graph_data["elements"]["nodes"][data][component]["name"],
                        dummy: graph_data["elements"]["nodes"][data][component]["dummy"],
                        href: graph_data["elements"]["nodes"][data][component]["href"]
                    },
                    position:{
                        x: graph_data["elements"]["nodes"][data][component]["x"] * 200,
                        y: graph_data["elements"]["nodes"][data][component]["y"] * 200
                    }
                });
            }
        }
        // グラフにエッジを追加
        for(let data in graph_data["elements"]["edges"]){
            for(let component in graph_data["elements"]["edges"][data]){
                cy.add({
                    group: "edges",
                    data:{
                        source: graph_data["elements"]["edges"][data][component]["source"],
                        target: graph_data["elements"]["edges"][data][component]["target"]
                    }
                })
            }
        }
        // グラフのスタイルを決定
        cy.style([
            {
                selector: "node",
                css: {"background-color": "red", "width": 50, "height": 50, "content": "data(id)"}
            },
            {
                selector:"label",
                css: {"text-halign":"center", "text-valign": "center"}
            },
            {
                selector: "edge",
                css: {"line-color": "black", "target-arrow-shape": "triangle", "curve-style": "straight",
                "target-arrow-color": "black", "arrow-scale": 3, "width": 3}
            },
        ]);
        // ノードをクリックした場合、リンクに飛ぶ(htmlリンクの設定)
        cy.on("tap", "node", function(){
            try {
                window.open(this.data("href"));
            } catch(e){
                window.location.href = this.data("href");
            }
        });

    });
});


/**
 * グラフの要素のスタイルを初期状態(ノード：赤い丸、エッジ：黒矢印)に戻す。
 * ただし、移動したノードの位置は戻らない。
 * @param {cytoscape object} cy cytoscapeのグラフ本体
 * @return
**/
function reset_elements_style(cy) {
    let all_class_names = ["highlight",  "not_highlight",  "selected"];
    for(let i=0; i<10; i++){
        all_class_names.push("selected_ancestors" + i);
        all_class_names.push("selected_descendants" + i);
    }
    cy.elements().removeClass(all_class_names);
    cy.nodes().unlock();
}


/**
 * 選んだ1つのノードに近づく、焦点を当てる。
 * @param {cytoscape object} cy: cytoscapeグラフ本体
 * @param {cytoscape object} selected_node: cyの単一のノード。近づきたいノード。
 * @return
**/
function focus_on_selected_node(cy, selected_node){
    cy.animate({
        fit:{
            eles: selected_node,
            padding: 450
        }
    });
}


/**
 * 選択したノード(select_node)とその祖先または子孫を任意の世代数(generations)までを
 * 強調表示するクラスに追加する。
 * アルゴリズム
 *      次の処理を辿りたい世代数まで繰り返す
            1. node_to_get_connectionの親(もしくは子)ノードとそのエッジを強調表示させるクラスに追加する
            2. 1でクラスに追加したノードをnode_to_get_connectionとして更新する
            3. 2でnode_to_get_connectionが空ならループを中断する
 * @param {cytoscape object} cy cytoscapeのグラフ本体
 * @param {int} generations 辿りたい世代数
 * @param {cytoscape object} select_node 選択したノード
 * @param {boolean} is_ancestor 辿りたいのは祖先かどうか。trueなら祖先、falseなら子孫を強調表示させていく。
 * @return
**/
function highlight_connected_elements(cy, generations, select_node, is_ancestor){
    let node_to_get_connection = cy.collection();  // 親(もしくは子)を取得したいノードのコレクション（≒リスト）
    node_to_get_connection = node_to_get_connection.union(select_node);
    for (let i=0; i<generations; i++){
        let class_name = is_ancestor ? "selected_ancestors" : "selected_descendants";
        class_name += Math.min(9, i);
        let next_node_to_get_connection = cy.collection();
        cy.$(node_to_get_connection).forEach(function(n){
            let connect_elements = is_ancestor ? n.outgoers() : n.incomers();
            connect_elements = connect_elements.difference(cy.$(connect_elements).filter(".highlight"));
            cy.$(connect_elements).addClass("highlight");
            cy.$(connect_elements).nodes().addClass(class_name);
            next_node_to_get_connection = next_node_to_get_connection.union(connect_elements.nodes());
        });
        node_to_get_connection = next_node_to_get_connection;
        if (node_to_get_connection.length === 0){
            break;
        }
    }
}


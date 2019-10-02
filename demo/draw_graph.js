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

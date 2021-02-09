using LightGraphs, SimpleWeightedGraphs

function (data)
    g = SimpleWeightedGraph(3)  # or use `SimpleWeightedDiGraph` for directed graphs
    add_edge!(g, 1, 2, 0.5)
    add_edge!(g, 2, 3, 0.8)
    add_edge!(g, 1, 3, 2.0)
    j=2
    print("elo")
    for i in 1:100000000
        j=j+i
    end
    return g
end

function(3)


# MIT License
#
# Copyright (c) 2021 Christophe-Marie Duquesne
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import itertools

#!/usr/bin/env python3
import networkx
import csv

def max_degree(g):
    """
    Returns the maximum number of edges of any node in the graph
    """
    return max([g.degree[n] for n in g])



def edge_styles(g):
    """
    Returns the list of all possible edge styles
    """
    styles = set()
    for e in g.edges(data="style"):
        style = "-"
        if e[2] is not None:
            style = e[2]
        styles.add(style)
    return sorted(list(styles))



def write_header(g, f):
    """
    Creates a header for the csv file of the graph
    """
    n = max_degree(g)
    es = edge_styles(g)

    f.write("# identity: nodeid\n")
    f.write("# label: %label%\n")
    f.write("# style: shape=%shape%;fillColor=%fill%;strokeColor=%stroke%;strokeWidth=1\n")
    f.write("# link: url\n")
    f.write("# width: @width\n")
    f.write("# height: @height\n")
    f.write("# layout: verticalflow\n")

    refs = [f"ref_{i}_{j}" for j in range(len(es)) for i in range(n)]
    labels = [f"label_{i}" for i in range(n)]

    f.write("# ignore: nodeid,style,height,width," + ",".join(refs +
        labels) + "\n" )

    # ref_i_j is connected to nodeid with label i and edge style j
    for j, s in enumerate(es):
        for i in range(n):
            f.write(
                f'# connect: {{"from": "ref_{i}_{j}", "to": "nodeid", '
                f'"fromlabel": "label_{i}", '
                f'"style": "{s}"}}\n')
    f.write(','.join(
        ["nodeid", "label", "tags", "shape",'fill','stroke', "width", "height", "link"] +
        refs + labels
        ) + "\n" )



def write_graph(g, f):
    """
    Creates the content for the csv file of the graph
    """
    n = max_degree(g)
    es = edge_styles(g)

    c = csv.writer(f)
    for node in g.nodes:
        label = g.nodes[node].get("label", "-")
        tags = g.nodes[node].get("tags", "-")
        shape = g.nodes[node].get("shape", "rectangle")
        fill = g.nodes[node].get("fill", "#FFFFFF")
        stroke = g.nodes[node].get("stroke", "#000000")
        link = g.nodes[node].get("link", "-")
        width = g.nodes[node].get("width", "auto")
        height = g.nodes[node].get("height", "auto")

        # ref_i_j is connected to nodeid with label i and edge style j
        refs = ["-"] * n * len(es)
        labels = ["-"] * n
        for i, e in enumerate(g.edges(node, data=True)):
            data = e[2]
            j = es.index(data.get("style", "-"))
            refs[j*n+i] = f"{e[1]}"
            labels[i] = data.get("label", "")
        c.writerow(itertools.chain([f"{node}", label, tags, shape, fill, stroke, width, height, link], refs, labels))
        #f.write(','.join([f"{node}", label, tags, style, width, height, link] + refs + labels) + "\n")




def write(g, f):
    write_header(g, f)
    write_graph(g, f)

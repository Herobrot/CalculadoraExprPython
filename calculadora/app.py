from flask import Flask, request, jsonify, render_template, send_file
from lark import Lark, exceptions, Transformer, Tree, Token
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

math_grammar = """
    ?start: expr
    ?expr: term
         | expr "+" term   -> add
         | expr "-" term   -> subtract
    ?term: factor
         | term "*" factor -> multiply
         | term "/" factor -> divide
    ?factor: NUMBER        -> number
           | "(" expr ")"
    NUMBER: /[0-9]+(\\.[0-9]+)?/
    %ignore " "
"""

parser = Lark(math_grammar, parser="lalr")

class EvaluateTree(Transformer):
    def number(self, n):
        return int(n[0])

    def add(self, values):
        return values[0] + values[1]

    def subtract(self, values):
        return values[0] - values[1]

    def multiply(self, values):
        return values[0] * values[1]

    def divide(self, values):
        if values[1] == 0:
            raise ZeroDivisionError("División por cero no permitida")
        return values[0] / values[1]

    def group(self, value):
        return value[0] 


def build_tree(node, graph=None, parent=None, pos=None, level=0, horizontal_spacing=1):
    if graph is None:
        graph = nx.DiGraph()
        pos = {}
    
    if isinstance(node, Tree):
        label = node.data
    elif isinstance(node, Token):
        label = str(node)
    else:
        label = str(node)
    
    current = f"{label}_{level}_{len(pos)}"
    pos[current] = (level, -len(pos) * horizontal_spacing)
    
    graph.add_node(current, label=label)
    
    if parent:
        graph.add_edge(parent, current)
    
    if isinstance(node, Tree):
        for child in node.children:
            build_tree(child, graph, current, pos, level + 1, horizontal_spacing)

    return graph, pos

def generate_binary_tree_image(tree):        
    graph, pos = build_tree(tree)
    labels = nx.get_node_attributes(graph, 'label')
    
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, with_labels=True, labels=labels, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=False)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer

def save_tree_image(buffer, folder="static/images", filename="binary_tree_equation.png"):    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    image_path = os.path.join(folder, filename)
    
    with open(image_path, 'wb') as f:
        f.write(buffer.getvalue())

    return image_path

def generate_tree(tree):
    try:        
        img = generate_binary_tree_image(tree)    
        if(not img):
            return "Error al generar el árbol binario"
        return save_tree_image(img)
    except ValueError as e:
        return {"error": str(e)}, 400

@app.route('/calcular', methods=['POST'])
def validate_expression():
    data = request.json
    expression = data.get('expression', '')

    try:        
        tree = parser.parse(expression)                
        result = EvaluateTree().transform(tree)
        url = generate_tree(tree)        
        print("Se guardo el arbol binario en: ", url)
        return jsonify({"valid": True, "result": result, "url": url})
    except exceptions.LarkError as e:
        return jsonify({"valid": False, "message": "Expresión inválida", "error": str(e)})
    except ZeroDivisionError:
        return jsonify({"valid": False, "message": "No se puede dividir entre 0"})

@app.route("/")
def main():
    return render_template("index.html")

from flask import Flask, request, jsonify, render_template, send_file
from lark import Lark, exceptions, Transformer, Tree, Token
import matplotlib.pyplot as plt
import io

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
    NUMBER: /[0-9]+/
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
    
def parse_to_tree(equation):
    try:        
        parse_tree = parser.parse(equation)        
        return build_tree(parse_tree)
    except exceptions.LarkError as e:
        raise ValueError(f"Error en la ecuación: {str(e)}")

def build_tree(parse_tree):
    def node_to_dict(node):
        if isinstance(node, Tree):
            if node.data == 'number':                
                return {"value": node.children[0].value}
            elif node.data in ('expr', 'term', 'factor'):                
                left = node_to_dict(node.children[0])
                if len(node.children) > 2:
                    op = node.children[1].value
                    right = node_to_dict(node.children[2])
                    return {"value": op, "left": left, "right": right}
                return left
        elif isinstance(node, Token):            
            return {"value": node.value}

    return node_to_dict(parse_tree)

def generate_binary_tree_image(tree):    
    fig, ax = plt.subplots()
    ax.set_axis_off()
       
    def plot_node(node, x, y, dx, depth):
        if not node:
            return
        ax.text(x, y, str(node["value"]), fontsize=12, ha='center', va='center', bbox=dict(boxstyle='circle', facecolor='lightblue'))
        if node.get("left"):
            ax.plot([x, x - dx], [y, y - depth], 'k-')
            plot_node(node["left"], x - dx, y - depth, dx / 2, depth)
        if node.get("right"):
            ax.plot([x, x + dx], [y, y - depth], 'k-')
            plot_node(node["right"], x + dx, y - depth, dx / 2, depth)

    example_tree = {"value": "+", "left": {"value": "5"}, "right": {"value": "5"}}

    plot_node(example_tree, 0, 0, 1, 1)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)
    return buffer

@app.route("/generate_tree", methods=["POST"])
def generate_tree():
    data = request.json
    equation = data.get("equation", "")
    try:
        tree = parse_to_tree(equation)        
        img = generate_binary_tree_image(tree)        
        return send_file(img, mimetype="image/png")
    except ValueError as e:
        return {"error": str(e)}, 400

@app.route('/calcular', methods=['POST'])
def validate_expression():
    data = request.json
    expression = data.get('expression', '')

    try:        
        tree = parser.parse(expression)                
        result = EvaluateTree().transform(tree)
        return jsonify({"valid": True, "result": result})
    except exceptions.LarkError as e:
        return jsonify({"valid": False, "message": "Expresión inválida", "error": str(e)})
    except ZeroDivisionError:
        return jsonify({"valid": False, "message": "No se puede dividir entre 0"})

@app.route("/")
def main():
    return render_template("index.html")

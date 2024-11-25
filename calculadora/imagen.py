import matplotlib.pyplot as plt
import io
import os

# Nodo del árbol binario
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Función recursiva para construir el árbol binario
def build_expression_tree():
    # Creación de nodos para la expresión "5+5+(8*5)-5"
    # El árbol es:
    #         -
    #        / \
    #       +   5
    #      / \
    #     5   *
    #        / \
    #       8   5
    left_subtree = TreeNode("+", TreeNode("5"), TreeNode("5"))
    right_subtree = TreeNode("*", TreeNode("8"), TreeNode("5"))
    root = TreeNode("-", left_subtree, right_subtree)
    return root

# Función para graficar el árbol binario
def generate_binary_tree_image(tree):
    fig, ax = plt.subplots()
    ax.set_axis_off()

    def plot_node(node, x, y, dx, depth):
        if not node:
            return
        ax.text(x, y, str(node.value), fontsize=12, ha='center', va='center', bbox=dict(boxstyle='circle', facecolor='lightblue'))
        if node.left:
            ax.plot([x, x - dx], [y, y - depth], 'k-')
            plot_node(node.left, x - dx, y - depth, dx / 2, depth)
        if node.right:
            ax.plot([x, x + dx], [y, y - depth], 'k-')
            plot_node(node.right, x + dx, y - depth, dx / 2, depth)

    # Llamada a plot_node con los parámetros iniciales
    plot_node(tree, x=0, y=0, dx=1, depth=1)

    # Generar la imagen en memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)

    return buffer

# Función para guardar la imagen en una carpeta local
def save_tree_image(buffer, folder="static/images", filename="binary_tree_equation.png"):
    # Verificar si la carpeta existe, si no, crearla
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Ruta completa donde se guardará la imagen
    image_path = os.path.join(folder, filename)

    # Guardar la imagen en el archivo especificado
    with open(image_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    print(f"Árbol binario guardado como '{image_path}'")

# Construir el árbol binario de la expresión
expression_tree = build_expression_tree()

# Generar la imagen del árbol binario
image_buffer = generate_binary_tree_image(expression_tree)

# Guardar la imagen en la carpeta local
save_tree_image(image_buffer)

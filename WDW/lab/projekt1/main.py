# requirements: numpy plotly

import sys
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

STEP=0.05

def f(a, b, c, d):
    # Miejsce na funkcję użytkownika
    return a / (a + b + c)

def convex_generator(n, step):
    total = int(round(1 / step))
    
    def recurse(current, remaining, depth):
        if depth == n - 1:
            last = remaining
            yield np.array(current + [last * step])
        else:
            for i in range(remaining + 1):
                yield from recurse(current + [i * step], remaining - i, depth + 1)

    yield from recurse([], total, 0)

def main():
    if len(sys.argv) > 1:
        print("Funkcję należy zdefiniować wewnątrz kodu w miejscu oznaczonym jako 'Miejsce na funkcję użytkownika'.")
        return

    bar_coords = np.array(list(convex_generator(4, STEP)))
    print(f'Resulution: {len(bar_coords)}')
    values = []
    categories = []

    lambdas = np.array([[0,0,0],[1,0,0],[1/2, (3**(1/2))/2, 0],[1/2, (3**(1/2))/4, 1]])

    for a, b, c, d in bar_coords:
        val = f(a, b, c, d)
        values.append(val)

        if np.isnan(val):
            categories.append("nan")
        elif np.isposinf(val):
            categories.append("+inf")
        elif np.isneginf(val):
            categories.append("-inf")
        else:
            categories.append("valid")

    cart_coords = []
    for bar_point in bar_coords:
        cart_coord = np.sum(np.array([x*l for (x,l) in zip(bar_point, lambdas)]), axis=0)
        cart_coords.append(cart_coord)
    cart_coords = np.array(cart_coords)

    fig = go.Figure()

    valid_points = [(bar_coord, v, cart_cord) for bar_coord, v, cat, cart_cord in zip(bar_coords, values, categories, cart_coords) if cat == "valid"]
    fig.add_trace(go.Scatter3d(        
        x=[cart_cord[0] for bar_coord, v, cart_cord in valid_points],
        y=[cart_cord[1] for bar_coord, v, cart_cord in valid_points],
        z=[cart_cord[2] for bar_coord, v, cart_cord in valid_points],
        mode='markers',
        marker=dict(
            size=3,
            color=[v for bar_coord, v, cart_cord in valid_points],
            colorscale='Turbo',
            colorbar=dict(title="f(a,b,c,d)", len=0.8),
            showscale=True
        ),
        text=[
            f"({a:.2f}, {b:.2f}, {c:.2f}, {d:.2f}) = {v:.2f}"
            for (a, b, c, d), v, cart_cord in valid_points
        ],
        name="valid"
    ))

    undefined_value_color = "#FF00FF"
    for cat in ["nan", "+inf", "-inf"]:
        idxs = [i for i, c in enumerate(categories) if c == cat]
        if idxs:
            fig.add_trace(go.Scatter3d(
                x=cart_coords[idxs,0],
                y=cart_coords[idxs,1],
                z=cart_coords[idxs,2],
                mode='markers',
                marker=dict(size=3, color=undefined_value_color),
                text=[
                    f"({a:.2f}, {b:.2f}, {c:.2f}, {d:.2f})"
                    for (a, b, c, d) in bar_coords[idxs]
                ],
                name=cat
            ))

    fig.update_layout(title="Wizualizator funkcji w Bary-4D", scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Z"
    ))

    file_path = Path("plot.html")
    fig.write_html(file_path)
    print(f'Plot saved to: {file_path.resolve()}')

if __name__ == "__main__":
    main()

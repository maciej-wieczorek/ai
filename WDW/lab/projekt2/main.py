import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances
from sklearn.manifold import MDS
import sys


def read_input_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    header = lines[0].split()
    mode = header[0]

    if mode == 'X':
        attr_names = header[1:]
        obj_names = []
        data = []

        for line in lines[1:]:
            tokens = line.split()
            obj_names.append(tokens[0])
            data.append([float(x) for x in tokens[1:]])

        return mode, np.array(data), obj_names

    elif mode == 'D':
        obj_names = header[1:]
        data = []

        for line in lines[1:]:
            tokens = line.split()
            data.append([float(x) for x in tokens[1:]])

        return mode, np.array(data), obj_names

    else:
        print("Nieprawidłowy format pliku. Pierwsza linia musi zaczynać się od 'X' lub 'D'.")
        sys.exit(1)


def visualize(points, labels):
    plt.figure(figsize=(6, 6))
    for (x, y), label in zip(points, labels):
        plt.scatter(x, y, label=label)
        plt.text(x + 0.02, y + 0.02, label)
    plt.title("Wizualizacja obiektów w 2D")
    plt.xlabel("Wymiar 1")
    plt.ylabel("Wymiar 2")
    plt.grid(True)
    plt.axis('equal')
    plt.show()


def compute_frobenius(D_target, D_actual):
    return np.linalg.norm(D_target - D_actual, ord='fro')


def main():
    parser = argparse.ArgumentParser(description="Wizualizacja obiektów w 2D")
    parser.add_argument('input_file', help='Ścieżka do pliku wejściowego')
    args = parser.parse_args()

    mode, data, labels = read_input_file(args.input_file)

    if mode == 'X':
        D = pairwise_distances(data, metric='euclidean')
    elif mode == 'D':
        D = data

    # Redukcja wymiarów za pomocą klasycznego MDS
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    points = mds.fit_transform(D)

    # Macierz odległości z wynikowej konfiguracji
    D_actual = pairwise_distances(points, metric='euclidean')

    # Oblicz norma Frobeniusa
    frob = compute_frobenius(D, D_actual)
    print(f"Norma Frobeniusa różnicy macierzy odległości: {frob:.4f}")

    visualize(points, labels)


if __name__ == '__main__':
    main()

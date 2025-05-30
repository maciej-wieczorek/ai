import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def parse_file(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip().split() for line in f if line.strip()]

    mode = lines[0][0]

    if mode == 'X':
        object_labels = [line[0] for line in lines[1:]]
        data = np.array([[float(val) for val in line[1:]] for line in lines[1:]])
        dist_matrix = calculate_distance_matrix(data)
    elif mode == 'D':
        object_labels = lines[0][1:]
        dist_matrix = np.array([[float(val) for val in line[1:]] for line in lines[1:]])
    else:
        raise ValueError("Pierwszy wiersz musi zaczynać się od 'X' lub 'D'")

    return mode, object_labels, dist_matrix

def calculate_distance_matrix(X):
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = np.linalg.norm(X[i] - X[j])
    return D

def mds_stress(positions_flat, D_target):
    n = D_target.shape[0]
    positions = positions_flat.reshape((n, 2))
    D_current = calculate_distance_matrix(positions)
    return np.linalg.norm(D_target - D_current)

def perform_mds(D_target):
    n = D_target.shape[0]
    init_pos = np.random.rand(n, 2)
    res = minimize(mds_stress, init_pos.flatten(), args=(D_target))
    final_positions = res.x.reshape((n, 2))
    D_final = calculate_distance_matrix(final_positions)
    frobenius_norm = np.linalg.norm(D_target - D_final)
    return final_positions, frobenius_norm

def plot_result(positions, labels, frobenius_norm):
    plt.figure(figsize=(8, 6))
    plt.scatter(positions[:, 0], positions[:, 1])
    for i, label in enumerate(labels):
        plt.text(positions[i, 0], positions[i, 1], label)
    plt.title(f'MDS - Norma Frobeniusa: {frobenius_norm:.4f}')
    plt.xlabel('Wymiar 1')
    plt.ylabel('Wymiar 2')
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def main():
    if len(sys.argv) < 2:
        print("Użycie: python mds.py <plik_wejściowy>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Plik nie istnieje: {input_file}")
        sys.exit(1)

    try:
        mode, labels, D = parse_file(input_file)
    except Exception as e:
        print(f"Błąd podczas wczytywania pliku: {e}")
        sys.exit(1)

    positions, frobenius_norm = perform_mds(D)
    print(f"Norma Frobeniusa: {frobenius_norm:.4f}")
    plot_result(positions, labels, frobenius_norm)

if __name__ == "__main__":
    main()

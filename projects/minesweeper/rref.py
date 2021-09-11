def rref(matrix):
    if not matrix:
        return []
    width = len(matrix[0])
    height = len(matrix)
    m = 0
    n = 0
    while n < width and m < height:
        for i in range(m, height):
            if matrix[i][n] != 0:
                if i != m:
                    matrix[i], matrix[m] = matrix[m], matrix[i]
                break
        else:
            n += 1
            continue
        pivot_row = matrix[m]
        pivot = pivot_row[n]
        for i in range(n, len(pivot_row)):
            pivot_row[i] /= pivot
        for i, row in enumerate(matrix):
            if i == m:
                continue
            coef = row[n]
            for j in range(n, len(row)):
                row[j] -= pivot_row[j] * coef
        m += 1
        n += 1
    return matrix


def frref(matrix):
    if not matrix:
        return []
    width = len(matrix[0])
    height = len(matrix)
    m = 0
    n = 0
    while n < width and m < height:
        for i in range(m, height):
            if matrix[i][n] != 0:
                if i != m:
                    matrix[i], matrix[m] = matrix[m], matrix[i]
                break
        else:
            n += 1
            continue
        pivot_row = matrix[m]
        pivot = pivot_row[n]
        for i in range(n, len(pivot_row)):
            pivot_row[i] //= pivot
        for i, row in enumerate(matrix):
            if i == m:
                continue
            coef = row[n]
            row[n] = 0
            for j in range(n + 1, len(row)):
                row[j] -= pivot_row[j] * coef
        m += 1
        n += 1
    return matrix


def main():
    # matrix = [
    #     [1, 1, 1, 1, 0, 0, 0, 1],
    #     [1, 1, 0, 0, 1, 0, 0, 2],
    #     [0, 1, 0, 0, 1, 1, 1, 2],
    #     [0, 1, 1, 0, 1, 0, 1, 1]
    # ]
    matrix = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 0, 0, 0, 0, 2],
        [0, 1, 0, 1, 1, 0, 1, 1, 1, 3],
        [0, 1, 0, 0, 1, 0, 0, 0, 1, 1]
    ]
    # matrix = [
    # [1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
    # [0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
    # [0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
    # [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    # [1, 1, 0, 1, 1, 0, 0, 0, 0, 2],
    # [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    # [0, 1, 0, 1, 1, 0, 1, 1, 1, 3],
    # [0, 1, 0, 0, 1, 0, 0, 0, 1, 1]
    # ]

    # matrix = [
    #     [1, 1, 1, 1, 1],
    #     [0, 1, 1, 0, 0],
    #     [1, 0, 1, 0, 0],
    #     [0, 0, 1, 0, 1],
    # ]

    # matrix = [
    #     [1, 1, 1, 1, 1],
    #     [0, 1, 1, 0, 0],
    #     [1, 0, 1, 0, 0],
    #     [0, 0, 1, 0, 1],
    # ]

    from copy import deepcopy

    print()
    for row in rref(deepcopy(matrix)):
        print(row)

    print()
    for row in frref(deepcopy(matrix)):
        print(row)


if __name__ == "__main__":
    main()

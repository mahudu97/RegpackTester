import numpy as np

def clean(matrix, tol=1e-10):
    arr = matrix.copy()

    # Flush small elements to zero
    arr[np.abs(arr) < tol] = 0

    # Coalesce similar elements
    if arr.size > 1:
        amfl = np.abs(arr.flat)
        amix = np.argsort(amfl)

        i, ix = 0, amix[0]
        for j, jx in enumerate(amix[1:], start=1):
            if amfl[jx] - amfl[ix] >= tol:
                if j - i > 1:
                    amfl[amix[i:j]] = np.median(amfl[amix[i:j]])
                i, ix = j, jx

        if i != j:
            amfl[amix[i:]] = np.median(amfl[amix[i:]])

        # Fix up the signs and assign
        arr.flat = np.copysign(amfl, arr.flat)

    return arr

def count_unique_constants(matrix, tol=1e-10):
    arr = matrix.copy()
    arr = arr[abs(arr) >= tol]
    unique, counts = np.unique(arr, return_counts=True)
    return np.array((unique, counts)).T

def num_unique_constants(matrix):
    return len(count_unique_constants(matrix))

def create_compact_dictionary(matrix, max_registers=32, vector_lane_width=8):
    constant_map = {}
    vector_map = {}

    sorted_unique = [const[0] for const in count_unique_constants(matrix)]
    vector_lanes = [sorted_unique[i:i + vector_lane_width] for i in range(0, len(sorted_unique), vector_lane_width)]

    num_constants = len(sorted_unique)
    if num_constants > max_registers * vector_lane_width:
        print("Exceeding recommended number of constants: Using " + str(num_constants) +
              " constants with " + str(max_registers * vector_lane_width) + " spaces")

    remaining_registers = max_registers

    while len(vector_lanes) > 0:
        vector = vector_lanes.pop(0)
        # determine variable name
        var_id = "v" + str(max_registers - remaining_registers)

        # create vector map for allocating packed constants
        vector_map[var_id] = vector + ([0] * (vector_lane_width - len(vector)))

        # build constant map
        for index, constant in enumerate(vector):
            constant_map[constant] = (var_id, index)

        # adjust remaining registers
        remaining_registers -= 1
        num_constants -= vector_lane_width

    mat_info = [[constant_map.get(num) or [None, None] for num in row] for row in matrix]
    return mat_info, vector_map

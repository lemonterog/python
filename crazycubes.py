import itertools
from collections import Counter

# ==========================================
# 1. INPUT DATA
# Format: [Top, Bottom, Front, Back, Left, Right]
# ==========================================
my_cubes = [
    [4, 1, 2, 5, 6, 3],
    [6, 4, 5, 2, 3, 1],
    [6, 3, 5, 2, 1, 4],
    [5, 3, 4, 6, 2, 1],
    [3, 6, 2, 1, 4, 5],
    [4, 5, 6, 3, 1, 2]
]


#rama 1
# ==========================================
# 2. GEOMETRY ENGINE
# ==========================================
def get_valid_rotation(cube_data, target_front, target_left):
    """
    Physically rotates the cube list [T, B, F, Bk, L, R] in 3D space
    until Front == target_front and Left == target_left.
    Returns the full rotated list.
    """
    # Indices: 0=T, 1=B, 2=F, 3=Bk, 4=L, 5=R
    # We generate all 24 permutations achievable by rotation

    current = list(cube_data)

    # Basic Rotations (90 degrees)
    def pitch(c):
        return [c[2], c[3], c[1], c[0], c[4], c[5]]  # F->T, B->F, T->Bk, Bk->B

    def yaw(c):
        return [c[0], c[1], c[4], c[5], c[3], c[2]]  # F->L, L->Bk, Bk->R, R->F

    def roll(c):
        return [c[4], c[5], c[2], c[3], c[1], c[0]]  # T->R, R->B, B->L, L->T

    # Strategy: Try to put every face in Front, then spin around Z
    attempts = []

    # 1. Start orientation
    base = list(current)
    attempts.append(base)
    # 2. Yaw 3 times (4 facings on horizontal plane)
    for _ in range(3):
        base = yaw(base)
        attempts.append(base)
    # 3. Pitch Up (Top becomes Front) -> Yaw 3 times
    base = pitch(list(current))
    attempts.append(base)
    for _ in range(3):
        base = yaw(base)
        attempts.append(base)
    # 4. Pitch Down (Bottom becomes Front) -> Yaw 3 times
    base = pitch(pitch(pitch(list(current))))  # 3 pitches = 1 reverse pitch
    attempts.append(base)
    for _ in range(3):
        base = yaw(base)
        attempts.append(base)

    # We need to cover all 6 faces as "Front".
    # The above covers F, L, Bk, R (via Yaws) and T, B (via Pitches).
    # We just need to check all 24 explicitly to be safe, or just scan these candidates.
    # A cleaner way: Map face indices to orientations.

    # Let's bruteforce the 24 permutations by chaining operations strictly:
    # Any cube state is reachable by sequence of Pitch/Yaw/Roll.
    # We will BFS to find the state matching our constraints.
    queue = [list(cube_data)]
    seen = set()

    for state in queue:
        state_tuple = tuple(state)
        if state_tuple in seen: continue
        seen.add(state_tuple)

        # Check if this rotation matches our solution
        if state[2] == target_front and state[4] == target_left:
            return state  # Found it!

        # Generate neighbors
        if len(seen) < 24:  # Optimization
            queue.append(pitch(state))
            queue.append(yaw(state))
            queue.append(roll(state))

    return None  # Should impossible if the cube actually contains the numbers


# ==========================================
# 3. SOLVER LOGIC
# ==========================================
def solve_specific_format(cubes):
    print("Solving with 3D Geometry Validation...")

    # EXTRACT PAIRS (0-1), (2-3), (4-5)
    cube_pairs = []
    for c in cubes:
        pairs = [
            tuple(sorted((c[0], c[1]))),
            tuple(sorted((c[2], c[3]))),
            tuple(sorted((c[4], c[5])))
        ]
        cube_pairs.append(pairs)

    # SEARCH FOR VALID CONFIGURATIONS
    valid_configs = []
    for indices in itertools.product(range(3), repeat=6):
        selected_pairs = []
        all_numbers = []
        for i, pair_idx in enumerate(indices):
            p = cube_pairs[i][pair_idx]
            selected_pairs.append(p)
            all_numbers.extend(p)

        if all(Counter(all_numbers)[k] == 2 for k in range(1, 7)):
            valid_configs.append({'axes': indices, 'pairs': selected_pairs})

    print(f"Found {len(valid_configs)} valid single-direction sets.")

    # FIND COMPATIBLE SOLUTIONS
    solutions = []
    for i in range(len(valid_configs)):
        for j in range(i + 1, len(valid_configs)):
            c1 = valid_configs[i]
            c2 = valid_configs[j]

            collision = False
            for k in range(6):
                if c1['axes'][k] == c2['axes'][k]:
                    collision = True
                    break

            if not collision:
                solutions.append((c1, c2))

    if not solutions:
        print("NO SOLUTION FOUND.")
        return

    # PROCESS THE FIRST SOLUTION
    sol_fb = solutions[0][0]
    sol_lr = solutions[0][1]

    # Helper to flip faces for Front/Left uniqueness
    def resolve_orientation(pairs_list):
        for flips in itertools.product([0, 1], repeat=6):
            primary = [pairs_list[k][flips[k]] for k in range(6)]
            if len(set(primary)) == 6:
                return primary
        return []

    final_fronts = resolve_orientation(sol_fb['pairs'])
    final_lefts = resolve_orientation(sol_lr['pairs'])

    print("\n" + "=" * 70)
    print(f"{'CUBE':<5} | {'FRONT':<6} {'BACK':<6} | {'LEFT':<6} {'RIGHT':<6} | {'TOP':<6} {'BOTTOM':<6}")
    print("=" * 70)

    for i in range(6):
        target_f = final_fronts[i]
        target_l = final_lefts[i]

        # !!! KEY FIX !!!
        # Rotate the *original* cube data to match F and L.
        # This automatically forces T, B, Bk, R to be physically correct.
        rotated = get_valid_rotation(cubes[i], target_f, target_l)

        if rotated:
            # Format: [T, B, F, Bk, L, R]
            t, b, f, bk, l, r = rotated
            print(f"#{i + 1:<4} | {f:<6} {bk:<6} | {l:<6} {r:<6} | {t:<6} {b:<6}")
        else:
            print(f"#{i + 1:<4} | ERROR: Impossible Geometry for F={target_f}, L={target_l}")

    print("-" * 70)


if __name__ == "__main__":
    solve_specific_format(my_cubes)

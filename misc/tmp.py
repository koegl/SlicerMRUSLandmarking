# sweetch between any amount of images

self_volumes_names = ["one", "two", 'three']


def get_next_combination(current_volumes=None, direction="forward"):
    if not self_volumes_names:
        return None
    if direction not in ["forward", "backward"]:
        return None

    forward_combinations = []
    next_index = None

    # create list of possible forward pairs
    for i in range(len(self_volumes_names)):
        if i == len(self_volumes_names) - 1:
            index1 = len(self_volumes_names) - 1
            index2 = 0
        else:
            index1 = i
            index2 = i + 1

        forward_combinations.append([self_volumes_names[index1], self_volumes_names[index2]])

    current_index = forward_combinations.index(current_volumes)
    combinations = forward_combinations

    if direction == "forward":
        if current_index == len(self_volumes_names) - 1:
            next_index = 0
        else:
            next_index = current_index + 1

    elif direction == "backward":
        if current_index == 0:
            next_index = len(self_volumes_names) - 1
        else:
            next_index = current_index - 1

    return combinations[next_index]


# e.g. 5 images
images = ["one", "two", "three"]  # , 3, 4, 5, 6]

print(get_next_combination(["two", "three"], "forward"))

possible_combinations = [[0, 1],
                         [1, 2],
                         [2, 3],
                         [3, 4],
                         [4, 0]]





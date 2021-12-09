# sweetch between any amount of images


def generate_forward_combinations(images_list=None):
    if not images_list:
        return

    forward_combinations = []
    backward_combinations = []

    # create list of possible forward pairs
    for i in range(len(images_list)):
        if i == len(images_list) - 1:
            index1 = len(images_list) - 1
            index2 = 0
        else:
            index1 = i
            index2 = i + 1

        forward_combinations.append([images_list[index1], images_list[index2]])
        backward_combinations.append([images_list[index2], images_list[index1]])

    return forward_combinations, backward_combinations


# e.g. 5 images
images = [0, 1, 2]  # , 3, 4, 5, 6]

print(generate_forward_combinations(images))

possible_combinations = [[0, 1],
                         [1, 2],
                         [2, 3],
                         [3, 4],
                         [4, 0]]





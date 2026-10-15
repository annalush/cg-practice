import random


def generate_array(size=None):
    if size is None:
        size = random.randint(20, 50)
    return [random.randint(10, 100) for _ in range(size)]


def bubble_sort_steps(values):
    n = len(values)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            yield {
                "type": "compare",
                "indices": (i, i + 1),
            }
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
                swapped = True
                yield {
                    "type": "swap",
                    "indices": (i, i + 1),
                }
        yield {
            "type": "pass_end",
            "sorted_index": end,
        }
        if not swapped:
            break
    yield {
        "type": "finished",
    }


def selection_sort_steps(values):
    n = len(values)
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            yield {
                "type": "compare",
                "indices": (j, min_index),
                "current_min": min_index,
            }
            if values[j] < values[min_index]:
                min_index = j
                yield {
                    "type": "new_min",
                    "indices": (min_index,),
                }
        if min_index != i:
            values[i], values[min_index] = values[min_index], values[i]
            yield {
                "type": "swap",
                "indices": (i, min_index),
            }
        yield {
            "type": "pass_end",
            "sorted_index": i,
        }
    yield {
        "type": "finished",
    }


def binary_search_steps(values, target):
    left = 0
    right = len(values) - 1

    while left <= right:
        mid = (left + right) // 2
        yield {
            "type": "check",
            "left": left,
            "right": right,
            "mid": mid,
            "target": target,
        }

        if values[mid] == target:
            yield {
                "type": "found",
                "index": mid,
                "target": target,
            }
            return

        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    yield {
        "type": "not_found",
        "target": target,
    }
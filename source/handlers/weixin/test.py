from collections import defaultdict

a = [{'a': 111, 'b': 2}, {'a': 222, 'b': 2}, {'a': 333, 'b': 2}, {'a':444, 'b':3}, {'a':555, 'b':3}]

# b = [{'a': [111, 222, 333], 'b': 2},{'a':[444,555],'b':3}]


def test(a):
    result_list = list()
    temp_dict = dict()
    for element in a:
        for key, value in element.items():
            if key == "b" and temp_dict.get(key) != value:
                temp_dict = dict()
                temp_dict[key] = value
                result_list.append(temp_dict)
            elif key == "a":
                if not temp_dict.get(key):
                    temp_dict[key] = list()
                temp_dict[key].append(value)

    return result_list


print(test(a))

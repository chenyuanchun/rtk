r"""
Util functions
"""


def traverse_complex_data(data, func):
    """
    traverse the data structure and run func on the leaf node
    :param data: input data to traverse
    :param func: function to run on leaf node
    :return: None
    """
    if isinstance(data, dict):
        for _value in data.values():
            traverse_complex_data(_value, func)
    elif isinstance(data, (list, tuple)):
        for _value in data:
            traverse_complex_data(_value, func)
    else:
        func(data)


def traverse_process_complex_data(data, processor):
    """
    traverse the data structure, run processor and replace leaf node
    :param data: input data
    :param processor: function to run on and replace leaf node
    :return: processed data
    """
    if isinstance(data, dict):
        return {key: traverse_process_complex_data(value, processor) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [traverse_process_complex_data(i, processor) for i in data]
    else:
        return processor(data)

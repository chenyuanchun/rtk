from pkg_resources import resource_filename


if __name__ == '__main__':
    _path = resource_filename('snippet', 'data/')
    print(_path)
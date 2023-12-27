import numpy as np
import yaml
import os
import re

def get_data_in_file(items):
    data_total = []
    for x in items:
        with open(x, 'r') as f:
            contents = f.readlines()

        end_line = -1
        
        data = []
        while True:
            ifInnerField = False
            try:
                start_line = contents[end_line+1:].index('(\n') + end_line + 1
                for i in range(end_line+1, start_line):
                    if 'internalField' in contents[i]:
                        ifInnerField = True
                        break
                end_line = contents[start_line+1:].index(')\n') + start_line + 1
            except:
                break
            if ifInnerField:
                data.append(np.array([float(x) for x in contents[start_line+1: end_line]]))
        data = np.concatenate(data)
        data_total.append(data)
    data_total = np.concatenate([x[:,np.newaxis] for x in data_total], axis=1)
    print(f'data size: {data_total.shape[0]}')
    return data_total
            


if __name__  == '__main__':
    with open('get_data.yaml', 'r') as f:
        options = yaml.load(f, Loader=yaml.FullLoader)

    if 'readItems' not in options.keys():
        raise ValueError('readItems not set!')
    else:
        readItems = options['readItems'].split()

    if 'mechanismName' in options.keys():
        mechanismName = options['mechanismName']
        with open(mechanismName, 'r') as f:
            mechanism = yaml.load(f, Loader=yaml.FullLoader)
            species = [x['name'] for x in mechanism['species']]
            readItems += species
    readItemsTotal = list(set(readItems))
    readItemsTotal.sort(key = readItems.index)

    if 'readFiles' not in options.keys():
        files = os.listdir()
        readFiles = [x for x in files if re.match(r'\d*\.\d*$', x)]
    else:
        readFiles = options['readFiles'].split()
    readFiles.sort(key=float)

    print('items need to read:')
    print(readItemsTotal)
    print('files need to process:')
    print(readFiles)
    data_total = []
    for file in readFiles:
        print(f'get data from {file}')
        os.chdir(file)
        os.system('gzip -d  ' + ' '.join([x + '.gz' for x in readItemsTotal]))
        data_total.append(get_data_in_file(readItemsTotal))
        os.system('gzip -f ' + ' '.join(readItemsTotal))
        os.chdir('..')

    data_array = np.concatenate(data_total)
    np.save('data.npy', data_array)

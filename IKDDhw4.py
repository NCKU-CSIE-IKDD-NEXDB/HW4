import os
import re
import operator
from tabulate import tabulate

class Graph():
    def __init__(self):
        self.node = dict()
        self.link = list()
        self.graph = dict()
        self.file = dict()
        self.file_to_node = dict()
        self.rank = dict()
        self.remove_node = list()

    def read_file(self):
        node_index = 1
        for dirPath, dirNames, fileNames in os.walk('dataset/'):
            for f in fileNames:
                file_dir = os.path.join(dirPath, f)
                file_read = open(file_dir, 'r', encoding='big5')
                file_str = str()
                self.file[f] = str()
                while True:
                    string = file_read.read()
                    if string == '':
                        break
                    else:
                        file_str += string
                for string in file_str.split('\n'):
                   self.file[f] += ' ' + string
                self.file_to_node[f] = node_index
                node_index += 1

    def find_link(self):
        for file_name in list(self.file.keys()):
            for string in self.file[file_name].split():
                pat = r'http://\S+.txt'
                match = re.search(pat, string)
                if match:
                    source_node = self.file_to_node[file_name]
                    target_node = self.file_to_node[match.group().split('/')[2]]
                    self.link.append((source_node, target_node))

    def construct_graph(self):
        link_list = list()
        node_list = list(self.file_to_node.values())
        for link in self.link:
            link_list.append(link)
        is_remove_dead = False
        while not is_remove_dead:
            node_num = len(node_list)
            for node in node_list:
                is_remove_node = True
                for link in link_list:
                    if node == link[0]:
                        is_remove_node = False

                if is_remove_node:
                    node_list.remove(node)
                    self.remove_node.append(node)
                    for link in link_list:
                        if node == link[0]:
                            link_list.remove(link)
                        elif node == link[1]:
                            link_list.remove(link)
                else:
                    node_num -= 1

            if node_num == 0:
                break

        for link in link_list:
            if link[0] in list(self.node.keys()):
                self.node[link[0]][link[1]] = {'weight': 1}
            else:
                tmp_dict = {link[1]: {'weight': 1}}
                self.node[link[0]] = tmp_dict

        for link in self.link:
            if link[0] in list(self.graph.keys()):
                self.graph[link[0]][link[1]] = {'weight': 1}
            else:
                tmp_dict = {link[1]: {'weight': 1}}
                self.graph[link[0]] = tmp_dict

    def pagerank(self, damp=0.15):
        for start_node in list(self.node.keys()):
            for end_node in list(self.node[start_node].keys()):
                self.node[start_node][end_node]['weight'] = (1 / len(self.node[start_node]))
        ans = dict.fromkeys(self.node, 1.0 / len(self.node))
        dangle_weight = ans
        dangle_node = [n for n in self.node if len(self.node[n]) == 0]
        for _ in range(100):
            anslast = ans
            ans = dict.fromkeys(anslast.keys(), 0)
            dead_node = (1 - damp) * sum(anslast[n] for n in dangle_node)
            for n in ans:
                for end_node in self.node[n]:
                    ans[end_node] += (1 - damp) * anslast[n] * self.node[n][end_node]['weight']
                ans[n] += dead_node * dangle_weight[n] + (damp) * dangle_weight[n]
            miss = sum([abs(ans[n] - anslast[n]) for n in ans])
            if miss < len(self.node) * 0.000001:
                break
        self.rank = ans

    def fill_pagerank(self):
        self.remove_node.reverse()
        for node in self.remove_node:
            link_list = list()
            for link in self.link:
                if node == link[1]:
                    link_list.append(link)
            score = int()
            for link in link_list:
                score += self.rank[link[0]] / len(self.graph[link[0]])
            self.rank[node] = score

    def shell(self):
        while True:
            search_str = input('Input: ')
            if search_str == 'bye':
                break
            match_list = list()
            result_dict = dict()
            result_table = list()
            result_rank = 1
            for file in list(self.file.keys()):
                if search_str in self.file[file]:
                    match_list.append(file)
            for match in match_list:
                result_dict[match] = self.rank[self.file_to_node[match]]
            result_dict = sorted(result_dict.items(), key=operator.itemgetter(1), reverse=True)
            for result in result_dict:
                result_table.append([result_rank, result[0]])
                result_rank += 1
            print (tabulate(result_table, headers=["Rank", "Filename"], tablefmt="grid"))

if __name__ == '__main__':
    graph = Graph()
    graph.read_file()
    graph.find_link()
    graph.construct_graph()
    graph.pagerank()
    graph.fill_pagerank()
    graph.shell()

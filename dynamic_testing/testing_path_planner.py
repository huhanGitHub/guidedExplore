import os
import json


class PathPlanner:
    atg_list = []
    reverse_atg_dict = {}
    visited_count = 0
    total_activity = 0
    visited_map = {}
    def __init__(self, atg_json):
        self.atg_list = rank_atg_weight(atg_json)
        self.total_activity = len(self.atg_list)
        self.reverse_atg_dict = reverse_atg(self.atg_list)
        for i in self.atg_list:
            self.visited_map.setdefault(i[0], False)

    def pop_next_activity(self):
        pop = None
        for index, activity in enumerate(self.atg_list):
            if self.visited_map.get(activity[0]) is True:
                continue
            else:
                self.visited_map[activity[0]] = True
                self.visited_count += 1
                pop = activity[0]
                break

        return pop

    def get_in_degrees(self, activity):
        in_degrees = self.reverse_atg_dict.get(activity)
        return in_degrees

    def set_visited(self, activity):
        self.visited_map[activity] = True
        self.visited_count += 1

    def get_visited_rate(self):
        return self.visited_count/self.total_activity


def rank_atg_weight(atg_json):
    with open(atg_json, 'r', encoding='utf8') as f:
        data = [i for i in json.load(f).items()]
        data = sorted(data, key=lambda d: len(d[1]), reverse=True)
        # print(data)
    return data


# build the in degree map of ATG
def reverse_atg(atg):
    reverse_dict = {}
    for i, j in atg:
        for jj in j:
            in_degree = reverse_dict.setdefault(jj, set())
            in_degree.add(i)
            reverse_dict[jj] = in_degree

    return reverse_dict


if __name__ == '__main__':
    atg_json = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/ATG/activity_match/atg/sap_successfactors_mobile.apk.json'
    # atg = rank_atg_weight(atg_json)
    # reverse_atg(atg)
    path_planner = PathPlanner(atg_json)
    print(path_planner.pop_next_activity(), path_planner)




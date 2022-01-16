import os
import json


class PathPlanner:
    atg_list = []
    reverse_atg_dict = {}
    total_activity = 0
    visited_map = {}
    deeplinks = {}

    def __init__(self, atg_json, deeplinks_json):
        self.atg_list = rank_atg_weight(atg_json)
        self.total_activity = len(self.atg_list)
        self.reverse_atg_dict = reverse_atg(self.atg_list)
        for i in self.atg_list:
            self.visited_map.setdefault(i[0], False)
        self.deeplinks = json.load(open(deeplinks_json, 'r', encoding='utf8'))

    def pop_next_activity(self):
        pop = None
        for index, activity in enumerate(self.atg_list):
            if self.visited_map.get(activity[0]) is True:
                continue
            else:
                self.visited_map[activity[0]] = True
                # self.visited_count += 1
                pop = activity[0]
                break

        return pop

    def get_in_degrees(self, activity):
        in_degrees = self.reverse_atg_dict.get(activity)
        return in_degrees

    def set_visited(self, activity):
        if activity is None:
            return
        for k, v in self.visited_map.items():
            if activity in k:
                self.visited_map[k] = True

    def check_visit(self, activity):
        visited = False
        for k, v in self.visited_map.items():
            if activity in k:
                if v:
                    visited = True
                    return visited
        return visited

    def get_activity_full_path(self, activity):
        for k, v in self.visited_map.items():
            if activity in k:
                return k

    def get_visited_rate(self):
        count = 0
        for k, v in self.visited_map.items():
            if v:
                count = count + 1
        return count/self.total_activity

    def get_deeplinks_by_package_activity(self, package, target_activity):
        deeplinks = []
        actions = []
        params = []
        activity_full = None
        packages = self.deeplinks.keys()
        if package in packages:
            activities = self.deeplinks.get(package)
            for activity in activities.keys():
                if target_activity in activity:
                    activity_full = activities.get(activity)
                    break

            if activity_full is None:
                return None, None, None
            else:
                deeplinks_actions = activity_full.get('deeplinks')
                for deeplink, action in deeplinks_actions:
                    deeplinks.append(deeplink)
                    actions.append(action)

                params = activity_full.get('params')

                return deeplinks, actions, params
        else:
            return None, None, None


def rank_atg_weight(atg_json):
    with open(atg_json, 'r', encoding='utf8') as f:
        data = [i for i in json.load(f).items()]
        data = sorted(data, key=lambda d: len(d[1]), reverse=True)
        data = [(i[0].replace('/', '.'), i[1]) for i in data]
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
    deeplinks = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/deeplinks_params.json'
    path_planner = PathPlanner(atg_json, deeplinks)
    print(path_planner.pop_next_activity(), path_planner)




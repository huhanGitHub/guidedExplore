import json


class ParamGenerator:
    intent_paras = {}
    params_types = ['getStringExtra', 'getExtras', 'getIntExtra', 'getBooleanExtra', 'getDoubleExtra', 'getLongExtra', 'getData']
    params_default_values = ['string', 'extras_string', 1, True, 1.1, 2, 'getData']
    params_adb_command = ['--es', '--es', '--ei', '--ez', '--ef', '--el', '--es']
    replace_char_list = [' ']

    def __init__(self, para_json):
        with open(para_json, 'r', encoding='utf8') as f:
            self.intent_paras = json.loads(f.read())

    def get_paras_by_pkg_activity(self, package, activity, assign_value=True):
        activities = self.intent_paras.get(package, None)
        if activities is None:
            return None
        else:
            activity_paras = activities.get(activity, None)
            if activity_paras is None:
                return None
            else:
                if assign_value:
                    return self.assign_default_value2params(activity_paras)
                return activity_paras

    def assign_default_value2params(self, params):
        results = []
        for i in params:
            key = i[0]
            if key == '' or key == ' ':
                continue
            key = str(key).replace(' ', '\\ ')
            value_type = i[1]
            value = 'other'
            cmd = '--es extra_key other'
            if value_type in self.params_types:
                index = self.params_types.index(value_type)
                value = self.params_default_values[index]
                cmd = self.params_adb_command[index]
                results.append(' '.join([cmd, key, str(value)]))
            else:
                results.append(cmd)

        return results

    def merge_deeplinks_params(self, deeplink_json,
                               merged_path=r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/deeplinks_params.json'):
        params = 'params'
        with open(deeplink_json, 'r', encoding='utf8') as f:
            deeplinks = json.loads(f.read())
            for package in deeplinks.keys():
                activities = deeplinks.get(package)
                for activity in activities.keys():
                    params_list = self.get_paras_by_pkg_activity(package, activity)
                    if params_list is not None:
                        activities.get(activity).get(params).extend(params_list)

            with open(merged_path, 'w', encoding='utf8') as save:
                json.dump(deeplinks, save, indent=4)


if __name__ == '__main__':
    params_path = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/intent_para.json'
    params = ParamGenerator(params_path)
    deeplinks_json = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/deeplinks.json'
    params.merge_deeplinks_params(deeplinks_json)
import collections

import xmltodict
import glob
import json
import os
import sys


def injectApk(folderName, deeplinks=r'deeplinks2.txt'):
    # get packageName
    xmlDir = os.path.join(folderName, 'AndroidManifest.xml')

    allLinks = []
    try:
        with open(xmlDir, 'r') as fd:
            doc = xmltodict.parse(fd.read())
            pkName = doc['manifest']['@package']

            # get activity
            schemeName = pkName.replace('.', '_')
            if 'activity' in doc['manifest']['application'].keys():
                for activity in doc['manifest']['application']['activity']:
                    # print(activity)
                    activity['@android:exported'] = True
                    activityName = activity['@android:name']

                    # start inject
                    if 'intent-filter' in activity.keys():
                        # print(activity['intent-filter'], activityName)
                        if type(activity['intent-filter']) == list:
                            activity['intent-filter'].append(
                            {'action': [{'@android:name': 'android.intent.action.VIEW'}],
                             'category': [{'@android:name': 'android.intent.category.DEFAULT'}, {'@android:name': 'android.intent.category.BROWSABLE'}],
                             'data': [{'@android:scheme': schemeName, '@android:host': activityName}]
                             }
                            )
                        else:
                            tempdict = activity['intent-filter']
                            activity['intent-filter'] = [tempdict]
                            activity['intent-filter'].append({'action': [{'@android:name': 'android.intent.action.VIEW'}],
                             'category': [{'@android:name': 'android.intent.category.DEFAULT'}, {'@android:name': 'android.intent.category.BROWSABLE'}],
                             'data': [{'@android:scheme': schemeName, '@android:host': activityName}]
                             }
                            )

                        allLinks.append(f'{schemeName}://{activityName}')
                    else:
                        activity['intent-filter'] = {'action': [{'@android:name': 'android.intent.action.VIEW'}],
                             'category': [{'@android:name': 'android.intent.category.DEFAULT'}, {'@android:name': 'android.intent.category.BROWSABLE'}],
                             'data': [{'@android:scheme': schemeName, '@android:host': activityName}]
                             },
                        allLinks.append(f'{schemeName}://{activityName}')
    except FileNotFoundError as e:
        print(e)
        return
    except TypeError as e:
        print(e)
        return
    except KeyError as e:
        print(e)
        return e

    with open(xmlDir, 'w') as fd:
        fd.write(xmltodict.unparse(doc, pretty=True))

    with open(deeplinks, 'a') as fd:
        fd.write(pkName + '\n')
        fd.write('\n'.join(allLinks))
        fd.write('\n\n\n')


if __name__ == '__main__':
    # get sys args
    args = sys.argv
    folderName = args[1]
    # folderName = 'Amazon Prime Video by Amazon Mobile LLC - com.amazon.avod.thirdpartyclient'
    deeplinks = r'deeplinks2.txt'
    injectApk(folderName, deeplinks)


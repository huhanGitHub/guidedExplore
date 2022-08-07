import collections
import glob
import json
import os
import sys

import xmltodict


def addLinkToDict(schemeName, activityName, linkCount, thisDict, pkName, action):
    deeplinks = "deeplinks"
    params = "params"
    if activityName in thisDict[pkName].keys():
        thisDict[pkName][activityName].get(deeplinks).append(
            [schemeName + "://" + activityName + str(linkCount), action]
        )
    else:
        item = {
            deeplinks: [[schemeName + "://" + activityName + str(linkCount), action]],
            params: [],
        }
        thisDict[pkName][activityName] = item
    return thisDict


def injectApk(folderName, deeplinks=r"deeplinks.json"):
    # get packageName
    xmlDir = os.path.join(folderName, "AndroidManifest.xml")

    allLinks = []
    thisDict = {}
    try:
        with open(xmlDir, "r") as fd:
            doc = xmltodict.parse(fd.read())
            pkName = doc["manifest"]["@package"]
            thisDict = {pkName: {}}

            # get activity
            schemeName = pkName.replace(".", "_")
            if "activity" in doc["manifest"]["application"].keys():
                for activity in doc["manifest"]["application"]["activity"]:
                    # print(activity)
                    linkCount = 0
                    activity["@android:exported"] = True
                    # activityName = activity['@android:name'].split('.')[-1]
                    activityName = activity["@android:name"]
                    # start inject
                    if "intent-filter" in activity.keys():
                        # print(activity['intent-filter'], activityName)
                        if type(activity["intent-filter"]) == list:
                            for i in range(0, len(activity["intent-filter"])):
                                actions = []
                                if "action" not in activity["intent-filter"][i].keys():
                                    continue
                                if type(activity["intent-filter"][i]["action"]) == list:
                                    for ac in activity["intent-filter"][i]["action"]:
                                        actions.append(ac["@android:name"])
                                else:
                                    actions.append(
                                        activity["intent-filter"][i]["action"][
                                            "@android:name"
                                        ]
                                    )

                                if "data" in activity["intent-filter"][i].keys():
                                    if (
                                        type(activity["intent-filter"][i]["data"])
                                        == list
                                    ):
                                        linkCount += 1
                                        activity["intent-filter"][i]["data"].append(
                                            {
                                                "@android:scheme": schemeName,
                                                "@android:host": activityName
                                                + str(linkCount),
                                            }
                                        )
                                    else:
                                        linkCount += 1
                                        activity["intent-filter"][i]["data"] = [
                                            activity["intent-filter"][i]["data"],
                                            {
                                                "@android:scheme": schemeName,
                                                "@android:host": activityName
                                                + str(linkCount),
                                            },
                                        ]
                                else:
                                    linkCount += 1
                                    activity["intent-filter"][i]["data"] = [
                                        {
                                            "@android:scheme": schemeName,
                                            "@android:host": activityName
                                            + str(linkCount),
                                        }
                                    ]
                                for action in actions:
                                    thisDict = addLinkToDict(
                                        schemeName,
                                        activityName,
                                        linkCount,
                                        thisDict,
                                        pkName,
                                        action,
                                    )

                            linkCount += 1
                            activity["intent-filter"].append(
                                {
                                    "action": [
                                        {"@android:name": "android.intent.action.VIEW"}
                                    ],
                                    "category": [
                                        {
                                            "@android:name": "android.intent.category.DEFAULT"
                                        },
                                        {
                                            "@android:name": "android.intent.category.BROWSABLE"
                                        },
                                    ],
                                    "data": [
                                        {
                                            "@android:scheme": schemeName,
                                            "@android:host": activityName
                                            + str(linkCount),
                                        }
                                    ],
                                }
                            )

                            thisDict = addLinkToDict(
                                schemeName,
                                activityName,
                                linkCount,
                                thisDict,
                                pkName,
                                "android.intent.action.VIEW",
                            )
                        else:
                            # add single intent-filter
                            actions = []
                            if "action" not in activity["intent-filter"]:
                                continue
                            if type(activity["intent-filter"]["action"]) == list:
                                for ac in activity["intent-filter"]["action"]:
                                    actions.append(ac["@android:name"])
                            else:
                                actions.append(
                                    activity["intent-filter"]["action"]["@android:name"]
                                )

                            if "data" in activity["intent-filter"].keys():
                                if type(activity["intent-filter"]["data"]) == list:
                                    linkCount += 1
                                    activity["intent-filter"]["data"].append(
                                        {
                                            "@android:scheme": schemeName,
                                            "@android:host": activityName
                                            + str(linkCount),
                                        }
                                    )
                                else:
                                    linkCount += 1
                                    activity["intent-filter"]["data"] = [
                                        activity["intent-filter"]["data"],
                                        {
                                            "@android:scheme": schemeName,
                                            "@android:host": activityName
                                            + str(linkCount),
                                        },
                                    ]
                            else:
                                linkCount += 1
                                activity["intent-filter"]["data"] = [
                                    {
                                        "@android:scheme": schemeName,
                                        "@android:host": activityName + str(linkCount),
                                    }
                                ]
                            for action in actions:
                                thisDict = addLinkToDict(
                                    schemeName,
                                    activityName,
                                    linkCount,
                                    thisDict,
                                    pkName,
                                    action,
                                )

                            tempdict = activity["intent-filter"]
                            activity["intent-filter"] = [tempdict]
                            linkCount += 1
                            activity["intent-filter"].append(
                                {
                                    "action": [
                                        {"@android:name": "android.intent.action.VIEW"}
                                    ],
                                    "category": [
                                        {
                                            "@android:name": "android.intent.category.DEFAULT"
                                        },
                                        {
                                            "@android:name": "android.intent.category.BROWSABLE"
                                        },
                                    ],
                                    "data": [
                                        {
                                            "@android:scheme": schemeName,
                                            "@android:host": activityName
                                            + str(linkCount),
                                        }
                                    ],
                                }
                            )
                        thisDict = addLinkToDict(
                            schemeName,
                            activityName,
                            linkCount,
                            thisDict,
                            pkName,
                            "android.intent.action.VIEW",
                        )
                    else:
                        linkCount += 1
                        activity["intent-filter"] = {
                            "action": [{"@android:name": "android.intent.action.VIEW"}],
                            "category": [
                                {"@android:name": "android.intent.category.DEFAULT"},
                                {"@android:name": "android.intent.category.BROWSABLE"},
                            ],
                            "data": [
                                {
                                    "@android:scheme": schemeName,
                                    "@android:host": activityName + str(linkCount),
                                }
                            ],
                        }
                        thisDict = addLinkToDict(
                            schemeName,
                            activityName,
                            linkCount,
                            thisDict,
                            pkName,
                            "android.intent.action.VIEW",
                        )
    except FileNotFoundError as e:
        print(e)
        return
    except TypeError as e:
        print(e)
        return
    except KeyError as e:
        print(e)
        return e

    with open(xmlDir, "w") as fd:
        fd.write(xmltodict.unparse(doc, pretty=True))

    if os.path.exists(deeplinks):
        with open(deeplinks, "r", encoding="utf8") as f:
            oldDict = f.read()
            if oldDict != "":
                oldDict = json.loads(oldDict)
                newDict = {**oldDict, **thisDict}
            else:
                newDict = thisDict
    else:
        newDict = thisDict
    with open(deeplinks, "w", encoding="utf8") as fd:
        json.dump(newDict, fd, indent=4)

    # if os.path.exists(deeplinks):
    #     with open(deeplinks, 'a+', encoding='utf8') as f:
    #         oldDict = json.loads(f.read())
    #         newDict = {**oldDict, **thisDict}
    #     with open(deeplinks, 'a+', encoding='utf8') as fd:
    #         json.dump(newDict, fd, indent=4)
    # else:
    #     with open(deeplinks, 'a+', encoding='utf8') as fd:
    #         json.dump(thisDict, fd, indent=4)


if __name__ == "__main__":
    # get sys args
    args = sys.argv
    # folderName = args[1]
    folderName = r"../data/recompiled_apks/realtor"
    # folderName = 'Amazon Prime Video by Amazon Mobile LLC - com.amazon.avod.thirdpartyclient'
    deeplinks = r"../data/deeplinks.json"
    injectApk(folderName, deeplinks)

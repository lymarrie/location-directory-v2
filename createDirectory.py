from yext import YextClient
import json
from types import SimpleNamespace
import time

client = YextClient('')

def getEntities(params):
    return(client.get_all_entities(params))

def getLocations():
    params = {"entityTypes":"location"}
    return(client.get_all_entities(params))

def getCities():
    params = {"entityTypes":"ce_city"}
    return(client.get_all_entities(params))

def getStates():
    params = {"entityTypes":"ce_state"}
    return(client.get_all_entities(params))


def createParents():
    newCities = []
    newStates = []
    abbreviations = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}

    # Add any existing cities/states in the account so we don't double-count
    cities = getCities()
    states = getStates()
    for city in cities:
        if city["name"] not in newCities:
            newCities.append(city["name"])
    for state in states:
        if state["name"] not in newStates:
            newStates.append(state["name"]) 
    print("Cities already in the platform: ", newCities)
    print("States already in the platform: ", newStates)   

    #  Create new city/state entities
    entities = getLocations()
    for entity in entities:
        if entity["address"]["city"] not in newCities:
            newCities.append(entity["address"]["city"])
            entityID = entity["address"]["city"].replace(" ", "") + entity["address"]["region"]
            profile = {
                'meta': {
                    'id': entityID,
                    'countryCode': 'US'
                },
                'name': entity["address"]["city"]
            }
            # Create city entity
            client.create_entity('ce_city', profile)
        if abbreviations[entity["address"]["region"]] not in newStates:
            newStates.append(abbreviations[entity["address"]["region"]])
            profile = {
                'meta': {
                    'id': entity["address"]["region"],
                    'countryCode': 'US'
                },
                'name': abbreviations[entity["address"]["region"]]
            }
            # Create state entity
            client.create_entity('ce_state', profile)
    print("created ", newCities, "\n", newStates)

def setParents():
    print("\nSetting parents\n")
    # Set city as parent for each location
    locations = getLocations()
    for location in locations:
        entityID = location["meta"]["id"]
        parentID = location["address"]["city"].replace(" ", "") + location["address"]["region"]
        print("Setting - ", parentID, " -  as parent for  - ", entityID)
        profile = {
            'meta': {
                'id': entityID,
                'countryCode': 'US'
            },
            'c_parents': [parentID]
        }
        client.update_entity(entityID, profile)
    # Set state as parent for each city
    cities = getCities()
    for city in cities:
        entityID = city["meta"]["id"]
        parentID = entityID[-2:]
        print("Setting - ", parentID, " -  as parent for  - ", entityID)
        profile = {
            'meta': {
                'id': entityID,
                'countryCode': 'US'
            },
            'c_parents': [parentID]
        }
        client.update_entity(entityID, profile)


def setChildren():
    print("\nSetting children\n")
    states = getStates()
    # Set city as child for each state
    for state in states:
        entityID = state["meta"]["id"]
        params = {
            "entityTypes":"ce_city",
            "filter": json.dumps({"c_parents":{"$eq":entityID}})
        }
        childCities = getEntities(params)
        children = []
        for city in childCities:
            print("Setting - ", city["name"], " -  as child of  - ", state["name"])
            children.append(city["meta"]["id"])
        profile = {
            'meta': {
                'id': entityID,
                'countryCode': 'US'
            },
            'c_children': children
        }
        client.update_entity(entityID, profile)
    # Set location as child for each city
    cities = getCities()
    for city in cities:
        entityID = city["meta"]["id"]
        params = {
            "entityTypes":"location",
            "filter": json.dumps({"c_parents":{"$eq":entityID}})
        }
        locations = getEntities(params)
        children = []
        for location in locations:
            print("Setting - ", location["name"], " -  as child of  - ", city["name"])
            children.append(location["meta"]["id"])
        profile = {
            'meta': {
                'id': entityID,
                'countryCode': 'US'
            },
            'c_children': children
        }
        client.update_entity(entityID, profile) 


def createDirectory():
    createParents()
    time.sleep(5)
    setParents()
    time.sleep(5)
    setChildren()


if __name__ == '__main__':
    createDirectory()
    # setChildren()
    # params = {
    #     "entityTypes":"location",
    #     "fields":"name,c_parents",
    #     "filter": json.dumps({"name":{"$eq":"86th and Lexington"}})
    # }

    # print(getEntities(params))
    # locs = getLocations()
    # cities = getCities()
    # states = getStates()
    # cities, states = createParents(locs, cities, states)
    # print(cities)
    # print(states)
    # setParents(locs, cities)
    # setChildren()
    # data = json.loads(str(locs[0]))
    # print(data["name"])
    # x = json.loads(locs, object_hook=lambda d: SimpleNamespace(**d))
    # print(x.name, x.address.city, x.address.region)
    # print(getStates())

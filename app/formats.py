# request --headers
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Host': 'cityexpert.rs',
    'User-Agent':'Mozilla/5.0',
    'Content-Type': 'application/json',
    'Referer': 'https://cityexpert.rs/en/properties-for-sale-in-belgrade',
}

# request --data
data = """{{
    "ptId":[],
    "cityId":1,
    "rentOrSale":"s",
    "currentPage":{0},
    "resultsPerPage":100,
    "floor":[],
    "avFrom":'false',
    "underConstruction":false,
    "furnished":[],
    "furnishingArray":[],
    "heatingArray":[],
    "parkingArray":[],
    "petsArray":[],
    "minPrice":null,
    "maxPrice":null,
    "minSize":null,
    "maxSize":null,
    "polygonsArray":[],
    "searchSource":"regular",
    "sort":"datedsc",
    "structure":[],
    "propIds":[],
    "filed":[],
    "ceiling":[],
    "bldgOptsArray":[],
    "joineryArray":[],
    "yearOfConstruction":[],
    "otherArray":[],
    "numBeds":null,
    "category":null,
    "maxTenants":null,
    "extraCost":null,
    "numFloors":null,
    "numBedrooms":null,
    "numToilets":null,
    "numBathrooms":null,
    "heating":null,
    "bldgEquipment":[],
    "cleaning":null,
    "extraSpace":[],
    "parking":null,
    "parkingIncluded":null,
    "parkingExtraCost":null,
    "parkingZone":null,
    "petsAllowed":null,
    "smokingAllowed":null,
    "aptEquipment":[],
    "site":"SR"
}}"""


# theese keys carry no information (always 0/false/null)
keys_to_delete = [
	"category",
    "maxTenants",
    "extraCost",
    "numFloors",
    "numBedrooms",
    "numFrenchBeds",
    "numSingleBeds",
    "numAuxBeds",
    "numBeds",
    "heating",
    "bldgEquipment",
    "cleaning",
    "extraSpace",
    "parking",
    "parkingIncluded",
    "parkingExtraCost",
    "parkingZone",
    "petsAllowed",
    "partiesAllowed",
    "smokingAllowed",
    "blockedDates",
    "score",
    "ceiling",
    "furnishing",
    "furnishingArray",
    "bldgOptsArray",
    "heatingArray",
    "parkingArray",
    "yearOfConstruction",
    "joineryArray",
    "petsArray",
    "otherArray",
    "aptEquipment"
]

furnished_dict = ["N/A", "Furnished", "Semi furnished", "Unfurnished" ]
filed_dict = ["N/A", "Unregistered", "Registered"]
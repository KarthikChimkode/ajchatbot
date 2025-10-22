import json 

with open("lawfeat_services_api.json", "r", encoding="utf-8") as f:
    data = json.load(f)



result = []


for category in data:
    category_name = category.get("name", "No Name")
    services = category.get("services", [])

    service_names = [service.get("serviceName", "No ServiceName") for service in services]

    result.append({
        "name": category_name,
        "services": service_names
    })


with open("extracted_services.json", "w") as outfile:
        json.dump(result, outfile, indent=2)

print("Extracted done")
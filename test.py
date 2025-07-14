import json
with open("database/datauser.json","r",encoding="UTF-8") as openedfile : 
    get_data = json.load(openedfile)
with open("database/datauser.json","w",encoding="UTF-8") as openedfile : 
    new_user = {
        "username" : "phuc",
        "pass" : "2502",
        "age" : 16,
        "gender" : "male",
        "hobby" : ["chơi game","thể thao"]
    }
    get_data["userlist"].append(new_user)
    json_data = json.dumps(get_data, indent=4, ensure_ascii=False)
    openedfile.write(json_data)
    print("đã ghi file")


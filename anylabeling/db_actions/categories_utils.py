import json
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv
# we import the random module
import random

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

print('connected to database')

def cat_id_to_name(cat_id: str):
    response = supabase.table("categories").select("name_en").eq("numeric_label", cat_id).execute().model_dump_json()
    data = json.loads(response)['data']
    if data:
        return json.loads(json.dumps(data[0]))['name_en']
    else:
        print('No category found for id')
        return None

def convert_hex_to_rgb(hex_color: str):
    return tuple(int(hex_color[i+1:i+3], 16) for i in (0, 2, 4))

def get_color_from_category(category: str):
    random_color = '#'+str(hex(random.randint(0,16777215)))[2:]
    
    response = supabase.table("categories").select("color").eq("name_en", category).execute().model_dump_json()
    data = json.loads(response)['data']
    if data:
        return json.loads(json.dumps(data[0]))['color']
    else:
        print('No color found for category, returning random color')
        rgb_color = convert_hex_to_rgb(random_color)
        return rgb_color

def get_categories_json_list():
    response = supabase.table("categories").select().execute().model_dump_json()
    return json.loads(response)['data']

def get_categories_json_list_by_model_id(model_id: str):
    response = supabase.table("categories").select().eq("model_id", model_id).execute().model_dump_json()
    return json.loads(response)['data']

def get_categories_json_list_by_model_id_via_supabase(model_id: str):
    response = supabase.table("Models").select().eq("id", model_id).execute().model_dump_json()
    return json.loads(response)['data'][0]['categories_id']

def category_json_list_to_list(json_list: list):
    category_list=[] 
    for cat in json_list:
        category_list.append(cat['name_en'])
    return category_list

# temporary dict - should come from database
orga_model_list = {
    "org_2n9vPpSVH3TOsa3InZy4sQp4pOe": 2,
    "org_2jLn0za5IpTINBIcnkCpmlyzlIi": 1,
    "org_2jL92CAVIJ2ycDl054mHRvHMDkn": 1  
}

orga_desc= {
    "org_2n9vPpSVH3TOsa3InZy4sQp4pOe": "Wastetide-test only for sorting errors",
    "org_2jLn0za5IpTINBIcnkCpmlyzlIi": "X-tract",
    "org_2jL92CAVIJ2ycDl054mHRvHMDkn": "X-Studio avec un nom long"
}

def get_model_id_from_organization(organization_id: str):
    ### TODO : get model id from dynamic database (Clerk)
    
    return orga_model_list[organization_id]

def get_category_list_from_organization(organization_id: str):
    model_id = get_model_id_from_organization(organization_id)
    categories = get_categories_json_list_by_model_id(model_id)
    return category_json_list_to_list(categories)

def get_category_list_from_organization_via_supabase(organization_id: str):
    model_id = get_model_id_from_organization(organization_id)
    categories_id = get_categories_json_list_by_model_id_via_supabase(model_id)
    categories_name = []
    for cat_id in categories_id['categories']:
        categories_name.append(cat_id_to_name(cat_id))
    return categories_name

print(get_category_list_from_organization_via_supabase("org_2jLn0za5IpTINBIcnkCpmlyzlIi"))
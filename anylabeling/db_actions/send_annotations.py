import json
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

print('connected to database')

class_2_label_bins = {
      "biowaste": 0,
      "cardboard": 1,
      "electronic": 2,
      "glass": 3,
      "hazardous": 4,
      "metal": 5,
      "other": 6,
      "paper": 7,
      "plastic": 8,
      "textile": 9,
        "wood": 10,
        "PS": 12,
        "plastic PE": 8,
        "plastic PET": 11,
        "Plastic PE": 8,
        "Plastic PET": 11,
        "Plastic PS": 8,
        "Plastic PVC":8,
        "plastic pp":8,
        "plastic ps":12,
        "plastic PP":8,
        "Plastic PP":8,
        "plastic pe":8,
        "plastic PS":12,
        "Wood": 10,
        "metals": 5,
        "Sand/Minerals": 6,
        "plastic toxic": 6,
        "mineral wool": 6,
        "e-waste": 2,
        "Plywood": 10,
        "Textile": 9,
        "TEXTILE":9,
        "Cardboard": 1,
        "DIB/OMR": 6,
        "Paint": 6,
        "Paper": 7,
        "Plastic": 8,
        "plywood": 10,
        "Silicate":5,
        "plastic PVC":8,
        
        
    }

default_path = '/Users/macbook/Desktop/annotations/'


def write_txt_from_json(json_path: str, class_2_label: dict,path=default_path):
    with open(os.path.join(path, json_path), 'r') as file:
        data = json.load(file)
        #the image name
        image_name = data['imagePath']
        #the image height
        image_height = data['imageHeight']
        #the image width
        image_width = data['imageWidth']
        
        
        #we create a .txt file with the same name as the image with yolo format
        if os.path.exists(os.path.join(path, image_name.split('.')[0] + '.txt')):
            os.remove(os.path.join(path, image_name.split('.')[0] + '.txt'))
                
        #now we create the .txt file
        with open(os.path.join(path, image_name.split('.')[0] + '.txt'), 'w') as file:
            file.write(' ')        
        
        #the points of the polygon
        for polygon in data['shapes']:
            points = polygon['points']
            #the x and y coordinates of the points
            x = [point[0] for point in points]
            y = [point[1] for point in points]
            
            #the bounding box coordinates
            x_min = min(x)
            x_max = max(x)
            y_min = min(y)
            y_max = max(y)
            
            #the class label
            #we raise an error if the class is not in the class_2_label dictionary
            if polygon['label'] not in class_2_label:
                print(f'Class {polygon["label"]} not in class_2_label dictionary')
                raise ValueError('Class not in class_2_label dictionary')
            label = class_2_label[polygon['label']]
            
            
            
            with open(os.path.join(path, image_name.split('.')[0] + '.txt'), 'a') as file:
                
                #we write the class label and the bounding box coordinates
                file.write(f'{label} {(x_min + x_max) / 2 / image_width} {(y_min + y_max) / 2 / image_height} {(x_max - x_min) / image_width} {(y_max - y_min) / image_height}\n')

def write_txt_from_all_jsons(path=default_path,annotation_list=None):
    for annotation_path in annotation_list:
        write_txt_from_json(annotation_path, class_2_label_bins,path=path)

    
keys = {"recyclable_keys": [1, 3, 5, 7, 8], "compostable_keys": [0], "hazardous_keys": [2, 4]}

def get_status_from_key(key: int, keys: dict):
    for status, key_list in keys.items():
        if key in key_list:
            return status.split('_')[0]
    
[{"box":[0.69140625,0.7453125,0.1328125,0.1625],"confidence":0.8330577611923218,"class":8,"status":"recyclable","score":0.017979078635107726},{"box":[0.71171875,0.6953125,0.1890625,0.23125],"confidence":0.2624787986278534,"class":8,"status":"recyclable","score":0.011475757631415036}]
[{"box":[0.9671875,0.78046875,0.065625,0.4015625],"confidence":0.26497554779052734,"class":7,"status":"recyclable","score":0.006982778473757207},{"box":[0.7671875,0.58046875,0.165625,0.4015625],"confidence":0.26497554779052734,"class":3,"status":"recyclable","score":0.006982778473757207}]
[{"box":[0.2484375,0.534375,0.478125,0.925],"confidence":0.5589472055435181,"class":9,"status":"unclassified","score":0.2472031352017075}]


#we want to send the annotations to the database in that format 

def annotations_from_txt(txt_path: str,path=default_path):
    if not os.path.exists(os.path.join(path, txt_path)):
        return []
    with open(os.path.join(path, txt_path), 'r') as file:
        annotations = []
        for line in file:
            line = line.strip().split(' ')
            if line[0] == '':
                continue
            class_label = int(line[0])
            x_center = float(line[1])
            y_center = float(line[2])
            width = float(line[3])
            height = float(line[4])
            area = width * height
            annotations.append({'box': [x_center, y_center, width, height], 'class': class_label, 'confidence': 1,'status': get_status_from_key(class_label, keys),'score': area })
            
        return annotations

def threshold_from_annotation(annotations: list):
    res = {}
    for key in keys:
        for annotation in annotations:
            if annotation['status'] == key.split('_')[0]:
                if key not in res:
                    res[key.split('_')[0]] = annotation['score']
                else:
                    res[key.split('_')[0]] += annotation['score']
    
    # we normalize the scores
    total = sum(res.values())
    for key in res:
        res[key] /= total
        res[key]*=100
    
    return res

#not tested
def send_annotations(scan_id: str, annotations: list,blank=False):
    # we verify that the scan exists
    '''response = supabase.table('Scan').select().eq('id', scan_id).execute()
    if response['status'] != 200:
        raise ValueError('Scan not found')'''
    if blank:
        supabase.table('ScanResult').update({'validated': 'TRUE'}).eq('scanId', scan_id).execute()
        return
    
    supabase.table('ScanResult').update({'responseData': json.dumps(annotations)}).eq('scanId', scan_id).execute()
    supabase.table('ScanResult').update({'thresholds': threshold_from_annotation(annotations)}).eq('scanId', scan_id).execute()
    supabase.table('ScanResult').update({'validated': 'TRUE'}).eq('scanId', scan_id).execute()

def move_scan(scan_id, destination, path=default_path):
    # after the annotations are sent, we move the images to another folder
    if not os.path.exists(destination):
        os.makedirs(destination)
        
    if not os.path.exists(f'{path}/{scan_id}.jpg'):
        raise ValueError('No image file found')
        
    if not os.path.exists(f'{path}/{scan_id}.txt'):
        raise ValueError('No txt file found')
    
    if not os.path.exists(f'{path}/{scan_id}.json'):
        raise ValueError('No json file found')
    
    os.rename(f'{path}/{scan_id}.jpg', f'{destination}/{scan_id}.jpg')
    os.rename(f'{path}/{scan_id}.txt', f'{destination}/{scan_id}.txt')
    os.rename(f'{path}/{scan_id}.json', f'{destination}/{scan_id}.json')
    

def upload_all_scans(path=default_path, destination=default_path):
    
    annotation_list = [ann_path for ann_path in os.listdir(path) if ann_path.endswith('.json')]
    
    write_txt_from_all_jsons(path=path,annotation_list=annotation_list)
    
    for annotation_path in annotation_list:
        scan_id = annotation_path.split('.')[0]
        annotations = annotations_from_txt(scan_id + '.txt',path)
        
        try:
            send_annotations(scan_id, annotations)
        except Exception as e:
            print(f"Failed to send annotations for scan_id {scan_id}: {e}")
        
        #i want the destination to be in the same folder as the path
        
        if destination == default_path:
            destination = os.path.join(default_path, 'reviewed_images')
        
        move_scan(scan_id, destination, path)
        
    print(f'{len(annotation_list)} annotations sent')
    print(f'{len(annotation_list)} images moved to reviewed_images folder')


if __name__ == '__main__':
    
    default_path = '/Users/macbook/Desktop/annotations/NB'
    
    annotation_list = [ann_path for ann_path in os.listdir(default_path) if ann_path.endswith('.json')]
    
    write_txt_from_all_jsons(default_path,annotation_list)


    '''nb_annotations = len(annotation_list)

    print(f'{nb_annotations} annotations to upload')


    for annotation_path in annotation_list:
        
        scan_id = annotation_path.split('.')[0]
        
        annotation_txt = scan_id + '.txt'
        
        annotations = annotations_from_txt(annotation_txt,default_path)
        print(annotations)
        send_annotations(scan_id, annotations)
        #move_scan(scan_id, 'reviewed_images', default_path)
        
    print(f'{nb_annotations} annotations sent')

    print(f'{nb_annotations} images moved to reviewed_images folder')'''
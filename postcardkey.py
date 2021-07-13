#-*-coding:utf-8-*-
import requests,json
import http.client
import mimetypes
from codecs import encode
url = "http://ec2-3-36-107-134.ap-northeast-2.compute.amazonaws.com/api/truck/check_out"
url2 = "http://ec2-3-36-107-134.ap-northeast-2.compute.amazonaws.com/api/truck/check_out_postprocess"
dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
def post_cardkey(user_id,session_key,site_uuid,card_key):
    global boundary,dataList,url
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=user_id;'))
    
    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
 
    dataList.append(encode(user_id))
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=session_key;'))

    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))

    dataList.append(encode(session_key))
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=site_uuid;'))

    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))
    
    dataList.append(encode(site_uuid))
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=card_key;'))

    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))

    dataList.append(encode(card_key))
    dataList.append(encode('--'+boundary+'--'))
    dataList.append(encode(''))
    body = b'\r\n'.join(dataList)
    payload=body
    files=[]
    headers = {'Host':'ec2-3-36-107-134.ap-northeast-2.compute.amazonaws.com',
            'Content-Type': 'multipart/form-data; boundary=wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'}
    #s=requests.session()
    #s.cookies.clear()
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    
    #response = s.post(url, headers=headers, data=payload, files=files)
    #print(response.text)
    html=response.text
    #print(payload)
    dataList = []
    #response.close()
    
    jsonObj=json.loads(html)
    reg_card=jsonObj.get('resultList')[0].get('reg_card')
    daily_count=jsonObj.get('resultList')[0].get('daily_count')
    monthly_count=jsonObj.get('resultList')[0].get('monthly_count')
    driver_name=jsonObj.get('resultItem').get('driver_name')
    truck_plate=jsonObj.get('resultItem').get('truck_plate')
    #driver_message=jsonObj.get('resultItem').get('driver_message')
    correlation_id=jsonObj.get('resultItem').get('correlation_id')
    #return_card_key=jsonObj.get('resultItem').get('card_key')
    #print(jsonObj.get('resultCode'))
    #return_value=[jsonObj.get('resultCode')]
    return_value=[reg_card]
    return_value.append(correlation_id)
    return_value.append(truck_plate)
    return_value.append(daily_count)
    return_value.append(monthly_count)
    return return_value

def post_file(user_id,session_key,correlation_id,plate_photo):
    global boundary,dataList,url2
    payload={'user_id':user_id,
            'session_key':session_key,
            'correlation_id':correlation_id}
    files=[('plate_photo',(plate_photo,open(plate_photo,'rb'),'image/jpeg'))]
    headers={}
    response=requests.request("POST",url2,headers=headers,data=payload,files=files)
    html=response.text
    jsonObj=json.loads(html)
    
    return jsonObj.get('resultCode')

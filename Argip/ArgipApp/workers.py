import json
import requests
import time
from google.cloud import translate_v2 as translate
from .models import Category
from .models import Product
import sys


class ArgipWorker(object):
    """
    ARGIP API worker class.
    """

    def __init__(self):
        self.times_begin = time.time() # Check token work time
        self.url = "https://argipapi.argip.com.pl/v1/"
        self.CID = 'Hmij5VYvJwsp3VVtpzVDEe5ITcML9MDx'
        self.SECRET = 'cAVLbd8rJF8R8WpWtz9vvoj7vMyUM84KTHrbThbkgyw2MMRdTgIqzkmFJlTZbogB'
        data = {'client_id':self.CID,
                'client_secret':self.SECRET,
                'grant_type':'client_credentials'}
        resp = json.loads(requests.post('https://identityserver.argip.com.pl/connect/token', data).text)
        self.token = resp['access_token']
        self.token_expired = resp['expires_in']

    def check_token(self):
        work_time = time.time() - self.times_begin
        if (work_time >= int(self.token_expired)):
            self.__init__()

    def api_call(self, method, data = {}):
        headers = {'Authorization':'Bearer ' + self.token}
        url = self.url + method
        response = json.loads(requests.get(url, headers = headers, params = data).text)
        #print(response)
        return response

    def make_products(self):
        headers = {'Authorization':'Bearer ' + self.token}
        for i in range(1,19):
            try:
                products_url = f"https://argipapi.argip.com.pl/v1/Products/{i}/1000/true"
                products = json.loads(requests.get(products_url, headers = headers).text)
            except:
                i = i - 1
                pass
            print(products)
            k = 1
            for product in products:
                product_exist = Product.objects.filter(barcode = product['EanBarcode'])
                if not product_exist:
                    if product['IsActive'] and product['YourMainPrice'] and product['PiecesInStock']:
                        new_product = Product()
                        new_product.name = product['ProductFullName']
                        new_product.price = int(float(product['YourMainPrice']) * 1.8 * 1.5)
                        new_product.argip_category_id = product['CategoryMapping']
                        new_product.summary = "Размер одной партии " + str(product['SinglePackQuantityInPieces']) + " ед."
                        new_product.barcode = product['EanBarcode']
                        new_product.count = product['PiecesInStock']
                        new_product.purchase_price = int(float(product['YourMainPrice']) * 1.8)
                        new_product.save()
                        time.sleep(0.05)
                else:
                    product_set_image = Product.objects.get(barcode = product['EanBarcode'])
                    product_set_image.image_url = product['PictureUrl']
                    product_set_image.save()
                    print('Product already exist')
                k = k + 1
                print(f'PAGE {i} FROM 19 --- PRODUCT {k} FROM 1000')




    def make_categories(self):
        i = 0
        categories_info = self.api_call('Categories')
        cat_length = len(categories_info)
        print('Vsego kategoriy ' + str(cat_length))
        for category in categories_info:
            print('SAVE ' + str(i) + ' FROM ' + str(cat_length))
            category_exist = Category.objects.filter(argip_id = category['CategoryId'])
            if not category_exist:
                new_category = Category()
                new_category.parent_category_id_argip = category['ParentCategoryId']
                new_category.argip_id = category['CategoryId']
                new_category.name = category['Name']
                new_category.save()
                time.sleep(0.2)
            i = i + 1
        return categories_info

    def download_images(self):
        products = Product.objects.exclude(image_url = '1', local_image_url = '1')
        count = products.count()
        i = 5346
        for product in products:

            try:
                img = requests.get(product.image_url)
                with open(f'images/img_{i}.jpg', 'wb') as out:
                    out.write(img.content)
                product.local_image_url = f'images/img_{i}.jpg'
                product.save()
            except Exception:
                print(f'Проблема с загрузкой изображения {product.name}')
                continue
            print(f'Загружено {i} из {count}')
            i = i + 1


class ShopScriptWorker(object):
    """
    ShopScript API worker class
    """
    def __init__(self):
        sys.setrecursionlimit(3000)
        #self.translator = GoogleWorker()
        self.start_call = 0
        self.token = 'ad213ea1de8cdab7e54f2aad44824962'
        self.url = 'https://struverus.webasyst.cloud/api.php/'

    def api_call(self, method, data = {}):
        if (time.time() - self.start_call < 0.3):
            time.sleep(0.3)
        self.start_call = time.time()
        data['access_token'] = self.token
        api_call_url = self.url + method
        while True:
            try:
                time.sleep(0.5)
                print('Попытка заливки')
                response = json.loads(requests.post(api_call_url, data).text)
                break
            except Exception:
                continue
        return response

    def image_api_call(self, product_id, file):
        api_call_url = f'{self.url}shop.product.images.add/?access_token={self.token}&product_id={product_id}'
        with open(file,'rb') as f:
            response = json.loads(requests.post(api_call_url, files = {'file':f}).text)
        return response

    def make_categories(self, list_of_cats):
        new_list = []
        cats = Category.objects.filter(parent_category_id_argip__in = list_of_cats)
        for ct in cats:
            par_cat = Category.objects.get(argip_id = ct.parent_category_id_argip)
            translated_name = self.translator.translate(ct.name)
            data = {'name':translated_name, 'parent_id': par_cat.shop_id}
            response = self.api_call('shop.category.add',data)
            try:
                if response['error_description'] == 'Parent category not found' :
                    data = {'name':translated_name, 'parent_id': '7212'}
                    response = self.api_call('shop.category.add',data)
                    print(f'Залита категория {ct.name} переведена как {translated_name}, но залита в корень')
            except Exception:
                print(f'Залита категория {ct.name} переведена как {translated_name}')
            ct.shop_id = response['id']
            ct.parent_category_id_shop = par_cat.shop_id
            ct.save()
            new_list.append(ct.argip_id)
        self.make_categories(new_list)

    def make_products(self):
        i = 0
        products = Product.objects.exclude(shop_id__icontains='10')
        counter = products.count()
        for product in products:
            try:
                product_cat = Category.objects.get(argip_id = product.argip_category_id)
            except Exception:
                product_cat = Category.objects.get(shop_id = '6197')
            if product_cat.shop_id == '1':
                product_cat = Category.objects.get(shop_id = '6197')
            data = {
        		'name': product.name,
        		'price': str(int(float(product.price) * 1.8 * 1.5)),
        		'categories[]':product_cat.shop_id,
        		"summary": product.summary,
        		'sku_type':0,
        		'skus[0][name]': product.barcode,
        		'skus[0][virtual]':0,
        		'skus[0][price]': str(int(float(product.price) * 1.8 * 1.5)),
        		'skus[0][available]': 1,
        		'skus[0][count]':  product.count,
        		"skus[0][purchase_price]": str(int(float(product.price) * 1.8))
        		# 'skus':[{'virtual':1, 'sku':art}],
        	}
            try:
                response = self.api_call('shop.product.add',data)
                product.shop_id = response['id']
                product.is_updated = '1'
                id = response['id']
                product.save()
                print(f'Залит товар {product.name}, по счету {i} из {counter}, получил ID {id}, в категорию {product_cat.name}')
                i = i + 1
            except Exception:
                print(f'Проблемы с заливкой товара {product.name}, по счету {i} из {counter}')
                continue



    def make_images(self):
        file_url = 'test/test123.png'
        response = self.image_api_call('98932',file_url)
        print(response)

class GoogleWorker(object):
    def __init__(self):
        self.translate_client = translate.Client()

    def translate(self,text):
        result = self.translate_client.translate(text, target_language='en')
        return(result['translatedText'])

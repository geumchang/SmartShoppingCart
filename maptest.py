from flask import Flask, request, jsonify, render_template, redirect, url_for
from PIL import Image, ImageDraw
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from flask import render_template
import subprocess
app = Flask(__name__)

shopping_cart = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        barcode = request.form['barcode']
        product_info = lookup_product_by_barcode(barcode)

        if product_info:
            update_cart(product_info)
            return render_template('cart.html', cart=shopping_cart, total=calculate_total(), context='scan')
        else:
            return render_template('result.html', error_message="Product not found")
    return render_template('scan.html')

def lookup_product_by_barcode(barcode):
    products = {
        '123456789': {'name': '포카리스웨트', 'price': 2000, 'category': 'Beverage'},
        '987654321': {'name': '포카칩', 'price': 1500, 'category': 'Snack'},
        '8801116013234': {'name': '믹스 아이스 더블', 'price': 4500, 'category': 'cigarette'},
        '98897447': {'name': '신라면', 'price': 1200, 'category': 'Noodle'},
        '1234567839': {'name': '테라', 'price': 2000, 'category': 'Beverage'},
        '9876543231': {'name': '된장', 'price': 1500, 'category': 'Snack'},
        '88011160133234': {'name': '모자', 'price': 4500, 'category': 'cigarette'},
        '988974473': {'name': '냄비', 'price': 1200, 'category': 'Noodle'},
        '8809001250320': {'name': '대명 참숯', 'price': 30000, 'category': '캠핑'},
        '8804987519119': {'name': '수성접착제 목공용', 'price': 5500, 'category': '문구'},
        '8802946888313': {'name': '딱풀 35g', 'price': 800, 'category': '문구'},
        '4549526608759': {'name': '카시오 공학용 계산기 FX-570', 'price': 20000, 'category': '문구'},
        '8809129330089': {'name': '레지스탕스 아발론', 'price': 20000, 'category': '문구'},
    }

    if barcode in products:
        product = products[barcode]
        product['barcode'] = barcode
        return product
    else:
        return None

def update_cart(product_info, quantity=1):
    for item in shopping_cart:
        if item['barcode'] == product_info['barcode']:
            item['quantity'] += quantity
            return

    new_item = {
        'barcode': product_info['barcode'],
        'name': product_info['name'],
        'price': product_info['price'],
        'quantity': quantity
    }
    shopping_cart.append(new_item)

def calculate_total():
    return sum(item['price'] * item['quantity'] for item in shopping_cart)

@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=shopping_cart, total=calculate_total(), context='cart')

# Update the delete_item route as follows:
@app.route('/delete_item', methods=['POST'])
def delete_item():
    barcode = request.form['barcode']
    global shopping_cart
    for item in shopping_cart:
        if item['barcode'] == barcode:
            shopping_cart.remove(item)
            break
    return jsonify({'success': True, 'total': calculate_total()})



@app.route('/add_item', methods=['POST'])
def add_item():
    barcode = request.form['barcode']
    context = request.form.get('context', 'cart')
    product_info = lookup_product_by_barcode(barcode)
    if product_info:
        update_cart(product_info)
        return jsonify({'success': True, 'total': calculate_total()})
    else:
        return jsonify({'success': False})


@app.route('/decrease_item', methods=['POST'])
def decrease_item():
    barcode = request.form['barcode']
    global shopping_cart
    for item in shopping_cart:
        if item['barcode'] == barcode:
            if item['quantity'] > 1:
                item['quantity'] -= 1
            else:
                shopping_cart.remove(item)
    return jsonify({'success': True, 'total': calculate_total()})

def set_zoom_level(browser, zoom_level):
    browser.execute_script(f"document.body.style.zoom='{zoom_level}%'")
    
@app.route('/get_lowest_price', methods=['POST'])
def lowest_price():
    product_name = request.form['product_name']
    result = get_lowest_price(product_name)
    return jsonify(result)

def get_lowest_price(product_name):
    chrome_options = Options()
    # chrome_options.add_argument('headless')
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get("https://naver.com")
    browser.find_element(By.CSS_SELECTOR, ".service_icon.type_shopping").click()
    time.sleep(2)
    new_window = browser.window_handles[1]
    browser.switch_to.window(new_window)
    browser.maximize_window()
    
    #광고제거
    try:
        popup_button = browser.find_element(By.CSS_SELECTOR, "button._buttonArea_button_1jZae")
        popup_button.click()
    except:
        pass
    #검색_lnbSearch_search_input_YVyzR N=a:sech.input
    search = browser.find_element(By.CSS_SELECTOR, "input._searchInput_search_text_3CUDs")
    search.send_keys(product_name)
    search.send_keys(Keys.ENTER)
    browser.refresh()
    # #낮은 가격순 클릭
    # low_price_sort_button = WebDriverWait(browser, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '낮은 가격순')]"))
    # )
    # low_price_sort_button.click()
    # time.sleep(2)
    
    #상품 명, 가격, 링크 크롤링
    item = browser.find_element(By.CSS_SELECTOR, ".product_item__MDtDF")
    name = item.find_element(By.CSS_SELECTOR, ".product_title__Mmw2K").text
    price = item.find_element(By.CSS_SELECTOR, ".price_num__S2p_v").text
    link = item.find_element(By.CSS_SELECTOR, ".price_delivery__yw_We").text
    
    browser.quit()
    
    return {'name': name, 'price': price, 'link': link}

   
@app.route('/get_coupang_lowest_price', methods=['POST'])
def coupang_lowest_price():
    product_name = request.form['product_name']
    result = get_coupang_lowest_price(product_name)
    return jsonify(result)

def get_coupang_lowest_price(product_name):
    subprocess.Popen(r'C:/Program Files/Google/Chrome/Application/chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chromeCookie"')
    chrome_options = Options()
    # chrome_options.add_argument('headless')
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #chrome_options.add_experimental_option("detach", True)
    #chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get("https://www.coupang.com")

    time.sleep(2)
    browser.maximize_window()

    search_box = browser.find_element(By.ID, "headerSearchKeyword")
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)

    # Wait for the search results to load
    time.sleep(2)



    # Parse the search results
    try:
        product_list = browser.find_element(By.ID, "productList")
        first_product = product_list.find_element(By.TAG_NAME, "li")
        
        # Extract the required details from the first product
        name = first_product.find_element(By.CLASS_NAME, "name").text
        price = first_product.find_element(By.CLASS_NAME, "price-value").text
        #discount = first_product.find_element(By.CLASS_NAME, "instant-discount-rate").text if first_product.find_elements(By.CLASS_NAME, "instant-discount-rate") else "No discount"
        #original_price = first_product.find_element(By.CLASS_NAME, "base-price").text if first_product.find_elements(By.CLASS_NAME, "base-price") else "No original price"
        #rating = first_product.find_element(By.CLASS_NAME, "rating").get_attribute("style").split(':')[-1].replace('%','')
        #review_count = first_product.find_element(By.CLASS_NAME, "rating-total-count").text
        arrival_info = first_product.find_element(By.CLASS_NAME, "arrival-info").text if first_product.find_elements(By.CLASS_NAME, "arrival-info") else "No arrival info"
        unit_price = first_product.find_element(By.CLASS_NAME, "unit-price").text if first_product.find_elements(By.CLASS_NAME, "unit-price") else "No unit price"
        #reward_cash = first_product.find_element(By.CLASS_NAME, "reward-cash-txt").text if first_product.find_elements(By.CLASS_NAME, "reward-cash-txt") else "No reward cash"

        print(f"Name: {name}")
        print(f"Price: {price}")
        #print(f"Discount: {discount}")
    # print(f"Original Price: {original_price}")
        #print(f"Rating: {float(rating)/20}")
        #print(f"Review Count: {review_count}")
        print(f"Arrival Info: {arrival_info}")
        print(f"Unit Price: {unit_price}")
        #print(f"Reward Cash: {reward_cash}")
    except Exception as e:
        print(f"Error occurred: {e}")
        
    finally:
        
        time.sleep(5)


        # Close the browser
        browser.quit()
    
    return {'name': name, 'price': price, 'arrival' : arrival_info}


@app.route('/checkout')
def checkout():
    total_amount = calculate_total()
    return render_template('checkout.html', cart=shopping_cart, total=total_amount)

@app.route('/start-payment')
def start_payment():
    total_amount = calculate_total()

    url = 'https://kapi.kakao.com/v1/payment/ready'
    headers = {
        'Authorization': 'KakaoAK ddf5ca89a14be407ce08f9ec086035c2',
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
    }
    data = {
        'cid': 'TC0ONETIME',
        'partner_order_id': '1001',
        'partner_user_id': 'user1001',
        'item_name': 'TUK마트',
        'quantity': 1,
        'total_amount': total_amount,
        'tax_free_amount': 0,
        'approval_url': url_for('approve_payment', _external=True),
        'cancel_url': url_for('cancel_payment', _external=True),
        'fail_url': url_for('fail_payment', _external=True)
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if response.status_code != 200:
        return jsonify(response_data), 400

    return redirect(response_data.get('next_redirect_pc_url'))

@app.route('/approve')
def approve_payment():
    return "결제 승인되었습니다."

@app.route('/cancel')
def cancel_payment():
    return "결제가 취소되었습니다."

@app.route('/fail')
def fail_payment():
    return "결제가 실패했습니다."

#상품 위치
products = {
    "1층": {
        "전자제품": ["티비", "노트북", "카메라","휴대폰", "컴퓨터", "모니터", "태블릿", "프린트기", "오디오", "안마의자", "마사지기", "에어컨", "선풍기", "공기청정기", "드라이기"],
        "식료품": ["과일", "채소", "쌀", "잡곡", "견과류", "소고기", "돼지고기", "오리고기", "닭고기", "계란", "생선", "건해산물", "냉동식품", "냉장식품", "즉석밥", "유제품", "베이커리", "김치", "반찬", "밀키트", "소스", "조미료", "과자", "시리얼", "커피", "생수", "음료", "주류", "유아식", "건강식품"]
    },
    "2층": {
        "의류": ["잠옷", "언더웨어", "양말", "운동화", "슬리퍼", "아동옷", "남성옷", "여성옷", "남녀공용옷"],
        "화장품": ["립스틱", "파운데이션", "향수","선크림", "클렌징", "립케어", "마스크팩", "베이스", "립 메이크업", "네일아트", "헤어케어"]
    },
    "3층": {
        "서적": ["소설", "만화책", "잡지","참고서", "베스트셀러", "동화책", "종교서적", "자격증", "에세이"],
        "문구류": ["공책", "펜", "마커","샤프", "학용품", "스케치북", "물감", "미술용품", "용지", "메모장", "음악용품", "칼", "가위", "스테이플러", "봉투", "풀", "파일", "테이프", "색종이", "크레파스"]
    },
    "4층": {
        "가정 전자가전": ["냉장고", "세탁기", "전자레인지","청소기", "다리미", "건조기", "전기밥솥", "온수매트", "전기장판", "에어프라이기", "믹서기", "토스트기", "인덕션"]
    },
    "5층": {
        "가구": ["소파", "탁자", "의자","침대", "수납장", "조명", "행거", "휴지통", "옷걸이", "인테리어 소품(향초, 식물)", "거울", "액자", "매트", "매트리스", "건전지", "커튼", "베개", "이불", "인형", "스탠드", "멀티탭", "스위치", "페인트", "공구"]
    }
}

@app.route('/map', methods=['GET', 'POST'])
def map():
    search_result = None
    if request.method == 'POST':
        search_query = request.form.get('search_query').lower()
        search_result = []
        for floor, categories in products.items():
            for category, items in categories.items():
                if search_query in category.lower():
                    search_result.append((floor, category, None))
                for item in items:
                    if search_query in item.lower():
                        search_result.append((floor, category, item))
    return render_template('map.html', products=products, search_result=search_result)

#반응 없을 시 배너 띄워줌
@app.route('/banner')
def banner():
    return render_template('banner.html')

if __name__ == '__main__':
    app.run(debug=True)

from rekono.settings import DEFECT_DOJO as config

headers = {
    'Authorization': f'Token {config.get("API_KEY")}'
}

base = f'{config.get("HOST")}/api/v2'
urls = {
    'prod_types': f'{base}/product_types/',
    'products': f'{base}/products/',
    'engagements': f'{base}/engagements/',
    'import': f'{base}/import-scan/',
}

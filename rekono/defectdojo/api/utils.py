from rekono.settings import DEFECT_DOJO as config

headers = {
    'Authorization': f'Token {config.get("API_KEY")}'
}

base = f'{config.get("HOST")}/api/v2'
urls = {
    'prod_types': f'{base}/product_types/',
    'products': f'{base}/products/',
    'engagements': f'{base}/engagements/',
    'test_types': f'{base}/test_types/',
    'tests': f'{base}/tests/',
    'findings': f'{base}/findings/',
    'endpoints': f'{base}/endpoints/',
    'import': f'{base}/import-scan/',
}

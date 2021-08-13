import asyncio
from src.adapter import adapter, configuration, io_loop
from src import crawler_app
from src.models.product import Product
from src.crawler.discover import DiscoverProduct, Categ

discover = DiscoverProduct()

def save(product: Product):
    print('product {} updated'.format(product.name))

async def run():
    limitpage = 50
        
    for _ in range(0, limitpage):
        for categ in discover.categories:
            categ: Categ = categ
            hasil = await crawler_app.get_products_categ.execute(categ)
            for product in hasil:
                save(product)

            categ.last_page += 1
        discover.save_obj()

io_loop.run_until_complete(run())
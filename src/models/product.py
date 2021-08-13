class Product:
    
    itemid: int
    name: str
    price: int
    shopid: int
    url: str
    weight: int
    last_updated: float
    pictures: list

    cat_id_1: int
    cat_id_2: int
    cat_id_3: int
    stock: int
    view: int
    diskusi: int
    review: int
    rating: float
    rating_count: int
    sold: int
    tx: int
    description: str

    def __init__(self,
        itemid: int,
        name: str,
        price: int,
        shopid: int,
        url: str,
        weight: int,
        last_updated: float,
        pictures: list,
        cat_id_1: int,
        cat_id_2: int,
        cat_id_3: int,
        stock: int,
        view: int,
        diskusi: int,
        review: int,
        rating: float,
        rating_count: int,
        sold: int,
        tx: int,
        description: str
    ):

        self.itemid = itemid
        self.name = name
        self.price = price
        self.shopid = shopid
        self.url = url
        self.weight = weight
        self.last_updated = last_updated
        self.pictures = pictures
        self.cat_id_1 = cat_id_1
        self.cat_id_2 = cat_id_2
        self.cat_id_3 = cat_id_3
        self.stock = stock
        self.view = view
        self.diskusi = diskusi
        self.review = review
        self.rating = rating
        self.rating_count = rating_count
        self.sold = sold
        self.tx = tx
        self.description = description
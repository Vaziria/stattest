class Toko:
    shopid: int
    username: str
    url: str
    city_name: str
    district_name: str
    jum_product: int
    sold: int
    tx: int
    percent_tx: float
    location: str
    rating: float
    review: int
    score_map: int
    score: int

    kep_bad: int
    kep_good: int
    kep_neutral: int
    last_updated: float
    

    def __init__(self,
        shopid: int,
        username: str,
        url: str,
        city_name: str,
        district_name: str,
        jum_product: int,
        sold: int,
        tx: int,
        percent_tx: float,
        location: str,
        rating: float,
        review: int,
        score_map: int,
        score: int,

        kep_bad: int,
        kep_good: int,
        kep_neutral: int,
        last_updated: float
    ):
        self.shopid = shopid
        self.username = username
        self.url = url
        self.city_name = city_name
        self.district_name = district_name
        self.jum_product = jum_product
        self.sold = sold 
        self.tx = tx
        self.percent_tx = percent_tx
        self.location = location
        self.rating = rating
        self.review = review
        self.score_map = score_map
        self.score = score
        self.kep_bad = kep_bad 
        self.kep_good = kep_good
        self.kep_neutral = kep_neutral
        self.last_updated = last_updated

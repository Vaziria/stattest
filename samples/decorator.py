


# inisiasi Task adapter untuk koneksi ke rabbit mq
RABBIT_URI = "amqp://localhost:5672/"
adapter = TaskAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)


# adapter mendekorasi fungsi crawl_homepage
@adapter.register("fib_server_q", publish_exchange="test_rpc")
def crawl_homepage():
    req = requests.get('https://tokopedia.com')
    return req

# fungsi dieksekusi biasa
crawl_homepage()

# akan dieksekusi di worker node
crawl_homepage.execute()


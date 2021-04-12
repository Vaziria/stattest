from r_server import req_ip, req_shopee

print(req_ip())
print('from worker')

for c in range(10):
    # data = req_ip.execute()
    data = req_ip.execute()
    print(data)
    print('covid')
    data = req_shopee.execute()
    print(data)
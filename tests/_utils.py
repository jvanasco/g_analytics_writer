from json import dumps as json_dumps

# we need to pass this in...
# production doesn't care about sorted keys
# py2 and p3 generate different sorts though
def custom_json_dumps_sorted(data):
    # simply the dumping
    return json_dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False)

from mprpc import RPCClient

client = RPCClient('127.0.0.1', 6100)
print(client.call('query', "a"))
# import socket
# # first = 'abcertcba'
# # second = 'cab'
# # start = 0
# # def f(a,b):
# #     if (len(a) == len(b)) and set(a) == set(b):
# #         return True
# #     else:
# #         return False
# # print(f(first,second))
# #
# #
# # def q(a,b):
# #     if set(b) == set(first(start, (len(second) - 1))):
# #         return True
# #     else:
# #         return False
# # print(q(first,second))
#
#
# def do_something(p):
#     l= len(p)
#     for i in range(1, l):
#         k = p[i]
#         j = i-1
#         while j >= 0 and k < p[j] :
#             p[j + 1] = p[j]
#             j -= 1
#         p[j + 1] = k
#
# print(sorted([5,4,6,2,1,2,3]))
#
#
# # def start_server():
# #     try:
# #         server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #         server.bind(('127.0.0.1', 5000))
# #         server.listen(4)
# #         while True:
# #             print('Working')
# #             client_socket, address = server.accept()
# #             data = client_socket.recv(1024).decode('utf-8')
# #             #print(data)
# #             content = load_page_from_get_request(data)
# #             client_socket.send(content)
# #             client_socket.shutdown(socket.SHUT_WR)
# #     except KeyboardInterrupt:
# #         server.close()
# #         print('Shutdown this server')
# #
# # def load_page_from_get_request(request_data):
# #     HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html: charset=utf-8\r\n\r\n'
# #     path = request_data.split(' ')[1]
# #     response = ''
# #     with open('2024-01-17_16-58-03.csv', 'rb') as file:
# #         response = file.read()
# #     return HDRS.encode('utf-8') + response
# #
# # if __name__ == '__main__':
# #     start_server()








a = 6
tuple = (1,2)

def simple(a):
    for i in range(2, a):
        #if a%i > 0:
            #continue
            #return True
        if a%i == 0:
            return False
    return True
        #else:
            #simple(a)
    #else:
        #print('Not Simple')
        #continue
        #return False

#for i in range(2, a):
simple(a)


















"""This code uses a socket to access the server of DNS """
# !/usr/bin/env python

import socket
import sys


def response_recv(sock):
    """this function loops through packet of 4096 from the server"""
    response = []
    while True:
        data = sock.recv(4096)
        if not data:
            break

        response.append(data)
    return b''.join(response)


def dechunk(sock):
    """opened the socket again.hex value of next chunk size will be used"""
    chunk = 1024
    response = []
    flag = 0
    while True:

        data = sock.recv(chunk)
        if(data.find(b'\r\n\r\n') != -1 and flag == 1):
            origchunk = chunk
            bigchunk = data[data.find(b'\r\n\r\n')+4:data.find(b'\r\n\r\n')+7]
            chunkerstring = str(bigchunk)
            chunksplit = chunkerstring.split('\'')
            chunko = chunksplit[1]
            chunkint = int(chunko, 16)
            chunkint = origchunk - (chunkint - data.find(b'\r\n\r\n') + 4)
            flag = 1

        elif data.find(b'\r\r\n') != -1:

            spec = data.find(b'\r\r\n')
            data = data[:spec+1]
        elif data.find(b'\r\n') != -1:

            end = data.find(b'\r\n')
            chunkerbyte = data[:end]
            chunkerstring = str(chunkerbyte)
            chunker = chunkerstring.split('\'')
            chunko = chunker[1]

            if data[len(data)-1:len(data)] != b'\r':

                data = data.strip()
            if chunko.find('\\') == -1 and chunko.find('/') == -1:
                chunk = int(chunko, 16)
                data = data[end+2:]
        elif not data:
            break

        response.append(data)
    return b''.join(response)


def retrieve_url2(url):
    """Forms the GET request and connects to the socket"""
    crlf = "\r\n"
    close = "Connection: close"
    url_http = url.strip("http://")
    new_url = url_http.split("/", 1)

    if len(new_url) > 1:

        path_url = new_url[1]
        host = "Host: "+new_url[0]
        final_url = "GET "+"/"+path_url+" "+"HTTP/1.1"
        final_url = final_url + crlf+host+crlf+close+crlf
        final_url = final_url + "Accept: */*" + crlf + crlf
    else:
        host = "Host: " + new_url[0]
        final_url = "GET / HTTP/1.1"+crlf+host+crlf
        final_url = final_url + close+crlf + "Accept: */*" + crlf + crlf
    return final_url


def retrieve_url3(url):
    """extension of retrieve url"""
    url_http = url.strip("http://")
    new_url = url_http.split("/", 1)
    host_url = new_url[0]
    if host_url.find(':') != -1:
        server = host_url[:(host_url.find(':'))]
        port = int(host_url[(host_url.find(':')+1):])
    else:
        server = host_url
        port = 80
    server_port = list()
    server_port.append(server)
    server_port.append(port)
    return server_port


def retrieve_url(url):
    """had too many local variables. this is just extension"""
    final_url = retrieve_url2(url)
    server_port = retrieve_url3(url)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((server_port[0], server_port[1]))
    except socket.error:
        return None

    soc.sendall(str.encode(final_url))
    response = response_recv(soc)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_port[0], server_port[1]))
    except socket.error:
        return None
    sock.sendall(str.encode(final_url))
    full_response = dechunk(sock)
    chunk_index = full_response.find(b'\r\n\r\n')+4
    if response.find(b'404 Not Found') != -1:
        return None
    index = response.find(b'\r\n\r\n')+4
    if response.find(b'Content-Type: image/gif') != -1:
        return response[index:]

    tmp = response[index:]
    full_response = full_response[chunk_index:]
    if response.find(b'Transfer-Encoding: chunked') != -1:
        if tmp.find(b'\n\r\n0\r\n\r\n') != -1:
            header = response[index:].decode()
            header = tmp.split(b'\r\n', 1)
            header = header[1].split(b'\n\r\n0\r\n\r\n', 1)
            header = header[0].decode('utf-8')+"\n"
        else:
            indy = full_response.find(b'\r\n')+2
            full_response = full_response[indy:]
            return full_response.strip()
    else:
        header = response[index:].decode()
    return header.encode()


if __name__ == "__main__":
    sys.stdout.buffer.write(retrieve_url(sys.argv[1]))

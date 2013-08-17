""" networking process """
import socket
import select
from util import named_runner 
def _run(hostport, (read_queue, write_queue), delimiter="\r\n"):
    """
    the networking process's entry point
    hostport - tuple with the host (string) and port (int) - ex: ("localhost", 1234)
    read_queue - multiprocessing.queue used to send strings to the socket
    write_queue - multiprocessing.queue that is given lines read from the socket
    delimiter - splitter for reading/writing lines
        Note: this could probably be abstracted to general tokenization
            hasNext(string) -> (bool) -  returns true if the string has a token in it
                e.g. lambda x: "\r\n" in x
            getNext(string) -> (string, string) - returns the next token, and the remaining buffer
                e.g. lambda x: x.split("\r\n",1)
            toNetwork(string) -> (string) - returns the argument prepped for network sending
                e.g. lambda x: x + "\r\n"
            but, since this if for an IRC bot, delimiter defaults to "\r\n" and the above examples
            are what's hardcoded

    If the write_queue (read_queue from the other end) is full, this will block further network consumption
    """
    #pylint: disable=W0212 
    #reason: using _reader and _writer for select.select

    assert len(delimiter) != 0, "Can not have an empty delimiter"

    sock = _create_socket()
    sock.connect(hostport)
    
    network_buffer = ""
    try:
        while True:
            readable, _, exceptioned = select.select(
                [sock, read_queue._reader], 
                [], #    [sock, write_queue._writer], 
                [sock], 1)
            _, writable, _ = select.select(
                [],
                [sock, write_queue._writer],
                [])
            #print readable, writable, exceptioned
            if sock in readable:
                data = sock.recv(1024)
                network_buffer += data

            if read_queue._reader in readable and sock in writable:
                item = read_queue.get()
                if item is None:
                    break
                sock.send(item + delimiter)

            while write_queue._writer in writable and delimiter in network_buffer:
                msg, network_buffer = network_buffer.split(delimiter, 1)
                write_queue.put(msg)

            if exceptioned:
                read_queue.close()
                write_queue.put(None)
                return
    except:
        import traceback
        traceback.print_exc()
    finally:
        #Signal end of network, and then close everything
        write_queue.put(None)
        #Close what we can 
        sock.close()
        read_queue.close()
        write_queue.close()

def _create_socket():
    """
    create a socket to work on. possibly implement ssl stuff here
    """
    sock = socket.socket()
    return sock

def simple_connect(hostport, delimiter = "\r\n"):
    """ 
    creates a new connection in another process

    takes a hostport tuple eg: ("localhost", 1234)
    and an optional delimiter, the delimiter is used to split "lines"
    it is also appended to each item before being sent on the socket
    see _run's documentation for more information

    returns a pair of queues 
    (write_queue, read_queue)

    The end of queue sentnal value is None
    putting None in the write_queue will close the socket and end the process

    getting None from the read_queue means that the socket has closed and no
    more data is on the way.
    """
    #pylint: disable=W0404
    #reason: bug in pylint http://www.logilab.org/ticket/60828
    import multiprocessing
    queues = multiprocessing.Queue(100), multiprocessing.Queue(100)
    
    net_proc = multiprocessing.Process(
        target=named_runner(_run), 
        name="Net", 
        args=(hostport, queues, delimiter))
    net_proc.start()
    return queues 
    
def _exampleIrc():
    """ example usage of this module """

    write_queue, read_queue = simple_connect(("localhost", 6667))
    
    #run(...) will make sure we're connected before dequeuing items
    #Connect to the irc server on localhost
    write_queue.put("NICK Dot")
    write_queue.put("USER Dot localhost localhost :Dot the bot")
    while True:
        data = read_queue.get()
        if data is None: #End of network condition
            return 
        if data.startswith("PING"):
            write_queue.put("PONG" + data[4:])
            write_queue.put("JOIN #test")
        if data.endswith("quit"):
            data = None # make the bot send None to kill the connection
        write_queue.put(data)

def _exampleHttp():
    write_queue, read_queue = simple_connect(("localhost", 80), "\n")
    write_queue.put("GET /bot/network.py HTTP/1.1\r")
    write_queue.put("Host: theepicsnail.net\r")
    write_queue.put("\r")
    
    #Pull the content length from the header
    contentLength = None
    data = read_queue.get()
    while data != "\r":
        if data.startswith("Content-Length:"):
            contentLength = int(data.split(" ")[1])
        data = read_queue.get()

    assert contentLength != None, "Failed to get Content-Length from header."
    
    #Download the data, note this only works for files ending with \n
    data = ""
    while contentLength != 0:
        tmp = read_queue.get()+"\n"
        contentLength -= len(tmp)
        data += tmp

    print data
    write_queue.put(None)
#    while True:
#        print read_queue.get()
if __name__ == "__main__":
    _exampleHttp()
    _exampleIrc()


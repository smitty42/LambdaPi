import os
import time
import json
import base64

import cloud

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

port = 8888
os.system('''kill -9 `netstat -nap tcp |
            grep %s |
            awk '{{split ($7, a, "/"); print a[1]}}'`'''%port)
define("port", default=port, help="run on the given port", type=int)

class PycloudMiddleman(tornado.web.RequestHandler):
    def get(s):
        sub = s.get_argument('substring')
        sub = base64.b64decode(str(sub))
        sub = json.loads(sub)
        sub = str(int(sub['substring']))

        number_of_nodes = 10
        charicters_processed = 10000000 * number_of_nodes
        nodes = map(lambda x: "%03d" % x,list(xrange(number_of_nodes)))
        args = map(lambda x: [sub,x],nodes)

        start = time.time()
        jids = cloud.map(pi_string_search,args)        
        from_cloud = cloud.result(jids)
        end = time.time()

        total_computation_time = sum(map(lambda x: x[0],from_cloud))
        graph_data = map(lambda x: [int(x[2]),x[1]],from_cloud)
        first_occurance = filter(lambda x: x != -1,map(lambda x: x[3],from_cloud))[0]
        average_node_time = total_computation_time / number_of_nodes
        total_instances = sum(map(lambda x: x[1],from_cloud))
        frequency = total_instances / float(charicters_processed)
        period = 1 / frequency
        average_instances = total_instances / float(number_of_nodes)
        average_time_per_node = total_computation_time / float(number_of_nodes)
        total_time_for_entire_process = end - start
        

        data_dict = {}
        data_dict['graph_data'] = graph_data
        data_dict['total_computation_time'] = total_computation_time
        data_dict['charicters_processed'] = charicters_processed
        data_dict['first_occurance'] = first_occurance
        data_dict['average_node_time'] = average_node_time
        data_dict['total_instances'] = total_instances
        data_dict['frequency'] = frequency
        data_dict['period'] = period
        data_dict['average_instances'] = average_instances
        data_dict['average_time_per_node'] = average_time_per_node
        data_dict['total_time_for_entire_process'] = total_time_for_entire_process
        
        return s.write(base64.b64encode(json.dumps(data_dict)))

def pi_string_search(data):
    sub = data[0]
    node = data[1]
    picloud_file = cloud.bucket.getf('pi_parts%s'% (node), prefix='classB')
    pi = picloud_file.read()

    start = time.time()
    instances = pi.count(sub)
    first_occurance = pi.find(sub)
    end = time.time()
    delta = end - start
    return [delta, instances, node, first_occurance]

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/search", PycloudMiddleman),
        ],
    )
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

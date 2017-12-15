from concurrent import futures
import threading
import time

import grpc
from pyspark.sql import SparkSession

import sparkpi_pb2
import sparkpi_pb2_grpc


def produce_pi(scale):
    spark = SparkSession.builder.appName("PythonPi").getOrCreate()
    n = 100000 * scale

    def f(_):
        from random import random
        x = random()
        y = random()
        return 1 if x ** 2 + y ** 2 <= 1 else 0

    count = spark.sparkContext.parallelize(
        range(1, n + 1), scale).map(f).reduce(lambda x, y: x + y)
    spark.stop()
    pi = 4.0 * count / n
    return pi


class SparkPiServicer(sparkpi_pb2_grpc.SparkPiServicer):
    def __init__(self, *args, **kwargs):
        super(SparkPiServicer, self).__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def GetPi(self, request, context):
        self.lock.acquire()
        print('=========================== Begin Pi Estimation '
              '===========================')
        print('Scale requested = {}'.format(request.size))
        pi = produce_pi(request.size)
        self.lock.release()
        return sparkpi_pb2.Pi(value=pi)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sparkpi_pb2_grpc.add_SparkPiServicer_to_server(
        SparkPiServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print('sparkpi-python-grpc server starting on 0.0.0.0:50051')
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()

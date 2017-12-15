# SparkPi GRPC Server

## How to generate the GRPC files

```
python -m grpc_tools.protoc -Iprotos --python_out=. --grpc_python_out=. protos/sparkpi.proto
```

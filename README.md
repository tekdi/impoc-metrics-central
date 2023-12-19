impoc-metrics-central

pip install grpcio==1.59.3
pip install grpcio-tools==1.59.3
python -m grpc_tools.protoc -I proto --python_out=. --pyi_out=. --grpc_python_out=.  proto/
metricCentral.proto
Executing the above command generates the metricCentral_pb2.py and metricCentral_pb2_grpc.py
These two files are generated from the .proto file for enabling gRPC
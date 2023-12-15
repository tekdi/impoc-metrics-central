import grpc
import os
from concurrent import futures
import metricCentral_pb2 as pb2
import metricCentral_pb2_grpc as pb2_grpc
from datetime import datetime

UPLOADS_FILE = 'uploaded_files_on_central.txt'
FILES_TO_UPLOAD_DIR = 'UploadedFilesOnCentralServer'
CHUNK_SIZE = 1024 * 1024  # 1MB

class FileService(pb2_grpc.FileServiceServicer):

    #get all chunk and save as file
    def save_chunks_to_file(self, chunks, filename):
        with open(filename, 'wb') as f:
            for chunk in chunks:
                f.write(chunk.buffer)
    
    #upload file on server in chunk
    def UploadFileMetric(self, request_iterator, context):
        first_chunk = next(request_iterator)
        filename = first_chunk.buffer.decode('utf-8')
        file_path = os.path.join(FILES_TO_UPLOAD_DIR, filename)
        print(file_path)

        self.save_chunks_to_file(request_iterator, file_path)

        response = pb2.ReplyMetric()
        response.message = f"{os.path.getsize(file_path)}"
        # Record upload in a file
        with open(UPLOADS_FILE, 'a') as file:
             file.write(f"{context.peer()} {datetime.now()} {os.path.getsize(file_path)} {filename}\n")

        return response

    # connect to server
    def sayHelloMetric(self, request, context):
        print("Companion APP connected to Metric Central Server")
        response = pb2.HelloReplyMetric();
        response.message = f"Hello {request.name}"
        return response
def serve():
    print("Server Running")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

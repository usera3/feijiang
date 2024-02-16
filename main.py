from flask import Flask, request, jsonify
import io
import os
import threading
import random
import string
import time

from webdav4.client import Client

app = Flask(__name__)

# 坚果云配置
webdav_url = 'https://dav.jianguoyun.com/dav/'
webdav_auth = ('1446437177@qq.com', 'arn2gaizaditvvt4')
remote_path = '/飞浆中转'  # 坚果云中的远程路径
remote_path2 = '/img_url'  # 坚果云中的远程路径

# 本地路径配置
local_path = 'E:/坚果云'  # 本地路径
local_path_url = 'E:/坚果云/img_url'  # 本地路径
# 实例化 Client 对象
client = Client(base_url=webdav_url, auth=webdav_auth)

def generate_random_filename(length):
    # 生成随机字符串作为文件名
    letters = string.ascii_lowercase + string.ascii_uppercase
    filename = ''.join(random.choice(letters) for _ in range(length))
    return filename

def check_filename_exists(filename):
    # 检查文件名是否已存在
    if os.path.exists(filename):
        return True
    else:
        return False

def generate_unique_filename(length):
    while True:
        filename = generate_random_filename(length)
        if not check_filename_exists(filename):
            return filename

@app.route("/upload_description", methods=["POST"])
def upload_description_api():
    # while True:
        # 获取用户输入的描述词
        description = request.form.get("description")#py用这个
        # description = request.get_json().get("description")#js用这个
        print(description)
        if description:
            # 将描述词存储为本地txt文件
            local_txt_path = os.path.join(local_path, "描述词.txt")
            with open(local_txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(description)
            with open(local_txt_path, 'rb') as file:
                file_io = io.BytesIO(file.read())

            try:

                # 上传描述词到坚果云
                upload_filename = generate_unique_filename(12) + ".txt"
                client.upload_file(from_path="E:\坚果云\描述词.txt", to_path=remote_path + '/' + upload_filename, overwrite=False)
                print("描述词已上传到坚果云")
                response = {
                    "upload_filename": upload_filename,
                    "message": "描述词已上传到坚果云"
                }
                return jsonify(response)
            except Exception as err:
                response = {
                    "error": "描述词上传失败：" + str(err)
                }
        else:
            response = {
                "message": "描述词为空"
            }

        return jsonify(response)

# ...剩余的代码...


# def download_files():
#     while True:
#         files = client.ls(remote_path, detail=False)
#         # 检查文件列表是否为空
#         if len(files) == 0:
#
#             print("文件列表为空，继续等待...")
#             time.sleep(10)
#             continue
#
#         for file_info in files:
#             file_name = os.path.basename(file_info)
#
#             local_path2 = os.path.join(local_path, file_name)
#
#             try:
#                 if ".png" in file_info:
#                     # 构建文件的完整路径
#                     file_path = file_info
#                     # print(file_path)
#                     # print(remote_path)
#                     # print( file_info)
#                     # 下载文件
#                     client.download_file(from_path=file_path, to_path=local_path2)
#
#                     # 删除文件
#                     client.remove(path=file_path)
#                     print(f"文件 {file_path} 删除成功")
#             except Exception as err:
#                 if "not found" in str(err) or "404 Not Found" in str(err):
#                     print(f"文件 {file_path} 已被删除或不存在")
#                 else:
#                     raise err


def download_files():
    while True:
        files = client.ls(remote_path2, detail=False)
        # 检查文件列表是否为空
        if len(files) == 0:
            print("暂未发现图片链接")
            time.sleep(10)
            continue

        for file_info in files:
            file_name = os.path.basename(file_info)

            local_path2 = os.path.join(local_path_url, file_name)

            try:
                if ".txt" in file_info:
                    # 构建文件的完整路径
                    file_path = file_info
                    # print(file_path)
                    # print(remote_path)
                    # print( file_info)
                    # 下载文件
                    client.download_file(from_path=file_path, to_path=local_path2)

                    # 下载成功，保存文件到本地
                    with open(local_path2, 'r') as file:
                        # txt_file_path = os.path.join(folder_path, file)
                        content = file.read()
                        print(content)

                    # 删除文件
                    client.remove(path=file_path)
                    print(f"文件 {file_path} 删除成功")
            except Exception as err:
                if "not found" in str(err) or "404 Not Found" in str(err):
                    print(f"文件 {file_path} 已被删除或不存在")
                else:
                    raise err

        # 完成当前循环后，等待一段时间再继续下一次循环
        time.sleep(10)



if __name__ == "__main__":
    # 创建一个新的线程来处理上传描述词的操作
    download_thread = threading.Thread(target=download_files)
    download_thread.start()
    app.run(host='0.0.0.0', port=8000, debug=False)

import argparse
import json
from threading import Thread
import websocket


class Client:
    def __init__(self, data, uri):
        self.data = data
        self.uri = uri

    # 建立连接
    def connect(self):
        ws_app = websocket.WebSocketApp(
            uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws_app.run_forever()

    # 建立连接后发送消息
    def on_open(self, ws):
        def run(*args):
            nbest_ = 1  # 返回多少个候选结果
            continuous_decoding_ = False
            start_paras = {
                "signal": "start",
                "nbest": nbest_,
                "continuous_decoding": continuous_decoding_,
            }
            ws.send(json.dumps(start_paras))

            for i in range(len(self.data)):
                ws.send(self.data[i], websocket.ABNF.OPCODE_BINARY)
                # time.sleep(0.5)

            end_paras = {"signal": "end"}
            ws.send(json.dumps(end_paras))

        Thread(target=run).start()

    # 接收消息
    def on_message(self, ws, message):
        data = json.loads(message)
        print(data)
        if data['type'] == 'final_result':
            nbest = json.loads(data['nbest'])
            print(nbest[0])

    # 打印错误
    def on_error(self, ws, error):
        print("error: ", str(error))

    # 关闭连接
    def on_close(self, ws, t_, p_):
        print("client closed.")


# 准备数据
def prepare_audio_data(args):
    # 读取音频文件
    with open(args.file_path, 'rb') as f:
        file = f.read()

    # Send data every 0.5 second
    interval = 0.5
    sample_interval = int(interval * int(args.sample_rate))
    print(f"send sample_interval, size : {sample_interval}")

    # TODO this is not pcm file
    splited_data = [
        file[i : i + sample_interval] for i in range(0, len(file), sample_interval)
    ]

    return splited_data


# 获取命令行输入参数
def get_args():
    parser = argparse.ArgumentParser(description='ASR')
    parser.add_argument(
        '-f', '--file_path', type=str, required=True, help="path to wav file (sr: 16k)"
    )
    parser.add_argument('--audio_format', type=str, default='wav')
    parser.add_argument('--sample_rate', type=str, default='16000')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()
    data = prepare_audio_data(args)
    uri = "ws://127.0.0.1:10086"

    # 建立Websocket连接
    client = Client(data, uri)
    client.connect()

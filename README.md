# ros2-trace-analyzer

#### 서브모듈 초기화 및 업데이트

```bash
# 서브모듈 초기화
git submodule update --init --recursive

# 서브모듈 최신 커밋으로 업데이트
git submodule update --remote --merge
```
#### ros2_tracing dependency

To enable tracing:

1. Install [LTTng](https://lttng.org/docs/v2.13/) (`>=2.11.1`) with the Python bindings to control tracing and read traces:
    ```
    sudo apt-get update
    sudo apt-get install lttng-tools liblttng-ust-dev
    sudo apt-get install python3-babeltrace python3-lttng
    ```
    * The above commands will only install the LTTng userspace tracer, LTTng-UST. You only need the userspace tracer to trace ROS 2.
    * To install the [LTTng kernel tracer](https://lttng.org/docs/v2.13/#doc-tracing-the-linux-kernel):
        ```
        sudo apt-get install lttng-modules-dkms
        ```
    * For more information about LTTng, [see its documentation](https://lttng.org/docs/v2.13/).

#### trace 시작하는법
```bash
#Tracing 확인
ros2 run tracetools status

# enabled 되어있어야함 
Tracing enabled 

# 명령 입력후 enter 종료 하려면 enter 한번더
ros2 trace -s ros_trace -p ~/ -l 
``` 

![newplot](https://github.com/user-attachments/assets/46fb722d-ba68-482d-9c2c-abd216317085)

#!/usr/bin/env python3
"""
설명:
    본 스크립트는 Babeltrace를 호출하여 지정된 trace 디렉토리의 데이터를 텍스트 로그(trace.txt)로 추출하고,
    추출된 텍스트 로그를 파싱하여 CSV 파일로 변환합니다.
    
    1. Babeltrace 호출: subprocess 모듈을 이용하여 trace 디렉토리 내의 데이터를 텍스트로 추출합니다.
    2. 텍스트 파싱 및 CSV 변환: 정규표현식을 사용하여 각 로그 라인에서 Timestamp, Channel, CPU, Event type,
       Contents 값을 추출한 후 CSV 파일에 저장합니다.
       
주의:
    - Babeltrace 명령어가 시스템 PATH에 있어야 하며, 환경에 따라 babeltrace 대신 babeltrace2를 사용해야 할 수 있습니다.
    - 정규표현식은 Babeltrace의 출력 형식에 맞추어 작성되었으므로, 필요 시 실제 출력 형식에 맞게 수정하시기 바랍니다.
    - 파일 인코딩 문제나 기타 예외 상황을 대비하여 errors 옵션 등을 적절히 설정하였습니다.
"""

import os
import re
import csv
import subprocess

# 수정: trace 파일들이 있는 최상위 폴더 경로 (실제 환경에 맞게 수정)
TRACE_DIR = "/home/pjs/ros_trace/ust/uid/1000/64-bit"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 추출된 텍스트 로그 파일과 생성될 CSV 파일을 data 폴더에 저장
TRACE_TXT = os.path.join(DATA_DIR, "trace.txt")
OUTPUT_CSV = os.path.join(DATA_DIR, "output.csv")

def ExtractTraceToText(trace_directory, output_txt):
    """
    babeltrace 명령어를 호출하여 trace_directory 내의 trace 데이터를 텍스트 형식으로 추출합니다.
    추출된 결과는 output_txt 파일에 저장됩니다.
    
    인자:
      trace_directory (str): trace 데이터가 저장된 최상위 폴더 경로.
      output_txt (str): 추출된 텍스트 로그를 저장할 파일명.
      
    반환:
      True: 추출 성공, False: 추출 실패.
    """
    # Babeltrace 명령어 설정 (필요시 'babeltrace2'로 교체)
    command = ["babeltrace", trace_directory]
    
    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        # stdout 결과를 디코딩 (필요 시 errors 옵션으로 대체)
        output = result.stdout.decode('utf-8', errors='replace')
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"trace.txt 파일 생성 완료: {output_txt}")
    except Exception as e:
        print(f"trace.txt 파일 생성 실패: {e}")
        return False
    return True

def ConvertTraceTextToCsv(text_file, output_csv):
    """
    Babeltrace로 생성된 텍스트 로그 파일(text_file)을 읽어
    정규표현식을 사용해 각 로그 라인에서 Timestamp, Channel, Event type, CPU, Contents를 추출한 후,
    CSV 파일(output_csv)로 저장합니다.
    """
    # 아래 정규표현식은 제공된 로그 라인 형식에 맞추어 제작되었습니다.
    # 로그 예시:
    # [19:47:48.545758429] (+0.000090935) pjs ros2:rclcpp_publish: { cpu_id = 10 }, { ... }, { ... }
    #
    # 그룹별 설명:
    #   timestamp: 대괄호 안의 전체 문자열 (예 "19:47:48.545758429")
    #   channel: "ros2" 등 알파벳과 숫자(일반적으로 단어)
    #   event: 콜론(:) 전까지의 이벤트 명 (예, "rclcpp_publish")
    #   cpu: 첫 번째 중괄호 내 "cpu_id = ..."에서 숫자만 추출
    #   contents: 첫 번째 중괄호 이후 쉼표로 구분된 나머지 문자열 전체
    #
    # ※ 필요에 따라 정규표현식의 공백, 콜론, 쉼표 주변 패턴을 조정하시기 바랍니다.
    line_pattern = re.compile(
        r'^\[(?P<timestamp>[^\]]+)\]\s+'                # [Timestamp]
        r'\([^)]+\)\s+'                                # (상대시간 등, 생략)
        r'\S+\s+'                                      # "pjs" 등 무시할 문자열
        r'(?P<channel>\w+):(?P<event>[^:]+):\s+'         # Channel:Event:
        r'\{\s*cpu_id\s*=\s*(?P<cpu>\d+)\s*\}'           # 첫 번째 중괄호: { cpu_id = 10 }
        r'(?:,\s*(?P<contents>.+))?$'                   # 나머지 문자열(Contents)
    )
    
    rows = []
    with open(text_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = line_pattern.match(line)
            if match:
                timestamp = match.group('timestamp')
                channel = match.group('channel')
                event = match.group('event').strip()
                cpu = match.group('cpu')
                contents = match.group('contents')
                if contents is None:
                    contents = ""
                # 추출한 결과를 CSV 행으로 추가
                rows.append([timestamp, channel, cpu, event, contents])
            else:
                # 매칭되지 않는 라인은 디버깅을 위해 출력 (필요 시 주석 처리 가능)
                print("매칭 실패 라인:", line)
    
    if rows:
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, escapechar='\\', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Timestamp", "Channel", "CPU", "Event type", "Contents"])
                writer.writerows(rows)
            print(f"CSV 파일 생성 완료: {output_csv}")
        except Exception as e:
            print(f"CSV 파일 저장 실패: {output_csv} - 오류: {e}")
    else:
        print("파싱된 데이터가 없어 CSV 파일을 생성하지 않습니다.")


def main():
    # Babeltrace를 호출하여 trace.txt 파일을 추출합니다.
    if ExtractTraceToText(TRACE_DIR, TRACE_TXT):
        # 텍스트 로그 추출에 성공했을 경우, 이를 CSV로 변환합니다.
        ConvertTraceTextToCsv(TRACE_TXT, OUTPUT_CSV)

if __name__ == "__main__":
    main()

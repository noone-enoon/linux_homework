from subprocess import run
import re
import linecache
import json
import argparse
import os


class Parser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--locate", help="where to search .log files: dir or file", required=True)
    parser.add_argument("-p", "--path", help="path dir or file", required=True)

    def get_locate_files(self):
        args = self.parser.parse_args()
        if args.locate == 'dir':
            files = run(f"find {args.path} -name '*.log'", capture_output=True, shell=True)
            files = files.stdout
            if not files:
                print("В данном каталоге нет файлов .log, попробуйте поменять каталог.")
                raise SystemExit
            else:
                files = files.decode().split('\n')[:-1]
                for file_name in files:
                    run(f"cat {file_name} >> result_raw.txt", shell=True)
                path = "result_raw.txt"
        else:
            path = args.path
            if not os.path.isfile(path):
                print("Не удалось найти указанный файл.")
                raise SystemExit

        return path

    def get_requests_count(self, path):
        requests_count = run([f"cat {path} | wc -l"], capture_output=True, shell=True)
        requests_count = requests_count.stdout
        result_count_str = requests_count.decode()
        return int(result_count_str.rstrip())

    def get_requests_with_method(self, method, path):
        requests_with_method = run(["grep", "-c", f"{method}", f"{path}"], capture_output=True)
        requests_with_method = requests_with_method.stdout
        requests_with_method_str = requests_with_method.decode()
        return int(requests_with_method_str.rstrip())

    def get_top_ips(self, path, top=3):
        ips_dict = {}
        run([f"grep -E -o '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' {path} > ips.txt"],
            capture_output=True, shell=True)
        with open('ips.txt', 'r') as f:
            for line in f.readlines():
                if line.rstrip() not in ips_dict.keys():
                    ips_dict[line.rstrip()] = 1
                else:
                    ips_dict[line.rstrip()] += 1
        ips_sorted = sorted(ips_dict.items(), key=lambda item: -item[1])[:top]
        ips_top = dict(ips_sorted)
        return ips_top

    def get_raw_text(self):
        with open("access.log", "r") as f:
            raw_text = f.read()
            mass_raw = raw_text.split("\n")
        return mass_raw

    def get_top_longest_request(self, path):
        result = []
        number_str = []
        run(f"grep -n -o -E '([0-9]+$)' {path} | sort -r -g -u -t ':' -k 2 | head -3 > time_top.txt",
            capture_output=True, shell=True)
        regexp = '^(?P<ip>\S*).*\[(?P<timestamp>.*)\]\s\"(?P<method>\S*)\s(\S*)\s([^\"]*)\"\s(\S*)\s(\S*)\s\"([^\"]*)\"\s\"([^\"]*)\"\s(?P<time>\d+)'
        with open('time_top.txt', 'r') as f:
            for line in f.readlines():
                number_str.append(line.split(':')[0])
        for number in number_str:
            raw_string = linecache.getline('access.log', int(number))
            template_string = re.search(regexp, raw_string)
            result.append(f"ip: {template_string.group('ip')} method: {template_string.group('method')}"
                          f" timestamp: {template_string.group('timestamp')} "
                          f"time: {template_string.group('time')}")
        return result

    def parse(self):
        path = self.get_locate_files()
        requests_count = self.get_requests_count(path=path)
        requests_get = self.get_requests_with_method('GET', path=path)
        requests_head = self.get_requests_with_method('HEAD', path=path)
        requests_post = self.get_requests_with_method('POST', path=path)
        requests_put = self.get_requests_with_method('PUT', path=path)
        requests_delete = self.get_requests_with_method('DELETE', path=path)
        requests_connect = self.get_requests_with_method('CONNECT', path=path)
        requests_options = self.get_requests_with_method('OPTIONS', path=path)
        requests_trace = self.get_requests_with_method('TRACE', path=path)
        top_ips = self.get_top_ips(path=path)
        top_longest_request = self.get_top_longest_request(path=path)

        result = {"Общее количество запросов": requests_count,
                  "Количество запросов с методом GET": requests_get,
                  "Количество запросов с методом HEAD": requests_head,
                  "Количество запросов с методом POST": requests_post,
                  "Количество запросов с методом PUT": requests_put,
                  "Количество запросов с методом DELETE": requests_delete,
                  "Количество запросов с методом CONNECT": requests_connect,
                  "Количество запросов с методом OPTIONS": requests_options,
                  "Количество запросов с методом TRACE": requests_trace,
                  "Топ 3 ip-адреса по количеству запросов": top_ips,
                  "Топ 3 запроса по времени выполнения запроса": top_longest_request
                  }
        print(json.dumps(result, indent=4, ensure_ascii=False))

        with open("access_log_parsed.json", "w") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)


Parser().parse()

from subprocess import run, PIPE
import datetime


class Parser:
    users = []
    user_processes = {}

    def get_raw_info(self):
        raw_mass = []
        result = run(["ps", "aux"], capture_output=True)
        result = result.stdout
        result_str = result.decode()
        result_mass = result_str.split("\n")[1:-1]

        for str in result_mass:
            str = str.split(maxsplit=10)
            raw_mass.append(str)
        return raw_mass

    def get_user_processes(self, raw_mass):
        str_result = ''
        for str in raw_mass:
            if str[0] not in self.user_processes:
                self.user_processes[str[0]] = 1
            else:
                self.user_processes[str[0]] += 1
        for key, value in self.user_processes.items():
            str_result += (f'{key}: {value}\n')
        return str_result, self.user_processes

    def get_unique_users(self, raw_mass):
        unique_users = list(raw_mass.keys())
        return ", ".join(unique_users)

    def get_count_processes(self, raw_mass):
        return len(raw_mass)

    def get_mem(self, raw_mass):
        mem = 0.0
        for str in raw_mass:
            mem += float(str[3])
        return mem

    def get_cpu(self, raw_mass):
        cpu = 0.0
        for str in raw_mass:
            cpu += float(str[2])
        return cpu

    def get_top_1(self, raw_mass, number_element):
        lider = 0
        process = ''
        for str in raw_mass:
            if float(str[number_element]) > lider:
                lider = float(str[number_element])
                process = str[10]
        return process[:20]

    def save_report_to_txt(self, report):
        now = datetime.datetime.now()
        now = now.strftime('%d-%m-%Y--%H-%M')
        file_name = f'{now}-ps_aux.txt'
        with open(file_name, 'w') as f:
            f.write(report)

    def parser(self):
        result = self.get_raw_info()
        count_processes = self.get_count_processes(raw_mass=result)
        user_processes = self.get_user_processes(raw_mass=result)
        unique_users = self.get_unique_users(raw_mass=user_processes[1])
        mem = self.get_mem(raw_mass=result)
        cpu = self.get_cpu(raw_mass=result)
        top_1_mem = self.get_top_1(raw_mass=result, number_element=3)
        top_1_cpu = self.get_top_1(raw_mass=result, number_element=2)

        report = f"Отчёт о состоянии системы:\n" \
                 f"Пользователи системы: {unique_users}\n" \
                 f"Процессов запущено: {count_processes}\n" \
                 f"Пользовательских процессов:\n{user_processes[0]}" \
                 f"Всего памяти используется: {mem}%\n" \
                 f"Всего CPU используется: {cpu}%\n" \
                 f"Больше всего памяти использует: {top_1_mem}\n" \
                 f"Больше всего CPU использует: {top_1_cpu}"

        print(report)
        self.save_report_to_txt(report=report)


Parser().parser()


import os
import ctypes
import subprocess
import glob
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def print_header():
    print("=" * 60)
    print("   ПОЛНАЯ И НАВЕЧНАЯ БЛОКИРОВКА ОБНОВЛЕНИЙ OPERA GX   ")
    print("=" * 60)

def kill_opera_processes():
    print("\n[Подготовка] Закрытие активных процессов Opera GX...")
    subprocess.run('taskkill /f /im opera.exe', shell=True, capture_output=True)
    time.sleep(1)

def set_environment_variable():
    print("\n[1/4] Установка глобальной блокирующей переменной...")
    try:
        subprocess.run('setx OPERA_AUTOUPDATE_DISABLED "1" /M', shell=True, capture_output=True)
        print(" -> [УСПЕШНО] Переменная OPERA_AUTOUPDATE_DISABLED установлена.")
    except Exception as e:
        print(f" -> [ОШИБКА] Не удалось установить переменную: {e}")

def block_hosts():
    print("\n[2/4] Блокировка серверов обновлений Opera в файле hosts...")
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    domains_to_block = [
        "autoupdate.geo.opera.com",
        "autoupdate.opera.com"
    ]
    
    try:
        with open(hosts_path, "r", encoding="cp1251", errors="ignore") as file:
            content = file.read()
        
        with open(hosts_path, "a", encoding="cp1251") as file:
            for domain in domains_to_block:
                if domain not in content:
                    file.write(f"\n127.0.0.1 {domain}")
                    print(f" -> [БЛОК] Домен {domain} перенаправлен на 127.0.0.1")
                else:
                    print(f" -> [ИНФО] Домен {domain} уже заблокирован.")
    except Exception as e:
        print(f" -> [ОШИБКА] Не удалось отредактировать hosts (проверьте антивирус): {e}")

def disable_tasks():
    print("\n[3/4] Отключение задач в Планировщике Windows...")
    tasks = ["Opera GX scheduled update", "Opera scheduled update", "Opera GX scheduled Assistant autoupdate"]
    for task in tasks:
        try:
            # ИСПРАВЛЕНО: Явно декодируем через OEM кодировку с игнорированием неизвестных байт
            result = subprocess.run(f'schtasks /change /tn "{task}" /disable', capture_output=True, shell=True)
            stdout_text = result.stdout.decode('cp866', errors='ignore')
            
            if "Успешно" in stdout_text or "SUCCESS" in stdout_text:
                print(f" -> Задача '{task}' отключена.")
            else:
                print(f" -> Задача '{task}' не найдена или уже отключена.")
        except Exception as e:
            print(f" -> Ошибка с планировщиком: {e}")

def block_autoupdate_file(base_dir):
    print(f"\n[4/4] Зачистка исполняемых файлов в папке: {base_dir}")
    search_pattern = os.path.join(base_dir, "**", "opera_autoupdate.exe")
    autoupdate_paths = glob.glob(search_pattern, recursive=True)

    if not autoupdate_paths:
        print(" -> Файлы opera_autoupdate.exe не найдены. Возможно, они уже удалены.")
        return

    for exe_path in autoupdate_paths:
        if os.path.isfile(exe_path):
            try:
                os.remove(exe_path)
                os.makedirs(exe_path, exist_ok=True)
                print(f" -> [БЛОК] Файл заменен непробиваемой папкой-заглушкой: {exe_path}")
            except Exception as e:
                print(f" -> [ОШИБКА] Не удалось заблокировать файл {exe_path}: {e}")
        else:
            print(f" -> [ИНФО] Файл {exe_path} уже заблокирован папкой-заглушкой.")

def restart_opera(base_dir):
    print("\n[Перезапуск] Запуск Opera GX с новыми настройками...")
    opera_exe = os.path.join(base_dir, "opera.exe")
    if os.path.exists(opera_exe):
        try:
            subprocess.Popen([opera_exe], creationflags=subprocess.DETACHED_PROCESS)
            print(" -> [УСПЕШНО] Браузер Opera GX успешно перезапущен!")
        except Exception as e:
            print(f" -> [ОШИБКА] Не удалось запустить браузер автоматически: {e}")
    else:
        print(f" -> [ОШИБКА] Файл opera.exe не найден по пути: {opera_exe}")

def main():
    print_header()
    
    if not is_admin():
        print("[КРИТИЧЕСКАЯ ОШИБКА] Скрипт запущен БЕЗ прав администратора!")
        print("Для редактирования hosts и системных переменных необходимы права админа.")
        input("\nНажмите Enter для выхода...")
        return

    user_profile = os.environ.get('USERPROFILE', '')
    default_path = os.path.join(user_profile, 'AppData', 'Local', 'Programs', 'Opera GX')

    print("Укажите путь к папке с Opera GX:")
    print(f"1. Использовать стандартный путь:\n   ({default_path})")
    print("2. Ввести путь к папке вручную")
    
    choice = input("\nВаш выбор (1/2): ").strip()
    target_dir = ""

    if choice == "1":
        target_dir = default_path
    elif choice == "2":
        user_input = input("\nВведите полный путь к папке Opera GX: ").strip().strip('"')
        # ИСПРАВЛЕНО: Защита от ввода папки профиля (Roaming) вместо папки программы (Local)
        if os.path.isdir(user_input):
            if not os.path.exists(os.path.join(user_input, "opera.exe")) and "Roaming" in user_input:
                print("\n[ВНИМАНИЕ] Похоже, вы ввели путь к папке профиля (Roaming).")
                print("Программа установки находится в папке Local.")
                user_input = user_input.replace("Roaming\\Opera Software\\Opera GX Stable", "Local\\Programs\\Opera GX")
                print(f"Автоматически скорректировано на: {user_input}")
            
            if os.path.isdir(user_input):
                target_dir = user_input
            else:
                print("[ОШИБКА] Скорректированный путь не существует.")
                input("\nНажмите Enter для выхода...")
                return
        else:
            print("[ОШИБКА] Указанный путь не существует.")
            input("\nНажмите Enter для выхода...")
            return
    else:
        print("[ОШИБКА] Неверный ввод.")
        input("\nНажмите Enter для выхода...")
        return

    kill_opera_processes()
    set_environment_variable()
    block_hosts()
    disable_tasks()
    block_autoupdate_file(target_dir)
    restart_opera(target_dir)
    
    print("\n" + "="*60)
    print("БЛОКИРОВКА УСПЕШНО ЗАВЕРШЕНА И БРАУЗЕР ОБНОВЛЕН!")
    print("Opera GX больше никогда не сможет обновиться автоматически.")
    print("="*60)
    input("\nНажмите Enter для завершения работы...")

if __name__ == "__main__":
    main()

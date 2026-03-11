import subprocess
with open('git_history.txt', 'w', encoding='utf-8') as f:
    out = subprocess.check_output(['git', '--no-pager', 'log', '-n', '10', '--name-status'], encoding='utf-8', errors='replace')
    f.write(out)

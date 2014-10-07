ps aux | grep 'python app.py'  | awk '{print $2}' | xargs -n1 kill -9

# 这个文件【故意留空】。
#
# 它的作用是：让 pytest 把【本文件所在目录】(chatapi/) 加进 import 路径，
# 这样 tests/ 里的测试文件才能 `from app.main import app`。
#
# 没有它 → 会报：ModuleNotFoundError: No module named 'app'

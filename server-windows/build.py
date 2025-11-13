#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将后端打包为Windows可执行文件
"""

import PyInstaller.__main__
import os

# 当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller参数
PyInstaller.__main__.run([
    'main.py',
    '--name=USB监控后端',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--add-data=config.json;.',
    f'--distpath={current_dir}/dist',
    f'--workpath={current_dir}/build',
    f'--specpath={current_dir}',
])

print("\n打包完成！可执行文件位于: dist/USB监控后端.exe")

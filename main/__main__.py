# __main__.py
import glob
from pathlib import Path
from main.utils import load_plugins
import logging
from . import IS_BOT_MODE, userbot  # 导入 userbot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

if IS_BOT_MODE:
    from . import bot  # 仅在机器人模式下导入 bot
    # 机器人模式，加载原有的插件
    path = "main/plugins/*.py"
    files = glob.glob(path)
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem
            # 排除手动下载模式的插件
            if plugin_name != "pyroplug_manual":
                load_plugins(plugin_name.replace(".py", ""))

    # 不要做一个小偷
    print("Successfully deployed!")
    print("By MaheshChauhan • DroneBots")

    if __name__ == "__main__":
        bot.run_until_disconnected()
else:
    # 手动下载模式，加载手动下载的插件
    from main.plugins.pyroplug_manual import get_msg
    import asyncio

    async def main():
        await userbot.start()  # 在事件循环中启动 userbot
        while True:
            link = input("请输入要下载的消息链接（输入 'q' 退出）：")
            if link.lower() == 'q':
                break
            try:
                await get_msg(link)
            except Exception as e:
                print(f"下载过程中发生错误：{str(e)}")
        await userbot.stop()  # 在事件循环中停止 userbot

    if __name__ == "__main__":
        asyncio.run(main())
from colorama import Fore, Style, init

init(autoreset=True)

def print_banner(version: str = "dev"):
    banner = f"""
{Fore.CYAN}██╗    ██╗██╗  ██╗ ██████╗
██║ █╗ ██║███████║██║   ██║
╚███╔███╔╝██║  ██║╚██████╔╝
 ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝
{Style.DIM}by @rhyugen | v{version}{Style.RESET_ALL}
"""
    print(banner)

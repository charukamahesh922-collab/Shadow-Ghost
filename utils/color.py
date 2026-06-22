
#!/usr/bin/env python3
"""
Color utility for ShadowGhost - Terminal styling
"""

from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class Colors:
    """Terminal color codes for styled output"""
    
    # Foreground colors
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Fore.RESET
    
    # Bright colors
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX
    BRIGHT_RED = Fore.LIGHTRED_EX
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    BRIGHT_BLUE = Fore.LIGHTBLUE_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_CYAN = Fore.LIGHTCYAN_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    
    # Background colors
    BG_BLACK = Back.BLACK
    BG_RED = Back.RED
    BG_GREEN = Back.GREEN
    BG_YELLOW = Back.YELLOW
    BG_BLUE = Back.BLUE
    BG_MAGENTA = Back.MAGENTA
    BG_CYAN = Back.CYAN
    BG_WHITE = Back.WHITE
    
    # Styles
    DIM = Style.DIM
    NORMAL = Style.NORMAL
    BRIGHT = Style.BRIGHT
    
    # Custom combinations
    HEADER = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    INFO = Fore.BLUE + Style.BRIGHT
    DEBUG = Fore.MAGENTA + Style.DIM
    
    @staticmethod
    def colorize(text, color=Fore.WHITE, style=Style.NORMAL):
        """Apply color and style to text"""
        return f"{style}{color}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def header(text):
        """Format text as header"""
        return f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def success(text):
        """Format text as success message"""
        return f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def warning(text):
        """Format text as warning message"""
        return f"{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def error(text):
        """Format text as error message"""
        return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def info(text):
        """Format text as info message"""
        return f"{Fore.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}"
    
    @staticmethod
    def debug(text):
        """Format text as debug message"""
        return f"{Fore.MAGENTA}{Style.DIM}{text}{Style.RESET_ALL}"

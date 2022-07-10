import rich_click as click

from rich.panel import Panel
from rich.console import Group
from rich.columns import Columns
from rich.console import Console

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import has_completions
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.filters import completion_is_selected

from flaunt.lib import (
    fontlist,
    get_nerd_font,
    remove_appdirs,
    nerd_font_list,
)

console = Console()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def flaunt():
    pass


@flaunt.command(help="Clean up the config and data directories.")
def clean():
    with console.status("Cleaning up..."):
        remove_appdirs()


@flaunt.command(help="Download a font.")
def get():

    key_bindings = KeyBindings()

    @key_bindings.add(
        "enter",
        filter=(has_completions & ~completion_is_selected),
    )
    def _(event):
        event.current_buffer.go_to_completion(0)
        event.current_buffer.validate_and_handle()

    choices = nerd_font_list()["names"]
    completer = FuzzyWordCompleter(choices)
    result = prompt(
        "Search: ",
        completer=completer,
        key_bindings=key_bindings,
        complete_while_typing=True,
    )

    with console.status(f"Installing font: {result}..."):
        get_nerd_font(result)


@flaunt.command(help="List the fonts installed on the system.")
def list():
    with console.status("Getting font list..."):
        fonts = fontlist()

    with console.pager(styles=True):
        console.print(
            Panel(
                Group(
                    Panel(
                        f"Number of installed fonts: [b]{len(fonts)}[/]",
                        expand=False,
                    ),
                    Panel(
                        Columns(
                            [f"[i]{_}[/]" for _ in fonts],
                            equal=True,
                            expand=True,
                        ),
                        padding=2,
                        expand=False,
                        title_align="left",
                        title="[b]Installed Fonts[/]",
                    ),
                ),
                expand=True,
                title_align="right",
                title="[b]flaunt[/]: [i]Download your fonts and show them off![/]",
            )
        )

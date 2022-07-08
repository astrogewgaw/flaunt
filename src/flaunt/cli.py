import rich_click as click

from rich.panel import Panel
from rich.console import Group
from rich.columns import Columns
from rich.console import Console

from .lib import fontlist

console = Console()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def flaunt():

    """
    Download your fonts and show them off!
    """

    pass


@flaunt.command()
def get():
    pass


@flaunt.command()
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


@flaunt.command()
def search():
    pass

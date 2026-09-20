"""Interface de linha de comando do pylibre."""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

from .epub import read_book


def _default_output(src: str) -> str:
    return os.path.splitext(src)[0] + ".txt"


def convert(src: str, include_meta: bool = True) -> str:
    """Converte um EPUB em texto puro e devolve o conteúdo."""
    with zipfile.ZipFile(src) as zf:
        book = read_book(zf)

    blocks: list[str] = []
    if include_meta and (book.title or book.authors):
        head = book.title or "(sem título)"
        if book.authors:
            head += "\n" + ", ".join(book.authors)
        blocks.append(head)
    blocks.extend(book.chapters)
    return "\n\n".join(blocks).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pylibre",
        description="Converte arquivos EPUB em texto puro (.txt).",
    )
    parser.add_argument("epub", nargs="+", help="arquivo(s) .epub para converter")
    parser.add_argument(
        "-o", "--output",
        help="arquivo de saída (apenas com um único EPUB de entrada)",
    )
    parser.add_argument(
        "--no-meta", action="store_true",
        help="não incluir título e autor no início do arquivo",
    )
    args = parser.parse_args(argv)

    if len(args.epub) > 1 and args.output:
        parser.error("--output só é válido com um único EPUB de entrada")

    failed = 0
    for src in args.epub:
        out = args.output or _default_output(src)
        try:
            text = convert(src, include_meta=not args.no_meta)
        except FileNotFoundError:
            print(f"erro: arquivo não encontrado: {src}", file=sys.stderr)
        except zipfile.BadZipFile:
            print(f"erro: {src} não parece um EPUB válido (não é um ZIP)", file=sys.stderr)
        except (ValueError, KeyError) as exc:
            print(f"erro: {src}: {exc}", file=sys.stderr)
        except Exception as exc:  # falha inesperada: mostra, mas continua com os demais
            print(f"erro inesperado em {src}: {type(exc).__name__}: {exc}", file=sys.stderr)
        else:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"ok: {src} -> {out} ({len(text)} caracteres)")
            continue
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

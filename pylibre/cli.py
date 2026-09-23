"""Interface de linha de comando do pylibre."""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

from .epub import read_book

_INVALID_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def _safe_name(name: str) -> str:
    """Deixa um nome de arquivo seguro (sem caracteres inválidos, curto e sem espaços extras)."""
    name = _INVALID_CHARS.sub(" ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:80].rstrip(" .")


def _chapter_filename(index: int, title: str, width: int) -> str:
    safe = _safe_name(title)
    if safe:
        return f"{index:0{width}d} - {safe}.txt"
    return f"{index:0{width}d}.txt"


def _unique_name(name: str, used: set[str]) -> str:
    if name not in used:
        used.add(name)
        return name
    stem, ext = os.path.splitext(name)
    n = 2
    while f"{stem} ({n}){ext}" in used:
        n += 1
    result = f"{stem} ({n}){ext}"
    used.add(result)
    return result


def convert(
    src: str,
    out: str | None = None,
    include_meta: bool = True,
    capitulos: bool = False,
    multi: bool = False,
) -> tuple[str, str]:
    """Converte um EPUB em texto puro.

    - Modo padrão: gera um único `.txt` e devolve (caminho, "N caracteres").
    - Modo capítulos (`capitulos=True`): gera uma pasta com um `.txt` por
      capítulo e devolve (pasta, "N capítulos").
    """
    with zipfile.ZipFile(src) as zf:
        book = read_book(zf)

    if not capitulos:
        blocks: list[str] = []
        if include_meta and (book.title or book.authors):
            head = book.title or "(sem título)"
            if book.authors:
                head += "\n" + ", ".join(book.authors)
            blocks.append(head)
        blocks.extend(chapter.text for chapter in book.chapters)
        text = "\n\n".join(blocks).strip() + "\n"
        destino = Path(out) if out else Path(os.path.splitext(src)[0] + ".txt")
        destino.write_text(text, encoding="utf-8")
        return str(destino), f"{len(text)} caracteres"

    stem = os.path.splitext(os.path.basename(src))[0]
    if out:
        folder = Path(out) / stem if multi else Path(out)
    else:
        folder = Path(os.path.dirname(os.path.abspath(src))) / stem
    folder.mkdir(parents=True, exist_ok=True)

    width = max(2, len(str(len(book.chapters))))
    used: set[str] = set()
    for i, chapter in enumerate(book.chapters, start=1):
        name = _unique_name(_chapter_filename(i, chapter.title, width), used)
        (folder / name).write_text(chapter.text.strip() + "\n", encoding="utf-8")
    return str(folder) + "/", f"{len(book.chapters)} capítulos"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pylibre",
        description="Converte arquivos EPUB em texto puro (.txt).",
    )
    parser.add_argument("epub", nargs="+", help="arquivo(s) .epub para converter")
    parser.add_argument(
        "-o", "--output",
        help=(
            "arquivo de saída (modo padrão) ou pasta de saída (--capitulos); "
            "com vários EPUBs e --capitulos, funciona como pasta-base"
        ),
    )
    parser.add_argument(
        "--no-meta", action="store_true",
        help="não incluir título e autor no início do arquivo (ignorado com --capitulos)",
    )
    parser.add_argument(
        "--capitulos", action="store_true",
        help="gera uma pasta com um .txt por capítulo (em vez de um único arquivo)",
    )
    args = parser.parse_args(argv)

    multi = len(args.epub) > 1
    if multi and args.output and not args.capitulos:
        parser.error("--output só é válido com um único EPUB de entrada")

    failed = 0
    for src in args.epub:
        try:
            saida, resumo = convert(
                src,
                out=args.output,
                include_meta=not args.no_meta,
                capitulos=args.capitulos,
                multi=multi,
            )
        except FileNotFoundError:
            print(f"erro: arquivo não encontrado: {src}", file=sys.stderr)
        except zipfile.BadZipFile:
            print(f"erro: {src} não parece um EPUB válido (não é um ZIP)", file=sys.stderr)
        except (ValueError, KeyError, OSError) as exc:
            print(f"erro: {src}: {exc}", file=sys.stderr)
        except Exception as exc:  # falha inesperada: mostra, mas continua com os demais
            print(f"erro inesperado em {src}: {type(exc).__name__}: {exc}", file=sys.stderr)
        else:
            print(f"ok: {src} -> {saida} ({resumo})")
            continue
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

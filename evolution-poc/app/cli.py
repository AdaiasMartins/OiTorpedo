from __future__ import annotations

import argparse
import json

from .evolution_client import EvolutionClient
from .tasks import enqueue_bulk_messages


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def parse_recipients(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="POC simples da Evolution API com Celery.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--instance", required=True)

    qr = subparsers.add_parser("qr")
    qr.add_argument("--instance", required=True)
    qr.add_argument("--output", default="qrcode.png")

    send = subparsers.add_parser("send")
    send.add_argument("--instance", required=True)
    send.add_argument("--number", required=True)
    send.add_argument("--text", required=True)

    bulk = subparsers.add_parser("bulk")
    bulk.add_argument("--instance", required=True)
    bulk.add_argument("--numbers", required=True, help="Numeros separados por virgula.")
    bulk.add_argument("--text", required=True)
    bulk.add_argument("--delay", type=float, default=None)

    args = parser.parse_args()
    client = EvolutionClient()

    if args.command == "create":
        print_json(client.create_instance(args.instance))
    elif args.command == "qr":
        print_json(client.save_qrcode(args.instance, args.output))
    elif args.command == "send":
        print_json(client.send_text(args.instance, args.number, args.text))
    elif args.command == "bulk":
        result = enqueue_bulk_messages(
            instance=args.instance,
            recipients=parse_recipients(args.numbers),
            message=args.text,
            delay_seconds=args.delay,
        )
        print_json(result)


if __name__ == "__main__":
    main()

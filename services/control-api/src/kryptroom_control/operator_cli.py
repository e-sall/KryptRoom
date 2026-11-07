"""Separate-credential pilot provisioning. Deliberately has no HTTP equivalent."""

import argparse
from uuid import UUID

from kryptroom_control.config import load_settings
from kryptroom_control.db import Database
from kryptroom_control.operator import Operator


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled local pilot operator")
    parser.add_argument(
        "action",
        choices=(
            "approve",
            "provision",
            "suspend-user",
            "suspend-org",
            "reject-org",
            "reactivate-org",
        ),
    )
    parser.add_argument("--organization", type=UUID)
    parser.add_argument("--user", type=UUID)
    parser.add_argument(
        "--role", choices=("ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER"), default="ORG_MEMBER"
    )
    parser.add_argument("--operator", required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    db = Database(load_settings())
    try:
        with db.transaction() as session:
            op = Operator(session, args.operator, args.case)
            if args.action == "suspend-user":
                if args.user is None:
                    parser.error("--user required")
                op.suspend_user(args.user)
            else:
                if args.organization is None:
                    parser.error("--organization required")
                if args.action == "approve":
                    op.approve(args.organization)
                elif args.action == "provision":
                    if args.user is None:
                        parser.error("--user required")
                    op.provision(args.organization, args.user, args.role)
                else:
                    status = {
                        "suspend-org": "SUSPENDED",
                        "reject-org": "REJECTED",
                        "reactivate-org": "ACTIVE",
                    }
                    op.set_organization_status(args.organization, status[args.action])
    except Exception:
        print("Operator operation refused; no credential or database detail displayed")
        return 1
    finally:
        db.close()
    print("Operator operation committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from iamspy import Model
import pathlib
import pytest


@pytest.mark.parametrize(
    "files,inp,out",
    [
        (
            {"gaads": ["role-boundary-no-policies.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            False,
        ),
        (
            {"gaads": ["user-allow-check.json"]},
            (
                "arn:aws:iam::123456789012:user/PermissionBoundaryAllow",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["user-boundary-allow.json"]},
            (
                "arn:aws:iam::123456789012:user/PermissionBoundaryAllow",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["user-boundary-deny.json"]},
            (
                "arn:aws:iam::123456789012:user/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            False,
        ),
        (
            {"gaads": ["role-boundary-allow.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["role-boundary-deny.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            False,
        ),
        (
            {"gaads": ["basic-deny.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            False,
        ),
        (
            {"gaads": ["basic-allow.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["basic-allow.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:111111111111:function:helloworld",
            ),
            False,
        ),
        (
            {"gaads": ["basic-allow.json"], "resources": ["cross-account-rp.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:111111111111:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            True,
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                [],
                None,
                True,
            ),
            False,
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                ["aws:referer=bobby.tables"],
            ),
            True,
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "arn:aws:iam::123456789012:role/name",
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                ["aws:referer=bobby.tables"],
                None,
                True,
            ),
            True,
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-allow-testing.json"]},
            (
                "arn:aws:iam::111111111111:role/testing",
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            True,
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-deny-testing2.json"]},
            (
                "arn:aws:iam::111111111111:role/testing2",
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            False,
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-allow-all.json"]},
            (
                "arn:aws:iam::111111111111:role/testing",
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            True,
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-implicit-deny-via-condition.json"]},
            (
                "arn:aws:iam::111111111111:role/testing",
                "s3:GetObject",
                "arn:aws:s3:::bucket/obj-1",
                ["aws:PrincipalArn=arn:aws:iam::111111111111:role/testing"],
                None,
                True,
            ),
            False,
        ),
    ],
)
def test_can_i(files, inp, out):
    m = Model()

    base_path = pathlib.Path(__file__).parent / "files"

    for gaad in files.get("gaads", []):
        m.load_gaad(base_path / gaad)

    for rp in files.get("resources", []):
        m.load_resource_policies(base_path / rp)

    assert m.can_i(*inp) == out


@pytest.mark.parametrize(
    "files,inp,out",
    [
        (
            {"gaads": ["role-boundary-no-policies.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set([]),
        ),
        (
            {"gaads": ["user-allow-check.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:user/PermissionBoundaryAllow"]),
        ),
        (
            {"gaads": ["user-boundary-allow.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:user/PermissionBoundaryAllow"]),
        ),
        (
            {"gaads": ["user-boundary-deny.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(),
        ),
        (
            {"gaads": ["role-boundary-allow.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["role-boundary-deny.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(),
        ),
        (
            {"gaads": ["basic-allow.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-allow-testing.json"]},
            (
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            set(["arn:aws:iam::111111111111:role/testing", "arn:aws:iam::111111111111:role/testing2"]),
        ),
        (
            {"gaads": ["basic-allow.json"], "resources": ["cross-account-rp.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:111111111111:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                [],
                None,
                True,
            ),
            set(),
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                ["aws:referer=bobby.tables"],
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["allow-with-conditions.json"]},
            (
                "lambda:InvokeFunction",
                "arn:aws:lambda:eu-west-1:123456789012:function:helloworld",
                ["aws:referer=bobby.tables"],
                None,
                True,
            ),
            set(["arn:aws:iam::123456789012:role/name"]),
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-allow-testing.json"]},
            (
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            set(["arn:aws:iam::111111111111:role/testing", "arn:aws:iam::111111111111:role/testing2"]),
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-deny-testing2.json"]},
            (
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            set([]),
        ),
        (
            {"gaads": ["allow-testing-s3.json"], "resources": ["resource-s3-allow-all.json"]},
            (
                "s3:ListBucket",
                "arn:aws:s3:::bucket",
            ),
            set(["arn:aws:iam::111111111111:role/testing", "arn:aws:iam::111111111111:role/testing2"]),
        ),
    ],
)
def test_who_can(files, inp, out):
    m = Model()

    base_path = pathlib.Path(__file__).parent / "files"

    for gaad in files.get("gaads", []):
        m.load_gaad(base_path / gaad)

    for rp in files.get("resources", []):
        m.load_resource_policies(base_path / rp)

    assert set(m.who_can(*inp)) == out

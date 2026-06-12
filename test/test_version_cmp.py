import pytest

# importing must not require distutils, which was removed in Python 3.12
from awxkit.awx import version_cmp


@pytest.mark.parametrize(
    'x, y, expected',
    [
        ('1.0.0', '2.0.0', -1),
        ('2.0.0', '2.0.0', 0),
        ('2.1.0', '2.0.3', 1),
        ('24.6.1', '24.6.0', 1),
    ],
)
def test_version_cmp(x, y, expected):
    assert version_cmp(x, y) == expected
